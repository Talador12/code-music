"""bossa_sunset.py - Bossa nova with gentle guitar and melody. Ipanema vibes."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Bossa Sunset", bpm=130, sample_rate=44100)

r = Note.rest

# Nylon guitar chords - bossa rhythm
gtr = song.add_track(Track(name="guitar", instrument="pluck", volume=0.45, pan=-0.15))
prog = [
    ("F", "maj7", 4.0),
    ("G", "dom7", 4.0),
    ("A", "min7", 4.0),
    ("D", "min7", 4.0),
    ("G", "min7", 4.0),
    ("C", "dom7", 4.0),
    ("F", "maj7", 4.0),
    ("E", "dom7", 4.0),
]
for root, shape, dur in prog * 3:
    gtr.add(Chord(root, shape, 3, duration=dur, velocity=45))

# Bass - root movement, bossa feel
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5, swing=0.1))
for root, _, _ in prog * 3:
    bass.extend([Note(root, 2, 1.5), Note(root, 3, 0.5), r(0.5), Note(root, 2, 1.0), r(0.5)])

# Melody - smooth and lyrical
mel = song.add_track(Track(name="melody", instrument="sine", volume=0.4, pan=0.2))
phrase = [
    Note("A", 4, 1.0),
    Note("C", 5, 0.5),
    Note("F", 5, 1.5),
    r(1.0),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 1.0),
    Note("A", 4, 1.5),
    r(0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("C", 5, 1.0),
    r(1.0),
    Note("F", 5, 1.0),
    Note("E", 5, 0.5),
    Note("D", 5, 1.0),
    Note.rest(1.5),
]
mel.extend(phrase * 6)

# Light percussion - shaker
shaker = song.add_track(Track(name="shaker", instrument="drums_hat", volume=0.2))
for _ in range(48):
    shaker.extend([Note("C", 6, 0.5, velocity=30), Note("C", 6, 0.5, velocity=20)])

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "melody": EffectsChain().add(delay, delay_ms=230.0, feedback=0.2, wet=0.15),
}
