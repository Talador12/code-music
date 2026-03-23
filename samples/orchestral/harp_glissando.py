"""Harp glissando: ascending C major scale sweep, then rolled chords."""

from code_music import Chord, Song, Track, scale

song = Song(title="harp_glissando", bpm=80)
tr = song.add_track(Track(name="harp", instrument="harp", volume=0.8))

# Ascending glissando — fast 16th notes
gliss = scale("C", "major", octave=3, length=21)  # 3 octaves
for n in gliss:
    n.duration = 0.125
tr.extend(gliss)

# Rolled chords
for chord_root, shape in [("C", "maj7"), ("F", "maj7"), ("G", "dom7"), ("C", "maj")]:
    tr.add(Chord(chord_root, shape, 4, duration=2.0, velocity=0.65))
