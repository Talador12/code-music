"""mosh_pit.py — Metal. Cm, 168 BPM. Double kick, distorted everything.

Fourth track for Fault Line album. Faster and meaner than fault_lines.
Straight 4/4 at speed — no odd time tricks, just velocity.
"""

from code_music import (
    EIGHTH,
    HALF,
    Chord,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    distortion,
)

song = Song(title="Mosh Pit", bpm=168)
BAR = 4.0
r = Note.rest
E8 = EIGHTH

gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.78, pan=-0.2))
riff = [
    Note("C", 3, E8),
    Note("C", 3, E8),
    Note("D#", 3, E8),
    Note("C", 3, E8),
    Note("F", 3, E8),
    Note("D#", 3, E8),
    Note("C", 3, E8),
    Note("A#", 2, E8),
]
gtr.extend(riff * 8)
gtr.extend(
    crescendo(
        [
            Chord("C", "min", 2, duration=HALF, velocity=0.8),
            Chord("G#", "maj", 2, duration=HALF, velocity=0.78),
        ]
        * 4,
        0.7,
        1.0,
    )
)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.82))
bass.extend(
    [
        Note("C", 2, E8),
        Note("C", 2, E8),
        r(E8),
        Note("C", 2, E8),
        Note("D#", 2, E8),
        r(E8),
        Note("F", 2, E8),
        Note("C", 2, E8),
    ]
    * 8
)
bass.extend([Note("C", 2, HALF), Note("G#", 1, HALF)] * 4)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, E8)] * (12 * 8))  # double kick 8ths

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.85))
for _ in range(12):
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
hat.extend([Note("F", 5, E8)] * (12 * 8))

song._effects = {
    "guitar": lambda s, sr: distortion(s, drive=4.0, tone=0.65, wet=0.75),
    "bass": lambda s, sr: distortion(
        compress(s, sr, threshold=0.4, ratio=6.0, makeup_gain=1.2), drive=2.0, tone=0.5, wet=0.4
    ),
}
