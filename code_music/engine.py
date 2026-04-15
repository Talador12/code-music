"""Core music primitives: Note, Chord, Beat, Track, Song."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

# Equal-temperament MIDI note number -> frequency (A4 = 440 Hz)
A4_FREQ = 440.0
A4_MIDI = 69

# ---------------------------------------------------------------------------
# Note duration constants  (1 beat = quarter note at any BPM)
# ---------------------------------------------------------------------------
WHOLE = 4.0
HALF = 2.0
QUARTER = 1.0
EIGHTH = 0.5
SIXTEENTH = 0.25
THIRTY_SECOND = 0.125
SIXTY_FOURTH = 0.0625

DOTTED_WHOLE = 6.0
DOTTED_HALF = 3.0
DOTTED_QUARTER = 1.5
DOTTED_EIGHTH = 0.75
DOTTED_SIXTEENTH = 0.375

DOUBLE_DOTTED_HALF = 3.5
DOUBLE_DOTTED_QUARTER = 1.75

# ---------------------------------------------------------------------------
# Note duration constants — all relative to one beat (quarter note = 1.0)
# ---------------------------------------------------------------------------

WHOLE = 4.0  # whole note
HALF = 2.0  # half note
QUARTER = 1.0  # quarter note (the reference beat)
EIGHTH = 0.5  # eighth note
SIXTEENTH = 0.25  # sixteenth note
THIRTY_SECOND = 0.125  # 32nd note
SIXTY_FOURTH = 0.0625  # 64th note

# Dotted values (1.5× the base duration)
DOTTED_WHOLE = 6.0
DOTTED_HALF = 3.0
DOTTED_QUARTER = 1.5
DOTTED_EIGHTH = 0.75
DOTTED_SIXTEENTH = 0.375

# Double-dotted (1.75× the base)
DOUBLE_DOTTED_QUARTER = 1.75
DOUBLE_DOTTED_HALF = 3.5


# ---------------------------------------------------------------------------
# Dynamic markings — standard velocity values for musical dynamics
# ---------------------------------------------------------------------------
PPPP = 0.08  # pianississimo — barely audible
PPP = 0.15  # pianissimo piano — very very soft
PP = 0.25  # pianissimo — very soft
P = 0.35  # piano — soft
MP = 0.50  # mezzo-piano — moderately soft
MF = 0.62  # mezzo-forte — moderately loud
F = 0.75  # forte — loud
FF = 0.85  # fortissimo — very loud
FFF = 0.92  # forte fortissimo — very very loud
FFFF = 0.98  # fortississimo — as loud as possible without distortion
# Accent modifiers (multiply with base dynamic)
SFZ = 1.0  # sforzando — sudden strong accent
FP = 0.40  # forte-piano — loud attack, immediately soft
SFP = 0.45  # sforzando-piano — accented then soft
FZ = 0.95  # forzando — forced accent
RF = 0.88  # rinforzando — reinforced

# Velocity curve presets for different instrument behaviors
VELOCITY_CURVES = {
    "linear": lambda v: v,
    "exponential": lambda v: v**2.0,
    "logarithmic": lambda v: v**0.5,
    "s_curve": lambda v: 3 * v**2 - 2 * v**3,
    "piano": lambda v: v**1.5,  # harder touch = more volume
    "organ": lambda v: 0.6 + v * 0.4,  # always audible, less range
    "percussion": lambda v: v**0.7,  # sensitive to light touch
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Enharmonic aliases — normalized when resolving pitch names
ENHARMONICS: dict[str, str] = {
    "Db": "C#",
    "Eb": "D#",
    "Fb": "E",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
    "E#": "F",
    "B#": "C",
}

# Interval shortcuts (semitones from root)
INTERVALS = {
    "unison": 0,
    "m2": 1,
    "M2": 2,
    "m3": 3,
    "M3": 4,
    "P4": 5,
    "tritone": 6,
    "P5": 7,
    "m6": 8,
    "M6": 9,
    "m7": 10,
    "M7": 11,
    "octave": 12,
}

# Common chord shapes as semitone offsets from root
CHORD_SHAPES = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    # Jazz extensions (commonly needed)
    "min7b5": [0, 3, 6, 10],  # half-diminished / ø chord
    "dim7": [0, 3, 6, 9],  # fully diminished
    "maj6": [0, 4, 7, 9],  # major 6th
    "min6": [0, 3, 7, 9],  # minor 6th
    "7sus4": [0, 5, 7, 10],  # dominant 7 suspended
    "maj9": [0, 4, 7, 11, 14],  # major 9th
    "min9": [0, 3, 7, 10, 14],  # minor 9th
    "dom9": [0, 4, 7, 10, 14],  # dominant 9th
    "7b9": [0, 4, 7, 10, 13],  # dominant b9 (jazz tension)
    "7#9": [0, 4, 7, 10, 15],  # dominant #9 (Hendrix chord)
}

# Scale patterns (semitone intervals from root)
SCALES = {
    # ── Diatonic modes ────────────────────────────────────────────────────────
    "major": [0, 2, 4, 5, 7, 9, 11],  # Ionian
    "minor": [0, 2, 3, 5, 7, 8, 10],  # Natural / Aeolian
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    # ── Minor variants ────────────────────────────────────────────────────────
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],  # raised 7th
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],  # raised 6th and 7th (ascending)
    "phrygian_dominant": [0, 1, 4, 5, 7, 8, 10],  # Spanish / flamenco
    # ── Pentatonic ────────────────────────────────────────────────────────────
    "pentatonic": [0, 2, 4, 7, 9],  # Major pentatonic
    "pentatonic_minor": [0, 3, 5, 7, 10],  # Minor pentatonic
    "pentatonic_blues": [0, 3, 5, 6, 7, 10],  # Minor pentatonic + blue note
    # ── Blues ─────────────────────────────────────────────────────────────────
    "blues": [0, 3, 5, 6, 7, 10],  # Classic blues hexatonic
    "blues_major": [0, 2, 3, 4, 7, 9],  # Major blues
    # ── Symmetric scales ──────────────────────────────────────────────────────
    "whole_tone": [0, 2, 4, 6, 8, 10],  # 6 notes, all whole steps
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11],  # Half-whole diminished (8 notes)
    "diminished_hw": [0, 1, 3, 4, 6, 7, 9, 10],  # Whole-half diminished
    "augmented": [0, 3, 4, 7, 8, 11],  # Augmented / hexatonic
    # ── Bebop scales ─────────────────────────────────────────────────────────
    "bebop_major": [0, 2, 4, 5, 7, 8, 9, 11],  # Major + chromatic passing tone
    "bebop_dominant": [0, 2, 4, 5, 7, 9, 10, 11],  # Mixolydian + maj 7
    "bebop_minor": [0, 2, 3, 4, 5, 7, 9, 10],  # Dorian + maj 3
    # ── World / ethnic scales ─────────────────────────────────────────────────
    "hungarian_minor": [0, 2, 3, 6, 7, 8, 11],  # Gypsy minor
    "hungarian_major": [0, 3, 4, 6, 7, 9, 10],
    "arabic": [0, 1, 4, 5, 7, 8, 11],  # Double harmonic / Byzantine
    "japanese": [0, 1, 5, 7, 8],  # Hirajoshi
    "hirajoshi": [0, 2, 3, 7, 8],  # Pentatonic variant
    "in_sen": [0, 1, 5, 7, 10],  # Japanese in-sen
    "yo": [0, 2, 5, 7, 9],  # Japanese yo scale
    "persian": [0, 1, 4, 5, 6, 8, 11],
    "enigmatic": [0, 1, 4, 6, 8, 10, 11],  # Verdi's enigmatic scale
    "neapolitan_major": [0, 1, 3, 5, 7, 9, 11],
    "neapolitan_minor": [0, 1, 3, 5, 7, 8, 11],
    # ── Modal jazz ────────────────────────────────────────────────────────────
    "lydian_dominant": [0, 2, 4, 6, 7, 9, 10],  # Lydian b7 — jazz / fusion
    "super_locrian": [0, 1, 3, 4, 6, 8, 10],  # Altered scale (7th mode melodic minor)
    "lydian_augmented": [0, 2, 4, 6, 8, 9, 11],  # 3rd mode melodic minor
    "locrian_natural2": [0, 2, 3, 5, 6, 8, 10],  # Half-diminished / 6th mode mel. minor
    # ── Additional modes ──────────────────────────────────────────────────────
    "aeolian": [0, 2, 3, 5, 7, 8, 10],  # = natural minor (alias)
    "acoustic": [0, 2, 4, 6, 7, 9, 10],  # Lydian dominant / overtone scale
    "altered": [0, 1, 3, 4, 6, 8, 10],  # Super Locrian / diminished whole tone
    "half_diminished": [0, 2, 3, 5, 6, 8, 10],  # Locrian natural 2
    # ── Additional world scales ──────────────────────────────────────────────
    "double_harmonic": [0, 1, 4, 5, 7, 8, 11],  # Byzantine / Arabic (alt name)
    "spanish_gypsy": [0, 1, 4, 5, 7, 8, 10],  # Phrygian dominant (alt name)
    "arabian": [0, 2, 4, 5, 6, 8, 10],  # Major locrian
    "balinese": [0, 1, 3, 7, 8],  # Indonesian pelog variant
    "chinese": [0, 4, 6, 7, 11],  # Pentatonic with tritone
    "egyptian": [0, 2, 5, 7, 10],  # Suspended pentatonic
    "iwato": [0, 1, 5, 6, 10],  # Japanese (dark)
    "kumoi": [0, 2, 3, 7, 9],  # Japanese pentatonic variant
    "pelog": [0, 1, 3, 7, 8],  # Indonesian gamelan
    "prometheus": [0, 2, 4, 6, 9, 10],  # Scriabin's mystic scale
    "tritone": [0, 1, 4, 6, 7, 10],  # Two augmented triads a tritone apart
    # ── Chromatic ─────────────────────────────────────────────────────────────
    "chromatic": list(range(12)),
}


# Chord shape additions
CHORD_SHAPES.update(
    {
        "9": [0, 4, 7, 10, 14],
        "min9": [0, 3, 7, 10, 14],
        "add9": [0, 4, 7, 14],
        "maj9": [0, 4, 7, 11, 14],
        "6": [0, 4, 7, 9],
        "min6": [0, 3, 7, 9],
        "6/9": [0, 4, 7, 9, 14],
        "11": [0, 4, 7, 10, 14, 17],
        "13": [0, 4, 7, 10, 14, 17, 21],
        "power": [0, 7],
        "flat5": [0, 4, 6],
        "aug7": [0, 4, 8, 10],
        # Extended jazz voicings (v169)
        "min11": [0, 3, 7, 10, 14, 17],
        "min13": [0, 3, 7, 10, 14, 17, 21],
        "7#11": [0, 4, 7, 10, 18],  # Lydian dominant
        "maj7#11": [0, 4, 7, 11, 18],  # Lydian
        "7alt": [0, 4, 7, 10, 13, 15],  # Altered dominant (b9 #9)
        "dim_maj7": [0, 3, 6, 11],  # Diminished major 7th
        "aug_maj7": [0, 4, 8, 11],  # Augmented major 7th
        "quartal": [0, 5, 10, 15],  # Stacked 4ths (McCoy Tyner)
        # ── v170 expansions ──────────────────────────────────────────────
        # Quintal / extended quartal stacks
        "quintal": [0, 7, 14, 21],  # Stacked 5ths (Hindemith, Debussy)
        "quartal5": [0, 5, 10, 15, 20],  # 5-note quartal stack
        "quintal4": [0, 7, 14, 21],  # 4-note quintal stack (alias)
        # Polychords (two triads superimposed)
        "poly_C_D": [0, 4, 7, 2, 6, 9],  # C + D = Stravinsky / Petrushka
        "poly_C_Gb": [0, 4, 7, 6, 10, 13],  # C + Gb = tritone polychord
        "poly_C_E": [0, 4, 7, 4, 8, 11],  # C + E = Messiaen color
        # Clusters (adjacent semitones - Cowell, Ligeti, Penderecki)
        "cluster3": [0, 1, 2],  # 3-note chromatic cluster
        "cluster4": [0, 1, 2, 3],  # 4-note chromatic cluster
        "cluster5": [0, 1, 2, 3, 4],  # 5-note chromatic cluster
        "diatonic_cluster3": [0, 2, 4],  # 3-note diatonic cluster
        "diatonic_cluster4": [0, 2, 4, 5],  # 4-note diatonic cluster
        # Slash chords (voicing with specific bass note offset)
        "maj_inv1_bass": [-8, 0, 4, 7],  # C/E (E in bass, -8 from root)
        "maj_inv2_bass": [-5, 0, 4, 7],  # C/G (G in bass)
        "min_inv1_bass": [-9, 0, 3, 7],  # Cm/Eb
        # Extended altered dominants
        "7b5": [0, 4, 6, 10],  # Dominant flat 5
        "7#5": [0, 4, 8, 10],  # Dominant sharp 5
        "7b5b9": [0, 4, 6, 10, 13],  # Altered tritone sub voicing
        "7#5#9": [0, 4, 8, 10, 15],  # Full altered dominant
        "7b13": [0, 4, 7, 10, 20],  # Dominant flat 13
        "9#11": [0, 4, 7, 10, 14, 18],  # Lydian dominant 9th
        "13#11": [0, 4, 7, 10, 14, 18, 21],  # Full lydian dominant
        # More jazz / neo-soul voicings
        "min_maj7": [0, 3, 7, 11],  # Minor major 7th (Bond chord)
        "min_add9": [0, 3, 7, 14],  # Minor add 9 (Radiohead)
        "maj_add9": [0, 4, 7, 14],  # Major add 9 (same as add9)
        "7sus2": [0, 2, 7, 10],  # Dominant 7 sus 2
        "9sus4": [0, 5, 7, 10, 14],  # 9 sus 4 (gospel / neo-soul)
        "min7_add11": [0, 3, 7, 10, 17],  # Minor 7 add 11
        "maj7_add13": [0, 4, 7, 11, 21],  # Major 7 add 13
        # Spectral / extended harmony (Grisey, Murail, Saariaho)
        "harmonic7": [0, 12, 19, 24, 28],  # Partials 1-5 from harmonic series
        "harmonic9": [0, 12, 19, 24, 28, 31],  # Partials 1-6
        "spectral_cluster": [0, 12, 19, 24, 28, 31, 34],  # Partials 1-7
        # Messiaen modes of limited transposition chords
        "messiaen_mode2": [0, 1, 3, 4, 6, 7, 9, 10],  # Octatonic
        "messiaen_mode3": [0, 2, 3, 4, 6, 7, 8, 10, 11],  # 9-note scale
        # Mu chord (Steely Dan) and other pop extensions
        "mu": [0, 2, 4, 7],  # Major with added 2nd
        "mu7": [0, 2, 4, 7, 11],  # Mu chord with major 7th
        # ── Jazz / Blues / Funk / Neo-soul voicings ──────────────────────
        # Blues-specific
        "dom7#9": [0, 4, 7, 10, 15],  # Hendrix chord (alias for 7#9)
        "dom7b9#9": [0, 4, 7, 10, 13, 15],  # tritone crunch
        "dom9#11": [0, 4, 7, 10, 14, 18],  # Lydian dominant 9th
        "blues_maj": [0, 3, 4, 7],  # major with blue note (b3 grace)
        # Funk one-chord vamp voicings
        "min7_funk": [0, 3, 7, 10, 14, 17],  # min11 - the funk default
        "dom7_funk": [0, 4, 7, 10, 14],  # 9th - JB / Herbie
        "min9_funk": [0, 3, 7, 10, 14],  # same as min9 but named for funk
        # Neo-soul / R&B / Gospel
        "maj9#11": [0, 4, 7, 11, 14, 18],  # Erykah Badu / D'Angelo
        "min11_neo": [0, 3, 5, 7, 10, 14],  # open neo-soul voicing
        "dom7#9#5": [0, 4, 8, 10, 15],  # altered funk chord
        "dim_add9": [0, 3, 6, 14],  # diminished + 9th (gospel passing)
        "maj7#5": [0, 4, 8, 11],  # augmented major 7 (Stevie Wonder)
        "min_add11": [0, 3, 7, 17],  # minor add 11 (neo-soul open)
        # Bossa nova / Latin jazz
        "6_9": [0, 4, 7, 9, 14],  # alias for 6/9 (bossa standard)
        "min6_9": [0, 3, 7, 9, 14],  # minor 6/9 (Jobim)
        "dom7b9_latin": [0, 4, 7, 10, 13],  # b9 for Latin ii-V
        "dom7#11_latin": [0, 4, 7, 10, 18],  # #11 for Latin V
        # Chill / Lofi / Ambient
        "maj7_open": [0, 7, 11, 16],  # wide maj7 (lofi Rhodes)
        "min7_open": [0, 7, 10, 15],  # wide min7 (lofi keys)
        "add9_open": [0, 7, 14, 16],  # wide add9 (ambient)
        "sus4_add9": [0, 5, 7, 14],  # sus4 with 9th (ambient floating)
        "maj7sus2": [0, 2, 7, 11],  # major 7 sus 2 (dreamy)
        # Big band section voicings (close position for sax/brass soli)
        "dom13": [0, 4, 7, 10, 14, 17, 21],  # full 13th
        "dom13_shell": [0, 4, 10, 21],  # root-3-7-13 (tight soli)
        "min13_shell": [0, 3, 10, 21],  # min root-b3-b7-13
        "dom7_drop24": [0, 4, -3, 10],  # drop 2-4 voicing
    }
)


def midi_to_freq(midi: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return A4_FREQ * (2.0 ** ((midi - A4_MIDI) / 12.0))


def normalize_note_name(name: str) -> str:
    """Normalize a note name to its canonical sharp-based form.

    Handles enharmonic equivalents (Db→C#, Bb→A#, E#→F, etc.)
    and mixed case input. Returns an entry from NOTE_NAMES.

    Raises ValueError for unrecognized names.
    """
    # Capitalize first letter, keep rest as-is for '#'/'b'
    cleaned = name[0].upper() + name[1:]
    # Resolve enharmonic aliases
    for alias, canon in ENHARMONICS.items():
        if cleaned == alias:
            cleaned = canon
            break
    if cleaned not in NOTE_NAMES:
        raise ValueError(f"Unknown note name: {name!r}")
    return cleaned


def note_name_to_midi(name: str, octave: int = 4) -> int:
    """Convert e.g. 'C#' + octave 4 to MIDI note number."""
    canon = normalize_note_name(name)
    semitone = NOTE_NAMES.index(canon)
    return (octave + 1) * 12 + semitone


def midi_to_note_name(midi_num: int) -> tuple[str, int]:
    """Convert a MIDI note number to (note_name, octave).

    Example::

        >>> midi_to_note_name(60)
        ('C', 4)
        >>> midi_to_note_name(61)
        ('C#', 4)
    """
    octave = (midi_num // 12) - 1
    semitone = midi_num % 12
    return NOTE_NAMES[semitone], octave


@dataclass
class Note:
    """A single pitched note with duration, velocity, and articulation.

    Attributes:
        pitch: Note name (e.g. 'A', 'C#') or MIDI number or None for rest.
        octave: Octave number (4 = middle octave, A4 = 440 Hz).
        duration: Duration in beats (1.0 = quarter note at current BPM).
        velocity: 0.0-1.0 volume/intensity.
        articulation: Playing technique that changes timbre, not just duration.
            None = default for the instrument. Common values:
            Strings: "arco", "pizzicato", "tremolo", "harmonics", "col_legno",
                     "sul_ponticello", "sul_tasto", "spiccato", "con_sordino"
            Brass:   "open", "muted", "harmon_mute", "cup_mute", "stopped",
                     "flutter_tongue", "sforzando"
            Woodwind: "normal", "flutter_tongue", "overblown", "subtone",
                      "slap_tongue"
            Keys:    "normal", "damped", "prepared", "una_corda", "tre_corde"
            Percussion: "stick", "mallet", "brush", "rod", "hot_rod",
                        "rimshot", "cross_stick", "rim_click", "dead_stroke",
                        "flam", "roll"
    """

    pitch: str | int | None  # name, MIDI int, or None for rest
    octave: int = 4
    duration: float = 1.0  # beats
    velocity: float = 0.8
    articulation: str | None = None

    @property
    def freq(self) -> float | None:
        """Return frequency in Hz, or None for a rest."""
        if self.pitch is None:
            return None
        if isinstance(self.pitch, int):
            return midi_to_freq(self.pitch)
        return midi_to_freq(note_name_to_midi(self.pitch, self.octave))

    @property
    def midi(self) -> int | None:
        if self.pitch is None:
            return None
        if isinstance(self.pitch, int):
            return self.pitch
        return note_name_to_midi(self.pitch, self.octave)

    # Convenience constructors
    @classmethod
    def rest(cls, duration: float = 1.0) -> "Note":
        return cls(pitch=None, duration=duration)

    def __repr__(self) -> str:
        p = "rest" if self.pitch is None else f"{self.pitch}{self.octave}"
        return f"Note({p}, dur={self.duration}, vel={self.velocity:.2f})"


@dataclass
class Chord:
    """Multiple notes played simultaneously.

    Attributes:
        root: Root note name (e.g. 'C').
        shape: Chord quality key from CHORD_SHAPES or list of semitone offsets.
        octave: Base octave of the root.
        duration: Duration in beats.
        velocity: 0.0–1.0.
    """

    root: str
    shape: str | list[int] = "maj"
    octave: int = 4
    duration: float = 2.0
    velocity: float = 0.7

    @property
    def notes(self) -> list[Note]:
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else self.shape
        root_midi = note_name_to_midi(self.root, self.octave)
        return [
            Note(pitch=root_midi + offset, duration=self.duration, velocity=self.velocity)
            for offset in offsets
        ]

    def invert(self, n: int = 1) -> "Chord":
        """Return an inverted voicing of this chord.

        Inversion n moves the bottom n notes up an octave:
          0 = root position  (C E G)
          1 = first inversion (E G C)
          2 = second inversion (G C E)

        Args:
            n: Inversion number (0 = root, 1 = first, 2 = second, etc.)

        Example::

            Chord("C", "maj", 4).invert(1)   # E in bass
            Chord("G", "dom7", 3).invert(2)  # D in bass
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)
        n = n % len(offsets)  # wrap around
        # Move the bottom n notes up an octave
        rotated = offsets[n:] + [o + 12 for o in offsets[:n]]
        # Normalize so the lowest offset is 0 relative to new bass
        base = rotated[0]
        normalized = [o - base for o in rotated]
        # Adjust root midi to reflect new bass note
        root_midi = note_name_to_midi(self.root, self.octave) + base
        new_root = NOTE_NAMES[root_midi % 12]
        new_octave = root_midi // 12 - 1
        return Chord(
            root=new_root,
            shape=normalized,
            octave=new_octave,
            duration=self.duration,
            velocity=self.velocity,
        )

    def spread(self, octave_spread: int = 1) -> "Chord":
        """Return an open voicing — spread notes across more octaves.

        Close voicing:  C E G      (all within one octave)
        Open voicing:   C G E      (notes spread across two octaves)

        The algorithm takes every other note and moves it up `octave_spread`
        octaves. This creates wider intervals between adjacent notes, giving
        the chord an open, orchestral quality vs the dense close voicing.

        Args:
            octave_spread: How many octaves to spread alternate notes (default 1).

        Example::

            Chord("C", "maj7", 3).spread()   # C G E B → open voicing
            Chord("A", "min9", 3).spread(2)  # very wide, orchestral
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)
        spread_offsets = list(offsets)
        for i in range(1, len(spread_offsets), 2):
            spread_offsets[i] += 12 * octave_spread
        return Chord(
            root=self.root,
            shape=spread_offsets,
            octave=self.octave,
            duration=self.duration,
            velocity=self.velocity,
        )

    def drop2(self) -> "Chord":
        """Return a drop-2 voicing — move the 2nd-from-top note down an octave.

        Drop-2 is the standard jazz guitar/piano voicing. It opens up the
        chord without making it as wide as full spread(). Very common in
        jazz comping.

        Example::

            Chord("C", "maj7", 4).drop2()   # close: C E G B → drop2: G C E B
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)
        if len(offsets) < 3:
            return Chord(self.root, list(offsets), self.octave, self.duration, self.velocity)
        d2 = list(offsets)
        # Move 2nd from top down an octave
        idx = len(d2) - 2
        d2[idx] -= 12
        d2.sort()
        return Chord(
            root=self.root,
            shape=d2,
            octave=self.octave,
            duration=self.duration,
            velocity=self.velocity,
        )

    def close(self) -> "Chord":
        """Return a close (tight) voicing — all notes within one octave.

        Useful after spread() or drop2() to return to compact voicing.
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)
        # Bring all notes into the range 0-11 (one octave)
        closed = sorted(set(o % 12 for o in offsets))
        return Chord(
            root=self.root,
            shape=closed,
            octave=self.octave,
            duration=self.duration,
            velocity=self.velocity,
        )

    def voicings(self) -> dict[str, "Chord"]:
        """Return a dict of all common voicings of this chord.

        Keys:
            "root"    — root position (default, unchanged)
            "inv1"    — first inversion
            "inv2"    — second inversion
            "drop2"   — drop-2 voicing (jazz guitar/piano standard)
            "spread"  — open voicing (alternate notes up an octave)
            "close"   — close voicing (all notes within one octave)
            "shell"   — shell voicing (root + 3rd + 7th only, no 5th)

        Shell voicing is only available for chords with 4+ notes (7th chords).
        For triads, "shell" returns root + 3rd only.

        Example::

            v = Chord("C", "maj7", 3).voicings()
            pad.add(v["drop2"])     # jazz voicing
            pad.add(v["spread"])    # orchestral voicing
            pad.add(v["shell"])     # minimal comping voicing

        Returns:
            Dict of name → Chord for each voicing.
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)

        result: dict[str, Chord] = {
            "root": self,
            "inv1": self.invert(1),
            "inv2": self.invert(2),
            "drop2": self.drop2(),
            "spread": self.spread(),
            "close": self.close(),
        }

        # Shell voicing: root + 3rd + 7th (skip the 5th)
        if len(offsets) >= 4:
            shell_offsets = [offsets[0], offsets[1], offsets[3]]
        elif len(offsets) >= 2:
            shell_offsets = [offsets[0], offsets[1]]
        else:
            shell_offsets = list(offsets)

        result["shell"] = Chord(
            root=self.root,
            shape=shell_offsets,
            octave=self.octave,
            duration=self.duration,
            velocity=self.velocity,
        )

        return result

    def shell_voicing(self, bass: str | None = None, bass_octave: int | None = None) -> "Chord":
        """Return a shell voicing: root + 3rd + 7th, skip the 5th.

        Shell voicings are the standard jazz comping approach — three notes
        that define the chord quality without the 5th (which adds density
        but little harmonic information).

        The optional ``bass`` parameter lets you put a different note in the
        bass — useful for slash chords (C/E, G/B) and walking bass lines
        where the pianist plays a rootless voicing above.

        Args:
            bass:        Optional bass note name (e.g. "E" for C/E).
                         If None, the chord root is the bass.
            bass_octave: Octave for the bass note (default: self.octave - 1).

        Returns:
            A new Chord with the shell voicing (custom offsets).

        Examples::

            Chord("C", "maj7", 3).shell_voicing()
            # → C E B  (root + 3rd + 7th)

            Chord("C", "maj7", 3).shell_voicing(bass="E")
            # → E C B  (E in bass — first inversion feel)

            Chord("G", "dom7", 3).shell_voicing(bass="F", bass_octave=2)
            # → F(2) G B F  (F bass, shell above)
        """
        offsets = CHORD_SHAPES[self.shape] if isinstance(self.shape, str) else list(self.shape)

        # Build shell: root(0) + 3rd(1) + 7th(3) for 4+ note chords
        if len(offsets) >= 4:
            shell = [offsets[0], offsets[1], offsets[3]]
        elif len(offsets) >= 2:
            shell = [offsets[0], offsets[1]]
        else:
            shell = list(offsets)

        if bass is not None:
            # Calculate bass note offset relative to chord root
            root_midi = note_name_to_midi(self.root, self.octave)
            b_oct = bass_octave if bass_octave is not None else self.octave - 1
            bass_midi = note_name_to_midi(bass, b_oct)
            bass_offset = bass_midi - root_midi
            # Put bass at the bottom, shell above
            new_offsets = [bass_offset] + shell
            return Chord(
                root=self.root,
                shape=new_offsets,
                octave=self.octave,
                duration=self.duration,
                velocity=self.velocity,
            )

        return Chord(
            root=self.root,
            shape=shell,
            octave=self.octave,
            duration=self.duration,
            velocity=self.velocity,
        )

    def __repr__(self) -> str:
        return f"Chord({self.root}{self.octave} {self.shape}, dur={self.duration})"


