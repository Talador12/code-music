"""scales/bebop_minor.py — Bebop Minor

    Dorian + major 3rd passing tone. 8 notes.
        Bridges minor and major sounds.
        Used in: bebop minor ii-V-i lines, modern jazz.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    To play 2 octaves: change octaves=1 to octaves=2 (or 3, etc.)

    Run:
        code-music scales/bebop_minor.py -o /tmp/bebop_minor.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "bebop_minor"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Bebop Minor — All Keys", bpm=160)
tr = song.add_track(Track(name="inst", instrument="saxophone", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, SCALE_TYPE, octave=4, octaves=1)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
