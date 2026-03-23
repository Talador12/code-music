"""scales/harmonic_minor.py — Harmonic Minor

    Natural minor with a raised 7th. Half-step pull to the root.
        That augmented 2nd (b6 to 7) is the characteristic sound.
        Used in: classical cadences, flamenco, metal, film scores.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/harmonic_minor.py -o /tmp/harmonic_minor.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "harmonic_minor"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Harmonic Minor — All Keys", bpm=108)
tr = song.add_track(Track(name="inst", instrument="piano", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
