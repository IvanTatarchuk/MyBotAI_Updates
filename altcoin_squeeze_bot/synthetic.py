"""Synthetic market with injected crowd-and-squeeze episodes.

Used for tests and for a dry run of the backtester without network access. Results on this data
say nothing about real profitability; they only prove the pipeline works end to end.
"""

from __future__ import annotations

import math
import random

from .strategy import Bar

STEP_MS = 15 * 60_000


def generate(
    seed: int = 1, n: int = 3000, start_price: float = 1.0, squeeze_every: int = 400, edge: bool = True
) -> list[Bar]:
    """edge=False keeps the crowd build-up and the trigger bar but removes any follow-through (pure noise).

    Note: a random-direction follow-through is NOT a fair null: stops + trailing exits profit from any big
    move, so that would still be a (volatility) edge. The honest null is "nothing happens after the trigger".
    """
    rng = random.Random(seed)
    btc, price, oi = 60_000.0, start_price, 1_000_000.0
    bars: list[Bar] = []
    episode_start = rng.randint(150, squeeze_every)
    direction, follow = 1, 1
    for i in range(n):
        btc_ret = rng.gauss(0, 0.002)
        btc *= 1 + btc_ret
        drift, oi_drift, funding = 0.0, rng.gauss(0, 0.002), 0.0001

        phase = i - episode_start
        if 0 <= phase < 16:  # crowd piles in: price runs, OI balloons, funding gets expensive
            drift, oi_drift, funding = 0.006 * direction, 0.008, 0.0006 * direction
        elif 16 <= phase < 20:  # stall at the top
            drift, oi_drift, funding = 0.0, 0.001, 0.0006 * direction
        elif phase == 20:  # trigger bar: breaks structure while OI flushes out
            drift, oi_drift, funding = -0.02 * direction, -0.012, 0.0002 * direction
            follow = 1 if edge else 0
        elif 20 < phase < 32:  # squeeze continues (edge) or nothing happens (no edge)
            drift, oi_drift, funding = -0.007 * direction * follow, -0.012, 0.0002 * direction
        elif phase == 32:
            episode_start = i + rng.randint(squeeze_every // 2, squeeze_every)
            direction = rng.choice((1, -1))

        o = price
        price *= 1 + 1.2 * btc_ret + drift + rng.gauss(0, 0.003)
        oi *= 1 + oi_drift
        wick = abs(rng.gauss(0, 0.002))
        high = max(o, price) * (1 + wick)
        low = min(o, price) * (1 - wick)
        bars.append(Bar(i * STEP_MS, o, high, low, price, 1000.0, oi, funding, btc))
    return bars


def universe(n_symbols: int = 5, n: int = 3000, edge: bool = True) -> dict[str, list[Bar]]:
    return {
        f"SYN{k}USDT": generate(seed=k + 1, n=n, start_price=math.pow(10, k % 3 - 1), edge=edge)
        for k in range(n_symbols)
    }
