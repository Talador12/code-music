"""scales/pentatonic_major.py — Major Pentatonic

    5 notes — removes the 4th and 7th. Every note consonant with every other.
        The universal scale: folk, country, blues, rock, Celtic.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/pentatonic_major.py -o /tmp/pentatonic_major.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "pentatonic"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Major Pentatonic — All Keys", bpm=120)
tr = song.add_track(Track(name="inst", instrument="guitar_acoustic", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
