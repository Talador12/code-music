"""electro_swing.py — Electro swing. Cm, 128 BPM. Parov Stelar meets Caravan Palace.

Vintage swing samples over modern electronic beats. Uses Track.loop for the
repeating brass riff and Section.repeat for structure.

Style: Electro swing, Cm, 128 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, compress, reverb

song = Song(title="Electro Swing", bpm=128)
r = Note.rest

verse = Section("verse", bars=4)
verse.add_track("kick", [Note("C", 2, 1.0)] * 16)
verse.add_track("snare", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
verse.add_track("hat", [Note("F#", 6, 0.33), Note("F#", 6, 0.33), Note("F#", 6, 0.34)] * 16)
verse.add_track("bass", [Note("C", 2, 0.5), Note("C", 2, 0.5), Note("Eb", 2, 0.5), Note("G", 2, 0.5),
                          Note("Ab", 2, 0.5), Note("G", 2, 0.5), Note("Eb", 2, 0.5), Note("C", 2, 0.5)] * 2)
verse.add_track("brass", [r(0.5), Note("C", 5, 0.5), Note("Eb", 5, 0.5), r(0.5),
                           Note("G", 5, 0.5), Note("Eb", 5, 0.5), Note("C", 5, 1.0)] * 2)
verse.add_track("pad", [Chord("C", "min", 3, duration=8.0), Chord("Ab", "maj", 3, duration=8.0)])

chorus = Section("chorus", bars=4)
chorus.add_track("kick", [Note("C", 2, 1.0)] * 16)
chorus.add_track("snare", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
chorus.add_track("hat", [Note("F#", 6, 0.25)] * 64)
chorus.add_track("bass", [Note("Ab", 2, 0.5), Note("Ab", 2, 0.5), Note("Bb", 2, 0.5), Note("C", 3, 0.5),
                           Note("Eb", 3, 0.5), Note("C", 3, 0.5), Note("Bb", 2, 0.5), Note("Ab", 2, 0.5)] * 2)
chorus.add_track("brass", [Note("C", 5, 0.5), Note("Eb", 5, 0.5), Note("G", 5, 0.5), Note("C", 6, 0.5),
                            Note("Bb", 5, 1.0), Note("G", 5, 1.0)] * 2 + [Note("C", 6, 2.0), r(2.0)])
chorus.add_track("pad", [Chord("Ab", "maj", 3, duration=4.0), Chord("Bb", "maj", 3, duration=4.0),
                          Chord("C", "min", 3, duration=4.0), Chord("G", "dom7", 3, duration=4.0)])

song.arrange(
    [*verse.repeat(2), *chorus.repeat(2), *verse.repeat(2), *chorus.repeat(3)],
    instruments={"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat",
                 "bass": "bass", "brass": "sawtooth", "pad": "pad"},
    volumes={"kick": 0.75, "snare": 0.5, "hat": 0.3, "bass": 0.6, "brass": 0.5, "pad": 0.25},
)

song.effects = {
    "brass": EffectsChain().add(reverb, room_size=0.4, wet=0.15).add(compress, threshold=0.5, ratio=3.0),
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
