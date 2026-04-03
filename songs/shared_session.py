"""Shared Session — two 'musicians' build a song via JSON exchange."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.serialization import song_from_json, song_to_json

# Musician A: creates the foundation
part_a = Song(title="Shared Session", bpm=120, sample_rate=44100)
part_a.add_track(Track(name="pad", instrument="pad", volume=0.4)).add(
    Chord("A", "min7", 3, duration=8.0)
)
part_a.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0)
)

# "Send" via JSON
json_data = song_to_json(part_a)

# Musician B: receives and adds parts
song = song_from_json(json_data)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2)).extend(
    [Note(n, 5, 1.0) for n in ["A", "C", "E", "G", "F", "E", "C", "A"]]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note("A", 2, 2.0), Note("A", 2, 2.0), Note("F", 2, 2.0), Note("G", 2, 2.0)]
)

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(f"Collaborative: {song.title}, {len(song.tracks)} tracks (2 from A + 2 from B)")
