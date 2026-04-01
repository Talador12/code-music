"""eb_minor_elegy.py — Dark orchestral elegy in Eb minor.

Uses enharmonic flats (Eb, Gb, Bb, Cb, Db) and Song.arrange() to build
a structured orchestral piece from intro, theme, development, and coda.
Strings fade in, brass fades out — all using Track.fade_in/fade_out.

Style: Late Romantic orchestral, Eb minor, 80 BPM.
"""

from code_music import (
    Chord,
    Note,
    Section,
    Song,
    reverb,
    stereo_width,
)

song = Song(title="Eb Minor Elegy", bpm=80)

r = Note.rest

# ── Sections ───────────────────────────────────────────────────────────────

intro = Section("intro", bars=4)
intro.add_track("strings", [Chord("Eb", "min", 3, duration=16.0)])
intro.add_track("brass", [r(16.0)])
intro.add_track("cello", [Note("Eb", 2, 8.0), Note("Bb", 2, 8.0)])

theme = Section("theme", bars=4)
theme.add_track(
    "strings",
    [
        Chord("Eb", "min", 3, duration=4.0),
        Chord("Cb", "maj", 3, duration=4.0),
        Chord("Gb", "maj", 3, duration=4.0),
        Chord("Db", "maj", 3, duration=4.0),
    ],
)
theme.add_track(
    "brass",
    [
        Note("Eb", 4, 2.0),
        Note("Gb", 4, 2.0),
        Note("Bb", 4, 2.0),
        Note("Ab", 4, 2.0),
        Note("Gb", 4, 4.0),
        Note("Db", 4, 2.0),
        Note("Eb", 4, 2.0),
    ],
)
theme.add_track(
    "cello",
    [
        Note("Eb", 2, 4.0),
        Note("Cb", 2, 4.0),
        Note("Gb", 2, 4.0),
        Note("Db", 2, 4.0),
    ],
)

development = Section("development", bars=4)
development.add_track(
    "strings",
    [
        Chord("Bb", "min7", 3, duration=4.0),
        Chord("Eb", "min", 3, duration=4.0),
        Chord("Ab", "min7", 3, duration=4.0),
        Chord("Db", "dom7", 3, duration=4.0),
    ],
)
development.add_track(
    "brass",
    [
        Note("Bb", 4, 1.0),
        Note("Ab", 4, 1.0),
        Note("Gb", 4, 1.0),
        Note("Eb", 4, 1.0),
        Note("Db", 4, 2.0),
        Note("Eb", 4, 2.0),
        Note("Ab", 4, 4.0),
        Note("Gb", 4, 2.0),
        Note("Db", 4, 2.0),
    ],
)
development.add_track(
    "cello",
    [
        Note("Bb", 2, 4.0),
        Note("Eb", 2, 4.0),
        Note("Ab", 2, 4.0),
        Note("Db", 2, 4.0),
    ],
)

coda = Section("coda", bars=4)
coda.add_track("strings", [Chord("Eb", "min", 3, duration=16.0)])
coda.add_track("brass", [Note("Eb", 4, 8.0), r(8.0)])
coda.add_track("cello", [Note("Eb", 2, 16.0)])

# ── Arrange ────────────────────────────────────────────────────────────────

song.arrange(
    [intro, theme, development, theme, coda],
    instruments={"strings": "pad", "brass": "sawtooth", "cello": "bass"},
    volumes={"strings": 0.45, "brass": 0.5, "cello": 0.55},
    pans={"strings": 0.0, "brass": 0.2, "cello": -0.15},
)

# Strings fade in, brass fades out at coda
for i, track in enumerate(song.tracks):
    if track.name == "strings":
        song.tracks[i] = track.fade_in(beats=12.0)
    elif track.name == "brass":
        song.tracks[i] = track.fade_out(beats=16.0)

song.effects = {
    "strings": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.75, wet=0.35), width=1.5),
    "brass": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.25),
}
