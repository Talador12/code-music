"""drift_phonk.py — Phonk. Fm, 130 BPM. Memphis cowbell, distorted 808.

A dark phonk track with the signature cowbell loop, pitched-down vocal chops
(simulated with organ stabs), distorted 808 bass, and lo-fi film grain.

Style: Phonk, Fm, 130 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    distortion,
    lowpass,
    reverb,
)

song = Song(title="Drift Phonk", bpm=130)

r = Note.rest

# ── Drums — Memphis bounce ───────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="clap", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    # Cowbell-style hi-hat triplet feel
    hat.extend(
        [
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.34),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.34),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.34),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.33),
            Note("F#", 6, 0.34),
        ]
    )

# ── 808 bass — distorted sub ─────────────────────────────────────────────
bass = song.add_track(Track(name="808", instrument="sine", volume=0.7))
bass_line = [
    Note("F", 2, 1.5),
    Note("F", 2, 0.5),
    r(1.0),
    Note("Ab", 2, 1.0),
    Note("F", 2, 1.0),
    Note("Eb", 2, 0.5),
    Note("F", 2, 0.5),
    r(2.0),
]
for _ in range(8):
    bass.extend(bass_line)

# ── Organ stab — pitched-down vocal chop proxy ──────────────────────────
stab = song.add_track(Track(name="vox_chop", instrument="organ", volume=0.35, pan=0.1))
chop = [
    r(2.0),
    Note("Ab", 3, 0.5),
    Note("F", 3, 0.5),
    r(1.0),
    Note("Ab", 3, 0.5),
    r(1.5),
    Note("Eb", 3, 0.5),
    r(1.5),
]
for _ in range(8):
    stab.extend(chop)

# ── Pad — dark atmosphere ────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(8):
    pad.extend(
        [
            Chord("F", "min", 3, duration=4.0),
            Chord("Db", "maj", 3, duration=4.0),
        ]
    )

song.effects = {
    "808": EffectsChain().add(distortion, drive=2.5, tone=0.3, wet=0.4).add(lowpass, cutoff_hz=180),
    "vox_chop": EffectsChain().add(reverb, room_size=0.6, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "clap": EffectsChain().add(compress, threshold=0.4, ratio=5.0),
}
