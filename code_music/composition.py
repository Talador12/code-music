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
    bar_width = 16

    for bar_start in range(0, total_bars, 4):
        chord_line = "|"
        melody_line = "|"
        bars_this_line = min(4, total_bars - bar_start)
        for b in range(bars_this_line):
            bar_beat = (bar_start + b) * beats_per_bar
            bar_end = bar_beat + beats_per_bar
            bar_chords = [c for pos, c in chord_events if bar_beat <= pos < bar_end]
            chord_str = " ".join(bar_chords) if bar_chords else ""
            chord_line += f" {chord_str:<{bar_width - 1}}|"
            bar_notes = [n for pos, n in melody_events if bar_beat <= pos < bar_end]
            note_str = " ".join(bar_notes[:beats_per_bar]) if bar_notes else ""
            melody_line += f" {note_str:<{bar_width - 1}}|"
        lines.append(chord_line)
        lines.append(melody_line)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ASCII guitar/bass tablature
# ---------------------------------------------------------------------------

# Standard guitar tuning (low to high): E2 A2 D3 G3 B3 E4
_GUITAR_TUNING = [("E", 2), ("A", 2), ("D", 3), ("G", 3), ("B", 3), ("E", 4)]
# Standard bass tuning: E1 A1 D2 G2
_BASS_TUNING = [("E", 1), ("A", 1), ("D", 2), ("G", 2)]

_SEMI_MAP = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}


def _note_to_midi(pitch: str, octave: int) -> int:
    return _SEMI_MAP.get(pitch, 0) + (octave + 1) * 12


def _find_fret(pitch: str, octave: int, string_pitch: str, string_octave: int) -> int | None:
    """Find the fret number for a note on a given string, or None if out of range."""
    note_midi = _note_to_midi(pitch, octave)
    string_midi = _note_to_midi(string_pitch, string_octave)
    fret = note_midi - string_midi
    if 0 <= fret <= 24:
        return fret
    return None


def to_tab(
    song: Song,
    tuning: str = "guitar",
    track_name: str | None = None,
    beats_per_bar: int = 4,
) -> str:
    """Render a song track as ASCII tablature.

    Args:
        song:          Song to render.
        tuning:        'guitar' (6-string) or 'bass' (4-string).
        track_name:    Name of the track to tab. If None, uses first melodic track.
        beats_per_bar: Beats per bar.

    Returns:
        Multi-line ASCII tablature string.

    Example output::

        TAB: My Song (Guitar, 120 BPM)
        e|---0---3---5---7---|
        B|-------------------|
        G|-------------------|
        D|-------------------|
        A|-------------------|
        E|-------------------|
    """
    strings = _GUITAR_TUNING if tuning == "guitar" else _BASS_TUNING
    string_names = [f"{p}" for p, _ in reversed(strings)]

    # Find the target track
    target = None
    if track_name:
        for t in song.tracks:
            if t.name == track_name:
                target = t
                break
    if target is None:
        for t in song.tracks:
            for b in t.beats:
                if b.event and isinstance(b.event, Note) and b.event.pitch is not None:
                    target = t
                    break
            if target:
                break

    lines = []
    tuning_label = tuning.capitalize()
    lines.append(f"TAB: {song.title} ({tuning_label}, {song.bpm:.0f} BPM)")
    lines.append("")

    if target is None:
        lines.append("(no melodic track found)")
        return "\n".join(lines)

    # Collect notes with positions
    events: list[tuple[float, str, int]] = []
    pos = 0.0
    for beat in target.beats:
        if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None:
            events.append((pos, str(beat.event.pitch), beat.event.octave))
        if beat.event:
            pos += beat.event.duration

    total_beats = pos
    total_bars = max(1, int(total_beats / beats_per_bar))

    # Render bars (4 bars per line)
    for bar_start in range(0, total_bars, 4):
        bars_this_line = min(4, total_bars - bar_start)
        # Initialize string lines
        tab_lines = {name: "" for name in string_names}
        for b in range(bars_this_line):
            bar_beat = (bar_start + b) * beats_per_bar
            bar_end = bar_beat + beats_per_bar

            # Find notes in this bar
            bar_events = [
                (p - bar_beat, pitch, oct) for p, pitch, oct in events if bar_beat <= p < bar_end
            ]

            for name_idx, name in enumerate(string_names):
                string_p, string_o = list(reversed(strings))[name_idx]
                bar_str = ""
                for beat_pos in range(beats_per_bar):
                    # Check if there's a note at this beat position
                    fret_str = "---"
                    for ev_pos, ev_pitch, ev_oct in bar_events:
                        if abs(ev_pos - beat_pos) < 0.1:
                            fret = _find_fret(ev_pitch, ev_oct, string_p, string_o)
                            if fret is not None:
                                fret_str = f"-{fret}-" if fret < 10 else f"{fret}-"
                                break
                    bar_str += fret_str + "-"
                tab_lines[name] += "|" + bar_str

        for name in string_names:
            tab_lines[name] += "|"
            lines.append(f"{name}|{tab_lines[name]}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ASCII structure map
# ---------------------------------------------------------------------------


def song_map(song: Song, beats_per_bar: int = 4) -> str:
    """Render an ASCII map of a song's structure.

    Shows each track as a row, each bar as a column, with density indicators
    for how many notes/chords are in each bar.

    Args:
        song:          Song to visualize.
        beats_per_bar: Beats per bar.

    Returns:
        Multi-line ASCII string.

    Example output::

        Song Map: My Song (120 BPM, 8 bars)
        ──────────────────────────────────────
        Track     | 1    | 2    | 3    | 4    |
        ──────────┼──────┼──────┼──────┼──────┤
        kick      | ████ | ████ | ████ | ████ |
        pad       | ▓▓▓▓ |      | ▓▓▓▓ |      |
        lead      | ░░░░ | ░░░░ | ░░░░ | ░░░░ |
    """
    # Calculate total bars
    total_beats = 0.0
    for track in song.tracks:
        track_dur = sum(b.event.duration if b.event else 0 for b in track.beats)
        total_beats = max(total_beats, track_dur)

    total_bars = max(1, int(total_beats / beats_per_bar))

    lines = []
    lines.append(f"Song Map: {song.title} ({song.bpm:.0f} BPM, {total_bars} bars)")
    lines.append("─" * (12 + total_bars * 7))

    # Header
    header = f"{'Track':<10} |"
    for b in range(min(total_bars, 16)):  # max 16 bars per line
        header += f" {b + 1:<4}|"
    lines.append(header)
    lines.append("─" * len(header))

    # Density chars
    DENSITY = {0: "     ", 1: " ░   ", 2: " ▒   ", 3: " ▓   ", 4: " ████"}

    for track in song.tracks:
        row = f"{track.name[:10]:<10} |"
        pos = 0.0
        bar_counts: dict[int, int] = {}
        for beat in track.beats:
            if beat.event:
                bar_idx = int(pos / beats_per_bar)
                if beat.event.pitch is not None if isinstance(beat.event, Note) else True:
                    bar_counts[bar_idx] = bar_counts.get(bar_idx, 0) + 1
                pos += beat.event.duration

        for b in range(min(total_bars, 16)):
            count = bar_counts.get(b, 0)
            density = min(count, 4)
            row += DENSITY[density] + "|"
        lines.append(row)

    return "\n".join(lines)
