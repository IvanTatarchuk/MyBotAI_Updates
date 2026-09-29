"""All tunable parameters in one place. Defaults are sized for a $100 account."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StrategyConfig:
    interval_min: int = 15  # candle size in minutes
    beta_window: int = 96  # bars used to estimate the alt's beta to BTC (96 x 15m = 24h)
    crowd_window: int = 16  # bars over which crowding is measured (16 x 15m = 4h)
    atr_period: int = 14

    # "Crowded" conditions (all must hold to arm a setup)
    z_arm: float = 2.0  # |BTC-neutral residual move| in standard deviations
    oi_rise_min: float = 0.06  # open interest grew >= 6% over crowd_window
    funding_long_min: float = 0.0002  # funding >= 0.02% -> longs are paying (crowded long)
    funding_short_max: float = -0.0001  # funding <= -0.01% -> shorts are paying (crowded short)
    arm_ttl_bars: int = 12  # how long an armed setup waits for the trigger

    # Trigger: the crowd starts getting liquidated
    breakout_lookback: int = 3  # close breaks the 3-bar low (for a short) / high (for a long)
    oi_drop_trigger: float = 0.004  # open interest drops >= 0.4% on the trigger bar

    # Exits
    stop_atr_min: float = 1.0
    stop_atr_max: float = 3.0
    tp1_r: float = 1.5  # take half at 1.5R, move stop to breakeven
    tp1_fraction: float = 0.5
    trail_atr: float = 2.0  # chandelier trail on the runner after TP1
    max_hold_bars: int = 48  # time stop (12h on 15m)

    # BTC regime filter: skip entries while BTC itself is moving violently
    btc_max_abs_move: float = 0.03


@dataclass
class TrendConfig:
    """Time-series momentum / Donchian breakout: the approach with the strongest net-of-cost evidence in crypto."""

    donchian: int = 192  # breakout of the previous 2-day high/low (15m bars)
    mom_long: int = 672  # 7-day return must agree with the breakout
    mom_short: int = 96  # 1-day return must agree too
    atr_period: int = 96
    stop_atr: float = 5.0
    trail_atr: float = 6.0  # no partial TP: trends pay through the few big winners
    max_hold_bars: int = 672 * 2
    max_abs_funding: float = 0.0005  # skip entries where our side already pays > 0.05% per 8h


@dataclass
class CarryConfig:
    """Delta-neutral funding carry: long spot + short perp, collects funding while funding is positive."""

    lookback_periods: int = 9  # trailing funding average over 9 x 8h = 3 days
    enter_rate: float = 0.0002  # enter when the trailing average >= 0.02% per 8h (~22% APR)
    exit_rate: float = 0.00005  # leave when it decays below 0.005% per 8h
    max_holdings: int = 3
    capital_usage: float = 0.9  # fraction of the sleeve deployed (rest is margin buffer)
    spot_fee: float = 0.001
    perp_fee: float = 0.00055


@dataclass
class RiskConfig:
    risk_per_trade: float = 0.015  # 1.5% of equity lost if the stop is hit
    max_leverage: float = 5.0  # hard cap on notional / equity per position
    max_positions: int = 2
    daily_loss_limit: float = 0.05  # stop opening trades for the UTC day after -5%
    max_drawdown: float = 0.30  # kill switch: stop the bot after -30% from peak
    min_notional: float = 5.0  # Bybit minimum order value in USDT


@dataclass
class UniverseConfig:
    min_turnover_24h: float = 5_000_000.0  # skip illiquid coins (slippage kills small accounts too)
    max_symbols: int = 40
    exclude: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "USDCUSDT", "USDEUSDT", "FDUSDUSDT")


@dataclass
class CostConfig:
    taker_fee: float = 0.00055
    slippage: float = 0.0005  # per side, conservative for alts


@dataclass
class Config:
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    universe: UniverseConfig = field(default_factory=UniverseConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    trend: TrendConfig = field(default_factory=TrendConfig)
    carry: CarryConfig = field(default_factory=CarryConfig)
    autopilot_rule: object | None = None  # autopilot.Rule learned from all coins (see autopilot.py)
    enabled: tuple[str, ...] = ("squeeze", "trend")  # directional strategies sharing the position slots
