"""synthwave_drive.py — Synthwave. Am, 108 BPM. Outrun neon sunset.

80s-inspired synthwave with arpeggiated pads, punchy sidechained kick,
and a soaring lead. Uses Track.transpose for the modulating bridge.

Style: Synthwave, Am, 108 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, delay, reverb, stereo_width

song = Song(title="Synthwave Drive", bpm=108)

r = Note.rest

verse = Section("verse", bars=4)
verse.add_track(
    "pad",
    [
        Chord("A", "min", 3, duration=4.0),
        Chord("F", "maj", 3, duration=4.0),
        Chord("C", "maj", 3, duration=4.0),
        Chord("G", "maj", 3, duration=4.0),
    ],
)
verse.add_track(
    "arp",
    [
        Note("A", 4, 0.25),
        Note("C", 5, 0.25),
        Note("E", 5, 0.25),
        Note("A", 5, 0.25),
    ]
    * 4
    + [
        Note("F", 4, 0.25),
        Note("A", 4, 0.25),
        Note("C", 5, 0.25),
        Note("F", 5, 0.25),
    ]
    * 4
    + [
        Note("C", 4, 0.25),
        Note("E", 4, 0.25),
        Note("G", 4, 0.25),
        Note("C", 5, 0.25),
    ]
    * 4
    + [
        Note("G", 4, 0.25),
        Note("B", 4, 0.25),
        Note("D", 5, 0.25),
        Note("G", 5, 0.25),
    ]
    * 4,
)
verse.add_track(
    "bass",
    [
        Note("A", 2, 2.0),
        Note("A", 2, 1.0),
        Note("E", 2, 1.0),
        Note("F", 2, 2.0),
        Note("F", 2, 1.0),
        Note("C", 2, 1.0),
        Note("C", 2, 2.0),
        Note("C", 2, 1.0),
        Note("G", 2, 1.0),
        Note("G", 2, 2.0),
        Note("G", 2, 1.0),
        Note("D", 2, 1.0),
    ],
)
verse.add_track("kick", [Note("C", 2, 1.0)] * 16)
verse.add_track("snare", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
verse.add_track(
    "lead",
    [
        Note("E", 5, 1.0),
        Note("A", 5, 0.5),
        Note("G", 5, 0.5),
        Note("F", 5, 1.0),
        Note("E", 5, 1.0),
        Note("C", 5, 0.5),
        Note("D", 5, 0.5),
        Note("E", 5, 1.0),
        Note("D", 5, 1.0),
        Note("C", 5, 1.0),
        Note("B", 4, 0.5),
        Note("A", 4, 0.5),
        Note("G", 4, 1.0),
        Note("A", 4, 1.0),
        Note("B", 4, 1.0),
        Note("C", 5, 2.0),
        r(2.0),
    ],
)

bridge = Section("bridge", bars=4)
bridge.add_track(
    "pad",
    [
        Chord("D", "min", 3, duration=4.0),
        Chord("Bb", "maj", 3, duration=4.0),
        Chord("F", "maj", 3, duration=4.0),
        Chord("C", "maj", 3, duration=4.0),
    ],
)
bridge.add_track("arp", [r(16.0)])
bridge.add_track(
    "bass", [Note("D", 2, 4.0), Note("Bb", 1, 4.0), Note("F", 2, 4.0), Note("C", 2, 4.0)]
)
bridge.add_track("kick", [Note("C", 2, 1.0)] * 16)
bridge.add_track("snare", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
bridge.add_track(
    "lead", [Note("D", 5, 4.0), Note("Bb", 4, 4.0), Note("F", 5, 4.0), Note("C", 5, 4.0)]
)

song.arrange(
    [*verse.repeat(2), bridge, *verse.repeat(2)],
    instruments={
        "pad": "pad",
        "arp": "triangle",
        "bass": "bass",
        "lead": "sawtooth",
        "kick": "drums_kick",
        "snare": "drums_snare",
    },
    volumes={"pad": 0.3, "arp": 0.35, "bass": 0.6, "lead": 0.5, "kick": 0.75, "snare": 0.5},
    pans={"pad": 0.0, "arp": 0.25, "lead": -0.15},
)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35).add(stereo_width, width=1.6),
    "arp": EffectsChain().add(delay, delay_ms=277, feedback=0.3, wet=0.2),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
