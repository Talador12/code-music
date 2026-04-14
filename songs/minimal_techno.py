"""minimal_techno.py - Repetitive minimal techno with evolving filter. Berlin style."""

from code_music import Chord, EffectsChain, Note, Song, Track, highpass, lowpass, reverb

song = Song(title="Minimal Techno", bpm=128, sample_rate=44100)

r = Note.rest

# Kick - four on the floor
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
for _ in range(64):
    kick.add(Note("C", 2, 1.0, velocity=85))

# Hi-hat - offbeat
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(64):
    hat.extend([r(0.5), Note("F", 5, 0.5, velocity=35)])

# Bass - minimal two-note loop in Am
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_loop = [
    Note("A", 2, 0.5),
    r(0.5),
    Note("A", 2, 0.25),
    Note("A", 2, 0.25),
    r(0.5),
    Note("E", 2, 0.5),
    r(0.5),
    Note("A", 2, 0.5),
    r(0.5),
]
bass.extend(bass_loop * 16)

# Stab - short chord hits, sparse
stab = song.add_track(Track(name="stab", instrument="square", volume=0.3, pan=0.1))
stab_pat = [r(2.0), Chord("A", "min", 4, duration=0.25, velocity=50), r(1.75)]
stab.extend(stab_pat * 16)

# Pad - slow evolving texture
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2, pan=-0.15))
for root, shape in [("A", "min7"), ("F", "maj7"), ("A", "min7"), ("E", "min7")] * 4:
    pad.add(Chord(root, shape, 4, duration=4.0, velocity=25))

song.effects = {
    "bass": lambda s, sr: lowpass(s, sr, cutoff_hz=800.0),
    "stab": EffectsChain().add(highpass, cutoff_hz=500.0).add(reverb, room_size=0.6, wet=0.3),
    "pad": EffectsChain().add(reverb, room_size=0.75, wet=0.4),
}
