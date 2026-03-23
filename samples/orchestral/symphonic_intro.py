"""Symphonic intro: Beethoven-style 4-bar opening gesture in C minor.

Strings unison → brass response → full tutti.
"""

from code_music import Note, Song, Track

song = Song(title="symphonic_intro", bpm=108)
r = Note.rest

# Unison string motif: famous short-short-short-LONG pattern
for inst, oct, pan_v in [
    ("violin", 5, -0.4),
    ("strings", 4, -0.1),
    ("cello", 3, 0.2),
    ("contrabass", 2, 0.4),
]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.7, pan=pan_v))
    tr.extend(
        [
            Note("G", oct, 0.25),
            Note("G", oct, 0.25),
            Note("G", oct, 0.25),
            Note("D#", oct, 2.0),
            r(0.25),
            Note("F", oct, 0.25),
            Note("F", oct, 0.25),
            Note("F", oct, 0.25),
            Note("D", oct, 2.0),
        ]
    )

# Brass response
for inst, oct, pan_v in [("french_horn", 3, -0.2), ("trumpet", 4, 0.2)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.8, pan=pan_v))
    tr.add(r(3.0))
    tr.extend(
        [
            Note("C", oct, 0.5),
            Note("G", oct - 1, 0.5),
            Note("C", oct, 1.0),
            r(1.0),
            Note("G", oct, 0.5),
            Note("F", oct, 0.5),
            Note("D#", oct, 1.0),
        ]
    )

# Timpani rolls
timp = song.add_track(Track(name="timp", instrument="timpani", volume=0.85))
timp.extend(
    [Note("G", 2, 0.25)] * 4
    + [Note("D#", 2, 2.0), r(0.25)]
    + [Note("F", 2, 0.25)] * 4
    + [Note("D", 2, 2.0)]
)
