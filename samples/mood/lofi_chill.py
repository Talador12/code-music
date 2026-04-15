"""Lofi chill - midnight study session vibes. Dusty Rhodes, vinyl crackle, Dilla drums."""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    reverb,
    chorus,
    MP,
    P,
    PP,
)
from code_music.effects import lofi_vinyl, tape_wow_flutter, tape_sat
from code_music.theory.rhythm import lofi_drum_pattern, apply_groove, groove_template

song = Song(title="Lofi Chill", bpm=75, key_sig="D", time_sig=(4, 4))

# Chord progression: melancholy lofi
prog = [
    ("D", "maj7_open"),
    ("F#", "min7_open"),
    ("G", "maj7_open"),
    ("E", "min7_open"),
]

# Dusty Rhodes - open voicings, low velocity, dreamy
rhodes = song.add_track(Track(name="rhodes", instrument="rhodes", volume=0.45, pan=-0.1))
for root, shape in prog * 2:
    rhodes.add(Chord(root, shape, 3, duration=4.0, velocity=PP))
    rhodes.add(Note.rest(4.0))

# Lofi bass - sparse and deep
from code_music.theory import bass_line_lofi

bass = song.add_track(Track(name="bass", instrument="sub_bass", volume=0.5, pan=0.0))
simple_prog = [("D", "maj7"), ("F#", "min7"), ("G", "maj7"), ("E", "min7")]
bass.extend(bass_line_lofi(simple_prog * 2, octave=2, seed=42))

# Drums: Dilla-drunk pocket
drums = lofi_drum_pattern(bars=8, seed=42)
lofi_feel = groove_template("lofi")

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.55))
kick.extend(apply_groove(drums["kick"], lofi_feel, strength=0.8))

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.35))
snare.extend(apply_groove(drums["snare"], lofi_feel, strength=0.8))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.2))
hat.extend(apply_groove(drums["hat"], lofi_feel, strength=0.8))

# Effects: the lofi sauce
song.effects = {
    "rhodes": (
        EffectsChain()
        .add(chorus, rate_hz=0.3, depth_ms=4.0, wet=0.3)
        .add(tape_sat, drive=1.5, warmth=0.6, wet=0.4)
        .add(lofi_vinyl, crackle=0.015, hiss=0.008, warmth=0.4, wear=0.3)
        .add(reverb, room_size=0.6, wet=0.25)
    ),
    "bass": EffectsChain().add(tape_sat, drive=1.3, warmth=0.7, wet=0.3),
    "kick": EffectsChain().add(tape_sat, drive=1.2, warmth=0.5, wet=0.2),
    "snare": EffectsChain().add(lofi_vinyl, crackle=0.01, warmth=0.3, wet=0.5),
}
