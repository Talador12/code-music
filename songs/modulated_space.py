"""Modulated Space — LFO modulation matrix creates evolving textures."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.automation import ModMatrix

mm = ModMatrix()
mm.connect("lfo1", "pad.volume", amount=0.3, rate=0.25)
mm.connect("lfo2", "lead.pan", amount=0.5, rate=0.1)
mm.connect("random", "bass.volume", amount=0.15)
print(f"Mod matrix: {mm}")

wobble = (
    SoundDesigner("wobble")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .add_osc("sawtooth", detune_cents=-5, volume=0.3)
    .envelope(attack=0.2, decay=0.1, sustain=0.6, release=0.5)
    .filter("lowpass", cutoff=2000, resonance=1.5)
    .lfo("filter_cutoff", rate=0.4, depth=0.6)
)

song = Song(title="Modulated Space", bpm=100, sample_rate=44100)
song.register_instrument("wobble", wobble)

tr_pad = song.add_track(Track(name="pad", instrument="wobble", volume=0.4, pan=-0.1))
tr_pad.add(Chord("A", "min9", 3, duration=8.0))
tr_pad.add(Chord("F", "maj7", 3, duration=8.0))

tr_lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.15))
for n in ["A", "C", "E", "G", "F", "E", "C", "A", "E", "G", "A", "C", "B", "A", "G", "E"]:
    tr_lead.add(Note(n, 5, 1.0))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["A", "A", "F", "F"]:
    tr_bass.add(Note(root, 2, 4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4)}
