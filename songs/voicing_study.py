"""Voicing Study — same progression in close, spread, drop-2, and rootless voicings."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import generate_chord_voicing

song = Song(title="Voicing Study", bpm=80, sample_rate=44100)
for voicing in ["close", "spread", "drop2", "rootless"]:
    tr = song.add_track(Track(name=f"v_{voicing}", instrument="piano", volume=0.4))
    for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7")]:
        tr.extend(generate_chord_voicing(root, shape, voicing=voicing))
song.effects = {f"v_close": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
