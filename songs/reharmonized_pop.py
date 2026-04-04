"""Reharmonized Pop — I-V-vi-IV jazzed up via reharmonize()."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import reharmonize

song = Song(title="Reharmonized Pop", bpm=110)

# Original pop progression
original = [("G", "maj"), ("D", "maj"), ("E", "min"), ("C", "maj")]

# Jazz reharmonization
jazz = reharmonize(original * 2, key="G", style="jazz")

# Play both: original then reharmonized
comp = song.add_track(Track(name="comp", instrument="piano", volume=0.45, pan=0.1))
for root, shape in original:
    comp.add(Chord(root, shape, 3, duration=4.0))
for root, shape in jazz:
    comp.add(Chord(root, shape, 3, duration=4.0))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in original:
    bass.add(Note(root, 2, 4.0))
for root, _ in jazz:
    bass.add(Note(root, 2, 4.0))

song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