@dataclass
class Beat:
    """A single rhythmic slot that holds either a Note or a Chord."""

    event: Note | Chord | None = None  # None = explicit rest beat

    @property
    def duration(self) -> float:
        if self.event is None:
            return 1.0
        return self.event.duration


def scale(
    root: str,
    mode: str = "major",
    octave: int = 4,
    length: int | None = None,
    octaves: int = 1,
) -> list[Note]:
    """Return scale as a list of Notes.

    Args:
        root:    Root note name (e.g. 'C', 'F#').
        mode:    Scale mode key from SCALES.
        octave:  Starting octave.
        length:  Exact number of notes to return (overrides octaves if set).
        octaves: How many octaves to span, ending on the top root note.
                 octaves=1 → C D E F G A B C  (8 notes for major)
                 octaves=2 → C D E F G A B C D E F G A B C (15 notes)
                 The final root note at the top is always included.
    """
    intervals = SCALES[mode]
    root_midi = note_name_to_midi(root, octave)
    notes = []

    if length is not None:
        # Explicit length requested — fill exactly that many notes
        for i in range(length):
            idx = i % len(intervals)
            extra_oct = i // len(intervals)
            notes.append(Note(pitch=root_midi + intervals[idx] + extra_oct * 12))
    else:
        # Play `octaves` complete octaves, always ending on the top root
        steps_per_octave = len(intervals)
        total_steps = steps_per_octave * octaves
        for i in range(total_steps):
            idx = i % steps_per_octave
            extra_oct = i // steps_per_octave
            notes.append(Note(pitch=root_midi + intervals[idx] + extra_oct * 12))
        # Append the final top root note
        notes.append(Note(pitch=root_midi + octaves * 12))

    return notes


# ---------------------------------------------------------------------------
# Composition helpers
# ---------------------------------------------------------------------------

ARP_PATTERNS: dict[str, list[int]] = {
    "up": [0, 1, 2, 3],
    "down": [3, 2, 1, 0],
    "up_down": [0, 1, 2, 3, 2, 1],
    "down_up": [3, 2, 1, 0, 1, 2],
    "random": [0, 2, 1, 3],
    "outside_in": [0, 3, 1, 2],
    "skip": [0, 2, 1, 3],
    "pinky": [0, 1, 2, 3, 2, 3, 2, 1],  # piano pinky technique
}


def arp(
    chord: Chord,
    pattern: str | list[int] = "up",
    rate: float = 0.25,
    octaves: int = 1,
) -> list[Note]:
    """Generate an arpeggio from a Chord.

    Args:
        chord:   Source chord to arpeggiate.
        pattern: Named pattern (see ARP_PATTERNS) or list of note indices.
        rate:    Duration of each arpeggiated note in beats.
        octaves: How many octaves to span (stacks the chord notes upward).

    Returns:
        List of Note objects ready to add to a Track.

    Example::

        tr.extend(arp(Chord("A", "min7", 4), pattern="up_down", rate=0.25))
    """
    base_notes = chord.notes
    # Build multi-octave note pool
    all_notes = []
    for oct_offset in range(octaves):
        for note in base_notes:
            all_notes.append(
                Note(
                    pitch=note.midi + oct_offset * 12 if note.midi is not None else None,
                    duration=rate,
                    velocity=note.velocity,
                )
            )

    raw_indices: list[int] = (
        ARP_PATTERNS.get(pattern, []) if isinstance(pattern, str) else list(pattern)
    )
    result = []
    for idx in raw_indices:
        if isinstance(idx, int) and 0 <= idx < len(all_notes):
            n = all_notes[idx]
            result.append(Note(pitch=n.pitch, duration=rate, velocity=n.velocity))
    return result


def crescendo(notes: list, start_vel: float = 0.2, end_vel: float = 1.0) -> list:
    """Apply a linear velocity crescendo across a list of Notes or Chords.

    Args:
        notes:     Notes or Chords to apply velocity ramp to.
        start_vel: Velocity at the start (0.0–1.0).
        end_vel:   Velocity at the end (0.0–1.0).
    """
    if not notes:
        return notes
    result = []
    n = len(notes)
    for i, item in enumerate(notes):
        v = round(start_vel + (end_vel - start_vel) * (i / max(n - 1, 1)), 3)
        if isinstance(item, Note):
            result.append(
                Note(pitch=item.pitch, octave=item.octave, duration=item.duration, velocity=v)
            )
        elif isinstance(item, Chord):
            result.append(
                Chord(
                    root=item.root,
                    shape=item.shape,
                    octave=item.octave,
                    duration=item.duration,
                    velocity=v,
                )
            )
        else:
            result.append(item)
    return result


def decrescendo(notes: list, start_vel: float = 1.0, end_vel: float = 0.1) -> list:
    """Apply a linear velocity decrescendo (diminuendo) across a list of Notes or Chords."""
    return crescendo(notes, start_vel, end_vel)


def transpose(notes: list[Note], semitones: int) -> list[Note]:
    """Shift a list of notes up or down by a number of semitones.

    Args:
        notes:     Input notes.
        semitones: Positive = up, negative = down.
    """
    result = []
    for note in notes:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
        elif isinstance(note.pitch, int):
            result.append(
                Note(pitch=note.pitch + semitones, duration=note.duration, velocity=note.velocity)
            )
        else:
            midi = note_name_to_midi(note.pitch, note.octave) + semitones
            result.append(Note(pitch=midi, duration=note.duration, velocity=note.velocity))
    return result


def humanize(
    notes: list[Note], vel_spread: float = 0.08, timing_spread: float = 0.02
) -> list[Note]:
    """Add small random variations to velocity and duration for a human feel.

    Args:
        vel_spread:    Max velocity variation (+/-).
        timing_spread: Max duration variation (+/- fraction of beat).
    """
    import random

    result = []
    for note in notes:
        dv = random.uniform(-vel_spread, vel_spread)
        dt = random.uniform(-timing_spread, timing_spread)
        new_vel = max(0.05, min(1.0, note.velocity + dv))
        new_dur = max(0.05, note.duration + dt)
        result.append(
            Note(pitch=note.pitch, octave=note.octave, duration=new_dur, velocity=new_vel)
        )
    return result


def staccato(notes: list[Note], factor: float = 0.5) -> list[Note]:
    """Shorten note durations and tag with staccato articulation.

    Each note's sounding duration is shortened to `factor` of its original,
    with the remaining time becoming silence (rest). The synth also sees the
    "staccato" articulation tag and applies a sharper release envelope.

    Args:
        notes:  List of Notes to articulate.
        factor: 0.0-1.0 - fraction of note duration that sounds (0.5 = half).
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
            continue
        sound_dur = max(0.05, n.duration * factor)
        rest_dur = n.duration - sound_dur
        result.append(
            Note(
                pitch=n.pitch,
                octave=n.octave,
                duration=sound_dur,
                velocity=n.velocity,
                articulation="staccato",
            )
        )
        if rest_dur > 0.01:
            result.append(Note.rest(rest_dur))
    return result


def legato(notes: list[Note], overlap: float = 0.1) -> list[Note]:
    """Extend note durations and tag with legato articulation.

    Each note is lengthened by `overlap` beats so it slightly overlaps the next.
    The synth sees the "legato" tag and uses a slower attack and longer release.

    Args:
        notes:   List of Notes to articulate.
        overlap: Extra duration in beats added to each note.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            result.append(
                Note(
                    pitch=n.pitch,
                    octave=n.octave,
                    duration=n.duration + overlap,
                    velocity=n.velocity,
                    articulation="legato",
                )
            )
    return result


def pizzicato(notes: list[Note]) -> list[Note]:
    """Convert notes to pizzicato articulation: plucked string sound.

    Sets the articulation to "pizzicato" which the synth renders with a
    percussive attack, zero sustain, and reduced harmonics. Much more
    realistic than just shortening the duration.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            result.append(
                Note(
                    pitch=n.pitch,
                    octave=n.octave,
                    duration=n.duration,
                    velocity=n.velocity,
                    articulation="pizzicato",
                )
            )
    return result


# ---------------------------------------------------------------------------
# Tuplet helpers
# ---------------------------------------------------------------------------


def triplet(base: float = QUARTER) -> float:
    """Duration of one note in a triplet filling `base` beats (default: QUARTER).

    Three triplet notes fit in the space of two normal notes.
    triplet(QUARTER) = 0.333  →  three notes per beat
    triplet(HALF)    = 0.667  →  three notes per half note
    """
    return base * 2 / 3


def tuplet(base: float, n: int) -> float:
    """Duration of one note in an n-tuplet filling `base` beats.

    triplet   = tuplet(QUARTER, 3)   → 0.333
    quintuplet= tuplet(QUARTER, 5)   → 0.200
    sextuplet = tuplet(QUARTER, 6)   → 0.167
    septuplet = tuplet(HALF,    7)   → 0.286
    """
    return base / n


def triplets(
    pitches: list, octave: int = 4, base: float = QUARTER, velocity: float = 0.75
) -> list[Note]:
    """Build a list of triplet Notes from pitch names (None = rest).

    Example::

        tr.extend(triplets(['C', 'E', 'G'], octave=4))
    """
    dur = triplet(base)
    return [
        Note(pitch=p, octave=octave, duration=dur, velocity=velocity)
        if p is not None
        else Note.rest(dur)
        for p in pitches
    ]


def tuplets(
    pitches: list, n: int, octave: int = 4, base: float = QUARTER, velocity: float = 0.75
) -> list[Note]:
    """Build a list of n-tuplet Notes from pitch names (None = rest).

    Example::

        tr.extend(tuplets(['C','D','E','F','G'], n=5))   # quintuplet
    """
    dur = tuplet(base, n)
    return [
        Note(pitch=p, octave=octave, duration=dur, velocity=velocity)
        if p is not None
        else Note.rest(dur)
        for p in pitches
    ]


# ---------------------------------------------------------------------------
# Ornaments — rendered as rapid note sequences, idiomatic to jazz/classical
# ---------------------------------------------------------------------------


def trill(
    note: Note, semitones: int = 1, speed: float = THIRTY_SECOND, count: int = 8
) -> list[Note]:
    """Rapid alternation between the note and an auxiliary note above.

    Args:
        note:      Principal note. Its total duration = speed * count.
        semitones: Interval to auxiliary (1 = half-step, 2 = whole-step).
        speed:     Duration of each trill note.
        count:     Number of alternations.

    Example::

        tr.extend(trill(Note('A', 4, HALF), semitones=2, count=8))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    aux = base + semitones
    return [
        Note(pitch=(base if i % 2 == 0 else aux), duration=speed, velocity=note.velocity)
        for i in range(count)
    ]


def mordent(note: Note, semitones: int = 1, speed: float = THIRTY_SECOND) -> list[Note]:
    """Lower mordent: principal → step-below → principal.

    Common Baroque ornament. The two ornament notes steal time from the main.

    Example::

        tr.extend(mordent(Note('E', 5, QUARTER)))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * 2)
    return [
        Note(pitch=base, duration=speed, velocity=note.velocity),
        Note(pitch=base - semitones, duration=speed, velocity=note.velocity * 0.85),
        Note(pitch=base, duration=main_dur, velocity=note.velocity),
    ]


def upper_mordent(note: Note, semitones: int = 1, speed: float = THIRTY_SECOND) -> list[Note]:
    """Upper mordent (Pralltriller): principal → step-above → principal."""
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * 2)
    return [
        Note(pitch=base, duration=speed, velocity=note.velocity),
        Note(pitch=base + semitones, duration=speed, velocity=note.velocity * 0.85),
        Note(pitch=base, duration=main_dur, velocity=note.velocity),
    ]


def turn(note: Note, semitones: int = 1, speed: float = THIRTY_SECOND) -> list[Note]:
    """Turn ornament (~): upper → principal → lower → principal.

    Classic 4-note Classical ornament. Common in Mozart, Haydn.

    Example::

        tr.extend(turn(Note('G', 5, QUARTER)))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * 3)
    return [
        Note(pitch=base + semitones, duration=speed, velocity=note.velocity * 0.9),
        Note(pitch=base, duration=speed, velocity=note.velocity),
        Note(pitch=base - semitones, duration=speed, velocity=note.velocity * 0.85),
        Note(pitch=base, duration=main_dur, velocity=note.velocity),
    ]


def grace_note(
    grace_pitch: str | int, main_note: Note, grace_dur: float = THIRTY_SECOND, grace_octave: int = 4
) -> list[Note]:
    """Acciaccatura (crushed grace note) before the main note.

    The grace note steals its duration from the main note.

    Example::

        tr.extend(grace_note('B', Note('C', 5, QUARTER)))
    """
    stolen = min(grace_dur, main_note.duration * 0.5)
    main_dur = max(SIXTY_FOURTH, main_note.duration - stolen)
    return [
        Note(
            pitch=grace_pitch,
            octave=grace_octave,
            duration=stolen,
            velocity=main_note.velocity * 0.8,
        ),
        Note(
            pitch=main_note.pitch,
            octave=main_note.octave,
            duration=main_dur,
            velocity=main_note.velocity,
        ),
    ]


