"""FM Bells - metallic bell tones from FM synthesis."""

from code_music import Note, Song, SoundDesigner, Track

fm_bell = (
    SoundDesigner("fm_bell_custom")
    .fm("sine", mod_ratio=1.414, mod_index=8.0, volume=0.6)
    .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.3)
    .envelope(attack=0.001, decay=0.8, sustain=0.1, release=1.0)
    .filter("lowpass", cutoff=8000, resonance=0.2)
)

song = Song(title="FM Bells", bpm=72, sample_rate=44100)
song.register_instrument("fm_bell_custom", fm_bell)

bell = song.add_track(Track(name="bell", instrument="fm_bell_custom", volume=0.5))
for note in ["C", "E", "G", "C", "B", "G", "E", "C"]:
    bell.add(Note(note, 5, 2.0, velocity=60))

# Low bell
low = song.add_track(Track(name="low_bell", instrument="fm_bell_custom", volume=0.4, pan=-0.2))
for note in ["C", "G", "C", "G"]:
    low.add(Note(note, 3, 4.0, velocity=50))
