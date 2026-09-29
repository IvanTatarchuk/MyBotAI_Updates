"""Download Bybit history and align klines, open interest, funding and BTC into Bar lists."""

from __future__ import annotations

import bisect
import json
import os
from collections.abc import Iterable

from .bybit_client import BybitClient
from .config import UniverseConfig
from .strategy import Bar


def _asof(series: list[tuple[int, float]], t: int, default: float = 0.0) -> float:
    """Latest value with timestamp <= t."""
    idx = bisect.bisect_right(series, (t, float("inf"))) - 1
    return series[idx][1] if idx >= 0 else default


def align(
    klines: list[list],
    btc_closes: dict[int, float],
    oi: list[tuple[int, float]],
    funding: list[tuple[int, float]],
    interval_min: int,
) -> list[Bar]:
    step = interval_min * 60_000
    bars = []
    for k in klines:
        ts = int(k[0])
        if ts not in btc_closes:
            continue
        close_t = ts + step
        oi_v = _asof(oi, close_t)
        if oi_v <= 0:
            continue
        bars.append(
            Bar(ts, float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5]), oi_v, _asof(funding, close_t),
                btc_closes[ts])
        )
    return bars


def fetch_klines(client: BybitClient, symbol: str, interval_min: int, start: int, end: int) -> list[list]:
    step = interval_min * 60_000
    out: list[list] = []
    cur = start
    while cur < end:
        batch = client.klines(symbol, interval_min, start=cur, end=min(end, cur + 999 * step), limit=1000)
        if not batch:
            cur += 1000 * step
            continue
        out += batch
        cur = int(batch[-1][0]) + step
    dedup = {int(k[0]): k for k in out}
    return [dedup[t] for t in sorted(dedup)]


def fetch_bars(client: BybitClient, symbol: str, interval_min: int, start: int, end: int,
               btc_closes: dict[int, float]) -> list[Bar]:
    kl = fetch_klines(client, symbol, interval_min, start, end)
    oi = client.open_interest(symbol, interval_min, start=start, end=end)
    fr = client.funding_history(symbol, start - 3 * 86_400_000, end)
    return align(kl, btc_closes, oi, fr, interval_min)


def btc_close_map(client: BybitClient, interval_min: int, start: int, end: int) -> dict[int, float]:
    return {int(k[0]): float(k[4]) for k in fetch_klines(client, "BTCUSDT", interval_min, start, end)}


def select_universe(tickers: Iterable[dict], cfg: UniverseConfig) -> list[str]:
    rows = [
        t for t in tickers
        if t["symbol"].endswith("USDT") and t["symbol"] not in cfg.exclude
        and float(t.get("turnover24h") or 0) >= cfg.min_turnover_24h
    ]
    rows.sort(key=lambda t: float(t["turnover24h"]), reverse=True)
    return [t["symbol"] for t in rows[: cfg.max_symbols]]


# ---- Binance public-data CSV (data.binance.vision or tools that mirror it) ----------------------
def _to_ms(value: str) -> int:
    value = value.strip()
    if value.isdigit():
        n = int(value)
        return n // 1000 if n > 10**14 else n  # microseconds (2025+ files) -> ms
    import datetime as dt

    return int(dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def load_binance_csv(path: str, symbol: str | None = None) -> dict[str, list[Bar]]:
    """Kline CSV: open_time, open, high, low, close, volume, ... Comment (#) and header lines are skipped.

    Spot files carry no open interest or funding: OI is set constant and funding to 0, so features that
    depend on them (crowding, funding filters) are simply inactive. The coin is its own
    BTC reference when no BTC series is supplied.
    """
    bars: list[Bar] = []
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            row = line.strip().split(",")
            try:
                ts = _to_ms(row[0])
                o, h, lo, c, v = (float(x) for x in row[1:6])
            except ValueError:
                continue  # header line
            bars.append(Bar(ts, o, h, lo, c, v, 1.0, 0.0, c))
    bars.sort(key=lambda b: b.ts)
    name = symbol or os.path.basename(path).split("-")[0].split("_")[-1] or "CSV"
    return {name: bars}


# ---- simple JSON cache so repeated backtests don't re-download --------------------------------
def save_bars(path: str, data: dict[str, list[Bar]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        json.dump({s: [list(vars(b).values()) for b in bars] for s, bars in data.items()}, fh)


def load_bars(path: str) -> dict[str, list[Bar]]:
    with open(path) as fh:
        raw = json.load(fh)
    return {s: [Bar(*row) for row in rows] for s, rows in raw.items()}
