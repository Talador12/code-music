"""berlin_four.py — Techno. 138 BPM, Fm, industrial, no melody required.

Structure:
  Bars 1-8:   Intro — kick + metallic percussion only
  Bars 9-16:  Layer 1 — acid bass enters
  Bars 17-24: Layer 2 — industrial stab, hats thicken
  Bars 25-40: Peak — everything, relentless
  Bars 41-48: Break — kick only, tension
  Bars 49-64: Second peak — full with additional texture
  Bars 65-72: Outro — elements drop off one by one
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    distortion,
    highpass,
    lfo_filter,
    lowpass,
)

song = Song(title="Concrete", bpm=138)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Kick — never stops, never varies. That's the point. ──────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * (72 * 4))

# ── Clap / snare on 2 & 4 ────────────────────────────────────────────────
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.72))
clap.extend(bars(8))  # intro: no clap
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 64)

# ── Hi-hat — driving 16ths from bar 17 ───────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))
hat.extend(bars(16))
hat.extend([Note("F", 5, 0.25)] * (56 * 16))

# ── Ride — offbeats from bar 25 ──────────────────────────────────────────
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.38))
ride.extend(bars(24))
ride.extend([r(0.5), Note("F", 5, 0.5)] * (48 * 4))

# ── Acid bass — that squelching 303 filter ────────────────────────────────
acid = song.add_track(Track(name="acid", instrument="acid", volume=0.75))
acid.extend(bars(8))

acid_line = [
    Note("F", 2, 0.25),
    Note("F", 2, 0.25),
    Note("C", 3, 0.25),
    Note("F", 2, 0.25),
    Note("G#", 2, 0.25),
    Note("F", 2, 0.25),
    Note("G", 2, 0.25),
    Note("F", 2, 0.25),
    Note("F", 2, 0.25),
    Note("A#", 2, 0.25),
    Note("G#", 2, 0.25),
    Note("G", 2, 0.25),
    Note("F", 2, 0.5),
    Note("D#", 2, 0.5),
    Note("F", 2, 0.25),
    Note("F", 2, 0.25),
    Note("G", 2, 0.25),
    Note("G#", 2, 0.25),
    Note("A#", 2, 0.5),
    Note("G#", 2, 0.25),
    Note("G", 2, 0.25),
    Note("F", 2, 2.0),
]
acid.extend(acid_line * 16)

# ── Industrial stab — harsh chord hits ───────────────────────────────────
stab = song.add_track(Track(name="stab", instrument="stab", volume=0.65, pan=-0.2))
stab.extend(bars(16))
stab_pat = [
    Chord("F", "min", 3, duration=0.25, velocity=0.9),
    r(0.75),
    r(BAR - 1.0),
]
stab.extend(stab_pat * 56)

# ── Sub bass hit — the low end weight ────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.8))
sub.extend(bars(24))
sub.extend([Note("F", 1, BAR, velocity=0.75)] * 40)
sub.extend(bars(8))

# ── Metallic texture — the industrial shimmer ─────────────────────────────
metal = song.add_track(Track(name="metal", instrument="drums_hat", volume=0.28, pan=0.4))
metal.extend(bars(1))
# Polyrhythmic 16th pattern against the main grid
poly = [Note("F", 6, 0.375)] * 2 + [r(0.25)]  # 1.0 beat cycle
metal.extend(poly * (71 * 3))

song.effects = {
    "acid": lambda s, sr: lfo_filter(s, sr, rate_hz=0.25, min_cutoff=200.0, max_cutoff=6000.0),
    "stab": lambda s, sr: distortion(s, drive=2.5, tone=0.7, wet=0.5),
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=90.0),
    "metal": lambda s, sr: highpass(s, sr, cutoff_hz=8000.0),
}
