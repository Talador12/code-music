"""scales/chromatic.py — Chromatic

    All 12 semitones. Not a tonal scale — a tool for passing tones and tuning.
        Used in: serialism, bebop passing tones, atonal music.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/chromatic.py -o /tmp/chromatic.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "chromatic"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Chromatic — All Keys", bpm=120)
tr = song.add_track(Track(name="inst", instrument="piano", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.125, velocity=0.72))
    tr.add(Note.rest(0.25))  # pause between keys
