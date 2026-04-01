"""raga_dawn.py — Indian classical fusion. D Phrygian, 90 BPM. Raga Bhairav feel.

A meditative raga-inspired piece with sitar-like lead (sawtooth), tabla-style
percussion, and a tanpura drone. Uses Section.repeat() for the alap → gat cycle.

Style: Indian classical fusion, D Phrygian, 90 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, reverb, stereo_width

song = Song(title="Raga Dawn", bpm=90)

r = Note.rest

# ── Sections ──────────────────────────────────────────────────────────────

alap = Section("alap", bars=4)
alap.add_track(
    "sitar",
    [
        Note("D", 4, 2.0),
        Note("Eb", 4, 1.0),
        Note("D", 4, 1.0),
        Note("A", 3, 2.0),
        Note("D", 4, 2.0),
        Note("F", 4, 1.5),
        Note("Eb", 4, 0.5),
        Note("D", 4, 1.0),
        Note("C", 4, 1.0),
        Note("D", 4, 2.0),
        r(2.0),
    ],
)
alap.add_track("drone", [Chord("D", "min", 2, duration=16.0)])
alap.add_track("tabla", [r(16.0)])

gat = Section("gat", bars=4)
gat.add_track(
    "sitar",
    [
        Note("D", 5, 0.5),
        Note("Eb", 5, 0.5),
        Note("F", 5, 0.5),
        Note("G", 5, 0.5),
        Note("A", 5, 1.0),
        Note("G", 5, 0.5),
        Note("F", 5, 0.5),
        Note("Eb", 5, 0.5),
        Note("D", 5, 0.5),
        Note("C", 5, 0.5),
        Note("D", 5, 0.5),
        Note("A", 4, 1.0),
        Note("D", 5, 1.0),
        Note("F", 5, 0.5),
        Note("G", 5, 0.5),
        Note("A", 5, 0.5),
        Note("Bb", 5, 0.5),
        Note("A", 5, 1.0),
        Note("G", 5, 0.5),
        Note("F", 5, 0.5),
        Note("Eb", 5, 1.0),
        Note("D", 5, 1.0),
    ],
)
gat.add_track("drone", [Chord("D", "min", 2, duration=16.0)])
tabla_pattern = [
    Note("C", 2, 0.5),
    r(0.5),
    Note("C", 2, 0.25),
    Note("C", 2, 0.25),
    r(0.5),
    Note("C", 2, 0.5),
    r(0.5),
    Note("C", 2, 0.5),
    r(0.5),
]
gat.add_track("tabla", tabla_pattern * 4)

jhala = Section("jhala", bars=4)
jhala.add_track(
    "sitar",
    [
        Note("D", 5, 0.25),
        Note("A", 5, 0.25),
        Note("D", 5, 0.25),
        Note("A", 5, 0.25),
        Note("Eb", 5, 0.25),
        Note("A", 5, 0.25),
        Note("D", 5, 0.25),
        Note("A", 5, 0.25),
    ]
    * 4,
)
jhala.add_track("drone", [Chord("D", "min", 2, duration=16.0)])
fast_tabla = [Note("C", 2, 0.25), Note("C", 2, 0.25), r(0.25), Note("C", 2, 0.25)] * 4
jhala.add_track("tabla", fast_tabla * 4)

coda = Section("coda", bars=4)
coda.add_track("sitar", [Note("D", 4, 4.0), r(12.0)])
coda.add_track("drone", [Chord("D", "min", 2, duration=16.0)])
coda.add_track("tabla", [r(16.0)])

# ── Arrange: alap → gat ×3 → jhala ×2 → coda ────────────────────────────

song.arrange(
    [*alap.repeat(2), *gat.repeat(3), *jhala.repeat(2), coda],
    instruments={"sitar": "sawtooth", "drone": "pad", "tabla": "drums_kick"},
    volumes={"sitar": 0.55, "drone": 0.3, "tabla": 0.5},
    pans={"sitar": 0.15, "drone": 0.0, "tabla": -0.1},
)

song.effects = {
    "sitar": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "drone": EffectsChain().add(reverb, room_size=0.8, wet=0.4).add(stereo_width, width=1.6),
}
