"""Granular Counterpoint — grain textures + algorithmic counterpoint."""

from code_music import EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.theory import generate_counterpoint

cloud = (
    SoundDesigner("cloud")
    .add_osc("triangle", volume=0.3)
    .granular(grain_size=0.06, density=18, scatter=0.7, volume=0.7, seed=42)
    .envelope(attack=0.5, decay=0.3, sustain=0.4, release=1.0)
    .filter("lowpass", cutoff=2500, resonance=0.5)
)

melody = [
    Note(n, 4, 0.5)
    for n in ["A", "B", "C", "D", "E", "F", "G", "A", "G", "F", "E", "D", "C", "B", "A", "A"]
]
thirds = generate_counterpoint(melody, interval="third", seed=42)
sixths = generate_counterpoint(melody, interval="sixth", seed=77)

song = Song(title="Granular Counterpoint", bpm=85, sample_rate=44100)
song.register_instrument("cloud", cloud)

song.add_track(Track(name="cloud", instrument="cloud", volume=0.25)).add(Note("A", 3, 16.0))
song.add_track(Track(name="cantus", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="thirds", instrument="piano", volume=0.4, pan=0.2)).extend(thirds)
song.add_track(Track(name="sixths", instrument="piano", volume=0.35, pan=-0.2)).extend(sixths)
song.effects = {
    "cloud": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "cantus": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
}
