"""slow_coast.py — Indie / lo-fi crossover. Em, 92 BPM. Third track for Room Tone album.

That Phoebe Bridgers / Japanese Breakfast / Adrianne Lenker space —
indie that's intimate but not precious. Acoustic guitar KS, sparse kit,
a synth pad underneath that you barely notice until you do.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    Song,
    Track,
    compress,
    decrescendo,
    humanize,
    reverb,
    suggest_progression,
    tape_sat,
)

song = Song(title="Slow Coast", bpm=92)

BAR = 4.0
r = Note.rest

PROG = suggest_progression("E", mood="sad", octave=3, duration=BAR, velocity=0.55)

# ── Pad — barely there ────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.28, pan=0.0))
for _ in range(8):
    pad.extend(PROG)

# ── KS acoustic guitar — main voice ──────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.78, pan=-0.1))

# Fingerpicked intro
intro = humanize(
    [
        Note("E", 3, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("E", 5, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("G", 4, EIGHTH),
        Note("E", 3, EIGHTH),
        Note("B", 4, EIGHTH),
    ]
    * 4,
    vel_spread=0.1,
    timing_spread=0.04,
)
gtr.extend(intro)

# Verse: melody emerges
verse = humanize(
    [
        Note("E", 5, DOTTED_QUARTER),
        Note("D", 5, EIGHTH),
        Note("B", 4, HALF),
        Note("C", 5, QUARTER),
        Note("B", 4, QUARTER),
        Note("A", 4, HALF),
        r(QUARTER),
        Note("G", 4, QUARTER),
        Note("A", 4, QUARTER),
        Note("B", 4, QUARTER),
        Note("E", 5, HALF),
        r(HALF),
        Note("D", 5, DOTTED_QUARTER),
        Note("C", 5, EIGHTH),
        Note("B", 4, HALF),
        Note("A", 4, QUARTER),
        Note("G", 4, QUARTER),
        Note("F#", 4, HALF),
        Note("E", 4, HALF),
        r(HALF),
    ]
    * 2,
    vel_spread=0.08,
    timing_spread=0.04,
)
gtr.extend(verse)

# Outro: decrescendo back to picking
outro = decrescendo(humanize(intro[:16], vel_spread=0.1), 0.65, 0.2)
gtr.extend(outro)

# ── Bass — simple, root-based ─────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.65, pan=0.1))
bass_line = humanize(
    [
        Note("E", 2, HALF),
        Note("E", 2, QUARTER),
        Note("F#", 2, QUARTER),
        Note("G", 2, HALF),
        Note("D", 2, HALF),
        Note("C", 2, DOTTED_QUARTER),
        Note("B", 1, EIGHTH),
        Note("A", 1, HALF),
        Note("B", 1, QUARTER),
        Note("C", 2, QUARTER),
        Note("D", 2, HALF),
    ]
    * 6,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(bass_line)
bass.extend([r(BAR)] * 4)

# ── Minimal kit ───────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.65))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

for _ in range(20):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(2.0)])
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.6), r(1.0), Note("D", 3, 1.0, velocity=0.55)]
    )
    hat.extend([Note("F", 5, EIGHTH, velocity=0.28)] * 8)

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

song.effects = {
    "guitar": lambda s, sr: tape_sat(
        reverb(s, sr, room_size=0.5, wet=0.18), sr, drive=1.8, warmth=0.4, wet=0.35
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
    "pad": lambda s, sr: reverb(s, sr, room_size=0.7, wet=0.3),
}
