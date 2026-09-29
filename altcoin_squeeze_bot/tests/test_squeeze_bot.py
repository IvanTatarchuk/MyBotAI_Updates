import hashlib
import hmac

from altcoin_squeeze_bot.backtest import run
from altcoin_squeeze_bot.bot import PaperBroker, fmt, fmt_price
from altcoin_squeeze_bot.bybit_client import sign
from altcoin_squeeze_bot.config import Config, RiskConfig, StrategyConfig
from altcoin_squeeze_bot.data import align, select_universe
from altcoin_squeeze_bot.risk import RiskGuard, position_size, round_step
from altcoin_squeeze_bot.strategy import (
    Bar,
    SqueezeDetector,
    compute_features,
    new_plan,
    scan,
    squeeze_exits,
    update_trail,
)
from altcoin_squeeze_bot.synthetic import generate, universe


def _flat(n: int, price: float = 1.0) -> list[Bar]:
    return [Bar(i * 900_000, price, price * 1.001, price * 0.999, price, 1, 1e6, 0.0001, 60_000.0) for i in range(n)]


def test_features_need_history():
    cfg = StrategyConfig()
    bars = generate(n=200)
    assert compute_features(bars, 50, cfg) is None
    assert compute_features(bars, 150, cfg) is not None


def test_beta_recovers_btc_exposure():
    cfg = StrategyConfig()
    bars = generate(seed=7, n=400, squeeze_every=10_000)  # no episodes in range
    f = compute_features(bars, 300, cfg)
    assert 0.6 < f.beta < 1.8  # generator uses beta 1.2 plus idiosyncratic noise


def test_detector_shorts_a_crowded_long_that_breaks():
    cfg = StrategyConfig()
    bars = _flat(200)
    price, oi = 1.0, 1e6
    # crowd piles in for 16 bars: price +0.8%/bar, OI +1%/bar, expensive funding
    for i in range(150, 166):
        o = price
        price *= 1.008
        oi *= 1.01
        bars[i] = Bar(bars[i].ts, o, price * 1.001, o * 0.999, price, 1, oi, 0.0008, 60_000.0)
    # breakdown bar with OI flushing out
    o = price
    price *= 0.97
    bars[166] = Bar(bars[166].ts, o, o * 1.001, price * 0.999, price, 1, oi * 0.98, 0.0008, 60_000.0)

    det = SqueezeDetector(cfg)
    signals = [s for i in range(167) if (s := det.step(bars, i))]
    assert len(signals) == 1
    sig = signals[0]
    assert sig.side == "Sell" and sig.stop > sig.entry and sig.ts == bars[166].ts
    assert scan(bars[:167], cfg) is not None  # replay reproduces the same live signal


def test_no_signal_on_quiet_market():
    cfg = StrategyConfig()
    assert scan(generate(seed=3, n=600, squeeze_every=100_000), cfg) is None


def test_position_size_risk_and_leverage_caps():
    rc = RiskConfig()
    qty = position_size(100, 1.0, 0.95, rc)  # risk 1.5 USDT over 0.05 -> 30 units, 30 USDT notional
    assert abs(qty - 30) < 1e-9
    capped = position_size(100, 1.0, 0.999, rc)  # tight stop would need 1500 units -> leverage cap 500
    assert abs(capped - 500) < 1e-9
    assert position_size(100, 1.0, 0.5, rc) == 0.0  # 3 USDT notional < 5 USDT minimum
    assert round_step(12.3456, 0.01) == 12.34


def test_risk_guard_daily_limit_and_kill_switch():
    g = RiskGuard(RiskConfig())
    g.update(100, 0)
    assert g.can_open(96)
    assert not g.can_open(94.9)
    g.update(100, 86_400_000)  # new day resets the daily limit
    assert g.can_open(99)
    g.update(69, 86_400_000 + 1)
    assert g.killed and not g.can_open(1000)


def test_trail_only_after_tp1_and_never_loosens():
    cfg = StrategyConfig()
    plan = new_plan("Buy", 100.0, 95.0, squeeze_exits(cfg))
    assert plan.tp1_price == 107.5
    bar = Bar(0, 100, 110, 99, 109, 1, 1, 0, 1)
    update_trail(plan, bar, 1.0)
    assert plan.stop == 95.0  # no trailing before TP1
    plan.tp1_done = True
    update_trail(plan, bar, 1.0)
    assert plan.stop == 108.0  # 110 - 2 * ATR
    update_trail(plan, Bar(0, 109, 109, 100, 101, 1, 1, 0, 1), 5.0)
    assert plan.stop == 108.0


