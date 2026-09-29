"""Market Rhythm: turn an M1 chart into music and predict the next "note" with a Markov model (no AI).

1. Sonification. Each 1-minute candle becomes a note:
   - pitch    = size/direction of the return (5 buckets -> 5 notes of a pentatonic scale)
   - rhythm   = traded volume (3 buckets): heavy volume -> short, loud notes; quiet -> long, soft notes
   The result is written as a standard MIDI file you can play in any player.

2. Prediction. A variable-order Markov chain (orders 1..max_order, longest context with enough
   history wins) counts which note followed each musical phrase in the past and turns the
   distribution of the next note into an expected return.

3. Honest evaluation. Bucket edges and transition counts are learned on the first part of the data
   only; the rest is scored out-of-sample against a coin flip, gross and after trading costs.

    python -m altcoin_squeeze_bot.rhythm --symbol SOLUSDT --days 7 --midi sol.mid
    python -m altcoin_squeeze_bot.rhythm --synthetic random     # must show NO edge
    python -m altcoin_squeeze_bot.rhythm --synthetic pattern    # hidden rhythm: must be found
"""

from __future__ import annotations

import argparse
import bisect
import math
import random
import struct
from collections import defaultdict
from dataclasses import dataclass

PENTATONIC = [57, 60, 62, 64, 67]  # A3 C4 D4 E4 G4: bucket 0 = strong drop ... 4 = strong rally
N_PITCH = len(PENTATONIC)
N_VOL = 3


@dataclass
class Candle:
    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float


# ---- 1. symbolization ---------------------------------------------------------------------------
def returns(candles: list[Candle]) -> list[float]:
    return [c.close / p.close - 1 for p, c in zip(candles, candles[1:], strict=False)]


def quantile_edges(values: list[float], buckets: int) -> list[float]:
    s = sorted(values)
    return [s[int(len(s) * k / buckets)] for k in range(1, buckets)]


@dataclass
class Scale:
    """Bucket edges learned on training data only (using test data here would leak the future)."""

    ret_edges: list[float]
    vol_edges: list[float]

    @classmethod
    def fit(cls, candles: list[Candle]) -> Scale:
        return cls(quantile_edges(returns(candles), N_PITCH), quantile_edges([c.volume for c in candles], N_VOL))

    def notes(self, candles: list[Candle]) -> list[tuple[int, int]]:
        """(pitch bucket, volume bucket) for every candle after the first."""
        rs = returns(candles)
        return [(bisect.bisect_right(self.ret_edges, r), bisect.bisect_right(self.vol_edges, c.volume))
                for r, c in zip(rs, candles[1:], strict=False)]


# ---- 2. MIDI export (stdlib only) ---------------------------------------------------------------
def _varlen(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))


def to_midi(notes: list[tuple[int, int]], path: str, predicted: list[int] | None = None, bpm: int = 240) -> None:
    """Write notes as MIDI. Volume bucket sets rhythm: 2 -> 1/8 loud, 1 -> 1/4, 0 -> 1/2 soft.

    Predicted continuation (pitch buckets) is appended on channel 2 with a different instrument.
    """
    tpq = 480
    dur = {2: tpq // 2, 1: tpq, 0: tpq * 2}
    vel = {2: 110, 1: 80, 0: 50}
    ev = bytearray()
    ev += _varlen(0) + b"\xff\x51\x03" + struct.pack(">I", 60_000_000 // bpm)[1:]  # tempo
    ev += _varlen(0) + bytes([0xC0, 0])  # channel 1: piano (market)
    ev += _varlen(0) + bytes([0xC1, 73])  # channel 2: flute (prediction)
    for p, v in notes:
        ev += _varlen(0) + bytes([0x90, PENTATONIC[p], vel[v]])
        ev += _varlen(dur[v]) + bytes([0x80, PENTATONIC[p], 0])
    for p in predicted or []:
        ev += _varlen(0) + bytes([0x91, PENTATONIC[p] + 12, 90])
        ev += _varlen(tpq) + bytes([0x81, PENTATONIC[p] + 12, 0])
    ev += _varlen(0) + b"\xff\x2f\x00"
    with open(path, "wb") as fh:
        fh.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq))
        fh.write(b"MTrk" + struct.pack(">I", len(ev)) + ev)


