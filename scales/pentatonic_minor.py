"""scales/pentatonic_minor.py — Minor Pentatonic

    The rock guitar scale. 5 notes, all usable, all powerful.
        Every blues and rock solo. Used in: blues, rock, metal, R&B.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/pentatonic_minor.py -o /tmp/pentatonic_minor.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "pentatonic_minor"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Minor Pentatonic — All Keys", bpm=112)
tr = song.add_track(Track(name="inst", instrument="guitar_electric", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
