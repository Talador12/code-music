"""neuromancer.py — Neurofunk DnB. 174 BPM, Fm. Dark, technical, cyberpunk.

Neurofunk is DnB's most technical subgenre: complex modulated bass
(wobble + pitch glide + distortion), polyrhythmic percussion, dark
atmospheric pads, no melody — just texture and aggression. Ed Rush,
Optical, Konflict, Noisia are the reference points.
"""

from code_music import (
    QUARTER,
    SIXTEENTH,
    Chord,
    Note,
    Song,
    Track,
    compress,
    distortion,
    highpass,
    lfo_filter,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Neuromancer", bpm=174)

BAR = 4.0
r = Note.rest


def b(n):
    return [r(BAR)] * n


# ── DnB kick — half-time feel ─────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick_pat = [
    Note("C", 2, 1.0),
    r(0.5),
    Note("C", 2, 0.5),
    r(1.0),
    Note("C", 2, 0.5),
    r(0.5),
]
kick.extend(b(4))
kick.extend(kick_pat * 28)
kick.extend(b(4))

# ── Snare — beat 3, military tight ───────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.92))
snare.extend(b(4))
snare.extend([r(2.0), Note("D", 3, 1.0, velocity=0.95), r(1.0)] * 28)
snare.extend(b(4))

# ── Neurofunk hat pattern — irregular, polyrhythmic ──────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))
hat.extend(b(4))
# Neurofunk hat: 16ths with accents creating cross-rhythm
neuro_hat = [
    Note("F", 5, SIXTEENTH, velocity=0.7),
    Note("F", 5, SIXTEENTH, velocity=0.4),
    Note("F", 5, SIXTEENTH, velocity=0.8),
    Note("F", 5, SIXTEENTH, velocity=0.35),
    Note("F", 5, SIXTEENTH, velocity=0.6),
    Note("F", 5, SIXTEENTH, velocity=0.9),
    Note("F", 5, SIXTEENTH, velocity=0.4),
    Note("F", 5, SIXTEENTH, velocity=0.55),
    Note("F", 5, SIXTEENTH, velocity=0.7),
    Note("F", 5, SIXTEENTH, velocity=0.3),
    Note("F", 5, SIXTEENTH, velocity=0.85),
    Note("F", 5, SIXTEENTH, velocity=0.45),
    Note("F", 5, SIXTEENTH, velocity=0.6),
    Note("F", 5, SIXTEENTH, velocity=0.4),
    Note("F", 5, SIXTEENTH, velocity=0.75),
    Note("F", 5, SIXTEENTH, velocity=0.5),
]
hat.extend(neuro_hat * 28)
hat.extend(b(4))

# ── Wobble bass — the neurofunk centerpiece ───────────────────────────────
wobble = song.add_track(Track(name="wobble", instrument="wobble", volume=0.88))
wobble.extend(b(4))
bass_seq = [
    Note("F", 2, 1.0, velocity=0.95),
    Note("F", 2, 0.5, velocity=0.85),
    Note("G#", 2, 0.5, velocity=0.9),
    Note("F", 2, 0.5, velocity=0.88),
    Note("D#", 2, 0.5, velocity=0.85),
    Note("C", 2, 1.0, velocity=0.9),
]
wobble.extend(bass_seq * 14)
wobble.extend(b(4))

# ── Sub bass ──────────────────────────────────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.82))
sub.extend(b(4))
sub.extend([Note("F", 1, BAR, velocity=0.75)] * 28)
sub.extend(b(4))

# ── Dark atmospheric pads — no melody, just texture ──────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
pad.extend(b(8))
for ch, sh in [("F", "min7"), ("C#", "maj7"), ("G#", "maj7"), ("D#", "dom7")] * 5:
    pad.add(Chord(ch, sh, 2, duration=BAR, velocity=0.3))
pad.extend(b(4))

# ── Metallic stabs — industrial punctuation ───────────────────────────────
stab = song.add_track(Track(name="stab", instrument="stab", volume=0.55, pan=0.3))
stab.extend(b(8))
stab_pat = [
    Chord("F", "min", 3, duration=SIXTEENTH, velocity=0.85),
    r(BAR - SIXTEENTH),
    r(BAR * 2),
    Chord("C#", "maj", 3, duration=SIXTEENTH, velocity=0.8),
    r(QUARTER - SIXTEENTH),
    Chord("F", "min", 3, duration=SIXTEENTH, velocity=0.88),
    r(BAR - QUARTER),
    r(BAR),
]
stab.extend(stab_pat * 6)
stab.extend(b(4))

song._effects = {
    "wobble": lambda s, sr: distortion(
        compress(s, sr, threshold=0.45, ratio=5.0, makeup_gain=1.2),
        drive=3.0,
        tone=0.65,
        wet=0.6,
    ),
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=85.0),
    "pad": lambda s, sr: stereo_width(
        lfo_filter(
            reverb(s, sr, room_size=0.75, wet=0.35),
            sr,
            rate_hz=0.08,
            min_cutoff=200.0,
            max_cutoff=5000.0,
        ),
        width=1.85,
    ),
    "stab": lambda s, sr: distortion(s, drive=2.0, wet=0.5),
    "hat": lambda s, sr: highpass(s, sr, cutoff_hz=6000.0),
}
