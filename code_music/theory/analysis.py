"""theory.analysis — analysis, statistics, fingerprinting, similarity, detection."""

from __future__ import annotations

from ._core import (
    Note,
    _CHORD_SEMI,
    _DISSONANCES,
    _FUNCTION_MAP,
    _GENRE_TEMPLATES,
    _INSTRUMENT_RANGES,
    _INTERVAL_NAMES,
    _NOTE_NAMES,
    _QUALITY_MAP,
    _ROMAN,
    _SCALE_INTERVALS,
    _motion_type,
    _semi,
)
from .harmony import detect_cadences, detect_key, functional_analysis


def analyze_harmony(song, key: str | None = None) -> list[dict]:
    """Analyze a song's chord progression with Roman numeral analysis.

    Finds all chords in the song, assigns Roman numerals relative to
    the detected (or specified) key, and labels harmonic function
    (tonic, subdominant, dominant).

    Args:
        song: Song object.
        key:  Key root (e.g. 'C'). If None, uses song.key_sig or detect_key().

    Returns:
        List of dicts with: beat, root, shape, roman, quality, function.

    Example::

        analysis = analyze_harmony(song)
        for a in analysis:
            print(f"Beat {a['beat']}: {a['roman']}{a['quality']} ({a['function']})")
        # Beat 0: IIm7 (supertonic)
        # Beat 4: V7 (dominant)
        # Beat 8: IM7 (tonic)
    """
    from ..engine import Chord

    # Determine key
    if key is None:
        key = getattr(song, "key_sig", "C")
        if key and len(key) > 1 and key[-1] == "m":
            key = key[:-1]  # strip minor indicator for root
    key_semi = _semi(key) if key else 0

    # Extract chords
    chords: list[tuple[float, str, str]] = []
    for track in song.tracks:
        pos = 0.0
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Chord):
                chords.append(
                    (
                        pos,
                        beat.event.root,
                        beat.event.shape if isinstance(beat.event.shape, str) else "maj",
                    )
                )
            if beat.event:
                pos += beat.event.duration

    # Analyze each chord
    result = []
    for beat_pos, root, shape in sorted(chords):
        root_semi = _semi(root)
        interval = (root_semi - key_semi) % 12
        roman = _ROMAN.get(interval, "?")
        quality = _QUALITY_MAP.get(shape, shape)

        # Lowercase roman for minor chords
        if shape in ("min", "min7", "min7b5", "dim", "dim7", "min9"):
            roman = roman.lower()

        func = _FUNCTION_MAP.get(interval, "chromatic")

        result.append(
            {
                "beat": beat_pos,
                "root": root,
                "shape": shape,
                "roman": roman,
                "quality": quality,
                "function": func,
            }
        )

    return result


def consonance_score(notes: list[Note]) -> float:
    """Measure harmonic consonance of simultaneous/sequential notes.

    Rates intervals: unison/octave=1.0, fifth=0.9, fourth=0.8,
    third/sixth=0.7, second/seventh=0.3, tritone=0.1.

    Args:
        notes: List of Notes (analyzed pairwise).

    Returns:
        Average consonance score (0.0-1.0).
    """
    _CONSONANCE = {
        0: 1.0,
        1: 0.3,
        2: 0.3,
        3: 0.7,
        4: 0.7,
        5: 0.8,
        6: 0.1,
        7: 0.9,
        8: 0.7,
        9: 0.7,
        10: 0.3,
        11: 0.3,
    }

    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return 1.0

    scores: list[float] = []
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i].pitch))
        b = _semi(str(pitched[i + 1].pitch))
        interval = abs(b - a) % 12
        scores.append(_CONSONANCE.get(interval, 0.5))

    return round(sum(scores) / len(scores), 3)


def count_pitch_classes(notes: list[Note]) -> dict[str, int]:
    """Count occurrences of each pitch class (ignoring octave).

    Args:
        notes: List of Notes.

    Returns:
        Dict mapping pitch name to count, sorted by frequency.
    """
    counts: dict[str, int] = {}
    for n in notes:
        if n.pitch is not None:
            pitch = str(n.pitch)
            counts[pitch] = counts.get(pitch, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def melodic_interval_histogram(notes: list[Note]) -> dict[str, int]:
    """Build a histogram of melodic interval sizes.

    Args:
        notes: List of Notes.

    Returns:
        Dict mapping interval name to count.
    """
    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return {}

    histogram: dict[str, int] = {}
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i].pitch)) + pitched[i].octave * 12
        b = _semi(str(pitched[i + 1].pitch)) + pitched[i + 1].octave * 12
        dist = abs(b - a) % 12
        name = _INTERVAL_NAMES.get(dist, f"{dist}st")
        histogram[name] = histogram.get(name, 0) + 1
    return dict(sorted(histogram.items(), key=lambda x: -x[1]))


def note_range(notes: list[Note]) -> dict:
    """Find the pitch range of a melody.

    Args:
        notes: List of Notes.

    Returns:
        Dict with lowest, highest, span_semitones, span_octaves.
    """
    pitched = [(n.pitch, n.octave) for n in notes if n.pitch is not None]
    if not pitched:
        return {"lowest": None, "highest": None, "span_semitones": 0, "span_octaves": 0}

    midi_vals = [_semi(str(p)) + o * 12 for p, o in pitched]
    lo_midi = min(midi_vals)
    hi_midi = max(midi_vals)
    lo_idx = midi_vals.index(lo_midi)
    hi_idx = midi_vals.index(hi_midi)

    return {
        "lowest": f"{pitched[lo_idx][0]}{pitched[lo_idx][1]}",
        "highest": f"{pitched[hi_idx][0]}{pitched[hi_idx][1]}",
        "span_semitones": hi_midi - lo_midi,
        "span_octaves": round((hi_midi - lo_midi) / 12, 1),
    }


def rhythmic_density(notes: list[Note]) -> dict:
    """Calculate rhythmic density metrics for a note list.

    Args:
        notes: List of Notes.

    Returns:
        Dict with total_notes, total_rests, total_beats, notes_per_beat,
        shortest_note, longest_note.
    """
    pitched = [n for n in notes if n.pitch is not None]
    rests = [n for n in notes if n.pitch is None]
    total_beats = sum(n.duration for n in notes)
    durations = [n.duration for n in pitched] if pitched else [0]

    return {
        "total_notes": len(pitched),
        "total_rests": len(rests),
        "total_beats": round(total_beats, 2),
        "notes_per_beat": round(len(pitched) / max(total_beats, 0.01), 2),
        "shortest_note": min(durations),
        "longest_note": max(durations),
    }


def detect_repeated_sections(
    song,
    beats_per_bar: int = 4,
    min_bars: int = 2,
) -> list[dict]:
    """Detect repeated bar patterns in a song.

    Compares bars by note content hash to find sections that repeat.

    Args:
        song:          Song to analyze.
        beats_per_bar: Beats per bar.
        min_bars:      Minimum bars for a section to count.

    Returns:
        List of dicts: {track, pattern_hash, bars, repeat_count}.
    """
    from ..engine import Chord as _Chord

    results: list[dict] = []

    for track in song.tracks:
        # Build bar content strings
        bar_contents: dict[int, str] = {}
        pos = 0.0
        for beat in track.beats:
            if beat.event:
                bar_idx = int(pos / beats_per_bar)
                event_str = ""
                if isinstance(beat.event, Note) and beat.event.pitch is not None:
                    event_str = f"{beat.event.pitch}{beat.event.octave}"
                elif isinstance(beat.event, _Chord):
                    event_str = f"{beat.event.root}{beat.event.shape}"
                bar_contents.setdefault(bar_idx, "")
                bar_contents[bar_idx] += event_str
                pos += beat.event.duration

        if not bar_contents:
            continue

        # Find repeated patterns (sequences of bars)
        for length in range(min_bars, len(bar_contents) // 2 + 1):
            patterns: dict[str, list[int]] = {}
            for start in range(0, len(bar_contents) - length + 1):
                pattern = "|".join(bar_contents.get(start + i, "") for i in range(length))
                if pattern and pattern != "|" * (length - 1):
                    patterns.setdefault(pattern, []).append(start)

            for pattern_hash, starts in patterns.items():
                if len(starts) > 1:
                    results.append(
                        {
                            "track": track.name,
                            "pattern_hash": hash(pattern_hash) % 10000,
                            "bars": length,
                            "repeat_count": len(starts),
                            "at_bars": starts,
                        }
                    )

    # Deduplicate — keep longest patterns
    seen: set[tuple[str, int]] = set()
    unique: list[dict] = []
    for r in sorted(results, key=lambda x: -x["bars"]):
        key = (r["track"], r["at_bars"][0])
        if key not in seen:
            unique.append(r)
            seen.add(key)

    return unique[:20]  # limit output


# ---------------------------------------------------------------------------
# Tension & resolution curves (v52.0)
# ---------------------------------------------------------------------------


def tension_curve(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[float]:
    """Calculate a tension value (0.0–1.0) for each chord in a progression.

    Tension is modeled from three factors:
    - Harmonic distance from tonic (chromatic chords = high tension)
    - Chord complexity (7ths > triads, altered > diatonic)
    - Dominant function (V and viio are inherently tense)

    The result is a curve you can plot or use to drive dynamics,
    filter sweeps, or arrangement density.

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of floats, one per chord, in range [0.0, 1.0].
    """
    key_semi = _semi(key)
    major_intervals = set(_SCALE_INTERVALS["major"])
    curve = []

    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12

        # Factor 1: diatonic distance (0 if diatonic, 0.3 if chromatic)
        diatonic = degree in major_intervals
        dist_score = 0.0 if diatonic else 0.3

        # Factor 2: chord complexity
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        complexity = min(len(semis) / 5.0, 0.3)  # more notes = more tension

        # Factor 3: dominant function
        dom_score = 0.0
        if degree == 7:  # V
            dom_score = 0.25
        elif degree == 11:  # viio
            dom_score = 0.3
        elif degree == 6:  # tritone area
            dom_score = 0.2

        # Factor 4: tonic resolution (I is the least tense)
        tonic_rest = 0.15 if degree == 0 else 0.0

        tension = min(1.0, dist_score + complexity + dom_score - tonic_rest)
        tension = max(0.0, tension)
        curve.append(round(tension, 3))

    return curve


def tension_at(
    progression: list[tuple[str, str]],
    index: int,
    key: str = "C",
) -> float:
    """Get the tension value at a specific chord index.

    Args:
        progression: List of (root, shape) tuples.
        index:       Chord index (0-based).
        key:         Key for analysis.

    Returns:
        Tension float in [0.0, 1.0].
    """
    curve = tension_curve(progression, key)
    if 0 <= index < len(curve):
        return curve[index]
    return 0.0


# ---------------------------------------------------------------------------
# Song fingerprinting & similarity (v61.0)
# ---------------------------------------------------------------------------


def song_fingerprint(
    progression: list[tuple[str, str]],
    notes: list[Note] | None = None,
) -> dict:
    """Extract a feature vector from a chord progression (and optional melody).

    The fingerprint captures the harmonic and melodic DNA of a piece:
    pitch class histogram, chord quality distribution, average interval,
    and rhythmic density. Use it to compare songs or cluster a corpus.

    Args:
        progression: List of (root, shape) tuples.
        notes:       Optional melody notes for pitch/rhythm stats.

    Returns:
        Dict with keys: pitch_histogram, quality_dist, avg_interval,
        rhythm_density, chord_count.
    """
    # Pitch class histogram (12 bins)
    pc_hist = [0] * 12
    quality_counts: dict[str, int] = {}
    for root, shape in progression:
        pc_hist[_semi(root)] += 1
        quality_counts[shape] = quality_counts.get(shape, 0) + 1

    total = max(sum(pc_hist), 1)
    pc_hist_norm = [round(c / total, 3) for c in pc_hist]

    quality_total = max(sum(quality_counts.values()), 1)
    quality_dist = {k: round(v / quality_total, 3) for k, v in sorted(quality_counts.items())}

    # Melody stats
    avg_interval = 0.0
    rhythm_density = 0.0
    if notes:
        intervals = []
        sounding = 0
        for i in range(1, len(notes)):
            if notes[i].pitch and notes[i - 1].pitch:
                a = _semi(str(notes[i].pitch)) + notes[i].octave * 12
                b = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
                intervals.append(abs(a - b))
            if notes[i].pitch is not None:
                sounding += 1
        avg_interval = round(sum(intervals) / max(len(intervals), 1), 2)
        rhythm_density = round(sounding / max(len(notes), 1), 3)

    return {
        "pitch_histogram": pc_hist_norm,
        "quality_dist": quality_dist,
        "avg_interval": avg_interval,
        "rhythm_density": rhythm_density,
        "chord_count": len(progression),
    }


def song_similarity(fp_a: dict, fp_b: dict) -> float:
    """Compute cosine similarity between two song fingerprints.

    Args:
        fp_a: First fingerprint (from song_fingerprint).
        fp_b: Second fingerprint.

    Returns:
        Similarity score in [0.0, 1.0].
    """
    import math

    vec_a = fp_a["pitch_histogram"]
    vec_b = fp_b["pitch_histogram"]
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a)) or 1e-9
    mag_b = math.sqrt(sum(b * b for b in vec_b)) or 1e-9
    return round(dot / (mag_a * mag_b), 3)


# ---------------------------------------------------------------------------
# Counterpoint rules validator (v62.0)
# ---------------------------------------------------------------------------


def validate_counterpoint(
    cf: list[Note],
    cp: list[Note],
    species: int = 1,
) -> list[str]:
    """Validate counterpoint against a cantus firmus and return violations.

    Checks:
    - No parallel perfect 5ths or octaves
    - No voice crossing
    - No leaps greater than an octave
    - Consonant intervals on strong beats (species 1)

    Args:
        cf: Cantus firmus notes.
        cp: Counterpoint notes.
        species: Species number (1 or 2).

    Returns:
        List of violation description strings. Empty = perfect counterpoint.
    """
    violations: list[str] = []
    min_len = min(len(cf), len(cp))

    for i in range(min_len):
        if cf[i].pitch is None or cp[i].pitch is None:
            continue

        cf_abs = _semi(str(cf[i].pitch)) + cf[i].octave * 12
        cp_abs = _semi(str(cp[i].pitch)) + cp[i].octave * 12
        interval = abs(cp_abs - cf_abs) % 12

        # Voice crossing check
        if cp_abs < cf_abs:
            violations.append(f"Bar {i + 1}: voice crossing (CP below CF)")

        # Consonance check on strong beats
        if species == 1 or i % 2 == 0:
            if interval in _DISSONANCES:
                violations.append(f"Bar {i + 1}: dissonant interval ({interval} semitones)")

        # Leap > octave in CP
        if i > 0 and cp[i - 1].pitch is not None:
            prev_cp = _semi(str(cp[i - 1].pitch)) + cp[i - 1].octave * 12
            leap = abs(cp_abs - prev_cp)
            if leap > 12:
                violations.append(f"Bar {i + 1}: leap > octave ({leap} semitones)")

        # Parallel 5ths/octaves
        if i > 0 and cf[i - 1].pitch is not None and cp[i - 1].pitch is not None:
            prev_cf = _semi(str(cf[i - 1].pitch)) + cf[i - 1].octave * 12
            prev_cp = _semi(str(cp[i - 1].pitch)) + cp[i - 1].octave * 12
            prev_interval = abs(prev_cp - prev_cf) % 12
            curr_interval = interval
            if prev_interval == curr_interval and curr_interval in (0, 7):
                cf_moved = cf_abs != prev_cf
                cp_moved = cp_abs != prev_cp
                if cf_moved and cp_moved:
                    label = "P8" if curr_interval == 0 else "P5"
                    violations.append(f"Bar {i + 1}: parallel {label}")

    return violations


