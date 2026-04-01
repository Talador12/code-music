"""east_coast_night.py — Hip-hop / boom bap. Am, 92 BPM. Sampled-feel jazz chords.

Classic East Coast hip-hop production: minor chord samples, hard kick and snare,
swung hi-hats. Nas, Jay-Z, Notorious B.I.G. era. The kind of production where
a 4-bar loop with jazz chords and dusty drums is everything.
Swung 8ths, piano as the melodic center.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    bitcrush,
    chorus,
    compress,
    humanize,
    reverb,
    tape_sat,
)

song = Song(title="East Coast Night", bpm=92)

BAR = 4.0
SWING = 0.54
r = Note.rest

# ── Boom bap kick — hard, punchy ──────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.98))
kick_pat = [
    Note("C", 2, 1.0, velocity=0.98),
    r(0.5),
    Note("C", 2, 0.5, velocity=0.75),
    r(1.0),
    Note("C", 2, 0.5, velocity=0.88),
    r(0.5),
]
for _ in range(12):
    kick.extend(kick_pat)

# ── Snare — 2 & 4, crisp ─────────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.88))
for _ in range(12):
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.92), r(1.0), Note("D", 3, 1.0, velocity=0.88)]
    )

# ── Swung hi-hats ─────────────────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45, swing=SWING))
for _ in range(12):
    hat.extend([Note("F", 5, EIGHTH, velocity=0.55)] * 8)

# ── Piano chops — the "sample" ────────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.72, swing=SWING, pan=-0.1))
# Classic boom bap: chord on 1, chord voicing on 2-and
chop_bar = [
    Chord("A", "min7", 3, duration=EIGHTH, velocity=0.78),
    r(EIGHTH),
    Chord("A", "min7", 3, duration=EIGHTH, velocity=0.72),
    r(QUARTER + EIGHTH),
    Chord("G", "dom7", 3, duration=EIGHTH, velocity=0.75),
    r(EIGHTH),
    Chord("G", "dom7", 3, duration=EIGHTH, velocity=0.70),
    r(QUARTER + EIGHTH),
]
for _ in range(12):
    piano.extend(chop_bar)

# ── Bass — root lock, sub-heavy ───────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.82, swing=SWING))
bass_line = humanize(
    [
        Note("A", 2, QUARTER),
        Note("A", 2, EIGHTH),
        r(EIGHTH),
        Note("G", 2, QUARTER),
        r(QUARTER),
        Note("F", 2, QUARTER),
        Note("G", 2, EIGHTH),
        Note("A", 2, EIGHTH),
        Note("E", 2, HALF),
    ],
    vel_spread=0.08,
    timing_spread=0.02,
)
for _ in range(12):
    bass.extend(bass_line)

# ── Sparse jazz melody — Rhodes, enters at bar 5 ─────────────────────────
mel = song.add_track(Track(name="mel", instrument="rhodes", volume=0.52, swing=SWING, pan=0.2))
mel.extend([r(BAR)] * 4)
phrase = humanize(
    [
        r(QUARTER + EIGHTH),
        Note("E", 5, EIGHTH),
        r(QUARTER),
        Note("C", 5, HALF),
        r(BAR),
        r(EIGHTH),
        Note("A", 4, EIGHTH),
        Note("C", 5, QUARTER),
        r(HALF),
        Note("G", 4, HALF),
        r(HALF),
    ],
    vel_spread=0.09,
    timing_spread=0.05,
)
mel.extend(phrase * 4)

song.effects = {
    "piano": lambda s, sr: bitcrush(
        tape_sat(reverb(s, sr, room_size=0.45, wet=0.2), sr, drive=1.6, warmth=0.5, wet=0.4),
        sr,
        bit_depth=12,
        downsample=1,
        wet=0.3,
    ),
    "mel": lambda s, sr: chorus(reverb(s, sr, room_size=0.4, wet=0.15), sr, rate_hz=0.5, wet=0.15),
    "bass": lambda s, sr: compress(s, sr, threshold=0.45, ratio=5.0, makeup_gain=1.2),
}
