"""Pattern miner: which chart "moments" really keep repeating?

Every pattern is a condition evaluated on a closed bar using only past data. For each pattern and
horizon we measure the forward return after it, relative to the market's normal drift over the same
period (BTC rose ~10x in the data, so "price went up afterwards" alone proves nothing).

Two stages, so that mining hundreds of patterns cannot fool us:
1. discovery   (first part of history): keep patterns whose excess return is significant after a
                multiple-testing correction (Bonferroni over all pattern x horizon pairs)
2. confirmation (later, unseen part): the pattern must repeat with the same sign, be significant on its
                own and be larger than round-trip trading costs

Overlapping forward windows are removed (after an event, the next event is only counted once the
horizon has passed), otherwise t-stats would be inflated.

    python -m altcoin_squeeze_bot.patterns --csv BTCUSDT-1h.csv --interval 60
"""

from __future__ import annotations

import argparse
import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from statistics import NormalDist

from .strategy import Bar


@dataclass
class Ctx:
    """Precomputed, strictly backward-looking series."""

    bars: list[Bar]
    ret: list[float]
    rz: list[float]  # bar return / rolling std
    hour: list[int]
    wday: list[int]
    mday: list[int]
    mdays: list[int]  # days in that month
    up_streak: list[int]
    dn_streak: list[int]
    z_sma_short: list[float]  # (close - SMA) / (std * sqrt(window))
    z_sma_long: list[float]
    ret_day_z: list[float]
    vol_ratio: list[float]  # short ATR / long ATR
    vz: list[float]  # volume / average volume
    lower_wick: list[float]
    upper_wick: list[float]
    new_high: list[bool]
    new_low: list[bool]
    bars_per_day: int


