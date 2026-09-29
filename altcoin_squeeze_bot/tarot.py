"""Chart Tarot: every bar of the chart is read as one of the 78 cards, computed from market data.

Major Arcana (22) = notable chart events, checked in priority order (e.g. The Tower = crash bar,
The Sun = euphoric rally on volume, Death = trend break, Wheel of Fortune = volatility explosion).
Minor Arcana (56) = the everyday state of the market:
    suit  = what dominates right now: Wands = price momentum, Cups = crowd mood (funding),
            Swords = volatility, Pentacles = money flow (volume / open interest)
    rank  = how strong it is (Ace .. King)
    reversed = the dominant force points down

Meaning of the cards is NOT assumed. The reader learns it online from history: for every card it
tracks the forward return that followed it, but only once that return is fully known (no lookahead).
A 3-card spread (past = card `horizon` bars ago, present = card now) uses the pair statistics when
there is enough history and falls back to the present card alone otherwise. A trade is taken only
when the card's past record is statistically strong (t-stat) and larger than trading costs.

    python -m altcoin_squeeze_bot.tarot SOLUSDT WIFUSDT          # today's spread from live data
    python -m altcoin_squeeze_bot.validate --strategies tarot --synthetic edge
"""

from __future__ import annotations

import math
from collections import deque

from .config import TarotConfig
from .strategy import Bar, Signal

MAJOR = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant",
    "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man",
    "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
]
SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Page", "Knight", "Queen", "King"]
DECK = MAJOR + [f"{r} of {s}" for s in SUITS for r in RANKS]
assert len(DECK) == 78
M = {name: i for i, name in enumerate(MAJOR)}

W_VOL = 96  # 1 day of 15m bars: volatility / volume / trend baseline
W_RANGE = 192  # 2-day range
W_FAST = 16  # 4 hours


def card_name(card: int, reversed_: bool) -> str:
    return DECK[card] + (" (reversed)" if reversed_ else "")


class ChartReader:
    """Computes the card of every bar in O(n) and caches it per bars list."""

    def __init__(self) -> None:
        self._key: tuple[int, int] | None = None
        self.cards: list[tuple[int, bool] | None] = []

    @staticmethod
    def min_history() -> int:
        return W_RANGE + W_FAST + 1

    def prepare(self, bars: list[Bar]) -> list[tuple[int, bool] | None]:
        key = (id(bars), len(bars))
        if key != self._key:
            self.cards = self._read_all(bars)
            self._key = key
        return self.cards

    def _read_all(self, bars: list[Bar]) -> list[tuple[int, bool] | None]:
        n = len(bars)
        out: list[tuple[int, bool] | None] = [None] * n
        rets = [0.0] + [bars[i].close / bars[i - 1].close - 1 for i in range(1, n)]
        s1 = s2 = vsum = csum = atr_f = atr_s = 0.0
        trs = [0.0] * n
        dq_h: deque[int] = deque()
        dq_l: deque[int] = deque()
        rz_hist: deque[float] = deque(maxlen=W_FAST)
        tz_hist: deque[float] = deque(maxlen=W_FAST + 1)
        for i in range(n):
            b = bars[i]
            r = rets[i]
            s1 += r
            s2 += r * r
            vsum += b.volume
            csum += b.close
            if i > 0:
                p = bars[i - 1].close
                trs[i] = max(b.high - b.low, abs(b.high - p), abs(b.low - p))
            atr_f += trs[i]
            atr_s += trs[i]
            if i >= W_VOL:
                old = rets[i - W_VOL]
                s1 -= old
                s2 -= old * old
                vsum -= bars[i - W_VOL].volume
                csum -= bars[i - W_VOL].close
                atr_s -= trs[i - W_VOL]
            if i >= 14:
                atr_f -= trs[i - 14]
            # previous-W_RANGE high/low (excluding bar i)
            while dq_h and dq_h[0] < i - W_RANGE:
                dq_h.popleft()
            while dq_l and dq_l[0] < i - W_RANGE:
                dq_l.popleft()
            hh = bars[dq_h[0]].high if dq_h else b.high
            ll = bars[dq_l[0]].low if dq_l else b.low
            while dq_h and bars[dq_h[-1]].high <= b.high:
                dq_h.pop()
            dq_h.append(i)
            while dq_l and bars[dq_l[-1]].low >= b.low:
                dq_l.pop()
            dq_l.append(i)

            if i < W_VOL:
                continue
            mean = s1 / W_VOL
            sd = math.sqrt(max(s2 / W_VOL - mean * mean, 1e-18))
            rz = r / sd
            tz = (b.close / bars[i - W_VOL].close - 1) / (sd * math.sqrt(W_VOL))
            prev_rz_min = min(rz_hist) if rz_hist else 0.0
            prev_tz = tz_hist[0] if len(tz_hist) == tz_hist.maxlen else tz
            rz_hist.append(rz)
            tz_hist.append(tz)
            if i < self.min_history() - 1:
                continue

            vz = b.volume / (vsum / W_VOL) if vsum > 0 else 1.0
            vol_ratio = (atr_f / 14) / (atr_s / W_VOL) if atr_s > 0 else 1.0
            sma = csum / W_VOL
            dz = (b.close / sma - 1) / (sd * math.sqrt(W_FAST))
            rng = hh - ll
            pos = (b.close - ll) / rng if rng > 0 else 0.5
            prev = bars[i - W_FAST]
            oi16 = b.oi / prev.oi - 1 if prev.oi else 0.0
            f16 = b.close / prev.close - 1
            btc16 = b.btc_close / prev.btc_close - 1 if prev.btc_close else 0.0
            body = abs(b.close - b.open)
            wick = (b.high - b.low - body) / (b.high - b.low) if b.high > b.low else 0.0

            out[i] = card_of(
                rz=rz, tz=tz, prev_tz=prev_tz, prev_rz_min=prev_rz_min, vz=vz, vol_ratio=vol_ratio, dz=dz,
                pos=pos, oi16=oi16, f16=f16, btc16=btc16, sd=sd, wick=wick, up=b.close >= b.open,
                funding=b.funding, breakout_up=b.close > hh, breakout_dn=b.close < ll,
            )
        return out


