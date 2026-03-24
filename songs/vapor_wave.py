"""vapor_wave.py — Vaporwave / aesthetic. Fm, 80 BPM. Slowed, pitched down, nostalgic.

Vaporwave is music processed to sound like it's decaying — slowed down,
pitched down, compressed to cassette quality. Corporate jazz and elevator
music run through bitcrusher and time-stretch until it sounds like a
memory of a mall that no longer exists. This track uses bitcrusher,
tape saturation, and a heavily reverbed Rhodes.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    arp,
    bitcrush,
    delay,
    lowpass,
    reverb,
    stereo_width,
    tape_sat,
)

song = Song(title="Vapor Wave", bpm=80)

BAR = 4.0
SWING = 0.48
r = Note.rest

# ── Pitched-down Rhodes pad ───────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="rhodes", volume=0.68, swing=SWING))
prog = [
    Chord("F", "min7", 3, duration=BAR * 2, velocity=0.55),
    Chord("C#", "maj7", 3, duration=BAR * 2, velocity=0.52),
    Chord("G#", "maj7", 3, duration=BAR * 2, velocity=0.55),
    Chord("D#", "dom7", 3, duration=BAR * 2, velocity=0.52),
]
for _ in range(4):
    pad.extend(prog)

# ── Arpeggio — very slow, wide ────────────────────────────────────────────
arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.38, pan=0.2))
for _ in range(4):
    for ch, sh in [("F", "min7"), ("C#", "maj7"), ("G#", "maj7"), ("D#", "dom7")]:
        arp_tr.extend(arp(Chord(ch, sh, 4), pattern="up_down", rate=QUARTER, octaves=2))

# ── Bass — very sparse ────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.72))
for _ in range(4):
    bass.extend(
        [
            Note("F", 2, WHOLE, velocity=0.65),
            Note("C#", 2, WHOLE, velocity=0.62),
            Note("G#", 1, WHOLE, velocity=0.65),
            Note("D#", 2, WHOLE, velocity=0.62),
        ]
    )

# ── Melody — floating, nostalgic ─────────────────────────────────────────
mel = song.add_track(
    Track(name="melody", instrument="wurlitzer", volume=0.55, pan=-0.1, swing=SWING)
)
mel.extend([r(BAR)] * 8)
melody = [
    Note("F", 4, HALF),
    r(QUARTER),
    Note("G#", 4, QUARTER),
    Note("A#", 4, HALF),
    r(HALF),
    Note("G", 4, QUARTER),
    Note("F", 4, QUARTER),
    r(HALF),
    Note("D#", 4, WHOLE),
    r(HALF),
    Note("C", 5, HALF),
    r(QUARTER),
    Note("A#", 4, QUARTER),
    Note("G#", 4, HALF),
    r(HALF),
    Note("F", 4, WHOLE * 2),
]
mel.extend(melody * 2)

# ── Background texture — very quiet drum machine ──────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.18))
hat.extend([Note("F", 5, EIGHTH, velocity=0.2)] * (32 * 8))

song._effects = {
    "pad": lambda s, sr: bitcrush(
        tape_sat(reverb(s, sr, room_size=0.7, wet=0.35), sr, drive=1.5, warmth=0.6, wet=0.5),
        sr,
        bit_depth=10,
        downsample=2,
        wet=0.4,
    ),
    "arp": lambda s, sr: delay(
        reverb(s, sr, room_size=0.65, wet=0.3), sr, delay_ms=750.0, feedback=0.4, wet=0.3
    ),
    "melody": lambda s, sr: stereo_width(
        tape_sat(reverb(s, sr, room_size=0.75, wet=0.4), sr, drive=1.8, warmth=0.5, wet=0.4),
        width=1.6,
    ),
    "bass": lambda s, sr: lowpass(s, sr, cutoff_hz=180.0),
}
