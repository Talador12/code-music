"""the_room.py — Indie rock. Guitars, space, something unsaid. 104 BPM, Em.

That Radiohead/National aesthetic: not quiet, not loud, just exactly
the right amount of present. The kind of song where the bass does
more emotional work than the melody.

Structure:
  Bars 1-4:   Intro — guitar only, open chord
  Bars 5-12:  Verse — bass + drums enter quietly
  Bars 13-16: Pre-chorus — tension builds
  Bars 17-24: Chorus — full, not explosive but full
  Bars 25-28: Bridge — stripped, most honest moment
  Bars 29-36: Chorus — bigger second time
  Bars 37-40: Outro — guitar only again
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    arp,
    compress,
    crescendo,
    decrescendo,
    delay,
    distortion,
    humanize,
)
from code_music.engine import DOTTED_QUARTER, EIGHTH, HALF, QUARTER

song = Song(title="Room Tone", bpm=104)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Guitar — electric, slightly distorted ────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.68, pan=-0.2))

# Intro: open E minor arpeggio
intro_arp = arp(Chord("E", "min7", 3, duration=BAR, velocity=0.55), pattern="up_down", rate=EIGHTH)
gtr.extend(intro_arp * 4)

# Verse: strummed pattern
verse_strum = [
    Chord("E", "min7", 3, duration=QUARTER, velocity=0.6),
    r(QUARTER),
    Chord("E", "min7", 3, duration=EIGHTH, velocity=0.55),
    r(EIGHTH),
    Chord("G", "maj", 3, duration=QUARTER, velocity=0.62),
    r(QUARTER),
    Chord("D", "maj", 3, duration=HALF, velocity=0.6),
    Chord("C", "maj7", 3, duration=QUARTER, velocity=0.58),
    r(QUARTER),
    Chord("C", "maj7", 3, duration=EIGHTH, velocity=0.55),
    r(EIGHTH),
    Chord("A", "min7", 3, duration=QUARTER, velocity=0.6),
    r(QUARTER),
    Chord("B", "dom7", 3, duration=HALF, velocity=0.65),
]
gtr.extend(verse_strum * 4)  # bars 5-12 (repeat twice)

# Pre-chorus: faster, building
pre = [
    Chord("C", "maj7", 3, duration=HALF, velocity=0.7),
    Chord("G", "maj", 3, duration=HALF, velocity=0.72),
    Chord("D", "maj", 3, duration=HALF, velocity=0.75),
    Chord("B", "dom7", 3, duration=HALF, velocity=0.78),
]
gtr.extend(pre)  # bars 13-16

# Chorus: bigger, more presence
chorus_gtr = [
    Chord("E", "min", 3, duration=QUARTER, velocity=0.8),
    r(EIGHTH),
    Chord("E", "min", 3, duration=EIGHTH, velocity=0.75),
    Chord("G", "maj", 3, duration=HALF, velocity=0.78),
    Chord("D", "maj", 3, duration=QUARTER, velocity=0.8),
    r(EIGHTH),
    Chord("D", "maj", 3, duration=EIGHTH, velocity=0.75),
    Chord("C", "maj", 3, duration=HALF, velocity=0.78),
]
gtr.extend(chorus_gtr * 4)  # bars 17-24

# Bridge: very sparse, quiet
bridge_arp = arp(Chord("A", "min7", 3, duration=BAR, velocity=0.4), pattern="up", rate=QUARTER)
gtr.extend(bridge_arp)
gtr.extend(arp(Chord("E", "min7", 3, duration=BAR, velocity=0.38), pattern="up", rate=QUARTER))
gtr.extend(arp(Chord("C", "maj7", 3, duration=BAR, velocity=0.4), pattern="up", rate=QUARTER))
gtr.extend(arp(Chord("B", "dom7", 3, duration=BAR, velocity=0.42), pattern="up", rate=QUARTER))

# Second chorus: same but louder
gtr.extend(crescendo(chorus_gtr * 4, start_vel=0.75, end_vel=0.95))  # 29-36

# Outro: back to intro arp, decrescendo
outro_arp = arp(Chord("E", "min7", 3, duration=BAR, velocity=0.5), pattern="up_down", rate=EIGHTH)
gtr.extend(decrescendo(outro_arp * 4, start_vel=0.55, end_vel=0.15))

# ── Bass — does the emotional heavy lifting ────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.75, pan=0.15))
bass.extend(bars(4))  # intro: no bass

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
    * 8,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(bass_line)

# Bridge bass: root only, very sustained
bass.extend(
    [
        Note("A", 1, BAR, velocity=0.5),
        Note("E", 1, BAR, velocity=0.48),
        Note("C", 2, BAR, velocity=0.5),
        Note("B", 1, BAR, velocity=0.52),
    ]
)

# Chorus 2 + outro bass
bass.extend(
    humanize(
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
    )
)

# ── Drums — restrained, deliberate ────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.88))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.78))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))

kick.extend(bars(4))
snare.extend(bars(4))
hat.extend(bars(4))

for _ in range(32):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5)] * 8)

kick.extend(bars(4))
snare.extend(bars(4))
hat.extend(bars(4))

song._effects = {
    "guitar": lambda s, sr: distortion(
        delay(s, sr, delay_ms=125.0, feedback=0.2, wet=0.1), drive=1.8, tone=0.55, wet=0.35
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