def grade_counterpoint(
    cf: list[Note],
    cp: list[Note],
    species: int = 1,
) -> int:
    """Grade counterpoint on a 0-100 scale.

    100 = no violations. Each violation deducts points based on severity.

    Args:
        cf: Cantus firmus.
        cp: Counterpoint.
        species: Species number.

    Returns:
        Integer score 0-100.
    """
    violations = validate_counterpoint(cf, cp, species)
    # Deduct 10 per violation, floor at 0
    score = max(0, 100 - len(violations) * 10)
    return score


# ---------------------------------------------------------------------------
# Song structure detection (v65.0)
# ---------------------------------------------------------------------------


def section_similarity_matrix(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
) -> list[list[float]]:
    """Compute pairwise similarity between sections of a progression.

    Divides the progression into chunks and compares each pair using
    pitch-class overlap. The resulting matrix reveals repeated sections.

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.

    Returns:
        NxN matrix of similarity scores (0.0–1.0), where N = number of sections.
    """
    sections = [
        progression[i : i + bars_per_section] for i in range(0, len(progression), bars_per_section)
    ]

    def _section_pcs(section: list[tuple[str, str]]) -> set[int]:
        return {_semi(r) for r, _ in section}

    n = len(sections)
    matrix: list[list[float]] = []
    for i in range(n):
        row: list[float] = []
        pcs_i = _section_pcs(sections[i])
        for j in range(n):
            pcs_j = _section_pcs(sections[j])
            union = pcs_i | pcs_j
            if not union:
                row.append(1.0)
            else:
                row.append(round(len(pcs_i & pcs_j) / len(union), 3))
        matrix.append(row)
    return matrix


def detect_sections(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
    threshold: float = 0.7,
) -> list[dict]:
    """Detect repeated sections in a chord progression.

    Groups sections by similarity: sections that match above the threshold
    get the same label (A, B, C, ...). Returns a list of section descriptors.

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.
        threshold:       Similarity threshold for grouping.

    Returns:
        List of dicts: {start, end, label}.
    """
    matrix = section_similarity_matrix(progression, bars_per_section)
    n = len(matrix)
    labels: list[str] = [""] * n
    current_label = "A"

    for i in range(n):
        if labels[i]:
            continue
        labels[i] = current_label
        for j in range(i + 1, n):
            if not labels[j] and matrix[i][j] >= threshold:
                labels[j] = current_label
        current_label = chr(ord(current_label) + 1)

    return [
        {
            "start": i * bars_per_section,
            "end": min((i + 1) * bars_per_section, len(progression)),
            "label": labels[i],
        }
        for i in range(n)
    ]


def label_form(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
) -> str:
    """Auto-label the form of a progression (e.g. 'AABA', 'ABAB').

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.

    Returns:
        Form string (e.g. 'AABA', 'ABCABC').
    """
    sections = detect_sections(progression, bars_per_section)
    return "".join(s["label"] for s in sections)


# ---------------------------------------------------------------------------
# Harmonic reduction (v68.0)
# ---------------------------------------------------------------------------


def reduce_to_chords(
    notes: list[Note],
    beats_per_chord: int = 4,
) -> list[tuple[str, str]]:
    """Collapse a melody to its implied chords by grouping pitch classes.

    Divides notes into chunks and finds the best-matching triad for
    each chunk. The reverse of melody generation — "what chords does
    this melody outline?"

    Args:
        notes:           Melody notes.
        beats_per_chord: Notes per chord group.

    Returns:
        List of (root, shape) tuples, one per group.
    """
    result: list[tuple[str, str]] = []
    for i in range(0, len(notes), beats_per_chord):
        chunk = notes[i : i + beats_per_chord]
        pcs = [_semi(str(n.pitch)) for n in chunk if n.pitch is not None]
        if not pcs:
            result.append(("C", "maj"))
            continue
        # Try each root and find best triad match
        best_root = 0
        best_shape = "maj"
        best_score = -1
        pc_set = set(pcs)
        for candidate_root in range(12):
            for shape, intervals in [
                ("maj", [0, 4, 7]),
                ("min", [0, 3, 7]),
                ("dim", [0, 3, 6]),
                ("aug", [0, 4, 8]),
            ]:
                chord_pcs = {(candidate_root + iv) % 12 for iv in intervals}
                score = len(pc_set & chord_pcs)
                if score > best_score:
                    best_score = score
                    best_root = candidate_root
                    best_shape = shape
        result.append((_NOTE_NAMES[best_root], best_shape))
    return result


