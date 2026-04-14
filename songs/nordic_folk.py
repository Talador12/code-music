"""Nordic Folk - Dorian melody with drone bass, Scandinavian feel."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale

song = Song(title="Nordic Folk", bpm=84, sample_rate=44100)

fiddle = song.add_track(Track(name="fiddle", instrument="triangle", volume=0.45, pan=0.15))
fiddle.extend(scale("D", "dorian", octave=5, length=14))

drone = song.add_track(Track(name="drone", instrument="pad", volume=0.25))
drone.add(Chord("D", "sus2", 3, duration=14.0, velocity=35))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
bass.add(Note("D", 2, 14.0, velocity=50))

song.effects = {
    "fiddle": EffectsChain().add(reverb, room_size=0.6, wet=0.2),
}
