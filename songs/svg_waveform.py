"""SVG Waveform — song with visual waveform output."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import to_svg_waveform

song = Song(title="SVG Waveform", bpm=120, sample_rate=44100)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0) * 2
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("C", "min7", 3, duration=8.0), Chord("G", "dom7", 3, duration=8.0)]
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
svg = to_svg_waveform(song)
print(f"SVG: {len(svg)} chars")
