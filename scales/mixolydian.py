"""scales/mixolydian.py — Mixolydian

    Major scale with a b7. Major feel with bluesy tension.
        Every dominant 7th chord is Mixolydian.
        Used in: blues, classic rock, Celtic, Grateful Dead.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    To play 2 octaves: change octaves=1 to octaves=2 (or 3, etc.)

    Run:
        code-music scales/mixolydian.py -o /tmp/mixolydian.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "mixolydian"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Mixolydian — All Keys", bpm=120)
tr = song.add_track(Track(name="inst", instrument="guitar_electric", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, SCALE_TYPE, octave=4, octaves=1)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
