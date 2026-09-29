"""Portfolio backtester for the Crowd Squeeze strategy.

Rules that keep it honest:
- signals are computed on a closed bar and filled at the NEXT bar's open, plus slippage
- if a bar touches both the stop and the target, the stop is assumed to hit first
- taker fees on every fill, funding charged/received every 8h
- same sizing and circuit breakers as the live bot

Usage:
    python -m altcoin_squeeze_bot.backtest --synthetic edge
    python -m altcoin_squeeze_bot.backtest --days 120 --top 25
    python -m altcoin_squeeze_bot.backtest --symbols WIFUSDT,PEPEUSDT --days 60
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field

from .config import Config
from .risk import RiskGuard, position_size
from .strategy import Bar, Features, Signal, SqueezeDetector, TradePlan, atr, new_plan, update_trail

FUNDING_PERIOD_MS = 8 * 3_600_000


@dataclass
class Position:
    symbol: str
    plan: TradePlan
    qty: float
    entry_ts: int
    realized: float = 0.0  # pnl booked so far (after fees)
    orig_qty: float = 0.0


@dataclass
class Trade:
    symbol: str
    side: str
    entry_ts: int
    exit_ts: int
    entry: float
    pnl: float
    r_multiple: float
    reason: str


@dataclass
class Result:
    start_equity: float
    equity: float
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[tuple[int, float]] = field(default_factory=list)
    killed: bool = False

    @property
    def max_drawdown(self) -> float:
        peak, dd = 0.0, 0.0
        for _, e in self.equity_curve:
            peak = max(peak, e)
            if peak > 0:
                dd = max(dd, 1 - e / peak)
        return dd

    def summary(self) -> str:
        n = len(self.trades)
        wins = [t for t in self.trades if t.pnl > 0]
        gross_win = sum(t.pnl for t in wins)
        gross_loss = -sum(t.pnl for t in self.trades if t.pnl <= 0)
        pf = gross_win / gross_loss if gross_loss > 0 else float("inf")
        avg_r = sum(t.r_multiple for t in self.trades) / n if n else 0.0
        lines = [
            f"Start equity     : {self.start_equity:,.2f} USDT",
            f"Final equity     : {self.equity:,.2f} USDT ({(self.equity / self.start_equity - 1) * 100:+.1f}%)",
            f"Trades           : {n}",
            f"Win rate         : {len(wins) / n * 100:.1f}%" if n else "Win rate         : -",
            f"Profit factor    : {pf:.2f}",
            f"Avg R per trade  : {avg_r:+.2f}",
            f"Max drawdown     : {self.max_drawdown * 100:.1f}%",
        ]
        if self.killed:
            lines.append("KILL SWITCH HIT  : bot would have stopped trading")
        return "\n".join(lines)


def run(
    data: dict[str, list[Bar]],
    cfg: Config,
    start_equity: float = 100.0,
    features: dict[str, list[Features | None]] | None = None,
) -> Result:
    sc, rc, cc = cfg.strategy, cfg.risk, cfg.costs
    step_ms = sc.interval_min * 60_000
    index = {s: {b.ts: i for i, b in enumerate(bars)} for s, bars in data.items()}
    detectors = {s: SqueezeDetector(sc, features.get(s) if features else None) for s in data}
    timeline = sorted({b.ts for bars in data.values() for b in bars})

    cash = start_equity
    guard = RiskGuard(rc)
    open_pos: dict[str, Position] = {}
    pending: dict[str, Signal] = {}
    res = Result(start_equity, start_equity)

    def close(pos: Position, qty: float, price: float, ts: int, reason: str) -> None:
        nonlocal cash
        d = pos.plan.direction
        pnl = d * (price - pos.plan.entry) * qty - price * qty * cc.taker_fee
        cash += pnl
        pos.realized += pnl
        pos.qty -= qty
        if pos.qty <= 1e-12:
            risk_usd = pos.plan.initial_risk * pos.orig_qty
            res.trades.append(
                Trade(pos.symbol, pos.plan.side, pos.entry_ts, ts, pos.plan.entry, pos.realized,
                      pos.realized / risk_usd if risk_usd else 0.0, reason)
            )
            del open_pos[pos.symbol]

    for ts in timeline:
        # 1) fills for signals from the previous bar
        for sym, sig in list(pending.items()):
            i = index[sym].get(ts)
            if i is None:
                continue
            del pending[sym]
            bar = data[sym][i]
            d = 1 if sig.side == "Buy" else -1
            fill = bar.open * (1 + d * cc.slippage)
            dist = abs(sig.entry - sig.stop)
            stop = fill - d * dist
            equity = cash + _unrealized(open_pos, data, index, ts, prev=True)
            qty = position_size(equity, fill, stop, rc)
            if qty <= 0:
                continue
            fee = fill * qty * cc.taker_fee
            open_pos[sym] = Position(sym, new_plan(sig.side, fill, stop, sc), qty, ts, realized=-fee, orig_qty=qty)
            cash -= fee

        # 2) manage open positions on this bar
        for sym, pos in list(open_pos.items()):
            i = index[sym].get(ts)
            if i is None:
                continue
            bar, plan = data[sym][i], pos.plan
            d = plan.direction
            stop_hit = bar.low <= plan.stop if d == 1 else bar.high >= plan.stop
            if stop_hit:
                px = min(plan.stop, bar.open) if d == 1 else max(plan.stop, bar.open)
                close(pos, pos.qty, px * (1 - d * cc.slippage), ts, "trail" if plan.tp1_done else "stop")
                continue
            if not plan.tp1_done and (bar.high >= plan.tp1_price if d == 1 else bar.low <= plan.tp1_price):
                close(pos, pos.qty * sc.tp1_fraction, plan.tp1_price, ts, "tp1")
                plan.tp1_done = True
            if (ts + step_ms) % FUNDING_PERIOD_MS == 0:
                pay = d * pos.qty * bar.close * bar.funding
                cash -= pay
                pos.realized -= pay
            f = features[sym][i] if features else None
            update_trail(plan, bar, f.atr if f else atr(data[sym], i, sc.atr_period), sc)
            if plan.bars_held >= sc.max_hold_bars:
                close(pos, pos.qty, bar.close * (1 - d * cc.slippage), ts, "time")

        # 3) account state + new signals
        equity = cash + _unrealized(open_pos, data, index, ts)
        res.equity_curve.append((ts, equity))
        guard.update(equity, ts)

        signals = []
        for sym, bars in data.items():
            i = index[sym].get(ts)
            if i is None:
                continue
            sig = detectors[sym].step(bars, i)
            if sig and sym not in open_pos and sym not in pending:
                signals.append((sym, sig))
        if signals and guard.can_open(equity):
            free = rc.max_positions - len(open_pos) - len(pending)
            for sym, sig in sorted(signals, key=lambda x: -x[1].score)[: max(free, 0)]:
                pending[sym] = sig

    res.equity = res.equity_curve[-1][1] if res.equity_curve else start_equity
    res.killed = guard.killed
    return res


def _unrealized(open_pos: dict[str, Position], data, index, ts: int, prev: bool = False) -> float:
    total = 0.0
    for sym, pos in open_pos.items():
        i = index[sym].get(ts)
        if i is None:
            continue
        if prev:
            i -= 1
        if i < 0:
            continue
        total += pos.plan.direction * (data[sym][i].close - pos.plan.entry) * pos.qty
    return total


def load_data(
    cfg: Config, synthetic: str | None, symbols: str | None, top: int, days: int, cache: str | None
) -> dict[str, list[Bar]]:
    if synthetic:
        from .synthetic import universe

        return universe(n_symbols=8, n=6000, edge=synthetic == "edge")

    import os

    from .bybit_client import BybitClient
    from .data import btc_close_map, fetch_bars, load_bars, save_bars, select_universe

    if cache and os.path.exists(cache):
        return load_bars(cache)
    client = BybitClient()
    end = int(time.time() * 1000)
    start = end - days * 86_400_000
    if symbols:
        names = symbols.split(",")
    else:
        cfg.universe.max_symbols = top
        names = select_universe(client.tickers(), cfg.universe)
    btc = btc_close_map(client, cfg.strategy.interval_min, start, end)
    data = {}
    for s in names:
        print(f"downloading {s} ...")
        data[s] = fetch_bars(client, s, cfg.strategy.interval_min, start, end, btc)
    if cache:
        save_bars(cache, data)
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description="Backtest the Crowd Squeeze strategy")
    ap.add_argument("--synthetic", choices=("edge", "noedge"), help="generated data, no network (pipeline check)")
    ap.add_argument("--symbols", help="comma separated, e.g. WIFUSDT,PEPEUSDT")
    ap.add_argument("--top", type=int, default=20, help="use top-N alts by 24h turnover")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--equity", type=float, default=100.0)
    ap.add_argument("--cache", help="JSON cache file for downloaded bars")
    ap.add_argument("--trades", action="store_true", help="print every trade")
    args = ap.parse_args()
    cfg = Config()

    data = load_data(cfg, args.synthetic, args.symbols, args.top, args.days, args.cache)
    res = run(data, cfg, args.equity)
    if args.trades:
        for t in res.trades:
            ts = time.strftime("%Y-%m-%d %H:%M", time.gmtime(t.entry_ts / 1000))
            print(f"{ts}  {t.symbol:<14} {t.side:<4} {t.reason:<5} pnl={t.pnl:+8.2f}  R={t.r_multiple:+.2f}")
    print(res.summary())


if __name__ == "__main__":
    main()
