"""Hoover lead: detuned square wave stack, rave/Mord Fustang energy, Am, 138 BPM."""

from code_music import Note, Song, Track

song = Song(title="hoover_lead", bpm=138)
tr = song.add_track(Track(name="hoover", instrument="hoover", volume=0.7, pan=0.0))
riff = [
    Note("A", 3, 0.5),
    Note("C", 4, 0.5),
    Note("E", 4, 1.0),
    Note("G", 4, 0.5),
    Note("E", 4, 0.5),
    Note("C", 4, 1.0),
    Note("A", 3, 0.5),
    Note("B", 3, 0.5),
    Note("C", 4, 0.5),
    Note("E", 4, 0.5),
    Note("A", 4, 2.0),
]
for _ in range(3):
    tr.extend(riff)
