"""Jazz comping: ii-V-I in C, shell voicings with piano, swung 8ths."""

from code_music import Chord, Song, Track

song = Song(title="jazz_comping", bpm=160)
# Piano comp track — slightly swung
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.7, swing=0.5))
# ii-V-I x2 then turnaround
pattern = [
    Chord("D", "min7", 3, duration=2.0),
    Chord("G", "dom7", 3, duration=2.0),
    Chord("C", "maj7", 3, duration=2.0),
    Chord("A", "min7", 3, duration=2.0),
]
for _ in range(2):
    comp.extend(pattern)
