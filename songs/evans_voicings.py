"""Evans Voicings — Bill Evans rootless A/B voicings through a ii-V-I."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_bass_line, rootless_a, rootless_b

song = Song(title="Evans Voicings", bpm=120)

# ii-V-I in C — the most important progression in jazz
prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")]

# Piano: alternate A and B voicings for smooth voice leading
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.45, pan=0.1))
for i, (root, shape) in enumerate(prog * 2):
    if i % 2 == 0:
        piano.extend(rootless_a(root, shape, octave=3, duration=4.0))
    else:
        piano.extend(rootless_b(root, shape, octave=3, duration=4.0))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for _ in range(2):
    bass.extend(generate_bass_line(prog, style="walking", seed=42))

# Ride cymbal
ride = song.add_track(Track(name="ride", instrument="drums_hat", volume=0.2, pan=0.2))
for _ in range(32):
    ride.add(Note("C", 5, 0.5))
    ride.add(Note("C", 5, 0.25))
    ride.add(Note.rest(0.25))

song.effects = {
    "piano": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
