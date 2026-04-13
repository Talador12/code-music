"""Electronic Theory — generated drums + walking bass meets electronic production."""

from code_music import Chord, EffectsChain, Pattern, Song, SoundDesigner, Track, reverb
from code_music.theory import generate_bass_line, generate_drums

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=0.5)
)

song = Song(title="Electronic Theory", bpm=128, sample_rate=44100)
song.register_instrument("supersaw", supersaw)

prog = [("E", "min7"), ("A", "min7"), ("D", "dom7"), ("G", "maj7")]

lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.45, pan=0.15))
pat = Pattern("E5 G5 B5 D6 C6 B5 G5 A5")
lead.extend(pat.to_notes(0.5))
lead.extend(pat.reverse().to_notes(0.5))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(generate_bass_line(prog, style="root_fifth"))

drums = generate_drums("electronic", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    song.add_track(Track(name=name, instrument=instr, volume=0.5)).extend(notes)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3)}
