"""arranged_journey.py — Showcases Song.arrange() with named sections.

A cinematic progression built from reusable Section blocks:
  Intro → Verse → Chorus → Bridge → Chorus → Outro

Uses Section-based composition so the same chorus can appear twice
without duplicating any code. Demonstrates fade_in/fade_out on tracks.

Style: Ambient cinematic, Db major, 96 BPM.
"""

from code_music import (
    Chord,
    Note,
    Section,
    Song,
    reverb,
    scale,
    stereo_width,
)

song = Song(title="Arranged Journey", bpm=96)

r = Note.rest

# ── Sections ───────────────────────────────────────────────────────────────

intro = Section("intro", bars=4)
intro.add_track("pad", [Chord("Db", "maj7", 3, duration=16.0)])
intro.add_track("lead", [r(16.0)])
intro.add_track("bass", [r(16.0)])

verse = Section("verse", bars=4)
verse.add_track(
    "pad",
    [
        Chord("Db", "maj7", 3, duration=4.0),
        Chord("Ab", "maj", 3, duration=4.0),
        Chord("Bb", "min7", 3, duration=4.0),
        Chord("Gb", "maj7", 3, duration=4.0),
    ],
)
verse.add_track("lead", scale("Db", "major", octave=5, length=16))
verse.add_track(
    "bass",
    [
        Note("Db", 2, 4.0),
        Note("Ab", 2, 4.0),
        Note("Bb", 2, 4.0),
        Note("Gb", 2, 4.0),
    ],
)

chorus = Section("chorus", bars=4)
chorus.add_track(
    "pad",
    [
        Chord("Ab", "maj", 3, duration=4.0),
        Chord("Db", "maj", 3, duration=4.0),
        Chord("Eb", "dom7", 3, duration=4.0),
        Chord("Ab", "maj", 3, duration=4.0),
    ],
)
chorus.add_track(
    "lead",
    [
        Note("Ab", 5, 2.0),
        Note("Db", 6, 2.0),
        Note("Eb", 5, 2.0),
        Note("Db", 5, 2.0),
        Note("Ab", 5, 4.0),
        Note("Gb", 5, 4.0),
        Note("Ab", 5, 2.0),
        Note("Bb", 5, 2.0),
    ],
)
chorus.add_track(
    "bass",
    [
        Note("Ab", 2, 4.0),
        Note("Db", 2, 4.0),
        Note("Eb", 2, 4.0),
        Note("Ab", 2, 4.0),
    ],
)

bridge = Section("bridge", bars=2)
bridge.add_track("pad", [Chord("Gb", "maj7", 3, duration=8.0)])
bridge.add_track("lead", [Note("Bb", 5, 2.0), Note("Ab", 5, 2.0), r(4.0)])
bridge.add_track("bass", [Note("Gb", 2, 4.0), Note("Ab", 2, 4.0)])

outro = Section("outro", bars=4)
outro.add_track("pad", [Chord("Db", "maj7", 3, duration=16.0)])
outro.add_track("lead", [r(16.0)])
outro.add_track("bass", [Note("Db", 2, 8.0), r(8.0)])

# ── Arrange ────────────────────────────────────────────────────────────────

song.arrange(
    [intro, verse, chorus, bridge, chorus, outro],
    instruments={"pad": "pad", "lead": "piano", "bass": "bass"},
    volumes={"pad": 0.45, "lead": 0.65, "bass": 0.6},
    pans={"pad": 0.0, "lead": 0.15, "bass": -0.1},
)

# Apply fade_in to pad, fade_out to lead for cinematic feel
for i, track in enumerate(song.tracks):
    if track.name == "pad":
        song.tracks[i] = track.fade_in(beats=8.0)
    elif track.name == "lead":
        song.tracks[i] = track.fade_out(beats=16.0)

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.8, wet=0.35), width=1.6),
    "lead": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
}
