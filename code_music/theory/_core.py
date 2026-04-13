"""theory._core — shared constants, data, and private helpers."""

from __future__ import annotations

from ..engine import Note, euclid  # noqa: F401 — re-exported for submodules

# ---------------------------------------------------------------------------
# Note utilities
# ---------------------------------------------------------------------------

_NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

_NOTE_TO_SEMI = {n: i for i, n in enumerate(_NOTE_NAMES)}

# Enharmonic aliases
_NOTE_TO_SEMI.update(
    {"Db": 1, "D#": 3, "Fb": 4, "E#": 5, "Gb": 6, "G#": 8, "A#": 10, "Cb": 11, "B#": 0}
)



def _semi(note: str) -> int:
    return _NOTE_TO_SEMI[note]



# ---------------------------------------------------------------------------
# Scale intervals (semitones from root)
# ---------------------------------------------------------------------------

_SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11],  # half-whole
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
}


# Chord shape → semitones from root
_CHORD_SEMI = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "min7b5": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "min9": [0, 3, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "dom9": [0, 4, 7, 10, 14],
}



# ---------------------------------------------------------------------------
# Song diffing
# ---------------------------------------------------------------------------
# Harmonic analysis
# ---------------------------------------------------------------------------

_ROMAN = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}


_QUALITY_MAP = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "+",
    "dom7": "7",
    "maj7": "M7",
    "min7": "m7",
    "dim7": "dim7",
    "min7b5": "m7b5",
    "sus2": "sus2",
    "sus4": "sus4",
    "min9": "m9",
    "maj9": "M9",
    "dom9": "9",
}


_FUNCTION_MAP = {
    0: "tonic",
    2: "supertonic",
    4: "mediant",
    5: "subdominant",
    7: "dominant",
    9: "submediant",
    11: "leading",
}



# ---------------------------------------------------------------------------
# Interval naming and parallel harmony
# ---------------------------------------------------------------------------

_INTERVAL_NAMES = {
    0: "unison",
    1: "minor 2nd",
    2: "major 2nd",
    3: "minor 3rd",
    4: "major 3rd",
    5: "perfect 4th",
    6: "tritone",
    7: "perfect 5th",
    8: "minor 6th",
    9: "major 6th",
    10: "minor 7th",
    11: "major 7th",
    12: "octave",
}



# Common chord progressions for suggestion engine
_COMMON_NEXT = {
    "I": ["IV", "V", "vi", "ii"],
    "ii": ["V", "vii", "IV"],
    "iii": ["vi", "IV", "ii"],
    "IV": ["V", "I", "ii", "vii"],
    "V": ["I", "vi", "IV"],
    "vi": ["IV", "ii", "V", "I"],
    "vii": ["I", "iii"],
}


_DEGREE_TO_SEMI = {"I": 0, "ii": 2, "iii": 4, "IV": 5, "V": 7, "vi": 9, "vii": 11}

_DEGREE_SHAPES = {
    "I": "maj",
    "ii": "min",
    "iii": "min",
    "IV": "maj",
    "V": "maj",
    "vi": "min",
    "vii": "dim",
}



# ---------------------------------------------------------------------------
# Voice leading engine — SATB (v42.0)
# ---------------------------------------------------------------------------

# SATB voice ranges (MIDI-style octave numbering)
_SATB_RANGES = {
    "soprano": (60, 79),  # C4–G5
    "alto": (53, 74),  # F3–D5
    "tenor": (48, 69),  # C3–A4
    "bass": (40, 64),  # E2–E4
}



def _note_to_abs(pitch: str, octave: int) -> int:
    """Convert note name + octave to absolute semitone (C4 = 60)."""
    return _semi(pitch) + octave * 12



