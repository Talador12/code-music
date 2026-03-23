"""scales/japanese.py — Japanese (Hirajoshi)

    5-note koto scale. Alternating large and small intervals.
        Sparse, pentatonic, meditative.
        Used in: Japanese traditional, ambient, film.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/japanese.py -o /tmp/japanese.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "japanese"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Japanese (Hirajoshi) — All Keys", bpm=80)
tr = song.add_track(Track(name="inst", instrument="vibraphone", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.5, velocity=0.72))
    tr.add(Note.rest(1.0))  # pause between keys
