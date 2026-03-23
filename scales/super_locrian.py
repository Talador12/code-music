"""scales/super_locrian.py — Super Locrian (Altered Scale)

    7th mode of melodic minor. b9, #9, b5/#11, b13 — every alteration.
        The jazz altered scale for V7alt chords.
        Used in: jazz (Parker, Coltrane, Hancock), fusion.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/super_locrian.py -o /tmp/super_locrian.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "super_locrian"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Super Locrian (Altered Scale) — All Keys", bpm=112)
tr = song.add_track(Track(name="inst", instrument="saxophone", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
