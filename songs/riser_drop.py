"""Riser Drop — tension-building riser into a chord drop."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, euclid, reverb
from code_music.composition import generate_fill, generate_riser

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.02, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=0.5)
)
song = Song(title="Riser Drop", bpm=140, sample_rate=44100)
song.register_instrument("supersaw", supersaw)
# Riser section
song.add_track(Track(name="riser", instrument="sawtooth", volume=0.4)).extend(
    generate_riser(bars=4, start_note="C", octave=3)
)
song.add_track(Track(name="buildup", instrument="drums_snare", volume=0.5)).extend(
    generate_fill(bars=4, style="buildup")
)
# Drop section
song.add_track(Track(name="drop", instrument="supersaw", volume=0.6)).extend(
    [Note.rest(1.0)] * 16
    + [
        Chord("C", "min", 4, duration=4.0),
        Chord("Ab", "maj", 4, duration=4.0),
        Chord("Eb", "maj", 4, duration=4.0),
        Chord("Bb", "maj", 4, duration=4.0),
    ]
)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8)).extend(
    [Note.rest(1.0)] * 16 + [Note("C", 2, 1.0) for _ in range(16)]
)
song.effects = {"drop": EffectsChain().add(reverb, room_size=0.4, wet=0.2)}