def test_backtest_pipeline_runs_and_accounts_consistently():
    res = run(universe(n_symbols=3, n=1500), Config(), 100.0)
    assert res.trades
    realized = sum(t.pnl for t in res.trades)
    # with everything closed, equity = start + realized (open positions add unrealized on top)
    assert abs(res.equity - 100.0 - realized) < 50  # sanity bound; open positions allowed at the end
    assert 0 <= res.max_drawdown < 1


def test_backtest_trades_nothing_without_crowds():
    data = {"QUIETUSDT": generate(seed=5, n=1500, squeeze_every=100_000)}
    res = run(data, Config(enabled=("squeeze",)), 100.0)
    assert res.trades == []


def test_align_uses_as_of_values():
    kl = [[0, "1", "1", "1", "1", "5", "5"], [900_000, "1", "1", "1", "2", "5", "5"]]
    bars = align(kl, {0: 60_000.0, 900_000: 61_000.0}, [(900_000, 10.0), (1_800_000, 12.0)], [(0, 0.0003)], 15)
    assert [b.oi for b in bars] == [10.0, 12.0]
    assert bars[1].funding == 0.0003 and bars[1].btc_close == 61_000.0


def test_universe_filters_majors_and_illiquid():
    tickers = [
        {"symbol": "BTCUSDT", "turnover24h": "9e9"},
        {"symbol": "WIFUSDT", "turnover24h": "8e7"},
        {"symbol": "TINYUSDT", "turnover24h": "1000"},
        {"symbol": "SOLUSDT", "turnover24h": "9e8"},
        {"symbol": "ETHPERP", "turnover24h": "9e9"},
    ]
    assert select_universe(tickers, Config().universe) == ["SOLUSDT", "WIFUSDT"]


def test_signature_matches_bybit_v5_scheme():
    expected = hmac.new(b"sec", b"1700000000000key5000a=1", hashlib.sha256).hexdigest()
    assert sign("sec", "1700000000000", "key", "5000", "a=1") == expected


def test_number_formatting_for_orders():
    assert fmt(12.3456, 0.01) == "12.34"
    assert fmt(1234.9, 10) == "1230"
    assert fmt_price(0.123456, 0.0001) == "0.1235"


def test_paper_broker_stop_and_tp():
    b = PaperBroker(100.0, fee=0.0, slippage=0.0)
    b.open("XUSDT", "Sell", 10, stop=1.1, _lev=5, px=1.0)
    b.place_tp("XUSDT", "Buy", 5, 0.9)
    b.on_closed_bar("XUSDT", Bar(0, 1.0, 1.01, 0.89, 0.95, 1, 1, 0, 1))
    assert b.sizes() == {"XUSDT": 5}
    assert abs(b.cash - 100.5) < 1e-9
    b.on_closed_bar("XUSDT", Bar(0, 0.95, 1.2, 0.95, 1.15, 1, 1, 0, 1))
    assert b.sizes() == {}
    assert abs(b.cash - (100.5 - 0.5)) < 1e-9


def test_trigger_ignores_too_short_history_with_precomputed_features():
    from altcoin_squeeze_bot.strategy import precompute_features

    cfg = StrategyConfig()
    bars = generate(n=300)
    feats = precompute_features(bars, cfg)
    det = SqueezeDetector(cfg, feats[150:])
    det.armed, det.armed_until = "short_crowded", 100
    sliced = bars[150:]
    for i in range(3):
        assert det.step(sliced, i) is None  # would slice bars[-3:0] without the guard


def test_features_cache_gives_identical_backtest():
    from altcoin_squeeze_bot.strategy import precompute_features

    data = universe(n_symbols=2, n=1200)
    cfg = Config()
    feats = {s: precompute_features(b, cfg.strategy) for s, b in data.items()}
    a, b = run(data, cfg), run(data, cfg, features=feats)
    assert [t.pnl for t in a.trades] == [t.pnl for t in b.trades]


