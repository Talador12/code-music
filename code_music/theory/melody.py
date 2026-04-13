"""theory.melody — melody generation, contour, patterns, smoothing, dynamics."""

from __future__ import annotations

from ._core import (
    _CHORD_SEMI,
    _NOTE_NAMES,
    _PATTERN_DB,
    _SCALE_INTERVALS,
    Note,
    _semi,
)


def generate_chord_melody(
    chords: list[tuple[str, str]],
    contour: str = "arch",
    octave: int = 5,
    duration: float = 0.5,
    notes_per_chord: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody that follows a chord progression's harmonic rhythm.

    Each chord gets `notes_per_chord` notes chosen from its chord tones,
    shaped by the contour pattern.

    Args:
        chords:          List of (root, shape) tuples.
        contour:         Melodic shape: 'arch' (up then down), 'descending',
                         'ascending', 'wave', 'random'.
        octave:          Base octave.
        duration:        Duration per note.
        notes_per_chord: How many notes to generate per chord.
        seed:            Random seed.

    Returns:
        List of Notes.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    total_notes = len(chords) * notes_per_chord

    for chord_idx, (root, shape) in enumerate(chords):
        root_semi = _semi(root)
        chord_semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in chord_semis]

        for note_idx in range(notes_per_chord):
            # Position in overall melody (0.0 to 1.0)
            pos = (chord_idx * notes_per_chord + note_idx) / max(total_notes - 1, 1)

            if contour == "arch":
                # Parabolic arch: low → high → low
                height = 1.0 - 4.0 * (pos - 0.5) ** 2
            elif contour == "ascending":
                height = pos
            elif contour == "descending":
                height = 1.0 - pos
            elif contour == "wave":
                import math

                height = 0.5 + 0.5 * math.sin(pos * 2 * math.pi)
            elif contour == "random":
                height = rng.random()
            else:
                height = 0.5

            # Map height to chord tone selection + octave offset
            tone_idx = int(height * (len(chord_notes) - 1))
            tone_idx = max(0, min(tone_idx, len(chord_notes) - 1))
            oct_offset = int(height * 2) - 1  # -1, 0, or 1
            note_oct = max(3, min(7, octave + oct_offset))

            result.append(Note(chord_notes[tone_idx], note_oct, duration))

    return result


def generate_counterpoint(
    melody: list[Note],
    species: int = 1,
    interval: str = "third",
    seed: int | None = None,
) -> list[Note]:
    """Generate a counterpoint line against a given melody.

    First species counterpoint: one note against one note, using
    consonant intervals (thirds, sixths, fifths, octaves).

    Args:
        melody:   The cantus firmus (original melody).
        species:  Counterpoint species (only 1 supported currently).
        interval: Preferred interval: 'third', 'sixth', 'fifth'.
        seed:     Random seed.

    Returns:
        List of Notes forming the counterpoint line.
    """
    import random

    rng = random.Random(seed)

    interval_semis = {"third": [3, 4], "sixth": [8, 9], "fifth": [7]}
    preferred = interval_semis.get(interval, [3, 4])

    result: list[Note] = []
    for note in melody:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
            continue

        note_semi = _semi(str(note.pitch))
        # Choose a consonant interval (above)
        offset = rng.choice(preferred)
        cp_semi = (note_semi + offset) % 12
        cp_pitch = _NOTE_NAMES[cp_semi]
        # Place counterpoint an octave above
        cp_oct = min(7, note.octave + 1)

        result.append(Note(cp_pitch, cp_oct, note.duration, velocity=note.velocity * 0.8))

    return result


# ---------------------------------------------------------------------------
# Melodic variation generators
# ---------------------------------------------------------------------------


