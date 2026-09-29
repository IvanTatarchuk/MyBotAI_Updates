"""Tarot + numerology strategy, formalised so it can be tested like any other strategy.

Nothing here reads prices to pick a direction: the direction comes only from the card of the day
and the numerology of the date and the coin's name. Price data is used only for the stop distance
(ATR), exactly like the other strategies, so the comparison is fair.

Rules
- Every UTC day, at the first bar of the day, a 78-card deck is shuffled with a seed made of the
  date and the symbol, and the top card is drawn (upright or reversed).
- Card meaning: bullish / bearish / neutral (see MEANINGS). A reversed card flips the meaning.
  Suit of Pentacles (money) counts double.
- Numerology: day number = digits of YYYYMMDD reduced to 1..9 (11, 22 master numbers kept);
  coin number = Pythagorean value of the coin's letters reduced the same way.
  The day "resonates" with the coin when both numbers share the same parity or one is a master.
- Day number meanings: 1, 3, 8 favour action upward; 5, 9 favour change/endings (downward);
  4, 7 are days of rest (no trade); 2, 6 follow the card only.
- Trade when the card is not neutral, the day resonates with the coin, and the number does not
  contradict the card.
"""

from __future__ import annotations

import hashlib
import random
import time

from .config import TarotConfig
from .strategy import Bar, Signal, atr

MAJOR = [
    ("The Fool", 1), ("The Magician", 1), ("The High Priestess", 0), ("The Empress", 1), ("The Emperor", 1),
    ("The Hierophant", 0), ("The Lovers", 1), ("The Chariot", 1), ("Strength", 1), ("The Hermit", -1),
    ("Wheel of Fortune", 1), ("Justice", 0), ("The Hanged Man", -1), ("Death", -1), ("Temperance", 0),
    ("The Devil", -1), ("The Tower", -1), ("The Star", 1), ("The Moon", -1), ("The Sun", 1),
    ("Judgement", 0), ("The World", 1),
]
SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Page", "Knight", "Queen", "King"]
# Minor arcana: traditional "positive" ranks lean bullish, "trouble" ranks bearish; Swords lean bearish.
_MINOR_RANK = {"Ace": 1, "Three": 1, "Six": 1, "Nine": 1, "Ten": 1, "Five": -1, "Seven": -1, "Eight": -1}
_SUIT_BIAS = {"Wands": 0, "Cups": 0, "Swords": -1, "Pentacles": 0}


def _minor_meaning(rank: str, suit: str) -> int:
    base = _MINOR_RANK.get(rank, 0) + _SUIT_BIAS[suit]
    return max(-1, min(1, base)) * (2 if suit == "Pentacles" else 1)


DECK: list[tuple[str, int]] = MAJOR + [(f"{r} of {s}", _minor_meaning(r, s)) for s in SUITS for r in RANKS]
assert len(DECK) == 78

PYTHAGOREAN = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
DAY_BIAS = {1: 1, 3: 1, 8: 1, 5: -1, 9: -1, 4: None, 7: None, 2: 0, 6: 0, 11: 0, 22: 0}
DAY_MS = 86_400_000


def reduce_number(n: int) -> int:
    while n > 9 and n not in (11, 22):
        n = sum(int(d) for d in str(n))
    return n


def day_number(ts_ms: int) -> int:
    return reduce_number(sum(int(d) for d in time.strftime("%Y%m%d", time.gmtime(ts_ms / 1000))))


def coin_number(symbol: str) -> int:
    name = symbol.removesuffix("USDT")
    return reduce_number(sum(PYTHAGOREAN.get(c, 0) for c in name.upper()) or 1)


def draw_card(symbol: str, ts_ms: int) -> tuple[str, bool, int]:
    """(card name, reversed?, meaning) for this coin and UTC day. Deterministic, so it can be tested."""
    day = time.strftime("%Y-%m-%d", time.gmtime(ts_ms / 1000))
    seed = int.from_bytes(hashlib.sha256(f"{symbol}|{day}".encode()).digest()[:8], "big")
    rng = random.Random(seed)
    deck = list(range(78))
    rng.shuffle(deck)
    name, meaning = DECK[deck[0]]
    reversed_ = rng.random() < 0.5
    return name, reversed_, -meaning if reversed_ else meaning


def reading(symbol: str, ts_ms: int) -> tuple[int, str]:
    """Direction (+1 / -1 / 0) and a human-readable explanation."""
    card, rev, meaning = draw_card(symbol, ts_ms)
    dn, cn = day_number(ts_ms), coin_number(symbol)
    text = f"{card}{' (reversed)' if rev else ''}, day number {dn}, {symbol} number {cn}"
    if meaning == 0:
        return 0, text + " -> neutral card"
    resonates = dn in (11, 22) or cn in (11, 22) or dn % 2 == cn % 2
    if not resonates:
        return 0, text + " -> no resonance"
    bias = DAY_BIAS.get(dn, 0)
    if bias is None:
        return 0, text + " -> day of rest"
    direction = 1 if meaning > 0 else -1
    if bias and bias != direction:
        return 0, text + " -> number contradicts the card"
    return direction, text + (" -> LONG" if direction > 0 else " -> SHORT")


class TarotDetector:
    name = "tarot"

    def __init__(self, cfg: TarotConfig, symbol: str):
        self.cfg, self.symbol = cfg, symbol

    @property
    def min_history(self) -> int:
        return self.cfg.atr_period + 1

    def step(self, bars: list[Bar], i: int) -> Signal | None:
        if i < self.min_history or bars[i].ts // DAY_MS == bars[i - 1].ts // DAY_MS:
            return None  # one reading per day, at the first bar of the UTC day
        direction, _ = reading(self.symbol, bars[i].ts)
        if direction == 0:
            return None
        a = atr(bars, i, self.cfg.atr_period)
        if a <= 0:
            return None
        bar = bars[i]
        side = "Buy" if direction > 0 else "Sell"
        strength = float(abs(draw_card(self.symbol, bar.ts)[2]))  # Pentacles count double
        return Signal(side, bar.close, bar.close - direction * self.cfg.stop_atr * a, a, strength, bar.ts, self.name)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Today's tarot + numerology reading per coin")
    ap.add_argument("symbols", nargs="*", default=["BTCUSDT", "SOLUSDT", "DOGEUSDT", "WIFUSDT", "PEPEUSDT"])
    args = ap.parse_args()
    now = int(time.time() * 1000)
    for s in args.symbols:
        print(f"{s:<12} {reading(s, now)[1]}")


if __name__ == "__main__":
    main()
