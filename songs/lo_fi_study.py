"""lo_fi_study.py - Lo-fi chill beats for studying. Warm and dusty."""

from code_music import Chord, EffectsChain, Note, Song, Track, lowpass, reverb

song = Song(title="Lo-fi Study", bpm=78, sample_rate=44100)

r = Note.rest

# Rhodes-style chords - jazzy and warm
keys = song.add_track(Track(name="keys", instrument="piano", volume=0.4, pan=-0.1, swing=0.12))
for root, shape in [("Eb", "maj7"), ("Cm", "min7"), ("Ab", "maj7"), ("Bb", "dom7")] * 6:
    keys.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# Bass - simple and round
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5, swing=0.1))
for root in ["Eb", "C", "Ab", "Bb"] * 6:
    bass.extend([Note(root, 2, 1.5), r(0.5), Note(root, 3, 0.5), r(0.5), Note(root, 2, 1.0)])

# Melody - pentatonic wandering, lots of space
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.35, pan=0.2))
phrase = [
    Note("Eb", 5, 0.5),
    Note("G", 5, 1.0),
    r(1.5),
    Note("Bb", 5, 0.5),
    Note("Ab", 5, 1.0),
    r(2.0),
    Note("G", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("C", 5, 1.5),
    r(1.5),
    Note("Bb", 4, 0.5),
    Note("Eb", 5, 1.5),
    r(2.0),
]
mel.extend(phrase * 6)

# Drums - laid back
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7, swing=0.1))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5, swing=0.12))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3, swing=0.15))
for _ in range(24):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), Note("C", 2, 1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, 0.5, velocity=35)] * 8)

song.effects = {
    "keys": EffectsChain().add(lowpass, cutoff_hz=3500.0).add(reverb, room_size=0.5, wet=0.2),
    "melody": EffectsChain().add(lowpass, cutoff_hz=4000.0).add(reverb, room_size=0.4, wet=0.15),
}
