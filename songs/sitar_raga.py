"""Sitar Raga - Indian classical with sitar, tabla, and drone."""

from code_music import EffectsChain, Note, Song, Track, reverb, scale
from code_music.sound_design import didgeridoo, sitar, tabla

song = Song(title="Sitar Raga", bpm=72, sample_rate=44100)
song.register_instrument("sitar", sitar)
song.register_instrument("tabla", tabla)
song.register_instrument("didgeridoo", didgeridoo)

# Sitar melody
sit = song.add_track(Track(name="sitar", instrument="sitar", volume=0.5, pan=0.15))
sit.extend(scale("D", "hirajoshi", octave=5, length=10))
sit.extend(scale("D", "hirajoshi", octave=4, length=10))

# Tabla rhythm
tab = song.add_track(Track(name="tabla", instrument="tabla", volume=0.55))
for _ in range(5):
    tab.add(Note("D", 3, 0.5, velocity=70))
    tab.add(Note.rest(0.25))
    tab.add(Note("D", 3, 0.25, velocity=55))
    tab.add(Note("D", 4, 0.5, velocity=65))
    tab.add(Note.rest(0.5))

# Tanpura drone (using didgeridoo for the buzz)
drone = song.add_track(Track(name="tanpura", instrument="didgeridoo", volume=0.25))
drone.add(Note("D", 2, 20.0, velocity=40))

song.effects = {
    "sitar": EffectsChain().add(reverb, room_size=0.6, wet=0.2),
}
