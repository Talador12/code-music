"""Ska showcase - all three waves plus the skank engine, horn stabs, and walking bass.

The offbeat owns this track. Every upstroke is a declaration of intent.
Prince Buster into The Specials into Reel Big Fish in one continuous groove.
"""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    scale,
    reverb,
    compress,
    delay,
    spring_reverb,
    F,
    MF,
    MP,
    P,
)
from code_music.theory.rhythm import (
    ska_drum_pattern,
    skank_pattern,
    ska_bass_line,
    ska_horn_riff,
    apply_groove,
    groove_template,
)

song = Song(title="Pick It Up (Ska Showcase)", bpm=168, key_sig="C", time_sig=(4, 4))

# ── Section 1: First Wave (Skatalites style) ────────────────────────
prog_1 = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass.extend(ska_bass_line(prog_1, style="walking", seed=42))

# Guitar skank: the offbeat engine
skank = song.add_track(
    Track(name="guitar_skank", instrument="guitar_electric", volume=0.5, pan=0.2)
)
for root, shape in prog_1:
    skank.extend(skank_pattern(root, shape, style="traditional", bars=1))

# Horn stabs: trumpet + trombone
horns = song.add_track(Track(name="horns", instrument="trumpet", volume=0.55, pan=-0.15))
horns.extend(ska_horn_riff("C", "maj", 5, bars=2, style="stab", seed=42))
horns.extend(ska_horn_riff("G", "dom7", 5, bars=2, style="riff", seed=42))

# Drums: traditional ska
drums_pat = ska_drum_pattern(bars=4, style="traditional")
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
kick.extend(drums_pat["kick"])
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.4))
snare.extend(drums_pat["snare"])
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.5))
hat.extend(drums_pat["hat"])

# ── Section 2: 2 Tone (The Specials vibes) ──────────────────────────
prog_2 = [("A", "min"), ("D", "min"), ("E", "dom7"), ("A", "min")]

bass_2 = song.add_track(Track(name="bass_2tone", instrument="bass", volume=0.6))
bass_2.extend(ska_bass_line(prog_2, style="walking", seed=43))

skank_2 = song.add_track(
    Track(name="skank_2tone", instrument="guitar_electric", volume=0.55, pan=0.2)
)
for root, shape in prog_2:
    skank_2.extend(skank_pattern(root, shape, style="two_tone", bars=1))

organ = song.add_track(Track(name="organ", instrument="organ", volume=0.4, pan=-0.2))
for root, shape in prog_2:
    organ.add(Chord(root, shape, 3, duration=4.0, velocity=MP))

drums_2 = ska_drum_pattern(bars=4, style="two_tone")
kick_2 = song.add_track(Track(name="kick_2t", instrument="drums_kick", volume=0.65))
kick_2.extend(drums_2["kick"])
snare_2 = song.add_track(Track(name="snare_2t", instrument="drums_snare", volume=0.5))
snare_2.extend(drums_2["snare"])
hat_2 = song.add_track(Track(name="hat_2t", instrument="drums_hat", volume=0.5))
hat_2.extend(drums_2["hat"])

# Effects: spring reverb on horns (that classic drippy ska sound)
song.effects = {
    "horns": EffectsChain().add(spring_reverb, tension=0.5, wet=0.2),
    "guitar_skank": EffectsChain().add(compress, threshold=0.4, ratio=4.0),
}