def card_of(*, rz: float, tz: float, prev_tz: float, prev_rz_min: float, vz: float, vol_ratio: float,
            dz: float, pos: float, oi16: float, f16: float, btc16: float, sd: float, wick: float, up: bool,
            funding: float, breakout_up: bool, breakout_dn: bool) -> tuple[int, bool]:
    """Map one bar's chart state to (card index, reversed)."""
    big16 = sd * math.sqrt(W_FAST)
    # ---- Major Arcana: notable events, most dramatic first ------------------------------------------
    if rz <= -4:
        return M["The Tower"], False
    if rz >= 4 and vz >= 2:
        return M["The Sun"], False
    if prev_rz_min <= -4 and rz >= 1:
        return M["The Star"], False
    if wick >= 0.8 and vz >= 2:
        return M["The Moon"], not up
    if abs(funding) >= 0.0005 and oi16 >= 0.05:
        return M["The Devil"], funding < 0
    if (prev_tz >= 1.5 and tz < 0) or (prev_tz <= -1.5 and tz > 0):
        return M["Death"], prev_tz < 0
    if vol_ratio >= 2.0:
        return M["Wheel of Fortune"], not up
    if (breakout_up or breakout_dn) and vol_ratio < 0.8:
        return M["The Fool"], breakout_dn
    if (breakout_up and tz >= 2) or (breakout_dn and tz <= -2):
        return M["The World"], breakout_dn
    if abs(tz) >= 2.5:
        return M["The Chariot"], tz < 0
    if vz >= 3 and abs(rz) < 0.5:
        return M["The Magician"], not up
    if abs(tz) >= 1.5 and oi16 <= -0.03:
        return M["The High Priestess"], tz < 0
    if abs(f16) >= big16 and abs(btc16) >= 0.01 and (f16 > 0) == (btc16 > 0):
        return M["The Lovers"], f16 < 0
    if abs(tz) >= 1.5 and vol_ratio < 0.7:
        return M["The Hanged Man"], tz < 0
    if abs(tz) >= 1.5 and vol_ratio < 1.2:
        return M["The Emperor"], tz < 0
    if (tz >= 1 and rz <= -1) or (tz <= -1 and rz >= 1):
        return M["Strength"], tz < 0
    if (pos <= 0.05 and rz > 0.5) or (pos >= 0.95 and rz < -0.5):
        return M["The Hierophant"], pos >= 0.95
    if 0.5 <= abs(tz) < 1.5 and vol_ratio < 1.0:
        return M["The Empress"], tz < 0
    if vz >= 2 and 0.45 <= pos <= 0.55:
        return M["Judgement"], not up
    if vol_ratio <= 0.5:
        return M["The Hermit"], not up
    if abs(dz) < 0.1 and abs(tz) < 0.3:
        return M["Justice"], not up
    if abs(tz) < 0.5 and 0.8 <= vol_ratio <= 1.2:
        return M["Temperance"], dz > 0
    # ---- Minor Arcana: dominant force picks the suit, its strength picks the rank -------------------
    forces = [
        tz,  # Wands: momentum
        funding / 0.0001,  # Cups: crowd mood
        math.log(max(vol_ratio, 1e-9)) * 3,  # Swords: volatility
        (vz - 1) + oi16 * 20,  # Pentacles: money flow
    ]
    suit = max(range(4), key=lambda k: abs(forces[k]))
    rank = min(13, int(abs(forces[suit]) * 3))
    return 22 + suit * 14 + rank, forces[suit] < 0


class CardStats:
    """Online mean / variance of forward returns per key (Welford)."""

    def __init__(self) -> None:
        self.n: dict = {}
        self.mean: dict = {}
        self.m2: dict = {}

    def add(self, key, x: float) -> None:
        n = self.n.get(key, 0) + 1
        mean = self.mean.get(key, 0.0)
        d = x - mean
        mean += d / n
        self.n[key], self.mean[key] = n, mean
        self.m2[key] = self.m2.get(key, 0.0) + d * (x - mean)

    def get(self, key) -> tuple[int, float, float]:
        """(count, mean, t-stat)."""
        n = self.n.get(key, 0)
        if n < 2:
            return n, self.mean.get(key, 0.0), 0.0
        sd = math.sqrt(self.m2[key] / (n - 1))
        return n, self.mean[key], self.mean[key] / (sd / math.sqrt(n)) if sd > 0 else 0.0


