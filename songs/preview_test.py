"""Preview Test — demonstrates fast render_preview for quick iteration."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import render_preview

song = Song(title="Preview Test", bpm=120, sample_rate=44100)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0) * 2
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).add(
    Chord("C", "min7", 3, duration=16.0)
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
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
preview = render_preview(song)
print(f"Preview: {len(preview)} samples (11025Hz mono)")
print(f"Full would be: ~{int(song.duration_sec * 44100 * 2)} samples (44100Hz stereo)")
