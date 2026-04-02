"""Composite Track — demonstrates song_overlay and song_extract."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.automation import song_extract, song_overlay

# Build two separate songs
intro = Song(title="Intro", bpm=120, sample_rate=44100)
tr_pad = intro.add_track(Track(name="pad", instrument="pad", volume=0.4))
tr_pad.add(Chord("C", "min7", 3, duration=8.0))

main = Song(title="Main", bpm=120, sample_rate=44100)
tr_lead = main.add_track(Track(name="lead", instrument="piano", volume=0.5))
for n in ["C", "Eb", "G", "Bb", "Ab", "G", "Eb", "C"]:
    tr_lead.add(Note(n, 5, 1.0))
tr_kick = main.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(8):
    tr_kick.add(Note("C", 2, 1.0))

# Overlay main onto intro
song_overlay(intro, main)
print(f"After overlay: {len(intro.tracks)} tracks")

# Extract just the melodic tracks
melodic = song_extract(intro, ["pad", "lead"])
print(f"Extracted: {len(melodic.tracks)} tracks")

# Use intro as the final song
song = intro
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
