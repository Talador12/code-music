"""SATB Chorale — four-part voice leading through a hymn-like progression."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import voice_lead_satb

song = Song(title="SATB Chorale", bpm=72)

# Classic chorale progression
prog = [
    ("C", "maj"),
    ("A", "min"),
    ("F", "maj"),
    ("G", "dom7"),
    ("C", "maj"),
    ("D", "min"),
    ("G", "dom7"),
    ("C", "maj"),
]

voicings = voice_lead_satb(prog, key="C")

# Soprano
soprano = song.add_track(Track(name="soprano", instrument="triangle", volume=0.5, pan=0.2))
for v in voicings:
    soprano.add(v[0])

# Alto
alto = song.add_track(Track(name="alto", instrument="triangle", volume=0.4, pan=0.1))
for v in voicings:
    alto.add(v[1])

# Tenor
tenor = song.add_track(Track(name="tenor", instrument="organ", volume=0.35, pan=-0.1))
for v in voicings:
    tenor.add(v[2])

# Bass
bass = song.add_track(Track(name="bass", instrument="organ", volume=0.4, pan=-0.2))
for v in voicings:
    bass.add(v[3])

song.effects = {
    "soprano": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "alto": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "tenor": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "bass": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
}
