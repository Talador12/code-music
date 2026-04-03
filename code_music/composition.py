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

    # Extract chords
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

    total_beats = max(sum(b.event.duration if b.event else 0 for b in t.beats) for t in song.tracks)
    total_bars = max(1, int(total_beats / beats_per_bar))
    bar_width = 16

    for bar_start in range(0, total_bars, 4):
        chord_line = "|"
        melody_line = "|"
        for b in range(min(4, total_bars - bar_start)):
            bar_beat = (bar_start + b) * beats_per_bar
            bar_end = bar_beat + beats_per_bar
            bar_chords = [c for p, c in chord_events if bar_beat <= p < bar_end]
            chord_line += f" {' '.join(bar_chords) if bar_chords else '':<{bar_width - 1}}|"
            bar_notes = [n for p, n in melody_events if bar_beat <= p < bar_end]
            melody_line += (
                f" {' '.join(bar_notes[:beats_per_bar]) if bar_notes else '':<{bar_width - 1}}|"
            )
        lines.append(chord_line)
        lines.append(melody_line)
        lines.append("")

    return "\n".join(lines)


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
