"""Violin tremolo: rapid bowing on a sustained chord, tension builder."""

from code_music import Note, Song, Track

song = Song(title="violin_tremolo", bpm=140)
# Tremolo = rapid repeated 16th notes on same pitch
vln1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.6, pan=-0.3))
vln2 = song.add_track(Track(name="vln2", instrument="violin", volume=0.55, pan=0.3))

for pitch, oct in [("B", 5), ("G", 5), ("E", 5), ("D", 5)]:
    vln1.extend([Note(pitch, oct, 0.25)] * 8)  # two bars tremolo each
for pitch, oct in [("G", 4), ("E", 4), ("C", 4), ("B", 3)]:
    vln2.extend([Note(pitch, oct, 0.25)] * 8)
