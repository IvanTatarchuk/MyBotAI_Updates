"""Anti-self-deception checks: a strategy must pass all of them before it touches real money.

1. Walk-forward: parameters are chosen on the past only and scored on the following, unseen period.
   Only out-of-sample (OOS) trades count.
2. Parameter plateau: a real edge survives neighbouring settings; a lucky spike does not.
3. Monte Carlo: reshuffle/bootstrap the OOS trades to estimate the chance of hitting the kill switch.

Usage:
    python -m altcoin_squeeze_bot.validate --days 180 --top 25 --cache data/bars.json
    python -m altcoin_squeeze_bot.validate --synthetic noedge   # must FAIL: proves the checks bite
"""

from __future__ import annotations

import argparse
import bisect
import itertools
import math
import random
from dataclasses import dataclass, replace

from .backtest import load_data, run
from .config import Config
from .strategy import Bar, Features, precompute_features

# Keys are "<config section>.<field>". Each directional strategy is validated on its own grid.
GRIDS: dict[str, dict[str, list[float]]] = {
    "squeeze": {
        "strategy.z_arm": [1.5, 2.0, 2.5],
        "strategy.oi_rise_min": [0.04, 0.06, 0.09],
        "strategy.tp1_r": [1.0, 1.5, 2.0],
    },
    "trend": {
        "trend.donchian": [96, 192, 384],
        "trend.stop_atr": [3.0, 5.0, 7.0],
        "trend.trail_atr": [4.0, 6.0, 8.0],
    },
    "tarot": {
        "tarot.horizon": [8, 16, 32],
        "tarot.t_min": [2.0, 2.5, 3.0],
        "tarot.stop_atr": [1.5, 2.0, 3.0],
    },
}
DEFAULT_GRID = GRIDS["squeeze"]


@dataclass
class Stats:
    n: int
    expectancy: float  # mean R per trade
    win_rate: float
    profit_factor: float
    t_stat: float  # expectancy / standard error; > 2 means unlikely to be pure luck

    def __str__(self) -> str:
        pf = "inf" if math.isinf(self.profit_factor) else f"{self.profit_factor:.2f}"
        return (f"trades={self.n:<4} E[R]={self.expectancy:+.3f}  win={self.win_rate * 100:5.1f}%  "
                f"PF={pf:<5} t={self.t_stat:+.2f}")


def stats(rs: list[float]) -> Stats:
    n = len(rs)
    if n == 0:
        return Stats(0, 0.0, 0.0, 0.0, 0.0)
    mean = sum(rs) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rs) / (n - 1)) if n > 1 else 0.0
    wins = sum(r for r in rs if r > 0)
    losses = -sum(r for r in rs if r <= 0)
    pf = wins / losses if losses > 0 else math.inf
    t = mean / (sd / math.sqrt(n)) if sd > 0 else 0.0
    return Stats(n, mean, sum(1 for r in rs if r > 0) / n, pf, t)


def grid_configs(base: Config, grid: dict[str, list[float]]) -> list[tuple[dict[str, float], Config]]:
    keys = list(grid)
    out = []
    for combo in itertools.product(*(grid[k] for k in keys)):
        params = dict(zip(keys, combo, strict=True))
        cfg = base
        for key, value in params.items():
            section, name = key.split(".") if "." in key else ("strategy", key)
            value = int(value) if isinstance(getattr(getattr(cfg, section), name), int) else value
            cfg = replace(cfg, **{section: replace(getattr(cfg, section), **{name: value})})
        out.append((params, cfg))
    return out


def slice_period(
    data: dict[str, list[Bar]], feats: dict[str, list[Features | None]], t0: int, t1: int, warmup_bars: int
) -> tuple[dict[str, list[Bar]], dict[str, list[Features | None]]]:
    """Bars in [t0, t1) plus a few warm-up bars so the detector can be armed at t0.

    Features were computed on the full history, but each one only looks backwards, so no lookahead.
    """
    d, f = {}, {}
    for s, bars in data.items():
        ts = [b.ts for b in bars]
        first = bisect.bisect_left(ts, t0)
        lo = max(0, first - warmup_bars)
        hi = bisect.bisect_left(ts, t1)
        if hi > first:  # the symbol has bars inside the period itself
            d[s], f[s] = bars[lo:hi], feats[s][lo:hi]
    return d, f


def r_multiples(data, feats, cfg: Config, t0: int, t1: int) -> list[float]:
    warmup = cfg.strategy.arm_ttl_bars + cfg.strategy.crowd_window
    if "tarot" in cfg.enabled:
        warmup = 10**9  # the tarot reader learns card meanings online: give it all earlier history
    d, f = slice_period(data, feats, t0, t1, warmup)
    if not d:
        return []
    return [t.r_multiple for t in run(d, cfg, 100.0, f).trades if t.entry_ts >= t0]


def score(s: Stats, min_trades: int) -> float:
    return s.t_stat if s.n >= min_trades else -math.inf


@dataclass
class WalkForward:
    oos: list[float]
    folds: list[tuple[dict[str, float], Stats, Stats]]  # chosen params, in-sample stats, OOS stats


