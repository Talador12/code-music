"""Alto saxophone: blues lick in A, bebop-inflected, swung 8ths.

Tank!/Bebop style — think Yoko Kanno / The Seatbelts.
"""

from code_music import Note, Song, Track

song = Song(title="saxophone_blues", bpm=168)
tr = song.add_track(Track(name="sax", instrument="saxophone", volume=0.8, swing=0.55))
# A blues scale: A C D Eb E G
lick = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.25),
    Note("D#", 5, 0.25),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.25),
    Note("C", 5, 0.25),
    Note("A", 4, 2.0),
    Note.rest(0.5),
    Note("C", 5, 0.25),
    Note("D", 5, 0.25),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.25),
    Note("E", 5, 0.25),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 3.0),
]
for _ in range(2):
    tr.extend(lick)
