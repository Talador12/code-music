"""lagos_nights.py — Afrobeats. Ab major, 108 BPM. The groove that runs Lagos.

Afrobeats is rhythm-first. The kick pattern is syncopated, the shaker
never stops, the guitar plays choppy muted chords on the offbeats, and
the bass sits in a pocket that's somehow both relaxed and urgent.
Burna Boy, Wizkid, Fela Kuti's DNA underneath everything modern.
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
    humanize,
    reverb,
)

song = Song(title="Lagos Nights", bpm=108, key_sig="Ab")

BAR = 4.0
r = Note.rest

# ── Afrobeats kick — syncopated, NOT 4-on-the-floor ───────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
# Classic afrobeats: kick on 1, 2-and, 4
afro_kick = [
    Note("C", 2, EIGHTH),
    r(EIGHTH),
    r(EIGHTH),
    Note("C", 2, EIGHTH),
    r(EIGHTH),
    r(EIGHTH),
    Note("C", 2, EIGHTH),
    r(EIGHTH),
]
for _ in range(16):
    kick.extend(afro_kick)

# ── Snare — 2 and 4, tight ────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
for _ in range(16):
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])

# ── Shaker — 16th notes, the engine ───────────────────────────────────────
shaker = song.add_track(Track(name="shaker", instrument="drums_hat", volume=0.35))
shaker_pat = humanize(
    [Note("F", 6, EIGHTH / 2, velocity=0.45 if i % 2 == 0 else 0.3) for i in range(16)],
    vel_spread=0.08,
)
for _ in range(16):
    shaker.extend(shaker_pat)

# ── Guitar — muted offbeat chops ──────────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_acoustic", volume=0.62, pan=-0.2))
chop = [
    r(EIGHTH),
    Chord("G#", "maj", 3, duration=EIGHTH, velocity=0.72),
    r(EIGHTH),
    Chord("G#", "maj", 3, duration=EIGHTH, velocity=0.68),
    r(EIGHTH),
    Chord("D#", "dom7", 3, duration=EIGHTH, velocity=0.70),
    r(EIGHTH),
    Chord("D#", "dom7", 3, duration=EIGHTH, velocity=0.65),
]
for _ in range(16):
    gtr.extend(chop)

# ── Bass — the pocket ─────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.82))
bass_groove = humanize(
    [
        Note("G#", 2, EIGHTH),
        r(EIGHTH),
        Note("G#", 2, EIGHTH),
        Note("A#", 2, EIGHTH),
        Note("C", 3, QUARTER),
        r(EIGHTH),
        Note("G#", 2, EIGHTH),
        Note("D#", 2, EIGHTH),
        r(EIGHTH),
        Note("D#", 2, EIGHTH),
        Note("F", 2, EIGHTH),
        Note("G#", 2, QUARTER),
        r(QUARTER),
    ],
    vel_spread=0.07,
    timing_spread=0.02,
)
for _ in range(16):
    bass.extend(bass_groove)

# ── Keys — Rhodes, sparse fills ───────────────────────────────────────────
keys = song.add_track(Track(name="keys", instrument="rhodes", volume=0.48, pan=0.2, swing=0.45))
keys.extend([r(BAR)] * 4)
keys_fill = [
    Chord("G#", "maj7", 3, duration=QUARTER, velocity=0.6),
    r(HALF + QUARTER),
    r(HALF),
    Chord("D#", "dom7", 3, duration=QUARTER, velocity=0.58),
    r(QUARTER),
]
for _ in range(12):
    keys.extend(keys_fill)

# ── Lead melody — enters at bar 9 ─────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="flute", volume=0.55, pan=0.1))
lead.extend([r(BAR)] * 8)
mel = humanize(
    [
        Note("G#", 5, QUARTER),
        r(EIGHTH),
        Note("F", 5, EIGHTH),
        Note("D#", 5, HALF),
        Note("C", 5, QUARTER),
        Note("D#", 5, QUARTER),
        r(HALF),
        Note("F", 5, QUARTER),
        r(EIGHTH),
        Note("G#", 5, EIGHTH),
        Note("A#", 5, HALF),
        Note("G#", 5, QUARTER),
        Note("F", 5, QUARTER),
        Note("D#", 5, HALF),
        r(BAR),
    ],
    vel_spread=0.07,
    timing_spread=0.04,
)
lead.extend(mel * 2)

song.effects = {
    "keys": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.15),
    "lead": lambda s, sr: delay(s, sr, delay_ms=278.0, feedback=0.25, wet=0.15),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
