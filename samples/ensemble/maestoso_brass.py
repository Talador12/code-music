"""Brass quintet sunrise: 2 trumpets + French horn + trombone + tuba.
G major, 84 BPM. The American fanfare sound. Copland country.

Energizing. Bright brass in major. Wide open harmonics.
The feeling of large landscapes and forward motion.
"""

from code_music import Note, Song, Track, crescendo, humanize, reverb, stereo_width

song = Song(title="brass_quintet_sunrise", bpm=84)

lines = {
    "tpt1": (
        "trumpet",
        4,
        -0.45,
        [
            Note("G", 4, 1.0),
            Note("B", 4, 1.0),
            Note("D", 5, 2.0),
            Note("E", 5, 1.0),
            Note("D", 5, 0.5),
            Note("B", 4, 0.5),
            Note("G", 4, 2.0),
            Note("A", 4, 1.0),
            Note("C", 5, 0.5),
            Note("D", 5, 0.5),
            Note("G", 5, 4.0),
        ],
    ),
    "tpt2": (
        "trumpet",
        4,
        -0.15,
        [
            Note("D", 4, 1.0),
            Note("G", 4, 1.0),
            Note("B", 4, 2.0),
            Note("C", 5, 1.0),
            Note("B", 4, 0.5),
            Note("G", 4, 0.5),
            Note("D", 4, 2.0),
            Note("F#", 4, 1.0),
            Note("A", 4, 1.0),
            Note("D", 5, 4.0),
        ],
    ),
    "horn": (
        "french_horn",
        3,
        0.15,
        [
            Note("G", 3, 2.0),
            Note("D", 4, 2.0),
            Note("G", 4, 1.0),
            Note("F#", 4, 1.0),
            Note("E", 4, 2.0),
            Note("C", 4, 1.0),
            Note("D", 4, 1.0),
            Note("G", 3, 4.0),
        ],
    ),
    "tbn": (
        "trombone",
        3,
        0.3,
        [
            Note("B", 3, 2.0),
            Note("G", 3, 2.0),
            Note("E", 4, 1.0),
            Note("D", 4, 1.0),
            Note("B", 3, 2.0),
            Note("A", 3, 1.0),
            Note("B", 3, 1.0),
            Note("G", 3, 4.0),
        ],
    ),
    "tuba": (
        "tuba",
        2,
        0.45,
        [
            Note("G", 2, 2.0),
            Note("D", 2, 2.0),
            Note("C", 3, 2.0),
            Note("G", 2, 2.0),
            Note("D", 2, 2.0),
            Note("G", 2, 4.0),
        ],
    ),
}

for name, (inst, oct, pan_v, melody) in lines.items():
    tr = song.add_track(Track(name=name, instrument=inst, volume=0.78, pan=pan_v))
    tr.extend(humanize(crescendo(melody, 0.4, 0.92), vel_spread=0.04))

song._effects = {
    k: lambda s, sr: stereo_width(reverb(s, sr, room_size=0.72, wet=0.25), width=1.4) for k in lines
}
