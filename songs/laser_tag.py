"""laser_tag.py — Cosmic electro. Bb major, 126 BPM. Fourth Neon Lollipop track.

More aggressive arp pattern than neon_grid, funkier bass.
"""

from code_music import (
    EIGHTH,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    arp,
    chorus,
    compress,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="Laser Tag", bpm=126)
BAR = 4.0
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * (16 * 4))
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.78))
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 16)
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (16 * 4))

laser = song.add_track(Track(name="laser", instrument="hoover", volume=0.58, pan=0.15))
for ch, sh in [("A#", "maj7"), ("G", "min7"), ("D#", "maj7"), ("F", "dom7")] * 4:
    laser.extend(arp(Chord(ch, sh, 4), pattern="cascade", rate=0.25, octaves=2))

bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.82))
for p, o in [("A#", 2), ("G", 2), ("D#", 2), ("F", 2)] * 4:
    bass.extend(
        [
            Note(p, o, EIGHTH),
            Note(p, o, EIGHTH),
            r(EIGHTH),
            Note(p, o + 1, EIGHTH),
            Note(p, o, QUARTER),
            r(QUARTER),
        ]
    )

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.38))
for ch, sh in [("A#", "maj7"), ("G", "min7"), ("D#", "maj7"), ("F", "dom7")] * 4:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.5))

song._effects = {
    "laser": lambda s, sr: chorus(
        delay(s, sr, delay_ms=198.0, feedback=0.25, wet=0.18), sr, rate_hz=1.0, wet=0.4
    ),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.65, wet=0.25), width=1.7),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