def doit(
    note: Note, semitones: int = 2, steps: int = 12, speed: float = SIXTY_FOURTH
) -> list[Note]:
    """Jazz doit: smooth upward pitch bend after the attack.

    The pitch rises through many micro-steps for a continuous bend feel.
    More steps = smoother curve. 12 steps with 64th note duration gives
    a fast, smooth scoop that sounds like a real brass player lifting.

    Args:
        note:       Source note.
        semitones:  Total pitch rise in semitones.
        steps:      Number of micro-steps (12+ for smooth, 4 for choppy).
        speed:      Duration per micro-step.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = [Note(pitch=base, duration=main_dur, velocity=note.velocity)]
    for i in range(1, steps + 1):
        # Smooth fractional MIDI pitch (the synth rounds, but small steps = smooth)
        frac = i / steps
        # Exponential curve: starts slow, accelerates (more natural than linear)
        curved_frac = frac**1.5
        pitch = base + round(semitones * curved_frac)
        vel = note.velocity * max(0.15, 1.0 - frac * 0.8)
        result.append(Note(pitch=pitch, duration=speed, velocity=vel))
    return result


def fall(
    note: Note, semitones: int = 3, steps: int = 12, speed: float = SIXTY_FOURTH
) -> list[Note]:
    """Jazz fall: smooth downward pitch bend after the attack.

    The pitch drops through many micro-steps. The velocity fades out
    naturally. More steps = smoother. An exponential curve makes it
    start slow and accelerate, like a real brass fall.

    Args:
        note:       Source note.
        semitones:  Total pitch drop in semitones.
        steps:      Number of micro-steps.
        speed:      Duration per micro-step.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = [Note(pitch=base, duration=main_dur, velocity=note.velocity)]
    for i in range(1, steps + 1):
        frac = i / steps
        curved_frac = frac**1.5
        pitch = base - round(semitones * curved_frac)
        vel = note.velocity * max(0.1, 1.0 - frac * 0.85)
        result.append(Note(pitch=pitch, duration=speed, velocity=vel))
    return result


def flip(note: Note, semitones: int = 2, steps: int = 6, speed: float = SIXTY_FOURTH) -> list[Note]:
    """Jazz flip / scoop: smooth upward approach into the note from below.

    The pitch starts below and curves up to the target. More steps than
    the old 2-step version for a continuous scoop feel.

    Args:
        note:       Target note.
        semitones:  How far below to start the scoop.
        steps:      Number of micro-steps (6+ for smooth).
        speed:      Duration per micro-step.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = []
    for i in range(steps):
        frac = i / steps
        # Starts at base - semitones, curves up to base
        pitch = base - round(semitones * (1.0 - frac**0.7))
        vel = note.velocity * (0.5 + 0.5 * frac)
        result.append(Note(pitch=pitch, duration=speed, velocity=vel))
    result.append(Note(pitch=base, duration=main_dur, velocity=note.velocity))
    return result


def glissando(
    start: Note,
    end_pitch: str | int,
    end_octave: int = 4,
    speed: float = THIRTY_SECOND,
) -> list[Note]:
    """Chromatic glissando: slide through every semitone between two pitches.

    The classic piano glissando (dragging a finger across the keys) or
    trombone slide. Every chromatic note between start and end is sounded.

    Args:
        start:      Starting note (uses its duration for the last note).
        end_pitch:  Target pitch name or MIDI number.
        end_octave: Target octave (if end_pitch is a name).
        speed:      Duration per intermediate note.
    """
    if start.pitch is None:
        return [Note.rest(start.duration)]
    start_midi = start.midi or 0
    end_midi = note_name_to_midi(end_pitch, end_octave) if isinstance(end_pitch, str) else end_pitch
    direction = 1 if end_midi > start_midi else -1
    result = []
    for midi in range(start_midi, end_midi, direction):
        result.append(Note(pitch=midi, duration=speed, velocity=start.velocity * 0.8))
    # Final note gets the remaining duration
    result.append(Note(pitch=end_midi, duration=start.duration, velocity=start.velocity))
    return result


def appoggiatura(note: Note, approach_from: int = 1) -> list[Note]:
    """Appoggiatura: accented non-chord tone that resolves to the main note.

    Unlike the acciaccatura (grace note, as fast as possible), the
    appoggiatura is ON the beat and takes half the main note's duration.
    It leans into the resolution. Beethoven used these constantly.

    Args:
        note:          Main note (the resolution).
        approach_from: Semitones above (+) or below (-) to approach from.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    app_dur = note.duration / 2
    main_dur = note.duration / 2
    return [
        Note(
            pitch=base + approach_from, duration=app_dur, velocity=note.velocity * 1.1
        ),  # accented
        Note(pitch=base, duration=main_dur, velocity=note.velocity),
    ]


def shake(note: Note, semitones: int = 2, speed: float = SIXTEENTH, count: int = 4) -> list[Note]:
    """Jazz shake: wide rapid alternation, idiomatic for brass.

    Like a trill but wider (typically a major 2nd+) and more aggressive.

    Example::

        tr.extend(shake(Note('Bb', 4, HALF), semitones=2, count=6))
    """
    return trill(note, semitones=semitones, speed=speed, count=count)


def prob(note: "Note | Chord | None", p: float = 0.8) -> "Note | Chord | None":
    """Return `note` with probability `p`, otherwise return a rest.

    Useful for generative patterns where notes randomly drop out.

    Args:
        note: Note, Chord, or None to potentially play.
        p:    Probability of playing (0.0–1.0).

    Example::

        tr.extend([prob(Note("A", 4), 0.7) for _ in range(16)])
    """
    import random

    if random.random() < p:
        return note
    dur: float = getattr(note, "duration", 1.0) or 1.0
    return Note.rest(dur)


def euclid(
    hits: int,
    steps: int,
    note: str = "C",
    octave: int = 4,
    duration: float = 0.5,
    rotation: int = 0,
) -> list["Note"]:
    """Generate a Euclidean rhythm — evenly distribute hits across steps.

    The Bjorklund algorithm distributes N onsets as evenly as possible over
    M time slots. Produces rhythms found in world music: tresillo (3,8),
    son clave (5,16), bossa nova (5,16 rot 2), etc.

    Args:
        hits:     Number of active beats (onsets).
        steps:    Total number of time slots.
        note:     Note name for active beats.
        octave:   Note octave.
        duration: Duration of each step in beats.
        rotation: Rotate the pattern by N steps (shifts downbeat).

    Returns:
        List of Notes and rests (rest = Note.rest(duration)).

    Example::

        # Tresillo rhythm (3 hits in 8 slots)
        tr.extend(euclid(3, 8, "C", 4, 0.5))

        # Son clave
        tr.extend(euclid(5, 16, "D", 4, 0.25))

        # Hi-hat pattern (6 of 8)
        hat.extend(euclid(6, 8, "F#", 6, 0.5))
    """
    if hits < 0 or steps <= 0 or hits > steps:
        raise ValueError(f"euclid requires 0 <= hits <= steps > 0, got hits={hits}, steps={steps}")

    # Bjorklund algorithm
    pattern = [1] * hits + [0] * (steps - hits)
    if hits == 0 or hits == steps:
        pass  # trivial cases
    else:
        groups: list[list[int]] = [[b] for b in pattern]
        while True:
            # Split into two groups: the "main" group and the "remainder"
            # Find where the values change
            first_val = groups[0]
            remainder_start = -1
            for i in range(1, len(groups)):
                if groups[i] != first_val:
                    remainder_start = i
                    break
            if remainder_start == -1:
                break
            remainder_count = len(groups) - remainder_start
            if remainder_count <= 1:
                break
            # Distribute remainder onto main
            new_groups: list[list[int]] = []
            main_count = remainder_start
            pairs = min(main_count, remainder_count)
            for i in range(pairs):
                new_groups.append(groups[i] + groups[remainder_start + i])
            # Leftovers from either side
            for i in range(pairs, main_count):
                new_groups.append(groups[i])
            for i in range(pairs, remainder_count):
                new_groups.append(groups[remainder_start + i])
            groups = new_groups
        pattern = [b for g in groups for b in g]

    # Apply rotation
    if rotation != 0:
        rotation = rotation % steps
        pattern = pattern[rotation:] + pattern[:rotation]

    result: list[Note] = []
    for beat in pattern:
        if beat:
            result.append(Note(note, octave, duration))
        else:
            result.append(Note.rest(duration))
    return result


def chord_prog(
    roots: list[str],
    shapes: list[str],
    octave: int = 3,
    duration: float = 4.0,
    velocity: float = 0.65,
) -> list[Chord]:
    """Build a chord progression from parallel lists of roots and shapes.

    Args:
        roots:    List of root note names (e.g. ["A", "F", "C", "G"]).
        shapes:   List of chord shapes (e.g. ["min7", "maj7", "maj", "dom7"]).
        octave:   Base octave for all chords.
        duration: Duration in beats for each chord.
        velocity: Velocity for all chords.

    Example::

        prog = chord_prog(["A","F","C","G"], ["min7","maj7","maj","dom7"])
        pad.extend(prog * 4)  # repeat 4 times
    """
    return [
        Chord(r, s, octave=octave, duration=duration, velocity=velocity)
        for r, s in zip(roots, shapes)
    ]


def generate_melody(
    scale_root: str,
    scale_mode: str = "pentatonic",
    octave: int = 4,
    bars: int = 4,
    bpm: float = 120.0,
    density: float = 0.65,
    seed: int | None = None,
) -> list[Note]:
    """Generate a simple procedural melody from a scale.

    Uses a random walk algorithm with melodic constraints:
    - Prefers stepwise motion (small intervals)
    - Occasionally leaps (wider intervals for interest)
    - Density controls how many 8th-note slots have notes vs rests
    - Phrase endings tend toward longer notes

    Args:
        scale_root:  Root note name.
        scale_mode:  Scale mode (pentatonic, major, minor, dorian, blues, etc.)
        octave:      Central octave for melody.
        bars:        How many bars to generate (4/4).
        bpm:         BPM (used to decide phrase lengths).
        density:     0.0–1.0 — fraction of 8th-note slots that have notes.
        seed:        Random seed for reproducibility.
    """
    import random

    if seed is not None:
        random.seed(seed)

    scale_notes = scale(scale_root, scale_mode, octave)
    # Extend one octave up and one down
    low = [Note(pitch=n.midi - 12) for n in scale_notes if n.midi is not None]
    high = [Note(pitch=n.midi + 12) for n in scale_notes if n.midi is not None]
    pool = low + scale_notes + high

    total_8ths = bars * 8  # 8 eighth notes per bar
    result = []
    pos = len(scale_notes)  # start in the middle register

    i = 0
    while i < total_8ths:
        # Phrase ending: last 2 slots of each bar → longer note
        is_bar_end = (i % 8) >= 6
        if is_bar_end and i < total_8ths - 1:
            # Long note (2–4 8th notes)
            dur_8ths = random.choice([2, 3, 4])
            dur_8ths = min(dur_8ths, total_8ths - i)
            if random.random() < density:
                note = pool[min(max(0, pos), len(pool) - 1)]
                result.append(
                    Note(
                        pitch=note.pitch,
                        duration=dur_8ths * 0.5,
                        velocity=random.uniform(0.55, 0.9),
                    )
                )
            else:
                result.append(Note.rest(dur_8ths * 0.5))
            i += dur_8ths
        elif random.random() > density:
            # Rest
            result.append(Note.rest(0.5))
            i += 1
        else:
            # Play a note — random walk
            step = random.choice([-2, -1, -1, 0, 1, 1, 2, 3])
            pos = max(0, min(len(pool) - 1, pos + step))
            vel = random.uniform(0.5, 0.85)
            result.append(Note(pitch=pool[pos].pitch, duration=0.5, velocity=vel))
            i += 1

    return result


def repeat(events: list, n: int) -> list:
    """Repeat a list of notes/chords/events n times."""
    result = []
    for _ in range(n):
        result.extend(events)
    return result


# ---------------------------------------------------------------------------
# Pitch range utilities — octave shifting and doubling
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Articulation helpers — set the articulation field for synth-aware rendering
# ---------------------------------------------------------------------------


def bend(
    note: Note,
    semitones: float = 2.0,
    speed: float = EIGHTH,
    direction: str = "up",
) -> list[Note]:
    """Guitar-style pitch bend with controllable rate.

    Starts at the written pitch and bends up (or down) to the target
    interval over the bend duration. Then holds. The bread and butter
    of blues and rock guitar. Slow bend = BB King. Fast bend = Hendrix.

    Args:
        note:       Starting note.
        semitones:  How far to bend (0.5=quarter tone, 1=half step, 2=whole step).
        speed:      Duration of the bend portion.
        direction:  "up" (default, standard bend) or "down" (pre-bend release).
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    bend_dur = min(speed, note.duration * 0.5)
    hold_dur = note.duration - bend_dur
    steps = 8
    step_dur = bend_dur / steps
    result = []
    for i in range(steps):
        frac = (i + 1) / steps
        if direction == "down":
            pitch = base + round(semitones * (1.0 - frac))
        else:
            pitch = base + round(semitones * frac)
        result.append(Note(pitch=pitch, duration=step_dur, velocity=note.velocity))
    target = base + round(semitones) if direction == "up" else base
    result.append(Note(pitch=target, duration=hold_dur, velocity=note.velocity))
    return result


def plop(note: Note, semitones: int = 3, steps: int = 6, speed: float = SIXTY_FOURTH) -> list[Note]:
    """Plop: approach from above and fall into the target note.

    The opposite of a scoop/flip. Pitch starts above and drops down to
    the target. Jazz trombone and bass clarinet use this constantly.

    Args:
        note:       Target note.
        semitones:  How far above to start.
        steps:      Number of micro-steps.
        speed:      Duration per step.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = []
    for i in range(steps):
        frac = i / steps
        pitch = base + round(semitones * (1.0 - frac**0.7))
        vel = note.velocity * (0.6 + 0.4 * frac)
        result.append(Note(pitch=pitch, duration=speed, velocity=vel))
    result.append(Note(pitch=base, duration=main_dur, velocity=note.velocity))
    return result


def inverted_turn(note: Note, semitones: int = 1) -> list[Note]:
    """Inverted turn (lower neighbor first): lower-main-upper-main.

    The opposite of a regular turn. Starts below the main note.

    Args:
        note:       Main note.
        semitones:  Interval for neighbor notes.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    dur = note.duration / 4
    return [
        Note(pitch=base - semitones, duration=dur, velocity=note.velocity * 0.85),
        Note(pitch=base, duration=dur, velocity=note.velocity),
        Note(pitch=base + semitones, duration=dur, velocity=note.velocity * 0.85),
        Note(pitch=base, duration=dur, velocity=note.velocity),
    ]


def double_mordent(note: Note, semitones: int = 1, speed: float = THIRTY_SECOND) -> list[Note]:
    """Double mordent: extended rapid alternation (4 alternations instead of 2).

    Args:
        note:       Main note.
        semitones:  Interval to alternate with (1=half step, 2=whole step).
        speed:      Duration of each alternation.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    n_alts = 4
    alt_dur = speed
    main_dur = max(SIXTY_FOURTH, note.duration - alt_dur * n_alts * 2)
    result = []
    for _ in range(n_alts):
        result.append(Note(pitch=base, duration=alt_dur, velocity=note.velocity))
        result.append(Note(pitch=base + semitones, duration=alt_dur, velocity=note.velocity * 0.85))
    result.append(Note(pitch=base, duration=main_dur, velocity=note.velocity))
    return result


def acciaccatura(note: Note, approach_from: int = -1) -> list[Note]:
    """Acciaccatura: crushed grace note, as fast as possible.

    Unlike appoggiatura (on the beat, takes time), the acciaccatura is
    BEFORE the beat and as short as physically possible. It "crushes"
    into the main note. The grace note that steals no time from the
    main note - it steals from the silence before.

    Args:
        note:          Main note.
        approach_from: Semitones below (-) or above (+) for the grace note.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    grace_dur = SIXTY_FOURTH * 0.5  # as short as possible
    return [
        Note(pitch=base + approach_from, duration=grace_dur, velocity=note.velocity * 0.7),
        Note(pitch=base, duration=note.duration, velocity=note.velocity),
    ]


def rip(note: Note, semitones: int = 12, speed: float = SIXTEENTH) -> list[Note]:
    """Brass rip: fast glissando up to a note. Big band shout chorus energy.

    The lead trumpet hits a high note by ripping up from below. Fast,
    aggressive, show-off. The sound of Maynard Ferguson, Cat Anderson,
    and every big band finale.

    Args:
        note:       Target note (the one you rip up to).
        semitones:  How far below to start the rip.
        speed:      Total duration of the rip.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    steps = min(semitones, 16)
    step_dur = speed / steps
    main_dur = max(SIXTY_FOURTH, note.duration - speed)
    result = []
    for i in range(steps):
        frac = i / steps
        pitch = base - semitones + round(semitones * frac)
        vel = note.velocity * (0.5 + 0.5 * frac)
        result.append(Note(pitch=pitch, duration=step_dur, velocity=vel))
    result.append(Note(pitch=base, duration=main_dur, velocity=note.velocity))
    return result


def smear(
    start: Note, end_pitch: str | int, end_octave: int = 4, speed: float = EIGHTH
) -> list[Note]:
    """Brass smear: slow glissando between two notes.

    Slower and more deliberate than a rip. The trombone slide. Used for
    expressive transitions, not flashy arrivals. Duke Ellington brass
    section territory.

    Args:
        start:      Starting note.
        end_pitch:  Target pitch.
        end_octave: Target octave.
        speed:      Duration per step.
    """
    if start.pitch is None:
        return [Note.rest(start.duration)]
    start_midi = start.midi or 0
    end_midi = note_name_to_midi(end_pitch, end_octave) if isinstance(end_pitch, str) else end_pitch
    direction = 1 if end_midi > start_midi else -1
    steps = abs(end_midi - start_midi)
    step_dur = min(speed, start.duration / max(steps, 1))
    result = []
    for i in range(steps):
        midi = start_midi + direction * i
        result.append(Note(pitch=midi, duration=step_dur, velocity=start.velocity))
    result.append(
        Note(
            pitch=end_midi,
            duration=max(SIXTY_FOURTH, start.duration - step_dur * steps),
            velocity=start.velocity,
        )
    )
    return result


def ghost_bend(note: Note, semitones: float = 2.0) -> list[Note]:
    """Ghost bend: bend up before picking, release to written pitch.

    The guitarist bends the string up silently, then picks and releases
    the bend down to the target pitch. Creates a descending wail effect.
    The note STARTS at the bent pitch and falls to the written pitch.

    Args:
        note:       Target note (where the bend releases to).
        semitones:  How far above the bend starts.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    steps = 8
    bend_dur = min(note.duration * 0.3, 0.5)
    step_dur = bend_dur / steps
    hold_dur = note.duration - bend_dur
    result = []
    for i in range(steps):
        frac = i / steps
        pitch = base + round(semitones * (1.0 - frac))
        result.append(Note(pitch=pitch, duration=step_dur, velocity=note.velocity))
    result.append(Note(pitch=base, duration=hold_dur, velocity=note.velocity))
    return result


def messa_di_voce(note: Note, peak_velocity: float = 1.0) -> list[Note]:
    """Messa di voce: pp -> ff -> pp on a single sustained note.

    The ultimate vocal/wind control exercise. Start soft, swell to full
    volume at the midpoint, decay back to soft. A single note that
    demonstrates complete dynamic control. Opera singers train years
    for this. We do it with velocity curves.

    Args:
        note:           The sustained note.
        peak_velocity:  Maximum velocity at the midpoint.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    segments = 8
    seg_dur = note.duration / segments
    base = note.midi or 0
    start_vel = note.velocity * 0.2
    result = []
    for i in range(segments):
        frac = i / (segments - 1)
        # Parabolic curve: peaks at 0.5
        vel = start_vel + (peak_velocity - start_vel) * (1.0 - (2.0 * frac - 1.0) ** 2)
        result.append(Note(pitch=base, duration=seg_dur, velocity=vel))
    return result


def subito(notes: list[Note], dynamic: float, at_index: int = 0) -> list[Note]:
    """Subito dynamic change: sudden shift to a new velocity.

    Subito piano (sudden soft), subito forte (sudden loud). No
    gradual transition - the dynamic changes instantly. Used for
    dramatic contrast. Beethoven's favorite trick.

    Args:
        notes:     Input notes.
        dynamic:   New velocity to apply from at_index onward.
        at_index:  Which note the subito occurs at.
    """
    result = []
    for i, n in enumerate(notes):
        if n.pitch is None:
            result.append(n)
        elif i >= at_index:
            result.append(
                Note(n.pitch, n.octave, n.duration, velocity=dynamic, articulation=n.articulation)
            )
        else:
            result.append(n)
    return result


def sextuplet(notes: list[Note], total_beats: float = 1.0) -> list[Note]:
    """Fit 6 notes into the space of 4 (sextuplet).

    Args:
        notes:        Up to 6 notes (extras are trimmed).
        total_beats:  Total duration to fit them into.
    """
    n = min(len(notes), 6)
    dur = total_beats / 6
    result = []
    for i in range(n):
        src = notes[i]
        if src.pitch is None:
            result.append(Note.rest(dur))
        else:
            result.append(
                Note(
                    src.pitch, src.octave, dur, velocity=src.velocity, articulation=src.articulation
                )
            )
    # Fill remaining with rests
    for _ in range(6 - n):
        result.append(Note.rest(dur))
    return result


def n_tuplet(
    notes: list[Note], n: int = 5, in_space_of: int = 4, total_beats: float = 1.0
) -> list[Note]:
    """Arbitrary n-tuplet: fit N notes in the space of M.

    Quintuplet (5:4), sextuplet (6:4), septuplet (7:4), or any ratio.
    The general-purpose tuplet function that covers everything from
    duplets to undecuplets.

    Args:
        notes:        Input notes (up to n, extras trimmed).
        n:            Number of notes to fit.
        in_space_of:  Number of notes that would normally fill the space.
        total_beats:  Total duration of the space.
    """
    dur = total_beats * in_space_of / (n * in_space_of)  # = total_beats / n
    dur = total_beats / n
    count = min(len(notes), n)
    result = []
    for i in range(count):
        src = notes[i]
        if src.pitch is None:
            result.append(Note.rest(dur))
        else:
            result.append(
                Note(
                    src.pitch, src.octave, dur, velocity=src.velocity, articulation=src.articulation
                )
            )
    for _ in range(n - count):
        result.append(Note.rest(dur))
    return result


