"""Scale Reference — prints info about common scales."""

from code_music import Song, Track, scale
from code_music.theory import scale_info

for s in ["major", "minor", "dorian", "pentatonic", "blues"]:
    info = scale_info(s, "C")
    print(f"{s}: {' '.join(info['notes'])} | fits: {', '.join(info['chord_fits'][:5])}")
song = Song(title="Scale Reference", bpm=100, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    scale("C", "major", octave=5, length=8)
)
song.effects = {}
