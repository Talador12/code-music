"""Italian Sixth Waltz — augmented sixth chords in 3/4 time."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import augmented_sixth

song = Song(title="Italian Sixth Waltz", bpm=108, time_sig=(3, 4))

# Waltz bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5, pan=-0.1))
for _ in range(2):
    bass.add(Note("A", 2, 1.0))
    bass.add(Note("E", 3, 0.5))
    bass.add(Note("E", 3, 0.5))
    bass.add(Note("A", 2, 1.0))
    # Italian sixth resolves to V
    bass.extend([Note("F", 2, 1.0), Note("C", 3, 0.5), Note("C", 3, 0.5), Note("E", 2, 1.0)])

# Harmony — Italian augmented sixths
harm = song.add_track(Track(name="harmony", instrument="organ", volume=0.4, pan=0.1))
for _ in range(2):
    harm.add(Chord("A", "min", 3, duration=3.0))
    harm.add(Chord("A", "min", 3, duration=3.0))
    harm.extend(augmented_sixth("A", "italian", octave=3, duration=3.0))
    harm.add(Chord("E", "maj", 3, duration=3.0))

# Melody — elegant waltz line
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.55, pan=0.2))
for _ in range(2):
    mel.extend([Note("C", 5, 1.0), Note("B", 4, 0.5), Note("A", 4, 0.5), Note("E", 5, 1.0)])
    mel.extend([Note("A", 5, 1.0), Note("G", 5, 0.5), Note("F", 5, 0.5), Note("E", 5, 1.0)])
    mel.extend([Note("F", 4, 1.0), Note("C", 5, 1.0), Note("F#", 4, 1.0)])
    mel.extend([Note("G#", 4, 1.0), Note("B", 4, 1.0), Note("E", 5, 1.0)])

song.effects = {
    "harmony": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "melody": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
