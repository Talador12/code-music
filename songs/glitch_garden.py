"""glitch_garden.py — IDM / glitch. Cm, 138 BPM. Aphex Twin / Autechre adjacent.

IDM (Intelligent Dance Music) is what happens when electronic musicians
decide the beat doesn't have to be for dancing. Irregular rhythms,
granular textures, unexpected pitch shifts, sounds that shouldn't
work together but do. This uses the granular and bitcrush effects.
"""

from code_music import (
    EIGHTH,
    QUARTER,
    SIXTEENTH,
    Chord,
    Note,
    Song,
    Track,
    bitcrush,
    compress,
    delay,
    generate_melody,
    granular,
    reverb,
    ring_mod,
    stereo_width,
)

song = Song(title="Glitch Garden", bpm=138)

BAR = 4.0
r = Note.rest
E8 = EIGHTH

# ── Kick — mostly regular but with gaps (IDM = imperfect 4/4) ─────────────
kick = song.add_track(
    Track(name="kick", instrument="drums_kick", volume=0.9, density=0.85, density_seed=42)
)
kick.extend([Note("C", 2, 1.0)] * (16 * 4))

# ── Snare — irregular, density-controlled ─────────────────────────────────
snare = song.add_track(
    Track(name="snare", instrument="drums_snare", volume=0.72, density=0.6, density_seed=99)
)
for _ in range(16):
    snare.extend(
        [r(E8), Note("D", 3, E8), r(QUARTER), Note("D", 3, E8), r(E8), Note("D", 3, E8), r(E8)]
    )

# ── Hi-hat — 32nd note stutters ───────────────────────────────────────────
hat = song.add_track(
    Track(name="hat", instrument="drums_hat", volume=0.4, density=0.7, density_seed=7)
)
hat.extend([Note("F", 5, SIXTEENTH)] * (16 * 16))

# ── Glitch bass — bitcrushed, irregular ───────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="acid", volume=0.78))
bass_pat = [
    Note("C", 2, E8),
    Note("C", 2, E8),
    r(E8),
    Note("D#", 2, E8),
    Note("G", 2, QUARTER),
    r(E8),
    Note("C", 2, E8),
    Note("F", 2, E8),
    r(E8),
    Note("C", 2, QUARTER),
    r(QUARTER),
]
bass.extend(bass_pat * 8)

# ── Generative melody — different each render ─────────────────────────────
mel = song.add_track(Track(name="mel", instrument="fm_bell", volume=0.52, pan=0.2))
mel.extend([r(BAR)] * 4)
gen = generate_melody("C", scale_mode="chromatic", octave=5, bars=12, density=0.45, seed=2187)
mel.extend(gen)

# ── Pad — granular texture ─────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35))
for ch, sh in [("C", "min7"), ("G#", "maj7"), ("D#", "maj"), ("A#", "dom7")] * 4:
    pad.add(Chord(ch, sh, 3, duration=BAR, velocity=0.4))

song._effects = {
    "bass": lambda s, sr: bitcrush(
        compress(s, sr, threshold=0.45, ratio=5.0, makeup_gain=1.2),
        sr,
        bit_depth=10,
        downsample=2,
        wet=0.5,
    ),
    "mel": lambda s, sr: granular(
        delay(s, sr, delay_ms=181.0, feedback=0.35, wet=0.25),
        sr,
        grain_size_ms=40.0,
        scatter=0.4,
        wet=0.5,
    ),
    "pad": lambda s, sr: stereo_width(
        granular(
            reverb(s, sr, room_size=0.7, wet=0.35),
            sr,
            grain_size_ms=80.0,
            scatter=0.3,
            pitch_spread=0.3,
            wet=0.6,
        ),
        width=1.9,
    ),
    "hat": lambda s, sr: ring_mod(s, sr, freq_hz=6000.0, wet=0.2),
}
