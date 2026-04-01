"""Formant vowels: synthesized vocal vowels A, O, E on a melody.

The formant presets apply bandpass resonator filters in the vowel frequency
regions, making the synth 'speak' the vowel shapes.
"""

from code_music import Note, Song, Track, reverb

song = Song(title="formant_vowels", bpm=90)

# Same melody, different vowel shapes
for vowel, pan_v in [("formant_a", -0.4), ("formant_o", 0.0), ("formant_e", 0.4)]:
    tr = song.add_track(Track(name=vowel, instrument=vowel, volume=0.7, pan=pan_v))
    tr.extend(
        [
            Note("A", 3, 1.0),
            Note("C", 4, 1.0),
            Note("E", 4, 2.0),
            Note("G", 4, 1.0),
            Note("E", 4, 1.0),
            Note("C", 4, 2.0),
            Note("A", 3, 4.0),
        ]
    )

song.effects = {
    "formant_a": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2),
    "formant_o": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2),
    "formant_e": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2),
}
