"""dembow.py — Reggaeton / dancehall. Gm, 95 BPM. The dembow riddim.

The dembow is the rhythmic backbone of reggaeton — a specific kick+snare
pattern that hasn't changed since Daddy Yankee's Gasolina. Boom-ch-boom-chick.
Simple, relentless, undeniable.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    compress,
    delay,
)

song = Song(title="Dembow", bpm=95)
BAR = 4.0
r = Note.rest
E8 = EIGHTH

# ── Dembow riddim — THE reggaeton beat ─────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))
# Boom-ch-boom-chick (kick on 1+3, snare on 2-and+4-and)
for _ in range(16):
    kick.extend([Note("C", 2, E8), r(E8), r(QUARTER), Note("C", 2, E8), r(E8), r(QUARTER)])
    snare.extend([r(E8), r(E8), Note("D", 3, E8), r(E8), r(E8), r(E8), Note("D", 3, E8), r(E8)])
    hat.extend([Note("F", 5, E8)] * 8)

# ── 808 sub ────────────────────────────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="drums_808", volume=0.88))
sub.extend(
    [Note("G", 1, HALF, velocity=0.9), r(HALF), Note("D#", 1, HALF, velocity=0.85), r(HALF)] * 8
)

# ── Synth stab — offbeat ──────────────────────────────────────────────────
stab = song.add_track(Track(name="stab", instrument="stab", volume=0.55, pan=0.15))
for _ in range(16):
    stab.extend(
        [
            r(E8),
            Chord("G", "min", 3, duration=E8, velocity=0.7),
            r(E8),
            Chord("G", "min", 3, duration=E8, velocity=0.65),
            r(E8),
            Chord("D#", "maj", 3, duration=E8, velocity=0.68),
            r(E8),
            Chord("D#", "maj", 3, duration=E8, velocity=0.62),
        ]
    )

# ── Lead melody ────────────────────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sine", volume=0.52, pan=-0.1))
lead.extend([r(BAR)] * 4)
mel = [
    Note("G", 5, QUARTER),
    r(E8),
    Note("F", 5, E8),
    Note("D#", 5, HALF),
    Note("D", 5, QUARTER),
    r(QUARTER),
    Note("C", 5, HALF),
    r(QUARTER),
    Note("A#", 4, QUARTER),
    Note("C", 5, QUARTER),
    r(QUARTER),
    Note("D", 5, HALF),
    r(HALF),
]
lead.extend(mel * 3)

song.effects = {
    "sub": lambda s, sr: compress(s, sr, threshold=0.4, ratio=6.0, makeup_gain=1.2),
    "lead": lambda s, sr: delay(s, sr, delay_ms=158.0, feedback=0.2, wet=0.12),
}
