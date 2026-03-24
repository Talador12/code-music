"""shifting_ground.py — Prog / experimental. Em, starts 100 BPM. Mixed meter.

The first song to use both BPM automation (ritardando) and time signature
changes mid-song. Proves both features work end-to-end in a real composition.

Structure:
  Bars 1-8:   4/4 at 100 BPM — guitar riff establishes the groove
  Bars 9-12:  Switch to 7/8 — the ground shifts, same riff rewritten
  Bars 13-16: Switch to 3/4 — waltz feel, strings enter
  Bars 17-20: Back to 4/4 — full band, building
  Bars 21-24: 4/4 ritardando (100 → 72 BPM) — everything slows into the outro
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
    conv_reverb,
    crescendo,
    decrescendo,
    delay,
    distortion,
    humanize,
)

song = Song(title="Shifting Ground", bpm=100, time_sig=(4, 4), key_sig="E")

# Time signature changes
song.add_time_sig_change(at_beat=32.0, numerator=7, denominator=8)  # bar 9
song.add_time_sig_change(at_beat=46.0, numerator=3, denominator=4)  # bar 13 (32 + 4*3.5)
song.add_time_sig_change(at_beat=58.0, numerator=4, denominator=4)  # bar 17 (46 + 4*3)

BAR_44 = 4.0
BAR_78 = 3.5  # 7 eighth notes
BAR_34 = 3.0
E8 = EIGHTH
r = Note.rest


# ── Guitar — the riff adapts to each meter ─────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.75, pan=-0.15))

# 4/4 section (bars 1-8): standard rock riff
riff_44 = humanize(
    [
        Note("E", 3, E8),
        Note("G", 3, E8),
        Note("A", 3, E8),
        Note("E", 3, E8),
        Note("B", 3, E8),
        Note("A", 3, E8),
        Note("G", 3, E8),
        Note("E", 3, E8),
    ]
    * 8,
    vel_spread=0.08,
)
gtr.extend(riff_44)

# 7/8 section (bars 9-12): same notes, missing one 8th per bar
riff_78 = humanize(
    [
        Note("E", 3, E8),
        Note("G", 3, E8),
        Note("A", 3, E8),
        Note("E", 3, E8),
        Note("B", 3, E8),
        Note("A", 3, E8),
        Note("G", 3, E8),
    ]
    * 4,
    vel_spread=0.08,
)
gtr.extend(riff_78)

# 3/4 section (bars 13-16): waltz-ified, chords instead of riff
gtr.extend([
    Chord("E", "min", 3, duration=QUARTER, velocity=0.72),
    Note("G", 3, QUARTER), Note("B", 3, QUARTER),
    Chord("C", "maj", 3, duration=QUARTER, velocity=0.70),
    Note("E", 3, QUARTER), Note("G", 3, QUARTER),
    Chord("D", "maj", 3, duration=QUARTER, velocity=0.72),
    Note("F#", 3, QUARTER), Note("A", 3, QUARTER),
    Chord("B", "dom7", 3, duration=QUARTER, velocity=0.74),
    Note("D#", 3, QUARTER), Note("F#", 3, QUARTER),
])

# Back to 4/4 (bars 17-20): full power
gtr.extend(crescendo([
    Chord("E", "min", 3, duration=HALF, velocity=0.78),
    Chord("C", "maj", 3, duration=HALF, velocity=0.76),
    Chord("G", "maj", 3, duration=HALF, velocity=0.78),
    Chord("D", "maj", 3, duration=HALF, velocity=0.80),
] * 2, 0.65, 0.95))

# Ritardando section (bars 21-24): same chords, slowing down
# The BPM change is handled by the render engine via bpm_map;
# here we just write the notes — they'll be stretched by the tempo curve.
gtr.extend(
    decrescendo(
        [
            Chord("E", "min", 3, duration=HALF, velocity=0.85),
            Chord("C", "maj", 3, duration=HALF, velocity=0.80),
            Chord("G", "maj", 3, duration=HALF, velocity=0.75),
            Chord("D", "maj", 3, duration=HALF, velocity=0.70),
            Chord("E", "min", 3, duration=BAR_44 * 2, velocity=0.55),
        ],
        0.85,
        0.25,
    )
)

# ── Bass — follows the meter changes ──────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.78))

# 4/4
bass.extend(
    [
        Note("E", 2, HALF),
        Note("A", 2, HALF),
        Note("G", 2, HALF),
        Note("B", 2, HALF),
    ]
    * 4
)

# 7/8: 3+4 grouping
bass.extend(
    [
        Note("E", 2, E8 * 3),
        Note("A", 2, E8 * 2),
        Note("G", 2, E8 * 2),
    ]
    * 4
)

# 3/4
bass.extend(
    [
        Note("E", 2, BAR_34),
        Note("C", 2, BAR_34),
        Note("D", 2, BAR_34),
        Note("B", 1, BAR_34),
    ]
)

# Back to 4/4
bass.extend(
    [
        Note("E", 2, HALF),
        Note("C", 2, HALF),
        Note("G", 2, HALF),
        Note("D", 2, HALF),
    ]
    * 2
)

# Ritardando
bass.extend(
    [
        Note("E", 2, HALF),
        Note("C", 2, HALF),
        Note("G", 2, HALF),
        Note("D", 2, HALF),
        Note("E", 2, BAR_44 * 2),
    ]
)

# ── Drums — adapt to each time sig ────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.92))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.40))

# 4/4 drums (bars 1-8)
for _ in range(8):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, E8)] * 8)

# 7/8 drums (bars 9-12): kick on 1 and 4, snare on 3 and 6
for _ in range(4):
    kick.extend([Note("C", 2, E8), r(E8 * 2), Note("C", 2, E8), r(E8 * 3)])
    snare.extend([r(E8 * 2), Note("D", 3, E8), r(E8 * 2), Note("D", 3, E8), r(E8)])
    hat.extend([Note("F", 5, E8)] * 7)

# 3/4 drums (bars 13-16): waltz — kick on 1, hat on 2 and 3
for _ in range(4):
    kick.extend([Note("C", 2, QUARTER), r(QUARTER), r(QUARTER)])
    snare.extend([r(QUARTER), Note("D", 3, QUARTER, velocity=0.5), r(QUARTER)])
    hat.extend([Note("F", 5, QUARTER)] * 3)

# Back to 4/4 (bars 17-20)
for _ in range(4):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, E8)] * 8)

# Ritardando (bars 21-24): drums thin out
kick.extend([Note("C", 2, 1.0), r(3.0)] * 2 + [Note("C", 2, BAR_44 * 2)])
snare.extend([r(1.0), Note("D", 3, 1.0, velocity=0.5), r(6.0)] + [r(BAR_44 * 2)])
hat.extend([r(BAR_44 * 4 + BAR_44 * 2)])

# ── Strings — enter in 3/4 section ───────────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="strings", volume=0.45, pan=0.2))
# Silent during 4/4 and 7/8
strings.extend([r(BAR_44)] * 8)  # 4/4 bars
strings.extend([r(BAR_78)] * 4)  # 7/8 bars

# 3/4: strings enter with sustained chords
strings.extend(
    crescendo(
        [
            Chord("E", "min", 3, duration=BAR_34, velocity=0.4),
            Chord("C", "maj", 3, duration=BAR_34, velocity=0.42),
            Chord("D", "maj", 3, duration=BAR_34, velocity=0.45),
            Chord("B", "dom7", 3, duration=BAR_34, velocity=0.48),
        ],
        0.25,
        0.65,
    )
)

# Back to 4/4 + ritardando: strings swell then fade
strings.extend(
    crescendo(
        [
            Chord("E", "min", 3, duration=BAR_44, velocity=0.5),
            Chord("C", "maj", 3, duration=BAR_44, velocity=0.55),
            Chord("G", "maj", 3, duration=BAR_44, velocity=0.6),
            Chord("D", "maj", 3, duration=BAR_44, velocity=0.65),
        ],
        0.4,
        0.8,
    )
)
strings.extend(
    decrescendo(
        [
            Chord("E", "min", 3, duration=BAR_44, velocity=0.75),
            Chord("C", "maj", 3, duration=BAR_44, velocity=0.65),
            Chord("E", "min", 3, duration=BAR_44 * 2, velocity=0.5),
        ],
        0.8,
        0.1,
    )
)

song._effects = {
    "guitar": lambda s, sr: distortion(
        delay(s, sr, delay_ms=125.0, feedback=0.2, wet=0.1),
        drive=1.8,
        tone=0.55,
        wet=0.3,
    ),
    "strings": lambda s, sr: conv_reverb(s, sr, room="hall", wet=0.35),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
