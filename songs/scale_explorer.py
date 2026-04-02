"""Scale Explorer — uses chord_scale() to pick melodies that fit each chord."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.theory import chord_scale

song = Song(title="Scale Explorer", bpm=100, sample_rate=44100)
prog = [("A", "min7"), ("D", "dom7"), ("G", "maj7"), ("C", "maj7")]

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=8.0))

# Map theory scale names to engine SCALES keys
_SCALE_MAP = {
    "aeolian": "minor",
    "mixolydian": "dorian",
    "lydian": "major",
    "phrygian": "minor",
    "locrian": "minor",
}

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
for root, shape in prog:
    scales = chord_scale(root, shape)
    chosen = scales[0] if scales else "major"
    engine_name = _SCALE_MAP.get(chosen, chosen)
    lead.extend(scale(root, engine_name, octave=5, length=8))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root, _ in prog:
    for _ in range(8):
        bass.add(Note(root, 2, 1.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
