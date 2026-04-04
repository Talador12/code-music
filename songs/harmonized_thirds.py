"""Harmonized Thirds — melody with auto-generated diatonic thirds harmony."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import harmonize_melody

song = Song(title="Harmonized Thirds", bpm=110)

melody = [
    Note("C", 5, 1.0),
    Note("D", 5, 0.5),
    Note("E", 5, 0.5),
    Note("F", 5, 1.0),
    Note("G", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("E", 5, 1.0),
    Note("D", 5, 1.0),
    Note("C", 5, 2.0),
]

voices = harmonize_melody(melody, key="C", style="thirds")

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(voices[0])

harmony = song.add_track(Track(name="harmony", instrument="sawtooth", volume=0.4, pan=-0.15))
harmony.extend(voices[1])

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
pad.add(Chord("C", "maj", 3, duration=8.0))
pad.add(Chord("F", "maj", 3, duration=4.0))

song.effects = {
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.15, wet=0.1),
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
