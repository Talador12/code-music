"""Pluck guitar: fingerpicked Am arpeggio pattern mimicking classical guitar."""

from code_music import Note, Song, Track

song = Song(title="pluck_guitar", bpm=100)
tr = song.add_track(Track(name="guitar", instrument="pluck", volume=0.8))
# Classic Am arpeggio: Am - F - C - G (Pachelbel-ish)
patterns = {
    "Am": [Note("A", 3, 0.5), Note("E", 4, 0.5), Note("A", 4, 0.5), Note("C", 5, 0.5)],
    "F": [Note("F", 3, 0.5), Note("C", 4, 0.5), Note("F", 4, 0.5), Note("A", 4, 0.5)],
    "C": [Note("C", 3, 0.5), Note("G", 3, 0.5), Note("C", 4, 0.5), Note("E", 4, 0.5)],
    "G": [Note("G", 3, 0.5), Note("D", 4, 0.5), Note("G", 4, 0.5), Note("B", 4, 0.5)],
}
for _ in range(3):
    for _, pat in patterns.items():
        tr.extend(pat)
