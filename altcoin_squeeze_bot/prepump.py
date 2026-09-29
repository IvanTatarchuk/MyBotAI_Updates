"""Pre-pump analyzer: what do altcoins have in common right BEFORE a big rally?

1. Pumps: bar i is labelled "pump ahead" when the highest high over the next `horizon` bars is
   >= `threshold` above its close, i.e. buying there would have caught the move. EVERY bar is labelled:
   keeping only the first qualifying bar of each move would be biased (that bar is typically right after a
   dip, so "buy the dip" would appear even in a random walk). Significance is computed on every
   `horizon`-th bar only, so overlapping windows do not inflate it.
2. Snapshot: ~20 features describing the coin at bar i, computed only from bars <= i.
3. Lift: pooled over coins, features are cut into deciles; lift = P(pump | decile) / P(pump).
   A decile with lift 3 means pumps start three times more often than usual in that state.
4. Repeats?: coins are split in two groups. Deciles are found on group A and must show the same
   lift on group B (coins the discovery never saw) and on the majority of individual B coins.

    python -m altcoin_squeeze_bot.prepump --top 40 --days 180 --cache data/prepump.json
    python -m altcoin_squeeze_bot.prepump --synthetic          # planted pre-pump signature: must be found
"""

from __future__ import annotations

import argparse
import bisect
import math
import random
from dataclasses import dataclass
from statistics import NormalDist

from .strategy import Bar

FEATURES = [
    "ret_1h", "ret_4h", "ret_24h", "ret_7d",  # recent moves (z-scored by the coin's own volatility)
    "resid_24h",  # move vs BTC over 24h (coin-specific strength)
    "vol_ratio",  # ATR 1 day / ATR 7 days (<1 = compression, >1 = expansion)
    "range_24h",  # 24h high-low range / price, in units of the coin's volatility
    "volume_ratio_4h",  # last 4h volume / average 4h volume over 7 days
    "volume_trend_24h",  # last 24h volume / previous 24h volume
    "oi_change_4h", "oi_change_24h",  # open interest growth
    "oi_vs_price_24h",  # OI growth minus price growth (positions built without price moving)
    "funding",  # current funding rate (negative = shorts pay = crowded shorts)
    "dist_from_30d_high",  # how far below the 30-day high (0 = at the high)
    "dist_from_30d_low",  # how far above the 30-day low
    "btc_ret_24h",  # market backdrop
    "green_share_24h",  # share of green bars in the last 24h
    "hour_utc",
]


def _z(x: float, sd: float, n: int) -> float:
    return x / (sd * math.sqrt(n)) if sd > 0 else 0.0


