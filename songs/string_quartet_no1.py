"""String Quartet No. 1 — auto-arranged from melody + harmony via string_quartet()."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import string_quartet

song = Song(title="String Quartet No. 1", bpm=72)

# Melody
melody = [
    Note("E", 5, 2.0),
    Note("D", 5, 2.0),
    Note("C", 5, 2.0),
    Note("D", 5, 2.0),
    Note("E", 5, 2.0),
    Note("F", 5, 2.0),
    Note("G", 5, 2.0),
    Note("E", 5, 2.0),
    Note("A", 5, 2.0),
    Note("G", 5, 2.0),
    Note("F", 5, 2.0),
    Note("E", 5, 2.0),
    Note("D", 5, 2.0),
    Note("C", 5, 2.0),
    Note("D", 5, 2.0),
    Note("C", 5, 4.0),
]

# Harmony
harmony = [
    ("C", "maj"),
    ("G", "maj"),
    ("A", "min"),
    ("F", "maj"),
    ("C", "maj"),
    ("F", "maj"),
    ("G", "dom7"),
    ("C", "maj"),
]

parts = string_quartet(melody, harmony, key="C", duration=4.0)

vln1 = song.add_track(Track(name="vln1", instrument="sawtooth", volume=0.45, pan=0.3))
vln1.extend(parts["violin_1"])

vln2 = song.add_track(Track(name="vln2", instrument="sawtooth", volume=0.4, pan=0.15))
vln2.extend(parts["violin_2"])

vla = song.add_track(Track(name="viola", instrument="triangle", volume=0.38, pan=-0.15))
vla.extend(parts["viola"])

vc = song.add_track(Track(name="cello", instrument="bass", volume=0.45, pan=-0.3))
vc.extend(parts["cello"])

song.effects = {
    "vln1": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "vln2": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "viola": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
    "cello": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
