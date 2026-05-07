"""tracker_trance.py - 16-step tracker grid in the Switch Angel style.

Demonstrates :mod:`code_music.ascii_tracker`. The whole song is a single
multi-line grid string; each column is a voice, each row is a sixteenth
note step at 138 BPM (classic trance tempo).

Run::

    code-music songs/tracker_trance.py --flac
"""

from code_music import AsciiTracker

GRID = """
     KICK SNARE HAT  BASS LEAD PAD
00 | C2   ...   C5   F1   ...  F3,A3,C4
01 | ...  ...   C5   ...  ...  ...
02 | ...  ...   C5   F1   A4   ...
03 | ...  ...   C5   ...  ...  ...
04 | C2   D2    C5   F1   ...  F3,A3,C4
05 | ...  ...   C5   ...  ...  ...
06 | ...  ...   C5   F1   C5   ...
07 | ...  ...   C5   ...  ...  ...
08 | C2   ...   C5   F1   ...  E3,G3,Bb3
09 | ...  ...   C5   ...  ...  ...
10 | ...  ...   C5   F1   D5   ...
11 | ...  ...   C5   ...  ...  ...
12 | C2   D2    C5   F1   ...  E3,G3,Bb3
13 | ...  ...   C5   ...  ...  ...
14 | ...  ...   C5   F1   F5   ...
15 | ...  ...   C5   ...  Eb5  ...
"""

INSTRUMENTS = {
    "KICK": "drums_kick",
    "SNARE": "drums_snare",
    "HAT": "drums_hat",
    "BASS": "bass",
    "LEAD": "supersaw",
    "PAD": "pad",
}

song = AsciiTracker.from_string(GRID).to_song(
    bpm=138.0,
    instruments=INSTRUMENTS,
    title="Tracker Trance",
)