def coin_features(bars: list[Bar], bars_per_hour: int = 1) -> list[dict[str, float] | None]:
    """Feature snapshot per bar (None during warm-up). Only bars <= i are used for bar i."""
    h = bars_per_hour
    d = 24 * h
    w = 7 * d
    m30 = 30 * d
    n = len(bars)
    out: list[dict[str, float] | None] = [None] * n
    rets = [0.0] + [bars[i].close / bars[i - 1].close - 1 for i in range(1, n)]
    btc = [0.0] + [bars[i].btc_close / bars[i - 1].btc_close - 1 if bars[i - 1].btc_close else 0.0
                   for i in range(1, n)]
    trs = [0.0] + [max(bars[i].high - bars[i].low, abs(bars[i].high - bars[i - 1].close),
                       abs(bars[i].low - bars[i - 1].close)) for i in range(1, n)]
    start = max(w, min(m30, n // 3)) + 1
    for i in range(start, n):
        b = bars[i]
        window = rets[i - w + 1 : i + 1]
        mean = sum(window) / w
        sd = math.sqrt(max(sum((r - mean) ** 2 for r in window) / w, 1e-18))
        bw = btc[i - w + 1 : i + 1]
        mb = sum(bw) / w
        var_b = sum((x - mb) ** 2 for x in bw) / w
        beta = (sum((window[k] - mean) * (bw[k] - mb) for k in range(w)) / w / var_b) if var_b > 0 else 0.0
        r24 = b.close / bars[i - d].close - 1
        b24 = b.btc_close / bars[i - d].btc_close - 1 if bars[i - d].btc_close else 0.0
        atr_d = sum(trs[i - d + 1 : i + 1]) / d
        atr_w = sum(trs[i - w + 1 : i + 1]) / w
        vol4 = sum(x.volume for x in bars[i - 4 * h + 1 : i + 1])
        vol_w = sum(x.volume for x in bars[i - w + 1 : i + 1]) / (w / (4 * h))
        v24 = sum(x.volume for x in bars[i - d + 1 : i + 1])
        v24p = sum(x.volume for x in bars[i - 2 * d + 1 : i - d + 1])
        lookback = bars[max(0, i - m30 + 1) : i + 1]
        hi30 = max(x.high for x in lookback)
        lo30 = min(x.low for x in lookback)
        oi4 = b.oi / bars[i - 4 * h].oi - 1 if bars[i - 4 * h].oi else 0.0
        oi24 = b.oi / bars[i - d].oi - 1 if bars[i - d].oi else 0.0
        out[i] = {
            "ret_1h": _z(b.close / bars[i - h].close - 1, sd, h),
            "ret_4h": _z(b.close / bars[i - 4 * h].close - 1, sd, 4 * h),
            "ret_24h": _z(r24, sd, d),
            "ret_7d": _z(b.close / bars[i - w].close - 1, sd, w),
            "resid_24h": _z(r24 - beta * b24, sd, d),
            "vol_ratio": atr_d / atr_w if atr_w > 0 else 1.0,
            "range_24h": _z(max(x.high for x in bars[i - d + 1 : i + 1]) / min(x.low for x in bars[i - d + 1 : i + 1])
                            - 1, sd, d),
            "volume_ratio_4h": vol4 / vol_w if vol_w > 0 else 1.0,
            "volume_trend_24h": v24 / v24p if v24p > 0 else 1.0,
            "oi_change_4h": oi4,
            "oi_change_24h": oi24,
            "oi_vs_price_24h": oi24 - r24,
            "funding": b.funding,
            "dist_from_30d_high": b.close / hi30 - 1,
            "dist_from_30d_low": b.close / lo30 - 1,
            "btc_ret_24h": b24,
            "green_share_24h": sum(1 for r in rets[i - d + 1 : i + 1] if r > 0) / d,
            "hour_utc": (b.ts // 3_600_000) % 24,
        }
    return out


def pump_starts(bars: list[Bar], horizon: int, threshold: float, down: bool = False) -> set[int]:
    """First bar of each move of >= threshold within `horizon` bars (up), or the mirror move (down):
    a +20% pump is mirrored by a -16.7% dump (same size in log terms)."""
    starts: set[int] = set()
    i = 0
    n = len(bars)
    dump_level = 1 / (1 + threshold) - 1
    while i < n - horizon:
        window = bars[i + 1 : i + 1 + horizon]
        hit = (min(b.low for b in window) / bars[i].close - 1 <= dump_level) if down else (
            max(b.high for b in window) / bars[i].close - 1 >= threshold)
        if hit:
            starts.add(i)
            i += horizon  # one event per move
        else:
            i += 1
    return starts


@dataclass
class DecileLift:
    feature: str
    decile: int  # 0 = lowest 10% of values, 9 = highest
    lo: float
    hi: float
    lift_a: float
    lift_b: float
    coins_b_agree: float  # share of B coins where this decile has lift > 1
    pumps_b: int  # independent (thinned) pump samples in this decile, group B
    dir_a: float  # pump lift / dump lift: > 1 means the state favours UP moves, not just any big move
    dir_b: float
    z_b: float  # significance of the excess pumps in group B (Poisson z-score)


def _poisson_z(observed: int, expected: float) -> float:
    return (observed - expected) / math.sqrt(expected) if expected > 0 else 0.0


def move_labels(bars: list[Bar], horizon: int, threshold: float, down: bool = False) -> list[bool]:
    """For every bar: is a move of >= threshold (or the mirror dump) reachable within `horizon` bars?"""
    n = len(bars)
    dump_level = 1 / (1 + threshold) - 1
    out = [False] * n
    for i in range(n - horizon):
        window = bars[i + 1 : i + 1 + horizon]
        if down:
            out[i] = min(b.low for b in window) / bars[i].close - 1 <= dump_level
        else:
            out[i] = max(b.high for b in window) / bars[i].close - 1 >= threshold
    return out


def _lifts(rows: list[tuple[float, bool]], edges: list[float]) -> tuple[list[float], list[int], list[int]]:
    counts, pumps = [0] * 10, [0] * 10
    for v, p in rows:
        k = bisect.bisect_right(edges, v)
        counts[k] += 1
        pumps[k] += p
    total_p = sum(pumps) / max(1, sum(counts))
    lifts = [(pumps[k] / counts[k]) / total_p if counts[k] and total_p > 0 else 0.0 for k in range(10)]
    return lifts, counts, pumps


def analyze(data: dict[str, list[Bar]], bars_per_hour: int = 1, horizon_h: int = 24, threshold: float = 0.20,
            seed: int = 7) -> tuple[list[DecileLift], dict]:
    coins = sorted(data)
    random.Random(seed).shuffle(coins)
    group_a, group_b = set(coins[: len(coins) // 2]), set(coins[len(coins) // 2 :])
    horizon = horizon_h * bars_per_hour
    per_coin: dict[str, list[tuple[dict[str, float], bool, bool]]] = {}
    thin: dict[str, list[tuple[dict[str, float], bool]]] = {}  # every horizon-th bar: ~independent samples
    n_pumps = n_dumps = 0
    for sym, bars in data.items():
        feats = coin_features(bars, bars_per_hour)
        ups = move_labels(bars, horizon, threshold)
        downs = move_labels(bars, horizon, threshold, down=True)
        n_pumps += len(pump_starts(bars, horizon, threshold))
        n_dumps += len(pump_starts(bars, horizon, threshold, down=True))
        last = len(bars) - horizon  # labels need `horizon` future bars
        per_coin[sym] = [(f, ups[i], downs[i]) for i, f in enumerate(feats) if f is not None and i < last]
        thin[sym] = [(f, ups[i]) for i, f in enumerate(feats) if f is not None and i < last and i % horizon == 0]

    results: list[DecileLift] = []
    for feat in FEATURES:
        a_rows = [(f[feat], p) for s in group_a for f, p, _ in per_coin[s]]
        b_rows = [(f[feat], p) for s in group_b for f, p, _ in per_coin[s]]
        if not a_rows or not b_rows or not any(p for _, p in a_rows):
            continue
        vals = sorted(v for v, _ in a_rows)
        edges = [vals[len(vals) * k // 10] for k in range(1, 10)]
        lift_a, _, _ = _lifts(a_rows, edges)
        lift_b, _, _ = _lifts(b_rows, edges)
        _, counts_b, pumps_b = _lifts([(f[feat], p) for s in group_b for f, p in thin[s]], edges)
        rate_b = sum(pumps_b) / max(1, sum(counts_b))
        dump_a, _, _ = _lifts([(f[feat], d) for s in group_a for f, _, d in per_coin[s]], edges)
        dump_b, _, _ = _lifts([(f[feat], d) for s in group_b for f, _, d in per_coin[s]], edges)
        per_b = {s: _lifts([(f[feat], p) for f, p, _ in per_coin[s]], edges)[0]
                 for s in group_b if any(p for _, p, _ in per_coin[s])}
        for k in range(10):
            agree = [lifts[k] > 1 for lifts in per_b.values()]
            lo = edges[k - 1] if k else -math.inf
            hi = edges[k] if k < 9 else math.inf
            results.append(DecileLift(
                feat, k, lo, hi, lift_a[k], lift_b[k], sum(agree) / len(agree) if agree else 0.0, pumps_b[k],
                lift_a[k] / dump_a[k] if dump_a[k] > 0 else math.inf,
                lift_b[k] / dump_b[k] if dump_b[k] > 0 else math.inf,
                _poisson_z(pumps_b[k], rate_b * counts_b[k]),
            ))
    meta = {"coins": len(coins), "group_a": sorted(group_a), "group_b": sorted(group_b), "pumps": n_pumps,
            "dumps": n_dumps}
    return results, meta


def repeating(results: list[DecileLift], min_lift: float = 1.5, min_agree: float = 0.6,
              min_pumps: int = 10, min_dir: float = 1.5, alpha: float = 0.05) -> list[DecileLift]:
    """Deciles that favour pumps on both coin groups, favour UP over DOWN moves, hold on most individual
    confirmation coins, and whose excess in the confirmation group survives a Bonferroni correction."""
    z_min = NormalDist().inv_cdf(1 - alpha / max(1, len(results)))
    return sorted(
        (r for r in results if r.lift_a >= min_lift and r.lift_b >= min_lift and r.coins_b_agree >= min_agree
         and r.pumps_b >= min_pumps and r.dir_a >= min_dir and r.dir_b >= min_dir and r.z_b >= z_min),
        key=lambda r: -min(r.lift_a, r.lift_b),
    )


# ---- synthetic market with a planted pre-pump signature ----------------------------------------
def synthetic_coins(
    n_coins: int = 16, n: int = 24 * 200, signature: bool = True, seed: int = 1
) -> dict[str, list[Bar]]:
    """Every 1-2 weeks a coin makes a big move: a +30% pump or a -25% dump at random. With `signature`, the 24h
    before a PUMP show volatility compression, rising open interest and negative funding (crowded shorts);
    dumps, and pumps without `signature`, come out of nowhere."""
    rng = random.Random(seed)
    btc_path, btc = [], 30_000.0
    for _ in range(n):
        btc *= 1 + rng.gauss(0, 0.004)
        btc_path.append(btc)
    out: dict[str, list[Bar]] = {}
    for c in range(n_coins):
        price, oi, bars = 1.0, 1e6, []
        next_pump = rng.randint(24 * 35, 24 * 45)
        up = rng.random() < 0.5
        for i in range(n):
            vol, oi_d, fund, drift = 0.012, rng.gauss(0, 0.004), 0.0001, 0.0
            phase = i - next_pump
            if -24 <= phase < 0 and signature and up:
                vol, oi_d, fund = 0.004, 0.006, -0.0004
            elif 0 <= phase < 12:
                drift, oi_d = (0.024 if up else -0.024), -0.01
            elif phase == 12:
                next_pump = i + rng.randint(24 * 7, 24 * 14)
                up = rng.random() < 0.5
            o = price
            price *= 1 + drift + 0.8 * (btc_path[i] / btc_path[i - 1] - 1 if i else 0.0) + rng.gauss(0, vol)
            oi *= 1 + oi_d
            wick = abs(rng.gauss(0, vol / 2))
            bars.append(Bar(i * 3_600_000, o, max(o, price) * (1 + wick), min(o, price) * (1 - wick), price,
                            1000 * (1 + abs(rng.gauss(0, 0.3))), oi, fund, btc_path[i]))
        out[f"SYN{c}USDT"] = bars
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="What do altcoins have in common before a big pump?")
    ap.add_argument("--synthetic", choices=("signature", "nosignature"))
    ap.add_argument("--top", type=int, default=40, help="top-N alts by turnover (Bybit)")
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--cache", help="JSON cache of downloaded 1h bars")
    ap.add_argument("--threshold", type=float, default=0.20, help="pump size, e.g. 0.20 = +20%%")
    ap.add_argument("--horizon", type=int, default=24, help="pump window in hours")
    args = ap.parse_args()

    if args.synthetic:
        data = synthetic_coins(signature=args.synthetic == "signature")
    else:
        import os
        import time

        from .bybit_client import BybitClient
        from .config import Config
        from .data import btc_close_map, fetch_bars, load_bars, save_bars, select_universe

        if args.cache and os.path.exists(args.cache):
            data = load_bars(args.cache)
        else:
            cfg = Config()
            cfg.universe.max_symbols = args.top
            client = BybitClient()
            end = int(time.time() * 1000)
            start = end - args.days * 86_400_000
            btc = btc_close_map(client, 60, start, end)
            data = {}
            for s in select_universe(client.tickers(), cfg.universe):
                print(f"downloading {s} ...")
                data[s] = fetch_bars(client, s, 60, start, end, btc)
            if args.cache:
                save_bars(args.cache, data)

    results, meta = analyze(data, 1, args.horizon, args.threshold)
    print(f"{meta['coins']} coins, {meta['pumps']} pumps of >= +{args.threshold * 100:.0f}% and {meta['dumps']} "
          f"mirror dumps within {args.horizon}h")
    print(f"discovery coins   : {', '.join(meta['group_a'])}")
    print(f"confirmation coins: {', '.join(meta['group_b'])}\n")
    rep = repeating(results)
    if not rep:
        print("Nothing repeats: no pre-pump state favours UP moves consistently on coins the discovery never saw.")
        return
    print(f"{'feature':<22}{'decile':>7}{'range':>26}{'lift A':>8}{'lift B':>8}{'up/down B':>10}{'B coins':>9}"
          f"{'pumps B':>8}{'z B':>7}")
    for r in rep:
        rng_txt = f"{r.lo:>11.4g} .. {r.hi:<11.4g}"
        print(f"{r.feature:<22}{r.decile:>7}{rng_txt:>26}{r.lift_a:>8.2f}{r.lift_b:>8.2f}{r.dir_b:>10.2f}"
              f"{r.coins_b_agree * 100:>8.0f}%{r.pumps_b:>8}{r.z_b:>7.1f}")


if __name__ == "__main__":
    main()
