"""HTML Export — generates a standalone HTML page for the song."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import to_html

song = Song(title="HTML Export", bpm=120, sample_rate=44100, key_sig="C")
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [Note(n, 5, 1.0) for n in ["C", "E", "G", "B", "A", "G", "E", "C"]]
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("C", "maj7", 3, duration=4.0), Chord("A", "min7", 3, duration=4.0)]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note("C", 2, 4.0), Note("A", 2, 4.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
html = to_html(song)
print(f"Generated {len(html)} chars of HTML")