def test_validation_rejects_a_market_without_edge():
    from altcoin_squeeze_bot.strategy import precompute_features
    from altcoin_squeeze_bot.validate import DEFAULT_GRID, monte_carlo, plateau, stats, verdict, walk_forward

    cfg = Config(enabled=("squeeze",))
    data = universe(n_symbols=4, n=4000, edge=False)
    feats = {s: precompute_features(b, cfg.strategy) for s, b in data.items()}
    grid = {"strategy.z_arm": [1.5, 2.5], "strategy.tp1_r": DEFAULT_GRID["strategy.tp1_r"][:2]}
    wf = walk_forward(data, feats, cfg, grid, n_folds=3, min_trades=5)
    pl = plateau(data, feats, cfg, grid)
    share = sum(1 for _, s in pl if s.n > 0 and s.expectancy > 0) / len(pl)
    checks = verdict(stats(wf.oos), share, monte_carlo(wf.oos, 0.015, 0.30, sims=500))
    assert not all(ok for ok, _ in checks)


def test_monte_carlo_and_stats_basics():
    from altcoin_squeeze_bot.validate import monte_carlo, stats

    s = stats([1.0, -1.0, 2.0, -1.0])
    assert s.n == 4 and abs(s.expectancy - 0.25) < 1e-12 and abs(s.profit_factor - 1.5) < 1e-12
    mc = monte_carlo([-1.0] * 40, risk=0.015, kill_dd=0.30, sims=50)
    assert mc.p_kill == 1.0 and mc.median_return < 0


def _trend_bars(n: int = 900, drift: float = 0.0015) -> list[Bar]:
    bars, price = [], 1.0
    for i in range(n):
        o = price
        price *= 1 + (drift if i > 700 else 0.0) + (0.001 if i % 2 else -0.001)
        bars.append(Bar(i * 900_000, o, max(o, price) * 1.001, min(o, price) * 0.999, price, 1, 1e6, 0.0001, 6e4))
    return bars


def test_trend_detector_breakout_long_and_funding_filter():
    from altcoin_squeeze_bot.config import TrendConfig
    from altcoin_squeeze_bot.trend import TrendDetector

    bars = _trend_bars()
    det = TrendDetector(TrendConfig())
    sigs = [s for i in range(len(bars)) if (s := det.step(bars, i))]
    assert sigs and all(s.side == "Buy" and s.strategy == "trend" and s.stop < s.entry for s in sigs)
    assert sigs[0].ts > bars[700].ts  # nothing before the trend starts

    for b in bars:
        b.funding = 0.001  # longs already pay 0.1% per 8h -> too crowded to join
    det = TrendDetector(TrendConfig())
    assert not [s for i in range(len(bars)) if det.step(bars, i)]


def test_trend_rolling_channel_matches_naive():
    from altcoin_squeeze_bot.config import TrendConfig
    from altcoin_squeeze_bot.trend import TrendDetector

    bars = generate(seed=11, n=800)
    det = TrendDetector(TrendConfig(donchian=50))
    det._prepare(bars)
    for i in (50, 123, 799):
        assert det._hh[i] == max(b.high for b in bars[i - 50 : i])
        assert det._ll[i] == min(b.low for b in bars[i - 50 : i])


def test_trend_plan_trails_from_entry_without_tp1():
    from altcoin_squeeze_bot.strategies import exits_for

    plan = new_plan("Sell", 100.0, 110.0, exits_for("trend", Config()), "trend")
    assert plan.trailing and plan.tp1_fraction == 0
    update_trail(plan, Bar(0, 100, 101, 80, 81, 1, 1, 0, 1), 1.0)
    assert plan.stop == 86.0  # 80 + 6 ATR, tightened immediately


def test_scan_all_prefers_strongest_signal():
    from altcoin_squeeze_bot.strategies import scan_all

    bars = _trend_bars()
    sig = scan_all(bars, Config(enabled=("trend",)))
    assert sig is None or sig.strategy == "trend"
    assert scan_all(bars, Config(enabled=("squeeze",))) is None


def _funding_bars(rates_per_8h: list[float]) -> list[Bar]:
    """15m bars where each 8h block (32 bars) carries the given funding rate."""
    bars = []
    for k, rate in enumerate(rates_per_8h):
        for j in range(32):
            i = k * 32 + j
            bars.append(Bar(i * 900_000, 1, 1, 1, 1, 1, 1e6, rate, 6e4))
    return bars


