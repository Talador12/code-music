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

from .engine import Chord, Note, Section, Song, Track

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

    melody_events: list[tuple[float, str]] = []
    if melody_track:
        pos = 0.0
        for beat in melody_track.beats:
            if beat.event:
                if isinstance(beat.event, Note) and beat.event.pitch is not None:
                    melody_events.append((pos, str(beat.event.pitch)))
                pos += beat.event.duration

    total_beats = max(sum(b.event.duration if b.event else 0 for b in t.beats) for t in song.tracks)
    total_bars = max(1, int(total_beats / beats_per_bar))
    bar_width = 16
    for bar_start in range(0, total_bars, 4):
        cl = "|"
        ml = "|"
        for b in range(min(4, total_bars - bar_start)):
            bb = (bar_start + b) * beats_per_bar
            be = bb + beats_per_bar
            bc = [c for p, c in chord_events if bb <= p < be]
            cl += f" {' '.join(bc) if bc else '':<{bar_width - 1}}|"
            bn = [n for p, n in melody_events if bb <= p < be]
            ml += f" {' '.join(bn[:beats_per_bar]) if bn else '':<{bar_width - 1}}|"
        lines.append(cl)
        lines.append(ml)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fast preview render
# ---------------------------------------------------------------------------


def render_preview(song: Song):
    """Render a fast low-quality preview of a song.

    Creates a temporary copy at 11025Hz mono for quick iteration.
    ~4x faster than full 44100Hz stereo render.

    Args:
        song: Song to preview.

    Returns:
        Mono float64 numpy array at 11025Hz.
    """
    import numpy as np

    original_sr = song.sample_rate
    song.sample_rate = 11025
    try:
        audio = song.render()
    finally:
        song.sample_rate = original_sr

    if audio.ndim > 1:
        return np.mean(audio, axis=1)
    return audio


# ---------------------------------------------------------------------------
# Quantize track
# ---------------------------------------------------------------------------


def quantize_track(
    notes: list[Note],
    grid: float = 0.5,
) -> list[Note]:
    """Snap note durations to the nearest grid value.

    Useful for cleaning up humanized or recorded input.

    Args:
        notes: List of Notes to quantize.
        grid:  Grid size in beats (0.25 = 16th, 0.5 = 8th, 1.0 = quarter).

    Returns:
        New list of Notes with quantized durations.
    """
    result: list[Note] = []
    for note in notes:
        snapped = max(grid, round(note.duration / grid) * grid)
        if note.pitch is None:
            result.append(Note.rest(snapped))
        else:
            result.append(Note(str(note.pitch), note.octave, snapped, velocity=note.velocity))
    return result


# ---------------------------------------------------------------------------
# Song summary
# ---------------------------------------------------------------------------


def song_summary(song: Song) -> str:
    """Generate a pretty-printed ASCII summary of a song.

    Includes title, BPM, duration, key signature, track list with
    instrument/volume/pan, and total beat count.

    Args:
        song: Song to summarize.

    Returns:
        Multi-line ASCII string.

    Example output::

        ╔══════════════════════════════════════╗
        ║  My Song                             ║
        ╠══════════════════════════════════════╣
        ║  BPM: 120    Key: C    Time: 4/4    ║
        ║  Duration: 32.0 beats (16.0 sec)    ║
        ║  Tracks: 3                           ║
        ╠══════════════════════════════════════╣
        ║  kick   drums_kick   vol=0.8  pan=0 ║
        ║  pad    pad          vol=0.4  pan=-0 ║
        ║  lead   piano        vol=0.5  pan=0  ║
        ╚══════════════════════════════════════╝
    """
    width = 42
    lines = []
    lines.append("╔" + "═" * width + "╗")
    lines.append(f"║  {song.title:<{width - 2}}║")
    lines.append("╠" + "═" * width + "╣")

    # Metadata line
    ts = f"{song.time_sig[0]}/{song.time_sig[1]}"
    meta = f"  BPM: {song.bpm:.0f}    Key: {song.key_sig}    Time: {ts}"
    lines.append(f"║{meta:<{width}}║")

    # Duration
    total_beats = song.total_beats
    dur_sec = song.duration_sec
    dur_line = f"  Duration: {total_beats:.1f} beats ({dur_sec:.1f} sec)"
    lines.append(f"║{dur_line:<{width}}║")

    # Track count
    track_line = f"  Tracks: {len(song.tracks)}"
    if song._custom_instruments:
        track_line += f"  Custom instruments: {len(song._custom_instruments)}"
    lines.append(f"║{track_line:<{width}}║")

    lines.append("╠" + "═" * width + "╣")

    # Track details
    for track in song.tracks:
        beats = len(track.beats)
        name = track.name[:8]
        inst = track.instrument[:12]
        tr_line = f"  {name:<8} {inst:<12} v={track.volume:.1f} p={track.pan:+.1f} [{beats}]"
        if len(tr_line) > width:
            tr_line = tr_line[:width]
        lines.append(f"║{tr_line:<{width}}║")

    lines.append("╚" + "═" * width + "╝")
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


# ---------------------------------------------------------------------------
# ABC notation export
# ---------------------------------------------------------------------------

_PITCH_TO_ABC = {
    "C": "C",
    "C#": "^C",
    "Db": "_D",
    "D": "D",
    "D#": "^D",
    "Eb": "_E",
    "E": "E",
    "F": "F",
    "F#": "^F",
    "Gb": "_G",
    "G": "G",
    "G#": "^G",
    "Ab": "_A",
    "A": "A",
    "A#": "^A",
    "Bb": "_B",
    "B": "B",
}


def _note_to_abc(pitch: str, octave: int, duration: float) -> str:
    """Convert a note to ABC notation."""
    abc = _PITCH_TO_ABC.get(pitch, pitch)
    if octave >= 5:
        abc = abc[0].lower() + abc[1:] if len(abc) > 1 else abc.lower()
        if octave >= 6:
            abc += "'" * (octave - 5)
    elif octave <= 3:
        abc += "," * (4 - octave)
    if duration == 0.5:
        abc += "/2"
    elif duration == 2.0:
        abc += "2"
    elif duration == 4.0:
        abc += "4"
    elif duration != 1.0 and duration == int(duration):
        abc += str(int(duration))
    return abc