def generate_variation(
    melody: list[Note],
    technique: str = "inversion",
    key: str = "C",
    seed: int | None = None,
) -> list[Note]:
    """Create a melodic variation using classical techniques.

    Args:
        melody:    Original melody (list of Notes).
        technique: Variation type:
            - 'inversion': mirror intervals (up→down, down→up)
            - 'retrograde': reverse the melody
            - 'retrograde_inversion': reverse + invert
            - 'augmentation': double note durations
            - 'diminution': halve note durations
            - 'sequence': transpose up by a step each repeat
            - 'ornamental': add passing tones between notes
        key:       Key root for scale-aware techniques.
        seed:      Random seed for ornamental technique.

    Returns:
        List of Notes forming the variation.
    """
    import random as _random

    if not melody:
        return []

    if technique == "retrograde":
        return [
            Note(str(n.pitch), n.octave, n.duration, velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(n.duration)
            for n in reversed(melody)
        ]

    elif technique == "inversion":
        # Mirror intervals around the first note
        result: list[Note] = []
        first_pitched = next((n for n in melody if n.pitch is not None), None)
        if first_pitched is None:
            return list(melody)
        anchor_semi = _semi(str(first_pitched.pitch)) + first_pitched.octave * 12
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                note_semi = _semi(str(note.pitch)) + note.octave * 12
                interval = note_semi - anchor_semi
                inv_semi = anchor_semi - interval
                inv_pc = inv_semi % 12
                inv_oct = max(2, min(7, inv_semi // 12))
                result.append(
                    Note(_NOTE_NAMES[inv_pc], inv_oct, note.duration, velocity=note.velocity)
                )
        return result

    elif technique == "retrograde_inversion":
        inverted = generate_variation(melody, "inversion", key)
        return list(reversed(inverted))

    elif technique == "augmentation":
        return [
            Note(str(n.pitch), n.octave, n.duration * 2, velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(n.duration * 2)
            for n in melody
        ]

    elif technique == "diminution":
        return [
            Note(str(n.pitch), n.octave, max(0.125, n.duration / 2), velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(max(0.125, n.duration / 2))
            for n in melody
        ]

    elif technique == "sequence":
        # Transpose up by 2 semitones (a whole step)
        result = []
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                semi = (_semi(str(note.pitch)) + 2) % 12
                result.append(
                    Note(_NOTE_NAMES[semi], note.octave, note.duration, velocity=note.velocity)
                )
        return result

    elif technique == "ornamental":
        # Add passing tones between notes
        rng = _random.Random(seed)
        result = []
        for i, note in enumerate(melody):
            if note.pitch is None:
                result.append(Note.rest(note.duration))
                continue
            half_dur = note.duration / 2
            result.append(Note(str(note.pitch), note.octave, half_dur, velocity=note.velocity))
            # Add a passing tone
            semi = _semi(str(note.pitch))
            step = rng.choice([-1, 1, 2, -2])
            pass_semi = (semi + step) % 12
            result.append(
                Note(_NOTE_NAMES[pass_semi], note.octave, half_dur, velocity=note.velocity * 0.7)
            )
        return result

    else:
        raise ValueError(
            f"Unknown technique {technique!r}. Choose: "
            "inversion, retrograde, retrograde_inversion, "
            "augmentation, diminution, sequence, ornamental"
        )


# ---------------------------------------------------------------------------
# Velocity humanization
# ---------------------------------------------------------------------------


def humanize_velocity(
    notes: list[Note],
    amount: float = 0.15,
    seed: int | None = None,
) -> list[Note]:
    """Add random velocity variation to notes for a more human feel.

    Args:
        notes:  List of Notes.
        amount: Maximum velocity deviation (0.0-0.5).
        seed:   Random seed for reproducibility.

    Returns:
        New list of Notes with randomized velocities.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    for note in notes:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
        else:
            delta = rng.uniform(-amount, amount)
            new_vel = max(0.05, min(1.0, note.velocity + delta))
            result.append(Note(str(note.pitch), note.octave, note.duration, velocity=new_vel))
    return result


# ---------------------------------------------------------------------------
# Scale info & chord extensions
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Melody analysis utilities
# ---------------------------------------------------------------------------


def melody_contour(notes: list[Note]) -> dict:
    """Classify the melodic contour (shape) of a note sequence.

    Returns step/skip/leap statistics and overall direction.

    Args:
        notes: List of Notes.

    Returns:
        Dict with direction, steps, skips, leaps, contour_string.
    """
    pitched = [(n.pitch, n.octave) for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return {"direction": "static", "steps": 0, "skips": 0, "leaps": 0, "contour_string": ""}

    intervals: list[int] = []
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i][0])) + pitched[i][1] * 12
        b = _semi(str(pitched[i + 1][0])) + pitched[i + 1][1] * 12
        intervals.append(b - a)

    steps = sum(1 for i in intervals if abs(i) <= 2)
    skips = sum(1 for i in intervals if 3 <= abs(i) <= 4)
    leaps = sum(1 for i in intervals if abs(i) >= 5)

    net = sum(intervals)
    if net > 2:
        direction = "ascending"
    elif net < -2:
        direction = "descending"
    else:
        direction = "static"

    contour = "".join("+" if i > 0 else "-" if i < 0 else "=" for i in intervals)

    return {
        "direction": direction,
        "steps": steps,
        "skips": skips,
        "leaps": leaps,
        "contour_string": contour,
    }


def dorian_lick(
    root: str,
    octave: int = 5,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a dorian mode lick (natural 6 over minor gives jazz/funk quality)."""
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    dorian = [0, 2, 3, 5, 7, 9, 10]
    dorian_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in dorian]
    lick_len = rng.randint(6, 10)
    result: list[Note] = [Note(rng.choice(dorian_notes), octave, duration) for _ in range(lick_len)]
    result.append(Note(root, octave, duration * 2))
    return result


def phrygian_run(
    root: str,
    octave: int = 5,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a phrygian scale run (b2 gives Spanish/flamenco quality)."""
    root_semi = _semi(root)
    phrygian = [0, 1, 3, 5, 7, 8, 10]
    result: list[Note] = []
    for i in range(length):
        idx = i % len(phrygian)
        oct_off = i // len(phrygian)
        semi = (root_semi + phrygian[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def lydian_run(
    root: str,
    octave: int = 5,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a lydian scale run (#4 gives bright, floating quality).

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.
    """
    root_semi = _semi(root)
    lydian = [0, 2, 4, 6, 7, 9, 11]  # 1 2 3 #4 5 6 7
    result: list[Note] = []
    for i in range(length):
        idx = i % len(lydian)
        oct_off = i // len(lydian)
        semi = (root_semi + lydian[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def mixolydian_lick(
    root: str,
    octave: int = 5,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a mixolydian lick (b7 gives bluesy/rock dominant quality).

    Args:
        root:     Root note.
        octave:   Octave.
        duration: Duration per note.
        seed:     Random seed.
    """
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    mixo = [0, 2, 4, 5, 7, 9, 10]  # 1 2 3 4 5 6 b7
    mixo_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in mixo]
    lick_len = rng.randint(6, 10)
    result: list[Note] = []
    for _ in range(lick_len):
        result.append(Note(rng.choice(mixo_notes), octave, duration))
    result.append(Note(root, octave, duration * 2))  # resolve to root
    return result


def whole_tone_run(
    root: str,
    octave: int = 4,
    length: int = 6,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a whole tone scale run (all whole steps).

    Creates a dreamlike, ambiguous quality — no leading tone.

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.
    """
    root_semi = _semi(root)
    wt_intervals = [0, 2, 4, 6, 8, 10]
    result: list[Note] = []
    for i in range(length):
        idx = i % len(wt_intervals)
        oct_off = i // len(wt_intervals)
        semi = (root_semi + wt_intervals[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def blues_lick(
    root: str,
    octave: int = 4,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a short blues lick from the blues scale.

    Classic turnaround phrase — 6-8 notes from the blues scale
    with characteristic bends (chromatic approach notes).

    Args:
        root:     Root note of the blues key.
        octave:   Octave.
        duration: Duration per note.
        seed:     Random seed.
    """
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    blues = [0, 3, 5, 6, 7, 10]  # blues scale intervals
    blues_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in blues]

    # Classic lick shape: root area → blue note → resolve
    lick_len = rng.randint(6, 8)
    result: list[Note] = []
    for i in range(lick_len):
        note = rng.choice(blues_notes)
        result.append(Note(note, octave, duration))
    # End on root
    result.append(Note(root, octave, duration * 2))
    return result


def arpeggio_pattern(
    root: str,
    shape: str,
    octave: int = 4,
    pattern: str = "1353",
    duration: float = 0.25,
) -> list[Note]:
    """Generate an arpeggio from a numbered pattern string.

    Pattern digits map to chord tone indices: 1=root, 3=third, 5=fifth, etc.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        pattern:  String of digits (1-indexed chord tones). e.g. "1353", "1535".
        duration: Duration per note.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")
    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]
    chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in semis]

    result: list[Note] = []
    for ch in pattern:
        idx = int(ch) - 1
        if 0 <= idx < len(chord_notes):
            result.append(Note(chord_notes[idx], octave, duration))
    return result


def chromatic_run(
    start: str,
    start_octave: int,
    length: int = 12,
    direction: str = "up",
    duration: float = 0.125,
) -> list[Note]:
    """Generate a chromatic scale run.

    Args:
        start:         Starting note.
        start_octave:  Starting octave.
        length:        Number of notes.
        direction:     'up' or 'down'.
        duration:      Duration per note.

    Returns:
        List of chromatic Notes.
    """
    semi = _semi(start)
    step = 1 if direction == "up" else -1
    result: list[Note] = []
    for i in range(length):
        s = (semi + i * step) % 12
        oct = start_octave + (semi + i * step) // 12
        oct = max(2, min(7, oct))
        result.append(Note(_NOTE_NAMES[s], oct, duration))
    return result


def trill(
    note: str,
    octave: int,
    upper: bool = True,
    duration: float = 2.0,
    speed: float = 0.125,
) -> list[Note]:
    """Generate a trill between two adjacent notes.

    Args:
        note:     Main note.
        octave:   Octave.
        upper:    If True, trill with note above; else below.
        duration: Total trill duration.
        speed:    Duration of each alternation.

    Returns:
        List of alternating Notes.
    """
    semi = _semi(note)
    alt_semi = (semi + (1 if upper else -1)) % 12
    alt_oct = octave + (
        1 if upper and semi + 1 >= 12 else (-1 if not upper and semi - 1 < 0 else 0)
    )
    alt_oct = max(2, min(7, alt_oct))
    alt_note = _NOTE_NAMES[alt_semi]

    count = max(2, int(duration / speed))
    result: list[Note] = []
    for i in range(count):
        if i % 2 == 0:
            result.append(Note(note, octave, speed))
        else:
            result.append(Note(alt_note, alt_oct, speed))
    return result


def diminished_run(
    root: str,
    octave: int = 4,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a diminished scale run (half-whole pattern).

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.

    Returns:
        List of Notes on the diminished scale.
    """
    root_semi = _semi(root)
    dim_intervals = [0, 1, 3, 4, 6, 7, 9, 10]  # half-whole
    result: list[Note] = []
    for i in range(length):
        idx = i % len(dim_intervals)
        octave_offset = i // len(dim_intervals)
        semi = (root_semi + dim_intervals[idx]) % 12
        oct = min(7, octave + octave_offset)
        result.append(Note(_NOTE_NAMES[semi], oct, duration))
    return result


def canon(melody: list[Note], delay_beats: float = 4.0, voices: int = 2) -> list[list[Note]]:
    """Create a canon (round) — the same melody offset in time.

    Returns multiple voice lists. Voice 0 starts immediately,
    voice 1 starts after delay_beats of rests, etc.

    Args:
        melody:      The melody to canonize.
        delay_beats: Beats of delay between each voice entry.
        voices:      Number of voices (2-4).

    Returns:
        List of note lists, one per voice.
    """
    result: list[list[Note]] = []
    for v in range(min(voices, 4)):
        voice: list[Note] = []
        rest_dur = delay_beats * v
        if rest_dur > 0:
            voice.append(Note.rest(rest_dur))
        voice.extend(melody)
        result.append(voice)
    return result


def hocket(melody: list[Note], voices: int = 2) -> list[list[Note]]:
    """Split a melody across multiple voices (hocket technique).

    Each voice gets alternating notes — the others rest. Creates
    an interlocking texture where voices complete each other.

    Args:
        melody: The melody to split.
        voices: Number of voices to distribute across.

    Returns:
        List of note lists, one per voice.
    """
    result: list[list[Note]] = [[] for _ in range(voices)]
    for i, note in enumerate(melody):
        for v in range(voices):
            if i % voices == v:
                result[v].append(note)
            else:
                result[v].append(Note.rest(note.duration))
    return result


def sequence_by_interval(
    melody: list[Note],
    interval: int = 2,
    repetitions: int = 3,
) -> list[Note]:
    """Repeat a melody transposed up by an interval each time.

    Classical sequential technique — the same phrase at ascending
    or descending pitch levels.

    Args:
        melody:      Original phrase.
        interval:    Semitones to transpose each repetition.
        repetitions: Total repetitions (including original).

    Returns:
        Concatenated transposed phrases.
    """
    result: list[Note] = []
    for rep in range(repetitions):
        shift = interval * rep
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                semi = (_semi(str(note.pitch)) + shift) % 12
                oct = note.octave + ((_semi(str(note.pitch)) + shift) // 12)
                oct = max(2, min(7, oct))
                result.append(Note(_NOTE_NAMES[semi], oct, note.duration, velocity=note.velocity))
    return result


def call_and_response(
    call: list[Note],
    key: str = "C",
    mode: str = "major",
    seed: int | None = None,
) -> list[Note]:
    """Generate a 'response' phrase that answers a 'call' phrase.

    The response uses the same rhythm but different pitches from the
    same scale, ending on a chord tone for resolution.

    Args:
        call: The call phrase (list of Notes).
        key:  Key root.
        mode: Scale mode.
        seed: Random seed.

    Returns:
        Response phrase (same length/rhythm as call).
    """
    import random

    rng = random.Random(seed)
    scale_intervals = _SCALE_INTERVALS.get(mode, _SCALE_INTERVALS["major"])
    root_semi = _semi(key)
    scale_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in scale_intervals]

    result: list[Note] = []
    for i, n in enumerate(call):
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        elif i == len(call) - 1:
            # End on root for resolution
            result.append(Note(key, n.octave, n.duration, velocity=n.velocity))
        else:
            pitch = rng.choice(scale_notes)
            result.append(Note(pitch, n.octave, n.duration, velocity=n.velocity))
    return result


def ostinato(
    pattern: list[Note],
    repeats: int = 4,
    variation: float = 0.0,
    seed: int | None = None,
) -> list[Note]:
    """Repeat a short pattern with optional subtle variation.

    Args:
        pattern:   Short note pattern to repeat.
        repeats:   Number of repetitions.
        variation: Probability (0-1) of each note being slightly altered.
        seed:      Random seed.

    Returns:
        Repeated pattern with optional variations.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    for _ in range(repeats):
        for n in pattern:
            if n.pitch is None or variation == 0 or rng.random() > variation:
                result.append(n)
            else:
                # Slight variation: shift pitch by ±1-2 semitones
                semi = _semi(str(n.pitch))
                shift = rng.choice([-2, -1, 1, 2])
                new_semi = (semi + shift) % 12
                result.append(
                    Note(_NOTE_NAMES[new_semi], n.octave, n.duration, velocity=n.velocity)
                )
    return result


def dynamics_curve(notes: list[Note], start_vel: float = 0.3, end_vel: float = 0.9) -> list[Note]:
    """Apply a linear dynamics curve (crescendo or decrescendo).

    Args:
        notes:     List of Notes.
        start_vel: Starting velocity.
        end_vel:   Ending velocity.

    Returns:
        New list with linearly interpolated velocities.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        t = i / max(len(notes) - 1, 1)
        vel = start_vel + (end_vel - start_vel) * t
        vel = max(0.05, min(1.0, vel))
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), n.octave, n.duration, velocity=vel))
    return result


def arpeggiate_chord(
    root: str,
    shape: str,
    octave: int = 4,
    duration: float = 0.25,
    direction: str = "up",
    repeats: int = 1,
) -> list[Note]:
    """Convert a chord into an arpeggiated note sequence.

    Args:
        root:      Chord root.
        shape:     Chord quality.
        octave:    Base octave.
        duration:  Duration per note.
        direction: 'up', 'down', or 'updown'.
        repeats:   How many times to repeat the pattern.

    Returns:
        List of Notes.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")
    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]
    notes = [
        Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
        for s in semis
    ]

    if direction == "down":
        notes = list(reversed(notes))
    elif direction == "updown":
        notes = (
            notes + list(reversed(notes[1:-1])) if len(notes) > 2 else notes + list(reversed(notes))
        )

    return notes * repeats


def staccato(notes: list[Note], ratio: float = 0.5) -> list[Note]:
    """Shorten notes and add rests for a staccato articulation.

    Args:
        notes: List of Notes.
        ratio: Fraction of duration to sound (0.0-1.0). Rest fills remainder.

    Returns:
        New list with shortened notes + rests.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            sounding = max(0.0625, n.duration * ratio)
            silence = n.duration - sounding
            result.append(Note(str(n.pitch), n.octave, sounding, velocity=n.velocity))
            if silence > 0.001:
                result.append(Note.rest(silence))
    return result


def legato_connect(notes: list[Note], overlap: float = 0.1) -> list[Note]:
    """Extend note durations for a legato feel (overlapping notes).

    Each note's duration is extended by `overlap` beats, creating
    a connected, singing quality.

    Args:
        notes:   List of Notes.
        overlap: Extra duration in beats to add.

    Returns:
        New list with extended durations.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), n.octave, n.duration + overlap, velocity=n.velocity))
    return result


def stretch_melody(notes: list[Note], factor: float = 2.0) -> list[Note]:
    """Multiply all note durations by a factor.

    factor > 1 = slower (augmentation), factor < 1 = faster (diminution).
    More flexible than generate_variation augmentation/diminution since
    it accepts any float factor.

    Args:
        notes:  List of Notes.
        factor: Duration multiplier.

    Returns:
        New list with scaled durations.
    """
    result: list[Note] = []
    for n in notes:
        new_dur = max(0.0625, n.duration * factor)
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(str(n.pitch), n.octave, new_dur, velocity=n.velocity))
    return result


def pedal_point(note: str, octave: int, melody: list[Note]) -> list[Note]:
    """Add a pedal point (sustained bass note) alternating with melody notes.

    Creates a bass line that alternates between the pedal note and each
    melody note. Classic technique for building tension.

    Args:
        note:   Pedal note pitch.
        octave: Pedal note octave.
        melody: Melody notes to alternate with.

    Returns:
        List with pedal-melody-pedal-melody pattern.
    """
    result: list[Note] = []
    for m in melody:
        result.append(Note(note, octave, m.duration, velocity=m.velocity * 0.7))
        result.append(m)
    return result


def normalize_notes(notes: list[Note], target_octave: int = 4) -> list[Note]:
    """Normalize all pitched notes to a single octave.

    Useful for pitch class analysis — removes octave variation.

    Args:
        notes:         List of Notes.
        target_octave: Octave to normalize to.

    Returns:
        New list with all pitches at target_octave.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), target_octave, n.duration, velocity=n.velocity))
    return result


def species_counterpoint(
    cantus_firmus: list[Note],
    species: int = 1,
    above: bool = True,
    seed: int | None = None,
) -> list[Note]:
    """Generate counterpoint against a cantus firmus.

    Species counterpoint is the 500-year-old method that trained Bach,
    Mozart, and Beethoven. Each species adds rhythmic complexity while
    maintaining consonance rules.

    Species 1: note-against-note (whole notes)
    Species 2: two notes against one (half notes, passing tones allowed)

    Args:
        cantus_firmus: The given melody (one note per bar).
        species:       1 or 2.
        above:         True = counterpoint above CF, False = below.
        seed:          Random seed for deterministic output.

    Returns:
        List of Notes forming the counterpoint voice.
    """
    import random as _rng

    rng = _rng.Random(seed)

    if species not in (1, 2):
        raise ValueError(f"Only species 1 and 2 are supported, got {species}")

    result: list[Note] = []

    if species == 1:
        # Note-against-note: each counterpoint note must be consonant
        for cf_note in cantus_firmus:
            if cf_note.pitch is None:
                result.append(Note.rest(cf_note.duration))
                continue
            cf_semi = _semi(str(cf_note.pitch))
            # Pick a consonant interval
            consonant = [0, 3, 4, 7, 8, 9]  # P1, m3, M3, P5, m6, M6
            interval = rng.choice(consonant)
            if above:
                new_semi = (cf_semi + interval) % 12
                new_oct = cf_note.octave + (1 if cf_semi + interval >= 12 else 0)
            else:
                new_semi = (cf_semi - interval) % 12
                new_oct = cf_note.octave - (1 if cf_semi - interval < 0 else 0)
            new_oct = max(2, min(7, new_oct))
            result.append(Note(_NOTE_NAMES[new_semi], new_oct, cf_note.duration))

    elif species == 2:
        # Two notes per CF note: strong beat consonant, weak beat can pass
        for cf_note in cantus_firmus:
            if cf_note.pitch is None:
                result.append(Note.rest(cf_note.duration))
                continue
            cf_semi = _semi(str(cf_note.pitch))
            half_dur = cf_note.duration / 2

            # Strong beat: consonant
            consonant = [0, 3, 4, 7, 8, 9]
            interval1 = rng.choice(consonant)
            if above:
                s1 = (cf_semi + interval1) % 12
                o1 = cf_note.octave + (1 if cf_semi + interval1 >= 12 else 0)
            else:
                s1 = (cf_semi - interval1) % 12
                o1 = cf_note.octave - (1 if cf_semi - interval1 < 0 else 0)
            o1 = max(2, min(7, o1))
            result.append(Note(_NOTE_NAMES[s1], o1, half_dur))

            # Weak beat: passing tone (step from strong beat)
            step = rng.choice([-2, -1, 1, 2])
            s2 = (s1 + step) % 12
            o2 = o1 + (1 if s1 + step >= 12 else (-1 if s1 + step < 0 else 0))
            o2 = max(2, min(7, o2))
            result.append(Note(_NOTE_NAMES[s2], o2, half_dur))

    return result


# ---------------------------------------------------------------------------
# Scale-aware melody generation (v47.0)
# ---------------------------------------------------------------------------


def generate_scale_melody(
    key: str = "C",
    scale_name: str = "major",
    length: int = 16,
    octave: int = 5,
    duration: float = 0.5,
    contour: str = "arch",
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody constrained to a scale with a shaped contour.

    Uses a biased random walk that respects scale degrees and follows
    a melodic contour (arch, descending, wave, flat). More musical than
    pure random — the contour shapes the phrase like a breath.

    Args:
        key:        Root note.
        scale_name: Scale name (major, minor/aeolian, dorian, etc).
        length:     Number of notes.
        octave:     Center octave.
        duration:   Note duration.
        contour:    Shape of the melody: 'arch', 'descending', 'wave', 'flat'.
        seed:       Random seed for reproducibility.

    Returns:
        List of Notes following the scale and contour.
    """
    import random as _rng

    rng = _rng.Random(seed)

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    if sname not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {scale_name!r}")

    intervals = _SCALE_INTERVALS[sname]
    key_semi = _semi(key)

    # Build pool of absolute pitches across 2 octaves centered on target
    pool: list[int] = []
    for oct in range(octave - 1, octave + 2):
        for iv in intervals:
            pool.append(key_semi + iv + oct * 12)
    pool.sort()

    # Contour: target index offset over time (as fraction of length)
    def _contour_bias(pos: float) -> float:
        if contour == "arch":
            return 1.0 - abs(2.0 * pos - 1.0)  # peak at middle
        elif contour == "descending":
            return 1.0 - pos
        elif contour == "wave":
            import math

            return 0.5 + 0.5 * math.sin(pos * math.pi * 2)
        else:  # flat
            return 0.5

    center_idx = len(pool) // 2
    spread = len(pool) // 4
    idx = center_idx
    result: list[Note] = []

    for i in range(length):
        frac = i / max(length - 1, 1)
        bias = _contour_bias(frac)
        # Target index: center ± spread, shaped by contour
        target = int(center_idx + (bias - 0.5) * 2 * spread)
        # Random walk biased toward target
        if idx < target:
            step = rng.choice([0, 1, 1, 2])
        elif idx > target:
            step = rng.choice([0, -1, -1, -2])
        else:
            step = rng.choice([-1, 0, 0, 1])
        idx = max(0, min(len(pool) - 1, idx + step))

        absolute = pool[idx]
        pitch = _NOTE_NAMES[absolute % 12]
        oct = absolute // 12
        result.append(Note(pitch, oct, duration))

    return result


# ---------------------------------------------------------------------------
# Motif development & variation (v54.0)
# ---------------------------------------------------------------------------


def augment(motif: list[Note], factor: float = 2.0) -> list[Note]:
    """Double (or multiply) note durations — rhythmic augmentation.

    Makes the motif grander and more spacious. Beethoven's Fifth
    is basically one motif augmented and diminished for 30 minutes.

    Args:
        motif:  List of Notes.
        factor: Duration multiplier (2.0 = double, 3.0 = triple).

    Returns:
        New list with stretched durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration * factor, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration * factor)
        for n in motif
    ]


def diminish(motif: list[Note], factor: float = 2.0) -> list[Note]:
    """Halve (or divide) note durations — rhythmic diminution.

    Makes the motif urgent and compressed. The stretto in a fugue
    is diminution plus imitation — chaos on purpose.

    Args:
        motif:  List of Notes.
        factor: Duration divisor (2.0 = halve, 4.0 = quarter).

    Returns:
        New list with compressed durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration / factor, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration / factor)
        for n in motif
    ]


def fragment(motif: list[Note], length: int) -> list[Note]:
    """Extract the first N notes of a motif — fragmentation.

    The head motif is the most memorable part. Fragmentation isolates
    it for development — repeat the fragment, sequence it, build
    tension by withholding the rest.

    Args:
        motif:  List of Notes.
        length: Number of notes to extract.

    Returns:
        First `length` notes of the motif.
    """
    return list(motif[:length])


def motif_similarity(a: list[Note], b: list[Note]) -> float:
    """Compare two motifs by pitch contour and rhythm similarity.

    Returns a value between 0.0 (completely different) and 1.0
    (identical). Uses normalized pitch intervals and duration ratios.

    Args:
        a: First motif.
        b: Second motif.

    Returns:
        Similarity score in [0.0, 1.0].
    """
    if not a or not b:
        return 0.0

    # Compare pitch contours (direction of intervals)
    def _contour(notes: list[Note]) -> list[int]:
        result = []
        for i in range(1, len(notes)):
            if notes[i].pitch is None or notes[i - 1].pitch is None:
                result.append(0)
                continue
            s_curr = _semi(str(notes[i].pitch)) + notes[i].octave * 12
            s_prev = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
            diff = s_curr - s_prev
            result.append(1 if diff > 0 else (-1 if diff < 0 else 0))
        return result

    ca = _contour(a)
    cb = _contour(b)

    # Pad shorter contour with zeros
    max_len = max(len(ca), len(cb))
    if max_len == 0:
        return 1.0
    ca.extend([0] * (max_len - len(ca)))
    cb.extend([0] * (max_len - len(cb)))

    # Contour match score
    contour_match = sum(1 for x, y in zip(ca, cb) if x == y) / max_len

    # Duration ratio similarity
    dur_a = [n.duration for n in a]
    dur_b = [n.duration for n in b]
    max_dur_len = max(len(dur_a), len(dur_b))
    dur_a.extend([0.0] * (max_dur_len - len(dur_a)))
    dur_b.extend([0.0] * (max_dur_len - len(dur_b)))
    dur_match = (
        sum(1.0 - abs(da - db) / max(da, db, 0.01) for da, db in zip(dur_a, dur_b)) / max_dur_len
    )

    return round((contour_match + dur_match) / 2.0, 3)


# ---------------------------------------------------------------------------
# Lyric rhythm matching (v58.0)
# ---------------------------------------------------------------------------


def count_syllables(word: str) -> int:
    """Estimate syllable count for an English word.

    Uses a vowel-cluster heuristic: count groups of consecutive vowels,
    adjust for silent-e and common patterns. Not perfect — English is
    a chaotic language — but good enough for songwriting.

    Args:
        word: A single English word.

    Returns:
        Estimated syllable count (minimum 1).
    """
    word = word.lower().strip(".,!?;:'\"()-")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent-e adjustment
    if word.endswith("e") and count > 1:
        count -= 1
    # Words like "the" need at least 1
    return max(count, 1)


def stress_pattern(text: str) -> list[bool]:
    """Extract a strong/weak syllable pattern from text.

    Simple heuristic: in multi-syllable words, odd-indexed syllables
    are stressed (English tends toward alternating stress). Single-syllable
    content words are stressed, function words are unstressed.

    Args:
        text: A line of text.

    Returns:
        List of bools (True = stressed, False = unstressed), one per syllable.
    """
    _UNSTRESSED_WORDS = {
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "and",
        "but",
        "or",
        "is",
        "was",
        "be",
        "it",
        "its",
        "my",
        "your",
        "his",
        "her",
        "our",
        "their",
        "this",
        "that",
        "with",
        "from",
        "by",
        "as",
    }
    pattern: list[bool] = []
    words = text.split()
    for word in words:
        clean = word.lower().strip(".,!?;:'\"()-")
        n = count_syllables(clean)
        if n == 1:
            pattern.append(clean not in _UNSTRESSED_WORDS)
        else:
            for i in range(n):
                pattern.append(i % 2 == 0)  # stress on even positions (1st, 3rd, ...)
    return pattern


def text_to_melody(
    text: str,
    key: str = "C",
    scale_name: str = "major",
    octave: int = 5,
    beat_duration: float = 0.5,
    seed: int | None = None,
) -> list[Note]:
    """Map text to a melody based on syllable stress and contour.

    Stressed syllables get higher pitches and longer durations.
    Unstressed syllables stay low and short. Questions end with
    a rising contour, statements fall. The bridge between words
    and music that every songwriter needs.

    Args:
        text:          Input text (one line).
        key:           Root note.
        scale_name:    Scale to constrain pitches.
        octave:        Center octave.
        beat_duration: Base duration per syllable.
        seed:          Random seed for variation.

    Returns:
        List of Notes, one per syllable.
    """
    import random as _rng

    rng = _rng.Random(seed)
    stresses = stress_pattern(text)
    if not stresses:
        return []

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)

    # Build pitch pool
    pool: list[int] = []
    for o in range(octave - 1, octave + 2):
        for iv in intervals:
            pool.append(k + iv + o * 12)
    pool.sort()
    center = len(pool) // 2

    # Question = rising end, statement = falling end
    is_question = text.strip().endswith("?")

    notes: list[Note] = []
    idx = center
    for i, stressed in enumerate(stresses):
        frac = i / max(len(stresses) - 1, 1)

        if stressed:
            idx = min(idx + rng.randint(1, 3), len(pool) - 1)
            dur = beat_duration * 1.5
        else:
            idx = max(idx - rng.randint(0, 2), 0)
            dur = beat_duration * 0.75

        # End contour
        if frac > 0.8:
            if is_question:
                idx = min(idx + 1, len(pool) - 1)
            else:
                idx = max(idx - 1, 0)

        absolute = pool[idx]
        pitch = _NOTE_NAMES[absolute % 12]
        oct = absolute // 12
        notes.append(Note(pitch, oct, dur))

    return notes


# ---------------------------------------------------------------------------
# Chord tone targeting (v63.0)
# ---------------------------------------------------------------------------


def target_chord_tones(
    progression: list[tuple[str, str]],
    key: str = "C",
    notes_per_chord: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody that lands on chord tones at strong beats.

    The core principle of jazz improvisation: beat 1 and 3 hit chord
    tones, beats 2 and 4 use passing scale tones. The difference
    between noodling and intentional storytelling.

    Args:
        progression: Chord progression as (root, shape) tuples.
        key:         Key for scale-tone fills.
        notes_per_chord: Notes per chord (must be even; odd beats = chord tones).
        seed:        Random seed.

    Returns:
        List of Notes targeting chord tones on strong beats.
    """
    import random as _rng

    rng = _rng.Random(seed)

    key_semi = _semi(key)
    scale_ivs = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
    scale_pcs = [(key_semi + iv) % 12 for iv in scale_ivs]

    result: list[Note] = []
    for root, shape in progression:
        root_semi = _semi(root)
        chord_pcs = [(root_semi + s) % 12 for s in _CHORD_SEMI.get(shape, [0, 4, 7])]

        for beat in range(notes_per_chord):
            if beat % 2 == 0:
                # Strong beat: chord tone
                pc = rng.choice(chord_pcs)
            else:
                # Weak beat: scale tone (passing)
                pc = rng.choice(scale_pcs)

            result.append(Note(_NOTE_NAMES[pc], 5, 0.5))

    return result


def approach_pattern(
    target: str,
    octave: int = 5,
    direction: str = "chromatic",
    duration: float = 0.25,
) -> list[Note]:
    """Generate an approach pattern to a target note.

    Approach patterns are how jazz musicians arrive at a chord tone
    with style instead of just landing on it. Three flavors:

    - chromatic: half-step above and below, then target
    - diatonic: step above, step below, then target
    - enclosure: above then below (or vice versa), then target

    Args:
        target:    Target pitch name.
        octave:    Target octave.
        direction: 'chromatic', 'diatonic', or 'enclosure'.
        duration:  Duration per approach note.

    Returns:
        List of 3 Notes: approach above, approach below, target.
    """
    t = _semi(target)
    if direction == "chromatic":
        above = (t + 1) % 12
        below = (t - 1) % 12
    elif direction == "diatonic":
        above = (t + 2) % 12
        below = (t - 2) % 12
    else:  # enclosure
        above = (t + 1) % 12
        below = (t - 2) % 12

    return [
        Note(_NOTE_NAMES[above], octave, duration),
        Note(_NOTE_NAMES[below], octave, duration),
        Note(target, octave, duration * 2),
    ]


# ---------------------------------------------------------------------------
# Melody harmonization (v75.0)
# ---------------------------------------------------------------------------


def harmonize_melody(
    melody: list[Note],
    key: str = "C",
    style: str = "thirds",
    scale_name: str = "major",
) -> list[list[Note]]:
    """Add harmony voices to a single-line melody.

    The inverse of melody extraction — given a melody, automatically
    generate 1-3 additional voices in a specific harmonic style.

    Styles:
    - 'thirds': parallel diatonic thirds (pop/rock)
    - 'sixths': parallel diatonic sixths (country)
    - 'chorale': SATB-style with contrary motion

    Args:
        melody:     Input melody notes.
        key:        Key root.
        style:      Harmonization style.
        scale_name: Scale for diatonic interval calculation.

    Returns:
        List of voice lists: [melody, harmony_1, ...].
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    scale_pcs = [(k + iv) % 12 for iv in intervals]

    def _diatonic_above(pc: int, steps: int) -> int:
        if pc in scale_pcs:
            idx = scale_pcs.index(pc)
        else:
            idx = min(range(len(scale_pcs)), key=lambda i: abs(scale_pcs[i] - pc))
        new_idx = (idx + steps) % len(scale_pcs)
        return scale_pcs[new_idx]

    def _diatonic_below(pc: int, steps: int) -> int:
        return _diatonic_above(pc, -steps)

    voices: list[list[Note]] = [list(melody)]

    if style == "thirds":
        harmony: list[Note] = []
        for n in melody:
            if n.pitch is None:
                harmony.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                h_pc = _diatonic_above(pc, 2)  # diatonic 3rd above
                harmony.append(Note(_NOTE_NAMES[h_pc], n.octave, n.duration, velocity=n.velocity))
        voices.append(harmony)

    elif style == "sixths":
        harmony = []
        for n in melody:
            if n.pitch is None:
                harmony.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                h_pc = _diatonic_below(pc, 2)  # diatonic 3rd below = 6th above
                harmony.append(
                    Note(
                        _NOTE_NAMES[h_pc],
                        n.octave - 1 if h_pc > pc else n.octave,
                        n.duration,
                        velocity=n.velocity,
                    )
                )
        voices.append(harmony)

    elif style == "chorale":
        # Simplified: thirds above + sixth below
        thirds: list[Note] = []
        sixths: list[Note] = []
        for n in melody:
            if n.pitch is None:
                thirds.append(Note.rest(n.duration))
                sixths.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                t_pc = _diatonic_above(pc, 2)
                s_pc = _diatonic_below(pc, 2)
                thirds.append(Note(_NOTE_NAMES[t_pc], n.octave, n.duration, velocity=n.velocity))
                sixths.append(
                    Note(
                        _NOTE_NAMES[s_pc],
                        n.octave - 1 if s_pc > pc else n.octave,
                        n.duration,
                        velocity=n.velocity,
                    )
                )
        voices.append(thirds)
        voices.append(sixths)

    return voices


def list_patterns(
    genre: str | None = None,
    max_difficulty: int | None = None,
) -> list[str]:
    """List available patterns, optionally filtered by genre/difficulty.

    Args:
        genre:          Filter by genre (jazz, blues, rock, latin, classical, funk).
        max_difficulty: Maximum difficulty (1-4).

    Returns:
        Sorted list of pattern names.
    """
    result = []
    for name, info in _PATTERN_DB.items():
        if genre and info["genre"] != genre:
            continue
        if max_difficulty and info["difficulty"] > max_difficulty:
            continue
        result.append(name)
    return sorted(result)


def get_pattern(
    name: str,
    key: str = "C",
    octave: int = 5,
    duration: float = 0.5,
) -> list[Note]:
    """Retrieve a named pattern transposed to a key.

    Args:
        name:     Pattern name from the database.
        key:      Key root to transpose to.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the pattern.

    Raises:
        ValueError: If pattern name not found.
    """
    if name not in _PATTERN_DB:
        raise ValueError(f"Unknown pattern {name!r}. Use list_patterns() to see available.")
    k = _semi(key)
    intervals = _PATTERN_DB[name]["notes"]
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def chain_patterns(
    names: list[str],
    key: str = "C",
    octave: int = 5,
    duration: float = 0.5,
    connector_duration: float = 0.25,
) -> list[Note]:
    """Chain multiple patterns together with scale-tone connectors.

    Retrieves each pattern and links them with a passing tone between
    the last note of one pattern and the first of the next.

    Args:
        names:              Pattern names.
        key:                Key root.
        octave:             Base octave.
        duration:           Note duration within patterns.
        connector_duration: Duration for connecting notes.

    Returns:
        List of Notes forming the chained sequence.
    """
    result: list[Note] = []
    for i, name in enumerate(names):
        notes = get_pattern(name, key, octave, duration)
        result.extend(notes)
        # Add connector between patterns
        if i < len(names) - 1 and notes:
            last_semi = _semi(str(notes[-1].pitch))
            next_pattern = get_pattern(names[i + 1], key, octave, duration)
            if next_pattern:
                next_semi = _semi(str(next_pattern[0].pitch))
                mid = ((last_semi + next_semi) // 2) % 12
                result.append(Note(_NOTE_NAMES[mid], octave, connector_duration))
    return result


# ---------------------------------------------------------------------------
# Dynamic range processing (v79.0)
# ---------------------------------------------------------------------------


def crescendo(
    notes: list[Note],
    start_vel: int = 40,
    end_vel: int = 100,
) -> list[Note]:
    """Apply a gradual volume increase across a note list.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity (0-127).
        end_vel:   Ending velocity (0-127).

    Returns:
        New note list with linearly interpolated velocities.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        vel = int(start_vel + (end_vel - start_vel) * frac)
        vel = max(0, min(127, vel))
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(n.pitch, n.octave, n.duration, velocity=vel))
    return result


def decrescendo(
    notes: list[Note],
    start_vel: int = 100,
    end_vel: int = 40,
) -> list[Note]:
    """Apply a gradual volume decrease across a note list.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity.
        end_vel:   Ending velocity.

    Returns:
        New note list with decreasing velocities.
    """
    return crescendo(notes, start_vel, end_vel)


def sforzando(notes: list[Note], position: int = 0, accent_vel: int = 127) -> list[Note]:
    """Apply a sudden accent at a specific note position.

    Args:
        notes:      Input notes.
        position:   Index of the note to accent.
        accent_vel: Velocity for the accented note.

    Returns:
        New note list with the accent applied.
    """
    result = list(notes)
    if 0 <= position < len(result) and result[position].pitch is not None:
        n = result[position]
        result[position] = Note(n.pitch, n.octave, n.duration, velocity=accent_vel)
    return result


def dynamics_map(notes: list[Note]) -> list[int]:
    """Extract the velocity curve from a note list.

    Args:
        notes: Input notes.

    Returns:
        List of velocity values, one per note (0 for rests).
    """
    return [n.velocity if n.pitch is not None else 0 for n in notes]


# ---------------------------------------------------------------------------
# Instrument technique simulation (v84.0)
# ---------------------------------------------------------------------------


def hammer_on(note_a: Note, note_b: Note) -> list[Note]:
    """Simulate a guitar hammer-on — second note is quieter with no attack gap.

    Args:
        note_a: First (picked) note.
        note_b: Second (hammered) note — gets reduced velocity.

    Returns:
        Two notes: original velocity, then 60% velocity.
    """
    n2_vel = int(note_b.velocity * 0.6) if note_b.pitch else 0
    return [
        note_a,
        Note(note_b.pitch, note_b.octave, note_b.duration, velocity=n2_vel)
        if note_b.pitch
        else Note.rest(note_b.duration),
    ]


def pull_off(note_a: Note, note_b: Note) -> list[Note]:
    """Simulate a guitar pull-off — reverse of hammer-on.

    Args:
        note_a: First (fretted) note.
        note_b: Second (pulled-off to) note — gets reduced velocity.

    Returns:
        Two notes with decreasing velocity.
    """
    return hammer_on(note_a, note_b)  # same velocity profile


def slide(
    note_a: Note,
    note_b: Note,
    steps: int = 4,
) -> list[Note]:
    """Simulate a glissando (slide) between two notes.

    Inserts chromatic passing tones between the start and end notes.
    The slide duration is divided equally among all intermediate notes.

    Args:
        note_a: Starting note.
        note_b: Ending note.
        steps:  Number of intermediate chromatic steps.

    Returns:
        List of notes from A to B via chromatic steps.
    """
    if note_a.pitch is None or note_b.pitch is None:
        return [note_a, note_b]

    a_abs = _semi(str(note_a.pitch)) + note_a.octave * 12
    b_abs = _semi(str(note_b.pitch)) + note_b.octave * 12
    direction = 1 if b_abs > a_abs else -1
    total_semitones = abs(b_abs - a_abs)
    actual_steps = min(steps, total_semitones)

    if actual_steps <= 0:
        return [note_a, note_b]

    step_dur = note_a.duration / (actual_steps + 1)
    result: list[Note] = []
    for i in range(actual_steps + 1):
        current = a_abs + direction * i * (total_semitones // (actual_steps + 1))
        pc = current % 12
        oct = current // 12
        vel = note_a.velocity - (i * 5)  # slight decay during slide
        result.append(Note(_NOTE_NAMES[pc], oct, step_dur, velocity=max(vel, 30)))

    result.append(note_b)
    return result


def palm_mute(notes: list[Note], decay_factor: float = 0.3) -> list[Note]:
    """Simulate palm muting — reduced sustain and percussive attack.

    Palm muting shortens note durations and reduces velocity for a
    tight, chunky sound. The backbone of metal rhythm guitar.

    Args:
        notes:        Input notes.
        decay_factor: Duration multiplier (0.3 = 30% of original length, rest fills gap).

    Returns:
        Notes with shortened durations, padded with rests.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            short_dur = n.duration * decay_factor
            rest_dur = n.duration * (1.0 - decay_factor)
            result.append(Note(n.pitch, n.octave, short_dur, velocity=n.velocity))
            result.append(Note.rest(rest_dur))
    return result


# ---------------------------------------------------------------------------
# Voice range optimizer (v108.0)
# ---------------------------------------------------------------------------


def fit_to_range(
    notes: list[Note],
    low: int = 48,
    high: int = 72,
) -> list[Note]:
    """Transpose notes to fit within a pitch range by octave shifting.

    Each note is individually octave-shifted to the closest octave
    placement that falls within [low, high]. Rests pass through.

    Args:
        notes: Input notes.
        low:   Lowest allowed absolute pitch (C3 = 48).
        high:  Highest allowed absolute pitch (C5 = 72).

    Returns:
        Notes with octaves adjusted to fit range.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
            continue
        pc = _semi(str(n.pitch))
        current_abs = pc + n.octave * 12
        if low <= current_abs <= high:
            result.append(n)
            continue
        # Find closest octave within range
        best_oct = n.octave
        best_dist = abs(current_abs - (low + high) // 2)
        for o in range(0, 10):
            candidate = pc + o * 12
            if low <= candidate <= high:
                dist = abs(candidate - (low + high) // 2)
                if dist < best_dist:
                    best_dist = dist
                    best_oct = o
        result.append(Note(n.pitch, best_oct, n.duration, velocity=n.velocity))
    return result


def auto_octave(
    notes: list[Note],
    target_octave: int = 4,
) -> list[Note]:
    """Shift all notes to center around a target octave.

    Calculates the average octave and shifts the entire melody.

    Args:
        notes:         Input notes.
        target_octave: Desired center octave.

    Returns:
        Octave-shifted notes.
    """
    sounding = [n for n in notes if n.pitch is not None]
    if not sounding:
        return list(notes)
    avg_oct = sum(n.octave for n in sounding) / len(sounding)
    shift = round(target_octave - avg_oct)
    return [
        Note(n.pitch, n.octave + shift, n.duration, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration)
        for n in notes
    ]


# ---------------------------------------------------------------------------
# Melodic contour matching (v110.0)
# ---------------------------------------------------------------------------


def contour_string(notes: list[Note]) -> str:
    """Encode a melody's contour as a string: U=up, D=down, R=repeat.

    The contour is the shape of the melody stripped of exact pitches.
    Two melodies with the same contour string move in the same
    directions — they're melodically related even if in different keys.

    Args:
        notes: Input melody.

    Returns:
        String of U/D/R characters.
    """
    result: list[str] = []
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        if b > a:
            result.append("U")
        elif b < a:
            result.append("D")
        else:
            result.append("R")
    return "".join(result)


def contour_match(melody_a: list[Note], melody_b: list[Note]) -> float:
    """Compare two melodies by contour similarity (0.0-1.0).

    Two melodies that move in the same directions at the same positions
    score 1.0, regardless of actual pitches or key.

    Args:
        melody_a: First melody.
        melody_b: Second melody.

    Returns:
        Similarity score 0.0-1.0.
    """
    ca = contour_string(melody_a)
    cb = contour_string(melody_b)
    if not ca or not cb:
        return 0.0
    max_len = max(len(ca), len(cb))
    matches = sum(1 for a, b in zip(ca, cb) if a == b)
    return round(matches / max_len, 3)


# ---------------------------------------------------------------------------
# Melody smoothing (v126.0)
# ---------------------------------------------------------------------------


def smooth_melody(
    notes: list[Note],
    max_leap: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Smooth a melody by filling in large leaps with passing tones.

    When two consecutive notes are more than max_leap semitones apart,
    insert a chromatic passing tone halfway between them (splitting
    the first note's duration in half).

    Args:
        notes:    Input melody.
        max_leap: Maximum allowed interval in semitones before smoothing.
        seed:     Random seed (unused currently, reserved for future variation).

    Returns:
        Smoothed melody with passing tones inserted.
    """
    if len(notes) < 2:
        return list(notes)

    result: list[Note] = []
    for i in range(len(notes) - 1):
        curr = notes[i]
        nxt = notes[i + 1]

        if curr.pitch is None or nxt.pitch is None:
            result.append(curr)
            continue

        a = _semi(str(curr.pitch)) + curr.octave * 12
        b = _semi(str(nxt.pitch)) + nxt.octave * 12
        gap = abs(b - a)

        if gap > max_leap:
            # Insert passing tone at midpoint
            mid = (a + b) // 2
            half_dur = curr.duration / 2
            result.append(Note(curr.pitch, curr.octave, half_dur, velocity=curr.velocity))
            result.append(
                Note(_NOTE_NAMES[mid % 12], mid // 12, half_dur, velocity=int(curr.velocity * 0.8))
            )
        else:
            result.append(curr)

    result.append(notes[-1])
    return result


def fill_leaps(
    notes: list[Note],
    threshold: int = 5,
) -> list[Note]:
    """Replace each large leap with a stepwise chromatic run.

    Unlike smooth_melody (which adds one passing tone), fill_leaps
    inserts all chromatic steps between the two notes, dividing
    the original duration equally.

    Args:
        notes:     Input melody.
        threshold: Minimum leap size to fill (semitones).

    Returns:
        Melody with leaps replaced by chromatic runs.
    """
    if len(notes) < 2:
        return list(notes)

    result: list[Note] = []
    for i in range(len(notes) - 1):
        curr = notes[i]
        nxt = notes[i + 1]

        if curr.pitch is None or nxt.pitch is None:
            result.append(curr)
            continue

        a = _semi(str(curr.pitch)) + curr.octave * 12
        b = _semi(str(nxt.pitch)) + nxt.octave * 12
        gap = abs(b - a)

        if gap >= threshold:
            direction = 1 if b > a else -1
            steps = gap
            step_dur = curr.duration / steps
            for s in range(steps):
                p = a + direction * s
                result.append(Note(_NOTE_NAMES[p % 12], p // 12, step_dur, velocity=curr.velocity))
        else:
            result.append(curr)

    result.append(notes[-1])
    return result


# ---------------------------------------------------------------------------
# Note list statistics summary (v130.0)
# ---------------------------------------------------------------------------


def melody_summary(notes: list[Note]) -> dict:
    """Generate a comprehensive statistical summary of a melody.

    Combines multiple analysis functions into one call — the one-stop
    diagnostic for any note list.

    Args:
        notes: Input melody.

    Returns:
        Dict with: note_count, sounding_count, rest_count, total_duration,
        unique_pitches, range, avg_pitch, rest_ratio, leap_step_ratio,
        repetition_ratio, pitch_center.
    """
    sounding = [n for n in notes if n.pitch is not None]
    rests = [n for n in notes if n.pitch is None]
    total_dur = sum(n.duration for n in notes)

    # Range
    if sounding:
        absolutes = [_semi(str(n.pitch)) + n.octave * 12 for n in sounding]
        low = min(absolutes)
        high = max(absolutes)
        avg = sum(absolutes) / len(absolutes)
        range_semi = high - low
    else:
        low = high = 0
        avg = 0.0
        range_semi = 0

    # Unique pitches
    unique = len({(str(n.pitch), n.octave) for n in sounding})

    # Rest ratio
    rest_dur = sum(n.duration for n in rests)
    r_ratio = round(rest_dur / max(total_dur, 0.001), 4)

    # Leap/step
    leaps = 0
    steps = 0
    repeats = 0
    total_pairs = 0
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        diff = abs(b - a)
        total_pairs += 1
        if diff == 0:
            repeats += 1
        elif diff >= 3:
            leaps += 1
        else:
            steps += 1

    ls_ratio = round(leaps / max(steps, 1), 3)
    rep_ratio = round(repeats / max(total_pairs, 1), 4)

    # Pitch center
    if sounding:
        center_abs = round(avg)
        center = (_NOTE_NAMES[center_abs % 12], center_abs // 12)
    else:
        center = None

    return {
        "note_count": len(notes),
        "sounding_count": len(sounding),
        "rest_count": len(rests),
        "total_duration": round(total_dur, 4),
        "unique_pitches": unique,
        "range_semitones": range_semi,
        "avg_pitch": round(avg, 1),
        "rest_ratio": r_ratio,
        "leap_step_ratio": ls_ratio,
        "repetition_ratio": rep_ratio,
        "pitch_center": center,
    }


# ---------------------------------------------------------------------------
# Intelligent countermelody generator (v132.0)
# ---------------------------------------------------------------------------


def generate_countermelody(
    melody: list[Note],
    progression: list[tuple[str, str]],
    key: str = "C",
    scale_name: str = "major",
    style: str = "independent",
    seed: int | None = None,
) -> list[Note]:
    """Generate a countermelody that complements an existing melody.

    Unlike species_counterpoint (which is rule-strict), this targets
    musicality: chord tones on strong beats, contrary motion preference,
    independent contour, and voice separation. The result sounds like a
    second singer or instrument — related but distinct.

    Styles:
        'independent': contrary motion, own contour, chord-tone anchored.
            Best for a second vocal or horn line.
        'descant': sits above the melody, lighter rhythm (half the notes).
            Best for a high flute or violin counterline.
        'bass_counter': below the melody, root-oriented but with passing
            motion. Best for a cello or bass voice.

    Args:
        melody:      Main melody (list of Notes).
        progression: Chord progression as (root, shape) tuples.
                     Each chord is assumed to cover melody notes evenly.
        key:         Key root.
        scale_name:  Scale name for diatonic passing tones.
        style:       'independent', 'descant', or 'bass_counter'.
        seed:        Random seed for reproducibility.

    Returns:
        List of Notes forming the countermelody.

    Example::

        >>> mel = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 1.0)]
        >>> cm = generate_countermelody(mel, [("C", "maj")], key="C", seed=42)
        >>> len(cm) == len(mel)
        True
    """
    import random as _rng

    rng = _rng.Random(seed)

    if not melody:
        return []

    # Build scale pitch classes
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    key_semi = _semi(key)
    scale_pcs = [(key_semi + iv) % 12 for iv in intervals]

    # Map each melody note to its chord (evenly distributed)
    notes_per_chord = max(1, len(melody) // max(len(progression), 1))

    def _chord_at(idx: int) -> tuple[str, str]:
        ci = min(idx // notes_per_chord, len(progression) - 1)
        return progression[ci]

    # Build chord tone pool per chord
    def _chord_pcs(root: str, shape: str) -> list[int]:
        r = _semi(root)
        return [(r + s) % 12 for s in _CHORD_SEMI.get(shape, [0, 4, 7])]

    # Helper: find nearest scale tone to a target absolute pitch
    def _nearest_scale(target_abs: int, pool_pcs: list[int], target_oct: int) -> tuple[str, int]:
        best = None
        best_dist = 999
        for pc in pool_pcs:
            for o in (target_oct - 1, target_oct, target_oct + 1):
                a = pc + o * 12
                d = abs(a - target_abs)
                if d < best_dist:
                    best_dist = d
                    best = (pc, o)
        if best is None:
            return (_NOTE_NAMES[target_abs % 12], target_abs // 12)
        return (_NOTE_NAMES[best[0]], best[1])

    result: list[Note] = []
    prev_abs: int | None = None

    for i, note in enumerate(melody):
        if note.pitch is None:
            result.append(Note.rest(note.duration))
            continue

        mel_semi = _semi(str(note.pitch))
        mel_abs = mel_semi + note.octave * 12
        root, shape = _chord_at(i)
        chord_pcs = _chord_pcs(root, shape)
        is_strong = i % 2 == 0

        if style == "independent":
            # Contrary motion: if melody went up, go down
            if prev_abs is not None:
                mel_dir = mel_abs - prev_abs
                if mel_dir > 0:
                    target_abs = (prev_abs or mel_abs) - rng.choice([2, 3, 4, 5])
                elif mel_dir < 0:
                    target_abs = (prev_abs or mel_abs) + rng.choice([2, 3, 4, 5])
                else:
                    target_abs = mel_abs + rng.choice([-3, -2, 2, 3])
            else:
                # Start a 3rd or 6th away
                offset = rng.choice([-9, -8, -4, -3, 3, 4, 8, 9])
                target_abs = mel_abs + offset

            # Strong beats: snap to chord tone; weak beats: scale tone
            if is_strong:
                p, o = _nearest_scale(target_abs, chord_pcs, target_abs // 12)
            else:
                p, o = _nearest_scale(target_abs, scale_pcs, target_abs // 12)
            o = max(3, min(6, o))
            result.append(Note(p, o, note.duration, velocity=note.velocity * 0.85))
            prev_abs = _semi(p) + o * 12

        elif style == "descant":
            # Above melody, sparser (rest on weak beats)
            if is_strong:
                target_abs = mel_abs + rng.choice([3, 4, 5, 7])
                p, o = _nearest_scale(target_abs, chord_pcs, target_abs // 12)
                o = max(4, min(7, o))
                result.append(Note(p, o, note.duration * 2, velocity=note.velocity * 0.7))
                prev_abs = _semi(p) + o * 12
            else:
                result.append(Note.rest(note.duration))

        elif style == "bass_counter":
            # Below melody, root-heavy with passing motion
            if is_strong:
                # Land on root or fifth
                root_semi = _semi(root)
                choices = [root_semi, (root_semi + 7) % 12]
                pc = rng.choice(choices)
                o = max(2, min(4, note.octave - 2))
                result.append(Note(_NOTE_NAMES[pc], o, note.duration, velocity=note.velocity * 0.9))
                prev_abs = pc + o * 12
            else:
                # Passing scale tone
                if prev_abs is not None:
                    step = rng.choice([-2, -1, 1, 2])
                    target_abs = prev_abs + step
                    p, o = _nearest_scale(target_abs, scale_pcs, target_abs // 12)
                    o = max(2, min(4, o))
                    result.append(Note(p, o, note.duration, velocity=note.velocity * 0.75))
                    prev_abs = _semi(p) + o * 12
                else:
                    root_semi = _semi(root)
                    o = max(2, min(4, note.octave - 2))
                    result.append(Note(_NOTE_NAMES[root_semi], o, note.duration, velocity=0.8))
                    prev_abs = root_semi + o * 12
        else:
            raise ValueError(f"Unknown style {style!r}. Choose: independent, descant, bass_counter")

    return result


# ---------------------------------------------------------------------------
# Motif-based composition (v132.0)
# ---------------------------------------------------------------------------


def develop_motif(
    motif: list[Note],
    techniques: list[str] | None = None,
    key: str = "C",
    repetitions: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Build a full melodic passage from a short motif using classical development.

    Takes a 2-8 note motif and applies a sequence of transformation
    techniques to create an extended musical passage. This is how
    Beethoven built symphonies from four notes.

    Techniques (applied in sequence, cycling through the list):
        'repeat':              exact repetition
        'sequence':            transpose up by a whole step
        'inversion':           mirror intervals
        'retrograde':          reverse the motif
        'retrograde_inversion': reverse + invert
        'augmentation':        double durations
        'diminution':          halve durations
        'fragmentation':       use only the first half
        'extension':           add a step to the end
        'ornamentation':       add passing tones

    If techniques is None, uses a default development arc:
    repeat → sequence → inversion → fragmentation → augmentation → repeat.

    Args:
        motif:       Short melodic figure (2-8 notes recommended).
        techniques:  List of technique names to apply in order.
        key:         Key root (used by some techniques).
        repetitions: How many technique applications to make.
        seed:        Random seed for ornamental/extension techniques.

    Returns:
        Concatenated melodic passage built from the developed motif.

    Example::

        >>> motif = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("C", 5, 0.5)]
        >>> techs = ["repeat", "sequence", "inversion"]
        >>> passage = develop_motif(motif, techniques=techs, repetitions=3)
        >>> len(passage) == len(motif) * 3  # each technique produces motif-length output
        True
    """
    import random as _rng

    rng = _rng.Random(seed)

    if not motif:
        return []

    default_arc = [
        "repeat",
        "sequence",
        "inversion",
        "fragmentation",
        "augmentation",
        "repeat",
    ]
    techs = techniques if techniques is not None else default_arc

    result: list[Note] = list(motif)  # start with the original statement
    current = list(motif)

    for i in range(repetitions):
        tech = techs[i % len(techs)]

        if tech == "repeat":
            result.extend(current)

        elif tech == "sequence":
            current = generate_variation(current, "sequence", key)
            result.extend(current)

        elif tech == "inversion":
            current = generate_variation(current, "inversion", key)
            result.extend(current)

        elif tech == "retrograde":
            current = generate_variation(current, "retrograde", key)
            result.extend(current)

        elif tech == "retrograde_inversion":
            current = generate_variation(current, "retrograde_inversion", key)
            result.extend(current)

        elif tech == "augmentation":
            aug = augment(current, factor=2.0)
            result.extend(aug)
            # Don't update current — augmentation changes duration, not pitch

        elif tech == "diminution":
            dim = diminish(current, factor=2.0)
            result.extend(dim)

        elif tech == "fragmentation":
            frag_len = max(1, len(current) // 2)
            frag = fragment(current, frag_len)
            # Repeat the fragment twice to fill time
            result.extend(frag)
            result.extend(frag)

        elif tech == "extension":
            # Add one note: step up from the last pitched note
            extended = list(current)
            last_pitched = next((n for n in reversed(current) if n.pitch is not None), None)
            if last_pitched:
                last_semi = _semi(str(last_pitched.pitch))
                step = rng.choice([1, 2])
                new_semi = (last_semi + step) % 12
                new_oct = last_pitched.octave + (1 if last_semi + step >= 12 else 0)
                new_oct = max(2, min(7, new_oct))
                extended.append(
                    Note(
                        _NOTE_NAMES[new_semi],
                        new_oct,
                        last_pitched.duration,
                        velocity=last_pitched.velocity,
                    )
                )
            current = extended
            result.extend(current)

        elif tech == "ornamentation":
            current = generate_variation(current, "ornamental", key, seed=rng.randint(0, 2**31))
            result.extend(current)

        else:
            raise ValueError(
                f"Unknown technique {tech!r}. Choose: repeat, sequence, inversion, "
                "retrograde, retrograde_inversion, augmentation, diminution, "
                "fragmentation, extension, ornamentation"
            )

    return result
