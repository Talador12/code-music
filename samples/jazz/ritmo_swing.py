"""Swing rhythm section: full big-band rhythm, 4/4 at 200 BPM."""

from code_music import Chord, Note, Song, Track

song = Song(title="swing_rhythm_section", bpm=200)
r = Note.rest

# Guitar comp (organ stand-in) — Freddie Green chop chords
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.55, swing=0.55, pan=-0.3))
for root, shape in [("G", "maj"), ("C", "dom7"), ("G", "maj"), ("D", "dom7")] * 2:
    comp.add(Chord(root, shape, 3, duration=1.0, velocity=0.6))

# Walking bass
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.85, pan=0.0))
walk = [
    Note("G", 2, 1.0),
    Note("A", 2, 1.0),
    Note("B", 2, 1.0),
    Note("C", 3, 1.0),
    Note("C", 3, 1.0),
    Note("A", 2, 1.0),
    Note("F#", 2, 1.0),
    Note("G", 2, 1.0),
] * 2
bass.extend(walk)

# Hi-hat + ride
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4, swing=0.55))
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.45, swing=0.55))
snare = song.add_track(Track(name="snr", instrument="drums_snare", volume=0.65))
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))

for _ in range(4):
    hat.extend([Note("F", 5, 0.5)] * 8)
    ride.extend([Note("F", 5, 0.5), Note("F", 5, 0.25), Note("F", 5, 0.25)] * 2)
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(1.5)])
