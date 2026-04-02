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
    density: float = 1.0  # 0.0–1.0 probability each note plays (1.0 = all notes)
    density_seed: int | None = None  # random seed for reproducible dropout

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

    def export_stems(self, out_dir: str, fmt: str = "wav") -> list:
        """Render each track as a separate audio file (stem export).

        Creates one file per track, named ``<track_name>.<fmt>``.
        Useful for mixing in a DAW, sharing individual parts, or remix work.

        Args:
            out_dir: Output directory (created if missing).
            fmt:     Audio format — "wav" (default), "flac", or "mp3".

        Returns:
            List of Path objects for the written files.

        Example::

            song.export_stems("dist/stems/my_song/")
            # → dist/stems/my_song/kick.wav, bass.wav, lead.wav, ...
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

            safe_name = track.name.replace(" ", "_").replace("/", "_")
            path = out / f"{safe_name}.{fmt}"
            if fmt == "flac":
                export_flac(stereo, path, self.sample_rate)
            elif fmt == "mp3":
                export_mp3(stereo, path, self.sample_rate)
            else:
                export_wav(stereo, path, self.sample_rate)
            results.append(path)

        return results

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
