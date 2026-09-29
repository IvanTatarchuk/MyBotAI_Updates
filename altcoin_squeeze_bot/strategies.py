"""Registry of directional strategies that share the account's position slots."""

from __future__ import annotations

from .config import Config
from .strategy import Bar, Exits, Features, Signal, SqueezeDetector, min_history, replay, squeeze_exits
from .trend import TrendDetector

NAMES = ("squeeze", "trend", "autopilot")


def _autopilot_rule(cfg: Config):
    import os

    from .autopilot import Rule

    if cfg.autopilot_rule is not None:
        return cfg.autopilot_rule
    path = os.environ.get("AUTOPILOT_RULE", "autopilot_rule.json")
    if not os.path.exists(path):
        raise ValueError(f"autopilot needs a learned rule: run `autopilot learn` (expected {path})")
    with open(path) as fh:
        return Rule.from_json(fh.read())


def make_detectors(cfg: Config, features: list[Features | None] | None = None, symbol: str = "",
                   lookup: dict | None = None) -> list:
    dets: list = []
    for name in cfg.enabled:
        if name == "squeeze":
            dets.append(SqueezeDetector(cfg.strategy, features))
        elif name == "trend":
            dets.append(TrendDetector(cfg.trend))
        elif name == "autopilot":
            from .autopilot import RuleDetector

            dets.append(RuleDetector(_autopilot_rule(cfg), max(1, 60 // cfg.strategy.interval_min), lookup))
        else:
            raise ValueError(f"unknown strategy {name!r}; choose from {NAMES}")
    return dets


def exits_for(name: str, cfg: Config) -> Exits:
    if name == "autopilot":
        from .autopilot import rule_exits

        return rule_exits(_autopilot_rule(cfg), max(1, 60 // cfg.strategy.interval_min))
    if name == "trend":
        t = cfg.trend
        return Exits(tp1_r=0.0, tp1_fraction=0.0, trail_atr=t.trail_atr, max_hold_bars=t.max_hold_bars,
                     atr_period=t.atr_period)
    return squeeze_exits(cfg.strategy)


def required_history(cfg: Config) -> int:
    need = [min_history(cfg.strategy)] if "squeeze" in cfg.enabled else []
    if "trend" in cfg.enabled:
        need.append(TrendDetector(cfg.trend).min_history)
    if "autopilot" in cfg.enabled:
        need.append(31 * 24 * max(1, 60 // cfg.strategy.interval_min))
    return max(need)


def step_all(dets: list, bars: list[Bar], i: int) -> Signal | None:
    """Every detector must see every bar (they carry state); return the strongest signal."""
    sigs = [s for d in dets if (s := d.step(bars, i))]
    return max(sigs, key=lambda s: s.score) if sigs else None


def scan_all(bars: list[Bar], cfg: Config, symbol: str = "") -> Signal | None:
    sigs = [s for d in make_detectors(cfg, symbol=symbol) if (s := replay(d, bars))]
    return max(sigs, key=lambda s: s.score) if sigs else None
