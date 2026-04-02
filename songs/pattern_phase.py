"""Pattern Phase — Steve Reich-inspired phasing from the Pattern language."""

from code_music import EffectsChain, Pattern, Song, Track, reverb

song = Song(title="Pattern Phase", bpm=130, sample_rate=44100)

# Two identical patterns, one rotated — creates phase shift over time
base = Pattern("C5 E5 G5 B5 A5 G5 E5 D5")
shifted = base.rotate(1)  # offset by one step

# Layer them: same melody, one step apart
tr_a = song.add_track(Track(name="piano_a", instrument="piano", volume=0.5, pan=-0.3))
tr_b = song.add_track(Track(name="piano_b", instrument="piano", volume=0.5, pan=0.3))

# 4 repetitions each
for _ in range(4):
    tr_a.extend(base.to_notes(0.5))
    tr_b.extend(shifted.to_notes(0.5))

# Degraded ghost layer
sparse = base.degrade(0.3, seed=42).fast(2)
tr_ghost = song.add_track(Track(name="ghost", instrument="pad", volume=0.25))
tr_ghost.extend(sparse.to_notes(0.5))

# Polymeter bass (3 vs 4)
bass_3 = Pattern("C3 E3 G3")
bass_4 = Pattern("A2 C3 E3 G3")
poly_bass = Pattern.polymeter(bass_3, bass_4)
tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for _ in range(3):
    tr_bass.extend(poly_bass.to_notes(0.5))

song.effects = {
    "ghost": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "piano_a": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
}
