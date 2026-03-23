"""scales/augmented.py — Augmented

    Minor 3rd + half step alternating. 6 notes, symmetric.
        Eerie, unstable, unsettling.
        Used in: Coltrane, Oliver Nelson, Bernard Herrmann film scores.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/augmented.py -o /tmp/augmented.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "augmented"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Augmented — All Keys", bpm=96)
tr = song.add_track(Track(name="inst", instrument="organ", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