def neighbor_tone(
    note: Note, direction: int = 1, semitones: int = 1, speed: float = SIXTEENTH
) -> list[Note]:
    """Insert a neighbor tone: step away and return.

    A non-chord tone that moves one step from the main note and comes
    back. Upper neighbor (direction=1) goes up then returns. Lower
    neighbor (direction=-1) goes down then returns. The most common
    ornamental motion in all of tonal music.

    Args:
        note:       Main note.
        direction:  1 = upper neighbor, -1 = lower neighbor.
        semitones:  Step size (1=chromatic, 2=diatonic whole step).
        speed:      Duration of the neighbor note.
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed)
    return [
        Note(pitch=base, duration=main_dur * 0.5, velocity=note.velocity),
        Note(pitch=base + direction * semitones, duration=speed, velocity=note.velocity * 0.8),
        Note(pitch=base, duration=main_dur * 0.5, velocity=note.velocity),
    ]


def passing_tone(start: Note, end: Note, chromatic: bool = False) -> list[Note]:
    """Insert passing tones between two notes.

    Fill the gap between two pitches with stepwise motion. Diatonic
    passing tones use whole steps. Chromatic passing tones use half
    steps. Makes melodic leaps smooth and connected.

    Args:
        start:     First note.
        end:       Second note.
        chromatic: True = chromatic (half steps), False = whole steps.
    """
    if start.pitch is None or end.pitch is None:
        return [start, end]
    start_midi = start.midi or 0
    end_midi = end.midi or 0
    if start_midi == end_midi:
        return [start, end]

    direction = 1 if end_midi > start_midi else -1
    step = 1 if chromatic else 2
    passing = []
    current = start_midi + direction * step
    while (direction == 1 and current < end_midi) or (direction == -1 and current > end_midi):
        passing.append(current)
        current += direction * step

    if not passing:
        return [start, end]

    total_passing_dur = start.duration * 0.4
    pass_dur = total_passing_dur / len(passing)
    main_dur = start.duration - total_passing_dur

    result = [Note(pitch=start_midi, duration=main_dur, velocity=start.velocity)]
    for p in passing:
        result.append(Note(pitch=p, duration=pass_dur, velocity=start.velocity * 0.75))
    result.append(end)
    return result


def escape_tone(note: Note, next_note: Note, semitones: int = 2) -> list[Note]:
    """Escape tone: step in one direction, leap in the other.

    A non-chord tone that steps away from the current note then leaps
    to the next note instead of stepping back. Creates a brief moment
    of melodic surprise. Less predictable than a neighbor tone.

    Args:
        note:       Current note (the escape steps away from this).
        next_note:  The note that follows (the escape leaps to this).
        semitones:  Step size for the escape.
    """
    if note.pitch is None or next_note.pitch is None:
        return [note, next_note]
    base = note.midi or 0
    target = next_note.midi or 0
    # Step in the opposite direction of the target
    escape_dir = -1 if target > base else 1
    escape_pitch = base + escape_dir * semitones
    escape_dur = note.duration * 0.25
    main_dur = note.duration - escape_dur
    return [
        Note(pitch=base, duration=main_dur, velocity=note.velocity),
        Note(pitch=escape_pitch, duration=escape_dur, velocity=note.velocity * 0.7),
        next_note,
    ]


def anticipation(note: Note, next_note: Note, amount: float = 0.25) -> list[Note]:
    """Anticipation: arrive at the next note early.

    The last portion of the current note's duration plays the NEXT note's
    pitch. Creates forward momentum - the melody leans into what is coming.
    Common in pop, jazz, and any music that wants to feel eager.

    Args:
        note:       Current note (shortened).
        next_note:  Next note (anticipated early).
        amount:     Fraction of current note's duration to anticipate (0.1-0.5).
    """
    if note.pitch is None or next_note.pitch is None:
        return [note, next_note]
    antic_dur = note.duration * amount
    main_dur = note.duration - antic_dur
    target_midi = next_note.midi or 0
    return [
        Note(pitch=note.midi, duration=main_dur, velocity=note.velocity),
        Note(pitch=target_midi, duration=antic_dur, velocity=next_note.velocity * 0.85),
        Note(pitch=target_midi, duration=next_note.duration, velocity=next_note.velocity),
    ]


def retardation(note: Note, next_note: Note, amount: float = 0.25) -> list[Note]:
    """Retardation: arrive at the next note late.

    The opposite of anticipation. The current note holds PAST its written
    duration into the next note's time, then resolves upward. Creates
    suspension-like tension. The melody resists moving forward.

    Args:
        note:       Current note (extended).
        next_note:  Next note (delayed).
        amount:     Fraction of next note's duration to delay (0.1-0.5).
    """
    if note.pitch is None or next_note.pitch is None:
        return [note, next_note]
    hold_dur = next_note.duration * amount
    remaining_dur = next_note.duration - hold_dur
    return [
        Note(pitch=note.midi, duration=note.duration + hold_dur, velocity=note.velocity),
        Note(pitch=next_note.midi, duration=remaining_dur, velocity=next_note.velocity),
    ]


def hairpin(
    notes: list[Note],
    start_vel: float = 0.3,
    peak_vel: float = 0.9,
    end_vel: float = 0.3,
    peak_at: float = 0.5,
) -> list[Note]:
    """Hairpin dynamics: crescendo to a peak, then decrescendo.

    Beat-level granularity dynamics with shape control. The peak
    position determines whether it is a crescendo-heavy hairpin
    (peak_at=0.8) or a decrescendo-heavy hairpin (peak_at=0.2).
    Symmetric (peak_at=0.5) is the classic diamond hairpin.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity.
        peak_vel:  Peak velocity at the apex.
        end_vel:   Ending velocity.
        peak_at:   Where the peak falls (0.0-1.0, 0.5=symmetric).
    """
    if not notes:
        return []
    result = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        if frac <= peak_at:
            # Crescendo phase
            phase_frac = frac / max(peak_at, 0.001)
            vel = start_vel + (peak_vel - start_vel) * phase_frac
        else:
            # Decrescendo phase
            phase_frac = (frac - peak_at) / max(1.0 - peak_at, 0.001)
            vel = peak_vel + (end_vel - peak_vel) * phase_frac
        vel = max(0.01, min(1.0, vel))
        if n.pitch is None:
            result.append(n)
        else:
            result.append(
                Note(n.pitch, n.octave, n.duration, velocity=vel, articulation=n.articulation)
            )
    return result


def breath_mark(duration: float = 0.125) -> Note:
    """Insert a breath mark: a natural phrasing pause for wind/vocal lines.

    A brief silence that represents a breath between phrases. Not just
    a rest - it is shorter and more specific to wind and vocal music.
    Standard breath mark is an eighth note or shorter.

    Args:
        duration: Length of the breath in beats (0.125 = 32nd note).
    """
    return Note.rest(duration)


def insert_breaths(
    notes: list[Note],
    every_n: int = 4,
    breath_dur: float = 0.125,
) -> list[Note]:
    """Insert breath marks every N notes for natural wind/vocal phrasing.

    Real wind players breathe. Real singers breathe. Without breath
    marks, synthesized wind and vocal lines sound robotic because they
    never pause. This inserts brief rests at regular intervals.

    Args:
        notes:      Input notes.
        every_n:    Insert a breath every N notes (4=every bar in 4/4).
        breath_dur: Duration of each breath.
    """
    result = []
    count = 0
    for n in notes:
        result.append(n)
        count += 1
        if count >= every_n and n.pitch is not None:
            result.append(breath_mark(breath_dur))
            count = 0
    return result


def passing_chords(
    progression: list[tuple[str, str]],
    style: str = "chromatic",
) -> list[tuple[str, str]]:
    """Insert passing chords between structural chords.

    Takes a chord progression and adds transitional chords between each
    pair based on voice leading rules. Chromatic passing chords use
    half-step root motion. Diatonic uses scale-degree steps.

    Args:
        progression: List of (root, quality) tuples.
        style:       "chromatic" (half-step root motion) or "diatonic" (scale steps).

    Returns:
        Expanded progression with passing chords inserted.
    """
    if len(progression) < 2:
        return list(progression)

    NOTE_ORDER = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def _semi(name: str) -> int:
        return (
            NOTE_ORDER.index(
                name.replace("b", "#")
                .replace("Db", "C#")
                .replace("Eb", "D#")
                .replace("Gb", "F#")
                .replace("Ab", "G#")
                .replace("Bb", "A#")
            )
            if name in NOTE_ORDER
            else 0
        )

    result = [progression[0]]
    for i in range(1, len(progression)):
        prev_root = _semi(progression[i - 1][0])
        next_root = _semi(progression[i][0])
        distance = (next_root - prev_root) % 12

        if distance == 0 or distance == 1 or distance == 11:
            # Already adjacent, no passing chord needed
            result.append(progression[i])
            continue

        if style == "chromatic":
            # Insert one chromatic passing chord at the midpoint
            if distance <= 6:
                mid = (prev_root + distance // 2) % 12
            else:
                mid = (prev_root - (12 - distance) // 2) % 12
            result.append((NOTE_ORDER[mid], progression[i - 1][1]))
        else:
            # Diatonic: insert chord a third above or below
            mid = (prev_root + 4) % 12  # major third above
            result.append((NOTE_ORDER[mid], "min7" if "min" in progression[i - 1][1] else "dom7"))

        result.append(progression[i])

    return result


def nested_tuplet(
    notes: list[Note],
    outer_n: int = 3,
    inner_n: int = 5,
    total_beats: float = 1.0,
) -> list[Note]:
    """Nested tuplet: a tuplet within a tuplet.

    Ligeti, Ferneyhough, and other complexity-loving composers use nested
    tuplets for rhythmic density that is humanly almost impossible to
    play but mathematically precise. A triplet where each note of the
    triplet is subdivided into quintuplets = 15 notes in the space of 1.

    Args:
        notes:        Input notes (up to outer_n * inner_n).
        outer_n:      Outer tuplet divisions.
        inner_n:      Inner tuplet divisions per outer note.
        total_beats:  Total duration to fit everything into.
    """
    total_notes = outer_n * inner_n
    dur = total_beats / total_notes
    count = min(len(notes), total_notes)
    result = []
    for i in range(count):
        src = notes[i]
        if src.pitch is None:
            result.append(Note.rest(dur))
        else:
            result.append(
                Note(
                    src.pitch, src.octave, dur, velocity=src.velocity, articulation=src.articulation
                )
            )
    for _ in range(total_notes - count):
        result.append(Note.rest(dur))
    return result


def swing_tuplet(
    notes: list[Note],
    ratio: float = 0.67,
    total_beats: float = 1.0,
) -> list[Note]:
    """Swing tuplet: long-short pattern with arbitrary ratio.

    Standard swing is 2:1 (triplet feel, ratio=0.67). But real swing
    varies by genre and tempo. New Orleans swing is closer to 60:40.
    Bebop at high tempos is nearly straight (52:48). This lets you
    dial in the exact ratio.

    Args:
        notes:       Input notes (pairs will be swung).
        ratio:       Long note fraction (0.5=straight, 0.67=triplet, 0.75=heavy).
        total_beats: Total duration per pair.
    """
    result = []
    pair_dur = total_beats
    long_dur = pair_dur * ratio
    short_dur = pair_dur * (1.0 - ratio)

    for i in range(0, len(notes), 2):
        n1 = notes[i]
        if n1.pitch is None:
            result.append(Note.rest(long_dur))
        else:
            result.append(
                Note(
                    n1.pitch,
                    n1.octave,
                    long_dur,
                    velocity=n1.velocity,
                    articulation=n1.articulation,
                )
            )
        if i + 1 < len(notes):
            n2 = notes[i + 1]
            if n2.pitch is None:
                result.append(Note.rest(short_dur))
            else:
                result.append(
                    Note(
                        n2.pitch,
                        n2.octave,
                        short_dur,
                        velocity=n2.velocity,
                        articulation=n2.articulation,
                    )
                )
    return result


def con_sordino(notes: list[Note]) -> list[Note]:
    """Apply mute (con sordino) to notes. Darker, softer timbre."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="con_sordino")
        if n.pitch is not None
        else n
        for n in notes
    ]


def senza_sordino(notes: list[Note]) -> list[Note]:
    """Remove mute. Return to normal open sound."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation=None)
        if n.pitch is not None
        else n
        for n in notes
    ]


def sul_ponticello(notes: list[Note]) -> list[Note]:
    """Bow near the bridge. Glassy, metallic, harmonic-rich."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="sul_ponticello")
        if n.pitch is not None
        else n
        for n in notes
    ]


def sul_tasto(notes: list[Note]) -> list[Note]:
    """Bow over the fingerboard. Breathy, dark, flute-like."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="sul_tasto")
        if n.pitch is not None
        else n
        for n in notes
    ]


def col_legno(notes: list[Note]) -> list[Note]:
    """Strike with the wood of the bow. Percussive, dry click."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="col_legno")
        if n.pitch is not None
        else n
        for n in notes
    ]


def spiccato(notes: list[Note]) -> list[Note]:
    """Bouncing bow. Short, crisp, more resonant than staccato."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="spiccato")
        if n.pitch is not None
        else n
        for n in notes
    ]


def tremolo_bow(notes: list[Note]) -> list[Note]:
    """Rapid bow tremolo. Shimmering, agitated sustain."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="tremolo")
        if n.pitch is not None
        else n
        for n in notes
    ]


def harmonics(notes: list[Note]) -> list[Note]:
    """Natural harmonics. Pure, bell-like, ethereal overtone."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="harmonics")
        if n.pitch is not None
        else n
        for n in notes
    ]


def muted(notes: list[Note]) -> list[Note]:
    """Muted/stopped brass or palm-muted guitar."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="muted")
        if n.pitch is not None
        else n
        for n in notes
    ]


def flutter_tongue(notes: list[Note]) -> list[Note]:
    """Flutter tongue on brass/woodwind. Buzzy, tremolo-like."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="flutter_tongue")
        if n.pitch is not None
        else n
        for n in notes
    ]


def with_brushes(notes: list[Note]) -> list[Note]:
    """Percussion played with brushes instead of sticks."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="brush")
        if n.pitch is not None
        else n
        for n in notes
    ]


def with_mallets(notes: list[Note]) -> list[Note]:
    """Percussion played with soft mallets. Warmer, rounder attack."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="mallet")
        if n.pitch is not None
        else n
        for n in notes
    ]


def with_rods(notes: list[Note]) -> list[Note]:
    """Percussion played with rods/hot rods. Between stick and brush."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="rod")
        if n.pitch is not None
        else n
        for n in notes
    ]


def rim_click(notes: list[Note]) -> list[Note]:
    """Cross-stick / rim click. Woodblock-like from a snare drum."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="cross_stick")
        if n.pitch is not None
        else n
        for n in notes
    ]


def dead_stroke(notes: list[Note]) -> list[Note]:
    """Dead stroke on percussion. Hit and immediately dampen. Dry thud."""
    return [
        Note(n.pitch, n.octave, n.duration, n.velocity, articulation="dead_stroke")
        if n.pitch is not None
        else n
        for n in notes
    ]


def octave_up(notes: list[Note], n: int = 1) -> list[Note]:
    """Shift all notes up by n octaves (12 semitones each)."""
    return transpose(notes, 12 * n)


def octave_down(notes: list[Note], n: int = 1) -> list[Note]:
    """Shift all notes down by n octaves (12 semitones each)."""
    return transpose(notes, -12 * n)


def double_octave(notes: list[Note], direction: str = "both") -> list[Note]:
    """Double notes at the octave for a fuller sound.

    Args:
        notes: Input notes.
        direction: "up" (add octave above), "down" (add octave below),
                   "both" (add both). Each note becomes 2 or 3 simultaneous pitches
                   expressed as sequential notes with zero-duration spacing.

    Returns:
        Expanded note list with octave doublings interleaved.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
            continue
        result.append(n)
        midi = n.midi
        if midi is None:
            continue
        if direction in ("up", "both"):
            result.append(Note(pitch=midi + 12, duration=n.duration, velocity=n.velocity * 0.7))
        if direction in ("down", "both"):
            result.append(Note(pitch=midi - 12, duration=n.duration, velocity=n.velocity * 0.65))
    return result


def velocity_curve(notes: list[Note], curve: str = "linear") -> list[Note]:
    """Apply a velocity curve to reshape dynamics without changing velocity values.

    Args:
        notes: Input notes.
        curve: Curve name from VELOCITY_CURVES: "linear", "exponential",
               "logarithmic", "s_curve", "piano", "organ", "percussion".

    Returns:
        Notes with velocities remapped through the curve function.
    """
    fn = VELOCITY_CURVES.get(curve, VELOCITY_CURVES["linear"])
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            new_vel = max(0.01, min(1.0, fn(n.velocity)))
            result.append(
                Note(pitch=n.pitch, octave=n.octave, duration=n.duration, velocity=new_vel)
            )
    return result