class TarotDetector:
    """Reads the spread on every bar; trades when the cards' learned meaning is strong and beats costs."""

    def __init__(self, cfg: TarotConfig, symbol: str = ""):
        self.cfg, self.symbol = cfg, symbol
        self.name = "hanged" if cfg.invert else ("destiny" if cfg.owner else "tarot")
        self.reader = ChartReader()
        self.stats = CardStats()
        self._learned_upto = -1  # last bar index whose forward return has been recorded

    @property
    def min_history(self) -> int:
        return ChartReader.min_history() + self.cfg.horizon

    def _keys(self, cards, i: int) -> tuple[tuple, tuple] | None:
        present = cards[i]
        if present is None:
            return None
        past = cards[i - self.cfg.horizon] if i >= self.cfg.horizon else None
        return ("spread", past, present), ("card", present)

    def _learn(self, bars: list[Bar], cards, i: int) -> None:
        """Record forward returns that are fully known at bar i (entries up to i - horizon)."""
        h = self.cfg.horizon
        for j in range(self._learned_upto + 1, i - h + 1):
            keys = self._keys(cards, j)
            if keys is None:
                continue
            fwd = bars[j + h].close / bars[j].close - 1
            for k in keys:
                self.stats.add(k, fwd)
        self._learned_upto = max(self._learned_upto, i - h)

    def meaning(self, cards, i: int) -> tuple[int, float, float, str]:
        """(count, mean forward return, t-stat, which key was used) for the spread ending at i."""
        keys = self._keys(cards, i)
        if keys is None:
            return 0, 0.0, 0.0, "-"
        spread, single = keys
        n, mean, t = self.stats.get(spread)
        if n >= self.cfg.min_count:
            return n, mean, t, "spread"
        n, mean, t = self.stats.get(single)
        return n, mean, t, "card"

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        cards = self.reader.prepare(bars)
        self._learn(bars, cards, i)
        if i < self.min_history:
            return None
        cfg = self.cfg
        n, mean, t, _ = self.meaning(cards, i)
        if n < cfg.min_count or abs(t) < cfg.t_min or abs(mean) < cfg.min_edge:
            return None
        owner = cfg.owner
        if owner is not None:  # destiny mode: owner's resonant personal days, or the birth card on the chart
            present = cards[i]
            birth_card_now = present is not None and present[0] == owner.birth_card
            if not (birth_card_now or owner.is_resonant_day(bars[i].ts)):
                return None
        a = self._atr(bars, i)
        if a <= 0:
            return None
        d = 1 if mean > 0 else -1
        if cfg.invert:  # The Hanged Man: the same reading, acted on upside down
            d = -d
        bar = bars[i]
        return Signal("Buy" if d > 0 else "Sell", bar.close, bar.close - d * cfg.stop_atr * a, a, abs(t), bar.ts,
                      self.name)

    def _atr(self, bars: list[Bar], i: int) -> float:
        p = self.cfg.atr_period
        trs = [max(bars[k].high - bars[k].low, abs(bars[k].high - bars[k - 1].close),
                   abs(bars[k].low - bars[k - 1].close)) for k in range(i - p + 1, i + 1)]
        return sum(trs) / p


def main() -> None:
    import argparse
    import time

    from .bybit_client import BybitClient
    from .config import Config
    from .data import btc_close_map, fetch_bars

    ap = argparse.ArgumentParser(description="Chart Tarot reading from live Bybit data")
    ap.add_argument("symbols", nargs="*", default=["SOLUSDT", "DOGEUSDT", "WIFUSDT"])
    ap.add_argument("--days", type=int, default=60, help="history the reader learns card meanings from")
    args = ap.parse_args()
    cfg = Config()
    client = BybitClient()
    end = int(time.time() * 1000)
    start = end - args.days * 86_400_000
    btc = btc_close_map(client, cfg.strategy.interval_min, start, end)
    for sym in args.symbols:
        bars = fetch_bars(client, sym, cfg.strategy.interval_min, start, end, btc)
        det = TarotDetector(cfg.tarot, sym)
        sig = None
        for i in range(len(bars)):
            sig = det.step(bars, i)
        cards = det.reader.cards
        i = len(bars) - 1
        past, now = cards[i - cfg.tarot.horizon], cards[i]
        n, mean, t, used = det.meaning(cards, i)
        print(f"\n{sym}")
        print(f"  past   : {card_name(*past) if past else '-'}")
        print(f"  present: {card_name(*now) if now else '-'}")
        print(f"  future : after this {used} the price moved {mean * 100:+.2f}% on average over "
              f"{cfg.tarot.horizon} bars ({n} times, t={t:+.2f})")
        print(f"  -> {sig.side + ' signal' if sig else 'no trade (the cards are not convincing enough)'}")


if __name__ == "__main__":
    main()
