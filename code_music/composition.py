"""Advanced composition tools — melody continuation, structure, lead sheets.

Melody continuation via Markov chains, named section types (Verse/Chorus/Bridge),
and ASCII lead sheet rendering.

Example::

    from code_music.composition import continue_melody, Verse, Chorus, to_lead_sheet

    # Continue a melody
    seed = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
    extended = continue_melody(seed, bars=4, key="C", mode="major", seed_rng=42)

    # Named sections
    v = Verse(bars=8)
    c = Chorus(bars=8)

    # ASCII lead sheet
    print(to_lead_sheet(song))
"""

from __future__ import annotations

import random

from .engine import Chord, Note, Section, Song

# ---------------------------------------------------------------------------
# Note constants
# ---------------------------------------------------------------------------

_NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_NOTE_TO_SEMI = {n: i for i, n in enumerate(_NOTE_NAMES)}
_NOTE_TO_SEMI.update({"Db": 1, "D#": 3, "Gb": 6, "G#": 8, "A#": 10})

_SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
}


# ---------------------------------------------------------------------------
# Melody continuation (Markov chain)
# ---------------------------------------------------------------------------


def _build_transitions(notes: list[Note], order: int = 1) -> dict:
    """Build a Markov transition table from a note sequence."""
    transitions: dict[tuple, list[tuple]] = {}
    pitched = [(n.pitch, n.octave) for n in notes if n.pitch is not None]
    if len(pitched) < order + 1:
        return transitions
    for i in range(len(pitched) - order):
        state = tuple(pitched[i : i + order])
        next_note = pitched[i + order]
        transitions.setdefault(state, []).append(next_note)
    return transitions


def continue_melody(
    seed_notes: list[Note],
    bars: int = 4,
    key: str = "C",
    mode: str = "major",
    duration: float = 0.5,
    octave: int = 5,
    order: int = 1,
    seed_rng: int | None = None,
) -> list[Note]:
    """Continue a melody using Markov chain transitions.

    If the seed is long enough, learns transition probabilities from it.
    Falls back to scale-based random walk when transitions are exhausted.

    Args:
        seed_notes: Starting melody fragment (used to learn transitions).
        bars:       Number of bars to generate.
        key:        Key root note.
        mode:       Scale mode (major, minor, dorian, pentatonic, etc).
        duration:   Duration per generated note.
        octave:     Default octave for generated notes.
        order:      Markov chain order (1 or 2).
        seed_rng:   Random seed for reproducibility.

    Returns:
        List of Notes (seed_notes + generated continuation).
    """
    rng = random.Random(seed_rng)
    beats_per_bar = int(4 / duration)
    total_notes = beats_per_bar * bars

    # Build transition table from seed
    transitions = _build_transitions(seed_notes, order)

    # Get scale notes for fallback
    root_semi = _NOTE_TO_SEMI.get(key, 0)
    intervals = _SCALE_INTERVALS.get(mode, _SCALE_INTERVALS["major"])
    scale_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in intervals]

    # Start from last notes in seed
    pitched = [(n.pitch, n.octave) for n in seed_notes if n.pitch is not None]
    result = list(seed_notes)

    for _ in range(total_notes):
        # Try Markov transition
        generated = False
        if len(pitched) >= order and transitions:
            state = tuple(pitched[-order:])
            if state in transitions:
                pitch, oct = rng.choice(transitions[state])
                result.append(Note(pitch, oct, duration))
                pitched.append((pitch, oct))
                generated = True

        if not generated:
            # Fallback: random walk within scale
            if pitched:
                last_pitch, last_oct = pitched[-1]
                # Find current position in scale
                last_semi = _NOTE_TO_SEMI.get(last_pitch, 0)
                # Step up or down by 1-2 scale degrees
                step = rng.choice([-2, -1, 1, 2])
                scale_idx = 0
                for i, n in enumerate(scale_notes):
                    if _NOTE_TO_SEMI[n] == last_semi % 12:
                        scale_idx = i
                        break
                new_idx = (scale_idx + step) % len(scale_notes)
                new_pitch = scale_notes[new_idx]
                # Handle octave crossings
                new_oct = last_oct
                if step > 0 and new_idx < scale_idx:
                    new_oct += 1
                elif step < 0 and new_idx > scale_idx:
                    new_oct -= 1
                new_oct = max(3, min(7, new_oct))
            else:
                new_pitch = rng.choice(scale_notes)
                new_oct = octave

            result.append(Note(new_pitch, new_oct, duration))
            pitched.append((new_pitch, new_oct))

    return result


