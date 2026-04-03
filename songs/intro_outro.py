"""Intro Outro — auto-generated intro and outro from song material."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import generate_intro, generate_outro

song = Song(title="Intro Outro", bpm=100, sample_rate=44100)
main_melody = [Note(n, 5, 1.0) for n in ["C", "E", "G", "B", "A", "G", "E", "C"]]
intro = generate_intro(song.__class__(title="temp", bpm=100, sample_rate=44100), bars=2)
# Build temp song for material extraction
temp = Song(title="temp", bpm=100, sample_rate=44100)
temp.add_track(Track(name="lead", instrument="piano")).extend(main_melody)
intro = generate_intro(temp, bars=2)
outro = generate_outro(temp, bars=2)
song.add_track(Track(name="intro_lead", instrument="piano", volume=0.3)).extend(intro)
song.add_track(Track(name="main_lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    main_melody
)
song.add_track(Track(name="outro_lead", instrument="piano", volume=0.3)).extend(outro)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("C", "maj7", 3, duration=8.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
