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


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

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
    }
)


def midi_to_freq(midi: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return A4_FREQ * (2.0 ** ((midi - A4_MIDI) / 12.0))


def note_name_to_midi(name: str, octave: int = 4) -> int:
    """Convert e.g. 'C#' + octave 4 to MIDI note number."""
    name = name.upper().replace("B#", "C").replace("CB", "B").replace("FB", "E").replace("E#", "F")
    # Handle flats
    name = (
        name.replace("DB", "C#")
        .replace("EB", "D#")
        .replace("GB", "F#")
        .replace("AB", "G#")
        .replace("BB", "A#")
    )
    if name not in NOTE_NAMES:
        raise ValueError(f"Unknown note name: {name!r}")
    semitone = NOTE_NAMES.index(name)
    return (octave + 1) * 12 + semitone


@dataclass
class Note:
    """A single pitched note with duration and velocity.

    Attributes:
        pitch: Note name (e.g. 'A', 'C#') or MIDI number or None for rest.
        octave: Octave number (4 = middle octave, A4 = 440 Hz).
        duration: Duration in beats (1.0 = quarter note at current BPM).
        velocity: 0.0–1.0 volume/intensity.
    """

    pitch: str | int | None  # name, MIDI int, or None for rest
    octave: int = 4
    duration: float = 1.0  # beats
    velocity: float = 0.8

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
    """Shorten note durations to create staccato articulation.

    Each note's sounding duration is shortened to `factor` of its original,
    with the remaining time becoming silence (rest). This creates the detached,
    clipped feel of staccato playing.

    Args:
        notes:  List of Notes to articulate.
        factor: 0.0–1.0 — fraction of note duration that sounds (0.5 = half).
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
            continue
        sound_dur = max(0.05, n.duration * factor)
        rest_dur = n.duration - sound_dur
        result.append(Note(pitch=n.pitch, octave=n.octave, duration=sound_dur, velocity=n.velocity))
        if rest_dur > 0.01:
            result.append(Note.rest(rest_dur))
    return result


def legato(notes: list[Note], overlap: float = 0.1) -> list[Note]:
    """Extend note durations slightly for legato (slurred) articulation.

    Each note is lengthened by `overlap` beats so it slightly overlaps the next.
    This creates the connected, smooth feel of legato playing.

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
                )
            )
    return result


def pizzicato(notes: list[Note]) -> list[Note]:
    """Convert notes to pizzicato articulation: very short, plucked feel.

    Equivalent to staccato(notes, factor=0.15).
    """
    return staccato(notes, factor=0.15)


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
    note: Note, semitones: int = 2, steps: int = 4, speed: float = THIRTY_SECOND
) -> list[Note]:
    """Jazz doit: note bends upward after the attack.

    Common in jazz brass. The pitch rises through chromatic steps after
    the initial attack.

    Example::

        tr.extend(doit(Note('Bb', 4, QUARTER)))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = [Note(pitch=base, duration=main_dur, velocity=note.velocity)]
    for i in range(1, steps + 1):
        result.append(
            Note(
                pitch=base + round(semitones * i / steps),
                duration=speed,
                velocity=note.velocity * max(0.2, 1.0 - i / steps),
            )
        )
    return result


def fall(
    note: Note, semitones: int = 3, steps: int = 4, speed: float = THIRTY_SECOND
) -> list[Note]:
    """Jazz fall: note bends downward after the attack.

    Opposite of doit — the pitch drops after the initial attack.

    Example::

        tr.extend(fall(Note('G', 5, QUARTER)))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * steps)
    result = [Note(pitch=base, duration=main_dur, velocity=note.velocity)]
    for i in range(1, steps + 1):
        result.append(
            Note(
                pitch=base - round(semitones * i / steps),
                duration=speed,
                velocity=note.velocity * max(0.2, 1.0 - i / steps),
            )
        )
    return result


def flip(note: Note, semitones: int = 2, speed: float = THIRTY_SECOND) -> list[Note]:
    """Jazz flip: quick upward scoop into the note from below.

    Example::

        tr.extend(flip(Note('D', 5, QUARTER)))
    """
    if note.pitch is None:
        return [Note.rest(note.duration)]
    base = note.midi or 0
    main_dur = max(SIXTY_FOURTH, note.duration - speed * 2)
    return [
        Note(pitch=base - semitones, duration=speed, velocity=note.velocity * 0.7),
        Note(pitch=base - 1, duration=speed, velocity=note.velocity * 0.85),
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

    def add(self, event: Note | Chord | None) -> "Track":
        """Append a note, chord, or rest beat. Returns self for chaining."""
        self.beats.append(Beat(event=event))
        return self

    def extend(self, events: Sequence[Note | Chord | None]) -> "Track":
        for e in events:
            self.add(e)
        return self

    @property
    def total_beats(self) -> float:
        return sum(b.duration for b in self.beats)


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
    time_sig: tuple[int, int] = (4, 4)
    composer: str = ""
    key_sig: str = "C"

    def add_track(self, track: Track) -> "Track":
        self.tracks.append(track)
        return track

    def add_polytrack(self, track) -> object:  # track: PolyphonicTrack
        """Add a PolyphonicTrack. Returns the track."""
        self.poly_tracks.append(track)
        return track

    def add_voice_track(self, track) -> object:  # track: VoiceTrack
        """Add a VoiceTrack to the song. Returns the track."""
        track.sample_rate = self.sample_rate
        self.voice_tracks.append(track)
        return track

    @property
    def beat_duration_sec(self) -> float:
        return 60.0 / self.bpm

    @property
    def total_beats(self) -> float:
        seq_beats = max((t.total_beats for t in self.tracks), default=0.0)
        poly_beats = max((t.total_beats for t in self.poly_tracks), default=0.0)
        return max(seq_beats, poly_beats)

    @property
    def duration_sec(self) -> float:
        return self.total_beats * self.beat_duration_sec


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
    new_song._effects = copy.copy(getattr(song, "_effects", {}))

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
    or rubato (free tempo). The returned list can be used with a custom
    render loop, or passed to the `bpm_map` field on a Song.

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
        # Then use with render_with_bpm_map(song, ramp)
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