def _abs_to_note(absolute: int) -> tuple[str, int]:
    """Convert absolute semitone to (pitch_name, octave)."""
    return (_NOTE_NAMES[absolute % 12], absolute // 12)



def _find_nearest(pc: int, target: int, low: int, high: int) -> int:
    """Find the absolute pitch closest to target with the given pitch class."""
    candidates = []
    for octave in range(low // 12, high // 12 + 2):
        absolute = pc + octave * 12
        if low <= absolute <= high:
            candidates.append(absolute)
    if not candidates:
        # Fallback: closest to range
        return pc + (target // 12) * 12
    return min(candidates, key=lambda a: abs(a - target))



def _smooth_voice_lead(chord_pcs: list[int], prev: list[int]) -> list[int]:
    """Voice-lead to new chord PCs from previous voicing, minimizing movement."""
    # For each voice, find the nearest realization of any chord tone
    used: set[int] = set()
    result: list[int] = []
    voices = ["soprano", "alto", "tenor", "bass"]

    for i, (prev_abs, voice) in enumerate(zip(prev, voices)):
        low, high = _SATB_RANGES[voice]
        best_abs = prev_abs
        best_dist = 999

        for pc in chord_pcs:
            for octave in range(low // 12, high // 12 + 2):
                candidate = pc + octave * 12
                if low <= candidate <= high:
                    dist = abs(candidate - prev_abs)
                    if dist < best_dist:
                        best_dist = dist
                        best_abs = candidate

        result.append(best_abs)
        used.add(best_abs % 12)

    return result



# ---------------------------------------------------------------------------
# Key modulation & pivot chords (v43.0)
# ---------------------------------------------------------------------------


def _diatonic_chords(key: str, mode: str = "major") -> list[tuple[str, str]]:
    """Return the 7 diatonic triads in a key."""
    intervals = _SCALE_INTERVALS.get(mode, _SCALE_INTERVALS["major"])
    k = _semi(key)
    # Quality pattern for major: maj min min maj maj min dim
    qualities_major = ["maj", "min", "min", "maj", "maj", "min", "dim"]
    qualities_minor = ["min", "dim", "maj", "min", "min", "maj", "maj"]
    quals = qualities_minor if mode in ("aeolian", "minor") else qualities_major
    chords = []
    for i, interval in enumerate(intervals[:7]):
        root = _NOTE_NAMES[(k + interval) % 12]
        chords.append((root, quals[i % len(quals)]))
    return chords



# ---------------------------------------------------------------------------
# Roman numeral parsing (v44.0)
# ---------------------------------------------------------------------------

_ROMAN_TO_DEGREE = {
    "I": 0,
    "II": 2,
    "III": 4,
    "IV": 5,
    "V": 7,
    "VI": 9,
    "VII": 11,
    "i": 0,
    "ii": 2,
    "iii": 4,
    "iv": 5,
    "v": 7,
    "vi": 9,
    "vii": 11,
}


_ROMAN_PATTERNS = [
    "VII",
    "VII",
    "III",
    "III",
    "II",
    "II",
    "IV",
    "IV",
    "VI",
    "VI",
    "vii",
    "iii",
    "ii",
    "iv",
    "vi",
    "I",
    "V",
    "i",
    "v",
]



# ---------------------------------------------------------------------------
# Species counterpoint (v46.0)
# ---------------------------------------------------------------------------

# Consonance classification (intervals in semitones)
_PERFECT_CONSONANCES = {0, 7}  # unison, perfect 5th

_IMPERFECT_CONSONANCES = {3, 4, 8, 9}  # minor/major 3rd, minor/major 6th

_DISSONANCES = {1, 2, 5, 6, 10, 11}  # seconds, tritone, sevenths



# ---------------------------------------------------------------------------
# Orchestration & instrument ranges (v53.0)
# ---------------------------------------------------------------------------

# Instrument ranges as (lowest_abs, highest_abs) using C4=60 convention
_INSTRUMENT_RANGES = {
    "violin": (55, 88),  # G3–E7
    "viola": (48, 81),  # C3–A5
    "cello": (36, 69),  # C2–A4
    "contrabass": (28, 55),  # E1–G3
    "flute": (60, 84),  # C4–C7
    "oboe": (58, 82),  # Bb3–A6
    "clarinet": (50, 79),  # D3–G5 (Bb clarinet, written)
    "bassoon": (34, 65),  # Bb1–F4
    "trumpet": (55, 77),  # G3–F5
    "french_horn": (41, 67),  # F2–G4
    "trombone": (34, 65),  # Bb1–F4
    "tuba": (24, 53),  # C1–F3
    "piano": (21, 108),  # A0–C8
    "guitar": (40, 76),  # E2–E5
    "bass_guitar": (28, 55),  # E1–G3
    "soprano_voice": (60, 79),  # C4–G5
    "alto_voice": (53, 74),  # F3–D5
    "tenor_voice": (48, 69),  # C3–A4
    "bass_voice": (40, 64),  # E2–E4
}



# ---------------------------------------------------------------------------
# Scale atlas — extended scale database (v56.0)
# ---------------------------------------------------------------------------

# Additional scales beyond the 14 standard ones in _SCALE_INTERVALS
_EXOTIC_SCALES = {
    "hungarian_minor": [0, 2, 3, 6, 7, 8, 11],
    "hungarian_major": [0, 3, 4, 6, 7, 9, 10],
    "hirajoshi": [0, 2, 3, 7, 8],
    "in_sen": [0, 1, 5, 7, 10],
    "iwato": [0, 1, 5, 6, 10],
    "phrygian_dominant": [0, 1, 4, 5, 7, 8, 10],
    "double_harmonic": [0, 1, 4, 5, 7, 8, 11],
    "enigmatic": [0, 1, 4, 6, 8, 10, 11],
    "prometheus": [0, 2, 4, 6, 9, 10],
    "augmented": [0, 3, 4, 7, 8, 11],
    "tritone": [0, 1, 4, 6, 7, 10],
    "bebop_dominant": [0, 2, 4, 5, 7, 9, 10, 11],
    "bebop_major": [0, 2, 4, 5, 7, 8, 9, 11],
    "bebop_minor": [0, 2, 3, 5, 7, 8, 9, 10],
    "neapolitan_major": [0, 1, 3, 5, 7, 9, 11],
    "neapolitan_minor": [0, 1, 3, 5, 7, 8, 11],
    "persian": [0, 1, 4, 5, 6, 8, 11],
    "arabian": [0, 2, 4, 5, 6, 8, 10],
    "balinese": [0, 1, 3, 7, 8],
    "chinese": [0, 4, 6, 7, 11],
    "egyptian": [0, 2, 5, 7, 10],
    "kumoi": [0, 2, 3, 7, 9],
    "pelog": [0, 1, 3, 7, 8],
    "spanish_gypsy": [0, 1, 4, 5, 7, 8, 10],
    "super_locrian": [0, 1, 3, 4, 6, 8, 10],
    "lydian_dominant": [0, 2, 4, 6, 7, 9, 10],
    "lydian_augmented": [0, 2, 4, 6, 8, 9, 11],
    "half_diminished": [0, 2, 3, 5, 6, 8, 10],
    "altered": [0, 1, 3, 4, 6, 8, 10],
    "acoustic": [0, 2, 4, 6, 7, 9, 10],
}


# Merge into the main dict at module load time
_SCALE_INTERVALS.update(_EXOTIC_SCALES)



# ---------------------------------------------------------------------------
# Groove templates & swing maps (v59.0)
# ---------------------------------------------------------------------------

# Named groove templates: list of timing offsets per 16th note in a bar
# Positive = late (behind the beat), negative = early (ahead)
_GROOVE_TEMPLATES = {
    "straight": [0.0] * 16,
    "mpc_swing": [
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
    ],
    "j_dilla": [
        0.0,
        0.06,
        -0.01,
        0.04,
        0.0,
        0.05,
        -0.02,
        0.03,
        0.0,
        0.07,
        -0.01,
        0.05,
        0.0,
        0.06,
        -0.02,
        0.04,
    ],
    "motown": [
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
    ],
    "shuffle": [
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
    ],
    "bossa": [
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
    ],
}



# ---------------------------------------------------------------------------
# Musical dice game — Musikalisches Würfelspiel (v69.0)
# ---------------------------------------------------------------------------

# Mozart's original table (simplified — measure indices for a minuet)
# Each row = one of 11 possible dice outcomes (2-12); each column = one bar position
_MOZART_MINUET_TABLE = [
    [96, 22, 141, 41, 105, 122, 11, 30, 70, 121, 26, 9, 112, 49, 109, 14],
    [32, 6, 128, 63, 146, 46, 134, 81, 117, 39, 126, 56, 174, 18, 116, 83],
    [69, 95, 158, 13, 153, 55, 110, 24, 66, 139, 15, 132, 73, 58, 145, 79],
    [40, 17, 113, 85, 161, 2, 159, 100, 90, 176, 7, 34, 67, 160, 52, 170],
    [148, 74, 163, 45, 80, 97, 36, 107, 25, 143, 64, 125, 76, 136, 1, 93],
    [104, 157, 27, 167, 154, 68, 118, 91, 138, 71, 150, 29, 101, 162, 23, 151],
    [152, 60, 171, 53, 99, 133, 21, 127, 16, 155, 57, 175, 43, 168, 89, 172],
    [119, 84, 114, 50, 140, 86, 169, 94, 120, 88, 48, 166, 51, 115, 72, 111],
    [98, 142, 42, 156, 75, 129, 62, 123, 65, 77, 19, 82, 137, 38, 149, 8],
    [3, 87, 165, 61, 135, 47, 147, 33, 102, 4, 31, 164, 144, 59, 173, 78],
    [54, 130, 10, 103, 28, 37, 106, 5, 35, 20, 108, 92, 12, 124, 44, 131],
]



# ---------------------------------------------------------------------------
# Microtuning & just intonation (v70.0)
# ---------------------------------------------------------------------------

# Pure harmonic ratios for just intonation
_JUST_RATIOS = {
    0: (1, 1),  # unison
    1: (16, 15),  # minor second
    2: (9, 8),  # major second
    3: (6, 5),  # minor third
    4: (5, 4),  # major third
    5: (4, 3),  # perfect fourth
    6: (45, 32),  # tritone (augmented fourth)
    7: (3, 2),  # perfect fifth
    8: (8, 5),  # minor sixth
    9: (5, 3),  # major sixth
    10: (9, 5),  # minor seventh
    11: (15, 8),  # major seventh
    12: (2, 1),  # octave
}



# ---------------------------------------------------------------------------
# Melodic pattern database (v78.0)
# ---------------------------------------------------------------------------

_PATTERN_DB = {
    # Jazz licks
    "jazz_ii_v_i": {"notes": [2, 4, 5, 7, 9, 7, 5, 4], "genre": "jazz", "difficulty": 2},
    "jazz_bebop_turn": {"notes": [0, 2, 4, 3, 4, 7, 5, 4], "genre": "jazz", "difficulty": 3},
    "jazz_enclosure": {"notes": [5, 3, 4, 7, 6, 7], "genre": "jazz", "difficulty": 2},
    "jazz_coltrane_pattern": {"notes": [0, 4, 7, 11, 9, 7, 4, 2], "genre": "jazz", "difficulty": 4},
    "jazz_blues_head": {"notes": [0, 3, 5, 6, 7, 10, 7, 5], "genre": "jazz", "difficulty": 2},
    # Blues licks
    "blues_bend": {"notes": [0, 3, 5, 3, 0], "genre": "blues", "difficulty": 1},
    "blues_turnaround": {"notes": [7, 6, 5, 4, 3, 2, 0], "genre": "blues", "difficulty": 2},
    "blues_call": {"notes": [0, 3, 5, 7, 5, 3], "genre": "blues", "difficulty": 1},
    "blues_response": {"notes": [10, 7, 5, 3, 0], "genre": "blues", "difficulty": 1},
    # Rock riffs
    "rock_power": {"notes": [0, 0, 7, 7, 5, 5, 0], "genre": "rock", "difficulty": 1},
    "rock_pentatonic_run": {"notes": [0, 2, 4, 7, 9, 12, 9, 7], "genre": "rock", "difficulty": 2},
    "rock_chromatic_walk": {"notes": [0, 1, 2, 3, 4, 5, 6, 7], "genre": "rock", "difficulty": 1},
    # Latin patterns
    "latin_montuno": {"notes": [0, 4, 7, 4, 0, 4, 7, 9], "genre": "latin", "difficulty": 2},
    "latin_guajeo": {"notes": [0, 3, 7, 8, 7, 3, 0, 3], "genre": "latin", "difficulty": 2},
    # Classical figures
    "classical_alberti": {"notes": [0, 4, 7, 4, 0, 4, 7, 4], "genre": "classical", "difficulty": 1},
    "classical_mordent": {"notes": [0, 2, 0], "genre": "classical", "difficulty": 1},
    "classical_turn": {"notes": [2, 0, -1, 0], "genre": "classical", "difficulty": 1},
    "classical_scale_run": {
        "notes": [0, 2, 4, 5, 7, 9, 11, 12],
        "genre": "classical",
        "difficulty": 2,
    },
    # Funk patterns
    "funk_slap": {"notes": [0, 12, 0, 5, 0, 12, 7, 5], "genre": "funk", "difficulty": 2},
    "funk_ghost": {"notes": [0, 0, 5, 0, 7, 0, 5, 0], "genre": "funk", "difficulty": 2},
}



# ---------------------------------------------------------------------------
# Chord progression generator (v80.0)
# ---------------------------------------------------------------------------

_GENRE_TEMPLATES = {
    "pop": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "V", "V"],
        ["vi", "IV", "I", "V"],
    ],
    "jazz": [
        ["IImaj7", "V7", "Imaj7", "Imaj7"],
        ["Imaj7", "vi7", "ii7", "V7"],
        ["iii7", "vi7", "ii7", "V7"],
    ],
    "classical": [
        ["I", "IV", "V", "I"],
        ["I", "vi", "IV", "V"],
        ["I", "ii", "V", "I"],
    ],
    "blues": [
        ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
    ],
}


# Mood modifiers: intervals to add/substitute
_MOOD_MAP = {
    "bright": {"prefer": ["I", "IV", "V"], "avoid": ["vi", "ii"]},
    "dark": {"prefer": ["vi", "ii", "iii"], "avoid": ["I", "IV"]},
    "tense": {"prefer": ["V7", "viio", "bII"], "avoid": ["I", "IV"]},
}



# ---------------------------------------------------------------------------
# Enharmonic intelligence (v86.0)
# ---------------------------------------------------------------------------

_ENHARMONIC_MAP = {
    "C": "C",
    "C#": "Db",
    "Db": "C#",
    "D": "D",
    "D#": "Eb",
    "Eb": "D#",
    "E": "Fb",
    "Fb": "E",
    "F": "F",
    "F#": "Gb",
    "Gb": "F#",
    "G": "G",
    "G#": "Ab",
    "Ab": "G#",
    "A": "A",
    "A#": "Bb",
    "Bb": "A#",
    "B": "Cb",
    "Cb": "B",
}


_KEY_SIGNATURES = {
    "C": [],
    "G": ["F#"],
    "D": ["F#", "C#"],
    "A": ["F#", "C#", "G#"],
    "E": ["F#", "C#", "G#", "D#"],
    "B": ["F#", "C#", "G#", "D#", "A#"],
    "F#": ["F#", "C#", "G#", "D#", "A#", "E#"],
    "F": ["Bb"],
    "Bb": ["Bb", "Eb"],
    "Eb": ["Bb", "Eb", "Ab"],
    "Ab": ["Bb", "Eb", "Ab", "Db"],
    "Db": ["Bb", "Eb", "Ab", "Db", "Gb"],
    "Gb": ["Bb", "Eb", "Ab", "Db", "Gb", "Cb"],
}



# ---------------------------------------------------------------------------
# Harmonic voice independence (v89.0)
# ---------------------------------------------------------------------------


def _motion_type(
    a1: int,
    a2: int,
    b1: int,
    b2: int,
) -> str:
    """Classify the motion between two voice pairs."""
    dir_a = 1 if a2 > a1 else (-1 if a2 < a1 else 0)
    dir_b = 1 if b2 > b1 else (-1 if b2 < b1 else 0)
    if dir_a == 0 and dir_b == 0:
        return "static"
    elif dir_a == 0 or dir_b == 0:
        return "oblique"
    elif dir_a == dir_b:
        return "similar"
    else:
        return "contrary"



# ---------------------------------------------------------------------------
# Chord voicing database (v95.0)
# ---------------------------------------------------------------------------

_VOICING_DB: dict[str, list[list[int]]] = {
    "maj": [
        [0, 4, 7],  # root position
        [4, 7, 12],  # first inversion
        [7, 12, 16],  # second inversion
        [0, 7, 16],  # open voicing
    ],
    "min": [
        [0, 3, 7],
        [3, 7, 12],
        [7, 12, 15],
        [0, 7, 15],
    ],
    "dom7": [
        [0, 4, 7, 10],
        [4, 7, 10, 12],
        [0, 4, 10],  # shell voicing
        [10, 16, 19],  # spread
    ],
    "maj7": [
        [0, 4, 7, 11],
        [4, 7, 11, 12],
        [0, 4, 11],  # shell
        [11, 16, 19],  # spread
    ],
    "min7": [
        [0, 3, 7, 10],
        [3, 7, 10, 12],
        [0, 3, 10],  # shell
        [10, 15, 19],  # spread
    ],
    "dim": [[0, 3, 6], [3, 6, 12]],
    "aug": [[0, 4, 8], [4, 8, 12]],
    "sus4": [[0, 5, 7], [5, 7, 12]],
    "sus2": [[0, 2, 7], [2, 7, 12]],
}



# ---------------------------------------------------------------------------
# Chord symbol formatter (v107.0)
# ---------------------------------------------------------------------------

_SHAPE_SYMBOLS = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "+",
    "dom7": "7",
    "maj7": "maj7",
    "min7": "m7",
    "dim7": "dim7",
    "aug7": "+7",
    "sus4": "sus4",
    "sus2": "sus2",
    "dom9": "9",
    "min9": "m9",
    "maj9": "maj9",
    "min11": "m11",
    "dom13": "13",
}



# ---------------------------------------------------------------------------
# Scale degree naming (v116.0)
# ---------------------------------------------------------------------------

_DEGREE_NAMES = {
    0: "1 (tonic)",
    1: "b2",
    2: "2",
    3: "b3 (minor 3rd)",
    4: "3 (major 3rd)",
    5: "4",
    6: "#4/b5 (tritone)",
    7: "5",
    8: "b6",
    9: "6",
    10: "b7",
    11: "7 (major 7th)",
}

