"""Extended Chords — 9th/11th/13th extensions on a jazz progression."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import chord_extensions

song = Song(title="Extended Chords", bpm=90, sample_rate=44100)
tr = song.add_track(Track(name="piano", instrument="piano", volume=0.45))
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]:
    tr.extend(chord_extensions(root, shape, ["9"]))
song.effects = {"piano": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
