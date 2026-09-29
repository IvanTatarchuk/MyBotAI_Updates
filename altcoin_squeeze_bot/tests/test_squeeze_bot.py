import hashlib
import hmac

from altcoin_squeeze_bot.backtest import run
from altcoin_squeeze_bot.bot import PaperBroker, fmt, fmt_price
from altcoin_squeeze_bot.bybit_client import sign
from altcoin_squeeze_bot.config import Config, RiskConfig, StrategyConfig
from altcoin_squeeze_bot.data import align, select_universe
from altcoin_squeeze_bot.risk import RiskGuard, position_size, round_step
from altcoin_squeeze_bot.strategy import Bar, SqueezeDetector, compute_features, new_plan, scan, update_trail
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
    plan = new_plan("Buy", 100.0, 95.0, cfg)
    assert plan.tp1_price == 107.5
    bar = Bar(0, 100, 110, 99, 109, 1, 1, 0, 1)
    update_trail(plan, bar, 1.0, cfg)
    assert plan.stop == 95.0  # no trailing before TP1
    plan.tp1_done = True
    update_trail(plan, bar, 1.0, cfg)
    assert plan.stop == 108.0  # 110 - 2 * ATR
    update_trail(plan, Bar(0, 109, 109, 100, 101, 1, 1, 0, 1), 5.0, cfg)
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
    res = run(data, Config(), 100.0)
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

    cfg = Config()
    data = universe(n_symbols=4, n=4000, edge=False)
    feats = {s: precompute_features(b, cfg.strategy) for s, b in data.items()}
    grid = {"z_arm": [1.5, 2.5], "tp1_r": DEFAULT_GRID["tp1_r"][:2]}
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
