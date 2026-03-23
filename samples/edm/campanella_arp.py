"""FM bell arpeggio: frequency-modulated metallic tones in D major."""

from code_music import Chord, Song, Track, arp

song = Song(title="fm_bell_arp", bpm=110)
tr = song.add_track(Track(name="bell", instrument="fm_bell", volume=0.75, pan=0.0))
for chord_root, shape in [("D", "maj7"), ("B", "min7"), ("G", "maj7"), ("A", "dom7")] * 2:
    tr.extend(arp(Chord(chord_root, shape, 4), pattern="up", rate=0.25, octaves=2))
