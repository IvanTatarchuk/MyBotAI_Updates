"""Impulse strategy: catch the start of a momentum burst.

Entry (long only by default) on a closed bar that is
    - an outsized move up: bar return >= z_min standard deviations of recent returns,
    - on heavy volume: volume >= volume_mult x its recent average,
    - a strong close: close in the top `close_pos` of the bar's range,
    - a breakout: close above the highest high of the previous `breakout` bars.
Stop just below the impulse bar's low (never tighter than min_stop_atr x ATR), take-profit at tp_r x risk,
time exit after max_hold_bars.
"""

from __future__ import annotations

import math

from .config import ImpulseConfig
from .strategy import Bar, Exits, Signal


class ImpulseDetector:
    name = "impulse"

    def __init__(self, cfg: ImpulseConfig):
        self.cfg = cfg
        self._key: tuple[int, int] | None = None
        self._rz: list[float] = []
        self._vr: list[float] = []
        self._hh: list[float] = []
        self._atr: list[float] = []

    @property
    def min_history(self) -> int:
        return max(self.cfg.window, self.cfg.breakout) + 2

    def _prepare(self, bars: list[Bar]) -> None:
        key = (id(bars), len(bars))
        if key == self._key:
            return
        w, n = self.cfg.window, len(bars)
        rz, vr, hh, atr_v = [0.0] * n, [0.0] * n, [math.inf] * n, [0.0] * n
        s1 = s2 = vs = ts = 0.0
        rets = [0.0] * n
        trs = [0.0] * n
        from collections import deque

        dq: deque[int] = deque()
        for i, b in enumerate(bars):
            if i:
                p = bars[i - 1].close
                rets[i] = b.close / p - 1
                trs[i] = max(b.high - b.low, abs(b.high - p), abs(b.low - p))
            # previous-`breakout` highest high, excluding bar i
            while dq and dq[0] < i - self.cfg.breakout:
                dq.popleft()
            if dq:
                hh[i] = bars[dq[0]].high
            while dq and bars[dq[-1]].high <= b.high:
                dq.pop()
            dq.append(i)
            # stats of the PREVIOUS window (the impulse bar itself must not dilute its own z-score)
            if i > w:
                m = s1 / w
                sd = math.sqrt(max(s2 / w - m * m, 1e-18))
                rz[i] = (rets[i] - m) / sd
                vr[i] = b.volume / (vs / w) if vs > 0 else 0.0
                atr_v[i] = ts / w
            s1 += rets[i]
            s2 += rets[i] ** 2
            vs += b.volume
            ts += trs[i]
            if i >= w:
                s1 -= rets[i - w]
                s2 -= rets[i - w] ** 2
                vs -= bars[i - w].volume
                ts -= trs[i - w]
        self._key, self._rz, self._vr, self._hh, self._atr = key, rz, vr, hh, atr_v

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        cfg = self.cfg
        if i < self.min_history:
            return None
        self._prepare(bars)
        b = bars[i]
        rng = b.high - b.low
        if rng <= 0 or self._atr[i] <= 0:
            return None
        if not (self._rz[i] >= cfg.z_min and self._vr[i] >= cfg.volume_mult and b.close > self._hh[i]
                and (b.close - b.low) / rng >= 1 - cfg.close_pos):
            return None
        stop = min(b.low, b.close - cfg.min_stop_atr * self._atr[i])
        return Signal("Buy", b.close, stop, self._atr[i], self._rz[i], b.ts, self.name)


def impulse_exits(cfg: ImpulseConfig) -> Exits:
    return Exits(tp1_r=cfg.tp_r, tp1_fraction=1.0, trail_atr=0.0, max_hold_bars=cfg.max_hold_bars,
                 atr_period=cfg.window)
