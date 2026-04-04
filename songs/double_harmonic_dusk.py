"""Double Harmonic Dusk — the Byzantine scale, both exotic and ancient."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_scale_melody

song = Song(title="Double Harmonic Dusk", bpm=80)

# Double harmonic (Byzantine) scale — two augmented seconds, middle eastern flavor
melody = generate_scale_melody(
    key="E",
    scale_name="double_harmonic",
    length=24,
    octave=5,
    duration=0.5,
    contour="descending",
    seed=33,
)

lead = song.add_track(Track(name="lead", instrument="pluck", volume=0.5, pan=0.2))
lead.extend(melody)

# Drone on E
drone = song.add_track(Track(name="drone", instrument="organ", volume=0.3, pan=-0.15))
drone.add(Note("E", 3, 12.0))

# Simple bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for _ in range(6):
    bass.extend([Note("E", 2, 1.0), Note("F", 2, 1.0)])

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=375, feedback=0.2, wet=0.2),
    "drone": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
