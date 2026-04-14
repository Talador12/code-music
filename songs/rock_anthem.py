"""Rock Anthem - power chords with distorted lead."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, distortion, reverb, scale

song = Song(title="Rock Anthem", bpm=140, sample_rate=44100)

# Power chord rhythm guitar
rhythm = song.add_track(Track(name="rhythm", instrument="sawtooth", volume=0.5, pan=-0.3))
for root in ["E", "G", "A", "E", "E", "G", "A", "B"] * 2:
    rhythm.add(Chord(root, "5", 3, duration=2.0, velocity=75))

# Lead guitar
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.3))
lead.extend(scale("E", "pentatonic_minor", octave=5, length=16))
lead.extend(scale("E", "blues", octave=5, length=16))

# Bass follows root
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for root in ["E", "G", "A", "E", "E", "G", "A", "B"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=70))

# Drums
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(32):
    kick.add(Note("C", 4, 1.0, velocity=85))

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
for _ in range(16):
    snare.add(Note.rest(1.0))
    snare.add(Note("C", 4, 1.0, velocity=75))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=35))

song.effects = {
    "rhythm": EffectsChain().add(distortion, drive=0.5, wet=0.6),
    "lead": EffectsChain()
    .add(distortion, drive=0.4, wet=0.5)
    .add(delay, delay_ms=375, feedback=0.2, wet=0.15)
    .add(reverb, room_size=0.4, wet=0.15),
}