def dynamics(notes: list[Note], marking: float) -> list[Note]:
    """Set all notes to a specific dynamic marking.

    Args:
        notes: Input notes.
        marking: One of the dynamic constants (PP, MP, MF, F, FF, etc.)
                 or any float 0.0-1.0.

    Returns:
        Notes with velocity set to the marking value.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            result.append(
                Note(pitch=n.pitch, octave=n.octave, duration=n.duration, velocity=marking)
            )
    return result


# ---------------------------------------------------------------------------
# Song Sections — arrange a Song in named blocks
# ---------------------------------------------------------------------------


@dataclass
class Section:
    """A named block of beats that can be referenced in an arrangement.

    Attributes:
        name:    Label (e.g. 'intro', 'verse', 'chorus', 'bridge', 'outro').
        tracks:  Dict of track_name → list of Note/Chord events for this section.
        bars:    How many bars this section lasts (for documentation).
    """

    name: str
    tracks: dict[str, list] = field(default_factory=dict)
    bars: int = 4

    def add_track(self, track_name: str, events: list) -> "Section":
        self.tracks[track_name] = events
        return self

    def repeat(self, n: int) -> list["Section"]:
        """Return a list of *n* copies of this Section for use in Song.arrange().

        The repeated sections share the same name but are independent objects
        so the arrangement timeline expands correctly.

        Example::

            chorus = Section("chorus", bars=4)
            chorus.add_track("lead", melody_notes)

            song.arrange([intro, *chorus.repeat(3), outro])
        """
        import copy

        return [copy.deepcopy(self) for _ in range(n)]

    def __repr__(self) -> str:
        return f"Section({self.name!r}, bars={self.bars}, tracks={list(self.tracks.keys())})"


@dataclass
class Clip:
    """A loopable slice of a Track's beats.

    Extract a range of beats, then loop, reverse, or trim. The building
    block for live-looping style composition: grab 4 bars of drums, loop
    them 8 times, layer with a 2-bar bass clip looped 16 times.

    Attributes:
        beats:  The extracted Beat objects.
        name:   Optional label.
        source: Name of the source track (for reference).

    Example::

        clip = Clip.from_track(drum_track, start_beat=0, end_beat=4)
        looped = clip.loop(8)  # 32 beats of drums
        drum_track.extend(looped.to_events())
    """

    beats: list["Beat"] = field(default_factory=list)
    name: str = "clip"
    source: str = ""

    @classmethod
    def from_track(
        cls,
        track: "Track",
        start_beat: int = 0,
        end_beat: int | None = None,
        name: str | None = None,
    ) -> "Clip":
        """Extract a clip from a track by beat index range.

        Args:
            track:      Source track.
            start_beat: First beat index (inclusive).
            end_beat:   Last beat index (exclusive). None = end of track.
            name:       Clip label. Defaults to track name.
        """
        import copy

        end = end_beat if end_beat is not None else len(track.beats)
        extracted = [copy.deepcopy(b) for b in track.beats[start_beat:end]]
        return cls(
            beats=extracted,
            name=name or track.name,
            source=track.name,
        )

    def loop(self, n: int) -> "Clip":
        """Repeat the clip N times, returning a new Clip.

        Args:
            n: Number of repetitions.

        Returns:
            New Clip with beats repeated N times.

        Example::

            four_bars = Clip.from_track(drums, 0, 16)
            thirty_two_bars = four_bars.loop(8)
        """
        import copy

        looped = []
        for _ in range(n):
            looped.extend(copy.deepcopy(self.beats))
        return Clip(beats=looped, name=self.name, source=self.source)

    def reverse(self) -> "Clip":
        """Return a new Clip with beats in reverse order."""
        import copy

        return Clip(
            beats=list(reversed([copy.deepcopy(b) for b in self.beats])),
            name=self.name,
            source=self.source,
        )

    def trim(self, start: int = 0, end: int | None = None) -> "Clip":
        """Return a new Clip trimmed to the given beat range.

        Args:
            start: First beat index (inclusive).
            end:   Last beat index (exclusive). None = end.
        """
        import copy

        sliced = [copy.deepcopy(b) for b in self.beats[start:end]]
        return Clip(beats=sliced, name=self.name, source=self.source)

    def to_events(self) -> list:
        """Extract the Note/Chord/None events from each beat.

        Returns:
            List of events suitable for Track.extend().
        """
        return [b.event for b in self.beats]

    @property
    def duration(self) -> float:
        """Total duration in beats."""
        return sum(b.duration for b in self.beats)

    def __len__(self) -> int:
        return len(self.beats)

    def crossfade(self, other: "Clip", overlap_beats: int = 2) -> "Clip":
        """Crossfade from this clip into another.

        The last `overlap_beats` of self fade out while the first
        `overlap_beats` of other fade in. Velocities are interpolated
        linearly across the overlap region. Events outside the overlap
        are untouched.

        Args:
            other:          The clip to transition into.
            overlap_beats:  Number of beats for the crossfade.

        Returns:
            New Clip with the crossfaded transition.
        """
        import copy

        if overlap_beats <= 0 or overlap_beats > min(len(self), len(other)):
            # No overlap possible, just concatenate
            return Clip(
                beats=copy.deepcopy(self.beats) + copy.deepcopy(other.beats),
                name=self.name,
                source=self.source,
            )

        result_beats: list["Beat"] = []

        # Pre-overlap from self
        pre = copy.deepcopy(self.beats[:-overlap_beats])
        result_beats.extend(pre)

        # Overlap zone: fade self out, fade other in
        for i in range(overlap_beats):
            fade_out = 1.0 - (i + 1) / (overlap_beats + 1)
            fade_in = (i + 1) / (overlap_beats + 1)

            beat_a = copy.deepcopy(self.beats[len(self) - overlap_beats + i])
            beat_b = copy.deepcopy(other.beats[i])

            # Pick the higher-velocity event and scale it
            if beat_a.event is not None and beat_b.event is not None:
                # Blend: use beat_b's pitch but interpolated velocity
                merged = copy.deepcopy(beat_b)
                vel_a = getattr(beat_a.event, "velocity", 70) * fade_out
                vel_b = getattr(beat_b.event, "velocity", 70) * fade_in
                if hasattr(merged.event, "velocity"):
                    merged.event.velocity = vel_a + vel_b
                result_beats.append(merged)
            elif beat_b.event is not None:
                result_beats.append(beat_b)
            else:
                result_beats.append(beat_a)

        # Post-overlap from other
        post = copy.deepcopy(other.beats[overlap_beats:])
        result_beats.extend(post)

        return Clip(beats=result_beats, name=self.name, source=self.source)

    def quantize_to_bars(self, beats_per_bar: int = 4, mode: str = "nearest") -> "Clip":
        """Snap clip length to the nearest bar boundary.

        Pads with rests or trims to make the clip an exact multiple of
        beats_per_bar. Useful for ensuring clips align on the grid when
        launched in a Session.

        Args:
            beats_per_bar: Beats per bar (default 4 for 4/4 time).
            mode:          'nearest' (round to closest bar), 'ceil' (round up),
                           'floor' (round down, may lose beats).

        Returns:
            New Clip with bar-aligned length.
        """
        import copy
        import math

        n = len(self.beats)
        if n == 0 or beats_per_bar <= 0:
            return Clip(beats=list(self.beats), name=self.name, source=self.source)

        if mode == "ceil":
            target = math.ceil(n / beats_per_bar) * beats_per_bar
        elif mode == "floor":
            target = max(beats_per_bar, math.floor(n / beats_per_bar) * beats_per_bar)
        else:  # nearest
            target = round(n / beats_per_bar) * beats_per_bar
            if target == 0:
                target = beats_per_bar

        result = copy.deepcopy(self.beats[:target])
        # Pad with rests if needed
        while len(result) < target:
            result.append(Beat(event=None))
        return Clip(beats=result, name=self.name, source=self.source)

    def __repr__(self) -> str:
        return f"Clip({self.name!r}, {len(self.beats)} beats, source={self.source!r})"


@dataclass
class ClipSlot:
    """A slot that holds a Clip with play/stop state.

    Part of the Session grid. Each slot can be playing, stopped, or queued.
    When playing, the clip loops continuously. Quantize to bar boundaries
    for tight transitions.

    Attributes:
        clip:     The Clip in this slot (None = empty slot).
        state:    'stopped', 'playing', 'queued'.
        loop:     Whether the clip loops when it reaches the end.

    Example::

        slot = ClipSlot(clip=my_clip)
        slot.play()
        slot.stop()
    """

    clip: Clip | None = None
    state: str = "stopped"
    loop: bool = True

    def play(self) -> "ClipSlot":
        """Start playing the clip."""
        if self.clip is not None:
            self.state = "playing"
        return self

    def stop(self) -> "ClipSlot":
        """Stop the clip."""
        self.state = "stopped"
        return self

    def queue(self) -> "ClipSlot":
        """Queue the clip to start on the next bar boundary."""
        if self.clip is not None:
            self.state = "queued"
        return self

    @property
    def is_playing(self) -> bool:
        return self.state == "playing"

    @property
    def is_empty(self) -> bool:
        return self.clip is None

    def __repr__(self) -> str:
        if self.clip is None:
            return "ClipSlot(empty)"
        return f"ClipSlot({self.clip.name!r}, {self.state})"


@dataclass
class Session:
    """Ableton-style session view: a grid of ClipSlots (tracks x scenes).

    Organize clips into a grid where rows are tracks and columns are scenes.
    Launch entire scenes at once (all clips in a column start together) or
    trigger individual slots. Render to a Song by playing scenes in sequence.

    Attributes:
        bpm:          Tempo.
        track_names:  List of track names (rows).
        scene_count:  Number of scenes (columns).
        grid:         2D dict: grid[track_name][scene_index] = ClipSlot.

    Example::

        session = Session(bpm=120)
        session.add_track("drums", instrument="drums_kick")
        session.add_track("bass", instrument="bass")

        session.set_clip("drums", 0, kick_clip)
        session.set_clip("bass", 0, bass_clip)

        song = session.render(scene_order=[0, 0, 1, 1, 0])
    """

    bpm: float = 120
    sample_rate: int = 44100
    track_names: list[str] = field(default_factory=list)
    _instruments: dict[str, str] = field(default_factory=dict)
    _volumes: dict[str, float] = field(default_factory=dict)
    grid: dict[str, list[ClipSlot]] = field(default_factory=dict)
    scene_count: int = 0
    _muted: set[str] = field(default_factory=set)
    _soloed: set[str] = field(default_factory=set)
    _pans: dict[str, float] = field(default_factory=dict)

    def add_track(
        self,
        name: str,
        instrument: str = "sine",
        volume: float = 0.8,
    ) -> "Session":
        """Add a track (row) to the session grid.

        Args:
            name:       Track name.
            instrument: Synth preset for this track.
            volume:     Track volume.
        """
        if name not in self.track_names:
            self.track_names.append(name)
            self._instruments[name] = instrument
            self._volumes[name] = volume
            self.grid[name] = [ClipSlot() for _ in range(max(1, self.scene_count))]
        return self

    def add_scene(self) -> int:
        """Add a new scene (column) to the grid. Returns the scene index."""
        idx = self.scene_count
        self.scene_count += 1
        for name in self.track_names:
            self.grid[name].append(ClipSlot())
        return idx

    def set_clip(self, track_name: str, scene_index: int, clip: Clip) -> "Session":
        """Place a clip into a slot.

        Args:
            track_name:  Track row.
            scene_index: Scene column.
            clip:        The Clip to place.
        """
        if track_name not in self.grid:
            raise ValueError(f"Unknown track: {track_name!r}")
        # Auto-expand scenes if needed
        while scene_index >= len(self.grid[track_name]):
            self.add_scene()
        self.grid[track_name][scene_index] = ClipSlot(clip=clip)
        self.scene_count = max(self.scene_count, scene_index + 1)
        return self

    def launch_scene(self, scene_index: int) -> "Session":
        """Start all clips in a scene (column)."""
        for name in self.track_names:
            if scene_index < len(self.grid[name]):
                slot = self.grid[name][scene_index]
                if not slot.is_empty:
                    slot.play()
        return self

    def stop_all(self) -> "Session":
        """Stop all playing clips."""
        for name in self.track_names:
            for slot in self.grid[name]:
                slot.stop()
        return self

    def stop_track(self, track_name: str) -> "Session":
        """Stop all clips on a specific track."""
        if track_name in self.grid:
            for slot in self.grid[track_name]:
                slot.stop()
        return self

    def mute(self, track_name: str) -> "Session":
        """Mute a track (set volume to 0 in render)."""
        self._muted.add(track_name)
        return self

    def unmute(self, track_name: str) -> "Session":
        """Unmute a track."""
        self._muted.discard(track_name)
        return self

    def solo(self, track_name: str) -> "Session":
        """Solo a track (mute everything else in render)."""
        self._soloed.add(track_name)
        return self

    def unsolo(self, track_name: str) -> "Session":
        """Remove solo from a track."""
        self._soloed.discard(track_name)
        return self

    def set_volume(self, track_name: str, volume: float) -> "Session":
        """Set a track's volume (0.0-1.0)."""
        self._volumes[track_name] = max(0.0, min(1.0, volume))
        return self

    def set_pan(self, track_name: str, pan: float) -> "Session":
        """Set a track's stereo pan (-1.0 to 1.0)."""
        self._pans[track_name] = max(-1.0, min(1.0, pan))
        return self

    def _effective_volume(self, track_name: str) -> float:
        """Get the effective volume for a track, accounting for mute/solo."""
        if self._soloed and track_name not in self._soloed:
            return 0.0
        if track_name in self._muted:
            return 0.0
        return self._volumes.get(track_name, 0.8)

    def render(
        self,
        scene_order: list[int] | None = None,
        loops_per_scene: int = 1,
    ) -> "Song":
        """Render the session to a Song by playing scenes in sequence.

        Args:
            scene_order:     List of scene indices to play in order.
                             None = play all scenes 0..N in order.
            loops_per_scene: How many times each scene's clips loop.

        Returns:
            A Song with one Track per session track, containing the
            concatenated clip events for the scene sequence.
        """
        if scene_order is None:
            scene_order = list(range(self.scene_count))

        song = Song(title="Session Render", bpm=self.bpm, sample_rate=self.sample_rate)

        for name in self.track_names:
            track = Track(
                name=name,
                instrument=self._instruments.get(name, "sine"),
                volume=self._effective_volume(name),
                pan=self._pans.get(name, 0.0),
            )

            for scene_idx in scene_order:
                if scene_idx < len(self.grid[name]):
                    slot = self.grid[name][scene_idx]
                    if slot.clip is not None:
                        looped = slot.clip.loop(loops_per_scene)
                        track.extend(looped.to_events())
                    else:
                        # Empty slot: add silence for the duration of the longest
                        # clip in this scene
                        max_dur = self._scene_duration(scene_idx)
                        if max_dur > 0:
                            track.add(Note.rest(max_dur * loops_per_scene))

            song.add_track(track)

        return song

    def _scene_duration(self, scene_index: int) -> float:
        """Duration of the longest clip in a scene."""
        max_dur = 0.0
        for name in self.track_names:
            if scene_index < len(self.grid[name]):
                slot = self.grid[name][scene_index]
                if slot.clip is not None:
                    max_dur = max(max_dur, slot.clip.duration)
        return max_dur

    def __repr__(self) -> str:
        filled = sum(
            1 for name in self.track_names for slot in self.grid.get(name, []) if not slot.is_empty
        )
        return (
            f"Session({len(self.track_names)} tracks, "
            f"{self.scene_count} scenes, {filled} clips, {self.bpm} BPM)"
        )


@dataclass
class Track:
    """A sequence of Beats with instrument/synth metadata.

    Attributes:
        name: Human-readable label.
        beats: Ordered sequence of Beat objects.
        instrument: Synth preset name (e.g. 'sine', 'square', 'sawtooth', 'piano').
        volume: Track-level gain 0.0–1.0.
        pan: Stereo position -1.0 (hard left) to 1.0 (hard right), 0.0 = center.
        swing: Swing ratio 0.0 (straight) to 0.67 (heavy swing). Delays every
               2nd 8th note by this fraction of one 8th note duration.
    """

    name: str = "track"
    beats: list[Beat] = field(default_factory=list)
    instrument: str = "sine"
    volume: float = 0.8
    pan: float = 0.0  # -1.0 (L) to 1.0 (R)
    swing: float = 0.0  # 0.0 = straight, 0.5 = medium swing, 0.67 = heavy
    density: float = 1.0  # 0.0-1.0 probability each note plays (1.0 = all notes)
    density_seed: int | None = None  # random seed for reproducible dropout
    humanize: float = 0.0  # 0.0 = robot, 0.3 = subtle, 0.7 = natural, 1.0 = loose
    # Spatial audio (v151.0) - binaural 3D positioning
    spatial_azimuth: float | None = None  # horizontal angle (-180..180), None = use pan
    spatial_elevation: float = 0.0  # vertical angle (-90..90)
    spatial_distance: float = 1.0  # distance from listener
    spatial_orbit_rate: float | None = None  # orbits/sec, None = static

    def add(self, event: Note | Chord | None) -> "Track":
        """Append a note, chord, or rest beat. Returns self for chaining."""
        self.beats.append(Beat(event=event))
        return self

    def extend(self, events: Sequence[Note | Chord | None]) -> "Track":
        for e in events:
            self.add(e)
        return self

    def concat(self, other: "Track") -> "Track":
        """Return a new Track joining *self* and *other* end-to-end.

        Metadata (instrument, volume, pan, etc.) comes from *self*.
        Both tracks' beats are preserved; *other*'s beats are appended
        after *self*'s.

        Example::

            intro_lead = lead_track.fade_in(4.0)
            full_lead = intro_lead.concat(main_lead).concat(outro_lead.fade_out(4.0))
            song.add_track(full_lead)
        """
        joined = self._clone_empty()
        joined.beats = list(self.beats) + list(other.beats)
        return joined

    def quantize(self, grid: float = 0.25) -> "Track":
        """Return a new Track with note durations snapped to the nearest grid.

        Rounds each note/chord/rest duration to the nearest multiple of ``grid``.
        Useful for tightening up humanized or generated patterns.

        Args:
            grid: Grid subdivision in beats (0.25 = 16th note, 0.5 = 8th, 1.0 = quarter).

        Returns:
            New Track with quantized durations. Original track unchanged.

        Example::

            tight = loose_track.quantize(grid=0.25)   # snap to 16th grid
            song.add_track(tight)
        """
        q = Track(
            name=self.name,
            instrument=self.instrument,
            volume=self.volume,
            pan=self.pan,
            swing=self.swing,
            density=self.density,
            density_seed=self.density_seed,
        )
        for beat in self.beats:
            if beat.event is None:
                q.beats.append(Beat(event=None))
                continue
            event = beat.event
            snapped_dur = max(grid, round(event.duration / grid) * grid)
            if isinstance(event, Note):
                q.add(
                    Note(
                        pitch=event.pitch,
                        octave=event.octave,
                        duration=snapped_dur,
                        velocity=event.velocity,
                    )
                )
            elif isinstance(event, Chord):
                q.add(
                    Chord(
                        root=event.root,
                        shape=event.shape,
                        octave=event.octave,
                        duration=snapped_dur,
                        velocity=event.velocity,
                    )
                )
        return q

    def reverse(self) -> "Track":
        """Return a new Track with all beats in reverse order.

        The instrument, volume, pan, swing, and density stay the same.
        Only the note/chord sequence is reversed.

        Example::

            reversed_melody = melody_track.reverse()
            song.add_track(reversed_melody)
        """
        rev = Track(
            name=self.name,
            instrument=self.instrument,
            volume=self.volume,
            pan=self.pan,
            swing=self.swing,
            density=self.density,
            density_seed=self.density_seed,
        )
        rev.beats = list(reversed(self.beats))
        return rev

    def fade_in(self, beats: float = 4.0) -> "Track":
        """Return a new Track with velocity ramped from 0 to original over *beats*.

        Notes that start before *beats* get scaled linearly; notes after
        the fade region keep their original velocity.

        Example::

            intro = melody.fade_in(beats=8.0)
            song.add_track(intro)
        """
        faded = self._clone_empty()
        cursor = 0.0
        for beat in self.beats:
            if beat.event is not None and beats > 0:
                t = min(cursor / beats, 1.0)
                event = self._scale_velocity(beat.event, t)
                faded.beats.append(Beat(event=event))
            else:
                faded.beats.append(Beat(event=beat.event))
            cursor += beat.duration
        return faded

    def fade_out(self, beats: float = 4.0) -> "Track":
        """Return a new Track with velocity ramped from original to 0 over the last *beats*.

        Example::

            outro = melody.fade_out(beats=8.0)
            song.add_track(outro)
        """
        total = self.total_beats
        fade_start = max(total - beats, 0.0)
        faded = self._clone_empty()
        cursor = 0.0
        for beat in self.beats:
            if beat.event is not None and cursor >= fade_start and beats > 0:
                remaining = total - cursor
                t = min(remaining / beats, 1.0)
                event = self._scale_velocity(beat.event, t)
                faded.beats.append(Beat(event=event))
            else:
                faded.beats.append(Beat(event=beat.event))
            cursor += beat.duration
        return faded

    def _clone_empty(self) -> "Track":
        """Return a new Track with the same metadata but no beats."""
        return Track(
            name=self.name,
            instrument=self.instrument,
            volume=self.volume,
            pan=self.pan,
            swing=self.swing,
            density=self.density,
            density_seed=self.density_seed,
        )

    @staticmethod
    def _scale_velocity(event: "Note | Chord", factor: float) -> "Note | Chord":
        """Return a copy of a Note or Chord with velocity scaled by *factor*."""
        import copy

        scaled = copy.copy(event)
        scaled.velocity = event.velocity * max(0.0, min(factor, 1.0))
        return scaled

    def transpose(self, semitones: int) -> "Track":
        """Return a new Track with all pitched events shifted by *semitones*.

        Rests pass through unchanged. Chords are transposed note-by-note.
        Track metadata (instrument, volume, pan, etc.) is preserved.

        Example::

            harmony = melody.transpose(7)   # up a perfect fifth
            low = melody.transpose(-12)     # down one octave
        """
        import copy

        transposed = self._clone_empty()
        for beat in self.beats:
            if beat.event is None:
                transposed.beats.append(Beat(event=None))
                continue

            event = beat.event
            if isinstance(event, Note):
                if event.pitch is None:
                    transposed.beats.append(Beat(event=copy.copy(event)))
                elif isinstance(event.pitch, int):
                    transposed.add(
                        Note(
                            event.pitch + semitones,
                            event.octave,
                            event.duration,
                            velocity=event.velocity,
                        )
                    )
                else:
                    midi = note_name_to_midi(str(event.pitch), event.octave) + semitones
                    new_name, new_oct = midi_to_note_name(midi)
                    transposed.add(Note(new_name, new_oct, event.duration, velocity=event.velocity))
            elif isinstance(event, Chord):
                new_root_midi = note_name_to_midi(str(event.root), event.octave) + semitones
                new_root, new_oct = midi_to_note_name(new_root_midi)
                transposed.add(
                    Chord(
                        new_root,
                        event.shape,
                        new_oct,
                        duration=event.duration,
                        velocity=event.velocity,
                    )
                )
            else:
                transposed.beats.append(Beat(event=copy.copy(event)))
        return transposed

    def loop(self, n: int) -> "Track":
        """Return a new Track with existing beats repeated *n* times.

        Preserves track metadata. Original track is not mutated.

        Example::

            four_bar_riff = bass.loop(4)   # riff plays 4 times
        """
        looped = self._clone_empty()
        for _ in range(n):
            looped.beats.extend(Beat(event=b.event) for b in self.beats)
        return looped

    def split(self, at_beat: float) -> tuple["Track", "Track"]:
        """Split the track at *at_beat*, returning (before, after).

        If a note/rest straddles the split point, it is divided into two
        with the appropriate durations. Both tracks preserve metadata.

        Example::

            intro, body = full_track.split(at_beat=16.0)
        """
        import copy

        before = self._clone_empty()
        after = self._clone_empty()
        cursor = 0.0
        split_done = False

        for beat in self.beats:
            if split_done:
                after.beats.append(Beat(event=copy.copy(beat.event) if beat.event else None))
                continue

            end = cursor + beat.duration
            if end <= at_beat:
                before.beats.append(Beat(event=copy.copy(beat.event) if beat.event else None))
            elif cursor >= at_beat:
                after.beats.append(Beat(event=copy.copy(beat.event) if beat.event else None))
                split_done = True
            else:
                # Straddles the split point
                left_dur = at_beat - cursor
                right_dur = end - at_beat
                if beat.event is None:
                    before.add(Note.rest(left_dur))
                    after.add(Note.rest(right_dur))
                elif isinstance(beat.event, Note):
                    e = beat.event
                    before.add(Note(e.pitch, e.octave, left_dur, velocity=e.velocity))
                    after.add(Note(e.pitch, e.octave, right_dur, velocity=e.velocity))
                elif isinstance(beat.event, Chord):
                    e = beat.event
                    before.add(
                        Chord(e.root, e.shape, e.octave, duration=left_dur, velocity=e.velocity)
                    )
                    after.add(
                        Chord(e.root, e.shape, e.octave, duration=right_dur, velocity=e.velocity)
                    )
                split_done = True
            cursor = end

        return before, after

    def merge(self, other: "Track") -> "Track":
        """Overlay *other*'s events on top of this track at matching beat positions.

        Walks both tracks in parallel. Where *other* has a pitched event and
        *self* has a rest (or vice-versa), the pitched event wins. Where both
        have pitched events, *self*'s event is kept. Metadata from *self*.

        Example::

            combined_hats = ride_pattern.merge(crash_accents)
        """
        import copy

        merged = self._clone_empty()
        self_beats = list(self.beats)
        other_beats = list(other.beats)

        s_cursor = 0.0

        # Walk through beat-by-beat using self's timeline as the grid
        for beat in self_beats:
            dur = beat.duration
            has_pitch = beat.event is not None and (
                getattr(beat.event, "pitch", None) is not None
                or getattr(beat.event, "root", None) is not None
            )
            if has_pitch:
                # Self has a real event — keep it
                merged.beats.append(Beat(event=copy.copy(beat.event)))
            else:
                # Self has rest — check if other has something at this position
                # Find other's beat overlapping s_cursor
                o_pos = 0.0
                found = None
                for ob in other_beats:
                    if o_pos + ob.duration > s_cursor + 0.001 and o_pos < s_cursor + dur - 0.001:
                        if ob.event is not None and (
                            getattr(ob.event, "pitch", None) is not None
                            or getattr(ob.event, "root", None) is not None
                        ):
                            found = ob.event
                            break
                    o_pos += ob.duration
                    if o_pos > s_cursor + dur:
                        break
                if found is not None:
                    merged.beats.append(Beat(event=copy.copy(found)))
                else:
                    merged.beats.append(Beat(event=copy.copy(beat.event) if beat.event else None))
            s_cursor += dur

        return merged

    def stretch(self, factor: float) -> "Track":
        """Return a new Track with all beat durations scaled by *factor*.

        factor > 1.0 slows down (longer notes), factor < 1.0 speeds up.
        Preserves pitch, velocity, and metadata.

        Example::

            half_speed = melody.stretch(2.0)
            double_speed = melody.stretch(0.5)
        """
        import copy

        stretched = self._clone_empty()
        for beat in self.beats:
            if beat.event is None:
                stretched.add(Note.rest(beat.duration * factor))
            else:
                event = copy.copy(beat.event)
                event.duration = beat.event.duration * factor
                stretched.beats.append(Beat(event=event))
        return stretched

    def slice(self, start_beat: float, end_beat: float) -> "Track":
        """Extract a subsection from *start_beat* to *end_beat*.

        Equivalent to ``split(start).after → split(end).before`` but in one pass.
        Events straddling the boundaries are trimmed to fit.

        Example::

            chorus = full_track.slice(32.0, 64.0)  # bars 9-16
        """
        _, after_start = self.split(start_beat)
        extract, _ = after_start.split(end_beat - start_beat)
        return extract

    def filter(self, predicate) -> "Track":
        """Return a new Track with only beats where *predicate(event)* is True.

        Beats that fail the predicate are replaced with rests of the same
        duration, preserving timeline alignment.

        Example::

            loud = track.filter(lambda e: e.velocity > 0.5)
            only_c = track.filter(lambda e: getattr(e, 'pitch', None) == 'C')
        """
        filtered = self._clone_empty()
        for beat in self.beats:
            if beat.event is not None and predicate(beat.event):
                import copy

                filtered.beats.append(Beat(event=copy.copy(beat.event)))
            else:
                filtered.add(Note.rest(beat.duration))
        return filtered

    def __repr__(self) -> str:
        n = len(self.beats)
        tb = self.total_beats
        return (
            f"Track({self.name!r}, instrument={self.instrument!r}, "
            f"beats={n}, total_beats={tb:.1f}, vol={self.volume:.2f})"
        )

    def __len__(self) -> int:
        return len(self.beats)

    def __bool__(self) -> bool:
        return len(self.beats) > 0

    @property
    def total_beats(self) -> float:
        return sum(b.duration for b in self.beats)