def build_ctx(bars: list[Bar], interval_min: int) -> Ctx:
    n = len(bars)
    bpd = max(1, 1440 // interval_min)
    w_s, w_l = bpd, bpd * 7
    ret = [0.0] + [bars[i].close / bars[i - 1].close - 1 for i in range(1, n)]
    rz, zs, zl, rdz, vr, vz = ([0.0] * n for _ in range(6))
    lw, uw = [0.0] * n, [0.0] * n
    nh, nl = [False] * n, [False] * n
    up, dn = [0] * n, [0] * n
    hour, wday, mday, mdays = [0] * n, [0] * n, [0] * n, [0] * n
    s1 = s2 = 0.0
    csum_s = csum_l = vsum = tr_s = tr_l = 0.0
    trs = [0.0] * n
    for i, b in enumerate(bars):
        t = time.gmtime(b.ts / 1000)
        hour[i], wday[i], mday[i] = t.tm_hour, t.tm_wday, t.tm_mday
        nxt = time.gmtime((b.ts + 86_400_000) / 1000)
        mdays[i] = t.tm_mday if nxt.tm_mon != t.tm_mon else 99  # 99 = not the last day of the month
        r = ret[i]
        up[i] = up[i - 1] + 1 if i and r > 0 else 0
        dn[i] = dn[i - 1] + 1 if i and r < 0 else 0
        s1 += r
        s2 += r * r
        csum_s += b.close
        csum_l += b.close
        vsum += b.volume
        if i:
            p = bars[i - 1].close
            trs[i] = max(b.high - b.low, abs(b.high - p), abs(b.low - p))
        tr_s += trs[i]
        tr_l += trs[i]
        if i >= w_l:
            o = ret[i - w_l]
            s1 -= o
            s2 -= o * o
            csum_l -= bars[i - w_l].close
            vsum -= bars[i - w_l].volume
            tr_l -= trs[i - w_l]
        if i >= w_s:
            csum_s -= bars[i - w_s].close
            tr_s -= trs[i - w_s]
        rng = b.high - b.low
        if rng > 0:
            lw[i] = (min(b.open, b.close) - b.low) / rng
            uw[i] = (b.high - max(b.open, b.close)) / rng
        if i < w_l:
            continue
        m = s1 / w_l
        sd = math.sqrt(max(s2 / w_l - m * m, 1e-18))
        rz[i] = r / sd
        zs[i] = (b.close / (csum_s / w_s) - 1) / (sd * math.sqrt(w_s))
        zl[i] = (b.close / (csum_l / w_l) - 1) / (sd * math.sqrt(w_l))
        rdz[i] = (b.close / bars[i - w_s].close - 1) / (sd * math.sqrt(w_s))
        vr[i] = (tr_s / w_s) / (tr_l / w_l) if tr_l > 0 else 1.0
        vz[i] = b.volume / (vsum / w_l) if vsum > 0 else 1.0
        prev = bars[i - w_l : i]
        nh[i] = b.close > max(x.high for x in prev)
        nl[i] = b.close < min(x.low for x in prev)
    return Ctx(bars, ret, rz, hour, wday, mday, mdays, up, dn, zs, zl, rdz, vr, vz, lw, uw, nh, nl, bpd)


def _round_level(price: float) -> bool:
    step = 10 ** max(0, int(math.log10(price)) - 1) * 5  # e.g. 5000 for 40k, 500 for 4k
    return abs(price - round(price / step) * step) / price < 0.003


def library(c: Ctx) -> dict[str, Callable[[int], bool]]:
    lib: dict[str, Callable[[int], bool]] = {}
    for h in range(24):
        lib[f"hour {h:02d} UTC"] = lambda i, h=h: c.hour[i] == h
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d in range(7):
        lib[f"day {names[d]}"] = lambda i, d=d: c.wday[i] == d and c.hour[i] == 23  # close of that day
    lib["weekend (Sat/Sun)"] = lambda i: c.wday[i] >= 5 and c.hour[i] == 0
    lib["month turn (last day)"] = lambda i: c.mdays[i] != 99 and c.hour[i] == 0
    for k in (3, 4, 5, 6):
        lib[f"{k} green bars in a row"] = lambda i, k=k: c.up_streak[i] == k
        lib[f"{k} red bars in a row"] = lambda i, k=k: c.dn_streak[i] == k
    for z in (2.0, 3.0):
        lib[f"far above 1-day mean (z>{z:g})"] = lambda i, z=z: c.z_sma_short[i] > z
        lib[f"far below 1-day mean (z<-{z:g})"] = lambda i, z=z: c.z_sma_short[i] < -z
    lib["far above 7-day mean (z>1.5)"] = lambda i: c.z_sma_long[i] > 1.5
    lib["far below 7-day mean (z<-1.5)"] = lambda i: c.z_sma_long[i] < -1.5
    for z in (3.0, 4.0):
        lib[f"huge green bar (>{z:g} sigma)"] = lambda i, z=z: c.rz[i] > z
        lib[f"huge red bar (<-{z:g} sigma)"] = lambda i, z=z: c.rz[i] < -z
    lib["strong day up (z>2)"] = lambda i: c.ret_day_z[i] > 2
    lib["strong day down (z<-2)"] = lambda i: c.ret_day_z[i] < -2
    lib["volatility squeeze (ATR ratio<0.5)"] = lambda i: c.vol_ratio[i] < 0.5
    lib["volatility explosion (ATR ratio>2)"] = lambda i: c.vol_ratio[i] > 2
    lib["volume spike x3 on green bar"] = lambda i: c.vz[i] > 3 and c.ret[i] > 0
    lib["volume spike x3 on red bar"] = lambda i: c.vz[i] > 3 and c.ret[i] < 0
    lib["hammer (lower wick > 60%)"] = lambda i: c.lower_wick[i] > 0.6 and c.vz[i] > 1.5
    lib["shooting star (upper wick > 60%)"] = lambda i: c.upper_wick[i] > 0.6 and c.vz[i] > 1.5
    lib["new 7-day high"] = lambda i: c.new_high[i]
    lib["new 7-day low"] = lambda i: c.new_low[i]
    lib["at a round price level"] = lambda i: _round_level(c.bars[i].close)
    return lib


@dataclass
class Result:
    name: str
    horizon: int
    n: int
    excess: float  # mean forward return minus unconditional mean, same period
    t: float


def measure(c: Ctx, cond: Callable[[int], bool], horizon: int, lo: int, hi: int, base: float) -> Result:
    """Non-overlapping events in [lo, hi); excess forward return vs base drift."""
    xs: list[float] = []
    next_free = lo
    step_ms = c.bars[1].ts - c.bars[0].ts if len(c.bars) > 1 else 0
    for i in range(max(lo, c.bars_per_day * 7), min(hi, len(c.bars) - horizon)):
        if i < next_free or not cond(i):
            continue
        if c.bars[i + horizon].ts - c.bars[i].ts != horizon * step_ms:
            continue  # data gap inside the window
        xs.append(c.bars[i + horizon].close / c.bars[i].close - 1 - base * horizon)
        next_free = i + horizon
    n = len(xs)
    if n < 2:
        return Result("", horizon, n, 0.0, 0.0)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return Result("", horizon, n, m, m / (sd / math.sqrt(n)) if sd > 0 else 0.0)


def mean_bar_return(c: Ctx, lo: int, hi: int) -> float:
    rs = c.ret[lo + 1 : hi]
    return sum(rs) / len(rs) if rs else 0.0


def mine(bars: list[Bar], interval_min: int, split: float = 0.65, horizons=(1, 4, 12, 24),
         cost: float = 0.0013, alpha: float = 0.05, min_events: int = 40):
    c = build_ctx(bars, interval_min)
    lib = library(c)
    cut = int(len(bars) * split)
    base_d, base_c = mean_bar_return(c, 0, cut), mean_bar_return(c, cut, len(bars))
    tests = len(lib) * len(horizons)
    t_disc = NormalDist().inv_cdf(1 - alpha / 2 / tests)  # Bonferroni
    rows = []
    for name, cond in lib.items():
        for h in horizons:
            d = measure(c, cond, h, 0, cut, base_d)
            d.name = name
            conf = measure(c, cond, h, cut, len(bars), base_c) if abs(d.t) >= t_disc and d.n >= min_events else None
            rows.append((d, conf))
    return c, cut, tests, t_disc, rows, cost


def verdict(d: Result, conf: Result | None, t_disc: float, cost: float, min_events: int) -> str:
    if d.n < min_events:
        return "too rare"
    if abs(d.t) < t_disc:
        return "chance"
    if conf is None or conf.n < 20:
        return "not enough confirmation data"
    if (conf.excess > 0) != (d.excess > 0):
        return "REVERSED later -> fake"
    if abs(conf.t) < 2:
        return "faded later -> fake"
    if abs(conf.excess) < cost:
        return "real, but smaller than costs"
    return "CONFIRMED & tradable"


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine repeating chart moments with honest out-of-sample confirmation")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--split", type=float, default=0.65)
    ap.add_argument("--all", action="store_true", help="also list patterns that failed discovery")
    args = ap.parse_args()

    from .data import load_binance_csv

    (sym, bars), = load_binance_csv(args.csv).items()
    c, cut, tests, t_disc, rows, cost = mine(bars, args.interval, args.split)
    day = lambda i: time.strftime("%Y-%m-%d", time.gmtime(bars[i].ts / 1000))  # noqa: E731
    print(f"{sym}: {len(bars)} bars | discovery {day(0)} .. {day(cut - 1)} | confirmation {day(cut)} .. {day(-1)}")
    print(f"{len(rows)} tests ({tests} pattern x horizon) -> discovery needs |t| >= {t_disc:.2f} (Bonferroni)")
    print(f"round-trip cost assumed {cost * 100:.2f}%\n")
    print(f"{'pattern':<36}{'h':>4}{'n':>6}{'disc. excess':>13}{'t':>7}{'n':>6}{'conf. excess':>13}{'t':>7}  verdict")
    shown = 0
    for d, conf in sorted(rows, key=lambda r: -abs(r[0].t)):
        v = verdict(d, conf, t_disc, cost, 40)
        if not args.all and v in ("chance", "too rare"):
            continue
        shown += 1
        cf = f"{conf.n:>6}{conf.excess * 100:>12.3f}%{conf.t:>7.2f}" if conf else f"{'':>6}{'':>13}{'':>7}"
        print(f"{d.name:<36}{d.horizon:>4}{d.n:>6}{d.excess * 100:>12.3f}%{d.t:>7.2f}{cf}  {v}")
    if not shown:
        print("No pattern survived discovery.")
    survivors = [d for d, conf in rows if verdict(d, conf, t_disc, cost, 40) == "CONFIRMED & tradable"]
    print(f"\nCONFIRMED & tradable: {len(survivors)}")


if __name__ == "__main__":
    main()
