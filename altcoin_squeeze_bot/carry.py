"""Funding carry sleeve: long spot + short perp on the same coin (delta-neutral).

When funding is positive, shorts are paid by longs every funding period. Holding the coin on spot
cancels the price risk, so the position earns the funding stream minus four taker fills
(spot buy, perp sell, and the reverse on exit). This is the idea behind open-source scanners such as
aoki-h-jp/funding-rate-arbitrage (MIT); it is re-implemented here, not copied.

Risks that remain: funding can flip negative, spot and perp prices can diverge temporarily (basis),
and the short leg can be liquidated if its margin is too thin during a spike, so keep >= 20% buffer.

    python -m altcoin_squeeze_bot.carry --scan                       # live opportunities, no keys
    python -m altcoin_squeeze_bot.carry --backtest --cache data/bars.json
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

from .config import CarryConfig, Config
from .strategy import Bar

PERIOD_MS = 8 * 3_600_000
PERIODS_PER_YEAR = 3 * 365
PERP_MARGIN = 0.2  # short leg at 5x: every 1 USDT of notional needs 1 USDT spot + 0.2 USDT margin


def settlements(bars: list[Bar], interval_min: int) -> dict[int, float]:
    """Funding rate settled at each 8h boundary. Coins on 4h/1h funding are approximated at 8h."""
    step = interval_min * 60_000
    return {b.ts + step: b.funding for b in bars if (b.ts + step) % PERIOD_MS == 0}


def round_trip_cost(cfg: CarryConfig) -> float:
    return 2 * (cfg.spot_fee + cfg.perp_fee)


@dataclass
class CarryResult:
    start_equity: float
    equity: float
    periods: int
    invested_periods: int
    switches: int
    fees: float
    curve: list[tuple[int, float]] = field(default_factory=list)

    @property
    def apr(self) -> float:
        years = self.periods / PERIODS_PER_YEAR
        return (self.equity / self.start_equity) ** (1 / years) - 1 if years > 0 and self.equity > 0 else 0.0

    @property
    def max_drawdown(self) -> float:
        peak, dd = 0.0, 0.0
        for _, e in self.curve:
            peak = max(peak, e)
            dd = max(dd, 1 - e / peak) if peak > 0 else dd
        return dd

    def summary(self) -> str:
        return "\n".join([
            f"Start equity   : {self.start_equity:,.2f} USDT",
            f"Final equity   : {self.equity:,.2f} USDT ({(self.equity / self.start_equity - 1) * 100:+.2f}%)",
            f"APR (compound) : {self.apr * 100:+.1f}%",
            f"Max drawdown   : {self.max_drawdown * 100:.2f}% (funding only; basis moves not modelled)",
            f"Time invested  : {self.invested_periods / max(self.periods, 1) * 100:.0f}% of periods",
            f"Entries        : {self.switches}, fees paid {self.fees:.2f} USDT",
        ])


def backtest_carry(data: dict[str, list[Bar]], cfg: Config, start_equity: float = 100.0) -> CarryResult:
    cc = cfg.carry
    series = {s: settlements(b, cfg.strategy.interval_min) for s, b in data.items()}
    timeline = sorted({t for ser in series.values() for t in ser})
    history: dict[str, list[float]] = {s: [] for s in series}
    holdings: dict[str, float] = {}  # symbol -> notional
    equity, fees, switches, invested = start_equity, 0.0, 0, 0
    res = CarryResult(start_equity, start_equity, len(timeline), 0, 0, 0.0)

    for t in timeline:
        # 1) collect / pay this period's funding on what we hold (short perp receives positive funding)
        for sym, notional in holdings.items():
            equity += notional * series[sym].get(t, 0.0)
        invested += bool(holdings)

        for sym, ser in series.items():
            if t in ser:
                history[sym].append(ser[t])

        def trailing(sym: str) -> float | None:
            h = history[sym]
            return sum(h[-cc.lookback_periods:]) / cc.lookback_periods if len(h) >= cc.lookback_periods else None

        # 2) exits: funding decayed
        for sym in list(holdings):
            avg = trailing(sym)
            if avg is not None and avg < cc.exit_rate:
                cost = holdings.pop(sym) * (cc.spot_fee + cc.perp_fee)
                equity -= cost
                fees += cost

        # 3) entries: best trailing funding first; the expected hold must pay back the fees
        size = equity * cc.capital_usage / (cc.max_holdings * (1 + PERP_MARGIN))
        ranked = sorted(((a, s) for s in series if s not in holdings and (a := trailing(s)) is not None), reverse=True)
        for avg, sym in ranked:
            if len(holdings) >= cc.max_holdings or avg < cc.enter_rate:
                break
            holdings[sym] = size
            cost = size * (cc.spot_fee + cc.perp_fee)
            equity -= cost
            fees += cost
            switches += 1
        res.curve.append((t, equity))

    res.equity, res.invested_periods, res.switches, res.fees = equity, invested, switches, fees
    return res


def scan_live(cfg: Config, hold_days: float = 7.0) -> list[dict]:
    """Current carry candidates with a spot market on Bybit, ranked by net APR over `hold_days`."""
    import time

    from .bybit_client import BybitClient

    c = BybitClient()
    cc = cfg.carry
    spot = {s for s, it in c.instruments("spot").items() if it.get("status") == "Trading"}
    linear = c.instruments("linear")
    now = int(time.time() * 1000)
    rows = []
    for t in c.tickers():
        sym = t["symbol"]
        if sym not in spot or float(t.get("turnover24h") or 0) < cfg.universe.min_turnover_24h:
            continue
        if float(t.get("fundingRate") or 0) < cc.enter_rate:
            continue
        interval_h = int(linear.get(sym, {}).get("fundingInterval", 480)) / 60
        hist = [r for _, r in c.funding_history(sym, now - 3 * 86_400_000, now)]
        if not hist:
            continue
        avg = sum(hist) / len(hist)
        per_year = 365 * 24 / interval_h
        gross_hold = avg * hold_days * 24 / interval_h
        net_hold = gross_hold - round_trip_cost(cc)
        rows.append({
            "symbol": sym, "funding_now": float(t["fundingRate"]), "avg_3d": avg, "interval_h": interval_h,
            "gross_apr": avg * per_year, "net_hold_pct": net_hold,
            "positive_share": sum(r > 0 for r in hist) / len(hist),
        })
    rows.sort(key=lambda r: -r["net_hold_pct"])
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Delta-neutral funding carry: scanner and backtest")
    ap.add_argument("--scan", action="store_true", help="list live opportunities (public API)")
    ap.add_argument("--backtest", action="store_true")
    ap.add_argument("--synthetic", choices=("edge", "noedge"))
    ap.add_argument("--cache")
    ap.add_argument("--symbols")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--equity", type=float, default=100.0)
    args = ap.parse_args()
    cfg = Config()

    if args.scan:
        rows = scan_live(cfg)
        print(f"{'symbol':<14}{'now':>9}{'avg3d':>9}{'every':>7}{'gross APR':>11}{'net 7d':>9}{'pos%':>6}")
        for r in rows[:20]:
            print(f"{r['symbol']:<14}{r['funding_now'] * 100:>8.3f}%{r['avg_3d'] * 100:>8.3f}%{r['interval_h']:>6.0f}h"
                  f"{r['gross_apr'] * 100:>10.1f}%{r['net_hold_pct'] * 100:>8.2f}%{r['positive_share'] * 100:>5.0f}%")
        if not rows:
            print("No carry above the entry threshold right now: that is normal, the sleeve then stays in cash.")
    if args.backtest:
        from .backtest import load_data

        data = load_data(cfg, args.synthetic, args.symbols, args.top, args.days, args.cache)
        print(backtest_carry(data, cfg, args.equity).summary())


if __name__ == "__main__":
    main()
