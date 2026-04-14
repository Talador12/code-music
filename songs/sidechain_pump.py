"""Sidechain Pump - classic EDM ducking with EnvFollower."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, sidechain

song = Song(title="Sidechain Pump", bpm=128, sample_rate=44100)

# Four-on-the-floor kick
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
for _ in range(32):
    kick.add(Note("C", 4, 1.0, velocity=85))

# Off-beat hats
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(32):
    hat.add(Note.rest(0.5))
    hat.add(Note("C", 6, 0.5, velocity=40))

# Sustained pad (will get ducked by the kick via sidechain effect)
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.5, pan=-0.1))
for root, shape in [("C", "min7"), ("Ab", "maj7"), ("Bb", "maj"), ("G", "dom7")] * 4:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=50))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for root in ["C", "C", "Ab", "Ab", "Bb", "Bb", "G", "G"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=70))

# Lead melody
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2))
from code_music import scale

mel = scale("C", "pentatonic_minor", octave=5, length=16)
for _ in range(2):
    lead.extend(mel)

# Per-track effects: sidechain the pad to the kick
song.effects = {
    "pad": EffectsChain()
    .add(sidechain, threshold=0.3, ratio=4.0, attack_ms=5, release_ms=150, wet=0.8)
    .add(reverb, room_size=0.6, wet=0.2),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
