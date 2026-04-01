"""afro_house.py — Afro house. Dm, 122 BPM. Black Coffee / Keinemusik energy.

Deep, percussive afro house with tribal drum patterns, a hypnotic bass loop,
vocal-ish pad, and a shaker groove. Uses EffectsChain throughout.

Style: Afro house, Dm, 122 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, highpass, reverb

song = Song(title="Afro House", bpm=122)

r = Note.rest

# ── Drums — afro groove ──────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
perc = song.add_track(Track(name="perc", instrument="drums_snare", volume=0.4))
hat = song.add_track(Track(name="shaker", instrument="drums_hat", volume=0.3))

for _ in range(24):
    kick.extend([Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5), r(1.0), Note("C", 2, 1.0)])
    perc.extend(
        [
            r(0.75),
            Note("E", 4, 0.25),
            r(0.5),
            Note("E", 4, 0.25),
            Note("E", 4, 0.25),
            r(0.5),
            Note("E", 4, 0.25),
            r(0.5),
            Note("E", 4, 0.25),
            r(0.25),
            Note("E", 4, 0.25),
        ]
    )
    hat.extend([Note("F#", 6, 0.25)] * 16)

# ── Bass — hypnotic one-bar loop ─────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_bar = [
    Note("D", 2, 0.5),
    r(0.5),
    Note("D", 2, 0.5),
    Note("F", 2, 0.5),
    Note("A", 2, 0.5),
    Note("F", 2, 0.5),
    Note("D", 2, 0.5),
    r(0.5),
]
for _ in range(24):
    bass.extend(bass_bar)

# ── Pad — vocal-ish wash ─────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
for _ in range(12):
    pad.extend(
        [
            Chord("D", "min7", 3, duration=4.0),
            Chord("A", "min", 3, duration=4.0),
        ]
    )

# ── Lead — sparse tribal melody ──────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="pluck", volume=0.4, pan=0.2))
for _ in range(6):
    lead.extend(
        [
            r(4.0),
            Note("D", 5, 0.5),
            Note("F", 5, 0.5),
            Note("A", 5, 0.5),
            r(0.5),
            Note("G", 5, 0.5),
            Note("F", 5, 0.5),
            Note("D", 5, 1.0),
            r(4.0),
            Note("A", 5, 0.5),
            Note("G", 5, 0.5),
            Note("F", 5, 0.5),
            Note("D", 5, 0.5),
            Note("C", 5, 1.0),
            r(1.0),
        ]
    )

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "lead": EffectsChain()
    .add(delay, delay_ms=245, feedback=0.2, wet=0.15)
    .add(highpass, cutoff_hz=500),
}
