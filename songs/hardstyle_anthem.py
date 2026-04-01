"""hardstyle_anthem.py — Hardstyle. E minor, 150 BPM. Defqon.1 energy.

A euphoric hardstyle anthem with the classic reverse bass kick, detuned
supersaw lead, and a massive buildup to the melody drop. Headhunterz /
D-Block & S-te-Fan territory.

Style: Hardstyle, Em, 150 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Section,
    Song,
    compress,
    distortion,
    reverb,
    stereo_width,
)

song = Song(title="Hardstyle Anthem", bpm=150)

r = Note.rest

# ── Sections ──────────────────────────────────────────────────────────────

intro = Section("intro", bars=8)
intro.add_track("kick", [Note("C", 2, 1.0)] * 32)
intro.add_track("bass", [r(32.0)])
intro.add_track("lead", [r(32.0)])
intro.add_track("pad", [Chord("E", "min", 3, duration=32.0)])

buildup = Section("buildup", bars=4)
buildup.add_track("kick", [r(16.0)])
buildup.add_track("bass", [r(16.0)])
buildup.add_track(
    "lead",
    [
        Note("E", 5, 0.5),
        Note("G", 5, 0.5),
        Note("A", 5, 0.5),
        Note("B", 5, 0.5),
        Note("E", 5, 0.5),
        Note("G", 5, 0.5),
        Note("A", 5, 0.5),
        Note("B", 5, 0.5),
        Note("E", 5, 0.25),
        Note("G", 5, 0.25),
        Note("A", 5, 0.25),
        Note("B", 5, 0.25),
        Note("E", 5, 0.25),
        Note("G", 5, 0.25),
        Note("A", 5, 0.25),
        Note("B", 5, 0.25),
        Note("E", 5, 0.125),
        Note("G", 5, 0.125),
        Note("A", 5, 0.125),
        Note("B", 5, 0.125),
        Note("E", 5, 0.125),
        Note("G", 5, 0.125),
        Note("A", 5, 0.125),
        Note("B", 5, 0.125),
        Note("E", 5, 0.125),
        Note("G", 5, 0.125),
        Note("A", 5, 0.125),
        Note("B", 5, 0.125),
        Note("E", 5, 0.125),
        Note("G", 5, 0.125),
        Note("A", 5, 0.125),
        Note("B", 5, 0.125),
        Note("B", 5, 4.0),
    ],
)
buildup.add_track("pad", [Chord("E", "min", 3, duration=16.0)])

drop = Section("drop", bars=8)
drop_kick = []
for _ in range(32):
    drop_kick.extend([Note("C", 2, 1.0)])
drop.add_track("kick", drop_kick)
drop_bass = []
for _ in range(8):
    drop_bass.extend(
        [
            Note("E", 2, 0.5),
            Note("E", 2, 0.5),
            r(0.5),
            Note("E", 2, 0.5),
            Note("E", 2, 0.5),
            Note("B", 1, 0.5),
            Note("E", 2, 0.5),
            r(0.5),
        ]
    )
drop.add_track("bass", drop_bass)
drop_melody = [
    Note("B", 5, 1.0),
    Note("E", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("E", 5, 2.0),
    Note("D", 5, 2.0),
    Note("B", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("E", 5, 2.0),
    r(2.0),
    Note("G", 5, 1.0),
    Note("A", 5, 1.0),
    Note("B", 5, 2.0),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("E", 5, 2.0),
    r(2.0),
]
drop.add_track("lead", drop_melody)
drop.add_track(
    "pad",
    [
        Chord("E", "min", 3, duration=8.0),
        Chord("C", "maj", 3, duration=8.0),
        Chord("G", "maj", 3, duration=8.0),
        Chord("D", "maj", 3, duration=8.0),
    ],
)

outro = Section("outro", bars=4)
outro.add_track("kick", [Note("C", 2, 1.0)] * 16)
outro.add_track("bass", [r(16.0)])
outro.add_track("lead", [r(16.0)])
outro.add_track("pad", [Chord("E", "min", 3, duration=16.0)])

# ── Arrange ───────────────────────────────────────────────────────────────

song.arrange(
    [intro, buildup, drop, buildup, drop, outro],
    instruments={"kick": "drums_kick", "bass": "bass", "lead": "sawtooth", "pad": "pad"},
    volumes={"kick": 0.85, "bass": 0.65, "lead": 0.55, "pad": 0.3},
    pans={"kick": 0.0, "bass": 0.0, "lead": 0.1, "pad": 0.0},
)

song.effects = {
    "kick": EffectsChain()
    .add(distortion, drive=1.8, tone=0.4, wet=0.3)
    .add(compress, threshold=0.4, ratio=6.0),
    "lead": EffectsChain().add(reverb, room_size=0.45, wet=0.2).add(stereo_width, width=1.5),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35).add(stereo_width, width=1.8),
}
