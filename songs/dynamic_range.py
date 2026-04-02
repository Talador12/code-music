"""Dynamic Range — classical-inspired piece showcasing the full LUFS metering system."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.mastering import measure_lufs

song = Song(title="Dynamic Range", bpm=72, sample_rate=44100)

# Quiet strings section
tr_str = song.add_track(Track(name="strings", instrument="pad", volume=0.3))
tr_str.add(Chord("C", "min", 3, duration=4.0))
tr_str.add(Chord("Eb", "maj", 3, duration=4.0))
tr_str.add(Chord("Ab", "maj", 3, duration=4.0))
tr_str.add(Chord("G", "dom7", 3, duration=4.0))

# Piano melody
tr_piano = song.add_track(Track(name="piano", instrument="piano", volume=0.5))
melody = [
    ("C", 5, 1.0),
    ("Eb", 5, 0.5),
    ("G", 5, 1.5),
    ("Ab", 5, 1.0),
    ("G", 5, 0.5),
    ("F", 5, 0.5),
    ("Eb", 5, 1.0),
    ("D", 5, 0.5),
    ("C", 5, 1.5),
    ("Bb", 4, 1.0),
    ("C", 5, 2.0),
    ("Eb", 5, 1.0),
    ("D", 5, 1.0),
    ("C", 5, 1.0),
    ("Bb", 4, 1.0),
]
for n, o, d in melody:
    tr_piano.add(Note(n, o, d))

# Bass
tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
for root in ["C", "Eb", "Ab", "G"]:
    tr_bass.add(Note(root, 2, 4.0))

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "piano": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
