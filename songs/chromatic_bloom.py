"""chromatic_bloom.py — Synth-pop / K-pop adjacent. C# major, 120 BPM.

Bright, punchy synth production. Four-chord major progression, clean
808 kick, arpeggiated supersaw stabs, a chorus that refuses to be
subtle. The kind of track that makes people crane their necks looking
for the source at a coffee shop.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    arp,
    chord_prog,
    compress,
    crescendo,
    delay,
    eq,
    reverb,
    stereo_width,
)

song = Song(title="Chromatic Bloom", bpm=120)

BAR = 4.0
r = Note.rest

PROG = chord_prog(
    ["C#", "A#", "F#", "G#"], ["maj", "maj", "maj", "maj"], octave=3, duration=BAR, velocity=0.62
)

# ── Drums ─────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.98))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.75))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, EIGHTH)] * 8)
    clap.extend([r(2.0), Note("D", 3, EIGHTH), r(EIGHTH), r(2.0 - EIGHTH)])

# ── Synth pads ─────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.45))
for _ in range(4):
    pad.extend(PROG)
pad.extend(crescendo(PROG * 8, start_vel=0.5, end_vel=0.82))
for _ in range(4):
    pad.extend(PROG)

# ── Arpeggiated stab ──────────────────────────────────────────────────────
stab = song.add_track(Track(name="stab", instrument="pluck", volume=0.50, pan=0.2))
stab.extend([r(BAR)] * 4)
for _ in range(12):
    for ch in PROG:
        stab.extend(arp(ch, pattern="up", rate=EIGHTH, octaves=2))
stab.extend([r(BAR)] * 4)

# ── Lead melody ────────────────────────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="sine", volume=0.65, pan=-0.1))
lead.extend([r(BAR)] * 8)
mel = crescendo(
    [
        Note("C#", 5, QUARTER),
        r(EIGHTH),
        Note("D#", 5, EIGHTH),
        Note("F#", 5, HALF),
        Note("G#", 5, QUARTER),
        Note("F#", 5, QUARTER),
        r(HALF),
        Note("F", 5, QUARTER),
        Note("D#", 5, QUARTER),
        Note("C#", 5, HALF),
        Note("A#", 4, WHOLE),
        r(QUARTER),
        Note("C#", 5, QUARTER),
        Note("D#", 5, QUARTER),
        Note("F#", 5, QUARTER),
        Note("A#", 5, HALF),
        Note("G#", 5, HALF),
        Note("F#", 5, WHOLE),
        r(BAR),
    ],
    start_vel=0.6,
    end_vel=0.95,
)
lead.extend(mel * 4)
lead.extend([r(BAR)] * 4)

# ── Bass ───────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.78))
for _ in range(16):
    for ch in PROG:
        bass.add(Note(ch.root, ch.octave - 1, BAR * 0.5, velocity=0.82))
        bass.add(r(BAR * 0.5))

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.4, wet=0.15), width=1.7),
    "lead": lambda s, sr: eq(
        delay(s, sr, delay_ms=250.0, feedback=0.25, wet=0.15),
        sr,
        bands=[(3000, +2.5, 1.2), (8000, +2.0, 0.8)],
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
