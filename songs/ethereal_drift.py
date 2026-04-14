"""Ethereal Drift - whisper pads and vocal drones in space."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.effects import orbit
from code_music.sound_design import ethereal_voice, ice_pad, whisper_pad

song = Song(title="Ethereal Drift", bpm=50, sample_rate=44100)
song.register_instrument("ethereal_voice", ethereal_voice)
song.register_instrument("whisper_pad", whisper_pad)
song.register_instrument("ice_pad", ice_pad)

# Ethereal voice melody
voice = song.add_track(Track(name="voice", instrument="ethereal_voice", volume=0.4, pan=0.1))
voice.extend(scale("E", "pentatonic", octave=5, length=8))

# Whisper pad bed
whisper = song.add_track(Track(name="whisper", instrument="whisper_pad", volume=0.3))
for root, shape in [("E", "min7"), ("C", "maj7")]:
    whisper.add(Chord(root, shape, 3, duration=16.0, velocity=30))

# Ice pad shimmer
ice = song.add_track(Track(name="ice", instrument="ice_pad", volume=0.2, pan=-0.2))
ice.add(Chord("E", "min", 5, duration=32.0, velocity=20))

# Sub drone
sub = song.add_track(Track(name="sub", instrument="bass", volume=0.3))
sub.add(Note("E", 1, 32.0, velocity=40))

song.effects = {
    "voice": EffectsChain().add(reverb, room_size=0.95, wet=0.5),
    "whisper": lambda samples, sr: orbit(samples, sr, rate=0.1, radius=3.0),
    "ice": EffectsChain().add(reverb, room_size=0.98, wet=0.6),
}
