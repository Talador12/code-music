"""Call & Response — a phrase answered by its generated response."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import call_and_response

call = [Note(n, 5, 0.5) for n in ["C", "E", "G", "B", "A", "G", "E", "C"]]
response = call_and_response(call, key="C", mode="major", seed=42)
song = Song(title="Call & Response", bpm=110, sample_rate=44100)
song.add_track(Track(name="call", instrument="piano", volume=0.5, pan=-0.2)).extend(call)
song.add_track(Track(name="response", instrument="piano", volume=0.5, pan=0.2)).extend(response)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