# ---- 3. variable-order Markov predictor ---------------------------------------------------------
class RhythmModel:
    def __init__(self, max_order: int = 4, min_count: int = 20):
        self.max_order, self.min_count = max_order, min_count
        self.counts: dict[tuple, list[int]] = defaultdict(lambda: [0] * N_PITCH)
        self.bucket_mean = [0.0] * N_PITCH  # average return of each pitch bucket (from training)

    def fit(self, notes: list[tuple[int, int]], rets: list[float]) -> RhythmModel:
        sums, ns = [0.0] * N_PITCH, [0] * N_PITCH
        for (p, _), r in zip(notes, rets, strict=True):
            sums[p] += r
            ns[p] += 1
        self.bucket_mean = [s / n if n else 0.0 for s, n in zip(sums, ns, strict=True)]
        for i in range(len(notes) - 1):
            nxt = notes[i + 1][0]
            for k in range(0, self.max_order + 1):
                if i - k + 1 < 0:
                    break
                self.counts[tuple(notes[i - k + 1 : i + 1]) if k else ()][nxt] += 1
        return self

    def distribution(self, context: list[tuple[int, int]]) -> tuple[list[float], int]:
        """Next-pitch probabilities from the longest phrase seen >= min_count times; returns (probs, order)."""
        for k in range(min(self.max_order, len(context)), -1, -1):
            c = self.counts.get(tuple(context[-k:]) if k else ())
            if c and sum(c) >= self.min_count:
                total = sum(c)
                return [x / total for x in c], k
        return [1 / N_PITCH] * N_PITCH, 0

    def expected_return(self, context: list[tuple[int, int]]) -> float:
        probs, _ = self.distribution(context)
        return sum(p * m for p, m in zip(probs, self.bucket_mean, strict=True))

    def continue_melody(self, context: list[tuple[int, int]], n: int) -> list[int]:
        """Most likely next pitches (volume assumed 'normal' for the imagined notes)."""
        ctx, out = list(context), []
        for _ in range(n):
            probs, _ = self.distribution(ctx)
            p = max(range(N_PITCH), key=probs.__getitem__)
            out.append(p)
            ctx.append((p, 1))
        return out


@dataclass
class Evaluation:
    n_signals: int
    hit_rate: float  # share of signals whose direction was right (non-zero next returns)
    z_score: float  # vs a 50% coin flip
    gross_bp: float  # average next-minute return captured per signal, basis points
    net_bp: float  # after round-trip costs
    cost_bp: float

    def __str__(self) -> str:
        return (f"signals={self.n_signals}  hit={self.hit_rate * 100:.2f}% (coin flip 50%)  z={self.z_score:+.2f}\n"
                f"avg gross={self.gross_bp:+.2f}bp  costs={self.cost_bp:.1f}bp  avg NET={self.net_bp:+.2f}bp per trade")


def evaluate(candles: list[Candle], train_frac: float = 0.7, threshold_bp: float = 0.0, max_order: int = 4,
             cost_bp: float = 2 * (5.5 + 1.0)) -> tuple[Evaluation, Scale, RhythmModel]:
    """Fit on the first train_frac of candles, score one-minute-ahead predictions on the rest."""
    cut = int(len(candles) * train_frac)
    train, test = candles[:cut], candles[cut - 1:]
    scale = Scale.fit(train)
    model = RhythmModel(max_order).fit(scale.notes(train), returns(train))

    notes, rets = scale.notes(test), returns(test)
    hits = n = 0
    captured = 0.0
    for i in range(max_order, len(notes) - 1):
        er = model.expected_return(notes[: i + 1][-max_order:])
        if abs(er) * 1e4 <= threshold_bp or er == 0:
            continue
        nxt = rets[i + 1]
        if nxt == 0:
            continue
        side = 1 if er > 0 else -1
        n += 1
        hits += side * nxt > 0
        captured += side * nxt
    hit = hits / n if n else 0.0
    z = (hit - 0.5) / math.sqrt(0.25 / n) if n else 0.0
    gross = captured / n * 1e4 if n else 0.0
    return Evaluation(n, hit, z, gross, gross - cost_bp, cost_bp), scale, model


