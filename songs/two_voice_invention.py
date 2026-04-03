"""Two Voice Invention — Bach-inspired counterpoint with thirds and sixths."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_counterpoint

cantus = [
    Note(n, 4, 0.5)
    for n in ["E", "F", "G", "A", "G", "F", "E", "D", "C", "D", "E", "F", "E", "D", "C", "C"]
]
thirds = generate_counterpoint(cantus, interval="third", seed=42)
sixths = generate_counterpoint(cantus, interval="sixth", seed=99)
song = Song(title="Two Voice Invention", bpm=100, sample_rate=44100)
song.add_track(Track(name="cantus", instrument="piano", volume=0.5)).extend(cantus)
song.add_track(Track(name="thirds", instrument="piano", volume=0.4, pan=0.2)).extend(thirds)
song.add_track(Track(name="sixths", instrument="piano", volume=0.35, pan=-0.2)).extend(sixths)
song.effects = {"cantus": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
