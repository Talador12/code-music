"""Full Report — song with comprehensive analysis output."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import analyze_song

song = Song(title="Full Report", bpm=120, sample_rate=44100, key_sig="Am")
song.add_track(Track(name="pad", instrument="pad", volume=0.4)).extend(
    [
        Chord("A", "min7", 3, duration=4.0),
        Chord("D", "min7", 3, duration=4.0),
        Chord("G", "dom7", 3, duration=4.0),
        Chord("C", "maj7", 3, duration=4.0),
    ]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["A", "C", "E", "G", "F", "D", "G", "B", "E", "G", "B", "D", "C", "E", "G", "C"]
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(n, 2, 4.0) for n in ["A", "D", "G", "C"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
report = analyze_song(song)
for k, v in report.items():
    if k not in ("arrangement", "harmony"):
        print(f"  {k}: {v}")
