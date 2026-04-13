"""Rhythm Changes Blowout — bebop-style contrafact on rhythm changes in Bb."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import rhythm_changes

song = Song(title="Rhythm Changes Blowout", bpm=240)

# Classic rhythm changes in Bb
prog = rhythm_changes("Bb")

# Comping — Freddie Green style
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.35, pan=-0.2))
for root, shape in prog:
    comp.add(Chord(root, shape, 3, duration=2.0))
# Repeat the A section
for root, shape in prog:
    comp.add(Chord(root, shape, 3, duration=2.0))

# Bass — root-fifth pattern
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
from code_music.theory import generate_bass_line  # noqa: E402

for _ in range(2):
    notes = generate_bass_line(prog, style="root_fifth", seed=42)
    bass.extend(notes)

# Bebop melody — Charlie Parker would approve (or at least tolerate)
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.15))
bebop_line = [
    Note("Bb", 5, 0.25),
    Note("D", 6, 0.25),
    Note("F", 5, 0.25),
    Note("A", 5, 0.25),
    Note("G", 5, 0.5),
    Note("F", 5, 0.25),
    Note("Eb", 5, 0.25),
    Note("D", 5, 0.5),
    Note("C", 5, 0.25),
    Note("Bb", 4, 0.25),
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.25),
    Note("D", 5, 0.25),
    Note("C", 5, 0.5),
    Note("Bb", 4, 0.5),
]
for _ in range(4):
    lead.extend(bebop_line)

# Drums — jazz ride
ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, pan=0.25))
for _ in range(32):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
