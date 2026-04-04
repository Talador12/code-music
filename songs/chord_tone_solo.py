"""Chord Tone Solo — jazz improv with chord-tone targeting over a ii-V-I."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import approach_pattern, generate_bass_line, target_chord_tones

song = Song(title="Chord Tone Solo", bpm=160)

prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")]

# Comping
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=-0.15))
for _ in range(2):
    for root, shape in prog:
        comp.add(Chord(root, shape, 3, duration=4.0))

# Solo — chord tones on strong beats, scale tones between
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
solo = target_chord_tones(prog * 2, key="C", notes_per_chord=8, seed=42)
lead.extend(solo)

# Approach pattern ornaments
for target in ["C", "E", "G"]:
    lead.extend(approach_pattern(target, octave=5, direction="enclosure"))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(2):
    bass.extend(generate_bass_line(prog, style="walking", seed=42))

# Ride
ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, pan=0.2))
for _ in range(32):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "lead": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
