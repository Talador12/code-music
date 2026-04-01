"""prog_metal.py — Progressive metal. Bm, 148 BPM, 5/4 time. Tool meets Meshuggah.

Odd-meter riffing in 5/4 with heavy palm-muted chugging, complex drum patterns,
and a soaring melodic bridge. Uses Section.repeat for the verse-chorus structure.

Style: Progressive metal, Bm, 5/4 time, 148 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, compress, distortion, reverb

song = Song(title="Prog Metal", bpm=148, time_sig=(5, 4))
r = Note.rest
BAR = 5.0

verse = Section("verse", bars=4)
verse.add_track("guitar", [
    Note("B", 2, 0.25), Note("B", 2, 0.25), r(0.25), Note("B", 2, 0.25),
    Note("D", 3, 0.25), Note("B", 2, 0.25), r(0.25), Note("E", 3, 0.25),
    Note("B", 2, 0.5), Note("F#", 3, 0.5),
] * 4)
verse.add_track("bass", [Note("B", 1, 2.5), Note("D", 2, 2.5)] * 4)
verse.add_track("kick", ([Note("C", 2, 0.5), r(0.25), Note("C", 2, 0.25),
                          r(0.5), Note("C", 2, 0.5), r(0.5),
                          Note("C", 2, 0.25), r(0.25), Note("C", 2, 0.5), r(0.5)] * 4))
verse.add_track("snare", [r(1.25), Note("E", 4, 0.5), r(1.75), Note("E", 4, 0.5), r(1.0)] * 4)
verse.add_track("lead", [r(20.0)])

chorus = Section("chorus", bars=4)
chorus.add_track("guitar", [
    Chord("B", "min", 3, duration=2.5), Chord("G", "maj", 3, duration=2.5),
    Chord("D", "maj", 3, duration=2.5), Chord("A", "maj", 3, duration=2.5),
])
chorus.add_track("bass", [Note("B", 1, 5.0), Note("G", 1, 5.0), Note("D", 2, 5.0), Note("A", 1, 5.0)])
chorus.add_track("kick", [Note("C", 2, 1.25)] * 16)
chorus.add_track("snare", [r(1.25), Note("E", 4, 1.25), r(1.25), Note("E", 4, 1.25)] * 4)
chorus.add_track("lead", [
    Note("F#", 5, 1.0), Note("B", 5, 1.0), Note("A", 5, 0.5), Note("G", 5, 0.5), Note("F#", 5, 2.0),
    Note("B", 5, 1.0), Note("D", 6, 1.0), Note("A", 5, 1.0), r(2.0),
    Note("G", 5, 1.5), Note("F#", 5, 1.0), Note("E", 5, 1.0), Note("D", 5, 1.5),
    Note("B", 4, 2.5), r(2.5),
])

song.arrange(
    [*verse.repeat(2), *chorus.repeat(2), *verse.repeat(2), *chorus.repeat(3)],
    instruments={"guitar": "sawtooth", "bass": "bass", "kick": "drums_kick", "snare": "drums_snare", "lead": "sawtooth"},
    volumes={"guitar": 0.55, "bass": 0.6, "kick": 0.8, "snare": 0.55, "lead": 0.5},
    pans={"guitar": -0.2, "lead": 0.2},
)

song.effects = {
    "guitar": EffectsChain().add(distortion, drive=3.5, tone=0.4, wet=0.5).add(compress, threshold=0.4, ratio=5.0),
    "lead": EffectsChain().add(reverb, room_size=0.45, wet=0.18),
}
