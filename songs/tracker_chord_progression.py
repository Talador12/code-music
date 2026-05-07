"""tracker_chord_progression.py - chord progression as an ASCII tracker grid.

Eight bars of a I-vi-IV-V progression in C, voiced as triads in the tracker
grid. One row per beat (step duration 1.0), one chord per row.

Run::

    code-music songs/tracker_chord_progression.py --flac
"""

from code_music import AsciiTracker

GRID = """
     PIANO         BASS
00 | C4,E4,G4      C2
01 | C4,E4,G4      C2
02 | C4,E4,G4      C2
03 | C4,E4,G4      C2
04 | A3,C4,E4      A1
05 | A3,C4,E4      A1
06 | A3,C4,E4      A1
07 | A3,C4,E4      A1
08 | F3,A3,C4      F1
09 | F3,A3,C4      F1
10 | F3,A3,C4      F1
11 | F3,A3,C4      F1
12 | G3,B3,D4      G1
13 | G3,B3,D4      G1
14 | G3,B3,D4      G1
15 | G3,B3,D4      G1
"""

song = AsciiTracker.from_string(GRID).to_song(
    bpm=84.0,
    step_duration=1.0,
    instruments={"PIANO": "piano", "BASS": "bass"},
    title="Tracker Chord Progression",
)
