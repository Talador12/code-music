"""Summary Showcase — prints a pretty song summary."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import song_summary

song = Song(title="Summary Showcase", bpm=128, sample_rate=44100, key_sig="Cm")
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    [Note("C", 2, 1.0) for _ in range(16)]
)
song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3)).extend(
    [Note("F#", 6, 0.5) for _ in range(32)]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(euclid(5, 16, "C", 2, 1.0))
song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.1)).extend(
    [Chord("C", "min7", 3, duration=8.0), Chord("Ab", "maj7", 3, duration=8.0)]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in [
            "C",
            "Eb",
            "G",
            "Bb",
            "Ab",
            "G",
            "Eb",
            "C",
            "Bb",
            "Ab",
            "Eb",
            "Bb",
            "G",
            "Eb",
            "C",
            "Bb",
        ]
    ]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(song_summary(song))
