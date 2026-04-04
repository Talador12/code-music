"""Giant Steps Study — Coltrane changes with walking bass and ride cymbal."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import coltrane_changes, generate_bass_line

song = Song(title="Giant Steps Study", bpm=280)

# Coltrane changes — the Mount Everest of jazz harmony
prog = coltrane_changes("B")

# Comping — chord hits
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=-0.15))
for root, shape in prog:
    comp.add(Chord(root, shape, 3, duration=2.0))

# Walking bass through the changes
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for i in range(0, len(prog), 4):
    chunk = prog[i : i + 4]
    notes = generate_bass_line(chunk, style="walking", seed=i)
    bass.extend(notes)

# Ride cymbal — jazz time
ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.25, pan=0.2))
for _ in range(24):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

# Walking melody over the changes (sparse, letting the harmony speak)
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.35, pan=0.1))
melody_notes = [
    Note("B", 5, 1.0),
    Note("D#", 5, 1.0),
    Note("D", 5, 1.0),
    Note("G#", 5, 1.0),
    Note("G", 5, 1.0),
    Note("F#", 5, 1.0),
    Note("B", 5, 1.0),
    Note("D#", 5, 1.0),
    Note("D", 5, 1.0),
    Note("G#", 5, 1.0),
    Note("G", 5, 1.0),
    Note("F#", 5, 1.0),
]
lead.extend(melody_notes)
lead.extend(melody_notes)

song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
