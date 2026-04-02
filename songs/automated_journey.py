"""Automated Journey — parameter automation shapes every moment."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.automation import Automation

vol = Automation([(0, 0.0), (4, 0.8), (12, 0.8), (16, 0.0)])
print(f"Volume curve: {vol}")
print(f"Start: {vol.value_at(0):.2f}, Peak: {vol.value_at(4):.2f}, End: {vol.value_at(16):.2f}")

song = Song(title="Automated Journey", bpm=110, sample_rate=44100)

tr_pad = song.add_track(Track(name="pad", instrument="pad", volume=0.5, pan=-0.15))
tr_pad.add(Chord("D", "min7", 3, duration=8.0))
tr_pad.add(Chord("Bb", "maj7", 3, duration=8.0))

tr_lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
for n in ["D", "F", "A", "C", "Bb", "A", "F", "D", "C", "D", "F", "A", "G", "F", "D", "C"]:
    tr_lead.add(Note(n, 5, 1.0))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["D", "D", "Bb", "Bb"]:
    tr_bass.add(Note(root, 2, 4.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
