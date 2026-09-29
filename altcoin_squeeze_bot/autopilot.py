"""Autopilot: analyse all coins, learn the pattern that precedes big rallies, trade it, re-learn regularly.

Learning (learn_rule)
    prepump.analyze_prepared finds decile zones that precede +20%/24h pumps on half of the coins and are
    confirmed on the other half. Singles and pairs of those zones (different features) become candidate
    rules; the rule kept is the one whose pump rate is highest on BOTH coin groups while favouring pumps
    over dumps and having enough independent samples. No zone -> no rule -> the autopilot does not trade.

Trading (RuleDetector)
    Buy when all conditions of the rule hold on a closed bar. Exit at +take_profit (default +28%), at
    -stop_loss (default -8%), or after `horizon` bars, whichever comes first. The rule is learned to
    predict a move of exactly the take-profit size.

Honest evaluation (walk_forward)
    Re-learn every `retrain_days` using only data known at that moment, then trade the next period with
    the rule it produced. Only those next-period trades are scored, so the pipeline is tested exactly as it
    would have run live. The usual Monte Carlo and verdict follow.

    python -m altcoin_squeeze_bot.autopilot validate --synthetic signature
    python -m altcoin_squeeze_bot.autopilot validate --top 40 --days 180 --cache data/prepump.json
    python -m altcoin_squeeze_bot.autopilot learn --top 40 --days 120 --out rule.json   # rule for the bot
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import asdict, dataclass, field

from .config import Config
from .prepump import Prepared, analyze_prepared, coin_features, prepare, repeating, split_coins
from .strategy import Bar, Exits, Signal

DAY_MS = 86_400_000


@dataclass
class Condition:
    feature: str
    lo: float
    hi: float

    def holds(self, f: dict[str, float]) -> bool:
        return self.lo < f[self.feature] <= self.hi if math.isfinite(self.lo) else f[self.feature] <= self.hi

    def __str__(self) -> str:
        if not math.isfinite(self.lo):
            return f"{self.feature} <= {self.hi:.4g}"
        if not math.isfinite(self.hi):
            return f"{self.feature} > {self.lo:.4g}"
        return f"{self.lo:.4g} < {self.feature} <= {self.hi:.4g}"


@dataclass
class Rule:
    conditions: list[Condition]
    pump_rate: float  # P(+threshold within horizon | rule) on learning data
    base_rate: float  # P(+threshold within horizon) overall
    lift_a: float
    lift_b: float
    samples: int  # independent (thinned) samples where the rule held
    learned_until: int  # ms: the rule saw nothing after this moment
    threshold: float = 0.28
    horizon_h: int = 24
    take_profit: float = 0.28
    stop_loss: float = 0.08
    notes: list[str] = field(default_factory=list)

    def holds(self, f: dict[str, float] | None) -> bool:
        return f is not None and all(c.holds(f) for c in self.conditions)

    def describe(self) -> str:
        cond = "  AND  ".join(str(c) for c in self.conditions)
        return (f"BUY when {cond}\n"
                f"  pump rate {self.pump_rate * 100:.1f}% vs base {self.base_rate * 100:.1f}% "
                f"(lift A {self.lift_a:.1f}, B {self.lift_b:.1f}, {self.samples} independent samples)\n"
                f"  exit: +{self.take_profit * 100:.0f}% / -{self.stop_loss * 100:.0f}% / after {self.horizon_h}h")

    def to_json(self) -> str:
        d = asdict(self)
        for c in d["conditions"]:
            c["lo"] = None if not math.isfinite(c["lo"]) else c["lo"]
            c["hi"] = None if not math.isfinite(c["hi"]) else c["hi"]
        return json.dumps(d, indent=2)

    @classmethod
    def from_json(cls, text: str) -> Rule:
        d = json.loads(text)
        d["conditions"] = [Condition(c["feature"], -math.inf if c["lo"] is None else c["lo"],
                                     math.inf if c["hi"] is None else c["hi"]) for c in d["conditions"]]
        return cls(**d)


# ---- learning -----------------------------------------------------------------------------------
def _rule_stats(prep: Prepared, conds: list[Condition], symbols: set[str], cutoff: int | None):
    n = hits = dumps = 0
    tn = thits = 0
    total = total_hits = total_dumps = 0
    for s in symbols:
        for i, f, up, down in prep.rows(s, cutoff):
            total += 1
            total_hits += up
            total_dumps += down
            if all(c.holds(f) for c in conds):
                n += 1
                hits += up
                dumps += down
                if i % prep.horizon == 0:
                    tn += 1
                    thits += up
    base = total_hits / total if total else 0.0
    base_d = total_dumps / total if total else 0.0
    rate = hits / n if n else 0.0
    rate_d = dumps / n if n else 0.0
    lift = rate / base if base else 0.0
    direction = (rate / base) / (rate_d / base_d) if rate_d > 0 and base_d > 0 and base > 0 else math.inf
    return rate, base, lift, direction, tn


TAKE_PROFIT = 0.28
STOP_LOSS = 0.08


def learn_rule(prep: Prepared, cutoff: int | None = None, seed: int = 7, max_zones: int = 6,
               min_lift: float = 2.0, min_samples: int = 15, min_dir: float = 1.5,
               take_profit: float = TAKE_PROFIT, stop_loss: float = STOP_LOSS) -> Rule | None:
    """Learn the rule. `prep` should be prepared with threshold == take_profit, so the rule is trained to
    predict exactly the move it will try to capture."""
    results, _ = analyze_prepared(prep, cutoff, seed)
    zones = repeating(results)[:max_zones]
    if not zones:
        return None
    group_a, group_b = split_coins(prep.coins, seed)
    everyone = group_a | group_b
    cands = [[z] for z in zones] + [list(p) for p in itertools.combinations(zones, 2) if p[0].feature != p[1].feature]
    best: tuple[float, Rule] | None = None
    for zs in cands:
        conds = [Condition(z.feature, z.lo, z.hi) for z in zs]
        _, _, lift_a, dir_a, _ = _rule_stats(prep, conds, group_a, cutoff)
        _, _, lift_b, dir_b, _ = _rule_stats(prep, conds, group_b, cutoff)
        rate, base, _, _, samples = _rule_stats(prep, conds, everyone, cutoff)
        if min(lift_a, lift_b) < min_lift or min(dir_a, dir_b) < min_dir or samples < min_samples:
            continue
        score = min(lift_a, lift_b)
        if best is None or score > best[0]:
            last_ts = max(c.ts[-1] for c in prep.coins.values())
            best = (score, Rule(conds, rate, base, lift_a, lift_b, samples, cutoff or last_ts, prep.threshold,
                                prep.horizon // prep.bars_per_hour, take_profit, stop_loss))
    return best[1] if best else None


# ---- trading ------------------------------------------------------------------------------------
class RuleDetector:
    """Signals a long when the learned rule holds. Features are looked up by timestamp when precomputed
    (backtests) or computed from the bars themselves (live)."""

    name = "autopilot"

    def __init__(self, rule: Rule, bars_per_hour: int = 1, lookup: dict[int, dict[str, float] | None] | None = None):
        self.rule, self.bph, self.lookup = rule, bars_per_hour, lookup
        self._key: tuple[int, int] | None = None
        self._feats: list[dict[str, float] | None] = []

    @property
    def min_history(self) -> int:
        return 31 * 24 * self.bph

    def _features(self, bars: list[Bar], i: int) -> dict[str, float] | None:
        if self.lookup is not None:
            return self.lookup.get(bars[i].ts)
        key = (id(bars), len(bars))
        if key != self._key:
            self._feats, self._key = coin_features(bars, self.bph), key
        return self._feats[i]

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        if not self.rule.holds(self._features(bars, i)):
            return None
        b = bars[i]
        stop = b.close * (1 - self.rule.stop_loss)
        return Signal("Buy", b.close, stop, b.close - stop, self.rule.lift_b, b.ts, self.name)


def rule_exits(rule: Rule, bars_per_hour: int = 1) -> Exits:
    return Exits(tp1_r=rule.take_profit / rule.stop_loss, tp1_fraction=1.0, trail_atr=0.0,
                 max_hold_bars=rule.horizon_h * bars_per_hour, atr_period=14)


def as_pseudo_coins(bars: list[Bar], chunk_days: int = 182, warmup_days: int = 31) -> dict[str, list[Bar]]:
    """Cut one long history into periods that act as separate "coins", so the discovery/confirmation split
    becomes a split across different years. Each chunk carries `warmup_days` of preceding bars; features are
    None there, so no bar is ever counted twice."""
    import time as _time

    if not bars:
        return {}
    out: dict[str, list[Bar]] = {}
    start = bars[0].ts
    while start <= bars[-1].ts:
        end = start + chunk_days * DAY_MS
        chunk = [b for b in bars if start - warmup_days * DAY_MS <= b.ts < end]
        if sum(1 for b in chunk if b.ts >= start) > 24 * 7:
            t = _time.gmtime(start / 1000)
            out[f"P{t.tm_year}-{t.tm_mon:02d}"] = chunk
        start = end
    return out


# ---- honest evaluation --------------------------------------------------------------------------
@dataclass
class Period:
    start: int
    end: int
    rule: Rule | None
    r_multiples: list[float]


def walk_forward(data: dict[str, list[Bar]], cfg: Config, retrain_days: int = 30, warmup_days: int = 60,
                 bars_per_hour: int = 1, prep: Prepared | None = None, take_profit: float = TAKE_PROFIT,
                 stop_loss: float = STOP_LOSS, horizon_h: int = 24) -> list[Period]:
    from dataclasses import replace

    from .backtest import run
    from .validate import measurement_config

    prep = prep or prepare(data, bars_per_hour, horizon_h, take_profit)
    t_min = min(b[0].ts for b in data.values())
    t_max = max(b[-1].ts for b in data.values()) + 1
    periods: list[Period] = []
    t = t_min + warmup_days * DAY_MS
    base_cfg = measurement_config(replace(cfg, enabled=("autopilot",)))
    lookups = {s: dict(zip(c.ts, c.feats, strict=True)) for s, c in prep.coins.items()}
    while t < t_max:
        end = min(t + retrain_days * DAY_MS, t_max)
        rule = learn_rule(prep, cutoff=t, take_profit=take_profit, stop_loss=stop_loss)
        rs: list[float] = []
        if rule is not None:
            run_cfg = replace(base_cfg, autopilot_rule=rule)
            window = {s: [b for b in bars if t - 2 * DAY_MS <= b.ts < end] for s, bars in data.items()}
            window = {s: b for s, b in window.items() if b}
            res = run(window, run_cfg, 1_000_000.0, autopilot_lookup=lookups)
            rs = [tr.r_multiple for tr in res.trades if tr.entry_ts >= t]
        periods.append(Period(t, end, rule, rs))
        t = end
    return periods


def main() -> None:
    import os
    import time

    from .validate import monte_carlo, stats, verdict

    ap = argparse.ArgumentParser(description="Learn the pre-pump pattern of all coins and trade it")
    ap.add_argument("command", choices=("learn", "validate"))
    ap.add_argument("--synthetic", choices=("signature", "nosignature"))
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--cache", help="JSON cache of 1h bars (shared with prepump)")
    ap.add_argument("--csv", help="Binance 1h kline CSV; a single coin is cut into half-year pseudo-coins")
    ap.add_argument("--retrain-days", type=int, default=30)
    ap.add_argument("--out", default="autopilot_rule.json", help="where `learn` writes the rule")
    ap.add_argument("--take-profit", type=float, default=TAKE_PROFIT, help="e.g. 0.28 = +28%%")
    ap.add_argument("--stop-loss", type=float, default=STOP_LOSS, help="e.g. 0.08 = -8%%")
    ap.add_argument("--horizon", type=int, default=24, help="hours the move has to happen in (also the time exit)")
    args = ap.parse_args()

    cfg = Config()
    cfg.strategy.interval_min = 60
    if args.csv:
        from .data import load_binance_csv

        data = {}
        for path in args.csv.split(","):
            data.update(load_binance_csv(path))
        if len(data) == 1:
            data = as_pseudo_coins(next(iter(data.values())))
            print(f"single coin -> {len(data)} half-year periods used as separate coins: {', '.join(data)}")
    elif args.synthetic:
        from .prepump import synthetic_coins

        data = synthetic_coins(signature=args.synthetic == "signature")
    else:
        from .bybit_client import BybitClient
        from .data import btc_close_map, fetch_bars, load_bars, save_bars, select_universe

        if args.cache and os.path.exists(args.cache):
            data = load_bars(args.cache)
        else:
            cfg.universe.max_symbols = args.top
            client = BybitClient()
            end = int(time.time() * 1000)
            start = end - args.days * DAY_MS
            btc = btc_close_map(client, 60, start, end)
            data = {}
            for s in select_universe(client.tickers(), cfg.universe):
                print(f"downloading {s} ...")
                data[s] = fetch_bars(client, s, 60, start, end, btc)
            if args.cache:
                save_bars(args.cache, data)

    day = lambda ms: time.strftime("%Y-%m-%d", time.gmtime(ms / 1000))  # noqa: E731
    prep = prepare(data, 1, args.horizon, args.take_profit)  # learn to predict exactly the take-profit move
    if args.command == "learn":
        rule = learn_rule(prep, take_profit=args.take_profit, stop_loss=args.stop_loss)
        if rule is None:
            print("No repeating pre-pump pattern found -> no rule written; the autopilot stays flat.")
            return
        with open(args.out, "w") as fh:
            fh.write(rule.to_json())
        print(rule.describe())
        print(f"\nsaved to {args.out}. Run `validate` first: only trade it if the walk-forward verdict passes.")
        return

    periods = walk_forward(data, cfg, args.retrain_days, prep=prep, take_profit=args.take_profit,
                           stop_loss=args.stop_loss, horizon_h=args.horizon)
    print(f"{len(data)} coins | re-learning every {args.retrain_days} days on past data only\n")
    all_rs: list[float] = []
    for p in periods:
        head = f"{day(p.start)} .. {day(p.end)}"
        if p.rule is None:
            print(f"{head}: no pattern found -> no trading")
            continue
        print(f"{head}: {' AND '.join(str(c) for c in p.rule.conditions)}")
        print(f"   next-period trades: {stats(p.r_multiples)}")
        all_rs += p.r_multiples
    oos = stats(all_rs)
    print(f"\nALL next-period trades: {oos}")
    mc = monte_carlo(all_rs, cfg.risk.risk_per_trade, cfg.risk.max_drawdown)
    print(f"Monte Carlo: median {mc.median_return * 100:+.1f}% | bad luck (5%) {mc.p5_return * 100:+.1f}% | "
          f"P(kill) {mc.p_kill * 100:.1f}%")
    rules = [p for p in periods if p.rule]
    feature_sets = {tuple(c.feature for c in p.rule.conditions) for p in rules}
    stable = bool(rules) and len(feature_sets) <= max(1, len(rules) // 2)
    checks = verdict(oos, 1.0 if stable else 0.0, mc)
    checks[4] = (stable, f"pattern is stable across re-learning ({'yes' if stable else 'no'})")
    for ok, text in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {text}")
    print("\nAUTOPILOT MAY TRADE" if all(ok for ok, _ in checks) else "\nAUTOPILOT MUST NOT TRADE REAL MONEY")


if __name__ == "__main__":
    main()
