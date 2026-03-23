"""Wobble bass: LFO-swept LP filter on sawtooth — the dubstep bass sound."""

from code_music import Note, Song, Track

song = Song(title="wobble_bass", bpm=140)
tr = song.add_track(Track(name="wobble", instrument="wobble", volume=0.85))
# The LFO rate is 2 Hz — two wobbles per second at default
pattern = [
    Note("C", 2, 0.5),
    Note("C", 2, 0.5),
    Note("C", 2, 0.25),
    Note("D#", 2, 0.25),
    Note("G", 2, 0.5),
    Note("A#", 1, 0.5),
    Note("G", 1, 0.5),
    Note("C", 2, 0.5),
    Note.rest(0.5),
]
for _ in range(4):
    tr.extend(pattern)
