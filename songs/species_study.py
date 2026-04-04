"""Species Study — species 1 and 2 counterpoint against a cantus firmus."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import species_counterpoint

song = Song(title="Species Study", bpm=60)

# Cantus firmus — a simple whole-note melody
cf = [
    Note("C", 4, 4.0),
    Note("D", 4, 4.0),
    Note("F", 4, 4.0),
    Note("E", 4, 4.0),
    Note("G", 4, 4.0),
    Note("A", 4, 4.0),
    Note("G", 4, 4.0),
    Note("C", 4, 4.0),
]

# Species 1: note-against-note above CF
cp1 = species_counterpoint(cf, species=1, above=True, seed=42)

# Species 2: two-against-one below CF
cp2 = species_counterpoint(cf, species=2, above=False, seed=99)

cf_track = song.add_track(Track(name="cantus", instrument="organ", volume=0.45, pan=0.0))
cf_track.extend(cf)

s1_track = song.add_track(Track(name="species1", instrument="triangle", volume=0.4, pan=0.2))
s1_track.extend(cp1)

s2_track = song.add_track(Track(name="species2", instrument="bass", volume=0.4, pan=-0.2))
s2_track.extend(cp2)

song.effects = {
    "cantus": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "species1": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "species2": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
