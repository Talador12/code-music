"""Generative melody: procedurally generated melodies in different modes.

Uses generate_melody() to create melodies from scratch. Each run with a
different seed produces a different melody. Good for inspiration.
"""

from code_music import Song, Track, generate_melody, reverb

song = Song(title="generative_melody", bpm=108)

# Three generated melodies in different modes over the same progression
modes = [("major", -0.3, 0), ("dorian", 0.0, 42), ("pentatonic", 0.3, 7)]
for mode, pan_v, seed in modes:
    tr = song.add_track(Track(name=f"mel_{mode}", instrument="piano", volume=0.65, pan=pan_v))
    mel = generate_melody("A", scale_mode=mode, octave=4, bars=8, density=0.65, seed=seed)
    tr.extend(mel)

song._effects = {
    "mel_major": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.15),
    "mel_dorian": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.15),
    "mel_pentatonic": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.15),
}
