"""Layered Sections — song_append builds a multi-section arrangement."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.automation import song_append

# Section A: ambient pad
section_a = Song(title="A", bpm=100, sample_rate=44100)
tr_pad = section_a.add_track(Track(name="pad", instrument="pad", volume=0.4))
tr_pad.add(Chord("A", "min7", 3, duration=8.0))

# Section B: add drums + bass
section_b = Song(title="B", bpm=100, sample_rate=44100)
tr_kick = section_b.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(8):
    tr_kick.add(Note("C", 2, 1.0))
tr_bass = section_b.add_track(Track(name="bass", instrument="bass", volume=0.5))
tr_bass.extend(euclid(5, 16, "A", 2, 0.5))
tr_pad_b = section_b.add_track(Track(name="pad", instrument="pad", volume=0.4))
tr_pad_b.add(Chord("F", "maj7", 3, duration=8.0))

# Append: A → B
song = song_append(section_a, section_b)
print(f"Combined: {song.title}, {len(song.tracks)} tracks")

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