def harmonic_skeleton(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[tuple[str, str]]:
    """Reduce a progression to its functional skeleton (I, IV, V only).

    Strips away secondary dominants, chromatic chords, and modal
    mixture — leaving only the three pillars of tonal harmony.

    Args:
        progression: Full chord progression.
        key:         Key for analysis.

    Returns:
        Simplified progression using only I, IV, and V.
    """
    key_semi = _semi(key)
    tonic = (_NOTE_NAMES[key_semi], "maj")
    subdominant = (_NOTE_NAMES[(key_semi + 5) % 12], "maj")
    dominant = (_NOTE_NAMES[(key_semi + 7) % 12], "maj")

    subdom_degrees = {1, 2, 5, 6, 10}  # bII, II, IV, bV, bVII → subdominant
    dom_degrees = {7, 11}  # V, VII → dominant

    result: list[tuple[str, str]] = []
    for root, _shape in progression:
        degree = (_semi(root) - key_semi) % 12
        if degree in dom_degrees:
            result.append(dominant)
        elif degree in subdom_degrees:
            result.append(subdominant)
        else:
            result.append(tonic)  # everything else is tonic function
    return result


def complexity_score(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> int:
    """Rate the harmonic complexity of a progression (0–100).

    Factors: number of distinct roots, chord quality variety, chromatic
    chords, and functional variety. A I-IV-V-I scores low; Coltrane
    changes score high.

    Args:
        progression: Chord progression.
        key:         Key for analysis.

    Returns:
        Integer score 0–100.
    """
    if not progression:
        return 0
    key_semi = _semi(key)
    major_pcs = {(key_semi + iv) % 12 for iv in _SCALE_INTERVALS["major"]}

    roots = {_semi(r) for r, _ in progression}
    shapes = {s for _, s in progression}
    chromatic = sum(1 for r, _ in progression if _semi(r) not in major_pcs)

    root_score = min(len(roots) * 8, 30)  # up to 30 for root variety
    shape_score = min(len(shapes) * 6, 25)  # up to 25 for quality variety
    chrom_score = min(chromatic * 5, 25)  # up to 25 for chromatic chords
    length_score = min(len(progression), 20)  # up to 20 for length

    return min(100, root_score + shape_score + chrom_score + length_score)


# ---------------------------------------------------------------------------
# Texture density control (v71.0)
# ---------------------------------------------------------------------------


def texture_density(
    notes: list[Note],
    window_beats: float = 4.0,
) -> list[float]:
    """Measure notes-per-beat density in a sliding window.

    Returns a density value for each note position, representing
    how busy the texture is at that point. Useful for identifying
    climaxes, sparse passages, and density transitions.

    Args:
        notes:        Input notes.
        window_beats: Window size in beats for density calculation.

    Returns:
        List of density values (notes-per-beat), one per note.
    """
    if not notes:
        return []

    # Calculate cumulative beat positions
    positions: list[float] = []
    beat = 0.0
    for n in notes:
        positions.append(beat)
        beat += n.duration

    result: list[float] = []
    for i, pos in enumerate(positions):
        # Count notes within the window centered on this position
        window_start = pos - window_beats / 2
        window_end = pos + window_beats / 2
        count = sum(1 for p in positions if window_start <= p <= window_end)
        density = count / window_beats
        result.append(round(density, 2))

    return result


def thin_texture(
    notes: list[Note],
    target_density: float = 0.5,
    seed: int | None = None,
) -> list[Note]:
    """Remove notes to reach a target density (notes-per-beat).

    Randomly converts sounding notes to rests until the overall
    density drops to the target. Preserves the first and last notes.

    Args:
        notes:          Input notes.
        target_density: Desired notes-per-beat.
        seed:           Random seed.

    Returns:
        Thinned note list with some notes replaced by rests.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if not notes:
        return []

    total_dur = sum(n.duration for n in notes)
    sounding = [i for i, n in enumerate(notes) if n.pitch is not None]
    current_density = len(sounding) / max(total_dur, 0.01)

    result = list(notes)
    # Protect first and last sounding notes
    removable = [i for i in sounding if i != 0 and i != len(notes) - 1]
    rng.shuffle(removable)

    while current_density > target_density and removable:
        idx = removable.pop()
        result[idx] = Note.rest(notes[idx].duration)
        sounding_count = sum(1 for n in result if n.pitch is not None)
        current_density = sounding_count / max(total_dur, 0.01)

    return result


def thicken_texture(
    notes: list[Note],
    scale_name: str = "major",
    key: str = "C",
    target_density: float = 2.0,
    seed: int | None = None,
) -> list[Note]:
    """Add passing tones to increase texture density.

    Inserts scale-tone fills between existing notes until the target
    density is reached. New notes are half the duration of the original.

    Args:
        notes:          Input notes.
        scale_name:     Scale for fill notes.
        key:            Key root.
        target_density: Desired notes-per-beat.
        seed:           Random seed.

    Returns:
        Thickened note list with added passing tones.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if not notes:
        return []

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    scale_pcs = [(k + iv) % 12 for iv in intervals]

    result: list[Note] = []
    total_dur = sum(n.duration for n in notes)
    sounding = sum(1 for n in notes if n.pitch is not None)
    current_density = sounding / max(total_dur, 0.01)

    for n in notes:
        result.append(n)
        if current_density < target_density and n.pitch is not None:
            # Insert a passing tone
            fill_pc = rng.choice(scale_pcs)
            fill_dur = n.duration / 2
            result[-1] = Note(n.pitch, n.octave, n.duration / 2, velocity=n.velocity)
            result.append(Note(_NOTE_NAMES[fill_pc], n.octave, fill_dur, velocity=70))
            sounding += 1
            current_density = sounding / max(total_dur, 0.01)

    return result


# ---------------------------------------------------------------------------
# Song statistics (v77.0)
# ---------------------------------------------------------------------------


def corpus_stats(
    progressions: list[list[tuple[str, str]]],
) -> dict:
    """Aggregate statistics across a collection of chord progressions.

    The bird's-eye view: how many unique roots, which chord shapes
    dominate, average progression length.

    Args:
        progressions: List of chord progressions (each a list of (root, shape) tuples).

    Returns:
        Dict with: total_chords, unique_roots, unique_shapes, avg_length,
        most_common_root, most_common_shape.
    """
    total_chords = 0
    root_counts: dict[str, int] = {}
    shape_counts: dict[str, int] = {}

    for prog in progressions:
        total_chords += len(prog)
        for root, shape in prog:
            root_counts[root] = root_counts.get(root, 0) + 1
            shape_counts[shape] = shape_counts.get(shape, 0) + 1

    avg_length = total_chords / max(len(progressions), 1)
    most_common_root = max(root_counts, key=root_counts.get) if root_counts else "C"
    most_common_shape = max(shape_counts, key=shape_counts.get) if shape_counts else "maj"

    return {
        "total_progressions": len(progressions),
        "total_chords": total_chords,
        "unique_roots": len(root_counts),
        "unique_shapes": len(shape_counts),
        "avg_length": round(avg_length, 1),
        "most_common_root": most_common_root,
        "most_common_shape": most_common_shape,
        "root_counts": dict(sorted(root_counts.items(), key=lambda x: -x[1])),
        "shape_counts": dict(sorted(shape_counts.items(), key=lambda x: -x[1])),
    }


def key_distribution(
    progressions: list[list[tuple[str, str]]],
) -> dict[str, int]:
    """Count how many progressions are in each estimated key.

    Args:
        progressions: List of chord progressions.

    Returns:
        Dict mapping key name → count, sorted by frequency.
    """
    counts: dict[str, int] = {}
    for prog in progressions:
        if prog:
            estimated = detect_key(prog)
            counts[estimated] = counts.get(estimated, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def tempo_distribution(
    bpms: list[float],
    bucket_size: float = 10.0,
) -> dict[str, int]:
    """Create a BPM histogram from a list of tempos.

    Args:
        bpms:        List of BPM values.
        bucket_size: Width of each histogram bucket.

    Returns:
        Dict mapping BPM range string → count.
    """
    buckets: dict[str, int] = {}
    for bpm in bpms:
        low = int(bpm // bucket_size) * int(bucket_size)
        high = low + int(bucket_size)
        key = f"{low}-{high}"
        buckets[key] = buckets.get(key, 0) + 1
    return dict(sorted(buckets.items()))


# ---------------------------------------------------------------------------
# Song comparison report (v85.0)
# ---------------------------------------------------------------------------


def compare_progressions(
    prog_a: list[tuple[str, str]],
    prog_b: list[tuple[str, str]],
    key: str = "C",
) -> dict:
    """Compare two chord progressions across multiple dimensions.

    Returns a structured report: shared chords, key estimates,
    complexity delta, length delta, root overlap ratio.

    Args:
        prog_a: First progression.
        prog_b: Second progression.
        key:    Key context for complexity scoring.

    Returns:
        Dict with comparison metrics.
    """
    set_a = set(prog_a)
    set_b = set(prog_b)
    shared = sorted(set_a & set_b)

    key_a = detect_key(prog_a) if prog_a else "C"
    key_b = detect_key(prog_b) if prog_b else "C"

    comp_a = complexity_score(prog_a, key)
    comp_b = complexity_score(prog_b, key)

    roots_a = {r for r, _ in prog_a}
    roots_b = {r for r, _ in prog_b}
    root_overlap = len(roots_a & roots_b) / max(len(roots_a | roots_b), 1)

    return {
        "length_a": len(prog_a),
        "length_b": len(prog_b),
        "shared_chords": shared,
        "shared_count": len(shared),
        "unique_to_a": sorted(set_a - set_b),
        "unique_to_b": sorted(set_b - set_a),
        "key_a": key_a,
        "key_b": key_b,
        "same_key": key_a == key_b,
        "complexity_a": comp_a,
        "complexity_b": comp_b,
        "complexity_delta": comp_b - comp_a,
        "root_overlap": round(root_overlap, 3),
    }


def similar_motion_ratio(voice_a: list[Note], voice_b: list[Note]) -> float:
    """What fraction of movements are in parallel (similar) motion.

    Args:
        voice_a: First voice.
        voice_b: Second voice.

    Returns:
        Ratio 0.0–1.0 of similar motion.
    """
    count = 0
    total = 0
    min_len = min(len(voice_a), len(voice_b))
    for i in range(1, min_len):
        if any(n.pitch is None for n in [voice_a[i - 1], voice_a[i], voice_b[i - 1], voice_b[i]]):
            continue
        a1 = _semi(str(voice_a[i - 1].pitch)) + voice_a[i - 1].octave * 12
        a2 = _semi(str(voice_a[i].pitch)) + voice_a[i].octave * 12
        b1 = _semi(str(voice_b[i - 1].pitch)) + voice_b[i - 1].octave * 12
        b2 = _semi(str(voice_b[i].pitch)) + voice_b[i].octave * 12
        total += 1
        if _motion_type(a1, a2, b1, b2) == "similar":
            count += 1
    return round(count / max(total, 1), 3)


def contrary_motion_ratio(voice_a: list[Note], voice_b: list[Note]) -> float:
    """What fraction of movements are in contrary motion.

    Contrary motion = voices move in opposite directions. The gold
    standard for voice independence — Bach maximized this.

    Args:
        voice_a: First voice.
        voice_b: Second voice.

    Returns:
        Ratio 0.0–1.0 of contrary motion.
    """
    count = 0
    total = 0
    min_len = min(len(voice_a), len(voice_b))
    for i in range(1, min_len):
        if any(n.pitch is None for n in [voice_a[i - 1], voice_a[i], voice_b[i - 1], voice_b[i]]):
            continue
        a1 = _semi(str(voice_a[i - 1].pitch)) + voice_a[i - 1].octave * 12
        a2 = _semi(str(voice_a[i].pitch)) + voice_a[i].octave * 12
        b1 = _semi(str(voice_b[i - 1].pitch)) + voice_b[i - 1].octave * 12
        b2 = _semi(str(voice_b[i].pitch)) + voice_b[i].octave * 12
        total += 1
        if _motion_type(a1, a2, b1, b2) == "contrary":
            count += 1
    return round(count / max(total, 1), 3)


def voice_independence_score(voices: list[list[Note]]) -> int:
    """Rate how independently multiple voices move (0-100).

    Higher = more contrary/oblique motion, fewer parallel movements.
    Bach would score 90+. Parallel thirds score ~30.

    Args:
        voices: List of voice note-lists.

    Returns:
        Score 0-100.
    """
    if len(voices) < 2:
        return 100

    total_contrary = 0.0
    pairs = 0
    for i in range(len(voices)):
        for j in range(i + 1, len(voices)):
            total_contrary += contrary_motion_ratio(voices[i], voices[j])
            pairs += 1

    avg_contrary = total_contrary / max(pairs, 1)
    return min(100, int(avg_contrary * 130))  # scale so ~77% contrary = 100


# ---------------------------------------------------------------------------
# Musical form analysis report (v93.0)
# ---------------------------------------------------------------------------


def analysis_report(
    progression: list[tuple[str, str]],
    key: str = "C",
    bpm: float = 120.0,
    title: str = "Untitled",
) -> str:
    """Generate a markdown analysis report for a chord progression.

    Covers: form, key, cadences, complexity, tension curve, chord
    function distribution. The kind of report a theory professor
    writes — but in one function call.

    Args:
        progression: Chord progression.
        key:         Key for analysis.
        bpm:         Tempo.
        title:       Song/progression title.

    Returns:
        Markdown-formatted analysis string.
    """
    # Form
    form = label_form(progression, bars_per_section=4)

    # Cadences
    cadences = detect_cadences(progression, key)
    cadence_strs = [f"  - {c['type']} at position {c['position']}" for c in cadences]

    # Functional analysis
    func_analysis = functional_analysis(progression, key)
    func_counts: dict[str, int] = {}
    for fa in func_analysis:
        func_counts[fa["function"]] = func_counts.get(fa["function"], 0) + 1

    # Tension
    curve = tension_curve(progression, key)
    avg_tension = sum(curve) / max(len(curve), 1)
    peak_idx = curve.index(max(curve)) if curve else 0

    # Complexity
    comp = complexity_score(progression, key)

    lines = [
        f"# Analysis: {title}",
        "",
        f"**Key:** {key} major",
        f"**Tempo:** {bpm} BPM",
        f"**Length:** {len(progression)} chords",
        f"**Form:** {form}",
        f"**Complexity:** {comp}/100",
        "",
        "## Cadences",
    ]
    if cadence_strs:
        lines.extend(cadence_strs)
    else:
        lines.append("  (none detected)")

    lines.extend(
        [
            "",
            "## Functional Distribution",
            f"  - Tonic (T): {func_counts.get('T', 0)}",
            f"  - Subdominant (S): {func_counts.get('S', 0)}",
            f"  - Dominant (D): {func_counts.get('D', 0)}",
            f"  - Chromatic: {func_counts.get('chromatic', 0)}",
            "",
            "## Tension Curve",
            f"  - Average tension: {avg_tension:.2f}",
            f"  - Peak tension at chord {peak_idx + 1}",
            f"  - Values: {', '.join(str(v) for v in curve)}",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Phrase boundary detection (v98.0)
# ---------------------------------------------------------------------------


def detect_phrases(
    notes: list[Note],
    min_gap: float = 0.5,
) -> list[dict]:
    """Detect phrase boundaries by rest gaps and contour peaks.

    A phrase ends when there's a rest longer than min_gap, or at
    a local pitch maximum followed by a descent.

    Args:
        notes:   Input notes.
        min_gap: Minimum rest duration to mark a boundary.

    Returns:
        List of dicts: {start, end, length}.
    """
    if not notes:
        return []

    phrases: list[dict] = []
    phrase_start = 0

    for i, n in enumerate(notes):
        is_boundary = False

        # Rest gap boundary
        if n.pitch is None and n.duration >= min_gap:
            is_boundary = True

        # End of list
        if i == len(notes) - 1:
            is_boundary = True

        if is_boundary and i >= phrase_start:
            phrases.append(
                {
                    "start": phrase_start,
                    "end": i,
                    "length": i - phrase_start,
                }
            )
            phrase_start = i + 1

    return phrases


def phrase_lengths(notes: list[Note], min_gap: float = 0.5) -> list[int]:
    """Return the length of each detected phrase.

    Args:
        notes:   Input notes.
        min_gap: Rest gap threshold.

    Returns:
        List of phrase lengths (note counts).
    """
    return [p["length"] for p in detect_phrases(notes, min_gap)]


# ---------------------------------------------------------------------------
# Rhythmic density analysis (v105.0)
# ---------------------------------------------------------------------------


def density_profile(
    notes: list[Note],
    resolution: float = 1.0,
) -> list[float]:
    """Build a rhythmic density profile — notes per beat at a given resolution.

    Divides the total duration into bins of `resolution` beats and counts
    the number of sounding note onsets in each bin.

    Args:
        notes:      Input notes.
        resolution: Bin size in beats.

    Returns:
        List of floats: note count per bin.
    """
    if not notes:
        return []
    total_dur = sum(n.duration for n in notes)
    n_bins = max(1, int(total_dur / resolution))
    bins = [0.0] * n_bins

    onset = 0.0
    for n in notes:
        if n.pitch is not None:
            bin_idx = min(int(onset / resolution), n_bins - 1)
            bins[bin_idx] += 1.0
        onset += n.duration

    return bins


def density_contrast(
    notes: list[Note],
    split_at: int | None = None,
) -> float:
    """Measure the density contrast between the first and second halves.

    Returns a ratio: second_half_density / first_half_density.
    Values > 1.0 = builds energy, < 1.0 = winds down, ~1.0 = steady.

    Args:
        notes:    Input notes.
        split_at: Note index to split at (default: midpoint).

    Returns:
        Density contrast ratio.
    """
    if not notes:
        return 1.0
    mid = split_at if split_at else len(notes) // 2
    first_half = notes[:mid]
    second_half = notes[mid:]

    def _density(ns: list[Note]) -> float:
        sounding = sum(1 for n in ns if n.pitch is not None)
        total_dur = sum(n.duration for n in ns) or 1.0
        return sounding / total_dur

    d1 = _density(first_half)
    d2 = _density(second_half)
    return round(d2 / max(d1, 0.001), 3)


# ---------------------------------------------------------------------------
# Harmonic ambiguity score (v106.0)
# ---------------------------------------------------------------------------


def ambiguity_score(
    progression: list[tuple[str, str]],
) -> float:
    """Rate how ambiguous a progression's key center is (0.0-1.0).

    0.0 = clearly in one key (all diatonic). 1.0 = completely ambiguous
    (every chord is chromatic, no key fits well). Measures the gap
    between the best and second-best key candidates.

    Args:
        progression: Chord progression.

    Returns:
        Ambiguity score 0.0-1.0.
    """
    if not progression:
        return 0.0

    root_counts = [0] * 12
    for root, _ in progression:
        root_counts[_semi(root)] += 1

    major_intervals = _SCALE_INTERVALS["major"]
    scores: list[int] = []
    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        scores.append(score)

    scores_with_root = []
    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        # Bonus for root being tonic itself
        root_bonus = root_counts[candidate] * 0.5
        scores_with_root.append(score + root_bonus)

    scores_with_root.sort(reverse=True)
    best = scores_with_root[0]
    second = scores_with_root[1] if len(scores_with_root) > 1 else 0
    total = sum(root_counts)

    if total == 0 or best == 0:
        return 0.0

    # Ambiguity = how close second-best is to best (normalized)
    gap = (best - second) / best
    return round(max(0.0, min(1.0, 1.0 - gap)), 3)


def key_certainty(
    progression: list[tuple[str, str]],
) -> dict:
    """Return the estimated key with a confidence score.

    Args:
        progression: Chord progression.

    Returns:
        Dict: {key, confidence (0.0-1.0), ambiguity}.
    """
    if not progression:
        return {"key": "C", "confidence": 0.0, "ambiguity": 0.0}

    estimated = detect_key(progression)
    amb = ambiguity_score(progression)
    confidence = round(1.0 - amb, 3)

    return {"key": estimated, "confidence": confidence, "ambiguity": amb}


# ---------------------------------------------------------------------------
# Progression complexity curve (v112.0)
# ---------------------------------------------------------------------------


def complexity_curve(
    progression: list[tuple[str, str]],
    key: str = "C",
    window: int = 4,
) -> list[int]:
    """Compute a sliding-window complexity score across a progression.

    Each position gets the complexity_score of the surrounding `window`
    chords. Shows where the harmony gets dense or simple over time.

    Args:
        progression: Chord progression.
        key:         Key context.
        window:      Number of chords per window.

    Returns:
        List of complexity scores, one per chord position.
    """
    if not progression:
        return []
    result: list[int] = []
    for i in range(len(progression)):
        start = max(0, i - window // 2)
        end = min(len(progression), start + window)
        chunk = progression[start:end]
        result.append(complexity_score(chunk, key))
    return result


def complexity_contrast(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> float:
    """Ratio of second-half complexity to first-half complexity.

    > 1.0 = gets more complex over time (builds).
    < 1.0 = gets simpler (resolves).
    ~1.0 = steady complexity.

    Args:
        progression: Chord progression.
        key:         Key context.

    Returns:
        Complexity contrast ratio.
    """
    if len(progression) < 2:
        return 1.0
    mid = len(progression) // 2
    first = complexity_score(progression[:mid], key)
    second = complexity_score(progression[mid:], key)
    return round(second / max(first, 1), 3)


# ---------------------------------------------------------------------------
# Note name utilities (v114.0)
# ---------------------------------------------------------------------------


def note_to_midi(pitch: str, octave: int) -> int:
    """Convert a note name + octave to MIDI note number.

    C4 = 60 (middle C). Standard MIDI convention.

    Args:
        pitch:  Note name.
        octave: Octave number.

    Returns:
        MIDI note number (0-127).
    """
    return _semi(pitch) + (octave + 1) * 12


def midi_to_note(midi: int) -> tuple[str, int]:
    """Convert a MIDI note number to (pitch_name, octave).

    Args:
        midi: MIDI note number.

    Returns:
        (pitch_name, octave) tuple.
    """
    return (_NOTE_NAMES[midi % 12], midi // 12 - 1)


def note_to_freq(pitch: str, octave: int, a4: float = 440.0) -> float:
    """Convert a note name + octave to frequency in Hz.

    Uses equal temperament with configurable A4 reference.

    Args:
        pitch:  Note name.
        octave: Octave number.
        a4:     Reference frequency for A4 (default 440 Hz).

    Returns:
        Frequency in Hz.
    """
    midi = note_to_midi(pitch, octave)
    return round(a4 * (2 ** ((midi - 69) / 12)), 3)


# ---------------------------------------------------------------------------
# Progression similarity (v115.0)
# ---------------------------------------------------------------------------


def progression_similarity(
    prog_a: list[tuple[str, str]],
    prog_b: list[tuple[str, str]],
) -> float:
    """Compare two progressions by root PC overlap + shape overlap.

    Combines Jaccard similarity on root pitch classes and chord quality
    distribution similarity. Transposition-dependent (use detect_key
    first if you want key-independent comparison).

    Args:
        prog_a: First progression.
        prog_b: Second progression.

    Returns:
        Similarity score 0.0-1.0.
    """
    if not prog_a or not prog_b:
        return 0.0

    fp_a = song_fingerprint(prog_a)
    fp_b = song_fingerprint(prog_b)
    pitch_sim = song_similarity(fp_a, fp_b)

    # Shape distribution similarity
    shapes_a = set(s for _, s in prog_a)
    shapes_b = set(s for _, s in prog_b)
    union = shapes_a | shapes_b
    if not union:
        shape_sim = 1.0
    else:
        shape_sim = len(shapes_a & shapes_b) / len(union)

    return round((pitch_sim + shape_sim) / 2, 3)


def find_similar_progressions(
    target: list[tuple[str, str]],
    corpus: list[list[tuple[str, str]]],
    top_n: int = 5,
) -> list[tuple[int, float]]:
    """Find the most similar progressions in a corpus.

    Args:
        target: The progression to compare against.
        corpus: List of progressions to search.
        top_n:  Number of results.

    Returns:
        List of (corpus_index, similarity_score) sorted by score descending.
    """
    scores = []
    for i, prog in enumerate(corpus):
        sim = progression_similarity(target, prog)
        scores.append((i, sim))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_n]


# ---------------------------------------------------------------------------
# Melodic range stats (v118.0)
# ---------------------------------------------------------------------------


def melodic_range(notes: list[Note]) -> dict:
    """Compute the melodic range statistics of a note list.

    Args:
        notes: Input melody.

    Returns:
        Dict: {lowest, highest, range_semitones, range_octaves, avg_pitch}.
    """
    sounding = [n for n in notes if n.pitch is not None]
    if not sounding:
        return {
            "lowest": None,
            "highest": None,
            "range_semitones": 0,
            "range_octaves": 0.0,
            "avg_pitch": 0.0,
        }

    absolutes = [_semi(str(n.pitch)) + n.octave * 12 for n in sounding]
    low = min(absolutes)
    high = max(absolutes)
    avg = sum(absolutes) / len(absolutes)

    low_p, low_o = _NOTE_NAMES[low % 12], low // 12
    high_p, high_o = _NOTE_NAMES[high % 12], high // 12

    return {
        "lowest": f"{low_p}{low_o}",
        "highest": f"{high_p}{high_o}",
        "range_semitones": high - low,
        "range_octaves": round((high - low) / 12, 2),
        "avg_pitch": round(avg, 1),
    }


def pitch_center(notes: list[Note]) -> tuple[str, int] | None:
    """Find the pitch center (average pitch) of a melody.

    Args:
        notes: Input melody.

    Returns:
        (pitch_name, octave) of the center, or None if no sounding notes.
    """
    sounding = [n for n in notes if n.pitch is not None]
    if not sounding:
        return None
    avg = sum(_semi(str(n.pitch)) + n.octave * 12 for n in sounding) / len(sounding)
    avg_int = round(avg)
    return (_NOTE_NAMES[avg_int % 12], avg_int // 12)


# ---------------------------------------------------------------------------
# Pitch histogram (v119.0)
# ---------------------------------------------------------------------------


def pitch_histogram(notes: list[Note]) -> dict[str, int]:
    """Count occurrences of each pitch name in a note list.

    Args:
        notes: Input notes.

    Returns:
        Dict mapping pitch name → count, sorted by frequency descending.
    """
    counts: dict[str, int] = {}
    for n in notes:
        if n.pitch is not None:
            p = str(n.pitch)
            counts[p] = counts.get(p, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def pitch_class_histogram(notes: list[Note]) -> list[int]:
    """Count occurrences of each pitch class (0-11) in a note list.

    Args:
        notes: Input notes.

    Returns:
        12-element list of counts (index 0 = C, 1 = C#, ..., 11 = B).
    """
    hist = [0] * 12
    for n in notes:
        if n.pitch is not None:
            hist[_semi(str(n.pitch))] += 1
    return hist


# ---------------------------------------------------------------------------
# Note velocity stats (v120.0)
# ---------------------------------------------------------------------------


def velocity_stats(notes: list[Note]) -> dict:
    """Compute velocity statistics for a note list.

    Args:
        notes: Input notes.

    Returns:
        Dict: {min, max, avg, range, count}.
    """
    vels = [n.velocity for n in notes if n.pitch is not None and hasattr(n, "velocity")]
    if not vels:
        return {"min": 0, "max": 0, "avg": 0.0, "range": 0, "count": 0}
    return {
        "min": min(vels),
        "max": max(vels),
        "avg": round(sum(vels) / len(vels), 1),
        "range": max(vels) - min(vels),
        "count": len(vels),
    }


def velocity_curve(notes: list[Note]) -> list[int]:
    """Extract the velocity values as a list for plotting.

    Args:
        notes: Input notes.

    Returns:
        List of velocities (0 for rests).
    """
    return [n.velocity if n.pitch is not None else 0 for n in notes]


# ---------------------------------------------------------------------------
# Duration stats (v121.0)
# ---------------------------------------------------------------------------


def duration_stats(notes: list[Note]) -> dict:
    """Compute duration statistics for a note list.

    Args:
        notes: Input notes.

    Returns:
        Dict: {min, max, avg, total, count, unique_durations}.
    """
    durs = [n.duration for n in notes]
    if not durs:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "total": 0.0, "count": 0, "unique_durations": 0}
    return {
        "min": round(min(durs), 4),
        "max": round(max(durs), 4),
        "avg": round(sum(durs) / len(durs), 4),
        "total": round(sum(durs), 4),
        "count": len(durs),
        "unique_durations": len(set(round(d, 4) for d in durs)),
    }


def total_duration(notes: list[Note]) -> float:
    """Sum of all note durations.

    Args:
        notes: Input notes.

    Returns:
        Total duration in beats.
    """
    return round(sum(n.duration for n in notes), 4)


# ---------------------------------------------------------------------------
# Rest analysis (v122.0)
# ---------------------------------------------------------------------------


def rest_ratio(notes: list[Note]) -> float:
    """Fraction of total duration that is rests (0.0-1.0).

    Args:
        notes: Input notes.

    Returns:
        Ratio of rest duration to total duration.
    """
    if not notes:
        return 0.0
    rest_dur = sum(n.duration for n in notes if n.pitch is None)
    total = sum(n.duration for n in notes)
    return round(rest_dur / max(total, 0.001), 4)


def longest_rest(notes: list[Note]) -> float:
    """Find the longest rest duration in a note list.

    Args:
        notes: Input notes.

    Returns:
        Duration of the longest rest (0.0 if no rests).
    """
    rests = [n.duration for n in notes if n.pitch is None]
    return max(rests) if rests else 0.0


# ---------------------------------------------------------------------------
# Leap/step analysis (v123.0)
# ---------------------------------------------------------------------------


def leap_count(notes: list[Note], threshold: int = 3) -> int:
    """Count melodic leaps (intervals larger than threshold semitones).

    Args:
        notes:     Input melody.
        threshold: Minimum semitones to count as a leap (default 3 = minor 3rd).

    Returns:
        Number of leaps.
    """
    count = 0
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        if abs(b - a) >= threshold:
            count += 1
    return count


def step_count(notes: list[Note], threshold: int = 3) -> int:
    """Count melodic steps (intervals smaller than threshold semitones).

    Args:
        notes:     Input melody.
        threshold: Maximum semitones to count as a step (default 3).

    Returns:
        Number of steps.
    """
    count = 0
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        if 0 < abs(b - a) < threshold:
            count += 1
    return count


def leap_step_ratio(notes: list[Note], threshold: int = 3) -> float:
    """Ratio of leaps to steps. Higher = more angular, lower = more stepwise.

    Args:
        notes:     Input melody.
        threshold: Leap/step boundary in semitones.

    Returns:
        Ratio (leaps / steps). Returns 0.0 if no steps.
    """
    leaps = leap_count(notes, threshold)
    steps = step_count(notes, threshold)
    return round(leaps / max(steps, 1), 3)


# ---------------------------------------------------------------------------
# Note repetition analysis (v124.0)
# ---------------------------------------------------------------------------


def repetition_ratio(notes: list[Note]) -> float:
    """Fraction of consecutive note pairs that repeat the same pitch (0.0-1.0).

    High repetition = static/drone-like. Low = constantly moving.

    Args:
        notes: Input melody.

    Returns:
        Ratio of repeated pitches to total consecutive pairs.
    """
    if len(notes) < 2:
        return 0.0
    repeats = 0
    total = 0
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        total += 1
        if notes[i].pitch == notes[i - 1].pitch and notes[i].octave == notes[i - 1].octave:
            repeats += 1
    return round(repeats / max(total, 1), 4)


def unique_pitches(notes: list[Note]) -> int:
    """Count the number of distinct pitches (name + octave) in a note list.

    Args:
        notes: Input notes.

    Returns:
        Number of unique pitch/octave combinations.
    """
    seen: set[tuple[str, int]] = set()
    for n in notes:
        if n.pitch is not None:
            seen.add((str(n.pitch), n.octave))
    return len(seen)


# ---------------------------------------------------------------------------
# Octave distribution (v128.0)
# ---------------------------------------------------------------------------


def octave_distribution(notes: list[Note]) -> dict[int, int]:
    """Count notes per octave.

    Args:
        notes: Input notes.

    Returns:
        Dict mapping octave number → count, sorted by octave.
    """
    counts: dict[int, int] = {}
    for n in notes:
        if n.pitch is not None:
            counts[n.octave] = counts.get(n.octave, 0) + 1
    return dict(sorted(counts.items()))


def register_spread(notes: list[Note]) -> int:
    """Count how many distinct octaves a melody spans.

    Args:
        notes: Input notes.

    Returns:
        Number of distinct octaves used.
    """
    return len(octave_distribution(notes))


class Change:
    """A single structural change between two songs."""

    __slots__ = ("change_type", "track_name", "detail")

    def __init__(self, change_type: str, track_name: str, detail: str):
        self.change_type = change_type  # "added", "removed", "modified"
        self.track_name = track_name
        self.detail = detail

    def __repr__(self) -> str:
        return f"Change({self.change_type!r}, {self.track_name!r}, {self.detail!r})"


def song_diff(a, b) -> list[Change]:
    """Compute structural differences between two songs.

    Returns a list of Change objects describing what changed between
    song A and song B.

    Args:
        a: First Song.
        b: Second Song.

    Returns:
        List of Change objects.
    """
    changes: list[Change] = []

    a_tracks = {t.name: t for t in a.tracks}
    b_tracks = {t.name: t for t in b.tracks}

    # Songs-level changes
    if a.bpm != b.bpm:
        changes.append(Change("modified", "_song", f"bpm: {a.bpm} → {b.bpm}"))
    if a.title != b.title:
        changes.append(Change("modified", "_song", f"title: {a.title!r} → {b.title!r}"))

    # Tracks added/removed
    for name in sorted(b_tracks.keys() - a_tracks.keys()):
        t = b_tracks[name]
        changes.append(Change("added", name, f"instrument={t.instrument}, {len(t.beats)} beats"))
    for name in sorted(a_tracks.keys() - b_tracks.keys()):
        t = a_tracks[name]
        changes.append(Change("removed", name, f"instrument={t.instrument}, {len(t.beats)} beats"))

    # Tracks modified
    for name in sorted(a_tracks.keys() & b_tracks.keys()):
        ta = a_tracks[name]
        tb = b_tracks[name]

        if ta.instrument != tb.instrument:
            changes.append(
                Change("modified", name, f"instrument: {ta.instrument} → {tb.instrument}")
            )
        if ta.volume != tb.volume:
            changes.append(Change("modified", name, f"volume: {ta.volume} → {tb.volume}"))
        if ta.pan != tb.pan:
            changes.append(Change("modified", name, f"pan: {ta.pan} → {tb.pan}"))
        if len(ta.beats) != len(tb.beats):
            changes.append(Change("modified", name, f"beats: {len(ta.beats)} → {len(tb.beats)}"))

    return changes


def song_patch(base, changes: list[Change]):
    """Apply a list of changes to a song (best-effort).

    Modifies the song in place. Only handles simple property changes
    and track additions (not beat-level reconstruction).

    Args:
        base:    Song to modify.
        changes: List of Change objects (from song_diff).

    Returns:
        The modified Song.
    """
    from ..engine import Track

    for change in changes:
        if change.track_name == "_song":
            if "bpm:" in change.detail:
                parts = change.detail.split(" → ")
                new_bpm = float(parts[1])
                base.bpm = new_bpm
            if "title:" in change.detail:
                parts = change.detail.split(" → ")
                base.title = parts[1].strip("'\"")

        elif change.change_type == "added":
            # Parse instrument from detail
            parts = change.detail.split(", ")
            instrument = parts[0].split("=")[1] if "=" in parts[0] else "sine"
            base.add_track(Track(name=change.track_name, instrument=instrument))

        elif change.change_type == "removed":
            base.tracks = [t for t in base.tracks if t.name != change.track_name]

        elif change.change_type == "modified":
            for track in base.tracks:
                if track.name == change.track_name:
                    if "volume:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.volume = float(parts[1])
                    elif "pan:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.pan = float(parts[1])
                    elif "instrument:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.instrument = parts[1].strip()
                    break

    return base


# ---------------------------------------------------------------------------
# Genre classifier (v131.0)
# ---------------------------------------------------------------------------

# Genre profiles: weighted feature vectors for classification.
# Each genre has expected distributions for root motion, chord quality mix,
# progression length, tension level, and characteristic intervals.
_GENRE_PROFILES: dict[str, dict] = {
    "blues": {
        "quality_weights": {"dom7": 0.9, "min7": 0.3, "maj": 0.1},
        "root_motion": {5: 0.4, 7: 0.3, 0: 0.2},  # IV, V, I motion
        "typical_lengths": [12, 24],
        "tension_bias": 0.5,
        "seventh_ratio_min": 0.4,  # blues uses lots of 7th chords
    },
    "jazz": {
        "quality_weights": {"maj7": 0.7, "min7": 0.8, "dom7": 0.6, "dim7": 0.4, "min7b5": 0.5},
        "root_motion": {5: 0.5, 7: 0.4, 2: 0.3},  # ii-V-I motion (down 5th)
        "typical_lengths": [4, 8, 16, 32],
        "tension_bias": 0.6,
        "seventh_ratio_min": 0.5,
    },
    "pop": {
        "quality_weights": {"maj": 0.8, "min": 0.6, "dom7": 0.1},
        "root_motion": {7: 0.4, 5: 0.3, 2: 0.2, 3: 0.2},
        "typical_lengths": [4, 8],
        "tension_bias": 0.3,
        "seventh_ratio_min": 0.0,
    },
    "rock": {
        "quality_weights": {"maj": 0.7, "min": 0.4, "sus4": 0.3, "dom7": 0.2},
        "root_motion": {7: 0.4, 5: 0.3, 2: 0.3, 10: 0.2},  # bVII motion
        "typical_lengths": [4, 8],
        "tension_bias": 0.4,
        "seventh_ratio_min": 0.0,
    },
    "classical": {
        "quality_weights": {"maj": 0.6, "min": 0.5, "dim": 0.3, "aug": 0.1},
        "root_motion": {7: 0.5, 5: 0.4, 2: 0.2},  # V-I, IV-I
        "typical_lengths": [4, 8, 16],
        "tension_bias": 0.4,
        "seventh_ratio_min": 0.0,
    },
    "r&b": {
        "quality_weights": {"min7": 0.7, "maj7": 0.6, "dom7": 0.4, "min9": 0.4, "maj9": 0.3},
        "root_motion": {5: 0.3, 7: 0.3, 2: 0.3, 3: 0.2},
        "typical_lengths": [4, 8],
        "tension_bias": 0.5,
        "seventh_ratio_min": 0.3,
    },
    "latin": {
        "quality_weights": {"min": 0.6, "maj": 0.6, "dom7": 0.5, "min7": 0.4},
        "root_motion": {7: 0.3, 5: 0.3, 3: 0.3, 10: 0.3},
        "typical_lengths": [4, 8],
        "tension_bias": 0.4,
        "seventh_ratio_min": 0.1,
    },
    "ambient": {
        "quality_weights": {"sus2": 0.6, "sus4": 0.5, "maj7": 0.5, "min7": 0.4, "maj": 0.3},
        "root_motion": {7: 0.2, 5: 0.2, 2: 0.2},  # sparse, slow motion
        "typical_lengths": [2, 4],
        "tension_bias": 0.2,
        "seventh_ratio_min": 0.0,
    },
    "electronic": {
        "quality_weights": {"min": 0.7, "maj": 0.4, "min7": 0.3},
        "root_motion": {7: 0.3, 5: 0.3, 3: 0.3, 2: 0.2},
        "typical_lengths": [4, 8],
        "tension_bias": 0.3,
        "seventh_ratio_min": 0.0,
    },
    "metal": {
        "quality_weights": {"maj": 0.5, "min": 0.6, "dim": 0.3},
        "root_motion": {1: 0.3, 6: 0.3, 7: 0.3, 3: 0.2},  # chromatic, tritone
        "typical_lengths": [4, 8],
        "tension_bias": 0.7,
        "seventh_ratio_min": 0.0,
    },
}


def classify_genre(
    progression: list[tuple[str, str]],
    bpm: float | None = None,
    swing: float = 0.0,
) -> dict:
    """Classify the likely genre of a chord progression.

    Uses weighted scoring across multiple features: chord quality
    distribution, root motion patterns, progression length, tension
    profile, and optional tempo/swing hints. No ML dependencies —
    pure rule-based scoring against 10 genre profiles.

    Args:
        progression: List of (root, shape) tuples.
        bpm:         Optional tempo hint (helps distinguish genres).
        swing:       Swing amount (0.0=straight, 0.5+=swing). Helps
                     identify jazz/blues vs electronic/rock.

    Returns:
        Dict with keys:
            genre:       Top predicted genre string.
            confidence:  Score for top genre (0.0-1.0).
            scores:      Dict of all genre scores.
            features:    Extracted feature dict (for inspection).

    Example::

        >>> classify_genre([("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")])
        {'genre': 'pop', 'confidence': 0.82, 'scores': {...}, 'features': {...}}
        >>> classify_genre([("C", "dom7"), ("F", "dom7"), ("G", "dom7")], bpm=120, swing=0.5)
        {'genre': 'blues', 'confidence': 0.78, ...}
    """
    if not progression:
        return {"genre": "unknown", "confidence": 0.0, "scores": {}, "features": {}}

    # --- Extract features ---

    # 1. Chord quality distribution
    quality_counts: dict[str, int] = {}
    for _, shape in progression:
        quality_counts[shape] = quality_counts.get(shape, 0) + 1
    total_chords = len(progression)

    # 2. Root motion histogram (intervals between successive roots)
    root_motions: dict[int, int] = {}
    for i in range(1, len(progression)):
        a = _semi(progression[i - 1][0])
        b = _semi(progression[i][0])
        motion = (b - a) % 12
        root_motions[motion] = root_motions.get(motion, 0) + 1
    motion_total = max(sum(root_motions.values()), 1)

    # 3. Seventh chord ratio
    seventh_shapes = {"dom7", "maj7", "min7", "dim7", "min7b5", "dom9", "min9", "maj9"}
    seventh_count = sum(v for k, v in quality_counts.items() if k in seventh_shapes)
    seventh_ratio = seventh_count / total_chords

    # 4. Tension score (based on dissonant intervals in chord types)
    tension_shapes = {"dom7", "dim", "dim7", "aug", "min7b5"}
    tension_count = sum(v for k, v in quality_counts.items() if k in tension_shapes)
    tension_ratio = tension_count / total_chords

    # 5. Unique roots / chromatic diversity
    unique_roots = len({_semi(root) for root, _ in progression})
    root_diversity = unique_roots / 12.0

    features = {
        "quality_counts": quality_counts,
        "root_motions": root_motions,
        "seventh_ratio": round(seventh_ratio, 3),
        "tension_ratio": round(tension_ratio, 3),
        "root_diversity": round(root_diversity, 3),
        "chord_count": total_chords,
    }

    # --- Score each genre ---
    scores: dict[str, float] = {}
    for genre, profile in _GENRE_PROFILES.items():
        score = 0.0

        # Quality match: how well do the chord qualities match this genre?
        quality_score = 0.0
        for shape, count in quality_counts.items():
            weight = profile["quality_weights"].get(shape, 0.0)
            quality_score += weight * (count / total_chords)
        # Penalize shapes the genre doesn't expect
        unexpected = sum(
            count / total_chords
            for shape, count in quality_counts.items()
            if shape not in profile["quality_weights"]
        )
        quality_score -= unexpected * 0.2
        score += max(0, quality_score) * 3.0  # quality is the strongest signal

        # Root motion match
        motion_score = 0.0
        for interval, expected_weight in profile["root_motion"].items():
            actual = root_motions.get(interval, 0) / motion_total
            motion_score += min(actual, expected_weight) * expected_weight
        score += motion_score * 2.0

        # Progression length match
        length_score = 0.0
        for tl in profile["typical_lengths"]:
            if total_chords == tl or total_chords % tl == 0:
                length_score = 0.3
                break
            elif abs(total_chords - tl) <= 2:
                length_score = 0.15
        score += length_score

        # Tension profile match
        tension_diff = abs(tension_ratio - profile["tension_bias"])
        score += max(0, 0.4 - tension_diff) * 1.5

        # Seventh ratio threshold
        if seventh_ratio >= profile["seventh_ratio_min"]:
            score += 0.2
        elif profile["seventh_ratio_min"] > 0:
            score -= 0.3  # penalize jazz/blues/r&b if no sevenths

        # BPM hints
        if bpm is not None:
            bpm_ranges = {
                "blues": (70, 160),
                "jazz": (100, 300),
                "pop": (90, 140),
                "rock": (100, 180),
                "classical": (50, 180),
                "r&b": (60, 110),
                "latin": (90, 140),
                "ambient": (40, 90),
                "electronic": (115, 145),
                "metal": (100, 220),
            }
            lo, hi = bpm_ranges.get(genre, (60, 200))
            if lo <= bpm <= hi:
                score += 0.3
            elif bpm < lo - 20 or bpm > hi + 20:
                score -= 0.2

        # Swing hint
        if swing >= 0.4:
            if genre in ("jazz", "blues", "r&b"):
                score += 0.4
            elif genre in ("electronic", "metal", "rock"):
                score -= 0.3

        scores[genre] = round(max(0, score), 3)

    # Normalize to 0-1
    max_score = max(scores.values()) if scores else 1.0
    if max_score > 0:
        scores = {k: round(v / max_score, 3) for k, v in scores.items()}

    best_genre = max(scores, key=lambda g: scores[g])
    return {
        "genre": best_genre,
        "confidence": scores[best_genre],
        "scores": dict(sorted(scores.items(), key=lambda x: -x[1])),
        "features": features,
    }


# ---------------------------------------------------------------------------
# Tension narrative (v133.0)
# ---------------------------------------------------------------------------


def tension_story(
    progression: list[tuple[str, str]],
    key: str = "C",
    bars_per_chord: int = 1,
) -> str:
    """Describe a song's tension arc in natural language.

    Reads the tension curve, functional analysis, and cadence detection
    to generate a plain-English narrative of how the harmonic story
    unfolds. The kind of description a theory teacher would write
    on a student's analysis worksheet.

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.
        bars_per_chord: Bars per chord (for bar numbering).

    Returns:
        A multi-sentence narrative string.

    Example::

        >>> prog = [("C","maj"),("F","maj"),("G","dom7"),("C","maj")]
        >>> print(tension_story(prog, "C"))
        Opens with stable tonic (C maj). ...
    """
    if not progression:
        return "Empty progression — no harmonic content to analyze."

    if len(progression) == 1:
        root, shape = progression[0]
        return f"Single chord: {root} {shape}. Static harmony, no tension arc."

    curve = tension_curve(progression, key)
    func = functional_analysis(progression, key)
    cadences = detect_cadences(progression, key)

    # Phase detection: split curve into segments
    segments: list[str] = []
    n = len(curve)

    # Opening
    _func_labels = {"T": "tonic", "S": "subdominant", "D": "dominant", "chromatic": "chromatic"}
    opening_t = curve[0]
    opening_func = func[0] if func else {}
    root0, shape0 = progression[0]
    func_word = _func_labels.get(opening_func.get("function", ""), "tonic")
    if opening_t < 0.2:
        segments.append(f"Opens with stable {func_word} ({root0} {shape0}).")
    elif opening_t < 0.4:
        segments.append(f"Opens with mild tension on {root0} {shape0}.")
    else:
        segments.append(
            f"Opens with high tension on {root0} {shape0} — an unusual, attention-grabbing start."
        )

    # Scan for tension arcs: rising, falling, climax
    if n >= 4:
        # Find the peak
        peak_idx = curve.index(max(curve))
        peak_bar = (peak_idx + 1) * bars_per_chord
        peak_root, peak_shape = progression[peak_idx]

        # Describe approach to peak
        if peak_idx > 0:
            pre_peak = curve[:peak_idx]
            if all(
                pre_peak[i] <= pre_peak[i + 1]
                for i in range(len(pre_peak) - 1)
                if len(pre_peak) > 1
            ):
                segments.append(f"Tension builds steadily through the first {peak_idx} chords.")
            elif peak_idx > 2:
                rises = sum(1 for i in range(1, peak_idx) if curve[i] > curve[i - 1])
                if rises > peak_idx // 2:
                    segments.append(f"Tension generally rises toward bar {peak_bar}.")

        # Describe the climax
        if max(curve) > 0.5:
            segments.append(
                f"Climax at bar {peak_bar} on {peak_root} {peak_shape} "
                f"(tension: {curve[peak_idx]:.2f})."
            )
        elif max(curve) > 0.3:
            segments.append(f"Moderate peak at bar {peak_bar} on {peak_root} {peak_shape}.")

        # Post-peak
        if peak_idx < n - 1:
            post_peak = curve[peak_idx:]
            if all(post_peak[i] >= post_peak[i + 1] for i in range(len(post_peak) - 1)):
                segments.append("Tension releases smoothly after the climax.")
            elif curve[-1] < curve[peak_idx]:
                segments.append("Tension eases toward the end.")

    # Describe cadences found
    if cadences:
        for cad in cadences[:2]:  # limit to 2 cadences in the narrative
            ctype = cad.get("type", "cadence")
            pos = cad.get("position", 0)
            bar = (pos + 1) * bars_per_chord
            if "perfect" in ctype.lower() or "authentic" in ctype.lower():
                segments.append(
                    f"Resolves with a {ctype} at bar {bar} — strong, satisfying closure."
                )
            elif "half" in ctype.lower():
                segments.append(
                    f"Half cadence at bar {bar} — pause on the dominant, expecting more."
                )
            elif "deceptive" in ctype.lower():
                segments.append(
                    f"Deceptive cadence at bar {bar} — the expected resolution is denied."
                )
            elif "plagal" in ctype.lower():
                segments.append(f"Plagal cadence at bar {bar} — the warm 'amen' ending.")
            else:
                segments.append(f"{ctype.title()} at bar {bar}.")

    # Ending
    end_t = curve[-1]
    end_root, end_shape = progression[-1]
    if end_t < 0.15:
        segments.append(f"Ends resolved on {end_root} {end_shape} — complete harmonic rest.")
    elif end_t < 0.3:
        segments.append(
            f"Ends with mild tension on {end_root} {end_shape} — "
            "slightly open, inviting continuation."
        )
    else:
        segments.append(
            f"Ends unresolved on {end_root} {end_shape} "
            f"(tension: {end_t:.2f}) — "
            "deliberately ambiguous or transitional."
        )

    # Overall shape
    avg_t = sum(curve) / n
    if avg_t < 0.2:
        segments.append("Overall: a calm, restful progression.")
    elif avg_t < 0.35:
        segments.append("Overall: moderate harmonic motion with clear direction.")
    elif avg_t < 0.5:
        segments.append("Overall: substantial harmonic activity and tension.")
    else:
        segments.append("Overall: high-tension, chromatically adventurous writing.")

    return " ".join(segments)


# ---------------------------------------------------------------------------
# Composition critique (v134.0)
# ---------------------------------------------------------------------------


def critique(
    progression: list[tuple[str, str]],
    melody: list[Note] | None = None,
    key: str = "C",
) -> dict:
    """Automated music theory review of a progression (and optional melody).

    Checks for common theory violations and quality indicators:
    parallel fifths/octaves, unresolved dominant, missing cadence,
    harmonic variety, voice range, and tension balance. Returns a
    graded report with a score and specific suggestions.

    The theory professor in a function call — honest, thorough, and
    occasionally blunt.

    Args:
        progression: List of (root, shape) tuples.
        melody:      Optional melody notes for melodic analysis.
        key:         Key for harmonic analysis.

    Returns:
        Dict with keys:
            score:       0-100 grade.
            grade:       Letter grade (A/B/C/D/F).
            issues:      List of issue strings found.
            strengths:   List of positive observations.
            suggestions: List of improvement suggestions.

    Example::

        >>> result = critique([("C","maj"),("G","dom7"),("C","maj")], key="C")
        >>> result["grade"]
        'B'
    """
    issues: list[str] = []
    strengths: list[str] = []
    suggestions: list[str] = []
    score = 100

    if not progression:
        return {
            "score": 0,
            "grade": "F",
            "issues": ["Empty progression — no content to evaluate."],
            "strengths": [],
            "suggestions": ["Write some chords first."],
        }

    # --- Harmonic checks ---

    # 1. Variety: how many unique chords?
    unique_chords = len(set(progression))
    if unique_chords == 1:
        issues.append("Only one chord used — static harmony.")
        score -= 20
        suggestions.append("Add at least a IV or V chord for harmonic motion.")
    elif unique_chords <= 2 and len(progression) >= 4:
        issues.append(f"Low chord variety ({unique_chords} unique in {len(progression)} chords).")
        score -= 10
        suggestions.append("Try adding a ii or vi chord for more color.")
    elif unique_chords >= 4:
        strengths.append(f"Good harmonic variety ({unique_chords} unique chords).")

    # 2. Quality variety: all triads? all 7ths?
    shapes = set(shape for _, shape in progression)
    if len(shapes) == 1 and len(progression) >= 4:
        issues.append(f"All chords are {next(iter(shapes))} — monotonous quality.")
        score -= 5
        suggestions.append("Mix chord qualities (e.g. add a dominant 7th or minor chord).")

    # 3. Cadence presence
    cadences = detect_cadences(progression, key)
    if not cadences and len(progression) >= 4:
        issues.append("No recognizable cadence found.")
        score -= 10
        suggestions.append("End with V-I (authentic) or IV-I (plagal) for closure.")
    elif cadences:
        cad_types = [c.get("type", "unknown") for c in cadences]
        strengths.append(f"Cadence(s) detected: {', '.join(cad_types)}.")

    # 4. Unresolved dominant: does the last chord leave tension?
    curve = tension_curve(progression, key)
    if curve and curve[-1] > 0.4:
        issues.append(f"Ends on high tension ({curve[-1]:.2f}) — unresolved.")
        score -= 8
        suggestions.append("Resolve to tonic (I) at the end for a sense of completion.")
    elif curve and curve[-1] < 0.2:
        strengths.append("Clean tonic resolution at the end.")

    # 5. Tension arc: is there a climax?
    if len(curve) >= 4:
        max_t = max(curve)
        min_t = min(curve)
        if max_t - min_t < 0.1:
            issues.append("Flat tension curve — no dramatic arc.")
            score -= 8
            suggestions.append("Build tension toward a climax (use V7, viio, or chromatic chords).")
        elif max_t > 0.4:
            strengths.append(f"Good tension arc (peak: {max_t:.2f}).")

    # 6. Key consistency
    detected_key = detect_key(progression)
    if detected_key != key:
        issues.append(f"Detected key ({detected_key}) differs from stated key ({key}).")
        score -= 5
        suggestions.append(
            f"Consider analyzing in {detected_key} instead, or reinforce {key} with V-I."
        )

    # 7. Functional balance
    func = functional_analysis(progression, key)
    func_counts: dict[str, int] = {}
    for f in func:
        func_counts[f["function"]] = func_counts.get(f["function"], 0) + 1

    total_func = sum(func_counts.values())
    if total_func > 0:
        dom_ratio = func_counts.get("D", 0) / total_func
        tonic_ratio = func_counts.get("T", 0) / total_func
        if dom_ratio > 0.5:
            issues.append("Too many dominant-function chords — relentless tension.")
            score -= 5
        if tonic_ratio > 0.6 and len(progression) >= 4:
            issues.append("Heavy tonic bias — progression doesn't go anywhere.")
            score -= 5
            suggestions.append("Add subdominant (IV, ii) and dominant (V) motion.")

    # --- Melodic checks (if melody provided) ---
    if melody:
        pitched = [n for n in melody if n.pitch is not None]

        # 8. Range check
        if pitched:
            midi_vals = [_semi(str(n.pitch)) + n.octave * 12 for n in pitched]
            span = max(midi_vals) - min(midi_vals)
            if span > 24:
                issues.append(f"Melody spans {span} semitones — may exceed performer range.")
                score -= 5
                suggestions.append("Keep melody within 2 octaves for singability.")
            elif span < 5 and len(pitched) >= 8:
                issues.append("Very narrow melodic range — lacks expressiveness.")
                score -= 5
                suggestions.append(
                    "Expand the range by using step motion to higher/lower registers."
                )
            elif 7 <= span <= 19:
                strengths.append(f"Good melodic range ({span} semitones).")

        # 9. Leap frequency
        if len(pitched) >= 4:
            leaps = 0
            for i in range(1, len(pitched)):
                a = _semi(str(pitched[i - 1].pitch)) + pitched[i - 1].octave * 12
                b = _semi(str(pitched[i].pitch)) + pitched[i].octave * 12
                if abs(b - a) > 4:
                    leaps += 1
            leap_ratio = leaps / (len(pitched) - 1)
            if leap_ratio > 0.6:
                issues.append(f"Too many leaps ({leap_ratio:.0%}) — angular, hard to sing.")
                score -= 5
                suggestions.append("Balance leaps with stepwise motion (seconds/thirds).")
            elif leap_ratio < 0.15:
                strengths.append("Good mix of steps and leaps.")

        # 10. Rest ratio
        rest_count = sum(1 for n in melody if n.pitch is None)
        if len(melody) > 0:
            rr = rest_count / len(melody)
            if rr > 0.4:
                issues.append(f"High rest ratio ({rr:.0%}) — melody feels sparse.")
                score -= 3

    # Clamp and grade
    score = max(0, min(100, score))
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    if not strengths:
        strengths.append("Progression exists — that's a start.")
    if not suggestions and score < 100:
        suggestions.append("Keep writing. Every progression teaches something.")

    return {
        "score": score,
        "grade": grade,
        "issues": issues,
        "strengths": strengths,
        "suggestions": suggestions,
    }


# ---------------------------------------------------------------------------
# Song-Level Critique (v140.0) — Full arrangement analysis
# ---------------------------------------------------------------------------


def critique_song(
    song,
    key: str | None = None,
) -> dict:
    """Comprehensive critique of a complete Song object.

    Extends the progression-level critique() to analyze full arrangements,
    including inter-track voice independence, register usage, instrument
    balance, and arrangement cohesion. The theory professor now reviews
    your entire composition, not just the chord chart.

    Args:
        song: Song to analyze.
        key:  Optional key override. If None, uses song.key_sig.

    Returns:
        Dict with:
            overall_score:    0-100 grade for the entire song.
            overall_grade:    Letter grade (A/B/C/D/F).
            harmony_critique: Standard critique() output for progression.
            tracks:           Per-track analysis dicts.
            arrangement:      Arrangement-level observations.
            issues:           Combined list of all issues found.
            strengths:        Combined list of all strengths.
            suggestions:      Prioritized improvement suggestions.

    Example::

        >>> from code_music import Song, Track, Note, Chord
        >>> song = Song(title="Test", key_sig="C")
        >>> # ... add tracks ...
        >>> result = critique_song(song)
        >>> result["overall_grade"]
        'B'
    """
    from ..engine import Chord, Note

    analysis_key = key or getattr(song, "key_sig", "C") or "C"

    issues: list[str] = []
    strengths: list[str] = []
    suggestions: list[str] = []

    # --- Extract progression from song ---
    progression: list[tuple[str, str]] = []
    for track in song.tracks:
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Chord):
                shape = beat.event.shape if isinstance(beat.event.shape, str) else "maj"
                progression.append((beat.event.root, shape))

    # --- Base harmony critique ---
    harmony_critique = critique(progression, key=analysis_key)

    # --- Per-track analysis ---
    track_analyses: list[dict] = []
    all_notes: list[Note] = []
    track_ranges: list[tuple[int, int]] = []
    track_densities: list[float] = []

    for track in song.tracks:
        track_notes = [
            beat.event
            for beat in track.beats
            if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None
        ]

        if track_notes:
            all_notes.extend(track_notes)

            # Calculate range
            midi_vals = [_semi(str(n.pitch)) + n.octave * 12 for n in track_notes]
            range_min, range_max = min(midi_vals), max(midi_vals)
            track_ranges.append((range_min, range_max))

            # Calculate density (notes per beat)
            total_beats = sum(b.event.duration for b in track.beats if b.event)
            density = len(track_notes) / max(total_beats, 1)
            track_densities.append(density)

            track_analyses.append(
                {
                    "name": track.name,
                    "instrument": track.instrument,
                    "note_count": len(track_notes),
                    "range_semitones": range_max - range_min,
                    "range_midi": (range_min, range_max),
                    "density": round(density, 2),
                }
            )
        else:
            track_analyses.append(
                {
                    "name": track.name,
                    "instrument": track.instrument,
                    "note_count": 0,
                    "range_semitones": 0,
                    "range_midi": None,
                    "density": 0,
                }
            )

    # --- Arrangement analysis ---
    arrangement: dict = {
        "track_count": len(song.tracks),
        "active_tracks": sum(1 for ta in track_analyses if ta["note_count"] > 0),
        "register_overlap": False,
        "voice_independence": 1.0,
        "balance_score": 100,
    }

    # Check for register overlap (voices stepping on each other)
    if len(track_ranges) >= 2:
        for i in range(len(track_ranges)):
            for j in range(i + 1, len(track_ranges)):
                min1, max1 = track_ranges[i]
                min2, max2 = track_ranges[j]
                # Check if ranges overlap significantly (>50% of smaller range)
                overlap_start = max(min1, min2)
                overlap_end = min(max1, max2)
                if overlap_start < overlap_end:
                    overlap_size = overlap_end - overlap_start
                    smaller_range = min(max1 - min1, max2 - min2)
                    if smaller_range > 0 and overlap_size / smaller_range > 0.5:
                        arrangement["register_overlap"] = True
                        issues.append(f"Significant register overlap between tracks {i} and {j}.")

    # Check density balance
    if track_densities:
        max_density = max(track_densities)
        min_density = (
            min(d for d in track_densities if d > 0) if any(d > 0 for d in track_densities) else 0
        )
        if max_density > 0 and min_density > 0:
            density_ratio = max_density / min_density
            if density_ratio > 5:
                arrangement["balance_score"] -= 15
                issues.append("Severe density imbalance — some tracks much busier than others.")
                suggestions.append(
                    "Balance activity across tracks; thin busy tracks or add interest to sparse ones."
                )
            elif density_ratio > 3:
                arrangement["balance_score"] -= 8
                issues.append("Moderate density imbalance between tracks.")

    # Calculate voice independence (are tracks doing different things?)
    if len(track_densities) >= 2:
        # Simple independence metric: variety in density and range
        density_variance = sum(
            (d - sum(track_densities) / len(track_densities)) ** 2 for d in track_densities
        )
        arrangement["voice_independence"] = round(
            min(1.0, density_variance / len(track_densities) + 0.5), 2
        )

    # --- Overall scoring ---
    base_score = harmony_critique["score"]
    arrangement_score = arrangement["balance_score"]

    # Weight: 60% harmony, 40% arrangement
    overall_score = int(base_score * 0.6 + arrangement_score * 0.4)

    # Adjust for track count (bonus for layered writing, penalty for overstuffing)
    active_count = arrangement["active_tracks"]
    if active_count >= 3 and active_count <= 6:
        overall_score += 3
        strengths.append(f"Well-layered arrangement with {active_count} active tracks.")
    elif active_count > 8:
        overall_score -= 5
        issues.append("Very dense arrangement — consider thinning for clarity.")

    # Register spread bonus
    if track_ranges:
        global_min = min(r[0] for r in track_ranges)
        global_max = max(r[1] for r in track_ranges)
        total_span = global_max - global_min
        if total_span >= 36:  # 3+ octaves
            overall_score += 5
            strengths.append("Excellent register spread across the arrangement.")
        elif total_span < 12 and active_count >= 3:
            overall_score -= 5
            issues.append("Narrow overall register — tracks may be crowding the same range.")
            suggestions.append(
                "Use different octaves for different track roles (bass low, melody high)."
            )

    # Clamp score
    overall_score = max(0, min(100, overall_score))

    # Grade
    if overall_score >= 90:
        overall_grade = "A"
    elif overall_score >= 80:
        overall_grade = "B"
    elif overall_score >= 70:
        overall_grade = "C"
    elif overall_score >= 60:
        overall_grade = "D"
    else:
        overall_grade = "F"

    # Combine all feedback
    all_issues = harmony_critique.get("issues", []) + issues
    all_strengths = harmony_critique.get("strengths", []) + strengths
    all_suggestions = harmony_critique.get("suggestions", []) + suggestions

    # Deduplicate
    all_issues = list(dict.fromkeys(all_issues))
    all_strengths = list(dict.fromkeys(all_strengths))
    all_suggestions = list(dict.fromkeys(all_suggestions))

    return {
        "overall_score": overall_score,
        "overall_grade": overall_grade,
        "harmony_critique": harmony_critique,
        "tracks": track_analyses,
        "arrangement": arrangement,
        "issues": all_issues,
        "strengths": all_strengths,
        "suggestions": all_suggestions,
    }


# ---------------------------------------------------------------------------
# Modulation detector (v134.0)
# ---------------------------------------------------------------------------


def detect_modulations(
    progression: list[tuple[str, str]],
    window: int = 4,
) -> list[dict]:
    """Detect key changes within a chord progression.

    Slides a window across the progression, running detect_key on each
    window. When the detected key changes, that's a modulation. Returns
    a timeline of key regions with pivot chord identification.

    Args:
        progression: List of (root, shape) tuples.
        window:      Number of chords per analysis window (default 4).

    Returns:
        List of dicts, each describing a key region:
            key:         Detected key for this region.
            start:       Start chord index (0-based).
            end:         End chord index (exclusive).
            pivot_chord: (root, shape) of the chord at the boundary,
                         or None for the first region.

    Example::

        >>> prog = [("C","maj"),("F","maj"),("G","dom7"),("C","maj"),
        ...         ("G","maj"),("C","maj"),("D","dom7"),("G","maj")]
        >>> mods = detect_modulations(prog, window=4)
        >>> mods[0]["key"]
        'C'
    """
    if len(progression) < window:
        # Too short to detect modulation — treat as one key
        key = detect_key(progression) if progression else "C"
        return [{"key": key, "start": 0, "end": len(progression), "pivot_chord": None}]

    # Slide window and detect key at each position
    key_timeline: list[str] = []
    for i in range(len(progression) - window + 1):
        w = progression[i : i + window]
        key_timeline.append(detect_key(w))

    # Pad end so timeline covers all chords
    while len(key_timeline) < len(progression):
        key_timeline.append(key_timeline[-1])

    # Merge consecutive same-key regions
    regions: list[dict] = []
    current_key = key_timeline[0]
    region_start = 0

    for i in range(1, len(key_timeline)):
        if key_timeline[i] != current_key:
            regions.append(
                {
                    "key": current_key,
                    "start": region_start,
                    "end": i,
                    "pivot_chord": None,
                }
            )
            # The pivot chord is the last chord of the previous region
            # (it's shared between old and new key)
            pivot = progression[i - 1] if i > 0 else None
            current_key = key_timeline[i]
            region_start = i
            # Mark pivot on the new region
            if regions:
                regions[-1]["pivot_chord"] = pivot

    # Final region
    regions.append(
        {
            "key": current_key,
            "start": region_start,
            "end": len(progression),
            "pivot_chord": None,
        }
    )

    # Add pivot chord to regions after the first
    for i in range(1, len(regions)):
        boundary = regions[i]["start"]
        if boundary > 0:
            regions[i]["pivot_chord"] = progression[boundary - 1]

    return regions


# ---------------------------------------------------------------------------
# Melodic similarity search (v135.0)
# ---------------------------------------------------------------------------


def _melody_intervals(notes: list[Note]) -> list[int]:
    """Extract signed interval sequence from pitched notes."""
    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return []
    intervals = []
    for i in range(1, len(pitched)):
        a = _semi(str(pitched[i - 1].pitch)) + pitched[i - 1].octave * 12
        b = _semi(str(pitched[i].pitch)) + pitched[i].octave * 12
        intervals.append(b - a)
    return intervals


def _contour_string(notes: list[Note]) -> str:
    """Extract contour direction string (U/D/R) from pitched notes."""
    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return ""
    dirs = []
    for i in range(1, len(pitched)):
        a = _semi(str(pitched[i - 1].pitch)) + pitched[i - 1].octave * 12
        b = _semi(str(pitched[i].pitch)) + pitched[i].octave * 12
        if b > a:
            dirs.append("U")
        elif b < a:
            dirs.append("D")
        else:
            dirs.append("R")
    return "".join(dirs)


def melody_similarity(
    melody_a: list[Note],
    melody_b: list[Note],
    weights: dict[str, float] | None = None,
) -> float:
    """Compute a similarity score between two melodies (0.0-1.0).

    Combines three features:
    - **Contour similarity**: do the melodies go up/down in the same places?
    - **Interval similarity**: are the interval sizes similar?
    - **Rhythm similarity**: do the durations match?

    Args:
        melody_a: First melody.
        melody_b: Second melody.
        weights:  Optional feature weights dict with keys
                  'contour', 'interval', 'rhythm'. Default: equal.

    Returns:
        Similarity score 0.0 (completely different) to 1.0 (identical).

    Example::

        >>> from code_music.engine import Note
        >>> a = [Note("C",5,1.0), Note("E",5,1.0), Note("G",5,1.0)]
        >>> b = [Note("D",5,1.0), Note("F#",5,1.0), Note("A",5,1.0)]
        >>> melody_similarity(a, b)  # same contour, same intervals
        1.0
    """
    if not melody_a or not melody_b:
        return 0.0

    w = weights or {"contour": 1.0, "interval": 1.0, "rhythm": 1.0}
    total_w = sum(w.values())
    if total_w == 0:
        return 0.0

    # 1. Contour similarity (Levenshtein-lite: fraction of matching directions)
    ca = _contour_string(melody_a)
    cb = _contour_string(melody_b)
    if ca and cb:
        min_len = min(len(ca), len(cb))
        matches = sum(1 for i in range(min_len) if ca[i] == cb[i])
        contour_sim = matches / max(len(ca), len(cb))
    elif not ca and not cb:
        contour_sim = 1.0
    else:
        contour_sim = 0.0

    # 2. Interval similarity (cosine-like on interval sequences)
    ia = _melody_intervals(melody_a)
    ib = _melody_intervals(melody_b)
    if ia and ib:
        min_len = min(len(ia), len(ib))
        max_len = max(len(ia), len(ib))
        diffs = sum(abs(ia[i] - ib[i]) for i in range(min_len))
        # Normalize: 12 semitones = completely different per step
        interval_sim = max(0.0, 1.0 - diffs / (max_len * 12))
    elif not ia and not ib:
        interval_sim = 1.0
    else:
        interval_sim = 0.0

    # 3. Rhythm similarity (duration pattern match)
    da = [n.duration for n in melody_a if n.pitch is not None]
    db = [n.duration for n in melody_b if n.pitch is not None]
    if da and db:
        min_len = min(len(da), len(db))
        max_len = max(len(da), len(db))
        dur_diffs = sum(abs(da[i] - db[i]) for i in range(min_len))
        # Normalize: 4.0 beats = max reasonable difference per note
        rhythm_sim = max(0.0, 1.0 - dur_diffs / (max_len * 4.0))
    elif not da and not db:
        rhythm_sim = 1.0
    else:
        rhythm_sim = 0.0

    # Weighted combination
    score = (
        w.get("contour", 1.0) * contour_sim
        + w.get("interval", 1.0) * interval_sim
        + w.get("rhythm", 1.0) * rhythm_sim
    ) / total_w

    return round(min(1.0, max(0.0, score)), 3)


def find_similar_melodies(
    query: list[Note],
    corpus: list[tuple[str, list[Note]]],
    top_k: int = 5,
    min_score: float = 0.0,
) -> list[dict]:
    """Search a corpus of melodies for those most similar to a query.

    Uses melody_similarity to score each corpus entry against the query,
    then returns the top-k results sorted by descending similarity.

    Args:
        query:     The melody to search for.
        corpus:    List of (name, melody) tuples to search.
        top_k:     Maximum results to return.
        min_score: Minimum similarity threshold (0.0-1.0).

    Returns:
        List of dicts sorted by similarity (descending):
            name:       Corpus entry name.
            score:      Similarity score (0.0-1.0).
            melody:     The matched melody.

    Example::

        >>> from code_music.engine import Note
        >>> query = [Note("C",5,1.0), Note("E",5,1.0), Note("G",5,1.0)]
        >>> corpus = [("rising", [Note("D",5,1.0), Note("F#",5,1.0), Note("A",5,1.0)]),
        ...           ("falling", [Note("G",5,1.0), Note("E",5,1.0), Note("C",5,1.0)])]
        >>> results = find_similar_melodies(query, corpus, top_k=2)
        >>> results[0]["name"]
        'rising'
    """
    if not query or not corpus:
        return []

    scored: list[dict] = []
    for name, melody in corpus:
        sim = melody_similarity(query, melody)
        if sim >= min_score:
            scored.append({"name": name, "score": sim, "melody": melody})

    scored.sort(key=lambda x: -x["score"])
    return scored[:top_k]


# ---------------------------------------------------------------------------
# Style Fingerprint (v136.0)
# ---------------------------------------------------------------------------


def style_fingerprint(
    song,
) -> dict:
    """Compute a multi-dimensional feature vector for a Song.

    Captures the musical DNA of a song across 8 dimensions: harmonic,
    melodic, rhythmic, timbral, dynamic, structural, register, and
    density. Two songs with similar fingerprints share a similar feel.
    Use for clustering, recommendation, or style comparison.

    Args:
        song: Song object to fingerprint.

    Returns:
        Dict with feature categories, each containing numeric values:
            harmonic:   root_diversity, quality_diversity, tension_mean,
                        tension_range, cadence_count, key_stability.
            melodic:    pitch_range, avg_interval, step_ratio,
                        leap_ratio, rest_ratio, contour_direction.
            rhythmic:   avg_duration, duration_variety, density,
                        swing_amount, syncopation_estimate.
            timbral:    instrument_count, unique_instruments,
                        has_percussion, has_bass, has_melody.
            dynamic:    velocity_mean, velocity_range, velocity_std,
                        has_crescendo, has_decrescendo.
            structural: track_count, total_beats, total_bars,
                        section_count_estimate.
            register:   lowest_midi, highest_midi, avg_midi,
                        register_span.
            density:    notes_per_beat, chords_per_beat,
                        rests_per_beat, overall_density.
            vector:     Flat list of all numeric values (for distance).

    Example::

        >>> from code_music import Song, Track, Note, Chord
        >>> song = Song(title="Test", bpm=120)
        >>> tr = song.add_track(Track())
        >>> tr.add(Note("C", 4, 1.0))
        >>> fp = style_fingerprint(song)
        >>> "harmonic" in fp and "vector" in fp
        True
    """
    import math

    from ..engine import Chord, Note

    # Collect all notes and chords
    all_notes: list[Note] = []
    all_chords: list[tuple[str, str]] = []
    all_velocities: list[float] = []
    all_durations: list[float] = []
    instruments: list[str] = []
    rest_count = 0
    total_events = 0

    for track in song.tracks:
        instruments.append(track.instrument)
        for beat in track.beats:
            total_events += 1
            if beat.event is None:
                rest_count += 1
            elif isinstance(beat.event, Note):
                if beat.event.pitch is not None:
                    all_notes.append(beat.event)
                    all_velocities.append(beat.event.velocity)
                    all_durations.append(beat.event.duration)
                else:
                    rest_count += 1
            elif isinstance(beat.event, Chord):
                shape = beat.event.shape if isinstance(beat.event.shape, str) else "maj"
                all_chords.append((beat.event.root, shape))
                all_velocities.append(beat.event.velocity)
                all_durations.append(beat.event.duration)

    total_beats = getattr(song, "total_beats", 0) or 1
    total_events = max(total_events, 1)

    # --- Harmonic features ---
    roots = set(r for r, _ in all_chords)
    qualities = set(s for _, s in all_chords)
    root_diversity = len(roots) / max(len(all_chords), 1)
    quality_diversity = len(qualities) / max(len(all_chords), 1)

    tension_vals: list[float] = []
    if all_chords:
        analysis_key = getattr(song, "key_sig", "C") or "C"
        try:
            from .harmony import tension_curve

            tension_vals = tension_curve(all_chords, key=analysis_key)
        except Exception:
            tension_vals = [0.5] * len(all_chords)

    tension_mean = sum(tension_vals) / max(len(tension_vals), 1)
    tension_range = (max(tension_vals) - min(tension_vals)) if tension_vals else 0.0

    cadence_count = 0
    if all_chords:
        try:
            from .harmony import detect_cadences

            cadence_count = len(detect_cadences(all_chords, getattr(song, "key_sig", "C") or "C"))
        except Exception:
            pass

    key_stability = 1.0
    if all_chords:
        try:
            from .harmony import detect_key as _dk

            _, _, conf = _dk(all_chords)
            key_stability = conf
        except Exception:
            pass

    harmonic = {
        "root_diversity": round(root_diversity, 4),
        "quality_diversity": round(quality_diversity, 4),
        "tension_mean": round(tension_mean, 4),
        "tension_range": round(tension_range, 4),
        "cadence_count": cadence_count,
        "key_stability": round(key_stability, 4),
    }

    # --- Melodic features ---
    midi_vals = []
    intervals = []
    for n in all_notes:
        try:
            m = _semi(str(n.pitch)) + n.octave * 12
            midi_vals.append(m)
        except Exception:
            pass

    for i in range(1, len(midi_vals)):
        intervals.append(abs(midi_vals[i] - midi_vals[i - 1]))

    pitch_range = (max(midi_vals) - min(midi_vals)) if midi_vals else 0
    avg_interval = sum(intervals) / max(len(intervals), 1)
    steps = sum(1 for iv in intervals if iv <= 2)
    leaps = sum(1 for iv in intervals if iv > 4)
    step_ratio = steps / max(len(intervals), 1)
    leap_ratio = leaps / max(len(intervals), 1)
    rest_ratio = rest_count / total_events

    # Contour direction: positive = ascending, negative = descending
    contour_dir = 0.0
    if len(midi_vals) >= 2:
        ups = sum(1 for i in range(1, len(midi_vals)) if midi_vals[i] > midi_vals[i - 1])
        downs = sum(1 for i in range(1, len(midi_vals)) if midi_vals[i] < midi_vals[i - 1])
        total_motion = ups + downs
        contour_dir = (ups - downs) / max(total_motion, 1)

    melodic = {
        "pitch_range": pitch_range,
        "avg_interval": round(avg_interval, 4),
        "step_ratio": round(step_ratio, 4),
        "leap_ratio": round(leap_ratio, 4),
        "rest_ratio": round(rest_ratio, 4),
        "contour_direction": round(contour_dir, 4),
    }

    # --- Rhythmic features ---
    avg_dur = sum(all_durations) / max(len(all_durations), 1)
    dur_set = set(round(d, 3) for d in all_durations)
    dur_variety = len(dur_set) / max(len(all_durations), 1)
    density = (len(all_notes) + len(all_chords)) / total_beats
    swing_amount = max((t.swing for t in song.tracks), default=0.0)

    # Syncopation estimate: notes with odd-beat durations
    syncopation = 0
    for d in all_durations:
        frac = d - int(d)
        if 0.1 < frac < 0.9:
            syncopation += 1
    syncopation_est = syncopation / max(len(all_durations), 1)

    rhythmic = {
        "avg_duration": round(avg_dur, 4),
        "duration_variety": round(dur_variety, 4),
        "density": round(density, 4),
        "swing_amount": round(swing_amount, 4),
        "syncopation_estimate": round(syncopation_est, 4),
    }

    # --- Timbral features ---
    unique_instr = set(instruments)
    perc_names = {"drums_kick", "drums_snare", "drums_hat", "percussion"}
    bass_names = {"bass", "sub_bass", "sub_808"}
    melody_names = {"sawtooth", "sine", "square", "triangle", "piano", "organ", "pluck"}

    timbral = {
        "instrument_count": len(instruments),
        "unique_instruments": len(unique_instr),
        "has_percussion": 1.0 if unique_instr & perc_names else 0.0,
        "has_bass": 1.0 if unique_instr & bass_names else 0.0,
        "has_melody": 1.0 if unique_instr & melody_names else 0.0,
    }

    # --- Dynamic features ---
    vel_mean = sum(all_velocities) / max(len(all_velocities), 1)
    vel_range = (max(all_velocities) - min(all_velocities)) if all_velocities else 0.0
    vel_std = 0.0
    if len(all_velocities) > 1:
        vel_std = math.sqrt(sum((v - vel_mean) ** 2 for v in all_velocities) / len(all_velocities))

    # Detect crescendo/decrescendo by checking velocity trend
    has_cresc = 0.0
    has_decresc = 0.0
    if len(all_velocities) >= 4:
        half = len(all_velocities) // 2
        first_half_avg = sum(all_velocities[:half]) / half
        second_half_avg = sum(all_velocities[half:]) / (len(all_velocities) - half)
        if second_half_avg > first_half_avg + 0.05:
            has_cresc = 1.0
        if first_half_avg > second_half_avg + 0.05:
            has_decresc = 1.0

    dynamic = {
        "velocity_mean": round(vel_mean, 4),
        "velocity_range": round(vel_range, 4),
        "velocity_std": round(vel_std, 4),
        "has_crescendo": has_cresc,
        "has_decrescendo": has_decresc,
    }

    # --- Structural features ---
    num, den = getattr(song, "time_sig", (4, 4))
    beats_per_bar = num * 4 / den
    total_bars = total_beats / beats_per_bar if beats_per_bar else 0

    # Estimate sections by looking for repeated patterns in chord progression
    section_est = 1
    if len(all_chords) >= 8:
        section_est = max(1, len(all_chords) // 4)

    structural = {
        "track_count": len(song.tracks),
        "total_beats": round(total_beats, 2),
        "total_bars": round(total_bars, 2),
        "section_count_estimate": section_est,
    }

    # --- Register features ---
    register = {
        "lowest_midi": min(midi_vals) if midi_vals else 0,
        "highest_midi": max(midi_vals) if midi_vals else 0,
        "avg_midi": round(sum(midi_vals) / max(len(midi_vals), 1), 2),
        "register_span": pitch_range,
    }

    # --- Density features ---
    notes_per_beat = len(all_notes) / total_beats
    chords_per_beat = len(all_chords) / total_beats
    rests_per_beat = rest_count / total_beats
    overall_density = (len(all_notes) + len(all_chords)) / total_beats

    density_features = {
        "notes_per_beat": round(notes_per_beat, 4),
        "chords_per_beat": round(chords_per_beat, 4),
        "rests_per_beat": round(rests_per_beat, 4),
        "overall_density": round(overall_density, 4),
    }

    # --- Build flat vector for distance computation ---
    vector: list[float] = []
    for category in [
        harmonic,
        melodic,
        rhythmic,
        timbral,
        dynamic,
        structural,
        register,
        density_features,
    ]:
        for v in category.values():
            vector.append(float(v))

    return {
        "harmonic": harmonic,
        "melodic": melodic,
        "rhythmic": rhythmic,
        "timbral": timbral,
        "dynamic": dynamic,
        "structural": structural,
        "register": register,
        "density": density_features,
        "vector": vector,
    }


# ---------------------------------------------------------------------------
# Arrangement Analyzer (v136.0)
# ---------------------------------------------------------------------------


def analyze_arrangement(
    song,
) -> dict:
    """Analyze the arrangement of a Song - track roles, register usage,
    instrument density, voice crossing, and instrument range compliance.

    The arrangement review that a producer gives before mixing: which
    track is doing what job, where they overlap, and where the gaps are.

    Args:
        song: Song object to analyze.

    Returns:
        Dict with:
            tracks:          Per-track analysis (role, range, density, register).
            roles:           Detected roles dict: melody, bass, pad, rhythm, other.
            register_usage:  Which octave ranges are covered/empty.
            voice_crossings: List of beat positions where tracks cross registers.
            range_violations: Tracks playing outside instrument standard range.
            frequency_balance: Low/mid/high register distribution.
            suggestions:     List of arrangement improvement suggestions.
            score:           0-100 arrangement quality score.

    Example::

        >>> from code_music import Song, Track, Note
        >>> song = Song(title="Test", bpm=120)
        >>> tr = song.add_track(Track(name="lead", instrument="piano"))
        >>> tr.add(Note("C", 5, 2.0))
        >>> result = analyze_arrangement(song)
        >>> "tracks" in result and "score" in result
        True
    """
    from ..engine import Chord, Note

    issues: list[str] = []
    suggestions: list[str] = []

    # --- Per-track analysis ---
    track_analyses: list[dict] = []
    role_map: dict[str, list[str]] = {
        "melody": [],
        "bass": [],
        "pad": [],
        "rhythm": [],
        "other": [],
    }

    # Instrument role heuristics
    _bass_instruments = {"bass", "sub_bass", "sub_808", "fm_bass"}
    _pad_instruments = {"pad", "organ", "vocal_pad", "strings", "wt_morph_pad"}
    _rhythm_instruments = {"drums_kick", "drums_snare", "drums_hat", "percussion"}
    _melody_instruments = {
        "sawtooth",
        "sine",
        "square",
        "triangle",
        "piano",
        "pluck",
        "fm_electric_piano",
        "fm_bell",
        "wt_bright_lead",
    }

    all_track_midis: list[list[int]] = []

    for track in song.tracks:
        notes = []
        midi_vals = []
        total_dur = 0.0
        note_count = 0
        rest_count = 0

        for beat in track.beats:
            total_dur += beat.duration
            if beat.event is None:
                rest_count += 1
            elif isinstance(beat.event, Note):
                if beat.event.pitch is not None:
                    notes.append(beat.event)
                    note_count += 1
                    try:
                        m = _semi(str(beat.event.pitch)) + beat.event.octave * 12
                        midi_vals.append(m)
                    except Exception:
                        pass
                else:
                    rest_count += 1
            elif isinstance(beat.event, Chord):
                note_count += 1
                for cn in beat.event.notes:
                    try:
                        m = _semi(str(cn.pitch)) + cn.octave * 12
                        midi_vals.append(m)
                    except Exception:
                        pass

        all_track_midis.append(midi_vals)

        # Determine role
        instr = track.instrument
        if instr in _rhythm_instruments:
            role = "rhythm"
        elif instr in _bass_instruments:
            role = "bass"
        elif instr in _pad_instruments:
            role = "pad"
        elif instr in _melody_instruments:
            role = "melody"
        else:
            # Heuristic: high register + short notes = melody
            avg_midi = sum(midi_vals) / max(len(midi_vals), 1) if midi_vals else 60
            avg_dur = sum(n.duration for n in notes) / max(len(notes), 1) if notes else 1
            if avg_midi >= 60 and avg_dur <= 1.0:
                role = "melody"
            elif avg_midi < 48:
                role = "bass"
            elif avg_dur >= 2.0:
                role = "pad"
            else:
                role = "other"

        role_map[role].append(track.name)

        # Register classification
        register = "mid"
        if midi_vals:
            avg = sum(midi_vals) / len(midi_vals)
            if avg < 48:
                register = "low"
            elif avg > 72:
                register = "high"

        density = note_count / max(total_dur, 1)

        track_analyses.append(
            {
                "name": track.name,
                "instrument": track.instrument,
                "role": role,
                "register": register,
                "note_count": note_count,
                "rest_count": rest_count,
                "density": round(density, 4),
                "midi_range": (min(midi_vals), max(midi_vals)) if midi_vals else (0, 0),
                "avg_midi": round(sum(midi_vals) / max(len(midi_vals), 1), 2) if midi_vals else 0,
            }
        )

    # --- Voice crossings ---
    crossings: list[dict] = []
    if len(all_track_midis) >= 2:
        # Compare adjacent tracks by role (e.g., bass should not go above melody)
        for i in range(len(all_track_midis)):
            for j in range(i + 1, len(all_track_midis)):
                midis_a = all_track_midis[i]
                midis_b = all_track_midis[j]
                if not midis_a or not midis_b:
                    continue
                avg_a = sum(midis_a) / len(midis_a)
                avg_b = sum(midis_b) / len(midis_b)
                # Check if the "lower" track has notes above the "upper" track
                if avg_a < avg_b:
                    crossing_notes = sum(1 for m in midis_a if m > avg_b + 6)
                else:
                    crossing_notes = sum(1 for m in midis_b if m > avg_a + 6)
                if crossing_notes > 0:
                    crossings.append(
                        {
                            "track_a": song.tracks[i].name,
                            "track_b": song.tracks[j].name,
                            "crossing_count": crossing_notes,
                        }
                    )

    # --- Range violations ---
    range_violations: list[dict] = []
    for ta in track_analyses:
        instr = ta["instrument"]
        if instr in _INSTRUMENT_RANGES:
            low_midi, high_midi = _INSTRUMENT_RANGES[instr]  # already MIDI numbers
            ta_low, ta_high = ta["midi_range"]
            if ta_low and ta_low < low_midi:
                range_violations.append(
                    {
                        "track": ta["name"],
                        "instrument": instr,
                        "issue": f"below range (MIDI {ta_low} < {low_midi})",
                    }
                )
            if ta_high and ta_high > high_midi:
                range_violations.append(
                    {
                        "track": ta["name"],
                        "instrument": instr,
                        "issue": f"above range (MIDI {ta_high} > {high_midi})",
                    }
                )

    # --- Register/frequency balance ---
    all_midis = [m for track_midis in all_track_midis for m in track_midis]
    low_count = sum(1 for m in all_midis if m < 48)
    mid_count = sum(1 for m in all_midis if 48 <= m <= 72)
    high_count = sum(1 for m in all_midis if m > 72)
    total_notes = max(len(all_midis), 1)

    frequency_balance = {
        "low": round(low_count / total_notes, 4),
        "mid": round(mid_count / total_notes, 4),
        "high": round(high_count / total_notes, 4),
    }

    # --- Register usage map ---
    octave_usage: dict[int, int] = {}
    for m in all_midis:
        octave = m // 12
        octave_usage[octave] = octave_usage.get(octave, 0) + 1

    # --- Suggestions ---
    if not role_map["bass"]:
        suggestions.append("No bass track detected - consider adding low-end support")
    if not role_map["melody"]:
        suggestions.append("No clear melody track - consider adding a lead voice")
    if not role_map["rhythm"]:
        suggestions.append("No percussion/rhythm track - consider adding rhythmic foundation")
    if len(role_map["melody"]) > 2:
        suggestions.append(
            f"Multiple melody tracks ({len(role_map['melody'])}) may compete for attention"
        )
    if crossings:
        issues.append(f"Voice crossings detected in {len(crossings)} track pair(s)")
    if range_violations:
        issues.append(f"{len(range_violations)} instrument range violation(s)")
    if frequency_balance["low"] < 0.05 and len(song.tracks) > 1:
        suggestions.append("Low register is thin - bass or sub could fill the bottom end")
    if frequency_balance["high"] < 0.05 and len(song.tracks) > 1:
        suggestions.append("High register is empty - a lead or shimmer could add sparkle")
    if frequency_balance["mid"] > 0.8:
        suggestions.append("Most notes cluster in mid register - spread out for better separation")

    # --- Score ---
    score = 100
    # Deductions
    if not role_map["bass"]:
        score -= 15
    if not role_map["melody"]:
        score -= 10
    if not role_map["rhythm"]:
        score -= 5
    score -= len(crossings) * 5
    score -= len(range_violations) * 5
    if frequency_balance["mid"] > 0.8:
        score -= 10
    if len(song.tracks) < 2:
        score -= 10
    score = max(0, min(100, score))

    return {
        "tracks": track_analyses,
        "roles": {k: v for k, v in role_map.items() if v},
        "register_usage": dict(sorted(octave_usage.items())),
        "voice_crossings": crossings,
        "range_violations": range_violations,
        "frequency_balance": frequency_balance,
        "issues": issues,
        "suggestions": suggestions,
        "score": score,
    }


# ---------------------------------------------------------------------------
# Chord Progression DNA (v137.0)
# ---------------------------------------------------------------------------


def progression_dna(
    progression: list[tuple[str, str]],
) -> dict:
    """Encode a chord progression as a compact feature vector.

    Extracts root motion histogram, quality distribution, tension curve
    statistics, and interval patterns into a fixed-size numeric fingerprint.
    Two progressions with similar DNA share a similar harmonic feel.
    Enables instant corpus-wide similarity search without per-chord comparison.

    Args:
        progression: List of (root, shape) tuples.

    Returns:
        Dict with:
            root_motion:       12-bin histogram of semitone root movements.
            quality_dist:      Dict of chord quality -> fraction.
            tension_stats:     mean, std, min, max, range of tension curve.
            interval_pattern:  List of semitone intervals between roots.
            length:            Number of chords.
            unique_roots:      Number of distinct roots.
            unique_qualities:  Number of distinct chord qualities.
            vector:            Flat float list for distance computation.

    Example::

        >>> dna = progression_dna([("C","maj"),("G","maj"),("A","min"),("F","maj")])
        >>> len(dna["vector"]) > 0
        True
        >>> dna["length"]
        4
    """
    import math

    if not progression:
        return {
            "root_motion": [0.0] * 12,
            "quality_dist": {},
            "tension_stats": {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "range": 0.0},
            "interval_pattern": [],
            "length": 0,
            "unique_roots": 0,
            "unique_qualities": 0,
            "vector": [0.0] * 22,
        }

    # Root motion histogram (12 bins, one per semitone 0-11)
    root_motion = [0] * 12
    intervals = []
    for i in range(1, len(progression)):
        prev_semi = _semi(progression[i - 1][0])
        curr_semi = _semi(progression[i][0])
        motion = (curr_semi - prev_semi) % 12
        root_motion[motion] += 1
        intervals.append(motion)

    total_motions = max(sum(root_motion), 1)
    root_motion_norm = [round(c / total_motions, 4) for c in root_motion]

    # Quality distribution
    quality_counts: dict[str, int] = {}
    for _, shape in progression:
        quality_counts[shape] = quality_counts.get(shape, 0) + 1
    total_chords = len(progression)
    quality_dist = {k: round(v / total_chords, 4) for k, v in quality_counts.items()}

    # Tension statistics
    tension_vals: list[float] = []
    try:
        from .harmony import tension_curve

        tension_vals = tension_curve(progression)
    except Exception:
        tension_vals = [0.5] * len(progression)

    t_mean = sum(tension_vals) / max(len(tension_vals), 1)
    t_min = min(tension_vals) if tension_vals else 0.0
    t_max = max(tension_vals) if tension_vals else 0.0
    t_range = t_max - t_min
    t_std = 0.0
    if len(tension_vals) > 1:
        t_std = math.sqrt(sum((v - t_mean) ** 2 for v in tension_vals) / len(tension_vals))

    tension_stats = {
        "mean": round(t_mean, 4),
        "std": round(t_std, 4),
        "min": round(t_min, 4),
        "max": round(t_max, 4),
        "range": round(t_range, 4),
    }

    unique_roots = len(set(r for r, _ in progression))
    unique_quals = len(set(s for _, s in progression))

    # Build flat vector: 12 root motion + 5 tension stats + 2 counts + 3 quality features
    # Quality features: fraction of major, minor, dominant
    maj_frac = sum(v for k, v in quality_dist.items() if k in ("maj", "maj7", "maj9")) / 1.0
    min_frac = sum(v for k, v in quality_dist.items() if k in ("min", "min7", "min9", "m7")) / 1.0
    dom_frac = sum(v for k, v in quality_dist.items() if k in ("dom7", "7", "9", "13")) / 1.0

    vector: list[float] = []
    vector.extend(root_motion_norm)  # 12
    vector.extend([t_mean, t_std, t_min, t_max, t_range])  # 5
    vector.extend([float(unique_roots), float(unique_quals)])  # 2
    vector.extend([maj_frac, min_frac, dom_frac])  # 3

    return {
        "root_motion": root_motion_norm,
        "quality_dist": quality_dist,
        "tension_stats": tension_stats,
        "interval_pattern": intervals,
        "length": total_chords,
        "unique_roots": unique_roots,
        "unique_qualities": unique_quals,
        "vector": vector,
    }


def progression_distance(
    dna_a: dict,
    dna_b: dict,
) -> float:
    """Compute distance between two progression DNA vectors.

    Uses Euclidean distance on the flat feature vectors. Lower = more
    similar. Zero = identical harmonic DNA.

    Args:
        dna_a: First progression DNA (from progression_dna()).
        dna_b: Second progression DNA (from progression_dna()).

    Returns:
        Euclidean distance (0.0 = identical).

    Example::

        >>> dna1 = progression_dna([("C","maj"),("G","maj"),("A","min"),("F","maj")])
        >>> dna2 = progression_dna([("C","maj"),("G","maj"),("A","min"),("F","maj")])
        >>> progression_distance(dna1, dna2)
        0.0
    """
    import math

    vec_a = dna_a.get("vector", [])
    vec_b = dna_b.get("vector", [])

    if not vec_a or not vec_b:
        return float("inf")

    # Pad shorter vector with zeros
    max_len = max(len(vec_a), len(vec_b))
    a = vec_a + [0.0] * (max_len - len(vec_a))
    b = vec_b + [0.0] * (max_len - len(vec_b))

    return round(math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))), 4)


def find_similar_progressions_dna(
    query: list[tuple[str, str]],
    corpus: list[tuple[str, list[tuple[str, str]]]],
    top_k: int = 5,
) -> list[dict]:
    """Search a corpus for progressions with similar DNA to a query.

    Computes progression_dna for the query, then ranks all corpus entries
    by Euclidean distance. Faster than per-chord comparison for large
    corpuses because it operates on fixed-size vectors.

    Args:
        query:  The progression to search for.
        corpus: List of (name, progression) tuples.
        top_k:  Maximum results to return.

    Returns:
        List of dicts sorted by distance (ascending):
            name:       Corpus entry name.
            distance:   DNA distance (lower = more similar).
            progression: The matched progression.

    Example::

        >>> query = [("C","maj"),("G","maj"),("A","min"),("F","maj")]
        >>> corpus = [("pop1", [("C","maj"),("F","maj"),("G","maj"),("C","maj")])]
        >>> results = find_similar_progressions_dna(query, corpus)
        >>> len(results) >= 1
        True
    """
    if not query or not corpus:
        return []

    query_dna = progression_dna(query)
    scored: list[dict] = []

    for name, prog in corpus:
        prog_dna = progression_dna(prog)
        dist = progression_distance(query_dna, prog_dna)
        scored.append({"name": name, "distance": dist, "progression": prog})

    scored.sort(key=lambda x: x["distance"])
    return scored[:top_k]
