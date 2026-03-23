"""scales/lydian_dominant.py — Lydian Dominant

    Mixolydian with a sharp 4. Bright + bluesy + floating.
        Used on dominant 7th chords resolving up a half step or tritone.
        Used in: jazz fusion, film (John Williams), Bartok.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/lydian_dominant.py -o /tmp/lydian_dominant.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "lydian_dominant"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Lydian Dominant — All Keys", bpm=112)
tr = song.add_track(Track(name="inst", instrument="rhodes", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
