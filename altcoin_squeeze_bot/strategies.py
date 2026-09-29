"""Registry of directional strategies that share the account's position slots."""

from __future__ import annotations

from dataclasses import replace

from .config import Config
from .destiny import Destiny
from .strategy import Bar, Exits, Features, Signal, SqueezeDetector, min_history, replay, squeeze_exits
from .tarot import TarotDetector
from .trend import TrendDetector

NAMES = ("squeeze", "trend", "tarot", "hanged", "destiny")


def make_detectors(cfg: Config, features: list[Features | None] | None = None, symbol: str = "") -> list:
    dets: list = []
    for name in cfg.enabled:
        if name == "squeeze":
            dets.append(SqueezeDetector(cfg.strategy, features))
        elif name == "trend":
            dets.append(TrendDetector(cfg.trend))
        elif name == "tarot":
            dets.append(TarotDetector(cfg.tarot, symbol))
        elif name == "hanged":  # Chart Tarot reversed by The Hanged Man
            dets.append(TarotDetector(replace(cfg.tarot, invert=True), symbol))
        elif name == "destiny":  # Chart Tarot filtered by the owner's numerology
            owner = cfg.tarot.owner or Destiny.from_env()
            if owner is None:
                raise ValueError("destiny needs the owner's birth date: --birth DD.MM.YYYY or BOT_OWNER_BIRTH")
            dets.append(TarotDetector(replace(cfg.tarot, owner=owner), symbol))
        else:
            raise ValueError(f"unknown strategy {name!r}; choose from {NAMES}")
    return dets


def exits_for(name: str, cfg: Config) -> Exits:
    if name == "trend":
        t = cfg.trend
        return Exits(tp1_r=0.0, tp1_fraction=0.0, trail_atr=t.trail_atr, max_hold_bars=t.max_hold_bars,
                     atr_period=t.atr_period)
    if name in ("tarot", "hanged", "destiny"):
        t = cfg.tarot
        return Exits(t.tp1_r, t.tp1_fraction, t.trail_atr, t.horizon, t.atr_period)  # exit when the "future" is due
    return squeeze_exits(cfg.strategy)


def required_history(cfg: Config) -> int:
    need = [min_history(cfg.strategy)] if "squeeze" in cfg.enabled else []
    if "trend" in cfg.enabled:
        need.append(TrendDetector(cfg.trend).min_history)
    if {"tarot", "hanged", "destiny"} & set(cfg.enabled):
        need.append(TarotDetector(cfg.tarot, "").min_history)
    return max(need)


def step_all(dets: list, bars: list[Bar], i: int) -> Signal | None:
    """Every detector must see every bar (they carry state); return the strongest signal."""
    sigs = [s for d in dets if (s := d.step(bars, i))]
    return max(sigs, key=lambda s: s.score) if sigs else None


def scan_all(bars: list[Bar], cfg: Config, symbol: str = "") -> Signal | None:
    sigs = [s for d in make_detectors(cfg, symbol=symbol) if (s := replay(d, bars))]
    return max(sigs, key=lambda s: s.score) if sigs else None
