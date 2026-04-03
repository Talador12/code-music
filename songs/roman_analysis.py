"""Roman Analysis — song with full harmonic analysis output."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import analyze_harmony

song = Song(title="Roman Analysis", bpm=100, sample_rate=44100, key_sig="D")
song.add_track(Track(name="pad", instrument="pad", volume=0.4)).extend(
    [
        Chord("D", "min7", 3, duration=4.0),
        Chord("G", "dom7", 3, duration=4.0),
        Chord("C", "maj7", 3, duration=4.0),
        Chord("A", "min7", 3, duration=4.0),
    ]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["D", "F", "A", "C", "B", "D", "G", "F", "E", "G", "C", "B", "A", "C", "E", "G"]
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(n, 2, 4.0) for n in ["D", "G", "C", "A"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
for a in analyze_harmony(song, key="C"):
    print(f"  {a['roman']}{a['quality']} ({a['function']})")
