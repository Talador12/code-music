"""quarter_life.py — Indie pop / bedroom pop. D major, 95 BPM.

That Phoebe Bridgers / boygenius / beabadoobee register — intimate,
slightly off-kilter, emotionally specific. Guitar sounds like it was
recorded in a bedroom. Drums are there but not assertive. The melody
is the whole thing. No production sheen. Just the song.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    decrescendo,
    delay,
    humanize,
    reverb,
    suggest_progression,
    tape_sat,
)

song = Song(title="Quarter Life", bpm=95, key_sig="D")

BAR = 4.0
r = Note.rest

PROG = suggest_progression("D", mood="sad", octave=3, duration=BAR, velocity=0.58, variation=1)

# ── Acoustic guitar KS — fingerpicked ────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_ks", volume=0.75, pan=-0.1))
gtr_intro = humanize(
    [
        Note("D", 3, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("D", 3, EIGHTH),
        Note("A", 4, EIGHTH),
    ]
    * 4,
    vel_spread=0.10,
    timing_spread=0.03,
)
gtr.extend(gtr_intro)

gtr_verse = humanize(
    [
        Note("D", 3, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("A", 4, QUARTER),
        Note("D", 5, EIGHTH),
        Note("A", 4, EIGHTH),
        Note("F#", 4, QUARTER),
        Note("B", 3, EIGHTH),
        Note("D", 4, EIGHTH),
        Note("F#", 4, QUARTER),
        Note("A", 4, EIGHTH),
        Note("F#", 4, EIGHTH),
        Note("D", 4, QUARTER),
        Note("G", 3, EIGHTH),
        Note("B", 4, EIGHTH),
        Note("D", 5, QUARTER),
        Note("G", 5, EIGHTH),
        Note("D", 5, EIGHTH),
        Note("B", 4, QUARTER),
        Note("A", 3, EIGHTH),
        Note("C#", 4, EIGHTH),
        Note("E", 4, QUARTER),
        Note("A", 4, EIGHTH),
        Note("E", 4, EIGHTH),
        Note("C#", 4, QUARTER),
    ]
    * 4,
    vel_spread=0.08,
    timing_spread=0.03,
)
gtr.extend(gtr_verse)
gtr.extend(decrescendo(gtr_intro[: len(gtr_intro) // 2], 0.65, 0.2))

# ── Lead vocal melody — piano proxy ───────────────────────────────────────
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.72, pan=0.05))
mel.extend([r(BAR)] * 4)

phrase = humanize(
    crescendo(
        [
            Note("D", 5, DOTTED_QUARTER),
            Note("E", 5, EIGHTH),
            Note("F#", 5, HALF),
            Note("E", 5, QUARTER),
            Note("D", 5, QUARTER),
            r(HALF),
            r(QUARTER),
            Note("B", 4, QUARTER),
            Note("D", 5, QUARTER),
            Note("E", 5, QUARTER),
            Note("F#", 5, WHOLE),
            r(HALF),
            Note("A", 4, DOTTED_QUARTER),
            Note("B", 4, EIGHTH),
            Note("D", 5, HALF),
            Note("C#", 5, QUARTER),
            Note("B", 4, QUARTER),
            r(HALF),
            r(QUARTER),
            Note("G", 4, QUARTER),
            Note("A", 4, HALF),
            Note("D", 4, WHOLE),
            r(BAR),
        ],
        0.45,
        0.88,
    ),
    vel_spread=0.07,
    timing_spread=0.05,
)
mel.extend(phrase)
mel.extend(phrase)
mel.extend(decrescendo(phrase[: len(phrase) // 2], 0.8, 0.2))

# ── Bass — low-key ────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.62, pan=0.1))
bass.extend([r(BAR)] * 4)
bass_line = humanize(
    [
        Note("D", 2, HALF),
        r(QUARTER),
        Note("F#", 2, QUARTER),
        Note("B", 1, HALF),
        r(QUARTER),
        Note("D", 2, QUARTER),
        Note("G", 2, HALF),
        r(QUARTER),
        Note("A", 2, QUARTER),
        Note("A", 1, HALF),
        r(HALF),
    ]
    * 6,
    vel_spread=0.07,
    timing_spread=0.02,
)
bass.extend(bass_line)
bass.extend([r(BAR)] * 4)

# ── Minimal drums ──────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.72))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.62))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.28))

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

for _ in range(14):
    kick.extend(
        [Note("C", 2, 1.0, velocity=0.68), r(0.5), Note("C", 2, 0.5, velocity=0.55), r(2.0)]
    )
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.60), r(1.0), Note("D", 3, 1.0, velocity=0.55)]
    )
    hat.extend([Note("F", 5, EIGHTH, velocity=0.25)] * 8)

kick.extend([r(BAR)] * 4)
snare.extend([r(BAR)] * 4)
hat.extend([r(BAR)] * 4)

song._effects = {
    "guitar": lambda s, sr: tape_sat(
        reverb(s, sr, room_size=0.45, wet=0.16), sr, drive=1.6, warmth=0.45, wet=0.3
    ),
    "melody": lambda s, sr: delay(
        reverb(s, sr, room_size=0.5, wet=0.2), sr, delay_ms=316.0, feedback=0.2, wet=0.12
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.55, ratio=3.5, makeup_gain=1.1),
}
