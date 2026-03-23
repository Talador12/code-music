"""scales/locrian.py — Locrian

    The unstable mode: b2, b5, b7. Tense, unresolved.
        Rarely used as a tonal center since the tonic chord is diminished.
        Used in: metal, jazz (Locrian #2), experimental.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    To play 2 octaves: change octaves=1 to octaves=2 (or 3, etc.)

    Run:
        code-music scales/locrian.py -o /tmp/locrian.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "locrian"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Locrian — All Keys", bpm=96)
tr = song.add_track(Track(name="inst", instrument="square", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, SCALE_TYPE, octave=3, octaves=1)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
