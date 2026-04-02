"""Latin Theory — latin drum patterns + syncopated bass from generators."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, generate_drums

song = Song(title="Latin Theory", bpm=105, sample_rate=44100)
prog = [("A", "min7"), ("D", "min7"), ("G", "dom7"), ("C", "maj7")]

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(generate_bass_line(prog, style="syncopated"))

drums = generate_drums("latin", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    song.add_track(Track(name=name, instrument=instr, volume=0.45)).extend(notes)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.15))
for n in ["A", "C", "E", "G", "F", "D", "G", "B", "E", "G", "B", "D", "C", "E", "G", "C"]:
    lead.add(Note(n, 5, 1.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.25)}
