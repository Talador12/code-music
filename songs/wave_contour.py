"""Wave Contour — sine-wave melodic shape over chord changes."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import generate_chord_melody

prog = [("A", "min7"), ("F", "maj7"), ("C", "maj7"), ("G", "dom7")]
melody = generate_chord_melody(prog, contour="wave", octave=5, notes_per_chord=8, seed=77)
song = Song(title="Wave Contour", bpm=100, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord(r, s, 3, duration=8.0) for r, s in prog]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