# ---------------------------------------------------------------------------
# Named section types
# ---------------------------------------------------------------------------


class Verse(Section):
    """A verse section — typically carries the narrative."""

    def __init__(self, bars: int = 8, **kwargs):
        super().__init__(name="verse", bars=bars, **kwargs)


class Chorus(Section):
    """A chorus section — the hook, typically louder and more energetic."""

    def __init__(self, bars: int = 8, **kwargs):
        super().__init__(name="chorus", bars=bars, **kwargs)


class Bridge(Section):
    """A bridge section — contrast before the final chorus."""

    def __init__(self, bars: int = 4, **kwargs):
        super().__init__(name="bridge", bars=bars, **kwargs)


class Intro(Section):
    """An intro section — sets the mood before the first verse."""

    def __init__(self, bars: int = 4, **kwargs):
        super().__init__(name="intro", bars=bars, **kwargs)


class Outro(Section):
    """An outro section — wraps up the song."""

    def __init__(self, bars: int = 4, **kwargs):
        super().__init__(name="outro", bars=bars, **kwargs)


# ---------------------------------------------------------------------------
# ASCII lead sheet
# ---------------------------------------------------------------------------


def to_lead_sheet(song: Song, beats_per_bar: int = 4) -> str:
    """Render a song as an ASCII lead sheet.

    Shows chord symbols above and melody note names below,
    organized by bar with bar lines.

    Args:
        song:          Song to render.
        beats_per_bar: Beats per bar (default 4 for 4/4).

    Returns:
        Multi-line ASCII string.

    Example output::

        Lead Sheet: My Song (120 BPM, C)
        ────────────────────────────────
        | Cmin7          | Gmaj7          |
        | C  Eb G  Bb    | G  B  D  F#    |
    """
    lines = []
    lines.append(f"Lead Sheet: {song.title} ({song.bpm:.0f} BPM, {song.key_sig})")
    lines.append("─" * 60)

    # Find chord track and melody track
    chord_track = None
    melody_track = None
    for track in song.tracks:
        for beat in track.beats:
            if beat.event is None:
                continue
            if isinstance(beat.event, Chord) and chord_track is None:
                chord_track = track
                break
            elif (
                isinstance(beat.event, Note)
                and beat.event.pitch is not None
                and melody_track is None
            ):
                melody_track = track
                break

    if chord_track is None and melody_track is None:
        lines.append("(empty song)")
        return "\n".join(lines)

    # Extract chords as (beat_position, chord_string)
    chord_events: list[tuple[float, str]] = []
    if chord_track:
        pos = 0.0
        for beat in chord_track.beats:
            if beat.event and isinstance(beat.event, Chord):
                shape_str = beat.event.shape if isinstance(beat.event.shape, str) else "?"
                chord_events.append((pos, f"{beat.event.root}{shape_str}"))
                pos += beat.event.duration
            elif beat.event:
                pos += beat.event.duration

    # Extract melody notes
    melody_events: list[tuple[float, str]] = []
    if melody_track:
        pos = 0.0
        for beat in melody_track.beats:
            if beat.event:
                if isinstance(beat.event, Note) and beat.event.pitch is not None:
                    melody_events.append((pos, str(beat.event.pitch)))
                pos += beat.event.duration

    # Calculate total duration
    total_beats = 0.0
    for track in song.tracks:
        track_dur = sum(b.event.duration if b.event else 0 for b in track.beats)
        total_beats = max(total_beats, track_dur)

    total_bars = max(1, int(total_beats / beats_per_bar))
    bar_width = 16  # characters per bar

    # Render bars
    for bar_start in range(0, total_bars, 4):  # 4 bars per line
        chord_line = "|"
        melody_line = "|"
        bars_this_line = min(4, total_bars - bar_start)

        for b in range(bars_this_line):
            bar_beat = (bar_start + b) * beats_per_bar
            bar_end = bar_beat + beats_per_bar

            # Chords in this bar
            bar_chords = [c for pos, c in chord_events if bar_beat <= pos < bar_end]
            chord_str = " ".join(bar_chords) if bar_chords else ""
            chord_line += f" {chord_str:<{bar_width - 1}}|"

            # Melody in this bar
            bar_notes = [n for pos, n in melody_events if bar_beat <= pos < bar_end]
            note_str = " ".join(bar_notes[:beats_per_bar]) if bar_notes else ""
            melody_line += f" {note_str:<{bar_width - 1}}|"

        lines.append(chord_line)
        lines.append(melody_line)
        lines.append("")

    return "\n".join(lines)
