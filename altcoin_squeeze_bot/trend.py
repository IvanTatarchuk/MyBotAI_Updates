"""Trend sleeve: time-series momentum confirmed by a Donchian breakout.

Academic work on crypto finds time-series momentum robust after costs while cross-sectional momentum
is not, so only the former is used. The idea (not code) follows the classic Turtle breakout: enter
when price leaves its recent range in the direction of the multi-day trend, exit on a wide ATR trail.
"""

from __future__ import annotations

import math
from collections import deque

from .config import TrendConfig
from .strategy import Bar, Signal


class TrendDetector:
    name = "trend"

    def __init__(self, cfg: TrendConfig):
        self.cfg = cfg
        self._key: tuple[int, int] | None = None
        self._hh: list[float] = []
        self._ll: list[float] = []
        self._atr: list[float] = []

    @property
    def min_history(self) -> int:
        return max(self.cfg.donchian, self.cfg.mom_long, self.cfg.atr_period) + 1

    def _prepare(self, bars: list[Bar]) -> None:
        """Rolling previous-N high/low and ATR in O(n) (monotonic deques), cached per bars list."""
        key = (id(bars), len(bars))
        if key == self._key:
            return
        d, p = self.cfg.donchian, self.cfg.atr_period
        n = len(bars)
        hh, ll, atr_v = [math.nan] * n, [math.nan] * n, [0.0] * n
        dq_h: deque[int] = deque()
        dq_l: deque[int] = deque()
        tr_sum, trs = 0.0, [0.0] * n
        for i in range(n):
            # previous-N window excludes bar i
            while dq_h and dq_h[0] < i - d:
                dq_h.popleft()
            while dq_l and dq_l[0] < i - d:
                dq_l.popleft()
            if i >= d:
                hh[i], ll[i] = bars[dq_h[0]].high, bars[dq_l[0]].low
            while dq_h and bars[dq_h[-1]].high <= bars[i].high:
                dq_h.pop()
            dq_h.append(i)
            while dq_l and bars[dq_l[-1]].low >= bars[i].low:
                dq_l.pop()
            dq_l.append(i)

            if i > 0:
                prev = bars[i - 1].close
                trs[i] = max(bars[i].high - bars[i].low, abs(bars[i].high - prev), abs(bars[i].low - prev))
                tr_sum += trs[i]
                if i > p:
                    tr_sum -= trs[i - p]
                atr_v[i] = tr_sum / min(i, p)
        self._key, self._hh, self._ll, self._atr = key, hh, ll, atr_v

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        cfg = self.cfg
        if i < self.min_history - 1:
            return None
        self._prepare(bars)
        bar, a = bars[i], self._atr[i]
        if a <= 0:
            return None
        ret_long = bar.close / bars[i - cfg.mom_long].close - 1
        ret_short = bar.close / bars[i - cfg.mom_short].close - 1
        # trend strength in "ATR units per sqrt(bar)": comparable across coins with different volatility
        score = abs(ret_long) * bar.close / (a * math.sqrt(cfg.mom_long))

        if bar.close > self._hh[i] and ret_long > 0 and ret_short > 0 and bar.funding <= cfg.max_abs_funding:
            return Signal("Buy", bar.close, bar.close - cfg.stop_atr * a, a, score, bar.ts, self.name)
        if cfg.long_only:
            return None
        if bar.close < self._ll[i] and ret_long < 0 and ret_short < 0 and bar.funding >= -cfg.max_abs_funding:
            return Signal("Sell", bar.close, bar.close + cfg.stop_atr * a, a, score, bar.ts, self.name)
        return None