def to_abc(song: Song, track_name: str | None = None) -> str:
    """Export a song track as ABC notation.

    Args:
        song:       Song to export.
        track_name: Track to export. If None, uses first melodic track.

    Returns:
        ABC notation string (parseable by abc2midi, EasyABC, etc).
    """
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

    lines = [
        "X:1",
        f"T:{song.title}",
        f"M:{song.time_sig[0]}/{song.time_sig[1]}",
        "L:1/4",
        f"Q:{song.bpm:.0f}",
        f"K:{song.key_sig}",
    ]

    if target is None:
        lines.append("z4|")
        return "\n".join(lines)

    bar_beats = 0.0
    beats_per_bar = song.time_sig[0]
    abc_line = ""
    for beat in target.beats:
        if beat.event is None:
            continue
        if isinstance(beat.event, Note):
            if beat.event.pitch is None:
                abc_line += "z"
                if beat.event.duration == 2.0:
                    abc_line += "2"
                elif beat.event.duration == 0.5:
                    abc_line += "/2"
            else:
                abc_line += _note_to_abc(
                    str(beat.event.pitch), beat.event.octave, beat.event.duration
                )
            bar_beats += beat.event.duration
        if bar_beats >= beats_per_bar:
            abc_line += "|"
            bar_beats = 0.0

    if not abc_line.endswith("|"):
        abc_line += "|"
    lines.append(abc_line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Arrangement detection
# ---------------------------------------------------------------------------


def generate_arrangement(song: Song, beats_per_bar: int = 4) -> list[dict]:
    """Auto-detect song structure by analyzing density changes.

    Args:
        song:          Song to analyze.
        beats_per_bar: Beats per bar.

    Returns:
        List of dicts: {start_bar, end_bar, label, tracks_active}.
    """
    total_beats = 0.0
    for track in song.tracks:
        track_dur = sum(b.event.duration if b.event else 0 for b in track.beats)
        total_beats = max(total_beats, track_dur)
    total_bars = max(1, int(total_beats / beats_per_bar))

    bar_density: dict[str, list[int]] = {}
    for track in song.tracks:
        counts = [0] * total_bars
        pos = 0.0
        for beat in track.beats:
            if beat.event:
                bar_idx = min(int(pos / beats_per_bar), total_bars - 1)
                if isinstance(beat.event, Note) and beat.event.pitch is not None:
                    counts[bar_idx] += 1
                elif isinstance(beat.event, Chord):
                    counts[bar_idx] += 1
                pos += beat.event.duration
        bar_density[track.name] = counts

    sections: list[dict] = []
    prev_active = -1
    section_start = 0
    for bar in range(total_bars):
        active = sum(1 for n in bar_density if bar_density[n][bar] > 0)
        if active != prev_active and bar > 0:
            pos_ratio = section_start / max(total_bars, 1)
            density_ratio = prev_active / max(len(bar_density), 1)
            label = _label_section(pos_ratio, density_ratio)
            active_tracks = [n for n in bar_density if any(bar_density[n][section_start:bar])]
            sections.append(
                {
                    "start_bar": section_start,
                    "end_bar": bar,
                    "label": label,
                    "tracks_active": active_tracks,
                }
            )
            section_start = bar
        prev_active = active

    if section_start < total_bars:
        pos_ratio = section_start / max(total_bars, 1)
        density_ratio = prev_active / max(len(bar_density), 1)
        label = _label_section(pos_ratio, density_ratio)
        active_tracks = [n for n in bar_density if any(bar_density[n][section_start:total_bars])]
        sections.append(
            {
                "start_bar": section_start,
                "end_bar": total_bars,
                "label": label,
                "tracks_active": active_tracks,
            }
        )

    return sections


def _label_section(pos_ratio: float, density_ratio: float) -> str:
    if pos_ratio < 0.1:
        return "intro"
    elif pos_ratio > 0.85:
        return "outro"
    elif density_ratio > 0.7:
        return "chorus"
    elif density_ratio < 0.3:
        return "breakdown"
    else:
        return "verse"


# ---------------------------------------------------------------------------
# Transition generators
# ---------------------------------------------------------------------------


def generate_fill(bars: int = 1, style: str = "snare_roll", duration: float = 0.25) -> list[Note]:
    """Generate a drum fill for transitions between sections."""
    total = int(4 / duration) * bars
    if style == "snare_roll":
        return [Note("D", 4, duration) for _ in range(total)]
    elif style == "buildup":
        result: list[Note] = []
        for i in range(total):
            if i < total // 3:
                result.append(Note("D", 4, duration) if i % 4 == 0 else Note.rest(duration))
            elif i < 2 * total // 3:
                result.append(Note("D", 4, duration) if i % 2 == 0 else Note.rest(duration))
            else:
                result.append(Note("D", 4, duration))
        return result
    elif style == "crash":
        return [Note("C", 6, duration)] + [Note.rest(duration)] * (total - 1)
    elif style == "tom_cascade":
        toms = ["G", "E", "C", "A"]
        return [Note(toms[i % len(toms)], 3, duration) for i in range(total)]
    return [Note("D", 4, duration) for _ in range(total)]


def generate_riser(
    bars: int = 2, start_note: str = "C", octave: int = 3, duration: float = 0.5
) -> list[Note]:
    """Generate an ascending chromatic riser for building tension."""
    _notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    total = int(4 / duration) * bars
    start_idx = _notes.index(start_note) if start_note in _notes else 0
    result: list[Note] = []
    for i in range(total):
        note_idx = (start_idx + i) % 12
        oct = min(octave + (start_idx + i) // 12, 7)
        result.append(Note(_notes[note_idx], oct, duration))
    return result


# ---------------------------------------------------------------------------
# Full song analysis report
# ---------------------------------------------------------------------------


def analyze_song(song: Song) -> dict:
    """Generate a comprehensive analysis report for a song.

    Combines key detection, harmony analysis, arrangement detection,
    density stats, and duration into a single dict.

    Args:
        song: Song to analyze.

    Returns:
        Dict with keys: title, bpm, key, duration_sec, total_beats, bars,
        tracks, arrangement, harmony, density_per_track.
    """
    from .theory import analyze_harmony as _analyze_harmony

    total_beats = song.total_beats
    duration_sec = song.duration_sec
    bars = max(1, int(total_beats / song.time_sig[0]))

    # Key detection
    try:
        from .engine import detect_key

        song.render()  # noqa: F841 — detect_key needs rendered audio
        root, mode, conf = detect_key(song)
        detected_key = f"{root} {mode} ({conf:.0%})"
    except Exception:
        detected_key = song.key_sig or "unknown"

    # Harmony
    try:
        harmony = _analyze_harmony(song, key=song.key_sig)
    except Exception:
        harmony = []

    # Arrangement
    try:
        arrangement = generate_arrangement(song)
    except Exception:
        arrangement = []

    # Per-track density
    density: dict[str, int] = {}
    for track in song.tracks:
        count = sum(
            1
            for b in track.beats
            if b.event
            and (
                (isinstance(b.event, Note) and b.event.pitch is not None)
                or isinstance(b.event, Chord)
            )
        )
        density[track.name] = count

    return {
        "title": song.title,
        "bpm": song.bpm,
        "key": detected_key,
        "duration_sec": round(duration_sec, 1),
        "total_beats": round(total_beats, 1),
        "bars": bars,
        "tracks": len(song.tracks),
        "track_names": [t.name for t in song.tracks],
        "arrangement": arrangement,
        "harmony": harmony,
        "density_per_track": density,
    }


# ---------------------------------------------------------------------------
# Auto-generate intro/outro
# ---------------------------------------------------------------------------


def generate_intro(song: Song, bars: int = 4) -> list[Note]:
    """Generate an intro section from existing song material.

    Takes the first melodic track's opening notes and creates a sparse,
    faded-in version suitable for an intro.

    Args:
        song:  Song to derive intro from.
        bars:  Length of intro in bars.

    Returns:
        List of Notes (sparse, with rests).
    """
    # Find first melodic track
    source_notes: list[Note] = []
    for track in song.tracks:
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None:
                source_notes.append(beat.event)
                if len(source_notes) >= bars * 2:
                    break
        if source_notes:
            break

    if not source_notes:
        return [Note.rest(float(bars * song.time_sig[0]))]

    # Create sparse version: note, rest, note, rest pattern
    result: list[Note] = []
    for i, note in enumerate(source_notes[: bars * 2]):
        result.append(
            Note(str(note.pitch), note.octave, note.duration, velocity=note.velocity * 0.5)
        )
        if i < len(source_notes) - 1:
            result.append(Note.rest(note.duration))
    return result


def generate_outro(song: Song, bars: int = 4) -> list[Note]:
    """Generate an outro section from existing song material.

    Takes the last melodic track's final notes reversed, with
    decreasing velocity for a fade-out effect.

    Args:
        song:  Song to derive outro from.
        bars:  Length of outro in bars.

    Returns:
        List of Notes (reversed, fading).
    """
    source_notes: list[Note] = []
    for track in reversed(song.tracks):
        for beat in reversed(track.beats):
            if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None:
                source_notes.append(beat.event)
                if len(source_notes) >= bars * 2:
                    break
        if source_notes:
            break

    if not source_notes:
        return [Note.rest(float(bars * song.time_sig[0]))]

    result: list[Note] = []
    for i, note in enumerate(source_notes[: bars * 2]):
        fade = max(0.1, 1.0 - (i / max(len(source_notes), 1)))
        result.append(
            Note(str(note.pitch), note.octave, note.duration, velocity=note.velocity * fade)
        )
    return result


# ---------------------------------------------------------------------------
# HTML export with embedded player
# ---------------------------------------------------------------------------


def to_html(song: Song, path: str | None = None) -> str:
    """Generate a standalone HTML page with embedded song data and player.

    The HTML includes the song's JSON serialization and a minimal JavaScript
    player UI with play/pause, track list, and song info.

    Args:
        song:  Song to export.
        path:  If provided, write HTML to this file.

    Returns:
        HTML string.
    """
    import json as _json

    from .serialization import song_to_json

    song_data = song_to_json(song)
    song_json = _json.dumps(song_data, indent=2)

    track_rows = ""
    for t in song.tracks:
        beats = len(t.beats)
        track_rows += f"<tr><td>{t.name}</td><td>{t.instrument}</td>"
        track_rows += f"<td>{t.volume:.1f}</td><td>{beats}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{song.title} — code-music</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px;
  margin: 2rem auto; padding: 0 1rem;
  background: #1a1a2e; color: #e0e0e0; }}
h1 {{ color: #7c3aed; margin-bottom: 0.5rem; }}
.meta {{ color: #888; margin-bottom: 1.5rem; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
th, td {{ padding: 0.5rem; text-align: left; border-bottom: 1px solid #333; }}
th {{ color: #7c3aed; }}
.info-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0; }}
.info-card {{ background: #16213e; padding: 1rem; border-radius: 8px; text-align: center; }}
.info-card .value {{ font-size: 1.5rem; font-weight: bold; color: #7c3aed; }}
.info-card .label {{ font-size: 0.8rem; color: #888; }}
pre {{ background: #16213e; padding: 1rem;
  border-radius: 8px; overflow-x: auto; font-size: 0.8rem; }}
footer {{ margin-top: 2rem; color: #555; font-size: 0.8rem; text-align: center; }}
</style>
</head>
<body>
<h1>{song.title}</h1>
<p class="meta">Generated by code-music |
{song.bpm:.0f} BPM | {song.key_sig} |
{song.time_sig[0]}/{song.time_sig[1]}</p>

<div class="info-grid">
  <div class="info-card">
    <div class="value">{len(song.tracks)}</div>
    <div class="label">Tracks</div></div>
  <div class="info-card">
    <div class="value">{song.total_beats:.0f}</div>
    <div class="label">Beats</div></div>
  <div class="info-card">
    <div class="value">{song.duration_sec:.1f}s</div>
    <div class="label">Duration</div></div>
</div>

<h2>Tracks</h2>
<table>
<tr><th>Name</th><th>Instrument</th><th>Volume</th><th>Beats</th></tr>
{track_rows}</table>

<h2>Song Data (JSON)</h2>
<details><summary>Click to expand</summary>
<pre>{song_json}</pre>
</details>

<footer>
  <p>Exported from
  <a href="https://github.com/Talador12/code-music"
  style="color:#7c3aed">code-music</a></p>
</footer>
</body>
</html>"""

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(html)

    return html


# ---------------------------------------------------------------------------
# SVG waveform visualization
# ---------------------------------------------------------------------------


def to_svg_waveform(
    song: Song,
    width: int = 800,
    height: int = 200,
    color: str = "#7c3aed",
    bg: str = "#1a1a2e",
    path: str | None = None,
) -> str:
    """Render a song's audio waveform as an SVG image.

    Renders the song, downsamples the waveform to `width` points,
    and draws it as a filled path.

    Args:
        song:   Song to visualize.
        width:  SVG width in pixels.
        height: SVG height in pixels.
        color:  Waveform fill color.
        bg:     Background color.
        path:   If provided, write SVG to this file.

    Returns:
        SVG string.
    """
    import numpy as np

    audio = song.render()
    if audio.ndim > 1:
        mono = np.mean(audio, axis=1)
    else:
        mono = audio

    n = len(mono)
    if n == 0:
        points_top = f"0,{height // 2}"
        points_bot = f"0,{height // 2}"
    else:
        # Downsample to width points
        chunk = max(1, n // width)
        samples = width if chunk > 0 else n
        peaks = np.zeros(samples)
        for i in range(samples):
            start = i * chunk
            end = min(start + chunk, n)
            if start < n:
                peaks[i] = np.max(np.abs(mono[start:end]))

        # Normalize
        peak_max = np.max(peaks)
        if peak_max > 0:
            peaks /= peak_max

        # Build SVG path points
        mid = height // 2
        top_points = []
        bot_points = []
        for i in range(samples):
            x = i * width / samples
            amp = peaks[i] * (height // 2 - 4)
            top_points.append(f"{x:.1f},{mid - amp:.1f}")
            bot_points.append(f"{x:.1f},{mid + amp:.1f}")
        points_top = " ".join(top_points)
        points_bot = " ".join(reversed(bot_points))

    vb = f"0 0 {width} {height}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  viewBox="{vb}" width="{width}" height="{height}">
<rect width="{width}" height="{height}" fill="{bg}"/>
<polygon points="{points_top} {points_bot}" fill="{color}" opacity="0.8"/>
<line x1="0" y1="{height // 2}" x2="{width}" y2="{height // 2}"
  stroke="{color}" stroke-width="0.5" opacity="0.3"/>
<text x="8" y="16" fill="{color}" font-size="12"
  font-family="system-ui">{song.title}</text>
</svg>"""

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(svg)

    return svg


# ---------------------------------------------------------------------------
# Piano Roll SVG Visualizer (v149.0)
# ---------------------------------------------------------------------------

# Track colors for the piano roll - 12 distinct hues
_PIANO_ROLL_COLORS = [
    "#7755ff",  # purple
    "#44cc88",  # green
    "#ffaa44",  # orange
    "#55aaff",  # blue
    "#ff5577",  # red
    "#ffdd44",  # yellow
    "#44dddd",  # cyan
    "#ff77cc",  # pink
    "#88cc44",  # lime
    "#cc77ff",  # violet
    "#ff8844",  # coral
    "#44aacc",  # teal
]


def to_piano_roll(
    song: Song,
    width: int = 1200,
    height: int = 500,
    bg: str = "#0a0a10",
    grid_color: str = "#1a1a25",
    path: str | None = None,
) -> str:
    """Render a Song as a piano roll SVG visualization.

    Each note becomes a colored rectangle: x-axis is time (beats),
    y-axis is pitch (MIDI note number), width is duration, color is
    per-track. Chords are expanded into individual note rectangles.
    Includes a grid, track legend, and pitch labels.

    Args:
        song:       Song to visualize.
        width:      SVG width in pixels.
        height:     SVG height in pixels.
        bg:         Background color.
        grid_color: Grid line color.
        path:       If provided, write SVG to this file path.

    Returns:
        SVG string.

    Example::

        >>> from code_music import Song, Track, Note
        >>> song = Song(title="Test", bpm=120)
        >>> tr = song.add_track(Track())
        >>> tr.add(Note("C", 4, 1.0))
        >>> svg = to_piano_roll(song)
        >>> "<svg" in svg
        True
    """
    from .engine import Chord as _Chord
    from .engine import Note as _Note

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

    # Collect all notes with time positions
    all_notes: list[dict] = []
    total_beats = 0.0

    for track_idx, track in enumerate(song.tracks):
        beat_pos = 0.0
        color = _PIANO_ROLL_COLORS[track_idx % len(_PIANO_ROLL_COLORS)]

        for beat in track.beats:
            if beat.event is not None:
                if isinstance(beat.event, _Note) and beat.event.pitch is not None:
                    pitch_str = str(beat.event.pitch)
                    semi = _SEMI_MAP.get(pitch_str, 0)
                    midi = semi + beat.event.octave * 12
                    all_notes.append(
                        {
                            "start": beat_pos,
                            "duration": beat.event.duration,
                            "midi": midi,
                            "track": track.name,
                            "color": color,
                            "velocity": getattr(beat.event, "velocity", 70),
                        }
                    )
                elif isinstance(beat.event, _Chord):
                    for cn in beat.event.notes:
                        if cn.pitch is not None:
                            semi = _SEMI_MAP.get(str(cn.pitch), 0)
                            midi = semi + cn.octave * 12
                            all_notes.append(
                                {
                                    "start": beat_pos,
                                    "duration": beat.event.duration,
                                    "midi": midi,
                                    "track": track.name,
                                    "color": color,
                                    "velocity": getattr(beat.event, "velocity", 60),
                                }
                            )
            beat_pos += beat.duration
        total_beats = max(total_beats, beat_pos)

    if not all_notes or total_beats == 0:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}"/>'
            f'<text x="{width // 2}" y="{height // 2}" fill="#555" '
            f'text-anchor="middle" font-size="14" '
            f'font-family="monospace">No notes to display</text>'
            f"</svg>"
        )
        if path:
            from pathlib import Path as _Path

            _Path(path).write_text(svg)
        return svg

    # Layout constants
    margin_left = 50
    margin_top = 30
    margin_bottom = 40
    margin_right = 20
    legend_height = 25
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom - legend_height

    # Pitch range
    midi_vals = [n["midi"] for n in all_notes]
    midi_min = max(0, min(midi_vals) - 2)
    midi_max = min(127, max(midi_vals) + 2)
    midi_range = max(midi_max - midi_min, 1)

    # Scale factors
    x_scale = plot_w / max(total_beats, 1)
    y_scale = plot_h / midi_range

    # Note names for pitch labels
    _NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'font-family="monospace">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="{bg}"/>')

    # Title
    parts.append(
        f'<text x="{margin_left}" y="18" fill="#888" font-size="12">'
        f"{song.title} - {song.bpm:.0f} BPM - {len(song.tracks)} tracks</text>"
    )

    # Grid: horizontal lines for octave C notes
    for midi in range(midi_min, midi_max + 1):
        if midi % 12 == 0:  # C notes
            y = margin_top + plot_h - (midi - midi_min) * y_scale
            parts.append(
                f'<line x1="{margin_left}" y1="{y:.1f}" '
                f'x2="{width - margin_right}" y2="{y:.1f}" '
                f'stroke="{grid_color}" stroke-width="1"/>'
            )
            octave = midi // 12 - 1
            parts.append(
                f'<text x="{margin_left - 5}" y="{y + 4:.1f}" '
                f'fill="#555" font-size="10" text-anchor="end">C{octave}</text>'
            )

    # Grid: vertical lines for beats
    beat_grid = 4 if total_beats > 32 else (2 if total_beats > 16 else 1)
    beat = 0.0
    while beat <= total_beats:
        x = margin_left + beat * x_scale
        parts.append(
            f'<line x1="{x:.1f}" y1="{margin_top}" '
            f'x2="{x:.1f}" y2="{margin_top + plot_h}" '
            f'stroke="{grid_color}" stroke-width="1"/>'
        )
        if beat % beat_grid == 0:
            parts.append(
                f'<text x="{x:.1f}" y="{margin_top + plot_h + 14}" '
                f'fill="#555" font-size="9" text-anchor="middle">{int(beat)}</text>'
            )
        beat += beat_grid

    # Note rectangles
    for n in all_notes:
        x = margin_left + n["start"] * x_scale
        w = max(1, n["duration"] * x_scale - 1)
        y = margin_top + plot_h - (n["midi"] - midi_min + 1) * y_scale
        h = max(2, y_scale - 1)
        opacity = 0.5 + (n["velocity"] / 127) * 0.5
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{n["color"]}" opacity="{opacity:.2f}" rx="1"/>'
        )

    # Track legend
    seen_tracks: dict[str, str] = {}
    for n in all_notes:
        if n["track"] not in seen_tracks:
            seen_tracks[n["track"]] = n["color"]
    legend_y = height - legend_height + 5
    legend_x = margin_left
    for name, color in seen_tracks.items():
        parts.append(
            f'<rect x="{legend_x}" y="{legend_y}" width="10" height="10" fill="{color}" rx="2"/>'
        )
        parts.append(
            f'<text x="{legend_x + 14}" y="{legend_y + 9}" fill="#888" font-size="10">{name}</text>'
        )
        legend_x += len(name) * 7 + 24

    parts.append("</svg>")
    svg = "\n".join(parts)

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(svg)

    return svg


# ---------------------------------------------------------------------------
# Comprehensive full analysis report
# ---------------------------------------------------------------------------


def to_harmonic_rhythm(
    song: Song,
    width: int = 800,
    height: int = 120,
    bg: str = "#0a0a10",
    path: str | None = None,
) -> str:
    """Visualize harmonic rhythm as an SVG timeline.

    Shows chord changes over time: each chord gets a colored block.
    Width = duration, label = chord name. Reveals harmonic rhythm at a
    glance - are changes fast (every beat) or slow (every 4 bars)?

    Args:
        song:   Song to visualize.
        width:  SVG width.
        height: SVG height.
        bg:     Background color.
        path:   Optional file path to write SVG.

    Returns:
        SVG string.

    Example::

        >>> from code_music import Song, Track, Chord
        >>> song = Song(title="Test", bpm=120)
        >>> tr = song.add_track(Track())
        >>> tr.add(Chord("C", "maj", 4, duration=4.0))
        >>> svg = to_harmonic_rhythm(song)
        >>> "<svg" in svg
        True
    """
    from .engine import Chord as _Chord

    # Chord hue map by root (circle of fifths coloring)
    _ROOT_HUES = {
        "C": 0,
        "G": 30,
        "D": 60,
        "A": 90,
        "E": 120,
        "B": 150,
        "F#": 180,
        "Gb": 180,
        "Db": 210,
        "Ab": 240,
        "Eb": 270,
        "Bb": 300,
        "F": 330,
    }

    # Extract chords with time positions
    chord_events: list[dict] = []
    for track in song.tracks:
        beat_pos = 0.0
        for beat in track.beats:
            if beat.event is not None and isinstance(beat.event, _Chord):
                chord_events.append(
                    {
                        "root": beat.event.root,
                        "shape": beat.event.shape if isinstance(beat.event.shape, str) else "maj",
                        "start": beat_pos,
                        "duration": beat.event.duration,
                    }
                )
            beat_pos += beat.duration

    if not chord_events:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}"/>'
            f'<text x="{width // 2}" y="{height // 2}" fill="#555" text-anchor="middle" '
            f'font-size="14" font-family="monospace">No chords</text></svg>'
        )
        if path:
            from pathlib import Path as _Path

            _Path(path).write_text(svg)
        return svg

    # Sort by start time and deduplicate overlapping chords
    chord_events.sort(key=lambda c: c["start"])
    total_dur = max(c["start"] + c["duration"] for c in chord_events)
    x_scale = (width - 20) / max(total_dur, 1)

    margin = 10
    bar_height = height - 50

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="monospace">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="{bg}"/>')
    parts.append(
        f'<text x="{margin}" y="16" fill="#888" font-size="11">'
        f"{song.title} - Harmonic Rhythm ({len(chord_events)} changes)</text>"
    )

    for chord in chord_events:
        x = margin + chord["start"] * x_scale
        w = max(2, chord["duration"] * x_scale - 1)
        hue = _ROOT_HUES.get(chord["root"], 0)
        # Minor chords are darker
        lightness = 35 if "min" in chord["shape"] or "dim" in chord["shape"] else 50
        fill = f"hsl({hue}, 70%, {lightness}%)"

        parts.append(
            f'<rect x="{x:.1f}" y="24" width="{w:.1f}" height="{bar_height}" '
            f'fill="{fill}" rx="2" opacity="0.85"/>'
        )
        # Label if wide enough
        label = f"{chord['root']}{chord['shape']}"
        if w > len(label) * 6:
            parts.append(
                f'<text x="{x + w / 2:.1f}" y="{24 + bar_height / 2 + 4}" '
                f'fill="white" font-size="10" text-anchor="middle">{label}</text>'
            )

    # Beat markers
    beat = 0.0
    while beat <= total_dur:
        bx = margin + beat * x_scale
        parts.append(
            f'<text x="{bx:.1f}" y="{height - 4}" fill="#555" font-size="9" '
            f'text-anchor="middle">{int(beat)}</text>'
        )
        beat += 4

    parts.append("</svg>")
    svg = "\n".join(parts)

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(svg)

    return svg


def to_spectrogram(
    song: Song,
    width: int = 900,
    height: int = 400,
    bg: str = "#0a0a10",
    fft_size: int = 2048,
    log_freq: bool = True,
    path: str | None = None,
) -> str:
    """Render a Song's audio as a spectrogram SVG.

    STFT-based frequency x time visualization. Each time-frequency bin
    is colored by magnitude (dark = quiet, bright = loud). Log-frequency
    axis by default for musical analysis (octaves are equally spaced).

    Args:
        song:      Song to visualize.
        width:     SVG width in pixels.
        height:    SVG height in pixels.
        bg:        Background color.
        fft_size:  FFT window size.
        log_freq:  If True, use log frequency axis (musical). If False, linear.
        path:      Optional file path to write SVG.

    Returns:
        SVG string.

    Example::

        >>> from code_music import Song, Track, Note
        >>> song = Song(title="Test", bpm=120, sample_rate=22050)
        >>> tr = song.add_track(Track(instrument="sine"))
        >>> tr.add(Note("C", 4, 2.0))
        >>> svg = to_spectrogram(song)
        >>> "<svg" in svg
        True
    """
    import numpy as np

    from .synth import Synth

    # Render to mono
    synth = Synth(sample_rate=song.sample_rate)
    try:
        stereo = synth.render_song(song)
        if stereo.ndim == 2:
            mono = np.mean(stereo, axis=1)
        else:
            mono = stereo
    except Exception:
        mono = np.zeros(song.sample_rate)

    sr = song.sample_rate
    n = len(mono)

    if n < fft_size:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}"/>'
            f'<text x="{width // 2}" y="{height // 2}" fill="#555" text-anchor="middle" '
            f'font-size="14" font-family="monospace">Audio too short</text></svg>'
        )
        if path:
            from pathlib import Path as _Path

            _Path(path).write_text(svg)
        return svg

    # Compute STFT
    hop = fft_size // 4
    window = np.hanning(fft_size)
    num_frames = (n - fft_size) // hop + 1
    num_bins = fft_size // 2 + 1

    # Limit resolution for SVG (too many rects = huge file)
    max_time_bins = min(num_frames, width)
    max_freq_bins = min(num_bins, height)

    time_step = max(1, num_frames // max_time_bins)
    freq_step = max(1, num_bins // max_freq_bins)

    # Compute magnitude spectrogram (decimated)
    magnitudes = []
    for t_idx in range(0, num_frames, time_step):
        start = t_idx * hop
        frame = mono[start : start + fft_size] * window
        spectrum = np.abs(np.fft.rfft(frame))
        # Decimate frequency bins
        decimated = spectrum[::freq_step]
        magnitudes.append(decimated)

    if not magnitudes:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}"/></svg>'
        )
        if path:
            from pathlib import Path as _Path

            _Path(path).write_text(svg)
        return svg

    mag_array = np.array(magnitudes)  # shape: (time_bins, freq_bins)

    # Convert to dB
    mag_db = 20 * np.log10(mag_array + 1e-10)
    # Normalize to 0-1
    db_min = np.percentile(mag_db, 5)
    db_max = np.max(mag_db)
    db_range = max(db_max - db_min, 1)
    mag_norm = np.clip((mag_db - db_min) / db_range, 0, 1)

    # Layout
    margin_left = 50
    margin_top = 30
    margin_bottom = 30
    margin_right = 10
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    time_bins, freq_bins = mag_norm.shape
    cell_w = max(1, plot_w / time_bins)
    cell_h = max(1, plot_h / freq_bins)

    # Color map: dark blue -> purple -> orange -> white
    def _color(val):
        if val < 0.25:
            r = int(val * 4 * 40)
            g = 0
            b = int(val * 4 * 100 + 20)
        elif val < 0.5:
            t2 = (val - 0.25) * 4
            r = int(40 + t2 * 80)
            g = 0
            b = int(100 - t2 * 30)
        elif val < 0.75:
            t2 = (val - 0.5) * 4
            r = int(120 + t2 * 135)
            g = int(t2 * 100)
            b = int(70 - t2 * 70)
        else:
            t2 = (val - 0.75) * 4
            r = 255
            g = int(100 + t2 * 155)
            b = int(t2 * 200)
        return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="monospace">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<text x="{margin_left}" y="18" fill="#888" font-size="11">'
        f"{song.title} - Spectrogram ({sr} Hz)</text>",
    ]

    # Draw spectrogram cells
    for ti in range(time_bins):
        x = margin_left + ti * cell_w
        for fi in range(freq_bins):
            # Flip y: low frequencies at bottom
            y = margin_top + plot_h - (fi + 1) * cell_h
            color = _color(mag_norm[ti, fi])
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{cell_w + 0.5:.1f}" height="{cell_h + 0.5:.1f}" '
                f'fill="{color}"/>'
            )

    # Frequency axis labels
    max_freq = sr / 2
    freq_labels = [100, 500, 1000, 2000, 5000, 10000]
    for freq in freq_labels:
        if freq > max_freq:
            continue
        if log_freq:
            import math

            y_frac = math.log2(max(freq, 20)) / math.log2(max_freq)
        else:
            y_frac = freq / max_freq
        y = margin_top + plot_h - y_frac * plot_h
        if margin_top <= y <= margin_top + plot_h:
            label = f"{freq}" if freq < 1000 else f"{freq // 1000}k"
            parts.append(
                f'<text x="{margin_left - 5}" y="{y + 3:.1f}" fill="#555" '
                f'font-size="9" text-anchor="end">{label}</text>'
            )

    # Time axis labels
    total_sec = n / sr
    for sec in range(0, int(total_sec) + 1, max(1, int(total_sec) // 6)):
        x = margin_left + (sec / total_sec) * plot_w
        parts.append(
            f'<text x="{x:.1f}" y="{height - 8}" fill="#555" '
            f'font-size="9" text-anchor="middle">{sec}s</text>'
        )

    parts.append("</svg>")
    svg = "\n".join(parts)

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(svg)

    return svg


def to_track_waveforms(
    song: Song,
    width: int = 900,
    track_height: int = 80,
    bg: str = "#0a0a10",
    path: str | None = None,
) -> str:
    """Render per-track waveforms as a stacked SVG.

    Each track gets its own waveform row, colored differently, with track
    name labels. Total height = track_height * number of tracks. Shows
    the relative amplitude and timing of each track at a glance.

    Args:
        song:         Song to visualize.
        width:        SVG width.
        track_height: Height per track row.
        bg:           Background color.
        path:         Optional file path to write SVG.

    Returns:
        SVG string.

    Example::

        >>> from code_music import Song, Track, Note
        >>> song = Song(title="Test", bpm=120, sample_rate=22050)
        >>> tr = song.add_track(Track(name="lead", instrument="sine"))
        >>> tr.add(Note("C", 4, 2.0))
        >>> svg = to_track_waveforms(song)
        >>> "<svg" in svg
        True
    """
    import numpy as np

    from .synth import Synth

    _COLORS = [
        "#7755ff",
        "#44cc88",
        "#ffaa44",
        "#55aaff",
        "#ff5577",
        "#ffdd44",
        "#44dddd",
        "#ff77cc",
        "#88cc44",
        "#cc77ff",
    ]

    synth = Synth(sample_rate=song.sample_rate)
    total_beats = song.total_beats
    margin_left = 70
    margin_right = 10
    plot_w = width - margin_left - margin_right
    total_height = max(100, track_height * len(song.tracks) + 30)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{total_height}" font-family="monospace">',
        f'<rect width="{width}" height="{total_height}" fill="{bg}"/>',
        f'<text x="{margin_left}" y="16" fill="#888" font-size="11">'
        f"{song.title} - Per-Track Waveforms</text>",
    ]

    if not song.tracks:
        parts.append(
            f'<text x="{width // 2}" y="{total_height // 2}" fill="#555" '
            f'text-anchor="middle" font-size="14">No tracks</text>'
        )
        parts.append("</svg>")
        svg = "\n".join(parts)
        if path:
            from pathlib import Path as _Path

            _Path(path).write_text(svg)
        return svg

    for idx, track in enumerate(song.tracks):
        y_offset = 24 + idx * track_height
        color = _COLORS[idx % len(_COLORS)]
        mid_y = y_offset + track_height // 2

        # Track label
        parts.append(
            f'<text x="{margin_left - 5}" y="{mid_y + 4}" fill="{color}" '
            f'font-size="10" text-anchor="end">{track.name}</text>'
        )

        # Center line
        parts.append(
            f'<line x1="{margin_left}" y1="{mid_y}" '
            f'x2="{width - margin_right}" y2="{mid_y}" '
            f'stroke="#1a1a25" stroke-width="1"/>'
        )

        # Render track to mono
        try:
            mono = synth.render_track(track, song.bpm, total_beats)
        except Exception:
            mono = np.zeros(int(song.sample_rate * 2))

        if len(mono) == 0:
            continue

        # Downsample to width points
        n = len(mono)
        samples = min(plot_w, n)
        step = max(1, n // samples)
        half_h = track_height // 2 - 4

        points_top = []
        points_bot = []
        for i in range(samples):
            chunk = mono[i * step : (i + 1) * step]
            if len(chunk) == 0:
                continue
            peak = float(np.max(np.abs(chunk)))
            x = margin_left + i * plot_w / samples
            amp = peak * half_h
            points_top.append(f"{x:.1f},{mid_y - amp:.1f}")
            points_bot.append(f"{x:.1f},{mid_y + amp:.1f}")

        if points_top:
            pts = " ".join(points_top + list(reversed(points_bot)))
            parts.append(f'<polygon points="{pts}" fill="{color}" opacity="0.6"/>')

    # Separator lines between tracks
    for idx in range(1, len(song.tracks)):
        y = 24 + idx * track_height
        parts.append(
            f'<line x1="{margin_left}" y1="{y}" '
            f'x2="{width - margin_right}" y2="{y}" '
            f'stroke="#1a1a25" stroke-width="0.5"/>'
        )

    parts.append("</svg>")
    svg = "\n".join(parts)

    if path:
        from pathlib import Path as _Path

        _Path(path).write_text(svg)

    return svg


def full_analysis(song: Song) -> str:
    """Generate a comprehensive multi-page markdown analysis report.

    Combines form detection, key centers, modulations, cadences, tension
    curves, harmonic complexity, rhythmic density, melodic range, phrase
    structure, voice independence, and style classification into a single
    readable markdown document.

    Args:
        song: Song to analyze.

    Returns:
        Multi-page markdown string suitable for printing or saving.

    Example::

        report = full_analysis(song)
        Path("song_analysis.md").write_text(report)
    """
    from .theory import (
        ambiguity_score,
        complexity_score,
        detect_cadences,
        detect_key,
        detect_modulations,
        functional_analysis,
        label_form,
        song_fingerprint,
        tension_curve,
    )

    lines: list[str] = []

    # Header
    lines.append(f"# {song.title}")
    lines.append("")
    lines.append(
        f"**BPM:** {song.bpm:.0f} | **Key:** {song.key_sig}"
        f" | **Time:** {song.time_sig[0]}/{song.time_sig[1]}"
    )
    lines.append("")

    # Basic stats
    total_beats = song.total_beats
    duration_sec = song.duration_sec
    bars = max(1, int(total_beats / song.time_sig[0]))

    lines.append("## Overview")
    lines.append("")
    lines.append(
        f"- **Duration:** {duration_sec:.1f} seconds ({total_beats:.1f} beats, {bars} bars)"
    )
    lines.append(f"- **Tracks:** {len(song.tracks)}")
    lines.append(f"- **Instruments:** {', '.join(t.instrument for t in song.tracks)}")
    lines.append("")

    # Extract progression from song
    progression: list[tuple[str, str]] = []
    for track in song.tracks:
        pos = 0.0
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Chord):
                prog_root = beat.event.root
                prog_shape = beat.event.shape if isinstance(beat.event.shape, str) else "maj"
                progression.append((prog_root, prog_shape))
            if beat.event:
                pos += beat.event.duration

    # Key analysis
    if progression:
        lines.append("## Harmonic Analysis")
        lines.append("")

        key_info = detect_key(progression)
        if key_info:
            # detect_key returns a string (key root); use key_certainty for confidence
            from .theory import key_certainty

            cert = key_certainty(progression)
            root = cert["key"]
            conf = cert["confidence"]
            lines.append(f"**Detected Key:** {root} major (confidence: {conf:.0%})")
            lines.append("")

        # Cadences
        cadences = detect_cadences(progression, song.key_sig)
        if cadences:
            lines.append("**Cadences:**")
            for cad in cadences:
                pos = cad.get("position", cad.get("bar", "?"))
                lines.append(
                    f"- Position {pos}: {cad['type']} ({cad['chords'][0]} → {cad['chords'][1]})"
                )
            lines.append("")

        # Functional analysis
        try:
            func_analysis = functional_analysis(progression, song.key_sig)
            func_summary: dict[str, int] = {}
            for entry in func_analysis:
                func = entry.get("function", "unknown")
                func_summary[func] = func_summary.get(func, 0) + 1
            if func_summary:
                lines.append("**Functional Distribution:**")
                for func, count in sorted(func_summary.items(), key=lambda x: -x[1]):
                    pct = count / len(func_analysis) * 100
                    lines.append(f"- {func.capitalize()}: {count} ({pct:.0f}%)")
                lines.append("")
        except Exception:
            pass

        # Tension curve
        try:
            tc = tension_curve(progression, song.key_sig)
            if tc:
                avg_tension = sum(tc) / len(tc)
                peak_tension = max(tc)
                lines.append(
                    f"**Tension Curve:** Average {avg_tension:.2f}, Peak {peak_tension:.2f}"
                )
                lines.append("")
        except Exception:
            pass

        # Complexity
        try:
            comp = complexity_score(progression, song.key_sig)
            lines.append(f"**Harmonic Complexity Score:** {comp:.0f}/100")
            lines.append("")
        except Exception:
            pass

        # Ambiguity
        try:
            amb = ambiguity_score(progression)
            cert = 1.0 - amb
            lines.append(f"**Key Certainty:** {cert:.0%} (ambiguity: {amb:.2f})")
            lines.append("")
        except Exception:
            pass

        # Modulations
        try:
            mods = detect_modulations(progression, window=min(4, len(progression)))
            if len(mods) > 1:
                lines.append("**Modulations Detected:**")
                for region in mods:
                    lines.append(
                        f"- Bars {region['start_idx']}-{region['end_idx']}:"
                        f" {region['key']}"
                        f" (confidence: {region.get('confidence', 0.5):.0%})"
                    )
                lines.append("")
        except Exception:
            pass

    # Structure analysis
    lines.append("## Structure")
    lines.append("")

    arrangement = generate_arrangement(song)
    if arrangement:
        lines.append("**Sections:**")
        for section in arrangement:
            label = section.get("label", "unknown")
            start = section.get("start_bar", 0)
            end = section.get("end_bar", 0)
            tracks = section.get("tracks_active", [])
            lines.append(f"- Bars {start}-{end}: {label.capitalize()} ({len(tracks)} tracks)")
        lines.append("")

        # Try form labeling
        try:
            if progression:
                bars_per = max(1, len(progression) // bars) if bars > 0 else 1
                form = label_form(progression, bars_per_chord=bars_per)
                if form:
                    lines.append(f"**Form Pattern:** {form}")
                    lines.append("")
        except Exception:
            pass

    # Per-track analysis
    lines.append("## Track Analysis")
    lines.append("")

    for track in song.tracks:
        lines.append(f"### {track.name} ({track.instrument})")
        lines.append("")

        # Count notes/chords
        note_count = 0
        chord_count = 0
        rest_count = 0
        velocities: list[int] = []
        pitches: list[int] = []
        durations: list[float] = []

        for beat in track.beats:
            if beat.event is None:
                rest_count += 1
                continue
            if isinstance(beat.event, Note):
                if beat.event.pitch is not None:
                    note_count += 1
                    velocities.append(beat.event.velocity)
                    if beat.event.midi:
                        pitches.append(beat.event.midi)
                else:
                    rest_count += 1
                durations.append(beat.event.duration)
            elif isinstance(beat.event, Chord):
                chord_count += 1
                durations.append(beat.event.duration)

        lines.append(
            f"- **Notes:** {note_count} | **Chords:** {chord_count} | **Rests:** {rest_count}"
        )

        if velocities:
            avg_vel = sum(velocities) / len(velocities)
            lines.append(f"- **Average Velocity:** {avg_vel:.0f}/127")

        if pitches:
            low, high = min(pitches), max(pitches)
            lines.append(f"- **Pitch Range:** {low}-{high} MIDI ({high - low} semitones)")

        if durations:
            avg_dur = sum(durations) / len(durations)
            lines.append(f"- **Average Duration:** {avg_dur:.2f} beats")

        lines.append("")

    # Song fingerprint
    try:
        if progression:
            fp = song_fingerprint(progression, [])
            lines.append("## Fingerprint")
            lines.append("")
            lines.append("**Pitch Distribution (12-tone):**")
            hist = fp.get("pitch_histogram", [])
            if hist:
                total = sum(hist)
                for i, count in enumerate(hist):
                    if count > 0:
                        note_names = [
                            "C",
                            "C#",
                            "D",
                            "Eb",
                            "E",
                            "F",
                            "F#",
                            "G",
                            "Ab",
                            "A",
                            "Bb",
                            "B",
                        ]
                        pct = count / total * 100 if total > 0 else 0
                        lines.append(f"- {note_names[i]}: {count} ({pct:.0f}%)")
            lines.append("")
    except Exception:
        pass

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by code-music*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Song Builder DSL v2 - Full multi-track song definition
# ---------------------------------------------------------------------------


def parse_song_dsl(text: str) -> dict:
    """Parse Song Builder DSL v2 into a complete song specification.

    The DSL allows defining full songs with BPM, time signature, key,
    multiple tracks with instruments, and effects — all in a compact
    mini-language.

    Syntax::

        bpm: 120
        time: 4/4
        key: C

        track lead piano:
          | C4 E4 G4 C5 | - - - - |

        track bass bass:
          | C3 - - - | G2 - - - |

        effects:
          lead: reverb(room_size=0.7, wet=0.3)
          master: delay(delay_ms=375, feedback=0.3)

    Track lines use mini-notation:
        - Notes: C4, E4, G#5, Bb3
        - Rests: - or ~
        - Chords: [C4 E4 G4]
        - Bar lines: |

    Args:
        text: DSL source text.

    Returns:
        Dict with: bpm, time_sig, key_sig, title, tracks, effects.

    Example::

        spec = parse_song_dsl('''
            title: My Song
            bpm: 128
            time: 4/4
            key: Am

            track pad synth:
              | [A3 C4 E4] - - - | [G3 B3 D4] - - - |

            track lead sawtooth:
              | A4 - C5 - | B4 - G4 - |
        ''')
        # Returns dict with parsed specification
    """
    result: dict = {
        "bpm": 120,
        "time_sig": (4, 4),
        "key_sig": "C",
        "title": "Untitled",
        "tracks": [],
        "effects": {},
    }

    lines = text.strip().splitlines()
    line_idx = 0
    current_track: dict | None = None
    current_effects: dict | None = None

    while line_idx < len(lines):
        line = lines[line_idx].strip()
        line_idx += 1

        if not line or line.startswith("#"):
            continue

        # Global settings
        if line.startswith("bpm:"):
            try:
                result["bpm"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
            continue

        if line.startswith("time:"):
            time_part = line.split(":", 1)[1].strip()
            try:
                num, den = time_part.split("/")
                result["time_sig"] = (int(num), int(den))
            except ValueError:
                pass
            continue

        if line.startswith("key:"):
            result["key_sig"] = line.split(":", 1)[1].strip()
            continue

        if line.startswith("title:"):
            result["title"] = line.split(":", 1)[1].strip()
            continue

        # Track definition
        if line.startswith("track "):
            if current_track:
                result["tracks"].append(current_track)
            # Parse: "track <name> <instrument>:"
            rest = line[len("track ") :].strip()
            if ":" in rest:
                header, _ = rest.rsplit(":", 1)
            else:
                header = rest
            parts = header.split()
            if len(parts) >= 2:
                name = parts[0]
                instrument = parts[1]
            else:
                name = parts[0] if parts else "track"
                instrument = "piano"
            current_track = {
                "name": name,
                "instrument": instrument,
                "lines": [],
            }
            continue

        # Effects section
        if line.startswith("effects:"):
            if current_track:
                result["tracks"].append(current_track)
                current_track = None
            current_effects = {}
            continue

        # Effect entry (indented, under effects:)
        if current_effects is not None and line and not line.startswith("track "):
            if ":" in line:
                track_name, effect_spec = line.split(":", 1)
                track_name = track_name.strip()
                effect_spec = effect_spec.strip()
                current_effects[track_name] = effect_spec
            continue

        # Track content (indented lines or bar patterns)
        if current_track is not None and line:
            # Remove leading | and trailing | for cleaner parsing
            clean = line.strip()
            if clean.startswith("|"):
                clean = clean[1:]
            if clean.endswith("|"):
                clean = clean[:-1]
            current_track["lines"].append(clean.strip())

    # Add final track if exists
    if current_track:
        result["tracks"].append(current_track)
    if current_effects:
        result["effects"] = current_effects

    return result


def song_from_dsl_v2(text: str) -> Song:
    """Create a complete Song from DSL v2 text.

    This is the full-song constructor from DSL. It parses the DSL and
    builds a complete Song object with tracks, instruments, notes, and
    effects.

    Args:
        text: DSL source defining the song.

    Returns:
        Fully constructed Song object.

    Example::

        song = song_from_dsl_v2('''
            title: Jazz Lounge
            bpm: 110
            key: Bb

            track chords piano:
              | [Bb3 D4 F4] - - - | [Eb3 G3 Bb3] - - - |
              | [F3 A3 C4] - - - | [Bb3 D4 F4] - - - |

            track bass bass:
              | Bb2 - - - | Eb2 - - - | F2 - - - | Bb2 - - - |
        ''')
        song.render()  # Ready to play
    """
    from .effects import EffectsChain, delay, reverb

    spec = parse_song_dsl(text)

    song = Song(
        title=spec["title"],
        bpm=spec["bpm"],
        key_sig=spec["key_sig"],
        time_sig=spec["time_sig"],
    )

    # Build tracks
    for track_spec in spec["tracks"]:
        track = song.add_track(Track(name=track_spec["name"], instrument=track_spec["instrument"]))

        # Parse each line of track content
        for line in track_spec.get("lines", []):
            # Split by bars
            bars = [b.strip() for b in line.split("|") if b.strip()]
            for bar_content in bars:
                # Parse tokens: notes, chords, rests
                tokens = bar_content.split()
                for token in tokens:
                    if token in ("-", "~", "r"):
                        # Rest
                        track.add(Note.rest(1.0))
                    elif token.startswith("[") and token.endswith("]"):
                        # Chord: [C4 E4 G4]
                        inner = token[1:-1]
                        notes_str = inner.split()
                        notes = []
                        for ns in notes_str:
                            n = _parse_note_token(ns)
                            if n:
                                notes.append(n)
                        if notes:
                            # Create chord from notes (simplified)
                            root = str(notes[0].pitch) if notes[0].pitch else "C"
                            track.add(
                                Chord(
                                    root, "maj", octave=notes[0].octave, duration=float(len(notes))
                                )
                            )
                        else:
                            track.add(Note.rest(1.0))
                    else:
                        # Single note
                        n = _parse_note_token(token)
                        if n:
                            track.add(n)
                        else:
                            track.add(Note.rest(1.0))

    # Apply effects (basic parsing)
    for track_name, effect_spec in spec.get("effects", {}).items():
        if track_name == "master":
            # Master effects not yet supported per-track
            continue
        if "reverb" in effect_spec.lower():
            # Simple reverb
            if track_name not in song.effects:
                song.effects[track_name] = EffectsChain()
            song.effects[track_name].add(reverb, room_size=0.5, wet=0.3)
        elif "delay" in effect_spec.lower():
            if track_name not in song.effects:
                song.effects[track_name] = EffectsChain()
            song.effects[track_name].add(delay, delay_ms=375.0, feedback=0.3, wet=0.25)

    return song


def _parse_note_token(token: str) -> Note | None:
    """Parse a note token like 'C4', 'G#5', 'Bb3' into a Note."""
    if not token or token in ("-", "~", "r"):
        return None

    # Extract pitch and octave
    # Handle sharps and flats
    token = token.strip()
    octave = 4  # default

    # Find where octave starts (last digit)
    pitch_part = token
    for i, ch in enumerate(token):
        if ch.isdigit():
            pitch_part = token[:i]
            try:
                octave = int(token[i:])
            except ValueError:
                octave = 4
            break

    if not pitch_part:
        return None

    return Note(pitch_part, octave, 1.0)


# ---------------------------------------------------------------------------
# Tempo map visualization
# ---------------------------------------------------------------------------


def tempo_map(song: Song) -> str:
    """Render an ASCII tempo map showing BPM over time.

    If the song has a bpm_map (tempo changes), shows the BPM at each
    point. Otherwise shows a flat line at the song's BPM.

    Args:
        song: Song to visualize.

    Returns:
        Multi-line ASCII string.
    """
    lines = []
    lines.append(f"Tempo Map: {song.title}")
    lines.append("─" * 50)

    bpm_map = getattr(song, "bpm_map", [])
    if not bpm_map:
        # Flat tempo
        bar = "█" * 20
        lines.append(f"  {song.bpm:.0f} BPM  {bar}  (constant)")
        return "\n".join(lines)

    # Show each tempo change point
    max_bpm = max(bpm for _, bpm in bpm_map)
    for beat, bpm in bpm_map:
        bar_len = int(20 * bpm / max_bpm)
        bar = "█" * bar_len
        lines.append(f"  Beat {beat:>6.1f}: {bpm:>6.1f} BPM  {bar}")

    return "\n".join(lines)
