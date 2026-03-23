"""scales/in_sen.py — In-Sen

    Japanese 5-note scale: root b2 4 5 b7. Sparse and haunting.
        Used in: Japanese traditional, experimental, ambient.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    To play 2 octaves: change octaves=1 to octaves=2 (or 3, etc.)

    Run:
        code-music scales/in_sen.py -o /tmp/in_sen.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "in_sen"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="In-Sen — All Keys", bpm=72)
tr = song.add_track(Track(name="inst", instrument="vibraphone", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, SCALE_TYPE, octave=4, octaves=1)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.5, velocity=0.72))
    tr.add(Note.rest(1.0))  # pause between keys
