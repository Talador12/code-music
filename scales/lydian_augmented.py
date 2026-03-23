"""scales/lydian_augmented.py — Lydian Augmented

    3rd mode of melodic minor. Lydian with a sharp 5. Very floating.
        Used in: jazz (Maj7#5 chords), film scores, Coltrane.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/lydian_augmented.py -o /tmp/lydian_augmented.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "lydian_augmented"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Lydian Augmented — All Keys", bpm=108)
tr = song.add_track(Track(name="inst", instrument="flute", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