@dataclass
class SampleTrack:
    """A track that plays back a WAV file at specified beat offsets.

    Load any audio file and trigger it at exact beat positions — this is
    sampling. Use for drum hits, vocal chops, field recordings, anything.

    The WAV is loaded once, then each trigger plays the full sample (or a
    specified duration). Pitch shifting via semitone offset is supported.

    Example::

        from code_music import SampleTrack

        kick = SampleTrack.from_wav("samples/kick.wav", name="kick", volume=0.9)
        kick.trigger(at=0.0)          # play at beat 0
        kick.trigger(at=1.0)          # play again at beat 1
        kick.trigger(at=2.0, semitones=-2)  # pitch down 2 semitones
        song.add_sample_track(kick)

    Attributes:
        name:       Track label.
        wav_path:   Path to the source WAV file.
        volume:     Track gain 0.0–1.0.
        pan:        Stereo position -1.0 (L) to 1.0 (R).
        triggers:   List of (beat_offset, semitones, velocity) tuples.
    """

    name: str = "sample"
    wav_path: str = ""
    volume: float = 0.8
    pan: float = 0.0
    triggers: list[tuple[float, float, float]] = field(default_factory=list)

    @classmethod
    def from_wav(
        cls, path: str, name: str = "sample", volume: float = 0.8, pan: float = 0.0
    ) -> "SampleTrack":
        """Create a SampleTrack from a WAV file path."""
        return cls(name=name, wav_path=path, volume=volume, pan=pan)

    def trigger(self, at: float, semitones: float = 0.0, velocity: float = 1.0) -> "SampleTrack":
        """Schedule the sample to play at a specific beat offset.

        Args:
            at:         Beat position to trigger the sample.
            semitones:  Pitch shift in semitones (0 = original pitch).
            velocity:   Volume multiplier for this trigger (0.0–1.0).

        Returns:
            self for chaining.
        """
        self.triggers.append((at, semitones, velocity))
        return self

    @property
    def total_beats(self) -> float:
        if not self.triggers:
            return 0.0
        return max(at for at, _, _ in self.triggers) + 1.0  # +1 beat for tail

    def load_audio(self, target_sr: int = 44100):
        """Load the WAV file and return a mono float64 numpy array + sample rate.

        Auto-resamples to target_sr if the WAV has a different rate.
        """
        import wave as _wave

        import numpy as np

        with _wave.open(self.wav_path, "rb") as wf:
            sr = wf.getframerate()
            n = wf.getnframes()
            ch = wf.getnchannels()
            sw = wf.getsampwidth()
            raw = wf.readframes(n)

        dtype = np.int16 if sw == 2 else np.int32
        samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
        samples /= 32768.0 if sw == 2 else 2147483648.0
        if ch == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)

        if sr != target_sr:
            from scipy import signal as _sig

            new_len = int(len(samples) * target_sr / sr)
            samples = _sig.resample(samples, new_len)

        return samples


