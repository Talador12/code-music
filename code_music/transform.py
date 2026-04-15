"""Genre transformation engine.

Convert any piece of music into a different genre, rhythm pattern, or style.
A genre transform is not one operation - it is seven layers that can be
applied independently or together:

    1. Rhythm   - change the feel (straight to swing, shuffle, Latin, etc.)
    2. Harmony  - reharmonize chords for the target genre
    3. Instruments - swap instruments to match the genre
    4. Groove   - apply genre-specific timing/feel template
    5. Articulation - change playing techniques
    6. Dynamics - adjust dynamic range for the genre
    7. Effects  - apply genre-specific effects chain

Example::

    from code_music import Song, Track, Note, Chord, scale
    from code_music.transform import genre_transform, rhythm_transform

    # Build a simple pop song
    song = Song(title="Pop Original", bpm=120)
    # ... add tracks ...

    # Transform to jazz
    jazz = genre_transform(song, "jazz")

    # Transform to bossa nova
    bossa = genre_transform(song, "bossa_nova")

    # Just change the rhythm feel without changing anything else
    swung = rhythm_transform(song, "swing")

    # Chain specific transforms
    from code_music.transform import (
        harmony_transform, instrument_transform, groove_transform,
    )
    custom = groove_transform(
        instrument_transform(
            harmony_transform(song, "jazz"),
            "jazz",
        ),
        "neo_soul",
    )
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Sequence

from .engine import (
    Beat,
    Chord,
    CHORD_SHAPES,
    Note,
    Song,
    Track,
    note_name_to_midi,
    midi_to_note_name,
)


# ---------------------------------------------------------------------------
# Genre profiles - full parameter sets for each target genre
# ---------------------------------------------------------------------------


@dataclass
class GenreProfile:
    """Complete parameter set defining how a genre sounds."""

    name: str
    bpm_range: tuple[int, int] = (100, 130)
    default_bpm: int = 120
    time_sig: tuple[int, int] = (4, 4)
    swing: float = 0.0  # 0.0 = straight, 0.5 = medium swing, 0.67 = hard swing
    groove: str = "straight"
    # Harmony: chord shape substitution map
    harmony_map: dict[str, str] = field(default_factory=dict)
    # Instruments: role -> preset name
    instruments: dict[str, str] = field(default_factory=dict)
    # Panning: role -> pan position
    pans: dict[str, float] = field(default_factory=dict)
    # Volumes: role -> volume level
    volumes: dict[str, float] = field(default_factory=dict)
    # Articulation: role -> default articulation
    articulations: dict[str, str | None] = field(default_factory=dict)
    # Dynamics: velocity range (min, max)
    dynamics_range: tuple[float, float] = (0.3, 0.9)
    # Effects hints (applied during render)
    effects_hints: dict[str, dict] = field(default_factory=dict)


GENRE_PROFILES: dict[str, GenreProfile] = {
    "jazz": GenreProfile(
        name="jazz",
        bpm_range=(110, 180),
        default_bpm=140,
        swing=0.55,
        groove="shuffle",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom9",
            "sus4": "9sus4",
            "dim": "dim7",
            "aug": "aug_maj7",
            "add9": "maj9",
            "min7": "min9",
        },
        instruments={
            "melody": "saxophone",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "rhodes",
        },
        pans={"melody": -0.15, "chords": 0.2, "bass": 0.05, "pad": -0.2},
        volumes={"melody": 0.65, "chords": 0.45, "bass": 0.55, "hat": 0.4},
        articulations={"melody": None, "bass": None, "snare": None},
        dynamics_range=(0.35, 0.85),
    ),
    "blues": GenreProfile(
        name="blues",
        bpm_range=(70, 130),
        default_bpm=110,
        swing=0.5,
        groove="shuffle",
        harmony_map={
            "maj": "dom7",
            "min": "min7",
            "maj7": "dom7",
            "min7": "min7",
            "sus4": "dom7",
            "dim": "dim7",
        },
        instruments={
            "melody": "harmonica",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        pans={"melody": -0.1, "chords": 0.15},
        dynamics_range=(0.4, 0.9),
    ),
    "funk": GenreProfile(
        name="funk",
        bpm_range=(85, 115),
        default_bpm=98,
        swing=0.0,
        groove="funk_tight",
        harmony_map={
            "maj": "dom7",
            "min": "min7_funk",
            "maj7": "dom9",
            "dom7": "dom7#9",
            "min7": "min7_funk",
        },
        instruments={
            "melody": "trumpet",
            "chords": "harpsichord",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.85, "snare": 0.75, "bass": 0.7, "chords": 0.4},
        articulations={"chords": "staccato", "bass": None},
        dynamics_range=(0.45, 0.95),
    ),
    "bossa_nova": GenreProfile(
        name="bossa_nova",
        bpm_range=(120, 160),
        default_bpm=140,
        swing=0.0,
        groove="bossa",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom9",
            "sus4": "6_9",
            "min7": "min6_9",
        },
        instruments={
            "melody": "flute",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "rhodes",
        },
        pans={"melody": -0.2, "chords": 0.2, "pad": -0.15},
        volumes={"melody": 0.5, "chords": 0.4, "bass": 0.5, "snare": 0.3, "hat": 0.25},
        articulations={"snare": "cross_stick"},
        dynamics_range=(0.25, 0.65),
    ),
    "latin_jazz": GenreProfile(
        name="latin_jazz",
        bpm_range=(150, 200),
        default_bpm=180,
        swing=0.0,
        groove="salsa",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom9",
        },
        instruments={
            "melody": "trumpet",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "woodblock",
            "hat": "drums_ride",
            "pad": "timbales",
        },
        volumes={"melody": 0.65, "chords": 0.55, "snare": 0.5},
        dynamics_range=(0.5, 0.95),
    ),
    "big_band": GenreProfile(
        name="big_band",
        bpm_range=(120, 180),
        default_bpm=160,
        swing=0.5,
        groove="big_band",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom13",
        },
        instruments={
            "melody": "trumpet",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "trombone",
        },
        volumes={"melody": 0.7, "pad": 0.55, "hat": 0.4, "kick": 0.3},
        dynamics_range=(0.35, 0.95),
    ),
    "lofi": GenreProfile(
        name="lofi",
        bpm_range=(65, 85),
        default_bpm=75,
        swing=0.0,
        groove="lofi",
        harmony_map={
            "maj": "maj7_open",
            "min": "min7_open",
            "dom7": "dom9",
            "maj7": "maj7_open",
            "min7": "min7_open",
        },
        instruments={
            "melody": "rhodes",
            "chords": "rhodes",
            "bass": "sub_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.4, "chords": 0.35, "bass": 0.45, "hat": 0.2},
        dynamics_range=(0.2, 0.55),
        effects_hints={"melody": {"lofi_vinyl": True}, "chords": {"tape_sat": True}},
    ),
    "neo_soul": GenreProfile(
        name="neo_soul",
        bpm_range=(75, 100),
        default_bpm=85,
        swing=0.0,
        groove="neo_soul",
        harmony_map={
            "maj": "maj9",
            "min": "min9",
            "dom7": "dom9",
            "maj7": "maj9#11",
            "min7": "min11_neo",
        },
        instruments={
            "melody": "saxophone",
            "chords": "rhodes",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.55, "chords": 0.45, "bass": 0.5, "hat": 0.25},
        dynamics_range=(0.3, 0.7),
    ),
    "reggae": GenreProfile(
        name="reggae",
        bpm_range=(70, 95),
        default_bpm=80,
        swing=0.0,
        groove="reggae",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7"},
        instruments={
            "melody": "organ",
            "chords": "organ",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"bass": 0.7, "chords": 0.4, "kick": 0.65},
        dynamics_range=(0.4, 0.8),
    ),
    "classical": GenreProfile(
        name="classical",
        bpm_range=(80, 140),
        default_bpm=108,
        swing=0.0,
        groove="straight",
        harmony_map={
            "dom7": "dom7",
            "min7": "min",
            "maj7": "maj",
            "dom9": "dom7",
            "min9": "min",
            "9sus4": "sus4",
        },
        instruments={
            "melody": "violin",
            "chords": "piano",
            "bass": "cello",
            "pad": "viola",
        },
        pans={"melody": -0.3, "chords": 0.15, "bass": 0.2, "pad": 0.0},
        dynamics_range=(0.2, 0.9),
    ),
    "rock": GenreProfile(
        name="rock",
        bpm_range=(100, 150),
        default_bpm=130,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj7": "power5",
            "min7": "min",
            "dom7": "power5",
            "dom9": "power5",
        },
        instruments={
            "melody": "lead_edm",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"chords": 0.7, "kick": 0.8, "snare": 0.75},
        dynamics_range=(0.5, 0.95),
    ),
    "electronic": GenreProfile(
        name="electronic",
        bpm_range=(118, 140),
        default_bpm=128,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
        },
        instruments={
            "melody": "lead_edm",
            "chords": "pad",
            "bass": "sub_808",
            "kick": "drums_808",
            "snare": "drums_clap",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.9, "bass": 0.7, "chords": 0.4},
        dynamics_range=(0.4, 0.95),
    ),
    "ambient": GenreProfile(
        name="ambient",
        bpm_range=(50, 80),
        default_bpm=65,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "sus4_add9",
            "power5": "sus4_add9",
        },
        instruments={
            "melody": "sine",
            "chords": "ambient_pad",
            "bass": "sub_bass",
            "pad": "glass_pad",
        },
        volumes={"melody": 0.3, "chords": 0.4, "pad": 0.35, "bass": 0.3},
        dynamics_range=(0.1, 0.45),
    ),
    "afrobeat": GenreProfile(
        name="afrobeat",
        bpm_range=(105, 125),
        default_bpm=115,
        swing=0.0,
        groove="afrobeat",
        harmony_map={"maj": "dom7", "min": "min7"},
        instruments={
            "melody": "trumpet",
            "chords": "organ",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.75, "bass": 0.65, "chords": 0.5},
        dynamics_range=(0.5, 0.9),
    ),
    "gospel": GenreProfile(
        name="gospel",
        bpm_range=(80, 130),
        default_bpm=105,
        swing=0.3,
        groove="shuffle",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom9",
            "sus4": "9sus4",
        },
        instruments={
            "melody": "choir_aah",
            "chords": "organ",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        dynamics_range=(0.4, 0.95),
    ),
    "disco": GenreProfile(
        name="disco",
        bpm_range=(115, 135),
        default_bpm=128,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj", "min": "min7"},
        instruments={
            "melody": "strings",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_open_hat",
        },
        volumes={"kick": 0.85, "bass": 0.7, "hat": 0.5},
        dynamics_range=(0.5, 0.9),
    ),
    "bebop": GenreProfile(
        name="bebop",
        bpm_range=(180, 280),
        default_bpm=220,
        swing=0.55,
        groove="swing_heavy",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom7alt",
            "sus4": "min7",
            "dim": "dim7",
        },
        instruments={
            "melody": "saxophone",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
        },
        volumes={"melody": 0.6, "chords": 0.4, "hat": 0.45, "kick": 0.25},
        dynamics_range=(0.35, 0.9),
    ),
    # ── More genres (v170 expansion) ─────────────────────────────────
    "country": GenreProfile(
        name="country",
        bpm_range=(100, 140),
        default_bpm=120,
        swing=0.15,
        groove="shuffle",
        harmony_map={"min": "min", "min7": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "guitar_acoustic",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "violin",
        },
        pans={"melody": -0.2, "chords": 0.2, "pad": 0.3},
        volumes={"melody": 0.6, "pad": 0.35},
        dynamics_range=(0.4, 0.85),
    ),
    "bluegrass": GenreProfile(
        name="bluegrass",
        bpm_range=(120, 200),
        default_bpm=160,
        swing=0.1,
        groove="straight",
        harmony_map={"min7": "min", "dom7": "maj", "maj7": "maj"},
        instruments={
            "melody": "mandolin",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "pad": "banjo_ks",
        },
        pans={"melody": -0.2, "chords": 0.15, "pad": -0.3},
        volumes={"melody": 0.65, "pad": 0.5},
        dynamics_range=(0.45, 0.9),
    ),
    "r&b": GenreProfile(
        name="r&b",
        bpm_range=(80, 110),
        default_bpm=90,
        swing=0.0,
        groove="neo_soul",
        harmony_map={
            "maj": "maj9",
            "min": "min9",
            "dom7": "dom9",
            "maj7": "maj9",
            "sus4": "9sus4",
        },
        instruments={
            "melody": "sine",
            "chords": "rhodes",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.5, "chords": 0.45, "hat": 0.25, "snare": 0.4},
        dynamics_range=(0.3, 0.7),
    ),
    "trap": GenreProfile(
        name="trap",
        bpm_range=(130, 170),
        default_bpm=145,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "min7", "min": "min7", "dom7": "min7"},
        instruments={
            "melody": "lead_edm",
            "chords": "dark_pad",
            "bass": "sub_808",
            "kick": "drums_808",
            "snare": "drums_clap",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.9, "bass": 0.8, "hat": 0.35, "chords": 0.3},
        dynamics_range=(0.4, 0.95),
    ),
    "hiphop": GenreProfile(
        name="hiphop",
        bpm_range=(80, 100),
        default_bpm=90,
        swing=0.0,
        groove="lofi",
        harmony_map={"maj": "min7", "min": "min7", "dom7": "min7"},
        instruments={
            "melody": "piano",
            "chords": "piano",
            "bass": "sub_808",
            "kick": "drums_808",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.85, "bass": 0.75, "hat": 0.3},
        dynamics_range=(0.35, 0.85),
    ),
    "ska": GenreProfile(
        name="ska",
        bpm_range=(140, 180),
        default_bpm=165,
        swing=0.0,
        groove="straight",
        harmony_map={"min7": "min", "dom7": "maj", "maj7": "maj"},
        instruments={
            "melody": "trumpet",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "organ",
        },
        articulations={"chords": "staccato", "snare": "cross_stick"},
        volumes={"chords": 0.55, "melody": 0.6},
        dynamics_range=(0.5, 0.9),
    ),
    # ── Ska variants ─────────────────────────────────────────────────
    "ska_first_wave": GenreProfile(
        # Original Jamaican ska: 1958-1966. Prince Buster, Skatalites.
        # Faster than later waves. Walking bass. Horn-driven melodies.
        # The one that started it all, born from mento + American R&B.
        name="ska_first_wave",
        bpm_range=(150, 200),
        default_bpm=180,
        swing=0.15,
        groove="shuffle",
        harmony_map={"min7": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "trumpet",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "trombone",
        },
        articulations={"chords": "staccato", "snare": "cross_stick"},
        pans={"melody": -0.15, "pad": 0.15, "chords": 0.25},
        volumes={"melody": 0.65, "pad": 0.55, "chords": 0.5, "bass": 0.6},
        dynamics_range=(0.5, 0.9),
    ),
    "ska_2tone": GenreProfile(
        # 2 Tone: 1979-1984. The Specials, Madness, The Selecter, The Beat.
        # Tighter, punkier, angrier. More guitar, less jazz. Coventry.
        # The revival that brought ska to the UK and fused it with punk energy.
        name="ska_2tone",
        bpm_range=(140, 180),
        default_bpm=165,
        swing=0.0,
        groove="straight",
        harmony_map={"min7": "min", "dom7": "maj", "maj7": "maj"},
        instruments={
            "melody": "trumpet",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "organ",
        },
        articulations={"chords": "staccato", "snare": "rimshot"},
        volumes={"chords": 0.6, "melody": 0.6, "kick": 0.7, "snare": 0.65},
        dynamics_range=(0.5, 0.9),
    ),
    "ska_third_wave": GenreProfile(
        # Third wave: 1990s. Reel Big Fish, Less Than Jake, Mighty Mighty Bosstones.
        # Ska-punk hybrid. Faster, louder, distorted guitar between the skanks.
        # The one where everyone in the pit is skanking and the horn section is huge.
        name="ska_third_wave",
        bpm_range=(160, 200),
        default_bpm=180,
        swing=0.0,
        groove="straight",
        harmony_map={
            "min7": "power5",
            "dom7": "power5",
            "maj7": "power5",
            "min": "power5",
            "maj": "power5",
        },
        instruments={
            "melody": "trumpet",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "trombone",
        },
        articulations={"chords": "staccato"},
        volumes={"chords": 0.75, "melody": 0.65, "kick": 0.8, "snare": 0.75, "pad": 0.55},
        dynamics_range=(0.55, 0.95),
    ),
    "ska_punk": GenreProfile(
        # Ska-punk: Operation Ivy, Rancid, Sublime, Streetlight Manifesto.
        # Full punk speed with offbeat guitar and horn breakdowns.
        # The pit at Warped Tour energy.
        name="ska_punk",
        bpm_range=(170, 220),
        default_bpm=195,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj": "power5",
            "min": "power5",
            "dom7": "power5",
            "maj7": "power5",
            "min7": "power5",
        },
        instruments={
            "melody": "trumpet",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "trombone",
        },
        volumes={
            "chords": 0.8,
            "kick": 0.85,
            "snare": 0.8,
            "bass": 0.7,
            "melody": 0.65,
            "pad": 0.55,
        },
        dynamics_range=(0.6, 1.0),
    ),
    "ska_jazz": GenreProfile(
        # Ska-jazz: Skatalites, Hepcat, New York Ska-Jazz Ensemble.
        # Slower, jazzier, more sophisticated harmony. Walking bass.
        # The horn players actually improvise. The drummer knows rudiments.
        name="ska_jazz",
        bpm_range=(130, 170),
        default_bpm=150,
        swing=0.2,
        groove="shuffle",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom9",
            "sus4": "9sus4",
        },
        instruments={
            "melody": "saxophone",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "trombone",
        },
        articulations={"chords": "staccato", "snare": "cross_stick"},
        pans={"melody": -0.2, "pad": 0.15, "chords": 0.25},
        volumes={"melody": 0.6, "pad": 0.5, "chords": 0.45, "bass": 0.55, "hat": 0.4},
        dynamics_range=(0.4, 0.85),
    ),
    "rocksteady": GenreProfile(
        # Rocksteady: 1966-1968. The transition between ska and reggae.
        # Slower than ska, bass becomes the star. Alton Ellis, Desmond Dekker.
        # The brief golden age where the tempo dropped and the groove deepened.
        name="rocksteady",
        bpm_range=(95, 120),
        default_bpm=108,
        swing=0.1,
        groove="reggae",
        harmony_map={"min7": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "trumpet",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "organ",
        },
        articulations={"chords": "staccato", "snare": "cross_stick"},
        volumes={"bass": 0.7, "chords": 0.45, "melody": 0.55},
        dynamics_range=(0.4, 0.8),
    ),
    "dub": GenreProfile(
        # Dub: King Tubby, Lee Perry, Scientist. Reggae through the mixing desk.
        # Heavy bass, echo on everything, instruments drop in and out.
        # The producer is the artist. The reverb is the instrument.
        name="dub",
        bpm_range=(65, 85),
        default_bpm=75,
        swing=0.0,
        groove="reggae",
        harmony_map={"maj": "min7", "min": "min7", "dom7": "min7"},
        instruments={
            "melody": "organ",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        articulations={"chords": "staccato"},
        volumes={"bass": 0.8, "kick": 0.75, "chords": 0.35, "melody": 0.4, "hat": 0.25},
        dynamics_range=(0.3, 0.8),
        effects_hints={"melody": {"delay": True}, "snare": {"delay": True}},
    ),
    "punk": GenreProfile(
        name="punk",
        bpm_range=(160, 220),
        default_bpm=180,
        swing=0.0,
        groove="straight",
        harmony_map={"maj7": "power5", "min7": "power5", "dom7": "power5", "min": "power5"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"chords": 0.8, "kick": 0.85, "snare": 0.8, "bass": 0.7},
        dynamics_range=(0.6, 1.0),
    ),
    "metal": GenreProfile(
        name="metal",
        bpm_range=(120, 200),
        default_bpm=160,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "power5", "min": "power5", "dom7": "power5"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"chords": 0.85, "kick": 0.9, "snare": 0.85, "bass": 0.75},
        dynamics_range=(0.6, 1.0),
    ),
    # ── 2004 Metal variants ──────────────────────────────────────────
    "melodic_metalcore": GenreProfile(
        # THE 2004 sound. Killswitch Engage, As I Lay Dying, All That Remains.
        # Dual guitar harmonies in thirds over chugging rhythm. Clean interludes
        # that make the heavy parts hit harder. Double bass runs. Adam D tone.
        name="melodic_metalcore",
        bpm_range=(130, 180),
        default_bpm=160,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj": "power5",
            "min": "power5",
            "dom7": "power5",
            "maj7": "power5",
            "min7": "power5",
        },
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "sawtooth",
        },
        pans={"melody": -0.35, "pad": 0.35, "chords": -0.15, "bass": 0.0},
        volumes={
            "melody": 0.7,
            "pad": 0.65,
            "chords": 0.8,
            "kick": 0.9,
            "snare": 0.85,
            "bass": 0.7,
            "hat": 0.35,
        },
        dynamics_range=(0.5, 1.0),
    ),
    "nwoahm": GenreProfile(
        # New Wave of American Heavy Metal. Lamb of God, Shadows Fall,
        # Chimaira, God Forbid. Groove-driven, less melody than metalcore,
        # more stomp. Randy Blythe energy. Chris Adler drumming.
        name="nwoahm",
        bpm_range=(120, 170),
        default_bpm=145,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "power5", "min": "power5", "dom7": "power5"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        pans={"melody": -0.3, "chords": 0.3},
        volumes={"chords": 0.85, "kick": 0.9, "snare": 0.85, "bass": 0.75},
        dynamics_range=(0.6, 1.0),
    ),
    "prog_metal": GenreProfile(
        # Dream Theater, Between the Buried and Me, Opeth, Mastodon.
        # Odd time signatures, clean/heavy dynamics, technical riffs,
        # guitar harmony leads. Petrucci tone with more gain.
        name="prog_metal",
        bpm_range=(100, 180),
        default_bpm=140,
        time_sig=(7, 8),
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "power5", "min": "min7", "dom7": "dom7", "maj7": "maj7"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "warm_pad",
        },
        pans={"melody": -0.3, "chords": 0.3, "pad": 0.0},
        volumes={"melody": 0.65, "chords": 0.75, "kick": 0.85, "pad": 0.3, "bass": 0.7},
        dynamics_range=(0.3, 1.0),
    ),
    "post_hardcore": GenreProfile(
        # Thrice, Thursday, Underoath, Saosin, Circa Survive.
        # Clean vocals over heavy riffs. Atmospheric. Emotional.
        # The quiet-loud-quiet structure but with more math.
        name="post_hardcore",
        bpm_range=(120, 170),
        default_bpm=150,
        swing=0.0,
        groove="straight",
        harmony_map={
            "maj": "power5",
            "min": "min7",
            "dom7": "power5",
            "maj7": "maj7",
            "sus4": "sus4_add9",
        },
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "ambient_pad",
        },
        pans={"melody": -0.3, "chords": 0.3, "pad": 0.0},
        volumes={"melody": 0.6, "chords": 0.7, "kick": 0.8, "pad": 0.35, "bass": 0.65},
        dynamics_range=(0.25, 1.0),
    ),
    "djent": GenreProfile(
        # Meshuggah, Periphery, Animals as Leaders, TesseracT.
        # Polyrhythmic chugs, extended range guitars, clean interludes.
        # 8-string territory. The thall.
        name="djent",
        bpm_range=(100, 160),
        default_bpm=130,
        time_sig=(4, 4),
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "power5", "min": "power5", "dom7": "power5"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "glass_pad",
        },
        pans={"melody": -0.35, "chords": 0.35},
        volumes={"chords": 0.9, "kick": 0.9, "snare": 0.8, "bass": 0.8, "pad": 0.25},
        dynamics_range=(0.4, 1.0),
    ),
    "prog_rock": GenreProfile(
        name="prog_rock",
        bpm_range=(90, 160),
        default_bpm=120,
        time_sig=(7, 8),
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "dom9"},
        instruments={
            "melody": "sawtooth",
            "chords": "organ",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "warm_pad",
        },
        volumes={"pad": 0.4, "chords": 0.55},
        dynamics_range=(0.3, 0.95),
    ),
    "synthwave": GenreProfile(
        name="synthwave",
        bpm_range=(100, 120),
        default_bpm=108,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7"},
        instruments={
            "melody": "sync_lead",
            "chords": "warm_pad",
            "bass": "moog_bass",
            "kick": "drums_808",
            "snare": "drums_clap",
            "hat": "drums_hat",
            "pad": "dark_pad",
        },
        volumes={"pad": 0.5, "chords": 0.45, "kick": 0.8, "snare": 0.6},
        dynamics_range=(0.4, 0.85),
    ),
    "vaporwave": GenreProfile(
        name="vaporwave",
        bpm_range=(60, 85),
        default_bpm=72,
        swing=0.0,
        groove="lofi",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "dom9"},
        instruments={
            "melody": "rhodes",
            "chords": "rhodes",
            "bass": "sub_bass",
            "pad": "glass_pad",
        },
        volumes={"melody": 0.35, "chords": 0.3, "pad": 0.35, "bass": 0.35},
        dynamics_range=(0.15, 0.45),
        effects_hints={"melody": {"lofi_vinyl": True, "tape_wow_flutter": True}},
    ),
    "shoegaze": GenreProfile(
        name="shoegaze",
        bpm_range=(90, 130),
        default_bpm=110,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "sus4_add9"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "ambient_pad",
        },
        volumes={"pad": 0.6, "chords": 0.65, "melody": 0.4, "hat": 0.2},
        dynamics_range=(0.3, 0.75),
        effects_hints={"chords": {"shimmer_reverb": True}},
    ),
    "post_rock": GenreProfile(
        name="post_rock",
        bpm_range=(80, 140),
        default_bpm=110,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "sus4_add9"},
        instruments={
            "melody": "guitar_electric",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
            "pad": "ambient_pad",
        },
        volumes={"pad": 0.5, "melody": 0.5},
        dynamics_range=(0.15, 0.95),
    ),
    "house": GenreProfile(
        name="house",
        bpm_range=(118, 130),
        default_bpm=124,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7"},
        instruments={
            "melody": "pluck",
            "chords": "pad",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_clap",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.9, "hat": 0.4, "chords": 0.4, "bass": 0.65},
        dynamics_range=(0.4, 0.9),
    ),
    "techno": GenreProfile(
        name="techno",
        bpm_range=(125, 145),
        default_bpm=135,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "min7", "min": "min7"},
        instruments={
            "melody": "pulse",
            "chords": "dark_pad",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_clap",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.95, "bass": 0.7, "melody": 0.35, "chords": 0.3},
        dynamics_range=(0.35, 0.9),
    ),
    "drum_and_bass": GenreProfile(
        name="drum_and_bass",
        bpm_range=(160, 180),
        default_bpm=174,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "min7", "min": "min7", "dom7": "min7"},
        instruments={
            "melody": "pluck",
            "chords": "ambient_pad",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.85, "snare": 0.8, "bass": 0.75, "chords": 0.3},
        dynamics_range=(0.4, 0.95),
    ),
    "dubstep": GenreProfile(
        name="dubstep",
        bpm_range=(138, 142),
        default_bpm=140,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "min7", "min": "min7"},
        instruments={
            "melody": "sync_lead",
            "chords": "dark_pad",
            "bass": "moog_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"bass": 0.9, "kick": 0.85, "snare": 0.8},
        dynamics_range=(0.4, 1.0),
    ),
    "motown": GenreProfile(
        name="motown",
        bpm_range=(100, 130),
        default_bpm=115,
        swing=0.2,
        groove="motown",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7"},
        instruments={
            "melody": "sine",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "strings",
        },
        volumes={"bass": 0.7, "pad": 0.4, "snare": 0.65},
        dynamics_range=(0.45, 0.85),
    ),
    "surf_rock": GenreProfile(
        name="surf_rock",
        bpm_range=(130, 170),
        default_bpm=150,
        swing=0.0,
        groove="straight",
        harmony_map={"maj7": "maj", "min7": "min", "dom7": "maj"},
        instruments={
            "melody": "guitar_electric",
            "chords": "guitar_electric",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.7, "chords": 0.6},
        dynamics_range=(0.5, 0.9),
        effects_hints={"melody": {"spring_reverb": True}},
    ),
    "grunge": GenreProfile(
        name="grunge",
        bpm_range=(100, 140),
        default_bpm=120,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "power5", "min": "power5", "dom7": "power5"},
        instruments={
            "melody": "sawtooth",
            "chords": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"chords": 0.75, "kick": 0.8, "snare": 0.7, "bass": 0.65},
        dynamics_range=(0.3, 0.95),
    ),
    "tango": GenreProfile(
        name="tango",
        bpm_range=(100, 140),
        default_bpm=120,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "bandoneon",
            "chords": "piano",
            "bass": "contrabass",
            "pad": "violin",
        },
        pans={"melody": -0.15, "chords": 0.15, "bass": 0.2, "pad": -0.2},
        volumes={"melody": 0.65, "pad": 0.5},
        articulations={"melody": "legato"},
        dynamics_range=(0.35, 0.9),
    ),
    "samba": GenreProfile(
        name="samba",
        bpm_range=(140, 200),
        default_bpm=170,
        swing=0.0,
        groove="samba",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "dom9"},
        instruments={
            "melody": "flute",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "kick": "surdo",
            "snare": "tambourine",
            "hat": "shaker",
        },
        volumes={"kick": 0.7, "snare": 0.5, "hat": 0.45},
        dynamics_range=(0.5, 0.9),
    ),
    "cumbia": GenreProfile(
        name="cumbia",
        bpm_range=(80, 110),
        default_bpm=95,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7"},
        instruments={
            "melody": "accordion",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "shaker",
            "pad": "guzheng",
        },
        volumes={"melody": 0.6, "hat": 0.45, "bass": 0.6},
        dynamics_range=(0.45, 0.85),
    ),
    "flamenco": GenreProfile(
        name="flamenco",
        bpm_range=(90, 160),
        default_bpm=130,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "guitar_acoustic",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "kick": "cajon",
            "snare": "cajon",
        },
        pans={"melody": -0.1, "chords": 0.1},
        volumes={"melody": 0.7, "chords": 0.6, "kick": 0.55},
        dynamics_range=(0.3, 0.95),
    ),
    "celtic": GenreProfile(
        name="celtic",
        bpm_range=(100, 160),
        default_bpm=130,
        swing=0.0,
        groove="straight",
        time_sig=(6, 8),
        harmony_map={"min7": "min", "dom7": "maj", "maj7": "maj"},
        instruments={
            "melody": "flute",
            "chords": "guitar_acoustic",
            "bass": "cello",
            "pad": "violin",
        },
        pans={"melody": -0.2, "pad": 0.2},
        volumes={"melody": 0.6, "pad": 0.5},
        dynamics_range=(0.35, 0.85),
    ),
    "bollywood": GenreProfile(
        name="bollywood",
        bpm_range=(100, 140),
        default_bpm=120,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7"},
        instruments={
            "melody": "sitar_ks",
            "chords": "tabla",
            "bass": "bass",
            "kick": "tabla",
            "snare": "tabla",
            "hat": "shaker",
            "pad": "strings",
        },
        volumes={"melody": 0.65, "pad": 0.45},
        dynamics_range=(0.4, 0.9),
    ),
    "smooth_jazz": GenreProfile(
        name="smooth_jazz",
        bpm_range=(85, 115),
        default_bpm=100,
        swing=0.3,
        groove="shuffle",
        harmony_map={
            "maj": "maj9",
            "min": "min9",
            "dom7": "dom9",
            "sus4": "9sus4",
            "maj7": "maj9",
        },
        instruments={
            "melody": "soprano_sax",
            "chords": "rhodes",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "pad": "warm_pad",
        },
        volumes={"melody": 0.55, "pad": 0.35, "hat": 0.3},
        dynamics_range=(0.3, 0.65),
    ),
    "cool_jazz": GenreProfile(
        name="cool_jazz",
        bpm_range=(100, 160),
        default_bpm=130,
        swing=0.45,
        groove="shuffle",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "dom7",
        },
        instruments={
            "melody": "trumpet",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
        },
        articulations={"melody": "con_sordino"},
        volumes={"melody": 0.5, "chords": 0.4, "hat": 0.4, "kick": 0.25},
        dynamics_range=(0.25, 0.65),
    ),
    "modal_jazz": GenreProfile(
        name="modal_jazz",
        bpm_range=(100, 160),
        default_bpm=136,
        swing=0.5,
        groove="shuffle",
        harmony_map={
            "maj": "maj7",
            "min": "min7",
            "dom7": "sus4_add9",
            "dim": "min7",
        },
        instruments={
            "melody": "saxophone",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
        },
        volumes={"melody": 0.6, "chords": 0.4, "hat": 0.45},
        dynamics_range=(0.3, 0.8),
    ),
    "fusion": GenreProfile(
        name="fusion",
        bpm_range=(100, 160),
        default_bpm=130,
        swing=0.2,
        groove="funk_loose",
        harmony_map={
            "maj": "maj9#11",
            "min": "min11",
            "dom7": "dom13",
            "sus4": "9sus4",
        },
        instruments={
            "melody": "guitar_electric",
            "chords": "rhodes",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
        },
        volumes={"melody": 0.6, "chords": 0.45, "hat": 0.4},
        dynamics_range=(0.35, 0.9),
    ),
    "trip_hop": GenreProfile(
        name="trip_hop",
        bpm_range=(80, 100),
        default_bpm=90,
        swing=0.0,
        groove="lofi",
        harmony_map={"maj": "min7", "min": "min7", "dom7": "min7"},
        instruments={
            "melody": "sine",
            "chords": "dark_pad",
            "bass": "sub_bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.7, "bass": 0.6, "chords": 0.4, "melody": 0.45, "hat": 0.2},
        dynamics_range=(0.25, 0.65),
    ),
    "second_line": GenreProfile(
        name="second_line",
        bpm_range=(100, 140),
        default_bpm=120,
        swing=0.3,
        groove="shuffle",
        harmony_map={"maj": "maj", "min": "min", "dom7": "dom7"},
        instruments={
            "melody": "trumpet",
            "chords": "trombone",
            "bass": "tuba",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.65, "chords": 0.55, "bass": 0.6, "snare": 0.7},
        dynamics_range=(0.5, 0.9),
    ),
    "chillwave": GenreProfile(
        name="chillwave",
        bpm_range=(80, 110),
        default_bpm=95,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "maj7", "min": "min7", "dom7": "maj7"},
        instruments={
            "melody": "sine",
            "chords": "warm_pad",
            "bass": "sub_bass",
            "kick": "drums_808",
            "snare": "drums_clap",
            "hat": "drums_hat",
            "pad": "glass_pad",
        },
        volumes={"pad": 0.45, "chords": 0.4, "melody": 0.35, "hat": 0.2},
        dynamics_range=(0.2, 0.55),
        effects_hints={"chords": {"tape_wow_flutter": True}},
    ),
    "swing": GenreProfile(
        name="swing",
        bpm_range=(120, 180),
        default_bpm=150,
        swing=0.55,
        groove="big_band",
        harmony_map={"maj": "6_9", "min": "min7", "dom7": "dom9"},
        instruments={
            "melody": "clarinet",
            "chords": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_ride",
        },
        volumes={"melody": 0.6, "chords": 0.45, "hat": 0.45, "kick": 0.3},
        dynamics_range=(0.4, 0.85),
    ),
    "new_orleans": GenreProfile(
        name="new_orleans",
        bpm_range=(90, 130),
        default_bpm=110,
        swing=0.35,
        groove="shuffle",
        harmony_map={"maj": "dom7", "min": "min7", "maj7": "dom9"},
        instruments={
            "melody": "trumpet",
            "chords": "piano",
            "bass": "tuba",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"melody": 0.65, "bass": 0.6, "snare": 0.6},
        dynamics_range=(0.45, 0.9),
    ),
    "acid_jazz": GenreProfile(
        name="acid_jazz",
        bpm_range=(100, 130),
        default_bpm=115,
        swing=0.0,
        groove="funk_loose",
        harmony_map={
            "maj": "dom9",
            "min": "min9",
            "dom7": "dom9",
        },
        instruments={
            "melody": "saxophone",
            "chords": "organ",
            "bass": "bass",
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
        },
        volumes={"bass": 0.65, "chords": 0.5, "hat": 0.35},
        dynamics_range=(0.4, 0.85),
    ),
    "reggaeton": GenreProfile(
        name="reggaeton",
        bpm_range=(85, 100),
        default_bpm=92,
        swing=0.0,
        groove="straight",
        harmony_map={"maj": "min", "min": "min", "dom7": "min"},
        instruments={
            "melody": "lead_edm",
            "chords": "pad",
            "bass": "sub_808",
            "kick": "drums_808",
            "snare": "drums_clap",
            "hat": "drums_hat",
        },
        volumes={"kick": 0.9, "bass": 0.8, "hat": 0.35},
        dynamics_range=(0.45, 0.9),
    ),
    "mariachi": GenreProfile(
        name="mariachi",
        bpm_range=(100, 150),
        default_bpm=130,
        swing=0.0,
        groove="straight",
        time_sig=(3, 4),
        harmony_map={"min7": "min", "dom7": "dom7", "maj7": "maj"},
        instruments={
            "melody": "trumpet",
            "chords": "guitar_acoustic",
            "bass": "bass",
            "pad": "violin",
        },
        pans={"melody": -0.15, "chords": 0.15, "pad": -0.2},
        volumes={"melody": 0.7, "pad": 0.55},
        dynamics_range=(0.5, 0.95),
    ),
}


# ---------------------------------------------------------------------------
# Individual transform layers
# ---------------------------------------------------------------------------


def rhythm_transform(
    song: Song,
    feel: str = "swing",
    amount: float = 1.0,
) -> Song:
    """Transform the rhythmic feel of a song without changing pitches or harmony.

    This is the "play it with swing" or "make it shuffle" operation.
    Changes note durations to fit the target rhythmic pattern while
    preserving the melodic and harmonic content.

    Feels:
        straight:  Remove all swing, even timing
        swing:     Swing 8th notes (jazz/blues, long-short pattern)
        shuffle:   Triplet shuffle (blues, boogie)
        latin:     Even 8ths with syncopated accents
        reggae:    Offbeat emphasis, push beats 2 and 4

    Args:
        song:    Source song.
        feel:    Target rhythmic feel.
        amount:  Blend 0.0 (no change) to 1.0 (full transform).

    Returns:
        New Song with transformed rhythm.
    """
    result = _clone_song(song)
    result.title = f"{song.title} ({feel})"

    swing_map = {
        "straight": 0.0,
        "swing": 0.5,
        "shuffle": 0.55,
        "heavy_swing": 0.67,
        "latin": 0.0,
        "reggae": 0.0,
    }

    target_swing = swing_map.get(feel, 0.0) * amount

    for track in result.tracks:
        track.swing = target_swing

        if feel == "reggae":
            # Reggae: shift chords to offbeats
            new_beats = []
            for i, beat in enumerate(track.beats):
                if beat.event is not None and hasattr(beat.event, "root"):
                    # Chord on offbeat: add a rest before it
                    half_dur = beat.event.duration * 0.5
                    new_beats.append(Beat(event=Note.rest(half_dur)))
                    shifted = copy.copy(beat.event)
                    shifted.duration = half_dur
                    new_beats.append(Beat(event=shifted))
                else:
                    new_beats.append(beat)
            track.beats = new_beats

    # Apply groove template if available
    groove_name = {
        "swing": "shuffle",
        "shuffle": "shuffle",
        "heavy_swing": "swing_heavy",
        "latin": "bossa",
        "reggae": "reggae",
        "straight": "straight",
        "funk": "funk_tight",
        "lofi": "lofi",
        "neo_soul": "neo_soul",
        "afrobeat": "afrobeat",
        "samba": "samba",
        "salsa": "salsa",
        "big_band": "big_band",
    }.get(feel, "straight")

    try:
        from .theory.rhythm import groove_template, apply_groove

        template = groove_template(groove_name)
        for track in result.tracks:
            has_chords = any(isinstance(getattr(b, "event", None), Chord) for b in track.beats)
            if has_chords:
                continue
            events = [b.event for b in track.beats]
            try:
                grooved = apply_groove(events, template, strength=amount * 0.7)
                track.beats = [Beat(event=e) for e in grooved]
            except (AttributeError, TypeError):
                pass
    except (KeyError, ValueError):
        pass

    return result


def harmony_transform(
    song: Song,
    target_genre: str,
) -> Song:
    """Reharmonize a song's chords for a target genre.

    Swaps chord qualities to match the genre's harmonic language.
    Jazz gets 7ths and extensions. Blues gets dom7 on everything.
    Funk gets 9ths and #9s. Ambient gets sus chords. The root
    motion stays the same - the color changes.

    Args:
        song:          Source song.
        target_genre:  Genre name (key in GENRE_PROFILES).

    Returns:
        New Song with reharmonized chords.
    """
    profile = GENRE_PROFILES.get(target_genre)
    if profile is None:
        return copy.deepcopy(song)

    result = _clone_song(song)
    h_map = profile.harmony_map

    for track in result.tracks:
        for beat in track.beats:
            if beat.event is not None and isinstance(beat.event, Chord):
                old_shape = beat.event.shape
                new_shape = h_map.get(old_shape, old_shape)
                if new_shape in CHORD_SHAPES:
                    beat.event = Chord(
                        beat.event.root,
                        new_shape,
                        beat.event.octave,
                        beat.event.duration,
                        beat.event.velocity,
                    )

    return result


def instrument_transform(
    song: Song,
    target_genre: str,
) -> Song:
    """Swap instruments to match a target genre.

    Identifies each track's role (melody, chords, bass, drums) by
    examining its content and instrument name, then swaps to the
    genre-appropriate instrument.

    Args:
        song:          Source song.
        target_genre:  Genre name.

    Returns:
        New Song with genre-appropriate instruments.
    """
    profile = GENRE_PROFILES.get(target_genre)
    if profile is None:
        return copy.deepcopy(song)

    result = _clone_song(song)

    for track in result.tracks:
        role = _detect_track_role(track)
        if role in profile.instruments:
            track.instrument = profile.instruments[role]
        if role in profile.pans:
            track.pan = profile.pans[role]
        if role in profile.volumes:
            track.volume = profile.volumes[role]

    return result


def groove_transform(
    song: Song,
    groove_name: str,
    strength: float = 0.7,
) -> Song:
    """Apply a groove template to a song's timing.

    The groove template shifts individual note timings by small amounts
    to create the feel of a specific style. This is the difference
    between a machine and a human playing the same notes.

    Args:
        song:         Source song.
        groove_name:  Groove template name (funk_tight, bossa, lofi, etc.)
        strength:     How strongly to apply (0.0-1.0).

    Returns:
        New Song with grooved timing.
    """
    from .theory.rhythm import groove_template, apply_groove

    result = _clone_song(song)
    template = groove_template(groove_name)

    for track in result.tracks:
        # apply_groove only works on Note objects, not Chords
        # Filter to Note-only tracks and skip tracks with Chords
        has_chords = any(isinstance(getattr(b, "event", None), Chord) for b in track.beats)
        if has_chords:
            continue
        events = [b.event for b in track.beats]
        try:
            grooved = apply_groove(events, template, strength=strength)
            track.beats = [Beat(event=e) for e in grooved]
        except (AttributeError, TypeError):
            pass

    return result


def dynamics_transform(
    song: Song,
    target_genre: str,
) -> Song:
    """Adjust velocity/dynamics to match a genre's typical range.

    Lofi is quiet and compressed. Rock is loud. Jazz has wide dynamics.
    This rescales all velocities to fit the genre's expected range.

    Args:
        song:          Source song.
        target_genre:  Genre name.

    Returns:
        New Song with adjusted dynamics.
    """
    profile = GENRE_PROFILES.get(target_genre)
    if profile is None:
        return copy.deepcopy(song)

    result = _clone_song(song)
    lo, hi = profile.dynamics_range

    for track in result.tracks:
        for beat in track.beats:
            if beat.event is not None and hasattr(beat.event, "velocity"):
                old_vel = beat.event.velocity
                # Rescale from [0, 1] to [lo, hi]
                beat.event.velocity = lo + old_vel * (hi - lo)

    return result


def articulation_transform(
    song: Song,
    target_genre: str,
) -> Song:
    """Apply genre-specific articulations to tracks.

    Jazz snare gets brushes. Classical strings get arco. Funk gets
    staccato chords. Bossa gets cross-stick. The genre profile
    defines default articulations per track role.

    Args:
        song:          Source song.
        target_genre:  Genre name.

    Returns:
        New Song with genre-appropriate articulations.
    """
    profile = GENRE_PROFILES.get(target_genre)
    if profile is None:
        return copy.deepcopy(song)

    result = _clone_song(song)

    for track in result.tracks:
        role = _detect_track_role(track)
        art = profile.articulations.get(role)
        if art is not None:
            for beat in track.beats:
                if beat.event is not None and isinstance(beat.event, Note):
                    beat.event.articulation = art

    return result


# ---------------------------------------------------------------------------
# The main event: full genre transform
# ---------------------------------------------------------------------------


def genre_transform(
    song: Song,
    target_genre: str,
    preserve_melody: bool = True,
    preserve_key: bool = True,
    bpm: int | None = None,
    seed: int | None = None,
) -> Song:
    """Transform a song into a different genre.

    This is the full pipeline. Takes a song and applies all seven
    transform layers to produce a version in the target genre. The
    melody and chord progression are preserved (roots stay the same)
    but everything else adapts: rhythm feel, chord voicings, instruments,
    groove, articulations, dynamics, and tempo.

    The musical equivalent of "play that pop song as jazz" or "give me
    the bossa nova version." Rasputin in every genre starts here.

    Args:
        song:              Source Song.
        target_genre:      Genre name from GENRE_PROFILES.
        preserve_melody:   Keep original melody pitches (True) or allow
                           genre-appropriate ornamentation (False).
        preserve_key:      Keep original key (True) or allow transposition.
        bpm:               Override tempo. None = use genre default.
        seed:              Random seed.

    Returns:
        New Song in the target genre's style.

    Example::

        pop = generate_full_song("pop", key="C", bpm=120, seed=42)
        jazz = genre_transform(pop, "jazz")
        bossa = genre_transform(pop, "bossa_nova")
        funk = genre_transform(pop, "funk")
        lofi = genre_transform(pop, "lofi")
    """
    profile = GENRE_PROFILES.get(target_genre)
    if profile is None:
        raise ValueError(
            f"Unknown genre {target_genre!r}. Available: {', '.join(sorted(GENRE_PROFILES))}"
        )

    # Layer 1: Start with a deep copy
    result = copy.deepcopy(song)

    # Layer 2: Tempo
    if bpm is not None:
        result.bpm = bpm
    else:
        result.bpm = profile.default_bpm

    result.time_sig = profile.time_sig

    # Layer 3: Harmony (reharmonize chords)
    result = harmony_transform(result, target_genre)

    # Layer 4: Instruments (swap presets)
    result = instrument_transform(result, target_genre)

    # Layer 5: Rhythm feel (swing, groove)
    for track in result.tracks:
        track.swing = profile.swing

    # Layer 6: Groove template
    try:
        result = groove_transform(result, profile.groove, strength=0.6)
    except (KeyError, ValueError):
        pass

    # Layer 7: Dynamics
    result = dynamics_transform(result, target_genre)

    # Layer 8: Articulations
    result = articulation_transform(result, target_genre)

    result.title = f"{song.title} ({profile.name.replace('_', ' ').title()} Version)"

    return result


# ---------------------------------------------------------------------------
# Convenience: rhythm pattern library
# ---------------------------------------------------------------------------


def apply_rhythm_pattern(
    notes: list[Note],
    pattern: str = "straight_8ths",
    beats_per_bar: int = 4,
) -> list[Note]:
    """Apply a named rhythm pattern to a note sequence.

    Takes a list of pitched notes and redistributes their durations
    to fit a named rhythmic pattern. The pitches cycle through the
    input notes while the rhythm changes underneath.

    Patterns:
        straight_8ths:   Even 8th notes
        straight_16ths:  Even 16th notes
        dotted_8ths:     Long-short dotted 8th + 16th
        shuffle:         Triplet long-short (swing 8ths)
        tresillo:        3+3+2 (Latin fundamental rhythm)
        habanera:        Dotted 8th + 16th + quarter + quarter
        bossa_rhythm:    Syncopated bossa pattern
        bo_diddley:      3+3+3+3+4 (the Bo Diddley beat)
        clave_32:        Son clave 3-2 rhythm applied to pitches
        charleston:      Quarter + dotted quarter (1920s swing)

    Args:
        notes:         Source notes (pitches used, durations replaced).
        pattern:       Pattern name.
        beats_per_bar: Beats per bar for pattern alignment.

    Returns:
        Notes with the rhythm pattern applied.
    """
    PATTERNS = {
        "straight_8ths": [0.5] * 8,
        "straight_16ths": [0.25] * 16,
        "straight_quarters": [1.0] * 4,
        "dotted_8ths": [0.75, 0.25] * 4,
        "shuffle": [0.667, 0.333] * 4,
        "tresillo": [1.5, 1.5, 1.0],
        "habanera": [0.75, 0.25, 1.0, 1.0],
        "bossa_rhythm": [1.5, 0.5, 1.0, 0.5, 0.5],
        "bo_diddley": [0.75, 0.75, 0.75, 0.75, 1.0],
        "clave_32": [1.5, 1.0, 1.5, 1.0, 1.0, 1.0],
        "charleston": [1.0, 1.5, 0.5, 1.0],
        # v170 expansion
        "dembow": [0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5, 0.5],  # reggaeton
        "four_on_floor": [1.0, 1.0, 1.0, 1.0],  # house/disco/techno
        "waltz": [1.0, 0.5, 0.5, 1.0, 0.5, 0.5],  # 3/4 oom-pah-pah
        "take_five": [1.5, 1.0, 1.0, 1.5],  # 5/4 (Brubeck)
        "balkan_7": [1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0],  # 7/8 (3+2+2)
        "second_line": [0.75, 0.25, 0.5, 0.75, 0.25, 0.5, 1.0],  # New Orleans
        "train_beat": [0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5],
        "half_time": [2.0, 2.0],  # halved pulse
        "double_time": [0.25] * 16,  # doubled pulse
        "baiao": [0.5, 0.5, 0.75, 0.25, 0.5, 0.5, 0.75, 0.25],  # Brazilian baiao
        "cumbia": [0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.5, 0.5],  # Colombian cumbia
        "songo": [0.5, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5],  # Cuban songo
        "nanigo": [1.0, 0.5, 0.5, 1.0, 0.5, 0.5],  # 6/8 Afro-Cuban
        "mozambique": [0.75, 0.25, 0.5, 0.75, 0.25, 0.5, 0.5, 0.5],  # Pello el Afrokan
        "soca": [0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.25, 0.25, 0.5],  # Trinidad
        "ska_offbeat": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # offbeat chops
        "reggae_one_drop": [2.0, 1.0, 1.0],  # kick on 1, snare on 3
    }

    durations = PATTERNS.get(pattern)
    if durations is None:
        raise ValueError(f"Unknown pattern {pattern!r}. Available: {', '.join(sorted(PATTERNS))}")

    pitched = [n for n in notes if n.pitch is not None]
    if not pitched:
        return list(notes)

    result: list[Note] = []
    pitch_idx = 0
    dur_idx = 0

    # Fill one bar at a time
    total_target = sum(durations)
    bar_count = max(1, int(sum(n.duration for n in pitched) / total_target))

    for _ in range(bar_count):
        for dur in durations:
            src = pitched[pitch_idx % len(pitched)]
            result.append(
                Note(
                    pitch=src.pitch,
                    octave=src.octave,
                    duration=dur,
                    velocity=src.velocity,
                    articulation=src.articulation,
                )
            )
            pitch_idx += 1

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clone_song(song: Song) -> Song:
    """Deep copy a Song."""
    return copy.deepcopy(song)


def _detect_track_role(track: Track) -> str:
    """Guess a track's musical role from its name and instrument."""
    name_lower = track.name.lower()
    inst_lower = track.instrument.lower()

    # Explicit role detection
    if any(k in name_lower for k in ("kick", "808")):
        return "kick"
    if any(k in name_lower for k in ("snare", "rim", "clap")):
        return "snare"
    if any(k in name_lower for k in ("hat", "ride", "cymbal")):
        return "hat"
    if "bass" in name_lower or "bass" in inst_lower:
        return "bass"
    if any(k in name_lower for k in ("pad", "rhodes", "keys")):
        return "pad"
    if any(k in name_lower for k in ("chord", "comp", "rhythm")):
        return "chords"
    if any(k in name_lower for k in ("lead", "melody", "solo", "vocal")):
        return "melody"

    # Instrument-based detection
    if any(k in inst_lower for k in ("kick", "808")):
        return "kick"
    if "snare" in inst_lower or "clap" in inst_lower:
        return "snare"
    if "hat" in inst_lower or "ride" in inst_lower:
        return "hat"
    if "bass" in inst_lower or "sub" in inst_lower:
        return "bass"
    if "pad" in inst_lower or "organ" in inst_lower or "rhodes" in inst_lower:
        return "pad"
    if "piano" in inst_lower or "guitar" in inst_lower:
        return "chords"

    # Content-based: if track has mostly chords, it is chords
    chord_count = sum(1 for b in track.beats if isinstance(getattr(b, "event", None), Chord))
    note_count = sum(
        1
        for b in track.beats
        if isinstance(getattr(b, "event", None), Note)
        and getattr(b.event, "pitch", None) is not None
    )

    if chord_count > note_count:
        return "chords"
    if note_count > 0:
        return "melody"

    return "melody"  # default


def list_genres() -> list[str]:
    """Return all available genre names for genre_transform."""
    return sorted(GENRE_PROFILES.keys())


def list_rhythm_patterns() -> list[str]:
    """Return all available rhythm pattern names."""
    # Build dynamically from the pattern dict so it stays in sync
    return sorted(
        [
            "straight_8ths",
            "straight_16ths",
            "straight_quarters",
            "dotted_8ths",
            "shuffle",
            "tresillo",
            "habanera",
            "bossa_rhythm",
            "bo_diddley",
            "clave_32",
            "charleston",
            "dembow",
            "four_on_floor",
            "waltz",
            "take_five",
            "balkan_7",
            "second_line",
            "train_beat",
            "half_time",
            "double_time",
            "baiao",
            "cumbia",
            "songo",
            "nanigo",
            "mozambique",
            "soca",
            "ska_offbeat",
            "reggae_one_drop",
        ]
    )