def test_carry_collects_funding_net_of_fees():
    from altcoin_squeeze_bot.carry import PERP_MARGIN, backtest_carry

    cfg = Config()
    cc = cfg.carry
    res = backtest_carry({"AUSDT": _funding_bars([0.0005] * 90)}, cfg, 100.0)  # 30 days at 0.05% / 8h
    size = 100 * cc.capital_usage / (cc.max_holdings * (1 + PERP_MARGIN))
    entry_fee = size * (cc.spot_fee + cc.perp_fee)
    held_periods = 90 - cc.lookback_periods  # funding collected from the period after entry
    expected = 100 - entry_fee + size * 0.0005 * held_periods
    assert res.switches == 1
    assert abs(res.equity - expected) < 1e-6


def test_carry_exits_when_funding_flips():
    from altcoin_squeeze_bot.carry import backtest_carry

    cfg = Config()
    rates = [0.0005] * 30 + [-0.0003] * 30
    res = backtest_carry({"AUSDT": _funding_bars(rates)}, cfg, 100.0)
    last_curve = [e for _, e in res.curve[-10:]]
    assert len(set(round(e, 9) for e in last_curve)) == 1  # flat: out of the position, no more payments
    assert res.equity > 100  # the good weeks paid more than the flip cost


def test_carry_ignores_low_funding():
    from altcoin_squeeze_bot.carry import backtest_carry

    res = backtest_carry({"AUSDT": _funding_bars([0.0001] * 60)}, Config(), 100.0)
    assert res.switches == 0 and res.equity == 100.0


def test_grid_configs_sets_nested_fields_with_types():
    from altcoin_squeeze_bot.validate import grid_configs

    combos = grid_configs(Config(), {"trend.donchian": [96.0], "strategy.z_arm": [2.5]})
    (_, cfg), = combos
    assert cfg.trend.donchian == 96 and isinstance(cfg.trend.donchian, int)
    assert cfg.strategy.z_arm == 2.5


def test_rhythm_finds_hidden_pattern_but_not_random_walk():
    from altcoin_squeeze_bot.rhythm import evaluate, synthetic

    rand, _, _ = evaluate(synthetic("random", n=8000))
    patt, _, _ = evaluate(synthetic("pattern", n=8000))
    assert abs(rand.z_score) < 3
    assert patt.z_score > 5 and patt.hit_rate > 0.58
    assert patt.net_bp < patt.gross_bp  # costs are always charged


def test_rhythm_scale_is_fit_on_training_only():
    from altcoin_squeeze_bot.rhythm import Scale, synthetic

    c = synthetic("random", n=2000)
    s = Scale.fit(c[:1000])
    notes = s.notes(c)
    assert len(notes) == len(c) - 1
    assert all(0 <= p < 5 and 0 <= v < 3 for p, v in notes)
    assert len(s.ret_edges) == 4 and s.ret_edges == sorted(s.ret_edges)


def test_rhythm_markov_backoff_and_midi(tmp_path):
    from altcoin_squeeze_bot.rhythm import RhythmModel, to_midi

    notes = [(0, 1), (4, 1)] * 50
    rets = [-0.001, 0.001] * 50
    m = RhythmModel(max_order=2, min_count=5).fit(notes, rets)
    probs, order = m.distribution([(4, 1), (0, 1)])
    assert order == 2 and probs[4] == 1.0  # after a drop always comes a rally
    assert m.expected_return([(0, 1)]) > 0
    probs, order = m.distribution([(2, 2)])  # unseen phrase -> falls back to unconditional counts
    assert order == 0
    assert m.continue_melody([(0, 1)], 4) == [4, 0, 4, 0]

    path = tmp_path / "x.mid"
    to_midi(notes[:10], str(path), predicted=[4, 0])
    data = path.read_bytes()
    assert data[:4] == b"MThd" and data[14:18] == b"MTrk" and data.endswith(b"\xff\x2f\x00")


def test_slice_period_keeps_symbols_with_unbounded_warmup():
    from altcoin_squeeze_bot.validate import slice_period

    bars = generate(n=500)
    feats = {"A": [None] * 500}
    t0, t1 = bars[300].ts, bars[400].ts
    d, _ = slice_period({"A": bars}, feats, t0, t1, 10**9)
    assert len(d["A"]) == 400 and d["A"][0].ts == bars[0].ts
    d, _ = slice_period({"A": bars}, feats, t0, t1, 16)
    assert len(d["A"]) == 116
    d, _ = slice_period({"A": bars}, feats, bars[-1].ts + 1, bars[-1].ts + 10, 16)
    assert d == {}


