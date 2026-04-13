"""theory.harmony — chords, voicings, voice leading, modulation, scales."""

from __future__ import annotations

from ._core import (
    _CHORD_SEMI,
    _COMMON_NEXT,
    _DEGREE_NAMES,
    _DEGREE_SHAPES,
    _DEGREE_TO_SEMI,
    _ENHARMONIC_MAP,
    _IMPERFECT_CONSONANCES,
    _INTERVAL_NAMES,
    _KEY_SIGNATURES,
    _NOTE_NAMES,
    _PERFECT_CONSONANCES,
    _ROMAN_TO_DEGREE,
    _SATB_RANGES,
    _SCALE_INTERVALS,
    _SHAPE_SYMBOLS,
    _VOICING_DB,
    Note,
    _abs_to_note,
    _diatonic_chords,
    _find_nearest,
    _note_to_abs,
    _semi,
    _smooth_voice_lead,
)

# ---------------------------------------------------------------------------
# Chord-scale theory
# ---------------------------------------------------------------------------


def chord_scale(root: str, shape: str) -> list[str]:
    """Return scales compatible with a given chord for improvisation.

    Finds scales whose notes contain all chord tones as a subset.

    Args:
        root:  Chord root note (e.g. 'C', 'F#').
        shape: Chord quality (e.g. 'min7', 'dom7', 'maj7').

    Returns:
        List of scale names compatible with the chord.

    Example::

        chord_scale("C", "min7")   # → ["dorian", "aeolian", "phrygian"]
        chord_scale("G", "dom7")   # → ["mixolydian"]
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    chord_pcs = {(root_semi + s) % 12 for s in _CHORD_SEMI[shape]}

    compatible = []
    for scale_name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = {(root_semi + s) % 12 for s in intervals}
        if chord_pcs.issubset(scale_pcs):
            compatible.append(scale_name)
    return sorted(compatible)


def available_tensions(root: str, shape: str) -> list[str]:
    """Return available tension extensions for a chord.

    Analyzes which 9th, 11th, and 13th degrees are available without
    clashing with the chord tones.

    Args:
        root:  Chord root note.
        shape: Chord quality.

    Returns:
        List of tension names (e.g. ["9", "11", "b13"]).
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    chord_pcs = {(root_semi + s) % 12 for s in _CHORD_SEMI[shape]}

    tensions = []
    # Check each possible tension
    tension_map = {
        "b9": 1,
        "9": 2,
        "#9": 3,
        "11": 5,
        "#11": 6,
        "b13": 8,
        "13": 9,
    }

    for name, semi in tension_map.items():
        tension_pc = (root_semi + semi) % 12
        # Tension is available if it doesn't clash with a chord tone
        # (not a semitone away from any chord tone)
        clashes = False
        for ct in chord_pcs:
            if abs(tension_pc - ct) == 1 or abs(tension_pc - ct) == 11:
                clashes = True
                break
        if not clashes and tension_pc not in chord_pcs:
            tensions.append(name)

    return tensions


def secondary_dominant(target_root: str, target_shape: str = "maj") -> tuple[str, str]:
    """Return the secondary dominant (V/x) that resolves to the target chord.

    The secondary dominant is a dom7 chord whose root is a perfect 5th
    above the target. V/ii, V/V, V/vi — classic tonicization technique.

    Args:
        target_root:  Root of the chord to tonicize.
        target_shape: Shape of target chord (unused in calculation, for context).

    Returns:
        (root, "dom7") tuple of the secondary dominant.
    """
    target_semi = _semi(target_root)
    dom_semi = (target_semi + 7) % 12  # perfect 5th above
    return (_NOTE_NAMES[dom_semi], "dom7")


def deceptive_cadence(key: str = "C") -> list[tuple[str, str]]:
    """Generate a deceptive cadence: V → vi instead of V → I.

    The listener expects resolution to tonic but gets the relative minor.
    Classic surprise ending used since the Baroque era.

    Args:
        key: Key root.

    Returns:
        Two-chord progression [(V, dom7), (vi, min)].
    """
    key_semi = _semi(key)
    v_semi = (key_semi + 7) % 12
    vi_semi = (key_semi + 9) % 12
    return [(_NOTE_NAMES[v_semi], "dom7"), (_NOTE_NAMES[vi_semi], "min")]


def plagal_cadence(key: str = "C") -> list[tuple[str, str]]:
    """Generate a plagal cadence: IV → I (the 'Amen' cadence).

    Warm, conclusive resolution without dominant tension.
    Used in hymns, gospel, and as a tag ending.

    Args:
        key: Key root.

    Returns:
        Two-chord progression [(IV, maj), (I, maj)].
    """
    key_semi = _semi(key)
    iv_semi = (key_semi + 5) % 12
    return [(_NOTE_NAMES[iv_semi], "maj"), (key, "maj")]


