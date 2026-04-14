"""Funk Groove - syncopated bass and drums with wah lead."""

from code_music import Chord, EffectsChain, Note, Song, Track, distortion, lowpass

song = Song(title="Funk Groove", bpm=100, sample_rate=44100)

# Kick: syncopated funk pattern
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
pattern = [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]
for _ in range(4):
    for hit in pattern:
        if hit:
            kick.add(Note("C", 4, 0.5, velocity=80))
        else:
            kick.add(Note.rest(0.5))

# Snare: 2 and 4
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
for _ in range(16):
    snare.add(Note.rest(1.0))
    snare.add(Note("C", 4, 1.0, velocity=75))

# Hat: 16ths
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3, swing=0.1))
for _ in range(64):
    hat.add(Note("C", 6, 0.5, velocity=35))

# Funk bass: syncopated root-octave pattern
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, swing=0.08))
for _ in range(4):
    for root in ["E", "E", "A", "A"]:
        bass.add(Note(root, 2, 0.5, velocity=75))
        bass.add(Note(root, 3, 0.25, velocity=60))
        bass.add(Note.rest(0.25))
        bass.add(Note(root, 2, 0.5, velocity=70))
        bass.add(Note.rest(0.5))

# Rhythm guitar (chords)
guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.35, pan=0.2, swing=0.08))
for _ in range(4):
    for root, shape in [("E", "min7"), ("E", "min7"), ("A", "dom7"), ("A", "dom7")]:
        guitar.add(Note.rest(0.5))
        guitar.add(Chord(root, shape, 3, duration=0.5, velocity=50))
        guitar.add(Note.rest(0.5))
        guitar.add(Chord(root, shape, 3, duration=0.5, velocity=45))

# Wah lead
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.4, pan=-0.2))
from code_music import scale

mel = scale("E", "pentatonic_minor", octave=5, length=32)
lead.extend(mel)

song.effects = {
    "lead": EffectsChain().add(distortion, drive=0.3, wet=0.4).add(lowpass, cutoff_hz=3000, q=2.0),
    "bass": EffectsChain().add(distortion, drive=0.15, wet=0.2),
}
