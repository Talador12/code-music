"""Granular Meditation - layered granular textures for deep listening."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.effects import room_reverb
from code_music.sound_design import grain_rain, grain_texture

song = Song(title="Granular Meditation", bpm=45, sample_rate=44100)
song.register_instrument("grain_texture", grain_texture)
song.register_instrument("grain_rain", grain_rain)

# Texture layer
texture = song.add_track(Track(name="texture", instrument="grain_texture", volume=0.35))
for note in ["E", "B", "G", "E"]:
    texture.add(Note(note, 4, 12.0, velocity=35))

# Rain layer
rain = song.add_track(Track(name="rain", instrument="grain_rain", volume=0.25, pan=0.3))
for note in ["B", "E", "G", "B"]:
    rain.add(Note(note, 5, 12.0, velocity=25))

# Sub bass
sub = song.add_track(Track(name="sub", instrument="bass", volume=0.3))
sub.add(Note("E", 1, 48.0, velocity=40))

song.effects = {
    "texture": EffectsChain()
    .add(room_reverb, width=20, depth=30, height=12, absorption=0.1, wet=0.4)
    .add(reverb, room_size=0.95, wet=0.5),
    "rain": EffectsChain().add(reverb, room_size=0.9, wet=0.45),
}
