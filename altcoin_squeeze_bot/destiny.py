"""Destiny profile: personal numerology and birth card of the bot's owner, used as a filter for Chart Tarot.

Classic Pythagorean numerology:
- life path  = all digits of the birth date reduced to 1..9 (master numbers 11, 22, 33 kept)
- expression = letters of the full name (A=1 .. I=9, J=1 ..) reduced the same way
- birth card = Major Arcana number: digits of the birth date summed and reduced to 1..21
- personal year = birth day + birth month + current year, reduced
- personal day  = personal year + calendar month + calendar day, reduced

Destiny mode trades Chart Tarot signals only on the owner's "resonant" personal days (personal day equals
the life path, expression or birth-card number) or when the present card on the chart is the birth card.

Personal data is never stored in the repository: pass it at runtime via --birth / --name or the
BOT_OWNER_BIRTH / BOT_OWNER_NAME environment variables.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from .tarot import MAJOR

PYTHAGOREAN = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
MASTER = (11, 22, 33)


def reduce(n: int, keep_master: bool = True) -> int:
    while n > 9 and not (keep_master and n in MASTER):
        n = sum(int(d) for d in str(n))
    return n


def parse_date(text: str) -> tuple[int, int, int]:
    """'25.07.1988' or '1988-07-25' -> (day, month, year)."""
    if "-" in text:
        y, m, d = (int(x) for x in text.split("-"))
    else:
        d, m, y = (int(x) for x in text.replace("/", ".").split("."))
    return d, m, y


def digits_sum(*numbers: int) -> int:
    return sum(int(c) for n in numbers for c in str(n))


@dataclass(frozen=True)
class Destiny:
    day: int
    month: int
    year: int
    name: str = ""

    @classmethod
    def from_text(cls, birth: str, name: str = "") -> Destiny:
        d, m, y = parse_date(birth)
        return cls(d, m, y, name)

    @classmethod
    def from_env(cls) -> Destiny | None:
        birth = os.environ.get("BOT_OWNER_BIRTH", "")
        return cls.from_text(birth, os.environ.get("BOT_OWNER_NAME", "")) if birth else None

    @property
    def life_path(self) -> int:
        return reduce(digits_sum(self.day, self.month, self.year))

    @property
    def expression(self) -> int:
        return reduce(sum(PYTHAGOREAN.get(c, 0) for c in self.name.upper())) if self.name.strip() else 0

    @property
    def birth_card(self) -> int:
        n = digits_sum(self.day, self.month, self.year)
        while n > 21:
            n = digits_sum(n)
        return n

    def personal_year(self, year: int) -> int:
        return reduce(digits_sum(self.day, self.month, year), keep_master=False)

    def personal_day(self, ts_ms: int) -> int:
        t = time.gmtime(ts_ms / 1000)
        return reduce(self.personal_year(t.tm_year) + digits_sum(t.tm_mon, t.tm_mday), keep_master=False)

    @property
    def resonant_numbers(self) -> set[int]:
        nums = {reduce(self.life_path, False), reduce(self.birth_card, False)}
        if self.expression:
            nums.add(reduce(self.expression, False))
        return nums

    def is_resonant_day(self, ts_ms: int) -> bool:
        return self.personal_day(ts_ms) in self.resonant_numbers

    def describe(self, now_ms: int | None = None) -> str:
        now_ms = now_ms or int(time.time() * 1000)
        t = time.gmtime(now_ms / 1000)
        today = "RESONANT: Chart Tarot may trade" if self.is_resonant_day(now_ms) else "quiet day: birth-card only"
        lines = [
            f"Life path number   : {self.life_path}",
            f"Expression number  : {self.expression or '-'}",
            f"Birth card         : {self.birth_card} - {MAJOR[self.birth_card]}",
            f"Resonant numbers   : {sorted(self.resonant_numbers)}",
            f"Personal year {t.tm_year}: {self.personal_year(t.tm_year)}",
            f"Personal day today : {self.personal_day(now_ms)} -> {today}",
        ]
        return "\n".join(lines)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Owner's numerology profile for destiny mode")
    ap.add_argument("--birth", default=os.environ.get("BOT_OWNER_BIRTH", ""), help="e.g. 25.07.1988")
    ap.add_argument("--name", default=os.environ.get("BOT_OWNER_NAME", ""))
    args = ap.parse_args()
    if not args.birth:
        raise SystemExit("pass --birth DD.MM.YYYY (or set BOT_OWNER_BIRTH)")
    print(Destiny.from_text(args.birth, args.name).describe())


if __name__ == "__main__":
    main()