def test_validation_is_not_blocked_by_kill_switch_in_warmup():
    from altcoin_squeeze_bot.validate import r_multiples

    # a crash early on trips the live kill switch, but later out-of-sample trades must still be measured
    data = universe(n_symbols=3, n=4000)
    cfg = Config(enabled=("squeeze",))
    cfg.risk.max_drawdown = 0.0001  # would stop a real account after the first loss
    t0 = data["SYN0USDT"][2500].ts
    t1 = data["SYN0USDT"][-1].ts + 1
    from altcoin_squeeze_bot.strategy import precompute_features

    feats = {s: precompute_features(b, cfg.strategy) for s, b in data.items()}
    assert r_multiples(data, feats, cfg, t0, t1)
    assert run(data, cfg).killed


def _hourly(n: int, seed: int, hidden_hour: int | None) -> list[Bar]:
    import random

    rng = random.Random(seed)
    bars, price = [], 100.0
    for i in range(n):
        ts = i * 3_600_000
        drift = 0.004 if hidden_hour is not None and (i - 1) % 24 == hidden_hour else 0.0  # bar after that hour
        o = price
        price *= 1 + drift + rng.gauss(0, 0.004)
        bars.append(Bar(ts, o, max(o, price) * 1.001, min(o, price) * 0.999, price, 100 + rng.random(), 1, 0, price))
    return bars


def test_pattern_miner_confirms_a_real_repeating_moment_and_nothing_in_noise():
    from altcoin_squeeze_bot.patterns import mine, verdict

    def confirmed(bars):
        _, _, _, t_disc, rows, cost = mine(bars, 60)
        return {(d.name, d.horizon) for d, conf in rows if verdict(d, conf, t_disc, cost, 40) == "CONFIRMED & tradable"}

    found = confirmed(_hourly(24 * 400, seed=1, hidden_hour=7))
    assert ("hour 07 UTC", 1) in found
    assert confirmed(_hourly(24 * 400, seed=2, hidden_hour=None)) == set()


def test_pattern_measure_skips_overlapping_windows():
    from altcoin_squeeze_bot.patterns import build_ctx, measure

    bars = _hourly(24 * 30, seed=3, hidden_hour=None)
    c = build_ctx(bars, 60)
    r = measure(c, lambda i: True, 24, 0, len(bars), 0.0)  # every bar qualifies
    assert r.n <= (len(bars) - 24 * 7) // 24 + 1  # but only one event per 24-bar window is counted


def test_prepump_finds_planted_signature_on_unseen_coins():
    from altcoin_squeeze_bot.prepump import analyze, repeating, synthetic_coins

    results, meta = analyze(synthetic_coins(n_coins=12, n=24 * 150, signature=True, seed=4))
    found = {r.feature for r in repeating(results)}
    assert {"funding", "oi_change_4h"} <= found
    assert meta["pumps"] > 0 and meta["dumps"] > 0


def test_prepump_finds_nothing_in_a_random_walk():
    import random

    from altcoin_squeeze_bot.prepump import analyze, repeating

    rng = random.Random(9)
    data = {}
    for c in range(10):
        price, bars = 1.0, []
        for i in range(24 * 120):
            o = price
            price *= 1 + rng.gauss(0, 0.02)  # volatile enough for many +/-20% moves, but no structure
            bars.append(Bar(i * 3_600_000, o, max(o, price), min(o, price), price, 1000 * (1 + rng.random()),
                            1e6 * (1 + rng.gauss(0, 0.01)), rng.gauss(0, 0.0002), 30_000.0))
        data[f"R{c}USDT"] = bars
    results, meta = analyze(data)
    assert meta["pumps"] > 50
    assert repeating(results) == []


def test_pump_starts_counts_each_move_once_and_mirrors_dumps():
    from altcoin_squeeze_bot.prepump import pump_starts

    closes = [1.0] * 30 + [1.0 + 0.05 * k for k in range(1, 11)] + [1.5] * 30  # +50% over 10 bars
    bars = [Bar(i, c, c, c, c, 1, 1, 0, 1) for i, c in enumerate(closes)]
    ups = pump_starts(bars, 24, 0.20)
    assert len(ups) == 1 and min(ups) < 34
    assert pump_starts(bars, 24, 0.20, down=True) == set()