# ---- data ---------------------------------------------------------------------------------------
def synthetic(kind: str, n: int = 20_000, seed: int = 3) -> list[Candle]:
    """'random': pure random walk (nothing to find). 'pattern': returns follow a hidden rhythm."""
    rng = random.Random(seed)
    price, out, prev = 100.0, [], 0.0
    motif = [1, 1, -1, 0, -1, 1, 0, -1]  # hidden 8-beat rhythm
    for i in range(n):
        if kind == "pattern":
            r = 0.0006 * motif[i % len(motif)] + rng.gauss(0, 0.0005)
        else:
            r = rng.gauss(0, 0.0008)
        prev = r
        o = price
        price *= 1 + prev
        vol = abs(prev) * 1e6 + rng.random() * 500
        out.append(Candle(i * 60_000, o, max(o, price), min(o, price), price, vol))
    return out


def fetch(symbol: str, days: int) -> list[Candle]:
    import time

    from .bybit_client import BybitClient
    from .data import fetch_klines

    end = int(time.time() * 1000)
    kl = fetch_klines(BybitClient(), symbol, 1, end - days * 86_400_000, end)
    return [Candle(int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])) for k in kl]


def main() -> None:
    ap = argparse.ArgumentParser(description="Turn an M1 chart into music and predict the next rhythm")
    ap.add_argument("--symbol", default="SOLUSDT")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--synthetic", choices=("random", "pattern"))
    ap.add_argument("--midi", help="write the last notes (+ predicted continuation) to this .mid file")
    ap.add_argument("--notes", type=int, default=240, help="how many recent candles to put in the MIDI")
    ap.add_argument("--order", type=int, default=4)
    ap.add_argument("--threshold-bp", type=float, default=0.0, help="trade only if |expected| > this")
    ap.add_argument("--csv", help="Binance kline CSV instead of downloading (any timeframe)")
    args = ap.parse_args()

    if args.csv:
        from .data import load_binance_csv

        (bars,) = load_binance_csv(args.csv).values()
        candles = [Candle(b.ts, b.open, b.high, b.low, b.close, b.volume) for b in bars]
    else:
        candles = synthetic(args.synthetic) if args.synthetic else fetch(args.symbol, args.days)
    print(f"{len(candles)} candles")
    ev, scale, model = evaluate(candles, threshold_bp=args.threshold_bp, max_order=args.order)
    print("\n== Out-of-sample prediction of the next note ==")
    print(ev)

    recent = scale.notes(candles[-args.notes - 1:])
    probs, order = model.distribution(recent[-args.order:])
    names = ["strong drop", "drop", "flat", "rise", "strong rise"]
    print(f"\n== Next note (context order {order}) ==")
    for name, p in zip(names, probs, strict=True):
        print(f"  {name:<12} {p * 100:5.1f}%  {'#' * int(p * 50)}")
    er = model.expected_return(recent[-args.order:]) * 1e4
    print(f"  expected next-minute return {er:+.2f}bp vs round-trip cost {ev.cost_bp:.1f}bp")

    if args.midi:
        to_midi(recent, args.midi, model.continue_melody(recent[-args.order:], 16))
        print(f"\nMIDI written to {args.midi} (piano = market, flute = predicted continuation)")

    print("\n== Verdict ==")
    if ev.n_signals >= 500 and ev.z_score > 3 and ev.net_bp > 0:
        print("The rhythm predicts the next minute AND beats costs out-of-sample -> worth a full validation.")
    elif ev.z_score > 3:
        print("There IS a rhythm (better than a coin flip), but it is smaller than trading costs -> not tradable.")
    else:
        print("No rhythm beyond chance: the next note is not predictable from previous notes on this data.")


if __name__ == "__main__":
    main()