def walk_forward(
    data, feats, base: Config, grid: dict[str, list[float]], n_folds: int = 4, min_trades: int = 10
) -> WalkForward:
    """Anchored walk-forward: train on segments [0, k), test on segment k, for k = 1..n_folds."""
    t_min = min(b[0].ts for b in data.values())
    t_max = max(b[-1].ts for b in data.values()) + 1
    edges = [t_min + (t_max - t_min) * k // (n_folds + 1) for k in range(n_folds + 2)]
    configs = grid_configs(base, grid)
    wf = WalkForward([], [])
    for k in range(1, n_folds + 1):
        best = max(configs, key=lambda pc: score(stats(r_multiples(data, feats, pc[1], edges[0], edges[k])),
                                                 min_trades))
        is_stats = stats(r_multiples(data, feats, best[1], edges[0], edges[k]))
        oos_rs = r_multiples(data, feats, best[1], edges[k], edges[k + 1])
        wf.oos += oos_rs
        wf.folds.append((best[0], is_stats, stats(oos_rs)))
    return wf


def plateau(data, feats, base: Config, grid: dict[str, list[float]]) -> list[tuple[dict[str, float], Stats]]:
    t0 = min(b[0].ts for b in data.values())
    t1 = max(b[-1].ts for b in data.values()) + 1
    return [(p, stats(r_multiples(data, feats, c, t0, t1))) for p, c in grid_configs(base, grid)]


@dataclass
class MonteCarlo:
    median_return: float
    p5_return: float  # bad-luck (5th percentile) outcome
    median_dd: float
    p95_dd: float
    p_kill: float  # probability the drawdown reaches the kill switch


def monte_carlo(rs: list[float], risk: float, kill_dd: float, sims: int = 5000, seed: int = 7) -> MonteCarlo:
    if not rs:
        return MonteCarlo(0.0, 0.0, 0.0, 0.0, 0.0)
    rng = random.Random(seed)
    finals, dds, kills = [], [], 0
    for _ in range(sims):
        eq = peak = 1.0
        dd = 0.0
        for _ in rs:
            eq *= 1 + rng.choice(rs) * risk
            peak = max(peak, eq)
            dd = max(dd, 1 - eq / peak)
        finals.append(eq - 1)
        dds.append(dd)
        kills += dd >= kill_dd
    finals.sort()
    dds.sort()
    return MonteCarlo(finals[sims // 2], finals[sims // 20], dds[sims // 2], dds[sims * 19 // 20], kills / sims)


def verdict(oos: Stats, plateau_share: float, mc: MonteCarlo) -> list[tuple[bool, str]]:
    return [
        (oos.n >= 30, f"OOS trades >= 30 (got {oos.n})"),
        (oos.expectancy > 0, f"OOS expectancy > 0 (got {oos.expectancy:+.3f}R)"),
        (oos.profit_factor > 1.2, f"OOS profit factor > 1.2 (got {oos.profit_factor:.2f})"),
        (oos.t_stat > 2.0, f"OOS t-stat > 2 (got {oos.t_stat:+.2f})"),
        (plateau_share >= 0.5, f">= 50% of parameter grid profitable (got {plateau_share * 100:.0f}%)"),
        (mc.p_kill < 0.10, f"P(kill switch) < 10% (got {mc.p_kill * 100:.1f}%)"),
    ]


def validate_strategy(name: str, data, feats, base: Config, folds: int) -> bool:
    cfg = replace(base, enabled=(name,))
    grid = GRIDS[name]
    print(f"\n################ {name.upper()} ################")
    print(f"== Walk-forward ({folds} folds, grid of {len(grid_configs(cfg, grid))}) ==")
    wf = walk_forward(data, feats, cfg, grid, folds)
    for k, (params, is_s, oos_s) in enumerate(wf.folds, 1):
        print(f"fold {k}: {params}\n   in-sample : {is_s}\n   OUT-sample: {oos_s}")
    oos = stats(wf.oos)
    print(f"ALL OOS     : {oos}")

    print("== Parameter plateau (full period, best 5 / worst 3) ==")
    pl = sorted(plateau(data, feats, cfg, grid), key=lambda x: -x[1].expectancy)
    for p, s in pl[:5] + pl[-3:]:
        print(f"  {p}  {s}")
    share = sum(1 for _, s in pl if s.n > 0 and s.expectancy > 0) / len(pl)

    print("== Monte Carlo on OOS trades ==")
    mc = monte_carlo(wf.oos, cfg.risk.risk_per_trade, cfg.risk.max_drawdown)
    print(f"  median return {mc.median_return * 100:+.1f}% | bad luck (5%) {mc.p5_return * 100:+.1f}%")
    print(f"  median max DD {mc.median_dd * 100:.1f}% | worst 5% DD {mc.p95_dd * 100:.1f}% | "
          f"P(kill) {mc.p_kill * 100:.1f}%")

    print("== Verdict ==")
    checks = verdict(oos, share, mc)
    for ok, text in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {text}")
    return all(ok for ok, _ in checks)


def main() -> None:
    ap = argparse.ArgumentParser(description="Walk-forward, plateau and Monte Carlo validation")
    ap.add_argument("--synthetic", choices=("edge", "noedge"), help="generated data, no network")
    ap.add_argument("--symbols")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--cache")
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--strategies", default="squeeze,trend")
    args = ap.parse_args()

    cfg = Config()
    data = load_data(cfg, args.synthetic, args.symbols, args.top, args.days, args.cache)
    print("precomputing features ...")
    feats = {s: precompute_features(b, cfg.strategy) for s, b in data.items()}

    results = {name: validate_strategy(name, data, feats, cfg, args.folds) for name in args.strategies.split(",")}
    print("\n================ SUMMARY ================")
    for name, ok in results.items():
        print(f"  {name:<8} {'PASS -> may be enabled' if ok else 'FAIL -> keep disabled'}")
    passed = [n for n, ok in results.items() if ok]
    if passed:
        print(f"\nNext: set Config.enabled = {tuple(passed)} and paper trade 2-4 weeks, then testnet.")
    else:
        print("\nDO NOT TRADE REAL MONEY: no strategy passed on this data.")


if __name__ == "__main__":
    main()
