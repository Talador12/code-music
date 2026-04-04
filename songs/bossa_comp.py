"""Bossa Comp — syncopated bossa nova comping with Latin bass."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import bass_line_latin, comp_pattern

song = Song(title="Bossa Comp", bpm=130)

prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")] * 2

comp = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=0.1))
comp.extend(comp_pattern(prog, style="bossa", octave=3))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(bass_line_latin(prog, seed=42))

song.effects = {"comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2)}
