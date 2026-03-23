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

    Equivalent to staccato(notes, factor=0.15) — makes each note extremely short.
    Use on string instrument tracks for a plucked character without changing
    the instrument preset.
    """
    return staccato(notes, factor=0.15)


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

    def add_track(self, track: Track) -> "Track":
        self.tracks.append(track)
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
        return max((t.total_beats for t in self.tracks), default=0.0)

    @property
    def duration_sec(self) -> float:
        return self.total_beats * self.beat_duration_sec
