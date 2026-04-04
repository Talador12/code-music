"""Wave Melody — generated melody with sinusoidal contour in A minor."""

from code_music import Chord, EffectsChain, Song, Track, delay, reverb
from code_music.theory import generate_scale_melody

song = Song(title="Wave Melody", bpm=88)

# Wave contour melody — the pitch rises and falls like a breath
wave = generate_scale_melody(
    key="A",
    scale_name="minor",
    length=48,
    octave=5,
    duration=0.5,
    contour="wave",
    seed=77,
)

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.5, pan=0.1))
lead.extend(wave)

# Harmonic bed
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.15))
pad.add(Chord("A", "min7", 3, duration=8.0))
pad.add(Chord("F", "maj7", 3, duration=8.0))
pad.add(Chord("D", "min7", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=375, feedback=0.25, wet=0.2),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
