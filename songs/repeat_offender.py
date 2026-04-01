"""repeat_offender.py — Showcases Section.repeat() for concise arrangement.

A pop-rock structure built entirely from Section.repeat():
  Intro → Verse ×2 → Chorus ×2 → Bridge → Chorus ×3 → Outro

No manual duplication — the chorus is defined once and repeated.

Style: Pop-rock, C major, 128 BPM.
"""

from code_music import Chord, EffectsChain, Note, Section, Song, compress, reverb

song = Song(title="Repeat Offender", bpm=128)

r = Note.rest

# ── Sections ──────────────────────────────────────────────────────────────

intro = Section("intro", bars=4)
intro.add_track("guitar", [Chord("C", "maj", 3, duration=16.0)])
intro.add_track(
    "bass", [Note("C", 2, 4.0), Note("G", 2, 4.0), Note("A", 2, 4.0), Note("F", 2, 4.0)]
)
intro.add_track("drums_k", [r(16.0)])
intro.add_track("drums_s", [r(16.0)])
intro.add_track("lead", [r(16.0)])

verse = Section("verse", bars=4)
verse.add_track(
    "guitar",
    [
        Chord("C", "maj", 3, duration=4.0),
        Chord("A", "min", 3, duration=4.0),
        Chord("F", "maj", 3, duration=4.0),
        Chord("G", "maj", 3, duration=4.0),
    ],
)
verse.add_track(
    "bass", [Note("C", 2, 4.0), Note("A", 2, 4.0), Note("F", 2, 4.0), Note("G", 2, 4.0)]
)
verse.add_track("drums_k", [Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)] * 4)
verse.add_track("drums_s", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
verse.add_track(
    "lead",
    [
        Note("E", 5, 0.5),
        Note("G", 5, 0.5),
        Note("C", 5, 1.0),
        r(2.0),
        Note("A", 4, 0.5),
        Note("C", 5, 0.5),
        Note("E", 5, 1.0),
        r(2.0),
        Note("F", 5, 1.0),
        Note("E", 5, 0.5),
        Note("D", 5, 0.5),
        r(2.0),
        Note("G", 5, 2.0),
        r(2.0),
    ],
)

chorus = Section("chorus", bars=4)
chorus.add_track(
    "guitar",
    [
        Chord("F", "maj", 3, duration=4.0),
        Chord("G", "maj", 3, duration=4.0),
        Chord("A", "min", 3, duration=4.0),
        Chord("C", "maj", 3, duration=4.0),
    ],
)
chorus.add_track(
    "bass", [Note("F", 2, 4.0), Note("G", 2, 4.0), Note("A", 2, 4.0), Note("C", 2, 4.0)]
)
chorus.add_track("drums_k", [Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)] * 4)
chorus.add_track("drums_s", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
chorus.add_track(
    "lead",
    [
        Note("C", 6, 1.0),
        Note("A", 5, 1.0),
        Note("G", 5, 1.0),
        Note("F", 5, 1.0),
        Note("G", 5, 2.0),
        Note("E", 5, 2.0),
        Note("A", 5, 1.0),
        Note("G", 5, 1.0),
        Note("F", 5, 1.0),
        Note("E", 5, 1.0),
        Note("C", 5, 2.0),
        r(2.0),
    ],
)

bridge = Section("bridge", bars=4)
bridge.add_track("guitar", [Chord("D", "min", 3, duration=8.0), Chord("E", "min", 3, duration=8.0)])
bridge.add_track("bass", [Note("D", 2, 8.0), Note("E", 2, 8.0)])
bridge.add_track("drums_k", [r(16.0)])
bridge.add_track("drums_s", [r(16.0)])
bridge.add_track(
    "lead", [Note("D", 5, 4.0), Note("E", 5, 4.0), Note("F", 5, 4.0), Note("G", 5, 4.0)]
)

outro = Section("outro", bars=4)
outro.add_track("guitar", [Chord("C", "maj", 3, duration=16.0)])
outro.add_track("bass", [Note("C", 2, 8.0), r(8.0)])
outro.add_track("drums_k", [Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)] * 4)
outro.add_track("drums_s", [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)] * 4)
outro.add_track("lead", [r(16.0)])

# ── Arrange with repeat ───────────────────────────────────────────────────

song.arrange(
    [intro, *verse.repeat(2), *chorus.repeat(2), bridge, *chorus.repeat(3), outro],
    instruments={
        "guitar": "pluck",
        "bass": "bass",
        "lead": "sawtooth",
        "drums_k": "drums_kick",
        "drums_s": "drums_snare",
    },
    volumes={"guitar": 0.4, "bass": 0.6, "lead": 0.5, "drums_k": 0.7, "drums_s": 0.5},
)

for i, track in enumerate(song.tracks):
    if track.name == "lead":
        song.tracks[i] = track.fade_out(beats=16.0)

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "lead": EffectsChain()
    .add(reverb, room_size=0.5, wet=0.2)
    .add(compress, threshold=0.5, ratio=3.0),
}
