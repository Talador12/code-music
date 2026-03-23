"""scales/enigmatic.py — Enigmatic Scale

    Verdi's 'scala enigmatica' — bizarre interval structure.
        Extremely rare, almost impossible to harmonize.
        Used in: novelty, experimental.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    To play 2 octaves: change octaves=1 to octaves=2 (or 3, etc.)

    Run:
        code-music scales/enigmatic.py -o /tmp/enigmatic.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "enigmatic"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Enigmatic Scale — All Keys", bpm=96)
tr = song.add_track(Track(name="inst", instrument="celesta", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, SCALE_TYPE, octave=4, octaves=1)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
