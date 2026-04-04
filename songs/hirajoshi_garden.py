"""Hirajoshi Garden — Japanese pentatonic scale with ambient textures."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_scale_melody

song = Song(title="Hirajoshi Garden", bpm=66)

# Hirajoshi scale melody (now available via scale atlas)
melody = generate_scale_melody(
    key="D",
    scale_name="hirajoshi",
    length=24,
    octave=5,
    duration=1.0,
    contour="wave",
    seed=42,
)

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.5, pan=0.15))
lead.extend(melody)

# Low drone
drone = song.add_track(Track(name="drone", instrument="pad", volume=0.3, pan=-0.1))
drone.add(Note("D", 3, 24.0))

# Sparse percussion
perc = song.add_track(Track(name="perc", instrument="pluck", volume=0.25, pan=0.3))
for _ in range(6):
    perc.add(Note("D", 6, 0.25))
    perc.add(Note.rest(3.75))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=500, feedback=0.3, wet=0.25),
    "drone": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
}
