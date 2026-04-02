"""Smooth Curves — smoothstep automation creates organic volume envelopes."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.automation import Automation

# Smoothstep creates S-curves instead of linear ramps
vol_smooth = Automation([(0, 0.0), (4, 0.9), (12, 0.9), (16, 0.0)], mode="smoothstep")
vol_linear = Automation([(0, 0.0), (4, 0.9), (12, 0.9), (16, 0.0)], mode="linear")

# Compare at midpoint of fade-in
print(f"Linear at beat 2: {vol_linear.value_at(2):.3f}")
print(f"Smoothstep at beat 2: {vol_smooth.value_at(2):.3f}")

song = Song(title="Smooth Curves", bpm=90, sample_rate=44100)

tr_strings = song.add_track(Track(name="strings", instrument="pad", volume=0.4))
tr_strings.add(Chord("E", "min7", 3, duration=4.0))
tr_strings.add(Chord("C", "maj7", 3, duration=4.0))
tr_strings.add(Chord("A", "min7", 3, duration=4.0))
tr_strings.add(Chord("B", "min7", 3, duration=4.0))

tr_piano = song.add_track(Track(name="piano", instrument="piano", volume=0.45))
melody = [
    ("E", 5, 1.0),
    ("G", 5, 0.5),
    ("B", 5, 1.5),
    ("A", 5, 1.0),
    ("G", 5, 0.5),
    ("F#", 5, 0.5),
    ("E", 5, 1.0),
    ("D", 5, 0.5),
    ("E", 5, 1.5),
    ("G", 5, 1.0),
    ("A", 5, 1.0),
    ("B", 5, 1.5),
    ("A", 5, 1.0),
    ("G", 5, 0.5),
    ("E", 5, 1.0),
    ("B", 4, 1.5),
]
for n, o, d in melody:
    tr_piano.add(Note(n, o, d))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["E", "C", "A", "B"]:
    tr_bass.add(Note(root, 2, 4.0))

song.effects = {"strings": EffectsChain().add(reverb, room_size=0.75, wet=0.35)}
