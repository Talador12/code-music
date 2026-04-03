"""Pentatonic Journey — pentatonic melody continuation with section markers."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import Chorus, Intro, Verse, continue_melody

intro_seed = [Note("C", 5, 1.0), Note("D", 5, 1.0)]
intro_melody = continue_melody(intro_seed, bars=2, key="C", mode="pentatonic", seed_rng=10)

verse_seed = [Note("E", 5, 0.5), Note("G", 5, 0.5), Note("A", 5, 0.5)]
verse_melody = continue_melody(verse_seed, bars=4, key="C", mode="pentatonic", seed_rng=20)

i = Intro(bars=2)
i.add_track("lead", intro_melody)
v = Verse(bars=4)
v.add_track("lead", verse_melody)

song = Song(title="Pentatonic Journey", bpm=110, sample_rate=44100)
tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
tr.extend(intro_melody)
tr.extend(verse_melody)

song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [
        Chord("C", "maj7", 3, duration=4.0),
        Chord("A", "min7", 3, duration=4.0),
        Chord("F", "maj7", 3, duration=4.0),
        Chord("G", "dom7", 3, duration=4.0),
    ]
)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6)).extend(
    euclid(4, 16, "C", 2, 0.5)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
