"""Structured Pop — verse/chorus arrangement using named sections."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import Chorus, Verse, continue_melody

verse_melody = [
    Note(n, 5, 0.5)
    for n in ["C", "D", "E", "G", "E", "D", "C", "D", "E", "G", "A", "G", "E", "D", "C", "C"]
]
chorus_seed = [Note("G", 5, 0.5), Note("A", 5, 0.5), Note("C", 6, 0.5)]
chorus_melody = continue_melody(chorus_seed, bars=2, key="C", mode="major", seed_rng=77)

v = Verse(bars=4)
v.add_track("lead", verse_melody)
c = Chorus(bars=4)
c.add_track("lead", chorus_melody)

song = Song(title="Structured Pop", bpm=120, sample_rate=44100)
tr_lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
tr_lead.extend(verse_melody)
tr_lead.extend(chorus_melody)

tr_pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35))
tr_pad.add(Chord("C", "maj7", 3, duration=4.0))
tr_pad.add(Chord("A", "min7", 3, duration=4.0))
tr_pad.add(Chord("F", "maj7", 3, duration=4.0))
tr_pad.add(Chord("G", "dom7", 3, duration=4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
