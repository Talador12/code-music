"""disco_revival.py — Disco. Gm, 118 BPM. Studio 54 four-on-the-floor.

Classic disco with octave bass, string stabs, and a Nile Rodgers-style
funky guitar. Uses Section.repeat for the verse-chorus loop.

Style: Disco, Gm, 118 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, compress, reverb

song = Song(title="Disco Revival", bpm=118)

r = Note.rest

verse = Section("verse", bars=4)
verse.add_track(
    "bass",
    [
        Note("G", 2, 0.5),
        Note("G", 3, 0.5),
        Note("G", 2, 0.5),
        Note("G", 3, 0.5),
        Note("Bb", 2, 0.5),
        Note("Bb", 3, 0.5),
        Note("Bb", 2, 0.5),
        Note("Bb", 3, 0.5),
        Note("C", 3, 0.5),
        Note("C", 4, 0.5),
        Note("C", 3, 0.5),
        Note("C", 4, 0.5),
        Note("D", 3, 0.5),
        Note("D", 4, 0.5),
        Note("D", 3, 0.5),
        Note("D", 4, 0.5),
    ],
)
verse.add_track(
    "strings",
    [
        Chord("G", "min", 4, duration=0.5),
        r(1.5),
        Chord("G", "min", 4, duration=0.5),
        r(1.5),
        Chord("Bb", "maj", 4, duration=0.5),
        r(1.5),
        Chord("Bb", "maj", 4, duration=0.5),
        r(1.5),
        Chord("C", "min", 4, duration=0.5),
        r(1.5),
        Chord("C", "min", 4, duration=0.5),
        r(1.5),
        Chord("D", "dom7", 4, duration=0.5),
        r(1.5),
        Chord("D", "dom7", 4, duration=0.5),
        r(1.5),
    ],
)
verse.add_track(
    "guitar",
    [
        r(0.5),
        Note("G", 4, 0.25),
        Note("Bb", 4, 0.25),
        r(0.5),
        Note("D", 5, 0.25),
        Note("Bb", 4, 0.25),
        r(0.5),
        Note("G", 4, 0.5),
        r(0.5),
        Note("Bb", 4, 0.25),
        Note("D", 5, 0.25),
        r(0.5),
        Note("G", 5, 0.25),
        Note("D", 5, 0.25),
        r(0.5),
        Note("Bb", 4, 0.5),
        r(0.5),
        Note("C", 5, 0.25),
        Note("Eb", 5, 0.25),
        r(0.5),
        Note("G", 5, 0.25),
        Note("Eb", 5, 0.25),
        r(0.5),
        Note("C", 5, 0.5),
        r(0.5),
        Note("D", 5, 0.25),
        Note("F#", 5, 0.25),
        r(0.5),
        Note("A", 5, 0.25),
        Note("F#", 5, 0.25),
        r(0.5),
        Note("D", 5, 0.5),
    ],
)
verse.add_track("kick", [Note("C", 2, 1.0)] * 16)
verse.add_track("hat", [Note("F#", 6, 0.5)] * 32)

chorus = Section("chorus", bars=4)
chorus.add_track(
    "bass",
    [
        Note("Eb", 2, 0.5),
        Note("Eb", 3, 0.5),
        Note("Eb", 2, 0.5),
        Note("Eb", 3, 0.5),
        Note("F", 2, 0.5),
        Note("F", 3, 0.5),
        Note("F", 2, 0.5),
        Note("F", 3, 0.5),
        Note("G", 2, 0.5),
        Note("G", 3, 0.5),
        Note("G", 2, 0.5),
        Note("G", 3, 0.5),
        Note("D", 2, 0.5),
        Note("D", 3, 0.5),
        Note("D", 2, 0.5),
        Note("D", 3, 0.5),
    ],
)
chorus.add_track(
    "strings",
    [
        Chord("Eb", "maj", 4, duration=4.0),
        Chord("F", "maj", 4, duration=4.0),
        Chord("G", "min", 4, duration=4.0),
        Chord("D", "dom7", 4, duration=4.0),
    ],
)
chorus.add_track("guitar", verse.tracks["guitar"])
chorus.add_track("kick", [Note("C", 2, 1.0)] * 16)
chorus.add_track("hat", [Note("F#", 6, 0.5)] * 32)

song.arrange(
    [*verse.repeat(2), *chorus.repeat(2), *verse.repeat(2), *chorus.repeat(3)],
    instruments={
        "bass": "bass",
        "strings": "pad",
        "guitar": "pluck",
        "kick": "drums_kick",
        "hat": "drums_hat",
    },
    volumes={"bass": 0.6, "strings": 0.35, "guitar": 0.4, "kick": 0.75, "hat": 0.3},
)

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.55, wet=0.25),
    "guitar": EffectsChain().add(compress, threshold=0.5, ratio=3.0),
}
