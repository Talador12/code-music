"""Pluck arpeggio: fast pluck synth arpeggio in Am, for textural highs."""

from code_music import Note, Song, Track

song = Song(title="pluck_arp", bpm=160)
tr = song.add_track(Track(name="pluck", instrument="pluck", volume=0.7))
# Am arpeggio pattern up/down
arp = [
    Note("A", 4, 0.25),
    Note("C", 5, 0.25),
    Note("E", 5, 0.25),
    Note("A", 5, 0.25),
    Note("E", 5, 0.25),
    Note("C", 5, 0.25),
    Note("A", 4, 0.25),
    Note.rest(0.25),
]
for _ in range(4):
    tr.extend(arp)