def tritone_sub(chords: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Apply tritone substitution to dominant 7th chords.

    Replaces V7 chords with bII7 (same tritone, different root).
    Classic jazz reharmonization technique.

    Args:
        chords: List of (root, shape) tuples.

    Returns:
        New list with dominant chords tritone-substituted.
    """
    result: list[tuple[str, str]] = []
    for root, shape in chords:
        if shape in ("dom7", "dom9"):
            root_semi = _semi(root)
            tri_semi = (root_semi + 6) % 12  # tritone = 6 semitones
            result.append((_NOTE_NAMES[tri_semi], shape))
        else:
            result.append((root, shape))
    return result


def modal_interchange(
    chords: list[tuple[str, str]],
    key: str = "C",
    target_mode: str = "minor",
) -> list[tuple[str, str]]:
    """Borrow chords from a parallel mode for harmonic color.

    Takes a progression in the key and substitutes chords that exist
    in the target mode but not the original major scale. Classic
    technique: borrowing bIII, bVI, bVII, iv from minor.

    Args:
        chords:      Original progression [(root, shape), ...].
        key:         Key root.
        target_mode: Mode to borrow from ('minor', 'dorian', 'mixolydian').

    Returns:
        New progression with some chords borrowed from target mode.
    """
    key_semi = _semi(key)
    mode_intervals = _SCALE_INTERVALS.get(
        target_mode, _SCALE_INTERVALS.get("aeolian", [0, 2, 3, 5, 7, 8, 10])
    )
    # Build borrowed chord lookup
    borrowed: dict[int, tuple[str, str]] = {}
    _degree_shapes_minor = {0: "min", 2: "dim", 3: "maj", 5: "min", 7: "min", 8: "maj", 10: "maj"}
    for interval in mode_intervals:
        semi = (key_semi + interval) % 12
        shape = _degree_shapes_minor.get(interval, "maj")
        borrowed[semi] = (_NOTE_NAMES[semi], shape)

    result: list[tuple[str, str]] = []
    for root, shape in chords:
        root_semi = _semi(root)
        # If chord is diatonic to major, sometimes swap with borrowed
        if root_semi in borrowed and shape == "maj":
            b_root, b_shape = borrowed[root_semi]
            if b_shape != shape:  # only swap if it's actually different
                result.append((b_root, b_shape))
                continue
        result.append((root, shape))
    return result


def invert_chord(notes: list[Note], inversion: int = 1) -> list[Note]:
    """Apply a chord inversion by rotating the bottom note(s) up an octave.

    Args:
        notes:     List of Notes forming a chord.
        inversion: 1=first inversion, 2=second, etc.

    Returns:
        New list with bottom note(s) moved up an octave.
    """
    result = list(notes)
    for _ in range(min(inversion, len(result) - 1)):
        bottom = result.pop(0)
        if bottom.pitch is not None:
            result.append(
                Note(
                    str(bottom.pitch),
                    min(bottom.octave + 1, 7),
                    bottom.duration,
                    velocity=bottom.velocity,
                )
            )
        else:
            result.append(bottom)
    return result


def rotate_voicing(notes: list[Note], steps: int = 1) -> list[Note]:
    """Rotate a voicing by moving notes cyclically (no octave change).

    Args:
        notes: List of Notes.
        steps: Number of positions to rotate (positive=right).

    Returns:
        Rotated list.
    """
    if not notes:
        return []
    s = steps % len(notes)
    return notes[s:] + notes[:s]


def interval_name(note_a: str, note_b: str) -> str:
    """Name the interval between two notes.

    Args:
        note_a: First note (e.g. 'C').
        note_b: Second note (e.g. 'E').

    Returns:
        Interval name (e.g. 'major 3rd').
    """
    semi_a = _semi(note_a)
    semi_b = _semi(note_b)
    dist = (semi_b - semi_a) % 12
    return _INTERVAL_NAMES.get(dist, f"{dist} semitones")


def parallel_motion(
    melody: list[Note],
    interval: int = 7,
    above: bool = True,
) -> list[Note]:
    """Harmonize a melody by adding a parallel interval.

    Args:
        melody:   Original melody.
        interval: Interval in semitones (default 7 = perfect 5th).
        above:    If True, harmony is above; if False, below.

    Returns:
        List of Notes at the parallel interval.
    """
    result: list[Note] = []
    for note in melody:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
        else:
            semi = _semi(str(note.pitch))
            offset = interval if above else -interval
            new_semi = (semi + offset) % 12
            new_oct = note.octave + (1 if above and semi + offset >= 12 else 0)
            new_oct = max(
                2, min(7, new_oct if above else note.octave - (1 if semi + offset < 0 else 0))
            )
            result.append(
                Note(_NOTE_NAMES[new_semi], new_oct, note.duration, velocity=note.velocity * 0.85)
            )
    return result


def suggest_next_chord(
    current_root: str,
    current_shape: str,
    key: str = "C",
) -> list[tuple[str, str]]:
    """Suggest the next chord in a progression based on common voice leading.

    Args:
        current_root:  Current chord root.
        current_shape: Current chord quality.
        key:           Key of the progression.

    Returns:
        List of (root, shape) suggestions, most common first.
    """
    key_semi = _semi(key)
    current_semi = _semi(current_root)
    degree_semi = (current_semi - key_semi) % 12

    # Find current degree
    current_degree = None
    for deg, semi in _DEGREE_TO_SEMI.items():
        if semi == degree_semi:
            current_degree = deg
            break

    if current_degree is None:
        # Chromatic chord — suggest tonic resolution
        return [(key, "maj")]

    suggestions = _COMMON_NEXT.get(current_degree, ["I"])
    result: list[tuple[str, str]] = []
    for deg in suggestions:
        semi = _DEGREE_TO_SEMI[deg]
        root = _NOTE_NAMES[(key_semi + semi) % 12]
        shape = _DEGREE_SHAPES[deg]
        result.append((root, shape))
    return result


def scale_info(scale_name: str, root: str = "C") -> dict:
    """Describe a scale with intervals, note names, and compatible chords.

    Args:
        scale_name: Scale name (major, minor, dorian, etc).
        root:       Root note.

    Returns:
        Dict with name, root, notes, intervals, chord_fits.
    """
    # Alias common names
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    scale_name = aliases.get(scale_name, scale_name)
    if scale_name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {scale_name!r}")

    root_semi = _semi(root)
    intervals = _SCALE_INTERVALS[scale_name]
    notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in intervals]

    # Find chords whose tones are subsets of this scale
    scale_pcs = {(root_semi + i) % 12 for i in intervals}
    chord_fits: list[str] = []
    for degree_idx, interval in enumerate(intervals):
        degree_root = _NOTE_NAMES[(root_semi + interval) % 12]
        for shape, semis in _CHORD_SEMI.items():
            chord_pcs = {(root_semi + interval + s) % 12 for s in semis}
            if chord_pcs.issubset(scale_pcs):
                chord_fits.append(f"{degree_root}{shape}")

    return {
        "name": scale_name,
        "root": root,
        "notes": notes,
        "intervals": intervals,
        "chord_fits": chord_fits,
    }


def chord_extensions(
    root: str,
    shape: str,
    extensions: list[str] | None = None,
) -> list[Note]:
    """Add extensions (9th, 11th, 13th) to a chord.

    Args:
        root:       Chord root note.
        shape:      Base chord quality.
        extensions: List of extensions to add: '9', '11', '13', 'b9', '#9', '#11', 'b13'.
                    If None, adds available tensions automatically.

    Returns:
        List of Notes forming the extended chord.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    base_semis = list(_CHORD_SEMI[shape])

    tension_map = {"b9": 1, "9": 2, "#9": 3, "11": 5, "#11": 6, "b13": 8, "13": 9}

    if extensions is None:
        extensions = available_tensions(root, shape)

    for ext in extensions:
        if ext in tension_map:
            base_semis.append(tension_map[ext])

    return [
        Note(_NOTE_NAMES[(root_semi + s) % 12], 3 + s // 12, 4.0) for s in sorted(set(base_semis))
    ]


# ---------------------------------------------------------------------------
# Chord voicing generators
# ---------------------------------------------------------------------------


def generate_chord_voicing(
    root: str,
    shape: str,
    octave: int = 3,
    voicing: str = "close",
    duration: float = 4.0,
) -> list[Note]:
    """Generate a specific chord voicing as individual notes.

    Args:
        root:     Chord root note.
        shape:    Chord quality (maj, min7, dom7, etc).
        octave:   Base octave.
        voicing:  Voicing type:
            - 'close': all notes within one octave (default)
            - 'spread': notes spread across 2+ octaves
            - 'drop2': second-highest note dropped an octave
            - 'rootless': omit root (jazz voicing)
        duration: Note duration.

    Returns:
        List of Notes forming the voicing.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]

    if voicing == "close":
        return [
            Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
            for s in semis
        ]
    elif voicing == "spread":
        result: list[Note] = []
        for i, s in enumerate(semis):
            oct = octave + i  # each note one octave higher
            result.append(Note(_NOTE_NAMES[(root_semi + s) % 12], min(oct, 7), duration))
        return result
    elif voicing == "drop2":
        close = [(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12) for s in semis]
        if len(close) >= 3:
            # Drop second-highest note by one octave
            second_idx = len(close) - 2
            p, o = close[second_idx]
            close[second_idx] = (p, max(2, o - 1))
        return [Note(p, o, duration) for p, o in close]
    elif voicing == "rootless":
        # Skip the root (first note)
        return [
            Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
            for s in semis[1:]
        ]
    else:
        raise ValueError(f"Unknown voicing {voicing!r}. Choose: close, spread, drop2, rootless")


# ---------------------------------------------------------------------------
# Chromatic harmony — Neapolitan, augmented sixth, picardy third (v39.0)
# ---------------------------------------------------------------------------


def neapolitan_chord(key: str = "C", octave: int = 3, duration: float = 4.0) -> list[Note]:
    """Generate a Neapolitan chord (bII major in first inversion).

    The Neapolitan is a major triad built on the lowered second degree,
    typically in first inversion. It resolves to V, creating dramatic
    pre-dominant tension. Staple of classical and film music.

    Args:
        key:      Key root.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the Neapolitan chord (bII/first inversion).
    """
    key_semi = _semi(key)
    bii_semi = (key_semi + 1) % 12  # lowered 2nd degree
    # Major triad on bII: root, major 3rd, perfect 5th
    pitches = [bii_semi, (bii_semi + 4) % 12, (bii_semi + 7) % 12]
    # First inversion: 3rd in bass, then root, then 5th
    return [
        Note(_NOTE_NAMES[pitches[1]], octave, duration),
        Note(_NOTE_NAMES[pitches[0]], octave + 1, duration),
        Note(_NOTE_NAMES[pitches[2]], octave + 1, duration),
    ]


def augmented_sixth(
    key: str = "C",
    variety: str = "italian",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate an augmented sixth chord (Italian, French, or German).

    All three share the characteristic interval: b6 to #4 (an augmented
    sixth) that resolves outward to an octave on the dominant. The varieties
    differ in the additional tones:

    - Italian (It+6): b6, 1, #4 — three notes, lean and bright
    - French (Fr+6): b6, 1, 2, #4 — adds the major 2nd, whole-tone flavor
    - German (Gr+6): b6, 1, b3, #4 — adds the minor 3rd, enharmonic with dom7

    Args:
        key:      Key root.
        variety:  'italian', 'french', or 'german'.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the augmented sixth chord.

    Raises:
        ValueError: If variety is not italian, french, or german.
    """
    key_semi = _semi(key)
    b6 = (key_semi + 8) % 12  # lowered 6th degree
    root = key_semi  # tonic (scale degree 1)
    sharp4 = (key_semi + 6) % 12  # raised 4th degree

    if variety == "italian":
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    elif variety == "french":
        d2 = (key_semi + 2) % 12  # major 2nd
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[d2], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    elif variety == "german":
        b3 = (key_semi + 3) % 12  # minor 3rd
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[b3], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    else:
        raise ValueError(f"Unknown variety {variety!r}. Choose: italian, french, german")


def picardy_third(key: str = "C", octave: int = 3, duration: float = 4.0) -> list[Note]:
    """Generate a Picardy third — major tonic chord in a minor key context.

    The Picardy third replaces the expected minor tonic with a major chord
    at the end of a piece in a minor key, creating an unexpectedly bright
    resolution. Common in Baroque music (Bach chorales), metal endings,
    and film scores.

    Args:
        key:      Minor key root (e.g. 'C' for C minor).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the major tonic (Picardy) chord.
    """
    key_semi = _semi(key)
    # Major triad on the tonic (raises the minor 3rd to major 3rd)
    pitches = [key_semi, (key_semi + 4) % 12, (key_semi + 7) % 12]
    return [Note(_NOTE_NAMES[p], octave + p // 12, duration) for p in pitches]


def voice_lead_satb(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[list[Note]]:
    """Generate four-part SATB voice leading for a chord progression.

    Produces smooth voice leading with parallel 5th/octave avoidance,
    voice range constraints, and common-tone retention. Each chord is
    realized as [soprano, alto, tenor, bass] Notes.

    This is the bread and butter of classical harmony — the algorithm
    every composition student learns in their first semester.

    Args:
        progression: List of (root, shape) chord tuples.
        key:         Key root (for context, used in doubling decisions).

    Returns:
        List of 4-element Note lists, one per chord in the progression.
    """
    if not progression:
        return []

    result: list[list[Note]] = []
    prev_voicing: list[int] | None = None

    for root, shape in progression:
        if shape not in _CHORD_SEMI:
            raise ValueError(f"Unknown chord shape {shape!r}")

        root_semi = _semi(root)
        chord_pcs = [(root_semi + s) % 12 for s in _CHORD_SEMI[shape]]

        if prev_voicing is None:
            # First chord — spread across SATB ranges
            bass_pc = chord_pcs[0]  # root in bass
            bass_abs = _find_nearest(bass_pc, 52, *_SATB_RANGES["bass"])
            tenor_pc = chord_pcs[2 % len(chord_pcs)]
            tenor_abs = _find_nearest(tenor_pc, 57, *_SATB_RANGES["tenor"])
            alto_pc = chord_pcs[1 % len(chord_pcs)]
            alto_abs = _find_nearest(alto_pc, 62, *_SATB_RANGES["alto"])
            soprano_pc = chord_pcs[0]  # double root in soprano
            soprano_abs = _find_nearest(soprano_pc, 72, *_SATB_RANGES["soprano"])
            voicing = [soprano_abs, alto_abs, tenor_abs, bass_abs]
        else:
            # Subsequent chords — minimize movement, retain common tones
            voicing = _smooth_voice_lead(chord_pcs, prev_voicing)

        # Enforce no voice crossing
        voicing.sort(reverse=True)  # soprano highest, bass lowest

        prev_voicing = voicing
        notes = []
        for absolute in voicing:
            p, o = _abs_to_note(absolute)
            notes.append(Note(p, o, 4.0))
        result.append(notes)

    return result


def check_parallel_fifths(voicing_a: list[Note], voicing_b: list[Note]) -> bool:
    """Check if two SATB voicings contain parallel perfect 5ths or octaves.

    Returns True if a forbidden parallel is detected. Classical part-writing
    rule: no two voices may move in parallel motion to a perfect 5th or octave.

    Args:
        voicing_a: First chord voicing (4 Notes, high to low).
        voicing_b: Second chord voicing (4 Notes, high to low).

    Returns:
        True if parallel 5ths or octaves are found.
    """
    for i in range(len(voicing_a)):
        for j in range(i + 1, len(voicing_a)):
            interval_a = (
                abs(
                    _note_to_abs(str(voicing_a[i].pitch), voicing_a[i].octave)
                    - _note_to_abs(str(voicing_a[j].pitch), voicing_a[j].octave)
                )
                % 12
            )
            interval_b = (
                abs(
                    _note_to_abs(str(voicing_b[i].pitch), voicing_b[i].octave)
                    - _note_to_abs(str(voicing_b[j].pitch), voicing_b[j].octave)
                )
                % 12
            )
            # Both intervals are P5 (7) or P8 (0) and voices moved
            if interval_a == interval_b and interval_a in (0, 7):
                moved_i = _note_to_abs(
                    str(voicing_a[i].pitch), voicing_a[i].octave
                ) != _note_to_abs(str(voicing_b[i].pitch), voicing_b[i].octave)
                moved_j = _note_to_abs(
                    str(voicing_a[j].pitch), voicing_a[j].octave
                ) != _note_to_abs(str(voicing_b[j].pitch), voicing_b[j].octave)
                if moved_i and moved_j:
                    return True
    return False


def find_pivot_chords(
    key_a: str,
    key_b: str,
    mode_a: str = "major",
    mode_b: str = "major",
) -> list[tuple[str, str]]:
    """Find chords common to two keys (pivot chords for modulation).

    A pivot chord exists diatonically in both keys, enabling smooth
    modulation. The listener hears it as belonging to the old key, but
    the composer reinterprets it in the new key. Sneaky and elegant.

    Args:
        key_a:  First key root.
        key_b:  Second key root.
        mode_a: Mode of first key.
        mode_b: Mode of second key.

    Returns:
        List of (root, shape) tuples that exist in both keys.
    """
    chords_a = set(_diatonic_chords(key_a, mode_a))
    chords_b = set(_diatonic_chords(key_b, mode_b))
    return sorted(chords_a & chords_b)


def modulation_path(
    key_a: str,
    key_b: str,
    mode: str = "major",
) -> list[tuple[str, str]]:
    """Find the shortest chord path from one key to another.

    Walks through the circle of fifths, collecting chords at each step.
    Each adjacent pair of keys shares many pivot chords, so the path
    stays smooth even for distant modulations.

    Args:
        key_a: Starting key root.
        key_b: Target key root.
        mode:  Mode for both keys.

    Returns:
        Chord progression that moves from key_a to key_b.
    """
    a_semi = _semi(key_a)
    b_semi = _semi(key_b)

    # Go around circle of fifths (each step = +7 semitones)
    # or circle of fourths (each step = +5 semitones), whichever shorter
    fifths_dist = 0
    s = a_semi
    while s != b_semi and fifths_dist < 12:
        s = (s + 7) % 12
        fifths_dist += 1

    fourths_dist = 0
    s = a_semi
    while s != b_semi and fourths_dist < 12:
        s = (s + 5) % 12
        fourths_dist += 1

    step = 7 if fifths_dist <= fourths_dist else 5
    steps = fifths_dist if step == 7 else fourths_dist

    path: list[tuple[str, str]] = []
    current = a_semi
    for _ in range(steps):
        next_semi = (current + step) % 12
        next_key = _NOTE_NAMES[next_semi]
        # Add V-I cadence at each step
        v_of_next = _NOTE_NAMES[(next_semi + 7) % 12]
        path.append((v_of_next, "dom7"))
        path.append((next_key, "maj"))
        current = next_semi

    return path


def direct_modulation(
    key_a: str,
    key_b: str,
) -> list[tuple[str, str]]:
    """Generate a direct (truck-driver) modulation — abrupt key change.

    No pivot chord, no preparation. Just slam into the new key with a
    V-I cadence. Used in pop music when you need that energy boost for
    the final chorus. Bon Jovi approved.

    Args:
        key_a: Starting key root.
        key_b: Target key root.

    Returns:
        Short progression: I in old key, then V7-I in new key.
    """
    b_semi = _semi(key_b)
    v_of_b = _NOTE_NAMES[(b_semi + 7) % 12]
    return [(key_a, "maj"), (v_of_b, "dom7"), (key_b, "maj")]


def pivot_modulation(
    key_a: str,
    key_b: str,
    mode_a: str = "major",
    mode_b: str = "major",
) -> list[tuple[str, str]]:
    """Generate a smooth modulation via a pivot chord.

    Finds a chord common to both keys and uses it as the bridge.
    The smoothest type of modulation — the listener barely notices
    the key change happened.

    Args:
        key_a:  Starting key root.
        key_b:  Target key root.
        mode_a: Mode of starting key.
        mode_b: Mode of target key.

    Returns:
        Progression: tonic A → pivot chord → V7 of B → tonic B.
    """
    pivots = find_pivot_chords(key_a, key_b, mode_a, mode_b)
    b_semi = _semi(key_b)
    v_of_b = _NOTE_NAMES[(b_semi + 7) % 12]

    if pivots:
        pivot = pivots[0]  # use the first common chord
        return [(key_a, "maj"), pivot, (v_of_b, "dom7"), (key_b, "maj")]
    else:
        # No common chords — fall back to direct modulation
        return direct_modulation(key_a, key_b)


def parse_roman(numeral: str, key: str = "C") -> tuple[str, str]:
    """Parse a Roman numeral chord symbol into (root, shape).

    Handles uppercase (major), lowercase (minor), diminished (o/dim),
    augmented (+), seventh chords (7), and applied chords (V/V).

    Examples:
        parse_roman('V7', 'C')    → ('G', 'dom7')
        parse_roman('ii', 'C')    → ('D', 'min')
        parse_roman('bVI', 'C')   → ('Ab', 'maj')
        parse_roman('viio', 'C')  → ('B', 'dim')
        parse_roman('V/V', 'C')   → ('D', 'dom7')

    Args:
        numeral: Roman numeral string.
        key:     Key root.

    Returns:
        (root, shape) tuple.
    """
    key_semi = _semi(key)
    original = numeral

    # Handle applied chords: V/V, vii/ii, etc
    if "/" in numeral:
        parts = numeral.split("/")
        # Resolve the target chord first
        target_root, _ = parse_roman(parts[1], key)
        # Then parse the applied chord relative to that target
        return parse_roman(parts[0], target_root)

    # Handle accidentals
    flat = False
    sharp = False
    if numeral.startswith("b"):
        flat = True
        numeral = numeral[1:]
    elif numeral.startswith("#"):
        sharp = True
        numeral = numeral[1:]

    # Extract quality suffix
    suffix = ""
    base = numeral
    for s in [
        "o7",
        "dim7",
        "maj7",
        "min7",
        "dom7",
        "7",
        "o",
        "dim",
        "+",
        "aug",
        "sus4",
        "sus2",
        "9",
        "min9",
        "maj9",
    ]:
        if numeral.endswith(s):
            suffix = s
            base = numeral[: -len(s)]
            break

    # Find degree
    degree_semi = None
    is_minor = base == base.lower() and base != ""
    upper_base = base.upper()

    for roman in ["VII", "III", "II", "IV", "VI", "I", "V"]:
        if upper_base == roman:
            degree_semi = _ROMAN_TO_DEGREE[roman]
            break

    if degree_semi is None:
        raise ValueError(f"Cannot parse Roman numeral {original!r}")

    # Apply accidentals
    if flat:
        degree_semi = (degree_semi - 1) % 12
    elif sharp:
        degree_semi = (degree_semi + 1) % 12

    root = _NOTE_NAMES[(key_semi + degree_semi) % 12]

    # Determine shape
    if suffix in ("o7", "dim7"):
        shape = "dim7"
    elif suffix in ("o", "dim"):
        shape = "dim"
    elif suffix in ("+", "aug"):
        shape = "aug"
    elif suffix == "maj7":
        shape = "maj7"
    elif suffix == "min7":
        shape = "min7"
    elif suffix == "dom7":
        shape = "dom7"
    elif suffix == "7":
        shape = "dom7" if not is_minor else "min7"
    elif suffix == "9":
        shape = "dom9"
    elif suffix == "min9":
        shape = "min9"
    elif suffix == "maj9":
        shape = "maj9"
    elif suffix == "sus4":
        shape = "sus4"
    elif suffix == "sus2":
        shape = "sus2"
    elif is_minor:
        shape = "min"
    else:
        shape = "maj"

    return (root, shape)


def progression_from_roman(
    numerals: list[str],
    key: str = "C",
) -> list[tuple[str, str]]:
    """Convert a list of Roman numerals to a chord progression.

    Enables writing progressions in analysis notation and getting
    concrete chords in any key. The universal language of harmony.

    Args:
        numerals: List of Roman numeral strings.
        key:      Key root.

    Returns:
        List of (root, shape) tuples.

    Examples:
        >>> progression_from_roman(['I', 'IV', 'V7', 'I'], 'C')
        [('C', 'maj'), ('F', 'maj'), ('G', 'dom7'), ('C', 'maj')]
    """
    return [parse_roman(n, key) for n in numerals]


def classify_interval(semitones: int) -> str:
    """Classify an interval as perfect consonance, imperfect consonance, or dissonance.

    The backbone of counterpoint rules — whether two notes sound stable,
    pleasant, or tense determines where they can appear in the texture.

    Args:
        semitones: Interval in semitones (mod 12).

    Returns:
        'perfect', 'imperfect', or 'dissonant'.
    """
    s = abs(semitones) % 12
    if s in _PERFECT_CONSONANCES:
        return "perfect"
    elif s in _IMPERFECT_CONSONANCES:
        return "imperfect"
    else:
        return "dissonant"


# ---------------------------------------------------------------------------
# Chord voicing library (v48.0)
# ---------------------------------------------------------------------------


def rootless_a(
    root: str,
    shape: str = "dom7",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate a Bill Evans 'A' rootless voicing (3rd on bottom).

    The rootless voicing omits the root (the bass player has it) and
    stacks the 3rd, 7th, and upper extensions. The 'A' form puts the
    3rd in the lowest position. Evans built modern jazz piano on this.

    Args:
        root:     Chord root.
        shape:    Chord quality (dom7, maj7, min7).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the rootless A voicing.
    """
    k = _semi(root)
    if shape in ("dom7", "dom9"):
        # 3, 7, 9, 13 → intervals: 4, 10, 14, 21
        intervals = [4, 10, 14, 21]
    elif shape in ("maj7", "maj9"):
        # 3, 7, 9 → intervals: 4, 11, 14
        intervals = [4, 11, 14]
    elif shape in ("min7", "min9"):
        # b3, 7, 9, 11 → intervals: 3, 10, 14, 17
        intervals = [3, 10, 14, 17]
    else:
        intervals = list(_CHORD_SEMI.get(shape, [0, 4, 7]))[1:]  # drop root
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def rootless_b(
    root: str,
    shape: str = "dom7",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate a Bill Evans 'B' rootless voicing (7th on bottom).

    The complement of the 'A' voicing — the 7th sits in the bass
    register with the 3rd on top. Alternating A and B voicings in a
    ii-V-I creates smooth voice leading without the pianist ever
    touching the root. Pure Evans magic.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the rootless B voicing.
    """
    k = _semi(root)
    if shape in ("dom7", "dom9"):
        # 7, 9, 3(+12), 13 → intervals: 10, 14, 16, 21
        intervals = [10, 14, 16, 21]
    elif shape in ("maj7", "maj9"):
        # 7, 9, 3(+12) → intervals: 11, 14, 16
        intervals = [11, 14, 16]
    elif shape in ("min7", "min9"):
        # 7, 9, b3(+12), 5(+12) → intervals: 10, 14, 15, 19
        intervals = [10, 14, 15, 19]
    else:
        semis = list(_CHORD_SEMI.get(shape, [0, 4, 7]))
        intervals = semis[1:] + [semis[0] + 12] if len(semis) > 1 else semis
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def quartal_voicing(
    root: str,
    octave: int = 3,
    duration: float = 4.0,
    layers: int = 4,
) -> list[Note]:
    """Generate a McCoy Tyner-style quartal voicing (stacked perfect 4ths).

    Quartal harmony replaces tertian (3rd-based) stacking with perfect
    4ths. The sound is open, ambiguous, and modern — neither clearly
    major nor minor. Tyner drove Coltrane's quartets with these.

    Args:
        root:     Starting note.
        octave:   Base octave.
        duration: Note duration.
        layers:   Number of stacked 4ths (default 4).

    Returns:
        List of Notes in stacked 4ths.
    """
    k = _semi(root)
    return [
        Note(
            _NOTE_NAMES[(k + i * 5) % 12],
            octave + (k + i * 5) // 12,
            duration,
        )
        for i in range(layers)
    ]


def stride_voicing(
    root: str,
    shape: str = "maj",
    octave: int = 3,
    duration: float = 1.0,
) -> list[Note]:
    """Generate a stride piano voicing (low root then mid-register chord).

    Stride alternates: beat 1 = root (or root+5th) in the bass,
    beat 2 = chord in the middle register. The left-hand bounce
    that powered ragtime, early jazz, and Thelonious Monk.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Bass octave for the root.
        duration: Duration per hit (root and chord each get this).

    Returns:
        List of Notes: [bass_root, chord_tone_1, chord_tone_2, ...].
    """
    k = _semi(root)
    semis = _CHORD_SEMI.get(shape, [0, 4, 7])
    bass = [Note(root, octave, duration)]
    chord_notes = [Note(_NOTE_NAMES[(k + s) % 12], octave + 1, duration) for s in semis]
    return bass + chord_notes


# ---------------------------------------------------------------------------
# Harmonic analysis (v50.0)
# ---------------------------------------------------------------------------


def functional_analysis(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[dict]:
    """Analyze each chord's function (tonic, subdominant, dominant).

    Returns a Roman numeral and functional label for each chord in
    the progression. The kind of analysis a theory professor puts
    on the blackboard — but automated.

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of dicts with keys: root, shape, roman, function.
    """
    key_semi = _semi(key)
    # Diatonic degrees → Roman numerals (major key)
    degree_roman_major = {
        0: "I",
        2: "ii",
        4: "iii",
        5: "IV",
        7: "V",
        9: "vi",
        11: "viio",
    }
    # Functional groups
    tonic_degrees = {0, 4, 9}  # I, iii, vi
    subdominant_degrees = {2, 5}  # ii, IV
    dominant_degrees = {7, 11}  # V, viio

    result = []
    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12
        roman = degree_roman_major.get(degree, f"?({degree})")

        if degree in tonic_degrees:
            func = "T"
        elif degree in subdominant_degrees:
            func = "S"
        elif degree in dominant_degrees:
            func = "D"
        else:
            func = "chromatic"

        result.append(
            {
                "root": root,
                "shape": shape,
                "roman": roman,
                "function": func,
            }
        )

    return result


def detect_cadences(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[dict]:
    """Detect cadences in a chord progression.

    Scans consecutive chord pairs for the four standard cadence types:
    - Authentic (V→I): the strongest resolution in tonal music
    - Half (→V): suspension of resolution, "to be continued"
    - Plagal (IV→I): the "Amen" cadence
    - Deceptive (V→vi): the bait-and-switch that makes listeners gasp

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of dicts: {position, type, chords}.
    """
    key_semi = _semi(key)
    cadences = []

    for i in range(len(progression) - 1):
        r1_semi = (_semi(progression[i][0]) - key_semi) % 12
        r2_semi = (_semi(progression[i + 1][0]) - key_semi) % 12

        if r1_semi == 7 and r2_semi == 0:
            cadences.append(
                {
                    "position": i,
                    "type": "authentic",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r2_semi == 7:
            cadences.append(
                {
                    "position": i,
                    "type": "half",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r1_semi == 5 and r2_semi == 0:
            cadences.append(
                {
                    "position": i,
                    "type": "plagal",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r1_semi == 7 and r2_semi == 9:
            cadences.append(
                {
                    "position": i,
                    "type": "deceptive",
                    "chords": (progression[i], progression[i + 1]),
                }
            )

    return cadences


def detect_key(
    progression: list[tuple[str, str]],
) -> str:
    """Estimate the key of a chord progression by pitch-class frequency.

    Counts how often each pitch class appears as a chord root and
    matches against major-key diatonic sets. The key whose diatonic
    set best covers the progression roots wins.

    Args:
        progression: List of (root, shape) tuples.

    Returns:
        Estimated key root (e.g. 'C', 'G').
    """
    root_counts: list[int] = [0] * 12
    for root, _ in progression:
        root_counts[_semi(root)] += 1

    major_intervals = _SCALE_INTERVALS["major"]
    best_key = 0
    best_score = -1

    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        # Tiebreaker: prefer key whose root appears most often
        if score > best_score or (
            score == best_score and root_counts[candidate] > root_counts[best_key]
        ):
            best_score = score
            best_key = candidate

    return _NOTE_NAMES[best_key]


def list_scales() -> list[str]:
    """Return all available scale names, sorted alphabetically.

    Returns:
        Sorted list of scale name strings.
    """
    return sorted(_SCALE_INTERVALS.keys())


def scale_search(pitches: list[str]) -> list[str]:
    """Find scales that contain all given pitch classes.

    Useful for: "I'm using these notes — what scale am I in?"
    The reverse lookup every improviser needs.

    Args:
        pitches: List of note names (e.g. ['C', 'E', 'G', 'Bb']).

    Returns:
        List of scale names that contain all given pitch classes
        (assumes C root — transpose mentally for other keys).
    """
    target_pcs = {_semi(p) for p in pitches}
    matches = []
    for name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = set(intervals)
        if target_pcs.issubset(scale_pcs):
            matches.append(name)
    return sorted(matches)


def scale_brightness(name: str) -> float:
    """Rank a scale from dark (0.0) to bright (1.0) by interval content.

    Brightness correlates with how many raised/sharp degrees a scale has.
    Lydian is the brightest mode, Locrian the darkest. This metric
    extends that concept to all scales in the atlas.

    Args:
        name: Scale name.

    Returns:
        Brightness score in [0.0, 1.0].

    Raises:
        ValueError: If scale name is not recognized.
    """
    if name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {name!r}")
    intervals = _SCALE_INTERVALS[name]
    # Brightness = average interval position relative to chromatic max
    # Higher average = brighter
    if not intervals:
        return 0.0
    avg = sum(intervals) / len(intervals)
    # Normalize: max possible avg for 7-note scale ≈ 8.14 (lydian)
    return round(min(avg / 8.5, 1.0), 3)


def scale_modes(name: str) -> list[tuple[str, list[int]]]:
    """Generate all rotational modes of a scale.

    Each mode starts on a different degree and rotates the intervals.
    The 7 modes of the major scale (Ionian through Locrian) are the
    most famous example, but every scale has modes.

    Args:
        name: Scale name.

    Returns:
        List of (mode_label, intervals) tuples.

    Raises:
        ValueError: If scale name is not recognized.
    """
    if name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {name!r}")
    intervals = _SCALE_INTERVALS[name]
    modes = []
    for i in range(len(intervals)):
        rotated = [(iv - intervals[i]) % 12 for iv in intervals]
        rotated.sort()
        modes.append((f"{name}_mode_{i + 1}", rotated))
    return modes


# ---------------------------------------------------------------------------
# Chord substitution engine (v60.0)
# ---------------------------------------------------------------------------


def suggest_substitutions(
    root: str,
    shape: str,
    key: str = "C",
) -> list[tuple[str, str, str]]:
    """Suggest chord substitutions for a given chord.

    Returns a list of alternative chords with the substitution type.
    Each result is (root, shape, substitution_type).

    Substitution types:
    - tritone_sub: replace dom7 with dom7 a tritone away
    - related_ii: add the ii chord that precedes a dominant
    - modal_interchange: borrow from parallel minor/major
    - relative: substitute with the relative major/minor

    Args:
        root:  Chord root.
        shape: Chord quality.
        key:   Key context.

    Returns:
        List of (root, shape, sub_type) tuples.
    """
    key_semi = _semi(key)
    root_semi = _semi(root)
    degree = (root_semi - key_semi) % 12
    subs: list[tuple[str, str, str]] = []

    # Tritone substitution (dom7 → dom7 a tritone away)
    if "dom" in shape or "7" in shape:
        tri_semi = (root_semi + 6) % 12
        subs.append((_NOTE_NAMES[tri_semi], "dom7", "tritone_sub"))

    # Related ii (prepend ii-V before a dominant)
    if degree == 7:  # V chord
        ii_semi = (key_semi + 2) % 12
        subs.append((_NOTE_NAMES[ii_semi], "min7", "related_ii"))

    # Modal interchange (borrow from parallel minor)
    if shape in ("maj", "maj7"):
        minor_semi = (root_semi + 0) % 12
        subs.append((_NOTE_NAMES[minor_semi], "min", "modal_interchange"))
    elif shape in ("min", "min7"):
        subs.append((_NOTE_NAMES[root_semi], "maj", "modal_interchange"))

    # Relative major/minor
    if shape in ("maj", "maj7"):
        rel_semi = (root_semi + 9) % 12  # relative minor
        subs.append((_NOTE_NAMES[rel_semi], "min", "relative"))
    elif shape in ("min", "min7"):
        rel_semi = (root_semi + 3) % 12  # relative major
        subs.append((_NOTE_NAMES[rel_semi], "maj", "relative"))

    return subs


def reharmonize(
    progression: list[tuple[str, str]],
    key: str = "C",
    style: str = "jazz",
) -> list[tuple[str, str]]:
    """Reharmonize a chord progression by applying substitutions.

    Takes a simple progression and adds color: tritone subs on
    dominants, related ii chords, modal interchange. The difference
    between a hymnal and a jazz standard.

    Styles:
    - 'jazz': tritone subs + related ii's on all dominants
    - 'modal': modal interchange on all diatonic chords
    - 'simple': relative major/minor swaps only

    Args:
        progression: Original (root, shape) progression.
        key:         Key context.
        style:       Substitution strategy.

    Returns:
        Reharmonized progression.
    """
    key_semi = _semi(key)
    result: list[tuple[str, str]] = []

    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12

        if style == "jazz":
            if degree == 7 and ("dom" in shape or "7" in shape):
                # Add related ii before V
                ii_semi = (root_semi - 5) % 12
                result.append((_NOTE_NAMES[ii_semi], "min7"))
            # Tritone sub on secondary dominants
            if "dom" in shape and degree != 7:
                tri_semi = (root_semi + 6) % 12
                result.append((_NOTE_NAMES[tri_semi], "dom7"))
            else:
                result.append((root, shape))

        elif style == "modal":
            if shape in ("maj", "maj7"):
                result.append((root, "min"))
            elif shape in ("min", "min7"):
                result.append((root, "maj"))
            else:
                result.append((root, shape))

        else:  # simple
            if shape in ("maj", "maj7"):
                rel = _NOTE_NAMES[(root_semi + 9) % 12]
                result.append((rel, "min"))
            elif shape in ("min", "min7"):
                rel = _NOTE_NAMES[(root_semi + 3) % 12]
                result.append((rel, "maj"))
            else:
                result.append((root, shape))

    return result


# ---------------------------------------------------------------------------
# Chord voicing constraints (v72.0)
# ---------------------------------------------------------------------------


def optimal_voicing(
    root: str,
    shape: str,
    voices: int = 4,
    max_span: int = 24,
    prefer_close: bool = True,
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Find the optimal voicing for a chord under constraints.

    A constraint-satisfaction approach: spread chord tones across
    the specified number of voices while respecting span limits and
    close/open position preference.

    Args:
        root:         Chord root.
        shape:        Chord quality.
        voices:       Number of voices (3-6).
        max_span:     Maximum semitone span from lowest to highest note.
        prefer_close: True = close position, False = open (spread).
        octave:       Base octave for lowest voice.
        duration:     Note duration.

    Returns:
        List of Notes forming the constrained voicing.
    """
    k = _semi(root)
    semis = list(_CHORD_SEMI.get(shape, [0, 4, 7]))

    # Build candidate pitches across octaves
    candidates: list[int] = []
    for o in range(octave, octave + 3):
        for s in semis:
            candidates.append(k + s + o * 12)
    candidates.sort()

    # Pick `voices` notes within max_span
    best: list[int] = []
    best_score = -1

    for start_idx in range(len(candidates)):
        bass = candidates[start_idx]
        group = [bass]
        for c in candidates[start_idx + 1 :]:
            if c - bass > max_span:
                break
            group.append(c)

        if len(group) < voices:
            continue

        # Score: prefer close or open position
        # Try all combinations of `voices` from `group`
        # For efficiency, just take the first `voices` (close) or spread evenly (open)
        if prefer_close:
            selected = group[:voices]
        else:
            step = max(1, len(group) // voices)
            selected = [group[i * step] for i in range(min(voices, len(group)))]

        if len(selected) < voices:
            continue

        span = selected[-1] - selected[0]
        # Score close voicings higher when prefer_close, wider when not
        if prefer_close:
            score = max_span - span
        else:
            score = span

        if score > best_score:
            best_score = score
            best = selected

    if not best:
        # Fallback: simple stacking
        best = [
            (k + semis[i % len(semis)] + (octave + i // len(semis)) * 12) for i in range(voices)
        ]

    return [Note(_NOTE_NAMES[p % 12], p // 12, duration) for p in best]


def smooth_voicings(
    progression: list[tuple[str, str]],
    voices: int = 4,
    max_span: int = 24,
    octave: int = 3,
    duration: float = 4.0,
) -> list[list[Note]]:
    """Generate smooth voice-led voicings for a progression under constraints.

    Each chord is voiced to minimize total movement from the previous voicing
    while respecting span and voice count constraints.

    Args:
        progression: List of (root, shape) tuples.
        voices:      Number of voices.
        max_span:    Maximum span per voicing.
        octave:      Base octave.
        duration:    Duration per chord.

    Returns:
        List of voicing note-lists, one per chord.
    """
    if not progression:
        return []

    result: list[list[Note]] = []
    prev: list[int] | None = None

    for root, shape in progression:
        voicing = optimal_voicing(root, shape, voices, max_span, True, octave, duration)
        current = [_semi(str(n.pitch)) + n.octave * 12 for n in voicing]

        if prev is not None:
            # Try to minimize movement by octave-shifting notes
            adjusted: list[int] = []
            for i, c in enumerate(current):
                target = prev[i] if i < len(prev) else c
                # Find the octave placement closest to target
                pc = c % 12
                best_abs = c
                best_dist = abs(c - target)
                for o in range(octave, octave + 3):
                    candidate = pc + o * 12
                    if abs(candidate - target) < best_dist:
                        best_dist = abs(candidate - target)
                        best_abs = candidate
                adjusted.append(best_abs)
            adjusted.sort()
            voicing = [Note(_NOTE_NAMES[p % 12], p // 12, duration) for p in adjusted]
            prev = adjusted
        else:
            prev = current

        result.append(voicing)

    return result


def enharmonic_equivalent(note: str) -> str:
    """Return the enharmonic equivalent of a note name.

    C# ↔ Db, F# ↔ Gb, etc. Notes without common enharmonics
    (like C, D, G) return themselves.

    Args:
        note: Note name.

    Returns:
        Enharmonic spelling.
    """
    return _ENHARMONIC_MAP.get(note, note)


def key_signature_accidentals(key: str) -> list[str]:
    """Return the sharps or flats in a key signature.

    Args:
        key: Key name (e.g. 'G', 'Bb', 'F#').

    Returns:
        List of accidentals (e.g. ['F#'] for G major, ['Bb', 'Eb'] for Bb major).
    """
    return list(_KEY_SIGNATURES.get(key, []))


def respell_note(note: str, key: str) -> str:
    """Pick the enharmonic spelling that fits the key signature.

    In Ab major, use Db (not C#). In A major, use C# (not Db).
    Context-aware spelling is what separates readable notation from chaos.

    Args:
        note: Note name to potentially respell.
        key:  Key context.

    Returns:
        The spelling that fits the key.
    """
    accidentals = key_signature_accidentals(key)
    alt = enharmonic_equivalent(note)

    # Prefer the spelling that appears in the key's accidentals
    if note in accidentals:
        return note
    if alt in accidentals:
        return alt

    # Prefer flats in flat keys, sharps in sharp keys
    has_flats = any("b" in a for a in accidentals)
    has_sharps = any("#" in a for a in accidentals)

    if has_flats and "b" in alt and "#" in note:
        return alt
    if has_sharps and "#" in alt and "b" in note:
        return alt

    return note  # no change needed


# ---------------------------------------------------------------------------
# Interactive scale explorer (v94.0)
# ---------------------------------------------------------------------------


def suggest_scale(
    notes_so_far: list[str],
    key: str = "C",
) -> list[tuple[str, float]]:
    """Rank scales by how well they fit the notes played so far.

    The real-time improv advisor: "you've played C E G Bb — you're
    probably in mixolydian or blues."

    Args:
        notes_so_far: Pitch names played so far.
        key:          Key root for scale transposition.

    Returns:
        List of (scale_name, fit_score) sorted by score descending.
    """
    k = _semi(key)
    played_pcs = {(_semi(n) - k) % 12 for n in notes_so_far}
    if not played_pcs:
        return [(name, 1.0) for name in sorted(_SCALE_INTERVALS)[:5]]

    results: list[tuple[str, float]] = []
    for name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = set(intervals)
        if not scale_pcs:
            continue
        overlap = len(played_pcs & scale_pcs)
        outside = len(played_pcs - scale_pcs)
        score = overlap / len(played_pcs) - outside * 0.3
        score = max(0.0, min(1.0, score))
        results.append((name, round(score, 3)))

    results.sort(key=lambda x: -x[1])
    return results


def available_notes(
    key: str = "C",
    scale_name: str = "major",
) -> list[str]:
    """Return all pitches available in a scale, in order.

    Args:
        key:        Key root.
        scale_name: Scale name.

    Returns:
        List of note names in the scale.
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    if sname not in _SCALE_INTERVALS:
        return []
    k = _semi(key)
    return [_NOTE_NAMES[(k + iv) % 12] for iv in _SCALE_INTERVALS[sname]]


def avoid_notes(
    key: str = "C",
    scale_name: str = "major",
) -> list[str]:
    """Return all pitches NOT in a scale — the notes to avoid.

    Args:
        key:        Key root.
        scale_name: Scale name.

    Returns:
        List of note names outside the scale.
    """
    good = set(available_notes(key, scale_name))
    return [_NOTE_NAMES[i] for i in range(12) if _NOTE_NAMES[i] not in good]


def lookup_voicing(
    root: str,
    shape: str,
    position: int = 0,
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Retrieve a specific voicing from the database.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        position: Voicing index (0 = root position, 1+ = inversions/spreads).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes.
    """
    voicings = _VOICING_DB.get(shape, [[0, 4, 7]])
    idx = position % len(voicings)
    k = _semi(root)
    return [
        Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in voicings[idx]
    ]


def random_voicing(
    root: str,
    shape: str,
    octave: int = 3,
    duration: float = 4.0,
    seed: int | None = None,
) -> list[Note]:
    """Pick a random voicing from the database for variety.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        duration: Note duration.
        seed:     Random seed.

    Returns:
        List of Notes.
    """
    import random as _rng

    rng = _rng.Random(seed)
    voicings = _VOICING_DB.get(shape, [[0, 4, 7]])
    idx = rng.randint(0, len(voicings) - 1)
    return lookup_voicing(root, shape, idx, octave, duration)


# ---------------------------------------------------------------------------
# Harmonic field map (v97.0)
# ---------------------------------------------------------------------------


def harmonic_field(
    key: str = "C",
    mode: str = "major",
) -> list[dict]:
    """Return all diatonic chords with Roman numerals and functions.

    The harmonic field is the complete map of a key — every chord
    that belongs, what it's called, and what it does.

    Args:
        key:  Key root.
        mode: 'major' or 'minor' (aeolian).

    Returns:
        List of 7 dicts: {degree, roman, root, shape, function}.
    """
    k = _semi(key)
    if mode in ("minor", "aeolian"):
        intervals = _SCALE_INTERVALS.get("aeolian", [0, 2, 3, 5, 7, 8, 10])
        romans = ["i", "iio", "III", "iv", "v", "VI", "VII"]
        shapes = ["min", "dim", "maj", "min", "min", "maj", "maj"]
        funcs = ["T", "S", "T", "S", "D", "T", "D"]
    else:
        intervals = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
        romans = ["I", "ii", "iii", "IV", "V", "vi", "viio"]
        shapes = ["maj", "min", "min", "maj", "maj", "min", "dim"]
        funcs = ["T", "S", "T", "S", "D", "T", "D"]

    field: list[dict] = []
    for i in range(7):
        root_pc = (k + intervals[i]) % 12
        field.append(
            {
                "degree": i + 1,
                "roman": romans[i],
                "root": _NOTE_NAMES[root_pc],
                "shape": shapes[i],
                "function": funcs[i],
            }
        )
    return field


def chord_relationships(key: str = "C") -> dict[str, list[str]]:
    """Map which chords resolve to which in a key.

    Dominant → tonic, subdominant → dominant or tonic. The arrows
    on the theory professor's blackboard.

    Args:
        key: Key root.

    Returns:
        Dict mapping Roman numeral → list of resolution targets.
    """
    return {
        "I": [],  # tonic = home, resolves nowhere
        "ii": ["V", "viio"],
        "iii": ["vi", "IV"],
        "IV": ["V", "I", "viio"],
        "V": ["I", "vi"],  # authentic or deceptive
        "vi": ["ii", "IV"],
        "viio": ["I"],
    }


# ---------------------------------------------------------------------------
# Chord quality morphing (v103.0)
# ---------------------------------------------------------------------------


def morph_chord(
    from_chord: tuple[str, str],
    to_chord: tuple[str, str],
    steps: int = 4,
    octave: int = 3,
    duration: float = 4.0,
) -> list[list[Note]]:
    """Morph from one chord to another by gradually changing pitch classes.

    At each step, one pitch class from the source chord moves by a
    semitone toward the target chord. The result is a smooth
    transformation — the harmonic equivalent of a dissolve cut.

    Args:
        from_chord: Starting (root, shape).
        to_chord:   Ending (root, shape).
        steps:      Number of intermediate chords.
        octave:     Base octave.
        duration:   Duration per chord.

    Returns:
        List of voicings (each a list of Notes), from source to target.
    """
    from_k = _semi(from_chord[0])
    to_k = _semi(to_chord[0])
    from_semis = [(from_k + s) % 12 for s in _CHORD_SEMI.get(from_chord[1], [0, 4, 7])]
    to_semis = [(to_k + s) % 12 for s in _CHORD_SEMI.get(to_chord[1], [0, 4, 7])]

    # Pad shorter chord to match length
    max_voices = max(len(from_semis), len(to_semis))
    while len(from_semis) < max_voices:
        from_semis.append(from_semis[-1])
    while len(to_semis) < max_voices:
        to_semis.append(to_semis[-1])

    result: list[list[Note]] = []
    for step in range(steps + 1):
        frac = step / max(steps, 1)
        current: list[int] = []
        for f, t in zip(from_semis, to_semis):
            # Linear interpolation in pitch-class space (shortest path)
            diff = (t - f + 6) % 12 - 6  # signed shortest distance
            c = (f + round(diff * frac)) % 12
            current.append(c)

        voicing = [Note(_NOTE_NAMES[pc], octave, duration) for pc in current]
        result.append(voicing)

    return result


def chord_interpolation(
    progression: list[tuple[str, str]],
    steps_between: int = 2,
    octave: int = 3,
    duration: float = 2.0,
) -> list[list[Note]]:
    """Insert morphing intermediate chords between each chord in a progression.

    Makes abrupt chord changes smoother by adding gradual transitions.

    Args:
        progression:   Chord progression.
        steps_between: Intermediate chords between each pair.
        octave:        Base octave.
        duration:      Duration per intermediate chord.

    Returns:
        List of voicings with morphing intermediates inserted.
    """
    if len(progression) < 2:
        return [
            [
                Note(_NOTE_NAMES[(_semi(r) + s) % 12], octave, duration)
                for s in _CHORD_SEMI.get(sh, [0, 4, 7])
            ]
            for r, sh in progression
        ]

    result: list[list[Note]] = []
    for i in range(len(progression) - 1):
        morphed = morph_chord(progression[i], progression[i + 1], steps_between, octave, duration)
        result.extend(morphed[:-1])  # skip last to avoid duplication with next start

    # Add final chord
    last_r, last_s = progression[-1]
    last_k = _semi(last_r)
    result.append(
        [
            Note(_NOTE_NAMES[(last_k + s) % 12], octave, duration)
            for s in _CHORD_SEMI.get(last_s, [0, 4, 7])
        ]
    )

    return result


def format_chord(root: str, shape: str) -> str:
    """Format a (root, shape) tuple as a standard chord symbol.

    Args:
        root:  Chord root.
        shape: Chord quality.

    Returns:
        Standard chord symbol string (e.g. 'Cmaj7', 'Dm7', 'G7', 'F#dim').
    """
    suffix = _SHAPE_SYMBOLS.get(shape, shape)
    return f"{root}{suffix}"


def format_progression(
    progression: list[tuple[str, str]],
    separator: str = " | ",
) -> str:
    """Format a full progression as a readable chord chart line.

    Args:
        progression: List of (root, shape) tuples.
        separator:   String between chords.

    Returns:
        Formatted string (e.g. 'Cmaj7 | Dm7 | G7 | Cmaj7').
    """
    return separator.join(format_chord(r, s) for r, s in progression)


# ---------------------------------------------------------------------------
# Interval sequence analysis (v109.0)
# ---------------------------------------------------------------------------


def interval_sequence(notes: list[Note]) -> list[int]:
    """Extract the sequence of melodic intervals (in semitones) from a note list.

    Args:
        notes: Input melody.

    Returns:
        List of signed integers: positive = ascending, negative = descending.
    """
    result: list[int] = []
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        result.append(b - a)
    return result


def common_intervals(notes: list[Note], top_n: int = 5) -> list[tuple[int, int]]:
    """Find the most frequently used melodic intervals.

    Args:
        notes: Input melody.
        top_n: Number of top intervals to return.

    Returns:
        List of (interval_semitones, count) sorted by frequency.
    """
    seq = interval_sequence(notes)
    counts: dict[int, int] = {}
    for iv in seq:
        counts[iv] = counts.get(iv, 0) + 1
    sorted_intervals = sorted(counts.items(), key=lambda x: -x[1])
    return sorted_intervals[:top_n]


# ---------------------------------------------------------------------------
# Chord inversion analyzer (v113.0)
# ---------------------------------------------------------------------------


def detect_inversion(notes: list[Note], root: str, shape: str) -> int:
    """Detect which inversion a chord voicing is in.

    0 = root position (root is lowest), 1 = first inversion (3rd is lowest),
    2 = second inversion (5th is lowest), 3 = third inversion (7th is lowest).

    Args:
        notes: The chord voicing as Notes (lowest to highest).
        root:  Expected root of the chord.
        shape: Chord quality.

    Returns:
        Inversion number (0-3).
    """
    if not notes:
        return 0
    sounding = [n for n in notes if n.pitch is not None]
    if not sounding:
        return 0

    bass_pc = _semi(str(sounding[0].pitch))
    root_pc = _semi(root)
    semis = _CHORD_SEMI.get(shape, [0, 4, 7])
    chord_pcs = [(root_pc + s) % 12 for s in semis]

    for i, pc in enumerate(chord_pcs):
        if pc == bass_pc:
            return i
    return 0


def inversion_label(inversion: int) -> str:
    """Return a human-readable label for a chord inversion.

    Args:
        inversion: Inversion number (0-3).

    Returns:
        Label string.
    """
    labels = {0: "root position", 1: "1st inversion", 2: "2nd inversion", 3: "3rd inversion"}
    return labels.get(inversion, f"{inversion}th inversion")


def scale_degree(pitch: str, key: str = "C") -> int:
    """Return the scale degree of a pitch relative to a key (0-11 semitones).

    Args:
        pitch: Note name.
        key:   Key root.

    Returns:
        Interval in semitones from the key root.
    """
    return (_semi(pitch) - _semi(key)) % 12


def scale_degree_name(pitch: str, key: str = "C") -> str:
    """Return a human-readable scale degree name.

    Args:
        pitch: Note name.
        key:   Key root.

    Returns:
        Degree name string (e.g. "5", "b3 (minor 3rd)").
    """
    return _DEGREE_NAMES.get(scale_degree(pitch, key), "?")


# ---------------------------------------------------------------------------
# Chord tone filter (v117.0)
# ---------------------------------------------------------------------------


def chord_tones(root: str, shape: str) -> list[str]:
    """Return the pitch names of a chord's tones.

    Args:
        root:  Chord root.
        shape: Chord quality.

    Returns:
        List of pitch names in the chord.
    """
    k = _semi(root)
    return [_NOTE_NAMES[(k + s) % 12] for s in _CHORD_SEMI.get(shape, [0, 4, 7])]


def is_chord_tone(pitch: str, root: str, shape: str) -> bool:
    """Check if a pitch is a chord tone.

    Args:
        pitch: Note to check.
        root:  Chord root.
        shape: Chord quality.

    Returns:
        True if pitch is in the chord.
    """
    return pitch in chord_tones(root, shape) or _NOTE_NAMES[_semi(pitch)] in chord_tones(
        root, shape
    )


def filter_chord_tones(
    notes: list[Note],
    root: str,
    shape: str,
) -> list[Note]:
    """Filter a melody to only chord tones, replacing non-chord-tones with rests.

    Args:
        notes: Input melody.
        root:  Chord root.
        shape: Chord quality.

    Returns:
        Filtered note list (non-chord-tones become rests).
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is not None and is_chord_tone(str(n.pitch), root, shape):
            result.append(n)
        else:
            result.append(Note.rest(n.duration) if n.pitch is not None else n)
    return result


# ---------------------------------------------------------------------------
# Chord symbol parser (v125.0)
# ---------------------------------------------------------------------------


def parse_chord_symbol(symbol: str) -> tuple[str, str]:
    """Parse a standard chord symbol string into (root, shape).

    Handles real-world chord symbols: Cmaj7, Dm7, G7, F#m, Bbdim7,
    Asus4, E+, Am7b5, etc.

    Args:
        symbol: Chord symbol string.

    Returns:
        (root, shape) tuple.

    Raises:
        ValueError: If the symbol can't be parsed.
    """
    if not symbol:
        raise ValueError("Empty chord symbol")

    # Extract root (letter + optional # or b)
    root = symbol[0].upper()
    idx = 1
    if idx < len(symbol) and symbol[idx] in "#b":
        root += symbol[idx]
        idx += 1

    suffix = symbol[idx:]

    # Map suffixes to internal shapes — ordered longest-first to avoid partial matches
    _SYMBOL_MAP = [
        ("maj9", "maj9"),
        ("min9", "min9"),
        ("m9", "min9"),
        ("maj7", "maj7"),
        ("min7", "min7"),
        ("m7b5", "min7b5"),
        ("m7", "min7"),
        ("dim7", "dim7"),
        ("aug7", "aug7"),
        ("7#9", "dom7"),
        ("7b9", "dom7"),
        ("7", "dom7"),
        ("dim", "dim"),
        ("aug", "aug"),
        ("+", "aug"),
        ("sus4", "sus4"),
        ("sus2", "sus2"),
        ("m", "min"),
        ("min", "min"),
        ("9", "dom9"),
        ("6", "maj6"),
        ("", "maj"),
    ]

    for pattern, shape in _SYMBOL_MAP:
        if suffix == pattern:
            return (root, shape)

    # Fallback: treat unknown suffix as the shape itself
    return (root, suffix if suffix else "maj")


def parse_chord_symbols(text: str) -> list[tuple[str, str]]:
    """Parse a space-separated string of chord symbols.

    Args:
        text: e.g. "Cmaj7 Dm7 G7 Cmaj7"

    Returns:
        List of (root, shape) tuples.
    """
    return [parse_chord_symbol(s.strip()) for s in text.split() if s.strip()]


# ---------------------------------------------------------------------------
# Chord Voicing AI — voice_progression (v133.0)
# ---------------------------------------------------------------------------


def voice_progression(
    progression: list[tuple[str, str]],
    style: str = "classical",
    octave: int = 3,
    duration: float = 4.0,
) -> list[list[Note]]:
    """Produce pianistic voicings for a progression that minimize hand movement.

    Unlike generate_chord_voicing (single chord) or smooth_voicings
    (constraint-based), this uses style-specific intelligence:

    Styles:
        'classical': Close position, common-tone retention, smooth bass.
            Root always in bass. Upper voices move by step when possible.
        'jazz_rootless': Alternating rootless A/B voicings for smooth
            voice leading. No root (bass player handles it). The Bill
            Evans approach.
        'quartal': McCoy Tyner-style stacked 4ths. Root-anchored but
            harmonically ambiguous. Best for modal jazz.
        'drop2': Drop-2 voicings (second-highest note dropped an octave).
            The standard jazz guitar voicing — wide spread, clear.
        'shell': 2-note shell voicings (root + 3rd or root + 7th).
            Minimal, rhythmic comping. Thelonious Monk territory.

    Args:
        progression: List of (root, shape) tuples.
        style:       Voicing style name.
        octave:      Base octave.
        duration:    Duration per chord.

    Returns:
        List of Note lists, one voicing per chord.

    Example::

        >>> prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7")]
        >>> voicings = voice_progression(prog, style="jazz_rootless")
        >>> len(voicings)
        3
    """
    if not progression:
        return []

    result: list[list[Note]] = []

    if style == "classical":
        # Close position with common-tone retention
        prev_notes: list[int] | None = None
        for root, shape in progression:
            k = _semi(root)
            semis = list(_CHORD_SEMI.get(shape, [0, 4, 7]))
            # Root in bass
            bass = k + octave * 12
            # Upper voices: close position above bass
            upper = [k + s + (octave + 1) * 12 for s in semis]

            if prev_notes is not None:
                # Retain common tones, minimize movement for others
                adjusted = [bass]
                for u in upper[1:]:  # skip root duplication
                    pc = u % 12
                    # Find closest octave placement to previous voice
                    best = u
                    best_dist = 999
                    for prev in prev_notes:
                        for o in range(octave, octave + 3):
                            cand = pc + o * 12
                            if abs(cand - prev) < best_dist:
                                best_dist = abs(cand - prev)
                                best = cand
                    adjusted.append(best)
                adjusted.sort()
                notes = [
                    Note(_NOTE_NAMES[p % 12], max(2, min(6, p // 12)), duration) for p in adjusted
                ]
                prev_notes = adjusted
            else:
                all_pitches = sorted([bass] + upper[1:])
                notes = [
                    Note(_NOTE_NAMES[p % 12], max(2, min(6, p // 12)), duration)
                    for p in all_pitches
                ]
                prev_notes = all_pitches
            result.append(notes)

    elif style == "jazz_rootless":
        # Alternate A and B rootless voicings for smooth leading
        for i, (root, shape) in enumerate(progression):
            if i % 2 == 0:
                notes = rootless_a(root, shape, octave, duration)
            else:
                notes = rootless_b(root, shape, octave, duration)
            result.append(notes)

    elif style == "quartal":
        for root, shape in progression:
            notes = quartal_voicing(root, octave, duration, layers=4)
            result.append(notes)

    elif style == "drop2":
        prev_abs: list[int] | None = None
        for root, shape in progression:
            notes = generate_chord_voicing(root, shape, octave, "drop2", duration)
            current = [_semi(str(n.pitch)) + n.octave * 12 for n in notes]
            if prev_abs is not None:
                # Minimize movement by shifting octaves
                adjusted = []
                for j, c in enumerate(current):
                    pc = c % 12
                    target = prev_abs[j] if j < len(prev_abs) else c
                    best = c
                    best_dist = abs(c - target)
                    for o in range(octave, octave + 3):
                        cand = pc + o * 12
                        if abs(cand - target) < best_dist:
                            best_dist = abs(cand - target)
                            best = cand
                    adjusted.append(best)
                adjusted.sort()
                notes = [
                    Note(_NOTE_NAMES[p % 12], max(2, min(6, p // 12)), duration) for p in adjusted
                ]
                prev_abs = adjusted
            else:
                prev_abs = current
            result.append(notes)

    elif style == "shell":
        for root, shape in progression:
            k = _semi(root)
            semis = _CHORD_SEMI.get(shape, [0, 4, 7])
            # Root + 3rd (or closest chord tone after root)
            root_note = Note(_NOTE_NAMES[k], octave, duration)
            if len(semis) >= 2:
                # For 7th chords: root + 7th (the shell)
                if len(semis) >= 4:
                    guide = semis[3]  # 7th
                else:
                    guide = semis[1]  # 3rd
                guide_note = Note(
                    _NOTE_NAMES[(k + guide) % 12],
                    octave + (k + guide) // 12,
                    duration,
                )
                result.append([root_note, guide_note])
            else:
                result.append([root_note])

    else:
        raise ValueError(
            f"Unknown voicing style {style!r}. Choose: classical, "
            "jazz_rootless, quartal, drop2, shell"
        )

    return result