@dataclass
class Song:
    """Container for multiple Tracks, VoiceTracks and global tempo/metadata.

    Attributes:
        title: Song title used in exported filename.
        bpm: Beats per minute.
        sample_rate: Audio sample rate (44100 for CD quality).
        tracks: List of Track objects mixed together on export.
        voice_tracks: List of VoiceTrack objects (rendered separately, then mixed).
    """

    title: str = "untitled"
    bpm: float = 120.0
    sample_rate: int = 44100
    tracks: list[Track] = field(default_factory=list)
    voice_tracks: list = field(default_factory=list)  # list[VoiceTrack]
    poly_tracks: list = field(default_factory=list)  # list[PolyphonicTrack]
    sample_tracks: list = field(default_factory=list)  # list[SampleTrack]
    time_sig: tuple[int, int] = (4, 4)
    time_sig_map: list[tuple[float, int, int]] = field(default_factory=list)
    composer: str = ""
    key_sig: str = "C"
    effects: dict = field(default_factory=dict)  # track_name → callable or EffectsChain
    bpm_map: list[float] = field(default_factory=list)  # per-beat BPM values (from bpm_ramp)
    _custom_instruments: dict = field(default_factory=dict)  # name → SoundDesigner

    def register_instrument(self, name: str, designer: object) -> "Song":
        """Register a custom SoundDesigner as a playable instrument.

        After registration, any Track with ``instrument=name`` will use
        the designer for rendering instead of the built-in synth presets.

        Returns self for chaining.

        Example::

            from code_music.sound_design import SoundDesigner
            kick = SoundDesigner("my_kick").add_osc("sine").pitch_envelope(4.0, 1.0, 0.04)
            song.register_instrument("my_kick", kick)
            tr = song.add_track(Track(instrument="my_kick"))
        """
        self._custom_instruments[name] = designer
        return self

    def __repr__(self) -> str:
        t = len(self.tracks)
        names = [tr.name for tr in self.tracks[:5]]
        if len(self.tracks) > 5:
            names.append("...")
        return (
            f"Song({self.title!r}, bpm={self.bpm}, tracks={t}, "
            f"beats={self.total_beats:.0f}, dur={self.duration_sec:.1f}s, "
            f"names={names})"
        )

    def __len__(self) -> int:
        return len(self.tracks)

    def __bool__(self) -> bool:
        return len(self.tracks) > 0

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_effects":
            import warnings

            warnings.warn(
                "song._effects is deprecated — use song.effects instead",
                DeprecationWarning,
                stacklevel=2,
            )
            # Silently redirect to the new attribute
            super().__setattr__("effects", value)
            return
        super().__setattr__(name, value)

    def __getattr__(self, name: str) -> object:
        if name == "_effects":
            import warnings

            warnings.warn(
                "song._effects is deprecated — use song.effects instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.effects
        raise AttributeError(f"'{type(self).__name__}' object has no attribute {name!r}")

    def add_time_sig_change(self, at_beat: float, numerator: int, denominator: int) -> "Song":
        """Schedule a time signature change at a specific beat offset.

        The change takes effect from `at_beat` onward until the next change.
        The initial time signature is set via `time_sig` on the Song.

        Args:
            at_beat:     Beat position where the change occurs.
            numerator:   Top number (beats per bar).
            denominator: Bottom number (beat unit: 4=quarter, 8=eighth).

        Example::

            song = Song(title="Mixed Meter", bpm=120, time_sig=(4, 4))
            song.add_time_sig_change(at_beat=16.0, numerator=3, denominator=4)
            song.add_time_sig_change(at_beat=28.0, numerator=7, denominator=8)
            # Bars 1-4: 4/4, bars 5-8ish: 3/4, then 7/8

        Returns:
            self for chaining.
        """
        self.time_sig_map.append((at_beat, numerator, denominator))
        self.time_sig_map.sort(key=lambda x: x[0])
        return self

    def time_sig_at(self, beat: float) -> tuple[int, int]:
        """Return the active time signature at a given beat position.

        Walks the time_sig_map in reverse to find the most recent change
        before or at the given beat. Returns the default time_sig if no
        changes have been scheduled yet.
        """
        result = self.time_sig
        for at_beat, num, den in self.time_sig_map:
            if at_beat <= beat:
                result = (num, den)
            else:
                break
        return result

    def add_track(self, track: Track) -> "Track":
        self.tracks.append(track)
        return track

    def add_polytrack(self, track) -> object:  # track: PolyphonicTrack
        """Add a PolyphonicTrack. Returns the track."""
        self.poly_tracks.append(track)
        return track

    def add_sample_track(self, track) -> object:  # track: SampleTrack
        """Add a SampleTrack (audio file sampling). Returns the track."""
        self.sample_tracks.append(track)
        return track

    def add_voice_track(self, track) -> object:  # track: VoiceTrack
        """Add a VoiceTrack to the song. Returns the track."""
        track.sample_rate = self.sample_rate
        self.voice_tracks.append(track)
        return track

    def add_vocal_track(self, track) -> object:
        """Add a VocalTrack (TTS-based vocals) to the song. Returns the track."""
        if not hasattr(self, "_vocal_tracks"):
            self._vocal_tracks = []
        self._vocal_tracks.append(track)
        return track

    def arrange(
        self,
        sections: Sequence[Section],
        instruments: dict[str, str] | None = None,
        volumes: dict[str, float] | None = None,
        pans: dict[str, float] | None = None,
    ) -> "Song":
        """Compose a song from an ordered list of Sections.

        Each Section contains named tracks with lists of Note/Chord events.
        ``arrange()`` concatenates these events in order, creating one Track
        per unique track name seen across all sections. Tracks that don't
        appear in a given section get rest-filled for that section's duration.

        Args:
            sections:    Ordered list of Section objects to concatenate.
            instruments: Map of track_name → synth preset. Defaults to "sine".
            volumes:     Map of track_name → volume (0.0–1.0). Defaults to 0.8.
            pans:        Map of track_name → pan (-1.0..1.0). Defaults to 0.0.

        Returns:
            self (with tracks populated) for chaining.

        Example::

            intro = Section("intro", bars=4)
            intro.add_track("pad", [Chord("A","min7",3,duration=16.0)])
            intro.add_track("lead", [Note.rest(16.0)])

            verse = Section("verse", bars=4)
            verse.add_track("pad", [Chord("D","min7",3,duration=16.0)])
            verse.add_track("lead", scale("A","pentatonic",5))

            song = Song(title="Arranged", bpm=120)
            song.arrange([intro, verse], instruments={"pad":"pad","lead":"piano"})
        """
        instruments = instruments or {}
        volumes = volumes or {}
        pans = pans or {}

        # Discover all track names across all sections
        all_track_names: list[str] = []
        for section in sections:
            for name in section.tracks:
                if name not in all_track_names:
                    all_track_names.append(name)

        # Build one Track per unique name
        built: dict[str, Track] = {}
        for name in all_track_names:
            built[name] = Track(
                name=name,
                instrument=instruments.get(name, "sine"),
                volume=volumes.get(name, 0.8),
                pan=pans.get(name, 0.0),
            )

        # Walk sections in order, appending events (or rests) per track
        num, den = self.time_sig
        for section in sections:
            section_beats = float(section.bars * num * (4.0 / den))
            for name in all_track_names:
                events = section.tracks.get(name)
                if events:
                    built[name].extend(events)
                    # Pad remainder if events are shorter than section
                    used = sum((e.duration if hasattr(e, "duration") else 0.0) for e in events)
                    if used < section_beats:
                        built[name].add(Note.rest(section_beats - used))
                else:
                    built[name].add(Note.rest(section_beats))

        for track in built.values():
            self.add_track(track)

        return self

    def merge(self, other: "Song", title: str | None = None) -> "Song":
        """Combine two songs by layering all their tracks into a new Song.

        Both songs' tracks, poly_tracks, and voice_tracks are copied into
        the result. The BPM and sample_rate come from self (the first song).
        Effects dicts are merged (other's effects override on name collision).

        Args:
            other: The second song to layer in.
            title: Title for the merged song (default: "self.title + other.title").

        Returns:
            A new Song containing all tracks from both songs.

        Example::

            drums = Song(title="Drums", bpm=120)
            # ... add drum tracks ...
            melody = Song(title="Melody", bpm=120)
            # ... add melody tracks ...
            full = drums.merge(melody, title="Full Arrangement")
        """
        import copy

        merged = Song(
            title=title or f"{self.title} + {other.title}",
            bpm=self.bpm,
            sample_rate=self.sample_rate,
            time_sig=self.time_sig,
            key_sig=self.key_sig,
            composer=self.composer,
        )

        # Copy tracks from both songs
        for track in self.tracks:
            merged.tracks.append(copy.deepcopy(track))
        for track in other.tracks:
            merged.tracks.append(copy.deepcopy(track))

        # Copy poly tracks
        for pt in self.poly_tracks:
            merged.poly_tracks.append(copy.deepcopy(pt))
        for pt in other.poly_tracks:
            merged.poly_tracks.append(copy.deepcopy(pt))

        # Copy voice tracks
        for vt in self.voice_tracks:
            merged.voice_tracks.append(copy.deepcopy(vt))
        for vt in other.voice_tracks:
            merged.voice_tracks.append(copy.deepcopy(vt))

        # Copy time_sig_map
        merged.time_sig_map = list(self.time_sig_map) + list(other.time_sig_map)
        merged.time_sig_map.sort(key=lambda x: x[0])

        # Merge effects dicts
        fx = dict(self.effects or {})
        fx.update(other.effects or {})
        merged.effects = fx

        return merged

    def info(self) -> dict:
        """Return a summary dict of this song's metadata and structure.

        Useful for dashboards, CLI tools, and inspecting songs programmatically.

        Returns::

            {
                "title":       "Trance Odyssey",
                "bpm":         138.0,
                "duration_sec": 90.2,
                "total_beats":  207.5,
                "time_sig":     (4, 4),
                "key_sig":      "C",
                "composer":     "",
                "sample_rate":  44100,
                "tracks":       5,
                "poly_tracks":  0,
                "voice_tracks": 0,
                "track_names":  ["kick", "snare", "hat", "pad", "lead"],
            }
        """
        return {
            "title": self.title,
            "bpm": self.bpm,
            "duration_sec": round(self.duration_sec, 1),
            "total_beats": round(self.total_beats, 1),
            "time_sig": self.time_sig,
            "key_sig": self.key_sig,
            "composer": self.composer,
            "sample_rate": self.sample_rate,
            "tracks": len(self.tracks),
            "poly_tracks": len(self.poly_tracks),
            "voice_tracks": len(self.voice_tracks),
            "track_names": [t.name for t in self.tracks],
        }

    def analyze(self) -> dict:
        """Return a comprehensive musical analysis of this song.

        Combines metadata, harmonic analysis, melodic analysis, rhythmic
        analysis, arrangement analysis, and style fingerprint into a
        single dict. Everything you want to know about a song in one call.

        Returns:
            Dict with sections: info, harmonic, melodic, rhythmic,
            arrangement, fingerprint, critique, suggestions.

        Example::

            >>> from code_music import Song, Track, Note
            >>> song = Song(title="Test", bpm=120, key_sig="C")
            >>> tr = song.add_track(Track(instrument="piano"))
            >>> tr.add(Note("C", 4, 1.0))
            >>> result = song.analyze()
            >>> "info" in result and "arrangement" in result
            True
        """
        result = {"info": self.info()}

        # Harmonic analysis: extract chords and analyze
        chords = []
        for track in self.tracks:
            for beat in track.beats:
                if beat.event is not None and hasattr(beat.event, "root"):
                    shape = beat.event.shape if isinstance(beat.event.shape, str) else "maj"
                    chords.append((beat.event.root, shape))

        key = self.key_sig or "C"

        if chords:
            try:
                from .theory.harmony import (
                    detect_cadences,
                    detect_key,
                    functional_analysis,
                    tension_curve,
                )

                detected_key, _, key_conf = detect_key(chords)
                cadences = detect_cadences(chords, key)
                functions = functional_analysis(chords, key)
                tensions = tension_curve(chords, key=key)

                result["harmonic"] = {
                    "detected_key": detected_key,
                    "key_confidence": round(key_conf, 3),
                    "chord_count": len(chords),
                    "unique_roots": len(set(r for r, _ in chords)),
                    "unique_qualities": len(set(s for _, s in chords)),
                    "cadences": len(cadences),
                    "tension_mean": round(sum(tensions) / max(len(tensions), 1), 3),
                    "tension_range": round((max(tensions) - min(tensions)) if tensions else 0, 3),
                    "functions": [f.get("roman", "?") for f in functions[:8]],
                }
            except Exception:
                result["harmonic"] = {"chord_count": len(chords)}
        else:
            result["harmonic"] = {"chord_count": 0}

        # Melodic analysis: extract notes
        all_notes = []
        for track in self.tracks:
            for beat in track.beats:
                if (
                    beat.event is not None
                    and hasattr(beat.event, "pitch")
                    and beat.event.pitch is not None
                ):
                    all_notes.append(beat.event)

        if all_notes:
            pitches = []
            for n in all_notes:
                try:
                    from .theory._core import _semi

                    midi = _semi(str(n.pitch)) + n.octave * 12
                    pitches.append(midi)
                except Exception:
                    pass

            intervals = [abs(pitches[i] - pitches[i - 1]) for i in range(1, len(pitches))]
            steps = sum(1 for iv in intervals if iv <= 2)
            leaps = sum(1 for iv in intervals if iv > 4)
            total_iv = max(len(intervals), 1)

            result["melodic"] = {
                "note_count": len(all_notes),
                "pitch_range": (max(pitches) - min(pitches)) if pitches else 0,
                "avg_interval": round(sum(intervals) / total_iv, 2),
                "step_ratio": round(steps / total_iv, 3),
                "leap_ratio": round(leaps / total_iv, 3),
                "avg_duration": round(sum(n.duration for n in all_notes) / len(all_notes), 3),
            }
        else:
            result["melodic"] = {"note_count": 0}

        # Rhythmic analysis
        all_durations = []
        rest_count = 0
        for track in self.tracks:
            for beat in track.beats:
                all_durations.append(beat.duration)
                if beat.event is None:
                    rest_count += 1

        total_events = max(len(all_durations), 1)
        result["rhythmic"] = {
            "total_events": total_events,
            "rest_ratio": round(rest_count / total_events, 3),
            "avg_duration": round(sum(all_durations) / total_events, 3),
            "duration_variety": len(set(round(d, 3) for d in all_durations)),
        }

        # Arrangement analysis
        try:
            from .theory.analysis import analyze_arrangement

            result["arrangement"] = analyze_arrangement(self)
        except Exception:
            result["arrangement"] = {"track_count": len(self.tracks)}

        # Style fingerprint
        try:
            from .theory.analysis import style_fingerprint

            result["fingerprint"] = style_fingerprint(self)
        except Exception:
            result["fingerprint"] = {}

        # Critique
        if chords:
            try:
                from .theory.analysis import critique_song

                result["critique"] = critique_song(self, key)
            except Exception:
                result["critique"] = {}

        return result

    def fill_tracks(
        self,
        roles: list[str] | None = None,
        genre: str = "pop",
        seed: int | None = None,
    ) -> "Song":
        """Auto-fill missing instrument roles in the song.

        Analyzes which roles (melody, bass, chords, drums) are present
        and generates tracks for the missing ones. Turn a melody sketch
        into a full arrangement in one call.

        Args:
            roles:  Roles to fill. None = auto-detect what is missing and
                    fill all gaps. Options: 'bass', 'chords', 'drums', 'melody'.
            genre:  Style for generated tracks (pop, jazz, rock, blues,
                    classical, electronic, ambient).
            seed:   Random seed.

        Returns:
            self (mutated with new tracks added).

        Example::

            >>> song = Song(title="Sketch", bpm=120, key_sig="C")
            >>> lead = song.add_track(Track(name="lead", instrument="piano"))
            >>> lead.extend(scale("C", "major", octave=5, length=16))
            >>> song.fill_tracks(genre="jazz")  # adds bass, chords, drums
        """
        import random as _rng

        rng = _rng.Random(seed)
        key = self.key_sig or "C"

        # Detect existing roles by instrument name
        existing_instruments = set(t.instrument for t in self.tracks)
        existing_names = set(t.name.lower() for t in self.tracks)

        _bass_instr = {"bass", "sub_bass", "sub_808", "fm_bass", "vintage_bass"}
        _drum_instr = {"drums_kick", "drums_snare", "drums_hat", "percussion"}
        _chord_instr = {
            "pad",
            "piano",
            "organ",
            "pluck",
            "vintage_epiano",
            "vintage_organ",
            "vintage_pad",
            "vintage_strings",
        }
        _melody_instr = {"sawtooth", "sine", "square", "triangle", "vintage_lead", "fm_bell"}

        has_bass = bool(existing_instruments & _bass_instr) or "bass" in existing_names
        has_drums = bool(existing_instruments & _drum_instr) or any(
            "drum" in n or "kick" in n or "hat" in n for n in existing_names
        )
        has_chords = bool(existing_instruments & _chord_instr) or "chords" in existing_names
        has_melody = (
            bool(existing_instruments & _melody_instr)
            or "melody" in existing_names
            or "lead" in existing_names
        )

        if roles is None:
            roles_to_fill = []
            if not has_bass:
                roles_to_fill.append("bass")
            if not has_chords:
                roles_to_fill.append("chords")
            if not has_drums:
                roles_to_fill.append("drums")
            if not has_melody:
                roles_to_fill.append("melody")
        else:
            roles_to_fill = list(roles)

        if not roles_to_fill:
            return self  # nothing to fill

        # Calculate target length from existing tracks
        total_beats = self.total_beats
        bars = max(4, int(total_beats / 4))
        chords_needed = max(4, bars)

        # Generate a chord progression for the song
        try:
            from .theory.generation import generate_progression

            prog = generate_progression(
                key=key,
                length=chords_needed,
                genre=genre,
                seed=rng.randint(0, 2**31),
            )
        except Exception:
            prog = [(key, "maj"), ("F", "maj"), ("G", "maj"), (key, "maj")]
            while len(prog) < chords_needed:
                prog = prog + prog
            prog = prog[:chords_needed]

        chord_dur = max(1.0, total_beats / max(len(prog), 1))

        if "chords" in roles_to_fill:
            chord_track = self.add_track(
                Track(name="chords", instrument="pad", volume=0.35, pan=-0.1)
            )
            for root, shape in prog:
                chord_track.add(Chord(root, shape, 3, duration=chord_dur, velocity=50))

        if "bass" in roles_to_fill:
            try:
                from .theory.generation import generate_bass_line

                bass_style = {
                    "jazz": "walking",
                    "blues": "walking",
                    "electronic": "syncopated",
                }.get(genre, "root_fifth")
                bass_notes = generate_bass_line(
                    prog,
                    style=bass_style,
                    seed=rng.randint(0, 2**31),
                )
                bass_track = self.add_track(Track(name="bass", instrument="bass", volume=0.5))
                bass_track.extend(bass_notes)
            except Exception:
                bass_track = self.add_track(Track(name="bass", instrument="bass", volume=0.5))
                for root, _ in prog:
                    bass_track.add(Note(root, 2, chord_dur, velocity=65))

        if "drums" in roles_to_fill and genre not in ("ambient", "classical"):
            drum_genres = {
                "pop": "rock",
                "rock": "rock",
                "jazz": "jazz",
                "blues": "jazz",
                "electronic": "electronic",
            }
            drum_genre = drum_genres.get(genre, "rock")
            try:
                from .theory.generation import generate_drums

                drum_data = generate_drums(
                    drum_genre,
                    bars=bars,
                    seed=rng.randint(0, 2**31),
                )
                for drum_name, drum_notes in drum_data.items():
                    instr = f"drums_{drum_name}"
                    if instr not in ("drums_kick", "drums_snare", "drums_hat"):
                        instr = "drums_kick"
                    dr = self.add_track(Track(name=drum_name, instrument=instr, volume=0.5))
                    dr.extend(drum_notes)
            except Exception:
                kick = self.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
                for _ in range(bars * 4):
                    kick.add(Note("C", 4, 1.0, velocity=75))

        if "melody" in roles_to_fill:
            try:
                from .theory.generation import generate_scale_melody

                _scale_map = {
                    "jazz": "dorian",
                    "blues": "blues",
                    "classical": "major",
                    "ambient": "pentatonic",
                }
                scale_name = _scale_map.get(genre, "pentatonic")
                mel = generate_scale_melody(
                    key=key,
                    scale_name=scale_name,
                    length=bars * 4,
                    octave=5,
                    duration=1.0,
                    seed=rng.randint(0, 2**31),
                )
                mel_track = self.add_track(
                    Track(name="melody", instrument="sawtooth", volume=0.5, pan=0.15)
                )
                mel_track.extend(mel)
            except Exception:
                mel_track = self.add_track(
                    Track(name="melody", instrument="sawtooth", volume=0.5, pan=0.15)
                )
                mel_track.extend(scale(key, "pentatonic", octave=5, length=bars * 4))

        return self

    def master(
        self,
        eq_bands: list | None = None,
        compress_threshold: float = 0.6,
        compress_ratio: float = 3.0,
        ceiling: float = 0.98,
    ) -> "Song":
        """Set up a master bus chain: EQ → compress → limit.

        Adds a ``_master_chain`` attribute that the Synth applies to the
        final stereo mix after all tracks are rendered and mixed.

        Args:
            eq_bands:           List of (freq_hz, gain_db, q) tuples for parametric EQ.
                                Default: gentle presence boost + low warmth + air.
            compress_threshold: Compressor threshold (0.0–1.0).
            compress_ratio:     Compression ratio.
            ceiling:            Limiter ceiling (0.0–1.0, typically 0.95–0.99).

        Returns:
            self for chaining.

        Example::

            song = Song(title="My Track", bpm=120)
            song.master()  # sensible defaults
            # or custom:
            song.master(
                eq_bands=[(80, +2.0, 0.7), (3000, +1.5, 1.2), (10000, +1.0, 0.8)],
                compress_threshold=0.5,
                compress_ratio=4.0,
                ceiling=0.97,
            )
        """
        if eq_bands is None:
            eq_bands = [
                (80.0, +1.5, 0.7),
                (3000.0, +1.0, 1.0),
                (10000.0, +0.8, 0.8),
            ]
        self._master_chain = {
            "eq_bands": eq_bands,
            "compress_threshold": compress_threshold,
            "compress_ratio": compress_ratio,
            "ceiling": ceiling,
        }
        return self

    def export_stems(
        self,
        out_dir: str,
        fmt: str = "wav",
        include_effects: bool = False,
        use_title_prefix: bool = False,
    ) -> list:
        """Render each track as a separate audio file (stem export).

        Creates one file per track. Naming convention:
        - Default: ``<track_name>.<fmt>``
        - With use_title_prefix: ``<song_title>_<track_name>.<fmt>``

        Args:
            out_dir:          Output directory (created if missing).
            fmt:              Audio format - "wav" (default), "flac", or "mp3".
            include_effects:  Apply per-track effects from song.effects dict.
            use_title_prefix: Prefix filenames with song title.

        Returns:
            List of Path objects for the written files.

        Example::

            song.export_stems("dist/stems/my_song/")
            song.export_stems("dist/stems/", include_effects=True, use_title_prefix=True)
        """
        from pathlib import Path as _Path

        from .export import export_flac, export_mp3, export_wav
        from .synth import Synth

        out = _Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        synth = Synth(sample_rate=self.sample_rate)
        total_beats = self.total_beats
        results = []

        import math

        import numpy as np

        effects_dict = getattr(self, "effects", {}) or {}

        for track in self.tracks:
            mono = synth.render_track(track, self.bpm, total_beats)
            total_samples = len(mono)
            # Pan to stereo
            angle = (track.pan + 1) / 2 * math.pi / 2
            stereo = np.zeros((total_samples, 2))
            stereo[:, 0] = mono * math.cos(angle)
            stereo[:, 1] = mono * math.sin(angle)
            # Normalize
            peak = np.max(np.abs(stereo))
            if peak > 0:
                stereo /= peak
            stereo = np.tanh(stereo * 0.95)

            # Apply per-track effects if requested
            if include_effects and track.name in effects_dict:
                fx = effects_dict[track.name]
                try:
                    if callable(fx):
                        stereo = fx(stereo, self.sample_rate)
                    elif hasattr(fx, "apply"):
                        stereo = fx.apply(stereo, self.sample_rate)
                except Exception:
                    pass  # skip broken effects, do not lose the stem

            safe_name = track.name.replace(" ", "_").replace("/", "_")
            if use_title_prefix:
                safe_title = self.title.lower().replace(" ", "_").replace("/", "_")
                filename = f"{safe_title}_{safe_name}.{fmt}"
            else:
                filename = f"{safe_name}.{fmt}"

            path = out / filename
            if fmt == "flac":
                export_flac(stereo, path, self.sample_rate)
            elif fmt == "mp3":
                export_mp3(stereo, path, self.sample_rate)
            else:
                export_wav(stereo, path, self.sample_rate)
            results.append(path)

        return results

    @classmethod
    def import_stems(
        cls,
        directory: str,
        bpm: float = 120,
        title: str | None = None,
        sample_rate: int = 44100,
    ) -> "Song":
        """Import a directory of WAV files as a Song with SampleTracks.

        Each WAV file becomes a SampleTrack triggered at beat 0. The file
        name (without extension) becomes the track name. This is the inverse
        of export_stems() - round-trip a song through stems and back.

        Args:
            directory:   Path to directory containing WAV files.
            bpm:         Tempo for the imported song.
            title:       Song title. Defaults to directory name.
            sample_rate: Sample rate for the song.

        Returns:
            A Song with one SampleTrack per WAV file found.

        Example::

            >>> import tempfile, os
            >>> song = Song.import_stems(tempfile.gettempdir(), bpm=120)
        """
        from pathlib import Path as _Path

        stem_dir = _Path(directory)
        if not stem_dir.is_dir():
            raise FileNotFoundError(f"Not a directory: {directory}")

        if title is None:
            title = stem_dir.name

        song = cls(title=title, bpm=bpm, sample_rate=sample_rate)

        wav_files = sorted(
            p for p in stem_dir.iterdir() if p.suffix.lower() in (".wav", ".flac", ".mp3")
        )

        for wav_path in wav_files:
            st = SampleTrack.from_wav(
                str(wav_path),
                name=wav_path.stem,
                volume=0.8,
            )
            st.trigger(at=0.0)
            song.add_sample_track(st)

        return song

    @property
    def beat_duration_sec(self) -> float:
        return 60.0 / self.bpm

    @property
    def total_beats(self) -> float:
        seq_beats = max((t.total_beats for t in self.tracks), default=0.0)
        poly_beats = max((t.total_beats for t in self.poly_tracks), default=0.0)
        sample_beats = max((t.total_beats for t in self.sample_tracks), default=0.0)

        voice_beats = 0.0
        for track in self.voice_tracks:
            estimate = getattr(track, "estimate_total_beats", None)
            if callable(estimate):
                try:
                    voice_beats = max(voice_beats, float(estimate(self.bpm)))
                except Exception:
                    continue

        return max(seq_beats, poly_beats, sample_beats, voice_beats)

    @property
    def duration_sec(self) -> float:
        return self.total_beats * self.beat_duration_sec

    def to_dict(self) -> dict:
        """Serialize the Song to a plain dict (JSON-compatible).

        Includes title, bpm, time_sig, key_sig, bpm_map, effects (via
        EffectsChain.to_dict), and all tracks with their note/chord data.

        Example::

            data = song.to_dict()
            import json
            json.dumps(data)  # fully JSON-serializable
        """
        tracks_data = []
        for track in self.tracks:
            beats_data = []
            for beat in track.beats:
                if beat.event is None:
                    beats_data.append({"type": "rest", "duration": beat.duration})
                elif isinstance(beat.event, Note):
                    e = beat.event
                    beats_data.append(
                        {
                            "type": "note",
                            "pitch": e.pitch,
                            "octave": e.octave,
                            "duration": e.duration,
                            "velocity": e.velocity,
                        }
                    )
                elif isinstance(beat.event, Chord):
                    e = beat.event
                    beats_data.append(
                        {
                            "type": "chord",
                            "root": e.root,
                            "shape": e.shape,
                            "octave": e.octave,
                            "duration": e.duration,
                            "velocity": e.velocity,
                        }
                    )
            tracks_data.append(
                {
                    "name": track.name,
                    "instrument": track.instrument,
                    "volume": track.volume,
                    "pan": track.pan,
                    "swing": track.swing,
                    "density": track.density,
                    "beats": beats_data,
                }
            )

        fx_data = {}
        for name, chain in self.effects.items():
            if hasattr(chain, "to_dict"):
                fx_data[name] = chain.to_dict()

        return {
            "title": self.title,
            "bpm": self.bpm,
            "sample_rate": self.sample_rate,
            "time_sig": list(self.time_sig),
            "key_sig": self.key_sig,
            "composer": self.composer,
            "bpm_map": self.bpm_map,
            "tracks": tracks_data,
            "effects": fx_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Song":
        """Reconstruct a Song from a dict produced by ``to_dict()``.

        Example::

            song = Song.from_dict(data)
            audio = song.render()
        """
        from .effects import EffectsChain

        song = cls(
            title=data.get("title", "untitled"),
            bpm=data.get("bpm", 120.0),
            sample_rate=data.get("sample_rate", 44100),
            time_sig=tuple(data.get("time_sig", [4, 4])),
            key_sig=data.get("key_sig", "C"),
            composer=data.get("composer", ""),
            bpm_map=data.get("bpm_map", []),
        )

        for td in data.get("tracks", []):
            track = Track(
                name=td.get("name", ""),
                instrument=td.get("instrument", "sine"),
                volume=td.get("volume", 0.8),
                pan=td.get("pan", 0.0),
                swing=td.get("swing", 0.0),
                density=td.get("density", 1.0),
            )
            for bd in td.get("beats", []):
                btype = bd.get("type", "rest")
                if btype == "rest":
                    track.add(Note.rest(bd["duration"]))
                elif btype == "note":
                    track.add(
                        Note(
                            bd["pitch"],
                            bd.get("octave", 4),
                            bd["duration"],
                            velocity=bd.get("velocity", 0.8),
                        )
                    )
                elif btype == "chord":
                    track.add(
                        Chord(
                            bd["root"],
                            bd["shape"],
                            bd.get("octave", 3),
                            duration=bd["duration"],
                            velocity=bd.get("velocity", 0.8),
                        )
                    )
            song.add_track(track)

        for name, chain_data in data.get("effects", {}).items():
            song.effects[name] = EffectsChain.from_dict(chain_data)

        return song

    def export_json(self, path):
        """Save the song to a JSON file via ``to_dict()``.

        Example::

            song.export_json("my_song.json")
        """
        import json
        from pathlib import Path as _Path

        out = _Path(path)
        out.write_text(json.dumps(self.to_dict(), indent=2))
        return out

    @classmethod
    def load_json(cls, path) -> "Song":
        """Load a Song from a JSON file created by ``export_json()``.

        Example::

            song = Song.load_json("my_song.json")
            audio = song.render()
        """
        import json
        from pathlib import Path as _Path

        data = json.loads(_Path(path).read_text())
        return cls.from_dict(data)

    def render(self):
        """Render the song to a stereo float64 numpy array.

        Convenience wrapper — equivalent to ``Synth(self.sample_rate).render_song(self)``.

        Returns:
            Stereo float64 array of shape (N, 2).

        Example::

            audio = song.render()
            export_wav(audio, "my_song.wav", song.sample_rate)
        """
        from .synth import Synth

        return Synth(sample_rate=self.sample_rate).render_song(self)


# ---------------------------------------------------------------------------
# Chord progression suggester
# ---------------------------------------------------------------------------

# Common progressions by mood, expressed as Roman numeral scale degrees (0-based)
# Each tuple: (scale_degree, chord_shape)
_PROGRESSIONS: dict[str, list[list[tuple[int, str]]]] = {
    "happy": [
        [(0, "maj"), (4, "maj"), (5, "maj"), (3, "min")],  # I-V-vi-IV  (pop)
        [(0, "maj"), (3, "min"), (4, "maj"), (4, "maj")],  # I-IV-V-V
        [(0, "maj"), (4, "maj"), (3, "maj"), (0, "maj")],  # I-V-IV-I  (rock)
    ],
    "sad": [
        [(5, "min"), (3, "maj"), (0, "maj"), (4, "maj")],  # vi-IV-I-V  (emotional pop)
        [(0, "min"), (6, "maj"), (3, "maj"), (4, "dom7")],  # i-bVII-bIV-V
        [(0, "min"), (5, "min"), (3, "maj"), (4, "dom7")],  # i-v-bIII-iv
    ],
    "tense": [
        [(0, "min"), (1, "dim"), (2, "min"), (4, "dom7")],  # i-ii°-III-V
        [(0, "min"), (6, "maj"), (4, "dom7"), (0, "min")],  # i-bVII-V-i
        [(0, "min7"), (5, "min7"), (2, "min7"), (4, "dom7")],  # jazz minor ii-V-i
    ],
    "dreamy": [
        [(0, "maj7"), (4, "maj7"), (2, "min7"), (3, "maj7")],  # Imaj7-Vmaj7-IIm7-IVmaj7
        [(0, "maj7"), (5, "min7"), (2, "min7"), (4, "dom7")],  # I-vi-ii-V jazz
        [(0, "maj7"), (3, "maj7"), (4, "dom7"), (0, "maj7")],  # I-IV-V7-I dreamy
    ],
    "epic": [
        [(0, "min"), (7, "maj"), (4, "maj"), (6, "maj")],  # i-bVIII-bV-bVII
        [(0, "min"), (5, "maj"), (3, "maj"), (6, "maj")],  # i-bVI-bIII-bVII  (Zimmer)
        [(0, "min"), (7, "maj"), (3, "maj"), (4, "dom7")],  # i-bVIII-bIII-V
    ],
    "groovy": [
        [(0, "dom7"), (3, "dom7"), (4, "dom7"), (3, "dom7")],  # I7-IV7-V7-IV7 blues
        [(0, "min7"), (0, "min7"), (3, "dom7"), (3, "dom7")],  # i7-i7-IV7-IV7 funk
        [(0, "min7"), (3, "dom7"), (5, "min7"), (1, "dom7")],  # jazz minor turnaround
    ],
    "dark": [
        [(0, "min"), (1, "dim"), (6, "maj"), (4, "dom7")],  # i-ii°-bVII-V  phrygian feel
        [(0, "min"), (1, "maj"), (4, "dom7"), (0, "min")],  # i-bII-V-i  Spanish/metal
        [(0, "min7"), (5, "min"), (2, "dim"), (4, "dom7")],  # i-v-ii°-V
    ],
    "chill": [
        [(0, "maj7"), (2, "min7"), (3, "maj7"), (4, "dom7")],  # I-II-IV-V jazz
        [(0, "min7"), (3, "maj7"), (6, "maj7"), (2, "dom7")],  # i-bIII-bVI-V lo-fi
        [(0, "maj7"), (4, "maj7"), (5, "min7"), (4, "dom7")],  # I-V-vi-V slow
    ],
}

_SCALE_MAJOR_DEGREES = [0, 2, 4, 5, 7, 9, 11]  # major scale intervals


def suggest_progression(
    root: str,
    mood: str = "happy",
    octave: int = 3,
    duration: float = 4.0,
    velocity: float = 0.65,
    variation: int = 0,
) -> list[Chord]:
    """Suggest a chord progression for a given root and mood.

    Looks up a common progression for the mood, maps the Roman numeral
    scale degrees to actual chord roots, and returns a list of Chords
    ready to add to a Track.

    Args:
        root:      Root note name (e.g. 'C', 'F#', 'Bb').
        mood:      Emotional character: happy, sad, tense, dreamy, epic,
                   groovy, dark, chill.
        octave:    Octave for chord voicings (3 or 4 typical).
        duration:  Beats per chord.
        velocity:  Chord velocity (0.0–1.0).
        variation: Which progression variation to use (0, 1, or 2).

    Returns:
        List of Chord objects — pass directly to Track.extend().

    Example::

        pad.extend(suggest_progression("Am", mood="sad", duration=4.0))
        pad.extend(suggest_progression("C",  mood="happy") * 4)

    Available moods: happy, sad, tense, dreamy, epic, groovy, dark, chill
    """
    if mood not in _PROGRESSIONS:
        raise ValueError(f"Unknown mood {mood!r}. Choose: {sorted(_PROGRESSIONS)}")

    variants = _PROGRESSIONS[mood]
    prog = variants[variation % len(variants)]

    root_midi = note_name_to_midi(root, octave=4)
    result = []
    for degree, shape in prog:
        # Map degree to semitone offset using major scale
        deg_idx = degree % len(_SCALE_MAJOR_DEGREES)
        oct_offset = degree // len(_SCALE_MAJOR_DEGREES)
        semitone = _SCALE_MAJOR_DEGREES[deg_idx] + oct_offset * 12
        chord_midi = root_midi + semitone
        chord_name = NOTE_NAMES[chord_midi % 12]
        result.append(
            Chord(
                root=chord_name,
                shape=shape,
                octave=octave,
                duration=duration,
                velocity=velocity,
            )
        )
    return result


# ---------------------------------------------------------------------------
# PolyphonicTrack — multiple notes sounding simultaneously
# ---------------------------------------------------------------------------


@dataclass
class PolyphonicTrack:
    """A track where multiple notes can sound at the same time.

    Unlike a regular Track (which is sequential — one note at a time),
    PolyphonicTrack holds a list of (Note, start_beat) pairs. All notes
    that overlap in time are mixed together during render.

    Useful for: piano left hand (full chord voicings that sustain while
    the right hand plays melody), guitar strumming, organ, pads with
    individual note control.

    Example::

        piano = song.add_polytrack(PolyphonicTrack(name="piano", instrument="piano"))
        piano.add(Note("C", 3, duration=4.0), at=0.0)   # bass note sustains
        piano.add(Note("E", 3, duration=4.0), at=0.0)   # chord tones
        piano.add(Note("G", 3, duration=4.0), at=0.0)
        piano.add(Note("C", 5, duration=0.5), at=0.5)   # melody over the top
        piano.add(Note("D", 5, duration=0.5), at=1.0)

    Attributes:
        name:       Track label.
        instrument: Synth preset name.
        volume:     Track gain 0.0–1.0.
        pan:        Stereo position -1.0 (L) to 1.0 (R).
        events:     List of (Note, start_beat) pairs — sorted by start_beat.
    """

    name: str = "poly"
    instrument: str = "piano"
    volume: float = 0.8
    pan: float = 0.0
    events: list[tuple[Note, float]] = field(default_factory=list)

    def add(self, note: Note, at: float) -> "PolyphonicTrack":
        """Add a note at a specific beat position. Returns self for chaining."""
        self.events.append((note, at))
        return self

    def add_chord(self, chord: Chord, at: float) -> "PolyphonicTrack":
        """Add all notes of a chord simultaneously at a beat position."""
        for note in chord.notes:
            self.events.append((note, at))
        return self

    @property
    def total_beats(self) -> float:
        if not self.events:
            return 0.0
        return max(at + note.duration for note, at in self.events)


# ---------------------------------------------------------------------------
# Song remix helper
# ---------------------------------------------------------------------------


def remix(
    song: "Song", semitones: int = 0, bpm_factor: float = 1.0, title: str | None = None
) -> "Song":
    """Create a remixed version of a song with transposition and/or tempo change.

    Args:
        song:        Source song to remix.
        semitones:   Transpose all pitched notes by this many semitones.
                     +7 = up a fifth, -5 = down a fourth, +12 = up an octave.
        bpm_factor:  Multiply the BPM by this factor.
                     1.5 = 50% faster, 0.75 = 25% slower.
        title:       Title for the remixed song (default: original + " (Remix)").

    Returns:
        A new Song with all tracks transposed and/or retempoed.

    Example::

        # Transpose "Offshore" up a minor third, 10% faster
        remixed = remix(song, semitones=3, bpm_factor=1.1, title="Offshore (Club Mix)")
        # Then render the remix
        from code_music.synth import Synth
        from code_music.export import export_wav
        export_wav(Synth().render_song(remixed), "remix.wav")
    """
    import copy

    new_song = Song(
        title=title or f"{song.title} (Remix)",
        bpm=song.bpm * bpm_factor,
        sample_rate=song.sample_rate,
        time_sig=song.time_sig,
        key_sig=song.key_sig,
        composer=song.composer,
    )
    new_song.effects = copy.copy(song.effects or {})

    for track in song.tracks:
        new_track = new_song.add_track(
            Track(
                name=track.name,
                instrument=track.instrument,
                volume=track.volume,
                pan=track.pan,
                swing=track.swing,
            )
        )
        for beat in track.beats:
            if beat.event is None:
                new_track.add(Note.rest(beat.duration))
            elif isinstance(beat.event, Note):
                n = beat.event
                if n.pitch is None:
                    new_track.add(Note.rest(n.duration))
                elif semitones == 0:
                    new_track.add(copy.copy(n))
                else:
                    new_midi = (n.midi or 60) + semitones
                    new_track.add(Note(pitch=new_midi, duration=n.duration, velocity=n.velocity))
            elif isinstance(beat.event, Chord):
                c = beat.event
                if semitones == 0:
                    new_track.add(copy.copy(c))
                else:
                    # Transpose chord root
                    root_midi = note_name_to_midi(c.root, c.octave) + semitones
                    new_root = NOTE_NAMES[root_midi % 12]
                    new_oct = root_midi // 12 - 1
                    new_track.add(Chord(new_root, c.shape, new_oct, c.duration, c.velocity))
    return new_song


# ---------------------------------------------------------------------------
# BPM automation — gradual tempo change within a song
# ---------------------------------------------------------------------------


def bpm_ramp(
    start_bpm: float,
    end_bpm: float,
    bars: int,
    beats_per_bar: int = 4,
) -> list[float]:
    """Return a list of per-beat BPM values for a gradual tempo change.

    Useful for ritardando (slowing down), accelerando (speeding up),
    or rubato (free tempo). Assign to ``song.bpm_map`` and the synth
    renderer will use per-beat tempo instead of a flat BPM.

    Args:
        start_bpm:    Starting tempo.
        end_bpm:      Ending tempo.
        bars:         How many bars the ramp spans.
        beats_per_bar: Beats per bar (default 4).

    Returns:
        List of BPM values, one per beat, linearly interpolated.

    Example::

        # Ritardando over 4 bars: 120 BPM → 80 BPM
        ramp = bpm_ramp(120, 80, bars=4)
        song.bpm_map = ramp
    """
    total_beats = bars * beats_per_bar
    return [
        start_bpm + (end_bpm - start_bpm) * (i / max(total_beats - 1, 1))
        for i in range(total_beats)
    ]


def accelerando(
    start_bpm: float, bars: int, factor: float = 1.5, beats_per_bar: int = 4
) -> list[float]:
    """Gradual speed-up. factor=1.5 means end BPM is 50% faster than start."""
    return bpm_ramp(start_bpm, start_bpm * factor, bars, beats_per_bar)


def ritardando(
    start_bpm: float, bars: int, factor: float = 0.7, beats_per_bar: int = 4
) -> list[float]:
    """Gradual slow-down. factor=0.7 means end BPM is 30% slower than start."""
    return bpm_ramp(start_bpm, start_bpm * factor, bars, beats_per_bar)


# ---------------------------------------------------------------------------
# Roman numeral chord analysis
# ---------------------------------------------------------------------------

_ROMAN = ["I", "bII", "II", "bIII", "III", "IV", "#IV", "V", "bVI", "VI", "bVII", "VII"]

_CHORD_QUALITY_SYMBOLS = {
    "maj": "",
    "min": "m",
    "dim": "°",
    "aug": "+",
    "maj7": "Δ7",
    "min7": "m7",
    "dom7": "7",
    "min7b5": "ø7",
    "dim7": "°7",
    "sus2": "sus2",
    "sus4": "sus4",
    "maj9": "Δ9",
    "min9": "m9",
    "dom9": "9",
}


def analyze_progression(
    chords: list[Chord],
    key_root: str = "C",
    mode: str = "major",
) -> list[str]:
    """Analyze a chord progression and return Roman numeral notation.

    Args:
        chords:    List of Chord objects to analyze.
        key_root:  Root note of the key (e.g. 'C', 'F#', 'Bb').
        mode:      'major' or 'minor'.

    Returns:
        List of Roman numeral strings (e.g. ['I', 'V', 'vi', 'IV']).

    Example::

        prog = suggest_progression("C", mood="happy")
        print(analyze_progression(prog, key_root="C"))
        # → ['I', 'V', 'vi', 'IV']
    """
    key_midi = note_name_to_midi(key_root, 4)
    result = []
    for chord in chords:
        chord_midi = note_name_to_midi(chord.root, 4)
        interval = (chord_midi - key_midi) % 12
        roman = _ROMAN[interval]

        # Determine if it's major/minor quality for case
        shape = chord.shape if isinstance(chord.shape, str) else "custom"
        is_minor = shape.startswith("min") or shape in ("dim", "dim7", "min7b5")
        quality = _CHORD_QUALITY_SYMBOLS.get(shape, f"({shape})")

        # Lowercase Roman for minor chords in major key
        if is_minor and mode == "major":
            roman = roman.lower()

        result.append(f"{roman}{quality}")
    return result


# ---------------------------------------------------------------------------
# Voice leading helper — smooth chord transitions
# ---------------------------------------------------------------------------


def voice_lead(
    chords: list[Chord],
    octave: int = 3,
    duration: float | None = None,
    velocity: float = 0.65,
) -> list[Chord]:
    """Return a version of the chord progression with smoother voice leading.

    Minimises the total semitone movement between adjacent chords by
    choosing the voicing (inversion) of each chord that moves the least
    distance from the previous chord.

    Args:
        chords:    Input chord progression.
        octave:    Base octave for voicing.
        duration:  Override chord duration (None = keep original).
        velocity:  Override chord velocity (None = keep original).

    Returns:
        New list of Chords with optimised inversions.

    Example::

        prog = suggest_progression("C", mood="happy")
        smooth = voice_lead(prog)          # minimise jumps between chords
        pad.extend(smooth * 4)
    """
    if not chords:
        return []

    def _chord_midis(chord: Chord, oct: int) -> list[int]:
        root_midi = note_name_to_midi(chord.root, oct)
        offsets = CHORD_SHAPES[chord.shape] if isinstance(chord.shape, str) else list(chord.shape)
        return [root_midi + o for o in offsets]

    def _inversion_midis(base_midis: list[int], inv: int) -> list[int]:
        """Rotate bottom `inv` notes up an octave."""
        midis = list(base_midis)
        for _ in range(inv % len(midis)):
            midis = midis[1:] + [midis[0] + 12]
        return midis

    def _total_motion(prev: list[int], curr: list[int]) -> int:
        n = min(len(prev), len(curr))
        return sum(abs(curr[i] - prev[i]) for i in range(n))

    result = []
    prev_midis = _chord_midis(chords[0], octave)

    for chord in chords:
        base = _chord_midis(chord, octave)
        n_inv = len(base)
        best_motion = float("inf")
        best_midis = base

        for inv in range(n_inv):
            candidate = _inversion_midis(base, inv)
            # Also try one octave up
            for shift in (0, 12):
                shifted = [m + shift for m in candidate]
                motion = _total_motion(prev_midis, shifted)
                if motion < best_motion:
                    best_motion = motion
                    best_midis = shifted

        # Build chord from the best MIDI voicing (as custom offsets)
        root_midi = best_midis[0]
        root_name = NOTE_NAMES[root_midi % 12]
        root_oct = root_midi // 12 - 1
        offsets = [m - root_midi for m in best_midis]

        result.append(
            Chord(
                root=root_name,
                shape=offsets,
                octave=root_oct,
                duration=duration if duration is not None else chord.duration,
                velocity=velocity,
            )
        )
        prev_midis = best_midis

    return result


# ---------------------------------------------------------------------------
# Song.generate — full multi-track generative songs
# ---------------------------------------------------------------------------

_GENRE_TEMPLATES: dict[str, dict] = {
    "lo_fi": {
        "bpm": 80,
        "mood": "chill",
        "mode": "pentatonic",
        "root": "A",
        "instruments": {
            "pad": "pad",
            "lead": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "hat": "drums_hat",
        },
        "volumes": {"pad": 0.35, "lead": 0.55, "bass": 0.55, "kick": 0.6, "hat": 0.2},
    },
    "jazz": {
        "bpm": 130,
        "mood": "groovy",
        "mode": "dorian",
        "root": "D",
        "instruments": {
            "pad": "organ",
            "lead": "piano",
            "bass": "bass",
            "kick": "drums_kick",
            "hat": "drums_hat",
        },
        "volumes": {"pad": 0.3, "lead": 0.5, "bass": 0.55, "kick": 0.6, "hat": 0.25},
    },
    "ambient": {
        "bpm": 70,
        "mood": "dreamy",
        "mode": "major",
        "root": "E",
        "instruments": {"pad": "pad", "lead": "triangle", "bass": "sine"},
        "volumes": {"pad": 0.35, "lead": 0.35, "bass": 0.4},
    },
    "edm": {
        "bpm": 128,
        "mood": "epic",
        "mode": "minor",
        "root": "A",
        "instruments": {
            "pad": "pad",
            "lead": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "hat": "drums_hat",
            "snare": "drums_snare",
        },
        "volumes": {"pad": 0.3, "lead": 0.5, "bass": 0.6, "kick": 0.8, "hat": 0.3, "snare": 0.5},
    },
    "rock": {
        "bpm": 140,
        "mood": "epic",
        "mode": "pentatonic",
        "root": "E",
        "instruments": {
            "pad": "sawtooth",
            "lead": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "hat": "drums_hat",
            "snare": "drums_snare",
        },
        "volumes": {"pad": 0.4, "lead": 0.5, "bass": 0.6, "kick": 0.75, "hat": 0.3, "snare": 0.55},
    },
    "classical": {
        "bpm": 90,
        "mood": "sad",
        "mode": "minor",
        "root": "C",
        "instruments": {"pad": "pad", "lead": "piano", "bass": "bass"},
        "volumes": {"pad": 0.4, "lead": 0.55, "bass": 0.5},
    },
    "funk": {
        "bpm": 108,
        "mood": "groovy",
        "mode": "mixolydian",
        "root": "Bb",
        "instruments": {
            "pad": "pluck",
            "lead": "sawtooth",
            "bass": "bass",
            "kick": "drums_kick",
            "hat": "drums_hat",
            "snare": "drums_snare",
        },
        "volumes": {"pad": 0.4, "lead": 0.45, "bass": 0.6, "kick": 0.75, "hat": 0.3, "snare": 0.5},
    },
    "hip_hop": {
        "bpm": 90,
        "mood": "dark",
        "mode": "pentatonic",
        "root": "C",
        "instruments": {
            "pad": "pad",
            "lead": "piano",
            "bass": "sine",
            "kick": "drums_kick",
            "hat": "drums_hat",
            "snare": "drums_snare",
        },
        "volumes": {"pad": 0.2, "lead": 0.4, "bass": 0.65, "kick": 0.8, "hat": 0.3, "snare": 0.5},
    },
}


def generate_song(
    genre: str = "lo_fi",
    bars: int = 16,
    seed: int | None = None,
    title: str | None = None,
    sample_rate: int = 44100,
) -> Song:
    """Generate a complete multi-track song from a genre template.

    Uses ``generate_melody()``, ``suggest_progression()``, and genre-specific
    drum/bass patterns to assemble a full song with pad, lead, bass, and drums.

    Args:
        genre:       Genre template. Available: lo_fi, jazz, ambient, edm, rock,
                     classical, funk, hip_hop.
        bars:        Number of bars to generate (4/4 time).
        seed:        Random seed for reproducibility (None = random each time).
        title:       Song title (defaults to genre name).
        sample_rate: Audio sample rate.

    Returns:
        A fully populated Song ready to render.

    Example::

        song = generate_song("jazz", bars=16, seed=42)
        play(song)
    """
    import random as _rng

    if genre not in _GENRE_TEMPLATES:
        raise ValueError(f"Unknown genre {genre!r}. Choose: {sorted(_GENRE_TEMPLATES)}")

    tmpl = _GENRE_TEMPLATES[genre]
    rng = _rng.Random(seed)
    bpm = tmpl["bpm"]
    root = tmpl["root"]
    mode = tmpl["mode"]
    mood = tmpl["mood"]

    song = Song(
        title=title or genre.replace("_", " ").title(),
        bpm=bpm,
        sample_rate=sample_rate,
    )

    instruments = tmpl["instruments"]
    volumes = tmpl["volumes"]

    # ── Chords (pad) ──────────────────────────────────────────────────
    if "pad" in instruments:
        pad = song.add_track(
            Track(
                name="pad",
                instrument=instruments["pad"],
                volume=volumes.get("pad", 0.35),
            )
        )
        chords = suggest_progression(
            root, mood=mood, octave=3, duration=4.0, variation=rng.randint(0, 2)
        )
        repeats = max(1, bars // len(chords))
        for _ in range(repeats):
            pad.extend(chords)

    # ── Melody (lead) ─────────────────────────────────────────────────
    if "lead" in instruments:
        lead = song.add_track(
            Track(
                name="lead",
                instrument=instruments["lead"],
                volume=volumes.get("lead", 0.5),
            )
        )
        melody = generate_melody(
            root,
            mode,
            octave=5,
            bars=bars,
            bpm=bpm,
            density=0.5 + rng.random() * 0.3,
            seed=rng.randint(0, 2**31),
        )
        lead.extend(melody)

    # ── Bass ──────────────────────────────────────────────────────────
    if "bass" in instruments:
        bass = song.add_track(
            Track(
                name="bass",
                instrument=instruments["bass"],
                volume=volumes.get("bass", 0.55),
            )
        )
        # Simple root-note bass following chord roots
        chords_for_bass = suggest_progression(
            root, mood=mood, octave=2, duration=4.0, variation=rng.randint(0, 2)
        )
        repeats = max(1, bars // len(chords_for_bass))
        for _ in range(repeats):
            for chord in chords_for_bass:
                # Convert chord root to a bass note pattern
                bass.extend(
                    [
                        Note(chord.root, 2, 1.0),
                        Note(chord.root, 2, 0.5),
                        Note.rest(0.5),
                        Note(chord.root, 2, 1.0),
                        Note.rest(1.0),
                    ]
                )

    # ── Drums ─────────────────────────────────────────────────────────
    if "kick" in instruments:
        kick = song.add_track(
            Track(
                name="kick",
                instrument=instruments["kick"],
                volume=volumes.get("kick", 0.7),
            )
        )
        for _ in range(bars):
            kick.extend([Note("C", 2, 1.0)] * 4)

    if "snare" in instruments:
        snare = song.add_track(
            Track(
                name="snare",
                instrument=instruments["snare"],
                volume=volumes.get("snare", 0.5),
            )
        )
        for _ in range(bars):
            snare.extend([Note.rest(1.0), Note("E", 4, 1.0), Note.rest(1.0), Note("E", 4, 1.0)])

    if "hat" in instruments:
        hat = song.add_track(
            Track(
                name="hat",
                instrument=instruments["hat"],
                volume=volumes.get("hat", 0.25),
            )
        )
        for _ in range(bars):
            hat.extend([Note("F#", 6, 0.5)] * 8)

    return song


# ---------------------------------------------------------------------------
# detect_key — analyze a Song to determine its likely key
# ---------------------------------------------------------------------------

_KEY_PROFILES: dict[str, list[float]] = {
    # Krumhansl-Kessler key profiles (normalized)
    "major": [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    "minor": [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
}


def detect_key(song: Song) -> tuple[str, str, float]:
    """Analyze a Song and return its most likely key.

    Uses the Krumhansl-Kessler pitch-class profile correlation algorithm:
    counts how often each pitch class appears (weighted by duration), then
    correlates against major and minor key profiles for all 12 roots.

    Args:
        song: A Song with at least one track containing pitched notes.

    Returns:
        (root, mode, confidence) — e.g. ``('A', 'minor', 0.87)``

    Example::

        root, mode, conf = detect_key(song)
        print(f"Detected: {root} {mode} ({conf:.0%} confidence)")
    """
    import numpy as _np

    # Count pitch-class durations
    pc_counts = _np.zeros(12)
    for track in song.tracks:
        for beat in track.beats:
            if beat.event is None:
                continue
            event = beat.event
            if isinstance(event, Note) and event.pitch is not None:
                try:
                    midi = note_name_to_midi(str(event.pitch), event.octave)
                    pc = midi % 12
                    pc_counts[pc] += event.duration
                except (ValueError, TypeError):
                    continue
            elif isinstance(event, Chord):
                try:
                    midi = note_name_to_midi(str(event.root), event.octave)
                    pc = midi % 12
                    pc_counts[pc] += event.duration * 2  # chords weight more
                except (ValueError, TypeError):
                    continue

    if pc_counts.sum() == 0:
        return ("C", "major", 0.0)

    # Correlate against all 24 key profiles (12 major + 12 minor)
    best_root = "C"
    best_mode = "major"
    best_corr = -1.0

    for mode_name, profile in _KEY_PROFILES.items():
        profile_arr = _np.array(profile)
        for shift in range(12):
            rotated = _np.roll(pc_counts, -shift)
            corr = _np.corrcoef(rotated, profile_arr)[0, 1]
            if corr > best_corr:
                best_corr = corr
                best_root = NOTE_NAMES[shift]
                best_mode = mode_name

    return (best_root, best_mode, max(0.0, float(best_corr)))
