"""Jazz Numerals — jazz turnaround written in Roman numeral notation."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import parse_roman, progression_from_roman

song = Song(title="Jazz Numerals", bpm=140)

# Jazz ii-V-I turnaround with applied chords, written in analysis notation
jazz_prog = progression_from_roman(
    ["Imaj7", "vi7", "ii7", "V7", "iii7", "vi7", "ii7", "V7"],
    key="Bb",
)

# Comp
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=-0.15))
for _ in range(2):
    for root, shape in jazz_prog:
        comp.add(Chord(root, shape, 3, duration=2.0))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
from code_music.theory import generate_bass_line

for _ in range(2):
    notes = generate_bass_line(jazz_prog, style="walking", seed=42)
    bass.extend(notes)

# Ride
ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, pan=0.2))
for _ in range(32):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
