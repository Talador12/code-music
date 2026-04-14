"""Spectral Blend - cross-synthesis blends two instruments together."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.effects import cross_synthesis

song = Song(title="Spectral Blend", bpm=90, sample_rate=44100)

# Source: piano melody (provides pitch and timing)
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.5, pan=0.15))
piano.extend(scale("F", "major", octave=4, length=16))

# Target: pad wash (provides spectral character)
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
for root, shape in [("F", "maj7"), ("Bb", "maj7"), ("C", "dom7"), ("F", "maj7")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# The cross-synthesis blend (applied as effect: piano timbre + pad spectrum)
blend = song.add_track(Track(name="blend", instrument="piano", volume=0.45))
blend.extend(scale("F", "major", octave=5, length=16))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["F", "F", "Bb", "Bb", "C", "C", "F", "F"]:
    bass.add(Note(root, 2, 2.0, velocity=60))

# Apply cross-synthesis: the blend track gets the pad's spectrum applied to it
song.effects = {
    "blend": lambda samples, sr: cross_synthesis(
        samples,
        samples * 0.5,  # self-modulate for spectral smearing
        sr,
        fft_size=2048,
        blend=0.6,
        wet=0.7,
    ),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
}
