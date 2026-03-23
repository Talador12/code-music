"""Clarinet: swinging big-band riff in Bb, medium tempo."""

from code_music import Note, Song, Track

song = Song(title="clarinet_swing", bpm=144)
tr = song.add_track(Track(name="clarinet", instrument="clarinet", volume=0.78, swing=0.5))
riff = [
    Note("A#", 4, 0.5),
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A#", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A#", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 2.0),
    Note.rest(1.0),
]
for _ in range(2):
    tr.extend(riff)
