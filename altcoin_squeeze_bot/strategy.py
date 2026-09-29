"""Crowd Squeeze strategy.

Idea: on altcoin perps, the crowd piles into one side (open interest balloons, funding gets
expensive, price runs far ahead of what BTC explains). That crowd is fuel. We do not fight the
move while it runs; we wait until the crowd starts being forced out (price breaks structure while
open interest drops = liquidations / stop-outs) and ride the cascade in the opposite direction.

- Crowded long  -> wait for breakdown with falling OI -> SHORT (long squeeze)
- Crowded short -> wait for breakout with falling OI  -> LONG  (short squeeze)

Everything here is pure (no I/O) so the backtester and live bot share exactly the same logic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import StrategyConfig


@dataclass
class Bar:
    ts: int  # candle open time, ms
    open: float
    high: float
    low: float
    close: float
    volume: float
    oi: float  # open interest at candle close
    funding: float  # latest known funding rate at this bar
    btc_close: float


@dataclass
class Features:
    beta: float
    z: float  # z-score of the BTC-neutral cumulative return over crowd_window
    oi_change: float  # OI growth over crowd_window
    oi_bar_change: float  # OI change on the current bar
    atr: float
    btc_move: float  # BTC return over crowd_window


@dataclass
class Signal:
    side: str  # "Buy" or "Sell"
    entry: float  # reference price (close of the trigger bar)
    stop: float
    atr: float
    score: float  # strategy-specific strength, used to rank simultaneous signals
    ts: int
    strategy: str = "squeeze"


def _ret(a: float, b: float) -> float:
    return a / b - 1.0 if b else 0.0


def atr(bars: list[Bar], i: int, period: int) -> float:
    """Simple average true range ending at bar i (inclusive)."""
    start = max(1, i - period + 1)
    trs = []
    for k in range(start, i + 1):
        prev = bars[k - 1].close
        trs.append(max(bars[k].high - bars[k].low, abs(bars[k].high - prev), abs(bars[k].low - prev)))
    return sum(trs) / len(trs) if trs else 0.0


def min_history(cfg: StrategyConfig) -> int:
    return cfg.beta_window + cfg.crowd_window + 1


def compute_features(bars: list[Bar], i: int, cfg: StrategyConfig) -> Features | None:
    if i < min_history(cfg) - 1:
        return None
    w, r = cfg.beta_window, cfg.crowd_window
    ra = [_ret(bars[k].close, bars[k - 1].close) for k in range(i - w + 1, i + 1)]
    rb = [_ret(bars[k].btc_close, bars[k - 1].btc_close) for k in range(i - w + 1, i + 1)]
    mb = sum(rb) / w
    ma = sum(ra) / w
    var_b = sum((x - mb) ** 2 for x in rb) / w
    cov = sum((ra[k] - ma) * (rb[k] - mb) for k in range(w)) / w
    beta = cov / var_b if var_b > 0 else 0.0

    resid = [ra[k] - beta * rb[k] for k in range(w)]
    mr = sum(resid) / w
    sd = math.sqrt(sum((x - mr) ** 2 for x in resid) / w)
    cum = sum(resid[-r:])
    z = cum / (sd * math.sqrt(r)) if sd > 0 else 0.0

    return Features(
        beta=beta,
        z=z,
        oi_change=_ret(bars[i].oi, bars[i - r].oi),
        oi_bar_change=_ret(bars[i].oi, bars[i - 1].oi),
        atr=atr(bars, i, cfg.atr_period),
        btc_move=_ret(bars[i].btc_close, bars[i - r].btc_close),
    )


def precompute_features(bars: list[Bar], cfg: StrategyConfig) -> list[Features | None]:
    """Features depend only on window lengths, not on thresholds, so parameter sweeps can reuse them."""
    return [compute_features(bars, i, cfg) for i in range(len(bars))]


class SqueezeDetector:
    """Per-symbol state machine: idle -> armed (crowd detected) -> signal (crowd breaking)."""

    name = "squeeze"

    def __init__(self, cfg: StrategyConfig, features: list[Features | None] | None = None):
        self.cfg = cfg
        self.features = features  # optional precomputed features (see precompute_features)
        self.armed: str | None = None  # "long_crowded" | "short_crowded"
        self.armed_until = -1
        self.armed_score = 0.0

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        cfg = self.cfg
        f = self.features[i] if self.features is not None else compute_features(bars, i, cfg)
        if f is None or f.atr <= 0:
            return None

        if self.armed and i > self.armed_until:
            self.armed = None

        signal = None
        if self.armed:
            signal = self._trigger(bars, i, f)
            if signal:
                self.armed = None
                return signal

        # (Re-)arm. A fresh, stronger crowd reading refreshes the timer.
        bar = bars[i]
        if f.z >= cfg.z_arm and f.oi_change >= cfg.oi_rise_min and bar.funding >= cfg.funding_long_min:
            self.armed, self.armed_until, self.armed_score = "long_crowded", i + cfg.arm_ttl_bars, abs(f.z)
        elif f.z <= -cfg.z_arm and f.oi_change >= cfg.oi_rise_min and bar.funding <= cfg.funding_short_max:
            self.armed, self.armed_until, self.armed_score = "short_crowded", i + cfg.arm_ttl_bars, abs(f.z)
        return None

    def _trigger(self, bars: list[Bar], i: int, f: Features) -> Signal | None:
        cfg = self.cfg
        if abs(f.btc_move) > cfg.btc_max_abs_move:
            return None
        if f.oi_bar_change > -cfg.oi_drop_trigger:
            return None
        lb = cfg.breakout_lookback
        if i < lb:
            return None
        prev = bars[i - lb : i]
        bar = bars[i]
        if self.armed == "long_crowded" and bar.close < min(b.low for b in prev):
            swing = max(b.high for b in bars[i - lb : i + 1])
            dist = min(max(swing - bar.close, cfg.stop_atr_min * f.atr), cfg.stop_atr_max * f.atr)
            return Signal("Sell", bar.close, bar.close + dist, f.atr, self.armed_score, bar.ts)
        if self.armed == "short_crowded" and bar.close > max(b.high for b in prev):
            swing = min(b.low for b in bars[i - lb : i + 1])
            dist = min(max(bar.close - swing, cfg.stop_atr_min * f.atr), cfg.stop_atr_max * f.atr)
            return Signal("Buy", bar.close, bar.close - dist, f.atr, self.armed_score, bar.ts)
        return None


def replay(det, bars: list[Bar]) -> Signal | None:
    """Replay a detector over history and return a signal only if it fires on the last bar.

    Replaying makes the live bot stateless across restarts: detector state is rebuilt from data.
    """
    sig = None
    for i in range(len(bars)):
        sig = det.step(bars, i)
    return sig


def scan(bars: list[Bar], cfg: StrategyConfig) -> Signal | None:
    return replay(SqueezeDetector(cfg), bars)


@dataclass
class Exits:
    """Per-strategy exit rules."""

    tp1_r: float
    tp1_fraction: float  # 0 -> no partial take profit; the trail is active from the start
    trail_atr: float
    max_hold_bars: int
    atr_period: int


def squeeze_exits(cfg: StrategyConfig) -> Exits:
    return Exits(cfg.tp1_r, cfg.tp1_fraction, cfg.trail_atr, cfg.max_hold_bars, cfg.atr_period)


@dataclass
class TradePlan:
    """State + exit rules of an open position, shared by backtest and live bot."""

    side: str
    entry: float
    stop: float
    initial_risk: float  # |entry - initial stop| per unit
    tp1_r: float
    tp1_fraction: float
    trail_atr: float
    max_hold_bars: int
    atr_period: int
    strategy: str = "squeeze"
    tp1_done: bool = False
    best_price: float = 0.0  # most favourable extreme since entry, used by the trail
    bars_held: int = 0

    @property
    def direction(self) -> int:
        return 1 if self.side == "Buy" else -1

    @property
    def tp1_price(self) -> float:
        return self.entry + self.direction * self.initial_risk * self.tp1_r

    @property
    def trailing(self) -> bool:
        return self.tp1_done or self.tp1_fraction <= 0


def new_plan(side: str, entry: float, stop: float, exits: Exits, strategy: str = "squeeze") -> TradePlan:
    return TradePlan(
        side, entry, stop, abs(entry - stop), exits.tp1_r, exits.tp1_fraction, exits.trail_atr,
        exits.max_hold_bars, exits.atr_period, strategy, best_price=entry,
    )


def update_trail(plan: TradePlan, bar: Bar, atr_value: float) -> float:
    """Advance plan state with a closed bar and return the (possibly tightened) stop.

    After TP1 the stop is never worse than breakeven. Without TP1 (trend) the trail runs from entry.
    """
    plan.bars_held += 1
    if plan.direction == 1:
        plan.best_price = max(plan.best_price, bar.high)
        if plan.trailing:
            floor = plan.entry if plan.tp1_done else plan.stop
            plan.stop = max(plan.stop, floor, plan.best_price - plan.trail_atr * atr_value)
    else:
        plan.best_price = min(plan.best_price, bar.low)
        if plan.trailing:
            cap = plan.entry if plan.tp1_done else plan.stop
            plan.stop = min(plan.stop, cap, plan.best_price + plan.trail_atr * atr_value)
    return plan.stop
