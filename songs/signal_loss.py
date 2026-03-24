"""signal_loss.py — Harder DnB. 174 BPM, Cm. Pendulum / Chase & Status energy.

Where liquid_dnb.py is warm and jazzy, this one is distorted and aggressive.
Reese bass run through distortion. Snare at 174 BPM that hits like a piston.
The amen break aesthetic without sampling — just drum programming that implies
the same energy. Synth stabs. Tension without release.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    compress,
    distortion,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Signal Loss", bpm=174)

BAR = 4.0
r = Note.rest


def bars_r(n, bar=4.0):
    return [r(bar)] * n


# ── DnB kick — 1 and beat 2.5 (the Amen feel) ────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
dnb_kick = [
    Note("C", 2, 1.0),
    r(0.5),
    Note("C", 2, 0.5),  # beat 1, beat 2.5
    r(1.0),
    Note("C", 2, 0.5),
    r(0.5),  # beat 4 ghost
]
kick.extend(bars_r(4, BAR))
kick.extend(dnb_kick * 28)
kick.extend(bars_r(4, BAR))


# ── Snare — beat 3 only (heavy DnB backbeat) ──────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.92))
snare.extend(bars_r(4))
snare.extend([r(2.0), Note("D", 3, 1.0, velocity=0.95), r(1.0)] * 28)
snare.extend(bars_r(4))

# ── Hi-hats — 8th notes with 16th rolls every 2 bars ─────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.48))
hat.extend(bars_r(4))
hat_std = [Note("F", 5, EIGHTH)] * 8
hat_roll = [Note("F", 5, EIGHTH / 2)] * 4 + [Note("F", 5, EIGHTH)] * 6
for i in range(28):
    hat.extend(hat_roll if i % 2 == 1 else hat_std)
hat.extend(bars_r(4))

# ── Reese bass — distorted, chord tones ──────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="reese_bass", volume=0.85))
bass.extend(bars_r(4))
bass_line = [
    Note("C", 2, 2.0, velocity=0.95),
    Note("D#", 2, 1.0, velocity=0.85),
    Note("G", 2, 1.0, velocity=0.9),
    Note("A#", 1, 2.0, velocity=0.9),
    Note("G", 1, 2.0, velocity=0.88),
    Note("G#", 1, 2.0, velocity=0.9),
    Note("A#", 1, 1.0, velocity=0.85),
    Note("C", 2, 1.0, velocity=0.88),
    Note("F", 2, 4.0, velocity=0.92),
]
bass.extend(bass_line * 4)
bass.extend(bass_line * 3)
bass.extend(bars_r(4))

# ── Synth stabs — brutal short hits ───────────────────────────────────────
stab = song.add_track(Track(name="stab", instrument="stab", volume=0.72, pan=-0.2))
stab.extend(bars_r(8))
stab_pat = [
    Chord("C", "min", 3, duration=EIGHTH, velocity=0.9),
    r(EIGHTH),
    r(QUARTER),
    r(HALF),
    r(QUARTER),
    Chord("G#", "maj", 3, duration=EIGHTH, velocity=0.85),
    r(EIGHTH),
    r(QUARTER),
    Chord("A#", "maj", 3, duration=EIGHTH, velocity=0.88),
    r(EIGHTH),
    r(HALF),
]
stab.extend(stab_pat * 18)
stab.extend(bars_r(4))

# ── Atmospheric pad underneath ────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.28, pan=0.3))
pad.extend(bars_r(8))
for ch, sh in [("C", "min7"), ("G#", "maj7"), ("A#", "dom7"), ("F", "min7")] * 5:
    pad.add(Chord(ch, sh, 2, duration=BAR, velocity=0.35))
pad.extend(bars_r(4))

# ── Sub bass hit ─────────────────────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.82))
sub.extend(bars_r(4))
sub.extend([Note("C", 1, BAR, velocity=0.75)] * 28)
sub.extend(bars_r(4))

song._effects = {
    "bass": lambda s, sr: distortion(
        compress(s, sr, threshold=0.45, ratio=6.0, makeup_gain=1.2),
        drive=2.8,
        tone=0.6,
        wet=0.55,
    ),
    "stab": lambda s, sr: distortion(s, drive=2.0, tone=0.7, wet=0.4),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.35), width=1.8),
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=90.0),
}
