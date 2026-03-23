"""scales/arabic.py — Arabic (Double Harmonic / Byzantine)

    Two tetrachords each with an augmented 2nd. Very dense and tense.
        Also called Byzantine, Raga Bhairav, Hijaz Kar.
        Used in: Middle Eastern music, flamenco, metal.

    All 12 keys in circle of fifths order: C G D A E B F# C# G# D# A# F
    Each key: ascending then descending.

    Run:
        code-music scales/arabic.py -o /tmp/arabic.wav
"""
from code_music import Note, Song, Track, scale

SCALE_TYPE = "arabic"
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

song = Song(title="Arabic (Double Harmonic / Byzantine) — All Keys", bpm=96)
tr = song.add_track(Track(name="inst", instrument="oboe", volume=0.75))

for root in CIRCLE:
    notes_up   = scale(root, SCALE_TYPE, octave=4)
    notes_down = list(reversed(notes_up[:-1]))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.72))
    tr.add(Note.rest(0.5))  # pause between keys
