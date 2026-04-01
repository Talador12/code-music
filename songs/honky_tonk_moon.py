"""honky_tonk_moon.py — Country. G major, 112 BPM. Pedal steel and twang.

A straightforward country shuffle with a walking bass, chicken-picked
lead over a I-IV-V-I progression. Think early 90s Garth Brooks.

Structure: Intro (2 bars) → Verse (8 bars) → Chorus (8 bars) × 2 → Outro (4 bars)
"""

from code_music import Chord, Note, Section, Song, reverb, slapback

song = Song(title="Honky Tonk Moon", bpm=112)

r = Note.rest

# ── Sections ───────────────────────────────────────────────────────────────

intro = Section("intro", bars=2)
intro.add_track(
    "steel",
    [
        Note("G", 4, 2.0),
        Note("B", 4, 1.0),
        Note("D", 5, 1.0),
        Note("G", 5, 2.0),
        r(2.0),
    ],
)
intro.add_track("bass", [Note("G", 2, 4.0), Note("D", 2, 4.0)])
intro.add_track("rhythm", [r(8.0)])
intro.add_track("kick", [r(8.0)])
intro.add_track("snare", [r(8.0)])

verse = Section("verse", bars=8)
verse_chords = [
    Chord("G", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("D", "maj", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
    Chord("D", "dom7", 3, duration=4.0),
]
verse.add_track("rhythm", verse_chords)
verse.add_track(
    "bass",
    [
        Note("G", 2, 2.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("G", 2, 2.0),
        Note("D", 2, 2.0),
        Note("C", 2, 2.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("C", 2, 2.0),
        Note("G", 2, 2.0),
        Note("D", 2, 2.0),
        Note("F#", 2, 1.0),
        Note("A", 2, 1.0),
        Note("C", 2, 2.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("G", 2, 2.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("D", 2, 2.0),
        Note("A", 2, 1.0),
        Note("D", 2, 1.0),
    ],
)
verse.add_track(
    "steel",
    [
        Note("B", 4, 1.0),
        Note("D", 5, 0.5),
        Note("G", 5, 0.5),
        r(2.0),
        Note("G", 4, 1.0),
        Note("A", 4, 0.5),
        Note("B", 4, 0.5),
        r(2.0),
        Note("E", 5, 1.0),
        Note("C", 5, 0.5),
        Note("G", 4, 0.5),
        r(2.0),
        Note("C", 5, 1.0),
        r(3.0),
        Note("D", 5, 1.0),
        Note("F#", 5, 0.5),
        Note("A", 5, 0.5),
        r(2.0),
        Note("E", 5, 1.0),
        Note("C", 5, 1.0),
        r(2.0),
        Note("B", 4, 2.0),
        Note("G", 4, 2.0),
        Note("A", 4, 1.0),
        Note("D", 5, 1.0),
        r(2.0),
    ],
)
drum_bar = [Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)]
snare_bar = [r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)]
verse.add_track("kick", drum_bar * 8)
verse.add_track("snare", snare_bar * 8)

chorus = Section("chorus", bars=8)
chorus_chords = [
    Chord("C", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
    Chord("D", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
    Chord("C", "maj", 3, duration=4.0),
    Chord("D", "dom7", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
    Chord("G", "maj", 3, duration=4.0),
]
chorus.add_track("rhythm", chorus_chords)
chorus.add_track(
    "bass",
    [
        Note("C", 2, 2.0),
        Note("E", 2, 1.0),
        Note("G", 2, 1.0),
        Note("G", 2, 2.0),
        Note("B", 2, 1.0),
        Note("D", 3, 1.0),
        Note("D", 2, 2.0),
        Note("F#", 2, 1.0),
        Note("A", 2, 1.0),
        Note("G", 2, 2.0),
        Note("D", 2, 2.0),
        Note("C", 2, 2.0),
        Note("G", 2, 2.0),
        Note("D", 2, 2.0),
        Note("A", 2, 1.0),
        Note("D", 2, 1.0),
        Note("G", 2, 4.0),
        Note("G", 2, 2.0),
        Note("D", 2, 2.0),
    ],
)
chorus.add_track(
    "steel",
    [
        Note("E", 5, 2.0),
        Note("G", 5, 2.0),
        Note("B", 5, 2.0),
        Note("G", 5, 1.0),
        Note("D", 5, 1.0),
        Note("A", 5, 2.0),
        Note("F#", 5, 1.0),
        Note("D", 5, 1.0),
        Note("G", 5, 4.0),
        Note("E", 5, 1.0),
        Note("C", 5, 1.0),
        Note("G", 4, 2.0),
        Note("D", 5, 2.0),
        Note("A", 4, 2.0),
        Note("B", 4, 2.0),
        Note("G", 4, 2.0),
        Note("G", 4, 2.0),
        r(2.0),
    ],
)
chorus.add_track("kick", drum_bar * 8)
chorus.add_track("snare", snare_bar * 8)

outro = Section("outro", bars=4)
outro.add_track("rhythm", [Chord("G", "maj", 3, duration=16.0)])
outro.add_track("bass", [Note("G", 2, 8.0), r(8.0)])
outro.add_track("steel", [Note("G", 5, 4.0), Note("D", 5, 4.0), Note("G", 4, 8.0)])
outro.add_track("kick", drum_bar * 4)
outro.add_track("snare", snare_bar * 4)

# ── Arrange ────────────────────────────────────────────────────────────────

song.arrange(
    [intro, verse, chorus, verse, chorus, outro],
    instruments={
        "steel": "triangle",
        "bass": "bass",
        "rhythm": "pluck",
        "kick": "drums_kick",
        "snare": "drums_snare",
    },
    volumes={
        "steel": 0.55,
        "bass": 0.6,
        "rhythm": 0.4,
        "kick": 0.7,
        "snare": 0.5,
    },
    pans={"steel": 0.3, "bass": -0.1, "rhythm": -0.2, "kick": 0.0, "snare": 0.05},
)

for i, track in enumerate(song.tracks):
    if track.name == "steel":
        song.tracks[i] = track.fade_in(beats=4.0)

song._effects = {
    "steel": lambda s, sr: slapback(reverb(s, sr, room_size=0.5, wet=0.2), sr, wet=0.15),
    "rhythm": lambda s, sr: reverb(s, sr, room_size=0.3, wet=0.1),
}
