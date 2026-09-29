"""Live / paper runner for the Crowd Squeeze strategy on Bybit USDT perpetuals.

    python -m altcoin_squeeze_bot.bot --mode paper              # no keys, simulated fills, real data
    python -m altcoin_squeeze_bot.bot --mode testnet            # api-testnet.bybit.com, testnet keys
    python -m altcoin_squeeze_bot.bot --mode live --i-understand-the-risk

Keys come from env vars BYBIT_API_KEY / BYBIT_API_SECRET. Use a sub-account API key with
"Contract - Orders/Positions" permission only, NO withdrawal permission, and bind it to your IP.

On the exchange every position always carries a server-side stop loss, so if this process dies
the worst case is the planned 1R loss, not a liquidation.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from dataclasses import asdict
from decimal import Decimal

from .bybit_client import BybitClient
from .config import Config
from .data import align, select_universe
from .risk import RiskGuard, position_size, round_step
from .strategy import Bar, Signal, TradePlan, atr, min_history, new_plan, scan, update_trail

log = logging.getLogger("squeeze")


def fmt(value: float, step: float) -> str:
    """Round to an exchange step and render without float noise, e.g. fmt(0.123456, 0.001) -> '0.123'."""
    if step <= 0:
        return str(value)
    q = Decimal(str(step)).normalize()
    if q >= 1:
        q = Decimal(1)
    return str(Decimal(str(round_step(value, step))).quantize(q))


def fmt_price(value: float, tick: float) -> str:
    """Prices round to nearest tick (not down)."""
    return fmt(round(value / tick) * tick + tick * 1e-9, tick) if tick > 0 else str(value)


# ---- brokers ------------------------------------------------------------------------------------
class LiveBroker:
    """Thin layer over BybitClient that handles instrument rounding."""

    def __init__(self, client: BybitClient, instruments: dict[str, dict]):
        self.c = client
        self.inst = instruments

    def filters(self, sym: str) -> tuple[float, float, float]:
        it = self.inst[sym]
        lot, pf = it["lotSizeFilter"], it["priceFilter"]
        return float(lot["qtyStep"]), float(lot["minOrderQty"]), float(pf["tickSize"])

    def equity(self) -> float:
        return self.c.equity()

    def sizes(self) -> dict[str, float]:
        return {s: float(p["size"]) for s, p in self.c.positions().items()}

    def open(self, sym: str, side: str, qty: float, stop: float, leverage: float, _px: float) -> float:
        step, _, tick = self.filters(sym)
        max_lev = float(self.inst[sym]["leverageFilter"]["maxLeverage"])
        self.c.set_leverage(sym, min(float(int(leverage + 0.999)), max_lev))
        self.c.market_order(sym, side, fmt(qty, step), stop_loss=fmt_price(stop, tick))
        for _ in range(10):
            pos = self.c.positions().get(sym)
            if pos:
                return float(pos["avgPrice"])
            time.sleep(0.5)
        raise RuntimeError(f"{sym}: order sent but no position appeared")

    def place_tp(self, sym: str, close_side: str, qty: float, price: float) -> None:
        step, min_qty, tick = self.filters(sym)
        q = round_step(qty, step)
        if q >= min_qty:
            self.c.limit_reduce_only(sym, close_side, fmt(q, step), fmt_price(price, tick))

    def move_stop(self, sym: str, stop: float) -> None:
        self.c.set_stop(sym, fmt_price(stop, self.filters(sym)[2]))

    def close_all(self, sym: str, close_side: str, qty: float, _px: float) -> None:
        self.c.cancel_all(sym)
        step = self.filters(sym)[0]
        self.c.market_order(sym, close_side, fmt(qty, step), reduce_only=True)

    def cleanup(self, sym: str) -> None:
        self.c.cancel_all(sym)

    def on_closed_bar(self, sym: str, bar: Bar) -> None:
        pass  # the exchange enforces stops and TPs itself


class PaperBroker:
    """Simulated fills on real market data. Stops/TPs are checked against each closed bar."""

    def __init__(self, cash: float, fee: float, slippage: float, book: dict | None = None):
        self.fee, self.slip = fee, slippage
        self.cash = cash
        self.book: dict[str, dict] = book or {}  # sym -> {side, qty, entry, stop, tp_qty, tp_px}
        self.last_px: dict[str, float] = {}

    def filters(self, sym: str) -> tuple[float, float, float]:
        return 0.0, 0.0, 0.0

    def equity(self) -> float:
        unreal = sum(
            (1 if p["side"] == "Buy" else -1) * (self.last_px.get(s, p["entry"]) - p["entry"]) * p["qty"]
            for s, p in self.book.items()
        )
        return self.cash + unreal

    def sizes(self) -> dict[str, float]:
        return {s: p["qty"] for s, p in self.book.items()}

    def _fill(self, sym: str, qty: float, px: float) -> None:
        p = self.book[sym]
        d = 1 if p["side"] == "Buy" else -1
        self.cash += d * (px - p["entry"]) * qty - px * qty * self.fee
        p["qty"] -= qty
        if p["qty"] <= 1e-12:
            del self.book[sym]

    def open(self, sym: str, side: str, qty: float, stop: float, _lev: float, px: float) -> float:
        d = 1 if side == "Buy" else -1
        fill = px * (1 + d * self.slip)
        self.cash -= fill * qty * self.fee
        self.book[sym] = {"side": side, "qty": qty, "entry": fill, "stop": stop, "tp_qty": 0.0, "tp_px": 0.0}
        return fill

    def place_tp(self, sym: str, _close_side: str, qty: float, price: float) -> None:
        self.book[sym].update(tp_qty=qty, tp_px=price)

    def move_stop(self, sym: str, stop: float) -> None:
        self.book[sym]["stop"] = stop

    def close_all(self, sym: str, _close_side: str, qty: float, px: float) -> None:
        d = 1 if self.book[sym]["side"] == "Buy" else -1
        self._fill(sym, qty, px * (1 - d * self.slip))

    def cleanup(self, sym: str) -> None:
        pass

    def on_closed_bar(self, sym: str, bar: Bar) -> None:
        self.last_px[sym] = bar.close
        p = self.book.get(sym)
        if not p:
            return
        d = 1 if p["side"] == "Buy" else -1
        if (bar.low <= p["stop"]) if d == 1 else (bar.high >= p["stop"]):
            px = min(p["stop"], bar.open) if d == 1 else max(p["stop"], bar.open)
            self._fill(sym, p["qty"], px * (1 - d * self.slip))
            return
        if p["tp_qty"] > 0 and ((bar.high >= p["tp_px"]) if d == 1 else (bar.low <= p["tp_px"])):
            self._fill(sym, min(p["tp_qty"], p["qty"]), p["tp_px"])
            if sym in self.book:
                self.book[sym]["tp_qty"] = 0.0


# ---- bot ----------------------------------------------------------------------------------------
class Bot:
    def __init__(self, mode: str, cfg: Config, state_path: str, paper_equity: float = 100.0):
        self.cfg, self.mode, self.state_path = cfg, mode, state_path
        self.data = BybitClient(testnet=(mode == "testnet"))
        self.state = self._load()
        self.guard = RiskGuard.from_dict(cfg.risk, self.state.get("guard", {}))
        self.instruments = self.data.instruments()
        if mode == "paper":
            p = self.state.get("paper", {})
            self.broker: LiveBroker | PaperBroker = PaperBroker(
                p.get("cash", paper_equity), cfg.costs.taker_fee, cfg.costs.slippage, p.get("book")
            )
        else:
            key, secret = os.environ.get("BYBIT_API_KEY", ""), os.environ.get("BYBIT_API_SECRET", "")
            self.broker = LiveBroker(BybitClient(key, secret, testnet=(mode == "testnet")), self.instruments)

    # -- persistence
    def _load(self) -> dict:
        if os.path.exists(self.state_path):
            with open(self.state_path) as fh:
                return json.load(fh)
        return {"positions": {}}

    def _save(self) -> None:
        self.state["guard"] = self.guard.to_dict()
        if isinstance(self.broker, PaperBroker):
            self.state["paper"] = {"cash": self.broker.cash, "book": self.broker.book}
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(self.state, fh, indent=2)
        os.replace(tmp, self.state_path)

    # -- data
    def _bars(self, sym: str, btc: dict[int, float], funding_now: float) -> list[Bar]:
        sc = self.cfg.strategy
        step = sc.interval_min * 60_000
        n = min_history(sc) + 60
        now = int(time.time() * 1000)
        start = now - n * step
        kl = [k for k in self.data.klines(sym, sc.interval_min, start=start, limit=1000) if int(k[0]) + step <= now]
        oi = self.data.open_interest(sym, sc.interval_min, start=start, end=now)
        fr = self.data.funding_history(sym, start - 3 * 86_400_000, now)
        bars = align(kl, btc, oi, fr, sc.interval_min)
        if bars:
            bars[-1].funding = funding_now  # the currently accruing rate is the freshest crowd reading
        return bars

    # -- one cycle, run right after a candle closes
    def cycle(self) -> None:
        sc, rc = self.cfg.strategy, self.cfg.risk
        step = sc.interval_min * 60_000
        now = int(time.time() * 1000)
        tickers = {t["symbol"]: t for t in self.data.tickers()}
        btc = {int(k[0]): float(k[4])
               for k in self.data.klines("BTCUSDT", sc.interval_min, start=now - (min_history(sc) + 60) * step)
               if int(k[0]) + step <= now}

        positions: dict[str, dict] = self.state["positions"]
        bars_cache: dict[str, list[Bar]] = {}

        # 1) manage open positions
        for sym in list(positions):
            bars = bars_cache[sym] = self._bars(sym, btc, float(tickers[sym].get("fundingRate") or 0))
            if not bars:
                continue
            p = positions[sym]
            plan = TradePlan(**p["plan"])
            for b in (b for b in bars if b.ts > p["last_bar_ts"]):
                self.broker.on_closed_bar(sym, b)
            size = self.broker.sizes().get(sym, 0.0)
            if size <= 0:
                log.info("%s closed by stop/trail", sym)
                self.broker.cleanup(sym)
                del positions[sym]
                continue
            if not plan.tp1_done and size < p["orig_qty"] * (1 - sc.tp1_fraction / 2):
                plan.tp1_done = True
                log.info("%s TP1 filled, stop -> breakeven", sym)
            old_stop = plan.stop
            for i, b in enumerate(bars):
                if b.ts > p["last_bar_ts"]:
                    update_trail(plan, b, atr(bars, i, sc.atr_period), sc)
            p["last_bar_ts"] = bars[-1].ts
            close_side = "Sell" if plan.side == "Buy" else "Buy"
            if plan.bars_held >= sc.max_hold_bars:
                log.info("%s time stop", sym)
                self.broker.close_all(sym, close_side, size, bars[-1].close)
                del positions[sym]
                continue
            if plan.stop != old_stop:
                log.info("%s stop %.6g -> %.6g", sym, old_stop, plan.stop)
                self.broker.move_stop(sym, plan.stop)
            p["plan"] = asdict(plan)

        # 2) circuit breakers
        equity = self.broker.equity()
        self.guard.update(equity, now)
        log.info("equity %.2f USDT | open %d | killed=%s", equity, len(positions), self.guard.killed)
        if not self.guard.can_open(equity) or len(positions) >= rc.max_positions:
            self._save()
            return

        # 3) scan for new setups
        universe = [s for s in select_universe(tickers.values(), self.cfg.universe) if s in self.instruments]
        signals: list[tuple[str, Signal, list[Bar]]] = []
        for sym in universe:
            if sym in positions:
                continue
            try:
                bars = bars_cache.get(sym) or self._bars(sym, btc, float(tickers[sym].get("fundingRate") or 0))
            except Exception as exc:  # one bad symbol must not stop the scan
                log.warning("%s data error: %s", sym, exc)
                continue
            if len(bars) < min_history(sc):
                continue
            sig = scan(bars, sc)
            if sig:
                signals.append((sym, sig, bars))

        free = rc.max_positions - len(positions)
        for sym, sig, bars in sorted(signals, key=lambda x: -x[1].score)[:free]:
            px = float(tickers[sym]["lastPrice"])
            d = 1 if sig.side == "Buy" else -1
            stop = px - d * abs(sig.entry - sig.stop)
            step_q, min_q, _ = self.broker.filters(sym)
            qty = position_size(equity, px, stop, rc, step_q, min_q)
            if qty <= 0:
                log.info("%s signal skipped: size below exchange minimum", sym)
                continue
            fill = self.broker.open(sym, sig.side, qty, stop, rc.max_leverage, px)
            plan = new_plan(sig.side, fill, stop, sc)
            self.broker.place_tp(sym, "Sell" if d == 1 else "Buy", qty * sc.tp1_fraction, plan.tp1_price)
            positions[sym] = {"plan": asdict(plan), "orig_qty": qty, "last_bar_ts": bars[-1].ts}
            log.info("OPEN %s %s qty=%s @ %.6g stop=%.6g tp1=%.6g (z=%.1f)",
                     sym, sig.side, qty, fill, stop, plan.tp1_price, sig.score)
        self._save()

    def run_forever(self) -> None:
        step_s = self.cfg.strategy.interval_min * 60
        while True:
            wait = step_s - time.time() % step_s + 10  # 10s after the candle closes
            log.info("next cycle in %ds", int(wait))
            time.sleep(wait)
            try:
                self.cycle()
            except Exception:
                log.exception("cycle failed; positions keep their exchange-side stops")


def main() -> None:
    ap = argparse.ArgumentParser(description="Crowd Squeeze bot for Bybit altcoin perpetuals")
    ap.add_argument("--mode", choices=("paper", "testnet", "live"), default="paper")
    ap.add_argument("--state", default="squeeze_state.json")
    ap.add_argument("--equity", type=float, default=100.0, help="starting balance for paper mode")
    ap.add_argument("--once", action="store_true", help="run a single cycle and exit")
    ap.add_argument("--i-understand-the-risk", action="store_true", dest="confirm")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.mode == "live" and not args.confirm:
        raise SystemExit("Live trading uses real money. Re-run with --i-understand-the-risk after paper/testnet.")
    bot = Bot(args.mode, Config(), args.state, args.equity)
    if args.once:
        bot.cycle()
    else:
        bot.run_forever()


if __name__ == "__main__":
    main()
