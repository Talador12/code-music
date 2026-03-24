"""slow_burn_suite.py — R&B slow jam. Ebm, 65 BPM. 90s quiet storm territory.

Silk, not satin. The tempo where everything moves like honey.
Rhodes with tremolo, contrabass pizzicato, brushed snare at whisper
volume. The melody never rushes. The chords are all extended — min9,
maj7, dom9. Nothing is plain. Babyface, Boyz II Men, SWV, Sade.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    PolyphonicTrack,
    Song,
    Track,
    chorus,
    conv_reverb,
    humanize,
    reverb,
    tremolo,
)

song = Song(title="Slow Burn Suite", bpm=65, key_sig="Eb")

BAR = 4.0
r = Note.rest
SWING = 0.5

# ── PolyphonicTrack Rhodes — sustained chords + melodic fills ──────────────
rhodes = song.add_polytrack(
    PolyphonicTrack(name="rhodes", instrument="rhodes", volume=0.68, pan=-0.1)
)

# Sustained chord bed — each voice placed independently
chords_data = [
    # Ebm9: Eb Gb Bb Db F
    [
        ("D#", 3, WHOLE * 2, 0.0, 0.5),
        ("F#", 3, WHOLE * 2, 0.0, 0.45),
        ("A#", 3, WHOLE * 2, 0.0, 0.42),
        ("C#", 4, WHOLE * 2, 0.0, 0.40),
        ("F", 4, WHOLE * 2, 0.0, 0.38),
    ],
    # Cbmaj7: Cb Eb Gb Bb
    [
        ("B", 2, WHOLE * 2, BAR * 2, 0.5),
        ("D#", 3, WHOLE * 2, BAR * 2, 0.45),
        ("F#", 3, WHOLE * 2, BAR * 2, 0.42),
        ("A#", 3, WHOLE * 2, BAR * 2, 0.40),
    ],
    # Gbmaj7: Gb Bb Db F
    [
        ("F#", 2, WHOLE * 2, BAR * 4, 0.5),
        ("A#", 3, WHOLE * 2, BAR * 4, 0.45),
        ("C#", 4, WHOLE * 2, BAR * 4, 0.42),
        ("F", 4, WHOLE * 2, BAR * 4, 0.40),
    ],
    # Db9: Db F Ab Cb Eb
    [
        ("C#", 2, WHOLE * 2, BAR * 6, 0.52),
        ("F", 3, WHOLE * 2, BAR * 6, 0.47),
        ("G#", 3, WHOLE * 2, BAR * 6, 0.44),
        ("B", 3, WHOLE * 2, BAR * 6, 0.42),
        ("D#", 4, WHOLE * 2, BAR * 6, 0.40),
    ],
]
for chord_notes in chords_data * 2:
    for pitch, oct, dur, at, vel in chord_notes:
        rhodes.add(Note(pitch, oct, dur, velocity=vel), at=at)

# Melodic fills floating above
fills = [
    (BAR + 2.0, "D#", 5, HALF, 0.6),
    (BAR + 3.5, "C#", 5, QUARTER, 0.55),
    (BAR * 3 + 1.0, "F#", 5, DOTTED_QUARTER, 0.58),
    (BAR * 3 + 3.0, "D#", 5, QUARTER, 0.52),
    (BAR * 5 + 2.0, "A#", 5, HALF, 0.62),
    (BAR * 7 + 0.0, "F#", 5, DOTTED_QUARTER, 0.55),
    (BAR * 7 + 2.5, "D#", 5, QUARTER, 0.50),
]
for at, p, o, dur, vel in fills:
    rhodes.add(Note(p, o, dur, velocity=vel), at=at)

# ── Pizzicato bass — gentle plucks ────────────────────────────────────────
bass = song.add_track(
    Track(name="bass", instrument="contrabass", volume=0.68, pan=0.05, swing=SWING)
)
bass_line = humanize(
    [
        Note("D#", 2, HALF),
        r(QUARTER),
        Note("F#", 2, QUARTER),
        Note("B", 1, HALF),
        r(QUARTER),
        Note("D#", 2, QUARTER),
        Note("F#", 2, HALF),
        r(QUARTER),
        Note("A#", 2, QUARTER),
        Note("C#", 2, HALF),
        r(HALF),
    ]
    * 4,
    vel_spread=0.06,
    timing_spread=0.03,
)
bass.extend(bass_line)

# ── Brushed kit — barely there ─────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.35, swing=SWING))
for _ in range(16):
    snare.extend(
        [r(1.0), Note("D", 3, 1.0, velocity=0.3), r(1.0), Note("D", 3, 1.0, velocity=0.28)]
    )

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.2, swing=SWING))
hat.extend([Note("F", 5, EIGHTH, velocity=0.2)] * (16 * 8))

song._effects = {
    "rhodes": lambda s, sr: tremolo(
        conv_reverb(chorus(s, sr, rate_hz=0.4, wet=0.15), sr, room="chamber", wet=0.28),
        sr,
        rate_hz=4.5,
        depth=0.12,
    ),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.15),
}
