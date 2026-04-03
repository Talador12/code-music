"""Lead Sheet Demo — song designed to produce a clean ASCII lead sheet."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import to_lead_sheet

song = Song(title="Lead Sheet Demo", bpm=120, sample_rate=44100, key_sig="Dm")

tr_pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]:
    tr_pad.add(Chord(root, shape, 3, duration=4.0))

tr_lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
for n in ["D", "F", "A", "C", "B", "D", "G", "F", "E", "G", "C", "B", "A", "C", "E", "G"]:
    tr_lead.add(Note(n, 5, 1.0))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["D", "G", "C", "A"]:
    tr_bass.add(Note(root, 2, 4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(to_lead_sheet(song))
