"""Auto Arrangement — arrangement detection labels song sections."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import generate_arrangement

song = Song(title="Auto Arrangement", bpm=128, sample_rate=44100)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    [Note("C", 2, 1.0) for _ in range(16)]
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("A", "min7", 3, duration=8.0), Chord("F", "maj7", 3, duration=8.0)]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["A", "C", "E", "G", "F", "E", "C", "A", "G", "A", "C", "E", "D", "C", "A", "G"]
    ]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
for s in generate_arrangement(song):
    print(
        f"  Bars {s['start_bar']}-{s['end_bar']}: {s['label']} ({len(s['tracks_active'])} tracks)"
    )
