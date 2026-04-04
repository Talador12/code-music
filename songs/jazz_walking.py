"""Jazz Walking — intelligent jazz bass line with chromatic approaches."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import bass_line_jazz

song = Song(title="Jazz Walking", bpm=140)

prog = [("C", "maj7"), ("A", "min7"), ("D", "min7"), ("G", "dom7")] * 2

comp = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=0.1))
for root, shape in prog:
    comp.add(Chord(root, shape, 3, duration=4.0))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
bass.extend(bass_line_jazz(prog, seed=42))

ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, pan=0.2))
for _ in range(32):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

song.effects = {"comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2)}
