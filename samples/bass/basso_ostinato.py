"""Sub bass pulse: sine-wave E1 for deep electronic music sub-bass."""

from code_music import Note, Song, Track

song = Song(title="sub_bass_pulse", bpm=130)
tr = song.add_track(Track(name="sub", instrument="sine", volume=0.95))
pattern = [
    Note("E", 1, 0.5),
    Note.rest(0.5),
    Note("E", 1, 0.5),
    Note.rest(0.25),
    Note("E", 1, 0.25),
    Note("E", 1, 0.5),
    Note.rest(0.5),
    Note("G", 1, 0.5),
    Note("A", 1, 0.5),
]
for _ in range(3):
    tr.extend(pattern)
