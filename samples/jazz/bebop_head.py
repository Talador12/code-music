"""Bebop head: fast unison melody in Bb, 240 BPM, Tank!/Bebop style.

Inspired by The Seatbelts / Yoko Kanno — tight trumpet+sax unison,
chromatic passing tones, bebop rhythms.
"""

from code_music import Note, Song, Track

song = Song(title="bebop_head", bpm=240)
r = Note.rest

# Unison trumpet + sax = classic bebop front line
for inst in ("trumpet", "saxophone"):
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.75, swing=0.5))
    head = [
        Note("A#", 4, 0.5),
        Note("D", 5, 0.25),
        Note("F", 5, 0.25),
        Note("A#", 5, 0.5),
        Note("G", 5, 0.25),
        Note("F", 5, 0.25),
        Note("D#", 5, 0.5),
        Note("D", 5, 0.25),
        Note("C", 5, 0.25),
        Note("A#", 4, 1.0),
        r(0.5),
        Note("C", 5, 0.25),
        Note("D", 5, 0.25),
        Note("D#", 5, 0.5),
        Note("F", 5, 0.25),
        Note("G", 5, 0.25),
        Note("A#", 5, 0.5),
        Note("A", 5, 0.25),
        Note("G", 5, 0.25),
        Note("F", 5, 0.5),
        Note("D#", 5, 0.25),
        Note("D", 5, 0.25),
        Note("C", 5, 2.0),
    ]
    tr.extend(head * 2)
