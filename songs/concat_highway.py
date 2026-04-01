"""concat_highway.py — Showcases Track.concat() for building long tracks from parts.

A progressive rock piece where each instrument is built by concatenating
distinct musical sections: intro riff → main theme → solo → reprise.

Style: Progressive rock, Am, 136 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Concat Highway", bpm=136)

r = Note.rest

# ── Build bass from concatenated sections ─────────────────────────────────
bass_intro = Track(name="bass", instrument="bass", volume=0.6)
for _ in range(4):
    bass_intro.extend([Note("A", 2, 1.0), Note("E", 2, 0.5), Note("A", 2, 0.5), r(2.0)])

bass_main = Track(name="bass", instrument="bass", volume=0.6)
for _ in range(8):
    bass_main.extend(
        [
            Note("A", 2, 0.5),
            Note("A", 2, 0.5),
            Note("C", 3, 0.5),
            Note("E", 3, 0.5),
            Note("D", 3, 0.5),
            Note("C", 3, 0.5),
            Note("A", 2, 0.5),
            Note("E", 2, 0.5),
        ]
    )

bass_solo = Track(name="bass", instrument="bass", volume=0.6)
for _ in range(4):
    bass_solo.extend([Note("A", 2, 2.0), Note("G", 2, 2.0)])

song.add_track(
    bass_intro.fade_in(4.0).concat(bass_main).concat(bass_solo).concat(bass_main.fade_out(8.0))
)

# ── Build guitar from concatenated sections ───────────────────────────────
guitar_intro = Track(name="guitar", instrument="pluck", volume=0.45, pan=0.2)
guitar_intro.extend([Chord("A", "min", 3, duration=16.0)])

guitar_main = Track(name="guitar", instrument="pluck", volume=0.45, pan=0.2)
for _ in range(4):
    guitar_main.extend(
        [
            Chord("A", "min", 3, duration=4.0),
            Chord("F", "maj", 3, duration=4.0),
        ]
    )

guitar_solo_backing = Track(name="guitar", instrument="pluck", volume=0.45, pan=0.2)
for _ in range(2):
    guitar_solo_backing.extend(
        [
            Chord("A", "min7", 3, duration=4.0),
            Chord("G", "maj", 3, duration=4.0),
        ]
    )

song.add_track(
    guitar_intro.concat(guitar_main).concat(guitar_solo_backing).concat(guitar_main.fade_out(8.0))
)

# ── Build lead from concatenated sections ─────────────────────────────────
lead_rest = Track(name="lead", instrument="sawtooth", volume=0.5, pan=-0.15)
lead_rest.add(r(16.0))

lead_theme = Track(name="lead", instrument="sawtooth", volume=0.5, pan=-0.15)
lead_phrase = [
    Note("A", 5, 0.5),
    Note("C", 6, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 1.0),
    Note("A", 4, 1.0),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
    Note("C", 6, 1.0),
    Note("B", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 1.0),
]
for _ in range(4):
    lead_theme.extend(lead_phrase)

lead_solo = Track(name="lead", instrument="sawtooth", volume=0.5, pan=-0.15)
solo_notes = [
    Note("E", 6, 0.25),
    Note("D", 6, 0.25),
    Note("C", 6, 0.25),
    Note("B", 5, 0.25),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 0.25),
    Note("B", 5, 0.25),
    Note("C", 6, 0.25),
    Note("D", 6, 0.25),
    Note("E", 6, 1.0),
]
for _ in range(4):
    lead_solo.extend(solo_notes)

song.add_track(lead_rest.concat(lead_theme).concat(lead_solo).concat(lead_theme.fade_out(8.0)))

# ── Drums — simple steady pattern ────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
total_bars = 28  # 4 intro + 8 main + 4 solo + 8 main + 4 outro-ish
for _ in range(total_bars):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "lead": EffectsChain()
    .add(delay, delay_ms=220, feedback=0.25, wet=0.18)
    .add(reverb, room_size=0.45, wet=0.15),
}
