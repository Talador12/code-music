"""Automation Sweep — showcasing automation curves and modulation matrix."""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Pattern,
    Song,
    SoundDesigner,
    Track,
    euclid,
    reverb,
)
from code_music.automation import Automation, ModMatrix

wobble = (
    SoundDesigner("wobble")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .add_osc("sawtooth", detune_cents=-5, volume=0.3)
    .envelope(attack=0.1, decay=0.1, sustain=0.6, release=0.4)
    .filter("lowpass", cutoff=2000, resonance=1.5)
    .lfo("filter_cutoff", rate=0.5, depth=0.6)
)

song = Song(title="Automation Sweep", bpm=130, sample_rate=44100)
song.register_instrument("wobble", wobble)

# Automation curves
vol = Automation([(0, 0.0), (4, 0.8), (12, 0.8), (16, 0.0)], mode="smoothstep")
mm = ModMatrix().connect("lfo1", "pad.volume", amount=0.3, rate=0.25)

song.add_track(Track(name="pad", instrument="wobble", volume=0.4, pan=-0.1)).extend(
    [Chord("E", "min7", 3, duration=8.0), Chord("C", "maj7", 3, duration=8.0)]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    Pattern("E5 G5 B5 D6 C6 B5 G5 A5").to_notes(0.5)
)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0) * 2
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(n, 2, 4.0) for n in ["E", "E", "C", "C"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
print(f"Vol at beat 8: {vol.value_at(8):.2f}, Mod routes: {len(mm)}")
