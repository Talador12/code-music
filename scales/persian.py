"""scales/persian.py — Persian

    root b2 3 4 b5 b6 7. Similar to double harmonic but with b5.
        Very tense and exotic.
        Used in: experimental, film, Middle Eastern fusion.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/persian.py -o /tmp/persian.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "persian"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Persian — All Keys", bpm=92)
tr = song.add_track(Track(name="inst", instrument="oboe", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
