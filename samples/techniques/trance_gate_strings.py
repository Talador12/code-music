"""Trance gated strings: classic euphoric trance texture on pad layer."""

from code_music import Chord, Song, Track, gate, reverb, stereo_width

song = Song(title="trance_gate_strings", bpm=138)

pad = song.add_track(Track(name="pad", instrument="strings", volume=0.65, pan=-0.1))
for chord in [
    Chord("A", "min7", 3, duration=4.0),
    Chord("F", "maj7", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("G", "dom7", 3, duration=4.0),
]:
    for _ in range(2):
        pad.add(chord)

song._effects = {
    "pad": lambda s, sr: stereo_width(
        gate(reverb(s, sr, room_size=0.5, wet=0.2), sr, rate_hz=4.0, shape="trapezoid", duty=0.5),
        width=1.6,
    ),
}
