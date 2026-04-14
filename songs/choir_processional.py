"""Choir Processional - formant choir voices in a cathedral setting."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.effects import room_reverb
from code_music.sound_design import choir_ah, choir_oo, ethereal_voice

song = Song(title="Choir Processional", bpm=66, sample_rate=44100)
song.register_instrument("choir_ah", choir_ah)
song.register_instrument("choir_oo", choir_oo)
song.register_instrument("ethereal_voice", ethereal_voice)

# Soprano choir (ah)
soprano = song.add_track(Track(name="soprano", instrument="choir_ah", volume=0.45, pan=0.15))
soprano.extend(scale("C", "major", octave=5, length=8))

# Alto choir (oo)
alto = song.add_track(Track(name="alto", instrument="choir_oo", volume=0.4, pan=-0.15))
for root in ["C", "E", "F", "G", "A", "G", "F", "E"]:
    alto.add(Note(root, 4, 2.0, velocity=50))

# Tenor (ethereal)
tenor = song.add_track(Track(name="tenor", instrument="ethereal_voice", volume=0.35))
for root, shape in [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")] * 2:
    tenor.add(Chord(root, shape, 3, duration=4.0, velocity=40))

# Organ drone
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.2))
organ.add(Chord("C", "maj", 2, duration=16.0, velocity=35))

song.effects = {
    "soprano": EffectsChain().add(
        room_reverb, width=15, depth=25, height=12, absorption=0.1, wet=0.4
    ),
    "alto": EffectsChain().add(room_reverb, width=15, depth=25, height=12, absorption=0.1, wet=0.4),
    "tenor": EffectsChain().add(reverb, room_size=0.9, wet=0.45),
}
