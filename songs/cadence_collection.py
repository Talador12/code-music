"""Cadence Collection — authentic, plagal, and deceptive cadences."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import deceptive_cadence, plagal_cadence, secondary_dominant

dec = deceptive_cadence("C")
plag = plagal_cadence("C")
sec_dom = secondary_dominant("D")  # V/ii
print(f"Deceptive: {dec}")
print(f"Plagal: {plag}")
print(f"Secondary dominant of D: {sec_dom}")
song = Song(title="Cadence Collection", bpm=80, sample_rate=44100)
tr = song.add_track(Track(name="chords", instrument="piano", volume=0.5))
for r, s in dec + plag + [sec_dom, ("D", "min7")]:
    tr.add(Chord(r, s, 4, duration=2.0))
song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.15)).extend(
    [Note(n, 5, 1.0) for n in "G B D F A C E G F A C E D F A D".split()]
)
song.effects = {"chords": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
