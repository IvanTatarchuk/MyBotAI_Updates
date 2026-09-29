"""Position sizing and account-level circuit breakers."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import RiskConfig

DAY_MS = 86_400_000


def round_step(value: float, step: float) -> float:
    """Round down to the exchange quantity step (never round a position up)."""
    if step <= 0:
        return value
    return math.floor(value / step + 1e-9) * step


def position_size(
    equity: float,
    entry: float,
    stop: float,
    cfg: RiskConfig,
    qty_step: float = 0.0,
    min_qty: float = 0.0,
) -> float:
    """Quantity that loses `risk_per_trade` of equity at the stop, capped by max leverage.

    Returns 0 when the trade is too small to place (below min qty / min notional).
    """
    dist = abs(entry - stop)
    if equity <= 0 or entry <= 0 or dist <= 0:
        return 0.0
    if cfg.fixed_leverage > 0:
        qty = equity * cfg.fixed_leverage / entry  # whole account at a fixed leverage
    else:
        qty = equity * cfg.risk_per_trade / dist
        qty = min(qty, equity * cfg.max_leverage / entry)
    qty = round_step(qty, qty_step)
    if qty <= 0 or qty < min_qty or qty * entry < cfg.min_notional:
        return 0.0
    return qty


@dataclass
class RiskGuard:
    """Blocks new entries after a bad day, and stops the bot entirely after a deep drawdown."""

    cfg: RiskConfig
    peak_equity: float = 0.0
    day: int = -1
    day_start_equity: float = 0.0
    killed: bool = False

    def update(self, equity: float, ts_ms: int) -> None:
        day = ts_ms // DAY_MS
        if day != self.day:
            self.day, self.day_start_equity = day, equity
        self.peak_equity = max(self.peak_equity, equity)
        if self.peak_equity > 0 and equity <= self.peak_equity * (1 - self.cfg.max_drawdown):
            self.killed = True

    def can_open(self, equity: float) -> bool:
        if self.killed:
            return False
        return equity > self.day_start_equity * (1 - self.cfg.daily_loss_limit)

    def to_dict(self) -> dict:
        return {
            "peak_equity": self.peak_equity,
            "day": self.day,
            "day_start_equity": self.day_start_equity,
            "killed": self.killed,
        }

    @classmethod
    def from_dict(cls, cfg: RiskConfig, d: dict) -> RiskGuard:
        return cls(
            cfg, d.get("peak_equity", 0.0), d.get("day", -1), d.get("day_start_equity", 0.0), d.get("killed", False)
        )
