"""Hungarian Fire — Hungarian minor scale with driving rhythm."""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, reverb
from code_music.theory import generate_scale_melody

song = Song(title="Hungarian Fire", bpm=150)

# Hungarian minor melody — that augmented 2nd is pure drama
melody = generate_scale_melody(
    key="A",
    scale_name="hungarian_minor",
    length=32,
    octave=5,
    duration=0.25,
    contour="arch",
    seed=77,
)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(melody)

# Power chords
rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.4, pan=-0.2))
for _ in range(4):
    rhythm.add(Chord("A", "min", 3, duration=2.0))
    rhythm.add(Chord("Bb", "maj", 3, duration=2.0))

# Drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(16):
    kick.add(Note("C", 2, 0.5))
    kick.add(Note.rest(0.5))

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "rhythm": EffectsChain().add(distortion, gain=3.0, wet=0.5),
}
