"""Core music primitives: Note, Chord, Beat, Track, Song."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

# Equal-temperament MIDI note number -> frequency (A4 = 440 Hz)
A4_FREQ = 440.0
A4_MIDI = 69

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
}

# Scale patterns (semitone steps)
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues": [0, 3, 5, 6, 7, 10],
    "chromatic": list(range(12)),
}


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


def scale(root: str, mode: str = "major", octave: int = 4, length: int | None = None) -> list[Note]:
    """Return scale as a list of Notes.

    Args:
        root: Root note name.
        mode: Scale mode key from SCALES.
        octave: Starting octave.
        length: How many notes to return; wraps to next octave if needed.
    """
    intervals = SCALES[mode]
    root_midi = note_name_to_midi(root, octave)
    notes = []
    target = length if length is not None else len(intervals)
    for i in range(target):
        idx = i % len(intervals)
        extra_octave = i // len(intervals)
        notes.append(Note(pitch=root_midi + intervals[idx] + extra_octave * 12))
    return notes


@dataclass
class Track:
    """A sequence of Beats with instrument/synth metadata.

    Attributes:
        name: Human-readable label.
        beats: Ordered sequence of Beat objects.
        instrument: Synth preset name (e.g. 'sine', 'square', 'sawtooth', 'piano').
        volume: Track-level gain 0.0–1.0.
    """

    name: str = "track"
    beats: list[Beat] = field(default_factory=list)
    instrument: str = "sine"
    volume: float = 0.8

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
    """Container for multiple Tracks and global tempo/metadata.

    Attributes:
        title: Song title used in exported filename.
        bpm: Beats per minute.
        sample_rate: Audio sample rate (44100 for CD quality).
        tracks: List of Track objects mixed together on export.
    """

    title: str = "untitled"
    bpm: float = 120.0
    sample_rate: int = 44100
    tracks: list[Track] = field(default_factory=list)

    def add_track(self, track: Track) -> "Track":
        self.tracks.append(track)
        return track

    @property
    def beat_duration_sec(self) -> float:
        return 60.0 / self.bpm

    @property
    def total_beats(self) -> float:
        return max((t.total_beats for t in self.tracks), default=0.0)

    @property
    def duration_sec(self) -> float:
        return self.total_beats * self.beat_duration_sec
