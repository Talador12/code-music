"""scales/phrygian_dominant.py — Phrygian Dominant

    Phrygian with a major 3rd. The Spanish/Flamenco scale.
        Also called: Spanish Gypsy, Jewish, Ahava Raba.
        Used in: flamenco, Middle Eastern music, klezmer, metal.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/phrygian_dominant.py -o /tmp/phrygian_dominant.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "phrygian_dominant"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Phrygian Dominant — All Keys", bpm=100)
tr = song.add_track(Track(name="inst", instrument="guitar_acoustic", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
