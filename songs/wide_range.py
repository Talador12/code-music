"""Wide Range — melody spanning 3 octaves with range analysis."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import note_range

melody = [
    Note(n, o, 0.5)
    for n, o in [
        ("C", 3),
        ("G", 3),
        ("C", 4),
        ("E", 4),
        ("G", 4),
        ("C", 5),
        ("E", 5),
        ("G", 5),
        ("C", 6),
        ("G", 5),
        ("E", 5),
        ("C", 5),
        ("G", 4),
        ("E", 4),
        ("C", 4),
        ("C", 3),
    ]
]
r = note_range(melody)
print(f"Range: {r['lowest']} → {r['highest']} ({r['span_octaves']} octaves)")
song = Song(title="Wide Range", bpm=90, sample_rate=44100)
song.add_track(Track(name="melody", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
