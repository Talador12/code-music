"""04 — Arrangement: compose a song from reusable Sections.

Run:  code-music examples/04_arrangement.py --play
"""

from code_music import Chord, EffectsChain, Note, Section, Song, reverb, scale

song = Song(title="Arranged Song", bpm=120)

r = Note.rest

# Define sections — each is a named block of bars with tracks
intro = Section("intro", bars=4)
intro.add_track("pad", [Chord("A", "min7", 3, duration=16.0)])
intro.add_track("lead", [r(16.0)])
intro.add_track("bass", [Note("A", 2, 4.0)] * 4)

verse = Section("verse", bars=4)
verse.add_track(
    "pad",
    [
        Chord("A", "min7", 3, duration=4.0),
        Chord("F", "maj7", 3, duration=4.0),
        Chord("C", "maj", 3, duration=4.0),
        Chord("G", "maj", 3, duration=4.0),
    ],
)
verse.add_track("lead", scale("A", "pentatonic", octave=5, length=16))
verse.add_track(
    "bass",
    [
        Note("A", 2, 4.0),
        Note("F", 2, 4.0),
        Note("C", 2, 4.0),
        Note("G", 2, 4.0),
    ],
)

chorus = Section("chorus", bars=4)
chorus.add_track(
    "pad",
    [
        Chord("F", "maj", 3, duration=4.0),
        Chord("G", "maj", 3, duration=4.0),
        Chord("A", "min", 3, duration=4.0),
        Chord("C", "maj", 3, duration=4.0),
    ],
)
chorus.add_track(
    "lead",
    [
        Note("C", 6, 1.0),
        Note("A", 5, 1.0),
        Note("G", 5, 2.0),
        Note("A", 5, 1.0),
        Note("G", 5, 1.0),
        Note("E", 5, 2.0),
        Note("F", 5, 1.0),
        Note("E", 5, 1.0),
        Note("D", 5, 2.0),
        Note("C", 5, 2.0),
        r(2.0),
    ],
)
chorus.add_track(
    "bass",
    [
        Note("F", 2, 4.0),
        Note("G", 2, 4.0),
        Note("A", 2, 4.0),
        Note("C", 2, 4.0),
    ],
)

# Arrange: define once, use as many times as you want with .repeat()
song.arrange(
    [intro, *verse.repeat(2), *chorus.repeat(2), verse, *chorus.repeat(3)],
    instruments={"pad": "pad", "lead": "piano", "bass": "bass"},
    volumes={"pad": 0.35, "lead": 0.55, "bass": 0.6},
)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
