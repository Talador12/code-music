"""Power Chords — parallel fifths on a distorted guitar-like tone."""

from code_music import EffectsChain, Note, Song, SoundDesigner, Track, distortion
from code_music.theory import parallel_motion

riff = [Note(n, 3, 0.5) for n in ["E", "E", "G", "A", "E", "E", "Bb", "A"]]
fifths = parallel_motion(riff, interval=7)
heavy = (
    SoundDesigner("heavy")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("square", detune_cents=-5, volume=0.3)
    .envelope(attack=0.005, decay=0.1, sustain=0.7, release=0.2)
    .filter("lowpass", cutoff=3000, resonance=1.0)
)
song = Song(title="Power Chords", bpm=140, sample_rate=44100)
song.register_instrument("heavy", heavy)
song.add_track(Track(name="root", instrument="heavy", volume=0.6)).extend(riff)
song.add_track(Track(name="fifth", instrument="heavy", volume=0.5)).extend(fifths)
song.effects = {"root": EffectsChain().add(distortion, drive=2.0, tone=0.5, wet=0.4)}
