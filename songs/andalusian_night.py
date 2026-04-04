"""Andalusian Night — flamenco-flavored piece using the Andalusian cadence."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import andalusian_cadence

song = Song(title="Andalusian Night", bpm=100)

# Andalusian cadence in A minor: Am - G - F - E
prog = andalusian_cadence("A")

# Nylon guitar chords (using pluck for that flamenco snap)
guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.5, pan=-0.1))
for _ in range(4):
    for root, shape in prog:
        guitar.add(Chord(root, shape, 3, duration=2.0))

# Bass — following the descending pattern
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(4):
    bass.extend([Note("A", 2, 2.0), Note("G", 2, 2.0), Note("F", 2, 2.0), Note("E", 2, 2.0)])

# Phrygian melody — the sound of flamenco
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=0.2))
phrygian_melody = [
    Note("A", 5, 0.5),
    Note("Bb", 5, 0.5),
    Note("C", 6, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 1.0),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 2.0),
]
for _ in range(4):
    lead.extend(phrygian_melody)

# Cajón (using kick for flamenco rhythm)
cajon = song.add_track(Track(name="cajon", instrument="drums_kick", volume=0.4))
for _ in range(16):
    cajon.extend([Note("C", 2, 1.0), Note("C", 2, 0.5), Note.rest(0.5)])

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.15, wet=0.15),
}
