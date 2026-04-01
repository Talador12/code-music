"""cold_wave.py — Post-punk / darkwave. Dm, 130 BPM. Joy Division meets Depeche Mode.

Driving bass line, minimal guitar, synth pad, drum machine. The bass
carries the melody — Peter Hook style (New Order/Joy Division). Everything
is slightly cold. The reverb is large but not warm. The snare is sharp.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    distortion,
    reverb,
    slapback,
)

song = Song(title="Cold Wave", bpm=130, key_sig="D")

BAR = 4.0
r = Note.rest
E8 = EIGHTH

# ── Driving bass — the melody, Peter Hook style ───────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.82))
hook = [
    Note("D", 3, E8),
    Note("D", 3, E8),
    Note("F", 3, E8),
    Note("A", 3, E8),
    Note("G", 3, E8),
    Note("F", 3, E8),
    Note("D", 3, E8),
    Note("C", 3, E8),
    Note("A#", 2, E8),
    Note("C", 3, E8),
    Note("D", 3, E8),
    Note("F", 3, E8),
    Note("D", 3, QUARTER),
    r(QUARTER),
]
bass.extend(hook * 8)

# ── Drum machine — tight, mechanical ──────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.92))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, E8)] * 8)

# ── Guitar — sparse, angular, slightly distorted ──────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.48, pan=-0.25))
gtr.extend([r(BAR)] * 4)
stab = [
    r(E8),
    Chord("D", "min", 4, duration=E8, velocity=0.7),
    r(QUARTER),
    r(E8),
    Chord("D", "min", 4, duration=E8, velocity=0.65),
    r(QUARTER),
    r(HALF),
]
gtr.extend(stab * 12)

# ── Synth pad — cold, wide ────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=0.2))
for ch, sh in [("D", "min7"), ("A#", "maj7"), ("F", "maj"), ("C", "dom7")] * 4:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.4))

song.effects = {
    "bass": lambda s, sr: chorus(
        compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15), sr, rate_hz=0.4, wet=0.12
    ),
    "guitar": lambda s, sr: slapback(
        distortion(s, drive=1.5, tone=0.5, wet=0.25), sr, delay_ms=110.0, level=0.4
    ),
    "pad": lambda s, sr: reverb(s, sr, room_size=0.8, wet=0.4),
    "snare": lambda s, sr: reverb(s, sr, room_size=0.65, wet=0.3),
}
