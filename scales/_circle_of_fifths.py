"""_circle_of_fifths.py — reference: all keys in circle of fifths order.

This file plays all 12 major scales in circle of fifths order:
  C → G → D → A → E → B → F# → C# → G# → D# → A# → F → C

The circle of fifths is the organizing principle of Western tonality.
Moving clockwise = add a sharp. Counter-clockwise = add a flat.

Run:
    make preview-_circle_of_fifths
    code-music scales/_circle_of_fifths.py -o /tmp/circle.wav

Also useful as a reference for key relationships:
  - Keys a fifth apart share 6 of 7 notes
  - Relative minor is 3 semitones below the major root
  - Parallel minor shares the same root

Circle of fifths (sharps → flats):
    C (0#/0b)
    G (1#: F#)
    D (2#: F# C#)
    A (3#: F# C# G#)
    E (4#: F# C# G# D#)
    B (5#: F# C# G# D# A#)
    F#/Gb (6#/6b)
    C#/Db (7#/5b)
    G#/Ab (4b: Bb Eb Ab Db)
    D#/Eb (3b: Bb Eb Ab)
    A#/Bb (2b: Bb Eb)
    F   (1b: Bb)
"""

from code_music import Note, Song, Track, scale

song = Song(title="Circle of Fifths — Major Scales", bpm=120)

# Circle of fifths order: C G D A E B F# C# G# D# A# F
CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

tr = song.add_track(Track(name="piano", instrument="piano", volume=0.75))

for root in CIRCLE:
    notes_up = scale(root, "major", octave=4, length=8)
    notes_down = list(reversed(scale(root, "major", octave=4, length=8)))
    for n in notes_up + notes_down:
        tr.add(Note(n.pitch, duration=0.25, velocity=0.75))
    tr.add(Note.rest(0.5))  # brief pause between keys
