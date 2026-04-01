"""boot_scoot.py — Bluegrass. A major, 170 BPM. Fourth No Boot Scootin track.

Fast flatpicking, banjo rolls, fiddle melody. Pure acoustic energy.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    humanize,
    reverb,
)

song = Song(title="Boot Scoot", bpm=170, key_sig="A")
BAR = 4.0
r = Note.rest
E8 = EIGHTH

banjo = song.add_track(Track(name="banjo", instrument="banjo_ks", volume=0.8, pan=-0.2))
roll = humanize(
    [
        Note("A", 3, E8),
        Note("C#", 4, E8),
        Note("E", 4, E8),
        Note("A", 4, E8),
        Note("E", 4, E8),
        Note("C#", 4, E8),
        Note("A", 3, E8),
        Note("E", 4, E8),
    ]
    * 6,
    vel_spread=0.1,
    timing_spread=0.02,
)
d_roll = humanize(
    [
        Note("D", 3, E8),
        Note("F#", 4, E8),
        Note("A", 4, E8),
        Note("D", 5, E8),
        Note("A", 4, E8),
        Note("F#", 4, E8),
        Note("D", 3, E8),
        Note("A", 4, E8),
    ]
    * 3,
    vel_spread=0.1,
    timing_spread=0.02,
)
e_roll = humanize(
    [
        Note("E", 3, E8),
        Note("G#", 4, E8),
        Note("B", 4, E8),
        Note("E", 5, E8),
        Note("B", 4, E8),
        Note("G#", 4, E8),
        Note("E", 3, E8),
        Note("B", 4, E8),
    ]
    * 3,
    vel_spread=0.1,
    timing_spread=0.02,
)
banjo.extend(roll + d_roll + e_roll + roll[: len(roll) // 2])

fiddle = song.add_track(Track(name="fiddle", instrument="violin", volume=0.68, pan=0.2))
fiddle.extend([r(BAR)] * 4)
mel = humanize(
    crescendo(
        [
            Note("A", 5, E8),
            Note("B", 5, E8),
            Note("C#", 6, E8),
            Note("E", 6, E8),
            Note("C#", 6, QUARTER),
            Note("A", 5, QUARTER),
            Note("F#", 5, E8),
            Note("A", 5, E8),
            Note("B", 5, QUARTER),
            Note("A", 5, HALF),
            r(HALF),
        ]
        * 3,
        0.55,
        0.9,
    ),
    vel_spread=0.07,
    timing_spread=0.02,
)
fiddle.extend(mel)

bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.72))
bass.extend(
    humanize(
        [
            Note("A", 2, 1.0),
            Note("C#", 3, 1.0),
            Note("E", 3, 1.0),
            Note("A", 2, 1.0),
            Note("D", 2, 1.0),
            Note("F#", 2, 1.0),
            Note("A", 2, 1.0),
            Note("D", 3, 1.0),
            Note("E", 2, 1.0),
            Note("G#", 2, 1.0),
            Note("B", 2, 1.0),
            Note("E", 3, 1.0),
            Note("A", 2, 4.0),
        ]
        * 2,
        vel_spread=0.06,
        timing_spread=0.02,
    )
)

song.effects = {
    "banjo": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.1),
    "fiddle": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.15),
    "bass": lambda s, sr: compress(s, sr, threshold=0.55, ratio=3.0, makeup_gain=1.1),
}
