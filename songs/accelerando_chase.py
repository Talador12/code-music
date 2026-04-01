"""accelerando_chase.py — Action score that speeds up via bpm_map.

Starts at 90 BPM and accelerates to 160 BPM over 8 bars, like a
film chase scene building tension. Then the last 4 bars hold at 160.

Style: Cinematic action, Cm, 90→160 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    bpm_ramp,
    compress,
    reverb,
)

song = Song(title="Accelerando Chase", bpm=90)

r = Note.rest

# 12 bars: 8 accelerating + 4 at max speed
BARS = 12

# Strings — tension chords
strings = song.add_track(Track(name="strings", instrument="pad", volume=0.4))
for _ in range(6):
    strings.extend(
        [
            Chord("C", "min", 3, duration=4.0),
            Chord("Ab", "maj", 3, duration=4.0),
        ]
    )

# Brass stabs
brass = song.add_track(Track(name="brass", instrument="sawtooth", volume=0.5, pan=0.15))
stab = [
    Note("C", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("G", 5, 0.5),
    r(0.5),
    Note("Ab", 5, 0.5),
    Note("G", 5, 0.5),
    Note("Eb", 5, 1.0),
]
for _ in range(BARS):
    brass.extend(stab)

# Bass — driving ostinato
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_riff = [
    Note("C", 2, 0.5),
    Note("C", 2, 0.5),
    Note("Eb", 2, 0.5),
    Note("G", 2, 0.5),
    Note("Ab", 2, 0.5),
    Note("G", 2, 0.5),
    Note("Eb", 2, 0.5),
    Note("C", 2, 0.5),
]
for _ in range(BARS):
    bass.extend(bass_riff)

# Drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(BARS):
    kick.extend([Note("C", 2, 1.0)] * 4)
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

# THE KEY FEATURE: accelerate from 90 → 160 over first 8 bars, hold for last 4
accel = bpm_ramp(90, 160, bars=8)
hold = [160.0] * 16  # 4 bars at 160
song.bpm_map = accel + hold

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.65, wet=0.3),
    "brass": EffectsChain()
    .add(reverb, room_size=0.4, wet=0.15)
    .add(compress, threshold=0.5, ratio=3.0),
}
