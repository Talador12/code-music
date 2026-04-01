"""two_step_garage.py — UK Garage / 2-step. Cm, 130 BPM. South London shuffle.

Skippy 2-step drum pattern, deep sub bass, chopped vocal-style chords,
and a bright garage lead. MJ Cole / Artful Dodger territory.

Style: UK Garage, Cm, 130 BPM.
"""

from code_music import Chord, Note, Song, Track, delay, lowpass, reverb

song = Song(title="Two Step Garage", bpm=130)

r = Note.rest

# ── Drums — 2-step shuffle ───────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))

for _ in range(16):
    # 2-step: kick on 1, ghost on the &-of-2, skip beat 3
    kick.extend(
        [Note("C", 2, 1.0), r(0.5), Note("C", 2, 0.5, velocity=0.5), r(1.0), Note("C", 2, 1.0)]
    )
    # Snare on 2 and 4 (but 4 is swung late)
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.5), Note("E", 4, 0.5)])
    # Hats: syncopated shuffle
    hat.extend(
        [
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.5),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.25),
            r(0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
        ]
    )

# ── Sub bass — deep and round ────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="sine", volume=0.65, pan=0.0))
bass_prog = [
    Note("C", 2, 2.0),
    Note("C", 2, 1.0),
    r(1.0),
    Note("Eb", 2, 2.0),
    Note("Eb", 2, 1.0),
    r(1.0),
    Note("Ab", 1, 2.0),
    Note("Ab", 1, 1.0),
    r(1.0),
    Note("Bb", 1, 2.0),
    Note("G", 2, 1.0),
    r(1.0),
]
for _ in range(4):
    bass.extend(bass_prog)

# ── Chords — chopped organ stabs ─────────────────────────────────────────
chords = song.add_track(Track(name="chords", instrument="organ", volume=0.35, pan=0.15))
chord_riff = [
    r(0.5),
    Chord("C", "min7", 4, duration=0.5),
    r(0.5),
    Chord("C", "min7", 4, duration=0.5),
    r(0.5),
    Chord("Eb", "maj7", 3, duration=0.5),
    r(1.0),
    r(0.5),
    Chord("Ab", "maj", 3, duration=0.5),
    r(0.5),
    Chord("Bb", "dom7", 3, duration=0.5),
    r(0.5),
    Chord("G", "min", 3, duration=0.5),
    r(1.0),
]
for _ in range(4):
    chords.extend(chord_riff)

# ── Lead — bright garage melody ──────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="square", volume=0.4, pan=0.2))
lead_phrase = [
    r(16.0),  # sit out first 4 bars
    Note("Eb", 5, 0.5),
    Note("G", 5, 0.5),
    Note("Bb", 5, 0.5),
    r(0.5),
    Note("C", 6, 1.0),
    Note("Bb", 5, 0.5),
    Note("G", 5, 0.5),
    Note("Ab", 5, 1.0),
    Note("G", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F", 5, 1.0),
    Note("Eb", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Eb", 5, 2.0),
    r(6.0),
]
for _ in range(4):
    lead.extend(lead_phrase)

song.effects = {
    "bass": lambda s, sr: lowpass(s, sr, cutoff_hz=200),
    "chords": lambda s, sr: delay(
        reverb(s, sr, room_size=0.4, wet=0.2), sr, delay_ms=250, feedback=0.2, wet=0.15
    ),
    "lead": lambda s, sr: delay(s, sr, delay_ms=187.5, feedback=0.25, wet=0.2),
}
