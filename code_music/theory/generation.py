"""theory.generation — generators, templates, progressions, DSL, practice tools."""

from __future__ import annotations

from ._core import (
    Note,
    _CHORD_SEMI,
    _GENRE_TEMPLATES,
    _GROOVE_TEMPLATES,
    _INSTRUMENT_RANGES,
    _INTERVAL_NAMES,
    _JUST_RATIOS,
    _MOZART_MINUET_TABLE,
    _NOTE_NAMES,
    _PATTERN_DB,
    _SCALE_INTERVALS,
    _semi,
    euclid,
)
from .analysis import classify_genre, corpus_stats, key_distribution
from .melody import (
    crescendo,
    decrescendo,
    dynamics_curve,
    fragment,
    generate_scale_melody,
    harmonize_melody,
    humanize_velocity,
)


# ---------------------------------------------------------------------------
# Smart generators
# ---------------------------------------------------------------------------


def generate_bass_line(
    chords: list[tuple[str, str]],
    style: str = "root",
    octave: int = 2,
    duration: float = 1.0,
    bars_per_chord: int = 1,
    seed: int | None = None,
) -> list[Note]:
    """Generate a bass line from a chord progression.

    Args:
        chords:         List of (root, shape) tuples.
        style:          'root' (roots only), 'root_fifth' (alternating root-5th),
                        'walking' (chromatic walking bass), 'syncopated'.
        octave:         Bass octave.
        duration:       Duration per note in beats.
        bars_per_chord: How many bars each chord gets.
        seed:           Random seed for 'walking' style.

    Returns:
        List of Notes.
    """
    import random

    rng = random.Random(seed)
    notes: list[Note] = []
    beats_per_bar = int(4 / duration)  # assuming 4/4

    for root, shape in chords:
        root_semi = _semi(root)
        chord_semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        fifth_semi = (root_semi + 7) % 12

        for bar in range(bars_per_chord):
            if style == "root":
                for _ in range(beats_per_bar):
                    notes.append(Note(root, octave, duration))

            elif style == "root_fifth":
                fifth_name = _NOTE_NAMES[fifth_semi]
                for i in range(beats_per_bar):
                    if i % 2 == 0:
                        notes.append(Note(root, octave, duration))
                    else:
                        notes.append(Note(fifth_name, octave, duration))

            elif style == "walking":
                # Walking bass: chord tones + chromatic approach notes
                chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in chord_semis]
                for i in range(beats_per_bar):
                    if i == 0:
                        notes.append(Note(root, octave, duration))
                    elif i == beats_per_bar - 1 and bar < bars_per_chord - 1:
                        # Approach note to next chord
                        notes.append(Note(rng.choice(chord_notes), octave, duration))
                    else:
                        notes.append(Note(rng.choice(chord_notes), octave, duration))

            elif style == "syncopated":
                # Offbeat emphasis
                for i in range(beats_per_bar):
                    if i % 2 == 1:
                        notes.append(Note(root, octave, duration))
                    else:
                        notes.append(Note.rest(duration))
            else:
                raise ValueError(f"Unknown bass style {style!r}")

    return notes


def generate_drums(
    genre: str = "rock",
    bars: int = 4,
    duration: float = 0.5,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate drum patterns for common genres.

    Returns a dict mapping track names to note lists.

    Args:
        genre:    'rock', 'jazz', 'electronic', 'latin', 'hiphop'.
        bars:     Number of bars to generate.
        duration: Duration per step (eighth note = 0.5 default).
        seed:     Random seed.

    Returns:
        Dict of {"kick": [...], "snare": [...], "hat": [...]}.
    """
    result: dict[str, list[Note]] = {"kick": [], "snare": [], "hat": []}
    steps_per_bar = int(4 / duration)

    for _ in range(bars):
        if genre == "rock":
            # Kick: 1 and 3, Snare: 2 and 4, Hat: all eighths
            result["kick"].extend(euclid(2, steps_per_bar, "C", 2, duration, rotation=0))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 2)
            )
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "jazz":
            # Ride: all, kick: sparse, snare: ghost notes
            result["kick"].extend(euclid(2, steps_per_bar, "C", 2, duration))
            result["snare"].extend(euclid(3, steps_per_bar, "D", 4, duration, rotation=1))
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "electronic":
            # Four-on-floor kick, offbeat hat, snare on 2+4
            for i in range(steps_per_bar):
                if i % (steps_per_bar // 4) == 0:
                    result["kick"].append(Note("C", 2, duration))
                else:
                    result["kick"].append(Note.rest(duration))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 4)
            )
            for i in range(steps_per_bar):
                if i % 2 == 1:
                    result["hat"].append(Note("F#", 6, duration))
                else:
                    result["hat"].append(Note.rest(duration))

        elif genre == "latin":
            # Tresillo kick, son clave snare
            result["kick"].extend(euclid(3, steps_per_bar, "C", 2, duration))
            result["snare"].extend(
                euclid(5, steps_per_bar * 2, "D", 4, duration / 2)[:steps_per_bar]
            )
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "hiphop":
            # Boom-bap: heavy kick, snare on 2+4, sparse hat
            result["kick"].extend(euclid(3, steps_per_bar, "C", 2, duration))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 4)
            )
            result["hat"].extend(euclid(5, steps_per_bar, "F#", 6, duration))

        else:
            raise ValueError(
                f"Unknown drum genre {genre!r}. Choose: rock, jazz, electronic, latin, hiphop"
            )

    return result


def transpose_progression(
    chords: list[tuple[str, str]],
    semitones: int = 0,
) -> list[tuple[str, str]]:
    """Transpose a chord progression by a number of semitones.

    Args:
        chords:    List of (root, shape) tuples.
        semitones: Number of semitones to transpose (positive=up, negative=down).

    Returns:
        New list of (root, shape) tuples with transposed roots.
    """
    result: list[tuple[str, str]] = []
    for root, shape in chords:
        root_semi = _semi(root)
        new_semi = (root_semi + semitones) % 12
        result.append((_NOTE_NAMES[new_semi], shape))
    return result


def detect_tempo(audio, sr: int = 44100) -> float:
    """Estimate BPM from rendered audio using onset detection.

    Simple energy-based onset detection with autocorrelation.

    Args:
        audio: Float64 audio array (mono or stereo).
        sr:    Sample rate.

    Returns:
        Estimated BPM (60-200 range).
    """
    import numpy as np

    if audio.ndim > 1:
        mono = np.mean(audio, axis=1)
    else:
        mono = audio

    # Compute energy envelope
    hop = sr // 100  # 10ms hops
    n_frames = len(mono) // hop
    if n_frames < 10:
        return 120.0  # not enough data

    energy = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop
        end = min(start + hop, len(mono))
        energy[i] = np.sum(mono[start:end] ** 2)

    # Onset detection (first difference of energy)
    onset = np.diff(energy)
    onset = np.maximum(onset, 0)

    # Autocorrelation to find periodicity
    if len(onset) < 20:
        return 120.0

    corr = np.correlate(onset, onset, mode="full")
    corr = corr[len(corr) // 2 :]

    # Find first significant peak after minimum lag
    min_bpm, max_bpm = 60, 200
    min_lag = int(60.0 / max_bpm * 100)  # 100 = frames per second
    max_lag = int(60.0 / min_bpm * 100)
    max_lag = min(max_lag, len(corr) - 1)

    if min_lag >= max_lag:
        return 120.0

    search = corr[min_lag:max_lag]
    if len(search) == 0:
        return 120.0

    peak_idx = np.argmax(search) + min_lag
    if peak_idx == 0:
        return 120.0

    bpm = 60.0 / (peak_idx / 100.0)
    return round(float(bpm), 1)


def merge_tracks(tracks_notes: list[list[Note]]) -> list[Note]:
    """Merge multiple note lists into a single interleaved list.

    Takes notes from each list in round-robin order.

    Args:
        tracks_notes: List of note lists to merge.

    Returns:
        Single merged list.
    """
    if not tracks_notes:
        return []

    result: list[Note] = []
    max_len = max(len(t) for t in tracks_notes)
    for i in range(max_len):
        for track in tracks_notes:
            if i < len(track):
                result.append(track[i])
    return result


# ---------------------------------------------------------------------------
# Chord progression templates (v41.0)
# ---------------------------------------------------------------------------


def twelve_bar_blues(
    key: str = "C",
) -> list[tuple[str, str]]:
    """Generate a 12-bar blues progression.

    The 12-bar blues is the most important chord progression in modern
    music. Rock, jazz, country, R&B — everything traces back to these
    12 bars. I-I-I-I / IV-IV-I-I / V-IV-I-V (quick change optional).

    Args:
        key: Key root.

    Returns:
        12-element list of (root, shape) tuples, one per bar.
    """
    k = _semi(key)
    tonic = (_NOTE_NAMES[k], "dom7")
    iv = (_NOTE_NAMES[(k + 5) % 12], "dom7")
    v = (_NOTE_NAMES[(k + 7) % 12], "dom7")
    return [tonic, tonic, tonic, tonic, iv, iv, tonic, tonic, v, iv, tonic, v]


def rhythm_changes(
    key: str = "Bb",
) -> list[tuple[str, str]]:
    """Generate the A section of rhythm changes (Gershwin's 'I Got Rhythm').

    Rhythm changes are the second most important chord progression in jazz
    after the blues. The 8-bar A section cycles I-vi-ii-V with chromatic
    turnarounds. Bird, Diz, Sonny Rollins — everyone cut their teeth
    on rhythm changes.

    Args:
        key: Key root (Bb is traditional).

    Returns:
        8-element list of (root, shape) tuples for the A section.
    """
    k = _semi(key)
    tonic = _NOTE_NAMES[k]
    vi = _NOTE_NAMES[(k + 9) % 12]
    ii = _NOTE_NAMES[(k + 2) % 12]
    v = _NOTE_NAMES[(k + 7) % 12]
    return [
        (tonic, "maj7"),
        (vi, "min7"),
        (ii, "min7"),
        (v, "dom7"),
        (tonic, "maj7"),
        (vi, "min7"),
        (ii, "min7"),
        (v, "dom7"),
    ]


def coltrane_changes(
    key: str = "C",
) -> list[tuple[str, str]]:
    """Generate Coltrane changes (Giant Steps substitution pattern).

    John Coltrane's 'Giant Steps' divides the octave into three equal
    parts (major thirds) and moves through all three tonal centers.
    The hardest chord changes in jazz — if you can play these, you can
    play anything.

    Args:
        key: Starting key root.

    Returns:
        12-element list of (root, shape) tuples cycling through three keys.
    """
    k = _semi(key)
    # Three tonal centers a major third apart
    c1 = _NOTE_NAMES[k]
    c2 = _NOTE_NAMES[(k + 4) % 12]
    c3 = _NOTE_NAMES[(k + 8) % 12]
    # V7 of each center
    v1 = _NOTE_NAMES[(k + 7) % 12]
    v2 = _NOTE_NAMES[(k + 11) % 12]
    v3 = _NOTE_NAMES[(k + 3) % 12]

    return [
        (c1, "maj7"),
        (v2, "dom7"),
        (c2, "maj7"),
        (v3, "dom7"),
        (c3, "maj7"),
        (v1, "dom7"),
        (c1, "maj7"),
        (v2, "dom7"),
        (c2, "maj7"),
        (v3, "dom7"),
        (c3, "maj7"),
        (v1, "dom7"),
    ]


def andalusian_cadence(
    key: str = "A",
) -> list[tuple[str, str]]:
    """Generate the Andalusian cadence (i-bVII-bVI-V).

    The most distinctive sound of flamenco, but it shows up everywhere:
    'Hit the Road Jack', 'Sultans of Swing', 'Stairway to Heaven' intro.
    Descending bass line from tonic through the Phrygian mode.

    Args:
        key: Minor key root (A minor is traditional).

    Returns:
        4-element list of (root, shape) tuples.
    """
    k = _semi(key)
    i = (_NOTE_NAMES[k], "min")
    bVII = (_NOTE_NAMES[(k + 10) % 12], "maj")
    bVI = (_NOTE_NAMES[(k + 8) % 12], "maj")
    V = (_NOTE_NAMES[(k + 7) % 12], "maj")
    return [i, bVII, bVI, V]


# ---------------------------------------------------------------------------
# Form templates (v49.0)
# ---------------------------------------------------------------------------


def song_form(
    form_name: str = "pop",
) -> list[str]:
    """Return a section-name list for a standard song form.

    Song form is the large-scale architecture — which sections appear
    in which order. This is the blueprint you fill in with chords,
    melody, and arrangement.

    Supported forms:
        'pop':    intro verse chorus verse chorus bridge chorus outro
        'aaba':   A A B A (Tin Pan Alley / jazz standard)
        'blues':  head solo head (3 × 12 bars)
        'edm':    intro buildup drop breakdown buildup drop outro
        'rondo':  A B A C A B A (classical rondo)

    Args:
        form_name: Form template name.

    Returns:
        List of section name strings.

    Raises:
        ValueError: If form_name is not recognized.
    """
    forms = {
        "pop": [
            "intro",
            "verse",
            "chorus",
            "verse",
            "chorus",
            "bridge",
            "chorus",
            "outro",
        ],
        "aaba": ["A", "A", "B", "A"],
        "blues": ["head", "solo", "head"],
        "edm": [
            "intro",
            "buildup",
            "drop",
            "breakdown",
            "buildup",
            "drop",
            "outro",
        ],
        "rondo": ["A", "B", "A", "C", "A", "B", "A"],
    }
    if form_name not in forms:
        raise ValueError(f"Unknown form {form_name!r}. Choose: {', '.join(forms)}")
    return forms[form_name]


def section_bars(
    form_name: str = "pop",
    bars_per_section: int = 8,
) -> list[tuple[str, int]]:
    """Return (section_name, bar_count) pairs for a song form.

    Combines song_form() with a default bar length per section.
    Useful for auto-generating arrangement skeletons.

    Args:
        form_name:        Form template name.
        bars_per_section: Default bars per section.

    Returns:
        List of (section_name, bars) tuples.
    """
    return [(s, bars_per_section) for s in song_form(form_name)]


# ---------------------------------------------------------------------------
# Ear training & exercises (v51.0)
# ---------------------------------------------------------------------------


def ear_training_intervals(
    count: int = 10,
    max_semitones: int = 12,
    seed: int | None = None,
) -> list[dict]:
    """Generate melodic interval ear training exercises.

    Each exercise is a pair of notes with the correct interval name.
    Play both notes, then check your answer. The building block of
    every ear training course from Berklee to YouTube.

    Args:
        count:          Number of exercises to generate.
        max_semitones:  Maximum interval size in semitones.
        seed:           Random seed for reproducibility.

    Returns:
        List of dicts: {note_a, note_b, semitones, interval_name}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    _INTERVAL_NAMES = {
        0: "P1",
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "TT",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
        12: "P8",
    }
    exercises = []
    for _ in range(count):
        root_semi = rng.randint(0, 11)
        interval = rng.randint(1, min(max_semitones, 12))
        target_semi = (root_semi + interval) % 12
        root_oct = 4
        target_oct = root_oct + (root_semi + interval) // 12
        exercises.append(
            {
                "note_a": Note(_NOTE_NAMES[root_semi], root_oct, 2.0),
                "note_b": Note(_NOTE_NAMES[target_semi], target_oct, 2.0),
                "semitones": interval,
                "interval_name": _INTERVAL_NAMES.get(interval, f"{interval}st"),
            }
        )
    return exercises


def ear_training_chords(
    count: int = 10,
    types: list[str] | None = None,
    seed: int | None = None,
) -> list[dict]:
    """Generate chord quality identification exercises.

    Each exercise is a chord with the correct quality label. Play it,
    name the quality. Major? Minor? Diminished? Aug? Dom7?

    Args:
        count: Number of exercises.
        types: Chord types to include (default: maj, min, dim, aug, dom7).
        seed:  Random seed.

    Returns:
        List of dicts: {root, shape, notes}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if types is None:
        types = ["maj", "min", "dim", "aug", "dom7"]
    exercises = []
    for _ in range(count):
        root_semi = rng.randint(0, 11)
        shape = rng.choice(types)
        root = _NOTE_NAMES[root_semi]
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        notes = [Note(_NOTE_NAMES[(root_semi + s) % 12], 4, 2.0) for s in semis]
        exercises.append({"root": root, "shape": shape, "notes": notes})
    return exercises


def scale_exercise(
    key: str = "C",
    mode: str = "major",
    direction: str = "ascending",
    octave: int = 4,
    duration: float = 0.5,
) -> list[Note]:
    """Generate a scale exercise — ascending, descending, or both.

    The most fundamental practice exercise in music. Every day,
    every key. There are no shortcuts.

    Args:
        key:       Root note.
        mode:      Scale name.
        direction: 'ascending', 'descending', or 'both'.
        octave:    Starting octave.
        duration:  Note duration.

    Returns:
        List of Notes traversing the scale.
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(mode, mode)
    if sname not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {mode!r}")

    k = _semi(key)
    intervals = _SCALE_INTERVALS[sname]
    asc = [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]
    # Add the octave
    asc.append(Note(key, octave + 1, duration))

    if direction == "ascending":
        return asc
    elif direction == "descending":
        return list(reversed(asc))
    else:  # both
        return asc + list(reversed(asc[:-1]))


def instrument_range(name: str) -> tuple[int, int]:
    """Return the playable range of an instrument as absolute semitones.

    Args:
        name: Instrument name (e.g. 'violin', 'cello', 'trumpet').

    Returns:
        (lowest, highest) absolute semitone values.

    Raises:
        ValueError: If instrument name is not recognized.
    """
    if name not in _INSTRUMENT_RANGES:
        raise ValueError(
            f"Unknown instrument {name!r}. Choose: {', '.join(sorted(_INSTRUMENT_RANGES))}"
        )
    return _INSTRUMENT_RANGES[name]


def in_range(note: Note, instrument: str) -> bool:
    """Check if a note falls within an instrument's playable range.

    Args:
        note:       A Note object.
        instrument: Instrument name.

    Returns:
        True if the note is playable on the instrument.
    """
    if note.pitch is None:
        return True  # rests are always valid
    low, high = instrument_range(instrument)
    absolute = _semi(str(note.pitch)) + note.octave * 12
    return low <= absolute <= high


def double_at_octave(
    notes: list[Note],
    direction: int = 1,
) -> list[Note]:
    """Create an octave doubling of a note list.

    Doubling at the octave is the simplest orchestration technique.
    It adds weight without changing the harmony. Strings do it
    constantly, brass does it for power.

    Args:
        notes:     Original notes.
        direction: +1 = octave above, -1 = octave below.

    Returns:
        New list with every note shifted by one octave.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(n.pitch, n.octave + direction, n.duration, velocity=n.velocity))
    return result


def string_quartet(
    melody: list[Note],
    harmony: list[tuple[str, str]],
    key: str = "C",
    duration: float = 4.0,
) -> dict[str, list[Note]]:
    """Arrange a melody and chord progression for string quartet.

    Assigns the melody to violin I, generates inner voices for
    violin II and viola from the harmony, and gives the cello
    the bass line. The most common chamber music ensemble.

    Args:
        melody:   Melody notes (assigned to violin I).
        harmony:  Chord progression as (root, shape) tuples.
        key:      Key (for voice leading context).
        duration: Duration per chord for inner voices.

    Returns:
        Dict with keys: 'violin_1', 'violin_2', 'viola', 'cello'.
    """
    violin_1 = list(melody)

    violin_2: list[Note] = []
    viola: list[Note] = []
    cello: list[Note] = []

    for root, shape in harmony:
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])

        # Cello: root
        cello.append(Note(root, 3, duration))

        # Viola: 5th (or 3rd if only 3 notes)
        fifth_idx = 2 if len(semis) > 2 else 1
        viola_semi = (k + semis[fifth_idx]) % 12
        viola.append(Note(_NOTE_NAMES[viola_semi], 4, duration))

        # Violin II: 3rd
        third_semi = (k + semis[1 % len(semis)]) % 12
        violin_2.append(Note(_NOTE_NAMES[third_semi], 4, duration))

    return {
        "violin_1": violin_1,
        "violin_2": violin_2,
        "viola": viola,
        "cello": cello,
    }


# ---------------------------------------------------------------------------
# Drone & ambient generator (v66.0)
# ---------------------------------------------------------------------------


def drone(
    key: str = "C",
    octave: int = 3,
    duration: float = 32.0,
    overtones: int = 4,
) -> list[Note]:
    """Generate a rich drone with harmonic overtone series.

    A drone is the simplest and oldest musical texture — a sustained
    tone with natural harmonics. Indian classical music, bagpipes,
    hurdy-gurdy, shoegaze guitar, ambient synths — the drone is
    the foundation.

    Args:
        key:       Root note.
        octave:    Base octave.
        duration:  Total duration.
        overtones: Number of harmonic overtones to include.

    Returns:
        List of Notes: root + overtones (layered, same duration).
    """
    k = _semi(key)
    # Harmonic series: 1x, 2x, 3x, 4x, 5x frequency
    # Approximated by octaves + fifths + thirds
    _OVERTONE_INTERVALS = [0, 12, 19, 24, 28, 31, 34, 36]
    result = []
    for i in range(min(overtones + 1, len(_OVERTONE_INTERVALS))):
        total_semi = k + _OVERTONE_INTERVALS[i]
        pc = total_semi % 12
        oct = octave + total_semi // 12
        vel = max(30, 100 - i * 15)  # overtones get quieter
        result.append(Note(_NOTE_NAMES[pc], oct, duration, velocity=vel))
    return result


def evolving_pad(
    key: str = "C",
    scale_name: str = "major",
    duration: float = 64.0,
    density: int = 8,
    octave: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a slowly morphing ambient pad texture.

    Random notes from the scale appear and sustain for varying
    durations, creating a cloud-like harmonic texture that evolves
    without repeating. Brian Eno's Music for Airports, in a function.

    Args:
        key:        Root note.
        scale_name: Scale to draw from.
        duration:   Total duration of the pad.
        density:    Number of note events.
        octave:     Center octave.
        seed:       Random seed.

    Returns:
        List of Notes with varying onsets and long durations.
    """
    import random as _rng

    rng = _rng.Random(seed)

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)

    pool = [(k + iv) % 12 for iv in intervals]
    result: list[Note] = []
    remaining = duration

    for _ in range(density):
        if remaining <= 0:
            break
        pc = rng.choice(pool)
        oct = octave + rng.choice([-1, 0, 0, 1])
        note_dur = rng.uniform(duration / density * 0.5, duration / density * 2.0)
        note_dur = min(note_dur, remaining)
        vel = rng.randint(40, 80)
        result.append(Note(_NOTE_NAMES[pc], oct, round(note_dur, 2), velocity=vel))
        remaining -= note_dur

    return result


def dice_game(
    seed: int | None = None,
    bars: int = 16,
) -> list[int]:
    """Select bar indices using Mozart's musical dice game.

    Roll two dice for each bar position, subtract 2, use as table index.
    The result is a list of "measure numbers" from Mozart's pool — each
    maps to a pre-composed one-bar fragment.

    Args:
        seed: Random seed.
        bars: Number of bars to generate (max 16 for the Mozart table).

    Returns:
        List of measure indices (integers from Mozart's table).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[int] = []
    for col in range(min(bars, 16)):
        roll = rng.randint(1, 6) + rng.randint(1, 6)  # 2d6
        row = roll - 2  # 0-10
        result.append(_MOZART_MINUET_TABLE[row][col])
    return result


def classical_minuet(
    key: str = "C",
    octave: int = 5,
    seed: int | None = None,
) -> list[Note]:
    """Generate a 16-bar minuet using Mozart's dice game method.

    Each bar's measure index from the dice roll maps to a simple
    melodic fragment derived from the key's scale. The original 1787
    algorithm — the first generative music, 230 years before AI.

    Args:
        key:    Key root.
        octave: Melody octave.
        seed:   Random seed.

    Returns:
        List of Notes forming a 16-bar minuet.
    """
    import random as _rng

    k = _semi(key)
    intervals = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
    bar_indices = dice_game(seed=seed)

    result: list[Note] = []
    for idx in bar_indices:
        # Use the index to seed a small melodic fragment (3 notes per bar in 3/4)
        frag_rng = _rng.Random(idx)
        for _ in range(3):
            iv = frag_rng.choice(intervals)
            pc = (k + iv) % 12
            result.append(Note(_NOTE_NAMES[pc], octave, 1.0))

    return result


def just_ratio(semitones: int) -> tuple[int, int]:
    """Return the pure harmonic ratio for an interval.

    Just intonation uses simple integer ratios instead of equal
    temperament's irrational numbers. A perfect fifth is 3/2, not
    2^(7/12). The difference is subtle but audible — just intervals
    are beatless and pure.

    Args:
        semitones: Interval in semitones (0–12).

    Returns:
        (numerator, denominator) ratio tuple.
    """
    s = abs(semitones) % 13
    return _JUST_RATIOS.get(s, (1, 1))


def cents_from_et(semitones: int) -> float:
    """Calculate how many cents a just interval deviates from equal temperament.

    A cent is 1/100th of a semitone. Just major third is ~14 cents flat
    compared to ET. This is why pianos sound slightly out of tune on
    sustained chords — they're in equal temperament, not just.

    Args:
        semitones: Interval in semitones.

    Returns:
        Deviation in cents (positive = sharp, negative = flat).
    """
    import math

    num, den = just_ratio(semitones)
    just_cents = 1200 * math.log2(num / den)
    et_cents = semitones * 100.0
    return round(just_cents - et_cents, 2)


def detune_to_just(
    notes: list[Note],
    key: str = "C",
) -> list[dict]:
    """Calculate just-intonation detuning for each note relative to a key.

    Returns the cent offset each note would need to sound in just
    intonation. Apply these offsets in a DAW or synth for pure tuning.

    Args:
        notes: Melody notes.
        key:   Reference key (the "1/1" pitch).

    Returns:
        List of dicts: {pitch, octave, cents_offset}.
    """
    key_semi = _semi(key)
    result = []
    for n in notes:
        if n.pitch is None:
            result.append({"pitch": None, "octave": n.octave, "cents_offset": 0.0})
        else:
            interval = (_semi(str(n.pitch)) - key_semi) % 12
            offset = cents_from_et(interval)
            result.append(
                {
                    "pitch": n.pitch,
                    "octave": n.octave,
                    "cents_offset": offset,
                }
            )
    return result


def quarter_tone(
    note: str,
    octave: int = 4,
    direction: str = "up",
    duration: float = 1.0,
) -> dict:
    """Create a quarter-tone pitch (halfway between two semitones).

    Quarter tones are fundamental to Arabic maqam, Turkish makam, and
    contemporary classical music. They don't fit into standard Western
    notation, so we return a dict with the nearest note + cent offset.

    Args:
        note:      Base note name.
        octave:    Octave.
        direction: 'up' = 50 cents sharp, 'down' = 50 cents flat.
        duration:  Note duration.

    Returns:
        Dict: {base_note, octave, cents_offset, duration}.
    """
    offset = 50.0 if direction == "up" else -50.0
    return {
        "base_note": note,
        "octave": octave,
        "cents_offset": offset,
        "duration": duration,
    }


# ---------------------------------------------------------------------------
# Bass line intelligence (v74.0)
# ---------------------------------------------------------------------------


def bass_line_jazz(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a jazz walking bass line with chromatic approaches.

    Hits the root on beat 1, walks through chord tones and chromatic
    approaches on beats 2-4. Mingus-level bass lines require a human,
    but this gets you 80% of the way.

    Args:
        progression: Chord progression as (root, shape) tuples.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes (4 notes per chord).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for idx, (root, shape) in enumerate(progression):
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        chord_tones = [(k + s) % 12 for s in semis]

        # Beat 1: root
        result.append(Note(_NOTE_NAMES[k], octave, 1.0, velocity=95))

        # Beat 2: chord tone
        ct = rng.choice(chord_tones[1:]) if len(chord_tones) > 1 else k
        result.append(Note(_NOTE_NAMES[ct], octave, 1.0, velocity=80))

        # Beat 3: passing tone (scale step)
        passing = (k + rng.choice([2, 5, 7, 9])) % 12
        result.append(Note(_NOTE_NAMES[passing], octave, 1.0, velocity=75))

        # Beat 4: chromatic approach to next root
        if idx + 1 < len(progression):
            next_root = _semi(progression[idx + 1][0])
            approach = (next_root + rng.choice([-1, 1])) % 12
        else:
            approach = (k + rng.choice([-1, 1])) % 12
        result.append(Note(_NOTE_NAMES[approach], octave, 1.0, velocity=85))

    return result


def bass_line_funk(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a syncopated funk bass line with octave pops.

    Bootsy Collins vibes: root on the one, syncopated ghost notes,
    and the occasional octave pop. The pocket is everything.

    Args:
        progression: Chord progression.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes (8 sixteenth-notes per chord).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for root, shape in progression:
        k = _semi(root)
        for beat in range(8):
            if beat == 0:
                # Strong downbeat
                result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=100))
            elif beat == 3 and rng.random() > 0.4:
                # Octave pop
                result.append(Note(_NOTE_NAMES[k], octave + 1, 0.5, velocity=90))
            elif rng.random() > 0.5:
                # Ghost note or passing tone
                ghost = (k + rng.choice([0, 5, 7])) % 12
                result.append(Note(_NOTE_NAMES[ghost], octave, 0.5, velocity=50))
            else:
                # Rest (the space IS the funk)
                result.append(Note.rest(0.5))

    return result


def bass_line_latin(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a Latin tumbao bass pattern.

    The tumbao is the rhythmic foundation of salsa, son, and
    Afro-Cuban music. Anticipates beat 1 by playing on the "and"
    of beat 4, creating forward momentum.

    Args:
        progression: Chord progression.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes in tumbao rhythm.
    """
    result: list[Note] = []

    for idx, (root, shape) in enumerate(progression):
        k = _semi(root)
        fifth = (k + 7) % 12

        # Tumbao pattern: rest, root, rest, fifth, rest, root, fifth, anticipation
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=90))
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[fifth], octave, 0.5, velocity=80))
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=85))
        result.append(Note(_NOTE_NAMES[fifth], octave, 0.5, velocity=75))
        # Anticipation: next root a half-beat early
        if idx + 1 < len(progression):
            next_k = _semi(progression[idx + 1][0])
            result.append(Note(_NOTE_NAMES[next_k], octave, 0.5, velocity=95))
        else:
            result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=80))

    return result


# ---------------------------------------------------------------------------
# Practice room tools (v76.0)
# ---------------------------------------------------------------------------


def click_track(
    bpm: float = 120.0,
    bars: int = 8,
    beats_per_bar: int = 4,
    subdivisions: int = 1,
    accent_note: str = "C",
    tick_note: str = "C",
    octave: int = 6,
) -> list[Note]:
    """Generate a metronome click track.

    Beat 1 is accented, remaining beats are softer. Subdivisions add
    ticks between beats (2 = 8th notes, 4 = 16th notes).

    Args:
        bpm:            Tempo (for reference — duration is calculated).
        bars:           Number of bars.
        beats_per_bar:  Beats per bar.
        subdivisions:   Subdivisions per beat (1 = none, 2 = 8ths, 4 = 16ths).
        accent_note:    Pitch for accented beat 1.
        tick_note:      Pitch for regular beats.
        octave:         Click octave.

    Returns:
        List of Notes forming the click track.
    """
    beat_dur = 60.0 / bpm
    sub_dur = beat_dur / subdivisions
    result: list[Note] = []

    for bar in range(bars):
        for beat in range(beats_per_bar):
            for sub in range(subdivisions):
                if beat == 0 and sub == 0:
                    result.append(Note(accent_note, octave, sub_dur, velocity=100))
                elif sub == 0:
                    result.append(Note(tick_note, octave, sub_dur, velocity=75))
                else:
                    result.append(Note(tick_note, octave - 1, sub_dur, velocity=50))

    return result


def backing_track(
    progression: list[tuple[str, str]],
    key: str = "C",
    style: str = "rock",
    bars_per_chord: int = 1,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate a backing track with drums, bass, and chords.

    One function to get a full rhythm section. Useful for practice,
    demos, or as the foundation of a song.

    Args:
        progression:    Chord progression.
        key:            Key for bass line.
        style:          'rock', 'jazz', 'latin', or 'funk'.
        bars_per_chord: Bars per chord (for duration calc).
        seed:           Random seed.

    Returns:
        Dict: {bass, chords, kick, snare, hat} — each a list of Notes.
    """
    chords: list[Note] = []
    chord_dur = bars_per_chord * 4.0
    for root, shape in progression:
        # Simple chord hit
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        for s in semis:
            chords.append(Note(_NOTE_NAMES[(k + s) % 12], 3, chord_dur))

    # Bass
    if style == "jazz":
        bass = bass_line_jazz(progression, seed=seed)
    elif style == "funk":
        bass = bass_line_funk(progression, seed=seed)
    elif style == "latin":
        bass = bass_line_latin(progression, seed=seed)
    else:
        # Rock: root notes
        bass = []
        for root, _ in progression:
            for _ in range(bars_per_chord * 4):
                bass.append(Note(root, 2, 1.0, velocity=90))

    # Drums (simplified patterns)
    total_beats = len(progression) * bars_per_chord * 4
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []
    for beat in range(total_beats):
        if beat % 4 == 0:
            kick.append(Note("C", 2, 1.0, velocity=100))
        elif beat % 4 == 2:
            kick.append(Note("C", 2, 1.0, velocity=70))
        else:
            kick.append(Note.rest(1.0))

        if beat % 4 == 2:
            snare.append(Note("C", 3, 1.0, velocity=90))
        else:
            snare.append(Note.rest(1.0))

        hat.append(Note("C", 5, 0.5, velocity=60))
        hat.append(Note("C", 5, 0.5, velocity=40))

    return {"bass": bass, "chords": chords, "kick": kick, "snare": snare, "hat": hat}


def tempo_trainer(
    start_bpm: float = 80.0,
    end_bpm: float = 160.0,
    bars_per_step: int = 4,
    bpm_increment: float = 10.0,
    beats_per_bar: int = 4,
) -> list[dict]:
    """Generate a tempo training plan with gradually increasing BPM.

    Returns a list of sections, each with its BPM and click track.
    Practice starts slow and builds — the only honest way to get fast.

    Args:
        start_bpm:      Starting tempo.
        end_bpm:        Target tempo.
        bars_per_step:  Bars at each tempo level.
        bpm_increment:  BPM increase per step.
        beats_per_bar:  Beats per bar.

    Returns:
        List of dicts: {bpm, click, bars}.
    """
    sections: list[dict] = []
    current_bpm = start_bpm
    while current_bpm <= end_bpm:
        clicks = click_track(current_bpm, bars_per_step, beats_per_bar)
        sections.append({"bpm": current_bpm, "click": clicks, "bars": bars_per_step})
        current_bpm += bpm_increment
    return sections


def generate_progression(
    key: str = "C",
    length: int = 4,
    genre: str = "pop",
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a chord progression from genre templates.

    Picks a template randomly from the genre's pool and transposes to key.
    For blues, returns a full 12-bar progression regardless of length.

    Args:
        key:    Key root.
        length: Number of chords (ignored for blues).
        genre:  'pop', 'jazz', 'classical', or 'blues'.
        seed:   Random seed.

    Returns:
        List of (root, shape) tuples.
    """
    import random as _rng

    rng = _rng.Random(seed)
    templates = _GENRE_TEMPLATES.get(genre, _GENRE_TEMPLATES["pop"])
    template = rng.choice(templates)

    # Parse roman numerals
    result: list[tuple[str, str]] = []
    for numeral in template:
        # Quick parse: uppercase = major context
        clean = numeral.replace("7", "").replace("maj", "")
        suffix = ""
        if "maj7" in numeral:
            suffix = "maj7"
        elif "7" in numeral:
            suffix = "dom7"

        roman_map = {
            "I": 0,
            "II": 2,
            "III": 4,
            "IV": 5,
            "V": 7,
            "VI": 9,
            "VII": 11,
            "i": 0,
            "ii": 2,
            "iii": 4,
            "iv": 5,
            "v": 7,
            "vi": 9,
            "vii": 11,
        }

        # Handle lowercase prefix
        is_minor = clean[0].islower() if clean else False
        upper = clean.upper()

        degree = roman_map.get(upper, 0)
        k = _semi(key)
        root = _NOTE_NAMES[(k + degree) % 12]

        if suffix:
            shape = suffix
        elif is_minor:
            shape = "min"
        else:
            shape = "maj"

        result.append((root, shape))

    # Trim or repeat to length (blues is always 12)
    if genre != "blues":
        while len(result) < length:
            result.extend(result)
        result = result[:length]

    return result


def extend_progression(
    existing: list[tuple[str, str]],
    bars: int = 4,
    key: str = "C",
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Extend an existing progression by generating compatible continuation.

    Uses the last chord as context to pick a natural next chord,
    then continues for the requested number of bars.

    Args:
        existing: Current progression.
        bars:     Number of chords to add.
        key:      Key context.
        seed:     Random seed.

    Returns:
        Extended progression (original + new chords).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result = list(existing)
    k = _semi(key)

    for _ in range(bars):
        # Pick a diatonic chord biased toward common functions
        degree = rng.choice([0, 0, 5, 5, 7, 7, 9, 2])  # I, IV, V, vi, ii
        root = _NOTE_NAMES[(k + degree) % 12]
        shape = "min" if degree in (2, 4, 9) else "maj"
        if degree == 7:
            shape = "dom7"
        result.append((root, shape))

    return result


# ---------------------------------------------------------------------------
# Comping pattern library (v82.0)
# ---------------------------------------------------------------------------


def comp_pattern(
    progression: list[tuple[str, str]],
    style: str = "rock",
    octave: int = 3,
    seed: int | None = None,
) -> list[Note]:
    """Generate a rhythmic comping (accompaniment) pattern for chords.

    Comping is what the rhythm section plays behind the soloist. Each
    style has its own rhythmic DNA — bossa nova syncopation is not
    swing quarter notes is not funk muted 16ths.

    Styles:
    - 'rock':   power chord 8th notes on every beat
    - 'swing':  Freddie Green quarter-note chunks
    - 'funk':   muted 16th-note chops with ghost notes
    - 'bossa':  syncopated shell voicings (3-7 on anticipations)
    - 'ballad': arpeggiated chords, slow and spacious

    Args:
        progression: Chord progression as (root, shape) tuples.
        style:       Comping style name.
        octave:      Chord octave.
        seed:        Random seed.

    Returns:
        List of Notes forming the comping pattern.
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for root, shape in progression:
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])

        if style == "rock":
            # 8th note power chords (root + 5th)
            for _ in range(8):
                result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=85))

        elif style == "swing":
            # Freddie Green: quarter note chords, beat 2 and 4 accented
            for beat in range(4):
                vel = 90 if beat in (1, 3) else 70
                result.append(Note(_NOTE_NAMES[(k + semis[0]) % 12], octave, 1.0, velocity=vel))

        elif style == "funk":
            # Muted 16th-note chops with gaps
            for sub in range(16):
                if sub % 4 == 0:
                    result.append(Note(_NOTE_NAMES[k], octave, 0.25, velocity=90))
                elif rng.random() > 0.4:
                    result.append(Note(_NOTE_NAMES[k], octave, 0.25, velocity=40))
                else:
                    result.append(Note.rest(0.25))

        elif style == "bossa":
            # Syncopated: hit on 1, anticipate beat 3 (on the "and" of 2)
            result.append(
                Note(_NOTE_NAMES[(k + semis[1 % len(semis)]) % 12], octave, 1.5, velocity=75)
            )
            result.append(
                Note(_NOTE_NAMES[(k + semis[2 % len(semis)]) % 12], octave, 1.0, velocity=70)
            )
            result.append(Note(_NOTE_NAMES[(k + semis[0]) % 12], octave, 1.5, velocity=80))

        else:  # ballad — arpeggiated
            for s in semis:
                pc = (k + s) % 12
                result.append(Note(_NOTE_NAMES[pc], octave, 4.0 / len(semis), velocity=60))

    return result


# ---------------------------------------------------------------------------
# Song builder DSL (v87.0)
# ---------------------------------------------------------------------------


def parse_chord_line(text: str) -> list[tuple[str, str]]:
    """Parse a chord chart line into a chord progression.

    Syntax: `| Cmaj7 | Am7 | Dm7 | G7 |`
    Each cell between pipes is one chord. Supports standard
    chord symbols: maj, min, 7, maj7, min7, dim, aug, sus4, sus2.

    Args:
        text: Chord chart line.

    Returns:
        List of (root, shape) tuples.
    """
    chords: list[tuple[str, str]] = []
    cells = [c.strip() for c in text.split("|") if c.strip()]

    for cell in cells:
        symbol = cell.strip()
        if not symbol or symbol == "-":
            continue

        # Extract root (1-2 chars: letter + optional #/b)
        root = symbol[0]
        idx = 1
        if idx < len(symbol) and symbol[idx] in "#b":
            root += symbol[idx]
            idx += 1

        suffix = symbol[idx:]
        shape_map = {
            "": "maj",
            "m": "min",
            "min": "min",
            "7": "dom7",
            "maj7": "maj7",
            "min7": "min7",
            "m7": "min7",
            "dim": "dim",
            "dim7": "dim7",
            "aug": "aug",
            "sus4": "sus4",
            "sus2": "sus2",
            "9": "dom9",
            "m9": "min9",
            "maj9": "maj9",
        }
        shape = shape_map.get(suffix, "maj")
        chords.append((root, shape))

    return chords


def parse_melody_line(
    text: str,
    octave: int = 5,
    duration: float = 0.5,
) -> list[Note]:
    """Parse a melody notation line into notes.

    Syntax: `C5 D5 E5 - F5 G5` where `-` is a rest.
    Notes can include octave (C5) or use the default octave (C).

    Args:
        text:     Melody line.
        octave:   Default octave if not specified per note.
        duration: Duration per note.

    Returns:
        List of Notes.
    """
    notes: list[Note] = []
    tokens = text.split()

    for token in tokens:
        if token == "-" or token == "~":
            notes.append(Note.rest(duration))
            continue

        # Extract pitch and optional octave
        pitch = token[0]
        idx = 1
        if idx < len(token) and token[idx] in "#b":
            pitch += token[idx]
            idx += 1

        if idx < len(token) and token[idx].isdigit():
            oct = int(token[idx])
        else:
            oct = octave

        notes.append(Note(pitch, oct, duration))

    return notes


def song_from_dsl(text: str, bpm: int = 120) -> dict:
    """Parse a mini-DSL into song components.

    Syntax:
        [verse]
        chords: | Cmaj7 | Am7 | Dm7 | G7 |
        melody: C5 D5 E5 - F5 G5 A5 G5

        [chorus]
        chords: | Fmaj7 | G7 | Cmaj7 | Cmaj7 |
        melody: A5 G5 F5 E5 D5 C5 D5 E5

    Returns a dict of sections, each with chords and melody.

    Args:
        text: DSL text.
        bpm:  Tempo.

    Returns:
        Dict: {bpm, sections: [{name, chords, melody}, ...]}.
    """
    result: dict = {"bpm": bpm, "sections": []}
    current_section: dict | None = None

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            if current_section:
                result["sections"].append(current_section)
            current_section = {"name": line[1:-1], "chords": [], "melody": []}
            continue

        if current_section is None:
            current_section = {"name": "intro", "chords": [], "melody": []}

        if line.startswith("chords:"):
            chord_text = line[len("chords:") :].strip()
            current_section["chords"] = parse_chord_line(chord_text)
        elif line.startswith("melody:"):
            melody_text = line[len("melody:") :].strip()
            current_section["melody"] = parse_melody_line(melody_text)

    if current_section:
        result["sections"].append(current_section)

    return result


# ---------------------------------------------------------------------------
# Remix engine (v88.0)
# ---------------------------------------------------------------------------


def change_key(
    notes: list[Note],
    from_key: str,
    to_key: str,
) -> list[Note]:
    """Transpose a note list from one key to another.

    Preserves intervals by shifting all pitches by the semitone
    difference between keys.

    Args:
        notes:    Input notes.
        from_key: Original key root.
        to_key:   Target key root.

    Returns:
        Transposed note list.
    """
    delta = (_semi(to_key) - _semi(from_key)) % 12
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            new_semi = (_semi(str(n.pitch)) + delta) % 12
            new_oct = n.octave + (_semi(str(n.pitch)) + delta) // 12
            result.append(Note(_NOTE_NAMES[new_semi], new_oct, n.duration, velocity=n.velocity))
    return result


def double_time(notes: list[Note]) -> list[Note]:
    """Halve all durations — double the effective tempo.

    Everything plays twice as fast without changing the BPM number.

    Args:
        notes: Input notes.

    Returns:
        Notes with halved durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration / 2, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration / 2)
        for n in notes
    ]


def half_time(notes: list[Note]) -> list[Note]:
    """Double all durations — halve the effective tempo.

    Everything plays twice as slow. The breakdown section.

    Args:
        notes: Input notes.

    Returns:
        Notes with doubled durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration * 2, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration * 2)
        for n in notes
    ]


# ---------------------------------------------------------------------------
# Music theory quiz generator (v90.0)
# ---------------------------------------------------------------------------


def quiz_intervals(
    count: int = 10,
    seed: int | None = None,
) -> list[dict]:
    """Generate interval identification quiz questions.

    Each question presents two notes; the answer is the interval name.

    Args:
        count: Number of questions.
        seed:  Random seed.

    Returns:
        List of dicts: {note_a, note_b, answer}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    _INTERVAL_NAMES = {
        0: "P1",
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "TT",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
    }
    questions = []
    for _ in range(count):
        pc_a = rng.randint(0, 11)
        interval = rng.randint(0, 11)
        pc_b = (pc_a + interval) % 12
        questions.append(
            {
                "note_a": _NOTE_NAMES[pc_a],
                "note_b": _NOTE_NAMES[pc_b],
                "answer": _INTERVAL_NAMES[interval],
            }
        )
    return questions


def quiz_chords(
    count: int = 10,
    seed: int | None = None,
) -> list[dict]:
    """Generate chord quality identification quiz questions.

    Each question presents a set of notes; the answer is the chord quality.

    Args:
        count: Number of questions.
        seed:  Random seed.

    Returns:
        List of dicts: {notes, answer_root, answer_shape}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    shapes = ["maj", "min", "dim", "aug", "dom7"]
    questions = []
    for _ in range(count):
        root_pc = rng.randint(0, 11)
        shape = rng.choice(shapes)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        note_names = [_NOTE_NAMES[(root_pc + s) % 12] for s in semis]
        questions.append(
            {
                "notes": note_names,
                "answer_root": _NOTE_NAMES[root_pc],
                "answer_shape": shape,
            }
        )
    return questions


def grade_quiz(answers: list[str], correct: list[str]) -> dict:
    """Grade a quiz — compare user answers to correct answers.

    Args:
        answers: User's answers.
        correct: Correct answers.

    Returns:
        Dict: {score, total, percentage, wrong_indices}.
    """
    total = len(correct)
    right = sum(1 for a, c in zip(answers, correct) if a == c)
    wrong = [i for i, (a, c) in enumerate(zip(answers, correct)) if a != c]
    return {
        "score": right,
        "total": total,
        "percentage": round(right / max(total, 1) * 100, 1),
        "wrong_indices": wrong,
    }


# ---------------------------------------------------------------------------
# Arrangement density planner (v91.0)
# ---------------------------------------------------------------------------


def density_plan(
    sections: list[str],
    instruments: list[str],
    pattern: str = "build",
) -> list[dict]:
    """Plan which instruments play in which sections.

    Patterns:
    - 'build':  start sparse, add instruments each section
    - 'strip':  start full, remove instruments each section
    - 'wave':   sparse → full → sparse → full
    - 'full':   all instruments in every section

    Args:
        sections:    Section names (e.g. ['intro', 'verse', 'chorus']).
        instruments: Instrument/track names.
        pattern:     Density pattern.

    Returns:
        List of dicts: {section, active_instruments, count}.
    """
    n_sections = len(sections)
    n_instruments = len(instruments)
    result: list[dict] = []

    for i, section in enumerate(sections):
        if pattern == "build":
            count = max(1, int((i + 1) / n_sections * n_instruments))
        elif pattern == "strip":
            count = max(1, n_instruments - int(i / max(n_sections - 1, 1) * (n_instruments - 1)))
        elif pattern == "wave":
            import math

            frac = (math.sin(i / max(n_sections - 1, 1) * math.pi) + 1) / 2
            count = max(1, int(frac * n_instruments))
        else:  # full
            count = n_instruments

        active = instruments[:count]
        result.append(
            {
                "section": section,
                "active_instruments": active,
                "count": count,
            }
        )

    return result


def orchestration_curve(plan: list[dict]) -> list[int]:
    """Extract the instrument count curve from a density plan.

    Args:
        plan: Output from density_plan().

    Returns:
        List of integers: active instrument count per section.
    """
    return [p["count"] for p in plan]


# ---------------------------------------------------------------------------
# Chord progression probability matrix (v92.0)
# ---------------------------------------------------------------------------


def build_transition_matrix(
    progressions: list[list[tuple[str, str]]],
) -> dict[tuple[str, str], dict[tuple[str, str], float]]:
    """Build a Markov transition matrix from a corpus of progressions.

    Counts how often each chord follows another, then normalizes
    to probabilities. The statistical DNA of a musical style.

    Args:
        progressions: List of chord progressions.

    Returns:
        Nested dict: matrix[from_chord][to_chord] = probability.
    """
    counts: dict[tuple[str, str], dict[tuple[str, str], int]] = {}

    for prog in progressions:
        for i in range(len(prog) - 1):
            current = prog[i]
            nxt = prog[i + 1]
            if current not in counts:
                counts[current] = {}
            counts[current][nxt] = counts[current].get(nxt, 0) + 1

    # Normalize to probabilities
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]] = {}
    for chord, transitions in counts.items():
        total = sum(transitions.values())
        matrix[chord] = {k: round(v / total, 4) for k, v in transitions.items()}

    return matrix


def most_likely_next(
    current: tuple[str, str],
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]],
) -> tuple[str, str] | None:
    """Return the most probable next chord from a transition matrix.

    Args:
        current: Current chord (root, shape).
        matrix:  Transition matrix from build_transition_matrix().

    Returns:
        Most likely next chord, or None if current not in matrix.
    """
    transitions = matrix.get(current)
    if not transitions:
        return None
    return max(transitions, key=lambda k: transitions[k])


def generate_from_matrix(
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]],
    length: int = 8,
    start: tuple[str, str] | None = None,
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a chord progression by random walk through a transition matrix.

    Each chord is chosen probabilistically based on the transition
    weights from the current chord. The statistical ghost of every
    progression in the training corpus.

    Args:
        matrix: Transition matrix.
        length: Number of chords to generate.
        start:  Starting chord (random if None).
        seed:   Random seed.

    Returns:
        Generated chord progression.
    """
    import random as _rng

    rng = _rng.Random(seed)

    if not matrix:
        return []

    if start is None:
        start = rng.choice(list(matrix.keys()))

    result = [start]
    current = start

    for _ in range(length - 1):
        transitions = matrix.get(current)
        if not transitions:
            # Dead end — restart from random
            current = rng.choice(list(matrix.keys()))
            result.append(current)
            continue

        chords = list(transitions.keys())
        weights = list(transitions.values())
        chosen = rng.choices(chords, weights=weights, k=1)[0]
        result.append(chosen)
        current = chosen

    return result


# ---------------------------------------------------------------------------
# Musical memory game (v96.0)
# ---------------------------------------------------------------------------


def memory_game(
    length: int = 8,
    key: str = "C",
    scale_name: str = "major",
    octave: int = 5,
    duration: float = 0.5,
    seed: int | None = None,
) -> list[list[Note]]:
    """Generate a Simon-says memory game — each round adds one note.

    Round 1 = 1 note, round 2 = 2 notes, ..., round N = N notes.
    All notes are drawn from the specified scale.

    Args:
        length:     Total sequence length (= number of rounds).
        key:        Key root.
        scale_name: Scale for note selection.
        octave:     Melody octave.
        duration:   Note duration.
        seed:       Random seed.

    Returns:
        List of rounds, each a list of Notes (growing by 1 each round).
    """
    import random as _rng

    rng = _rng.Random(seed)
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    pool = [_NOTE_NAMES[(k + iv) % 12] for iv in intervals]

    full_seq = [rng.choice(pool) for _ in range(length)]
    rounds: list[list[Note]] = []
    for i in range(1, length + 1):
        round_notes = [Note(p, octave, duration) for p in full_seq[:i]]
        rounds.append(round_notes)

    return rounds


def verify_playback(
    original: list[Note],
    attempt: list[Note],
) -> dict:
    """Check if a playback attempt matches the original sequence.

    Args:
        original: The correct sequence.
        attempt:  The player's attempt.

    Returns:
        Dict: {correct, total, accuracy, wrong_positions}.
    """
    total = len(original)
    correct = 0
    wrong: list[int] = []
    for i in range(min(len(original), len(attempt))):
        if original[i].pitch == attempt[i].pitch:
            correct += 1
        else:
            wrong.append(i)

    # Missing notes count as wrong
    if len(attempt) < total:
        wrong.extend(range(len(attempt), total))

    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / max(total, 1) * 100, 1),
        "wrong_positions": wrong,
    }


# ---------------------------------------------------------------------------
# Song template engine (v99.0)
# ---------------------------------------------------------------------------


class SongTemplate:
    """A slot-based song template for rapid composition.

    Define a form with named sections, fill each section with
    chords and melody, then render to a flat progression + melody.

    Example:
        t = SongTemplate("pop")
        t.fill("verse", chords=[("C","maj"),("G","dom7")], melody=[Note("E",5,1.0)])
        t.fill("chorus", chords=[("F","maj"),("C","maj")])
        result = t.render()
    """

    def __init__(self, form_name: str = "pop"):
        self.sections = song_form(form_name)
        self._slots: dict[str, dict] = {}

    def fill(
        self,
        section_name: str,
        chords: list[tuple[str, str]] | None = None,
        melody: list[Note] | None = None,
    ) -> "SongTemplate":
        """Fill a section slot with chords and/or melody.

        Args:
            section_name: Section to fill (e.g. 'verse', 'chorus').
            chords:       Chord progression for this section.
            melody:       Melody notes for this section.

        Returns:
            Self for chaining.
        """
        self._slots[section_name] = {
            "chords": chords or [],
            "melody": melody or [],
        }
        return self

    def render(self) -> dict:
        """Render the template to flat chord + melody lists.

        Returns:
            Dict: {chords: [...], melody: [...], form: [...]}.
        """
        chords: list[tuple[str, str]] = []
        melody: list[Note] = []

        for section in self.sections:
            slot = self._slots.get(section, {"chords": [], "melody": []})
            chords.extend(slot["chords"])
            melody.extend(slot["melody"])

        return {"chords": chords, "melody": melody, "form": list(self.sections)}

    def randomize(
        self,
        key: str = "C",
        seed: int | None = None,
    ) -> "SongTemplate":
        """Auto-fill all empty slots with generated content.

        Args:
            key:  Key for generation.
            seed: Random seed.

        Returns:
            Self for chaining.
        """
        import random as _rng

        rng = _rng.Random(seed)
        unique_sections = set(self.sections)

        for section in unique_sections:
            if section not in self._slots:
                prog = generate_progression(
                    key=key, length=4, genre="pop", seed=rng.randint(0, 9999)
                )
                mel = generate_scale_melody(key=key, length=8, seed=rng.randint(0, 9999))
                self.fill(section, chords=prog, melody=mel)

        return self


# ---------------------------------------------------------------------------
# Corpus learning (v101.0)
# ---------------------------------------------------------------------------


def train_style_from_corpus(
    progressions: list[list[tuple[str, str]]],
) -> dict:
    """Learn a musical style from a corpus of progressions.

    Extracts: transition matrix, root frequency, shape frequency,
    average length, and key distribution. Everything needed to
    generate new music "in the style of" the corpus.

    Args:
        progressions: List of chord progressions.

    Returns:
        Style dict: {matrix, root_freq, shape_freq, avg_length, key_dist}.
    """
    matrix = build_transition_matrix(progressions)
    stats = corpus_stats(progressions)
    keys = key_distribution(progressions)

    return {
        "matrix": matrix,
        "root_freq": stats["root_counts"],
        "shape_freq": stats["shape_counts"],
        "avg_length": stats["avg_length"],
        "key_dist": keys,
        "corpus_size": len(progressions),
    }


def continue_in_style(
    style: dict,
    start: tuple[str, str] | None = None,
    length: int = 8,
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a new progression in a learned style.

    Uses the transition matrix from train_style_from_corpus to
    produce a stochastic walk that sounds like the training data.

    Args:
        style:  Style dict from train_style_from_corpus.
        start:  Starting chord (None = random from corpus).
        length: Number of chords to generate.
        seed:   Random seed.

    Returns:
        Generated chord progression.
    """
    return generate_from_matrix(style["matrix"], length, start, seed)


# ---------------------------------------------------------------------------
# Note probability (v102.0)
# ---------------------------------------------------------------------------


def note_probability(
    notes: list[Note],
) -> dict[str, float]:
    """Calculate the probability distribution of pitch classes in a note list.

    Args:
        notes: Input notes.

    Returns:
        Dict mapping pitch name → probability (0.0–1.0).
    """
    counts: dict[str, int] = {}
    total = 0
    for n in notes:
        if n.pitch is not None:
            p = str(n.pitch)
            counts[p] = counts.get(p, 0) + 1
            total += 1
    if total == 0:
        return {}
    return {k: round(v / total, 4) for k, v in sorted(counts.items(), key=lambda x: -x[1])}


def next_note_distribution(
    notes: list[Note],
    current: str,
) -> dict[str, float]:
    """Given the current note, what's the probability of each next note?

    Builds a first-order Markov chain from the note list and queries
    the distribution for the current pitch.

    Args:
        notes:   Training melody.
        current: Current pitch name.

    Returns:
        Dict mapping pitch name → probability of following `current`.
    """
    transitions: dict[str, dict[str, int]] = {}
    for i in range(len(notes) - 1):
        if notes[i].pitch is None or notes[i + 1].pitch is None:
            continue
        src = str(notes[i].pitch)
        dst = str(notes[i + 1].pitch)
        if src not in transitions:
            transitions[src] = {}
        transitions[src][dst] = transitions[src].get(dst, 0) + 1

    if current not in transitions:
        return {}

    trans = transitions[current]
    total = sum(trans.values())
    return {k: round(v / total, 4) for k, v in sorted(trans.items(), key=lambda x: -x[1])}


# ---------------------------------------------------------------------------
# Chord progression reversal & rotation (v129.0)
# ---------------------------------------------------------------------------


def reverse_progression(
    progression: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Reverse a chord progression.

    The retrograde of harmony — play the chords backwards. Useful for
    creating B sections that mirror A sections.

    Args:
        progression: Input progression.

    Returns:
        Reversed progression.
    """
    return list(reversed(progression))


def rotate_progression(
    progression: list[tuple[str, str]],
    steps: int = 1,
) -> list[tuple[str, str]]:
    """Rotate a chord progression by N steps.

    Moves the first N chords to the end. Starting on a different
    chord of the same loop creates a different harmonic feeling
    without writing new material.

    Args:
        progression: Input progression.
        steps:       Number of positions to rotate.

    Returns:
        Rotated progression.
    """
    if not progression:
        return []
    n = steps % len(progression)
    return progression[n:] + progression[:n]


# ---------------------------------------------------------------------------
# Full Song Generator (v131.0)
# ---------------------------------------------------------------------------

# Default arrangements per genre: instrument -> (engine_instrument, volume, pan)
_GENRE_ARRANGEMENTS: dict[str, dict[str, tuple[str, float, float]]] = {
    "jazz": {
        "drums": ("drums_hat", 0.4, 0.0),
        "bass": ("bass", 0.55, 0.0),
        "chords": ("piano", 0.45, -0.2),
        "melody": ("sawtooth", 0.5, 0.15),
    },
    "pop": {
        "drums": ("drums_kick", 0.5, 0.0),
        "bass": ("bass", 0.5, 0.0),
        "chords": ("piano", 0.4, -0.15),
        "melody": ("triangle", 0.55, 0.2),
    },
    "rock": {
        "drums": ("drums_snare", 0.55, 0.0),
        "bass": ("bass", 0.55, 0.0),
        "chords": ("sawtooth", 0.4, -0.25),
        "melody": ("sawtooth", 0.5, 0.25),
    },
    "blues": {
        "drums": ("drums_hat", 0.4, 0.0),
        "bass": ("bass", 0.5, 0.0),
        "chords": ("piano", 0.4, -0.15),
        "melody": ("triangle", 0.5, 0.15),
    },
    "classical": {
        "bass": ("bass", 0.45, 0.0),
        "chords": ("pad", 0.4, -0.1),
        "melody": ("triangle", 0.55, 0.1),
    },
    "electronic": {
        "drums": ("drums_kick", 0.6, 0.0),
        "bass": ("bass", 0.55, 0.0),
        "chords": ("pad", 0.35, -0.2),
        "melody": ("sawtooth", 0.5, 0.2),
    },
    "ambient": {
        "chords": ("pad", 0.5, 0.0),
        "melody": ("sine", 0.35, 0.1),
    },
}

# Genre -> (scale, bass_style, drum_genre, swing, form)
_GENRE_DEFAULTS: dict[str, dict] = {
    "jazz": {
        "scale": "dorian",
        "bass_style": "walking",
        "drum_genre": "jazz",
        "swing": 0.55,
        "form": "aaba",
        "bars_per_section": 8,
    },
    "pop": {
        "scale": "major",
        "bass_style": "root_fifth",
        "drum_genre": "rock",
        "swing": 0.0,
        "form": "pop",
        "bars_per_section": 8,
    },
    "rock": {
        "scale": "pentatonic_minor",
        "bass_style": "root_fifth",
        "drum_genre": "rock",
        "swing": 0.0,
        "form": "pop",
        "bars_per_section": 8,
    },
    "blues": {
        "scale": "blues",
        "bass_style": "walking",
        "drum_genre": "jazz",
        "swing": 0.5,
        "form": "blues",
        "bars_per_section": 12,
    },
    "classical": {
        "scale": "major",
        "bass_style": "root",
        "drum_genre": None,
        "swing": 0.0,
        "form": "rondo",
        "bars_per_section": 8,
    },
    "electronic": {
        "scale": "aeolian",
        "bass_style": "syncopated",
        "drum_genre": "electronic",
        "swing": 0.0,
        "form": "edm",
        "bars_per_section": 8,
    },
    "ambient": {
        "scale": "lydian",
        "bass_style": None,
        "drum_genre": None,
        "swing": 0.0,
        "form": "pop",
        "bars_per_section": 8,
    },
}


def generate_full_song(
    genre: str = "pop",
    key: str = "C",
    bpm: int = 120,
    sections: list[str] | None = None,
    seed: int | None = None,
) -> "Song":
    """Generate a complete multi-track Song with drums, bass, chords, and melody.

    Glues together ~15 existing functions: generate_progression, song_form,
    generate_bass_line, generate_drums, generate_scale_melody,
    harmonize_melody, comp_pattern, density_plan, crescendo/decrescendo,
    groove_template, humanize_velocity, and more.

    Args:
        genre:    Target genre: 'jazz', 'pop', 'rock', 'blues', 'classical',
                  'electronic', 'ambient'.
        key:      Key root note.
        bpm:      Tempo in BPM.
        sections: Custom section list. If None, uses genre default form.
        seed:     Random seed for reproducibility.

    Returns:
        A fully constructed Song object with named tracks and section structure.

    Example::

        >>> song = generate_full_song("jazz", key="Bb", bpm=140, seed=42)
        >>> len(song.tracks)  # drums, bass, chords, melody
        4
        >>> song.title
        'Jazz in Bb'
    """
    import random as _rng
    from ..engine import Chord, Song, Track

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731

    # Genre defaults
    defaults = _GENRE_DEFAULTS.get(genre, _GENRE_DEFAULTS["pop"])
    arrangement = _GENRE_ARRANGEMENTS.get(genre, _GENRE_ARRANGEMENTS["pop"])
    scale_name = defaults["scale"]
    bass_style = defaults["bass_style"]
    drum_genre = defaults["drum_genre"]
    swing = defaults["swing"]

    # Song form
    if sections is None:
        sections = song_form(defaults["form"])
    bars_per_section = defaults["bars_per_section"]

    # Build song
    song = Song(title=f"{genre.title()} in {key}", bpm=bpm)

    # Generate a chord progression per section type (cache same sections)
    section_progs: dict[str, list[tuple[str, str]]] = {}
    for section_name in set(sections):
        length = bars_per_section
        if genre == "blues" and section_name in ("head", "solo"):
            length = 12
        prog = generate_progression(key=key, length=length, genre=genre, seed=child_seed())
        section_progs[section_name] = prog

    # Build full chord sequence
    full_prog: list[tuple[str, str]] = []
    for section_name in sections:
        full_prog.extend(section_progs[section_name])

    total_bars = len(full_prog)

    # --- Chord track ---
    inst, vol, pan = arrangement.get("chords", ("piano", 0.4, 0.0))
    chord_track = song.add_track(Track(name="chords", instrument=inst, volume=vol, pan=pan))
    for root, shape in full_prog:
        chord_track.add(Chord(root, shape, 3, duration=4.0))

    # --- Bass track ---
    if bass_style:
        inst, vol, pan = arrangement.get("bass", ("bass", 0.5, 0.0))
        bass_track = song.add_track(Track(name="bass", instrument=inst, volume=vol, pan=pan))
        bass_notes = generate_bass_line(
            full_prog, style=bass_style, octave=2, duration=1.0, seed=child_seed()
        )
        if swing > 0:
            from .rhythm import swing_notes

            bass_notes = swing_notes(bass_notes, amount=swing)
        bass_notes = humanize_velocity(bass_notes, amount=0.1, seed=child_seed())
        bass_track.extend(bass_notes)

    # --- Drum track ---
    if drum_genre:
        inst, vol, pan = arrangement.get("drums", ("drums_kick", 0.5, 0.0))
        drum_track = song.add_track(Track(name="drums", instrument=inst, volume=vol, pan=pan))
        drums = generate_drums(genre=drum_genre, bars=total_bars, seed=child_seed())
        # Use the hat pattern as the main drum voice
        drum_track.extend(drums.get("hat", drums.get("kick", [])))

    # --- Melody track ---
    inst, vol, pan = arrangement.get("melody", ("triangle", 0.5, 0.15))
    melody_track = song.add_track(Track(name="melody", instrument=inst, volume=vol, pan=pan))

    # Generate melody section by section with contour variation
    contours = ["arch", "descending", "wave", "arch", "ascending", "arch"]
    for i, section_name in enumerate(sections):
        prog = section_progs[section_name]
        contour = contours[i % len(contours)]
        section_melody = generate_scale_melody(
            key=key,
            scale_name=scale_name,
            length=len(prog) * 4,
            octave=5,
            duration=1.0,
            contour=contour,
            seed=child_seed(),
        )
        # Apply dynamics per section
        if section_name in ("chorus", "drop"):
            section_melody = dynamics_curve(section_melody, start_vel=0.7, end_vel=0.9)
        elif section_name in ("intro", "outro"):
            section_melody = dynamics_curve(section_melody, start_vel=0.3, end_vel=0.5)
        elif section_name in ("bridge", "breakdown"):
            section_melody = dynamics_curve(section_melody, start_vel=0.4, end_vel=0.6)

        section_melody = humanize_velocity(section_melody, amount=0.08, seed=child_seed())
        melody_track.extend(section_melody)

    return song


# ---------------------------------------------------------------------------
# Arrangement Engine (v131.0)
# ---------------------------------------------------------------------------

# Style presets for auto_arrange
_ARRANGE_PRESETS: dict[str, dict] = {
    "jazz_combo": {
        "instruments": {
            "bass": ("bass", 0.5, 0.0, "walking"),
            "piano": ("piano", 0.4, -0.2, "comp"),
            "drums": ("drums_hat", 0.4, 0.1, "jazz"),
            "melody": ("sawtooth", 0.5, 0.15, "lead"),
        },
        "scale": "dorian",
        "swing": 0.55,
        "density_pattern": "build",
    },
    "rock_band": {
        "instruments": {
            "bass": ("bass", 0.55, 0.0, "root_fifth"),
            "guitar": ("sawtooth", 0.45, -0.3, "comp"),
            "drums": ("drums_snare", 0.55, 0.0, "rock"),
            "lead": ("sawtooth", 0.5, 0.3, "lead"),
        },
        "scale": "pentatonic_minor",
        "swing": 0.0,
        "density_pattern": "wave",
    },
    "orchestral": {
        "instruments": {
            "bass": ("bass", 0.4, 0.0, "root"),
            "strings": ("pad", 0.5, -0.1, "pad"),
            "woodwind": ("triangle", 0.4, 0.2, "lead"),
            "brass": ("sawtooth", 0.3, 0.0, "accent"),
        },
        "scale": "major",
        "swing": 0.0,
        "density_pattern": "build",
    },
    "electronic": {
        "instruments": {
            "bass": ("bass", 0.55, 0.0, "syncopated"),
            "pad": ("pad", 0.35, -0.2, "pad"),
            "drums": ("drums_kick", 0.6, 0.0, "electronic"),
            "lead": ("sawtooth", 0.5, 0.2, "lead"),
        },
        "scale": "aeolian",
        "swing": 0.0,
        "density_pattern": "wave",
    },
}


def auto_arrange(
    progression: list[tuple[str, str]],
    key: str = "C",
    bpm: int = 120,
    style: str = "rock_band",
    bars_per_chord: int = 1,
    seed: int | None = None,
) -> "Song":
    """Take a chord progression and produce a full arrangement.

    Assigns instruments, generates bass lines, drum patterns, comping,
    density curves, and a lead melody. Style presets control instrument
    choice, swing, scale, and arrangement density.

    Style presets: 'jazz_combo', 'rock_band', 'orchestral', 'electronic'.

    Args:
        progression:   List of (root, shape) tuples (the lead sheet).
        key:           Key root note.
        bpm:           Tempo.
        style:         Arrangement preset name.
        bars_per_chord: How many bars each chord gets.
        seed:          Random seed for reproducibility.

    Returns:
        Fully arranged Song with instrument tracks, dynamics, and fills.

    Example::

        >>> prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")]
        >>> song = auto_arrange(prog, key="C", style="jazz_combo", seed=42)
        >>> [t.name for t in song.tracks]
        ['bass', 'piano', 'drums', 'melody']
    """
    import random as _rng
    from ..engine import Chord, Song, Track

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731

    preset = _ARRANGE_PRESETS.get(style, _ARRANGE_PRESETS["rock_band"])
    scale_name = preset["scale"]
    swing_amount = preset["swing"]

    # Expand progression to bars
    expanded_prog: list[tuple[str, str]] = []
    for root, shape in progression:
        for _ in range(bars_per_chord):
            expanded_prog.append((root, shape))

    total_bars = len(expanded_prog)

    # Density plan: build a per-bar density value (0.0-1.0)
    # We create virtual "sections" from bar indices for the density planner
    import math

    density_values: list[float] = []
    dp = preset["density_pattern"]
    for i in range(total_bars):
        frac = i / max(total_bars - 1, 1)
        if dp == "build":
            density_values.append(frac)
        elif dp == "strip":
            density_values.append(1.0 - frac)
        elif dp == "wave":
            density_values.append((math.sin(frac * math.pi * 2) + 1) / 2)
        else:
            density_values.append(0.8)

    song = Song(title=f"{style.replace('_', ' ').title()} Arrangement", bpm=bpm)

    instruments = preset["instruments"]

    for track_name, (inst, vol, pan, role) in instruments.items():
        track = song.add_track(Track(name=track_name, instrument=inst, volume=vol, pan=pan))

        if role == "walking":
            notes = generate_bass_line(
                expanded_prog, style="walking", octave=2, duration=1.0, seed=child_seed()
            )
            if swing_amount > 0:
                from .rhythm import swing_notes

                notes = swing_notes(notes, amount=swing_amount)
            notes = humanize_velocity(notes, amount=0.1, seed=child_seed())
            track.extend(notes)

        elif role in ("root", "root_fifth", "syncopated"):
            notes = generate_bass_line(
                expanded_prog, style=role, octave=2, duration=1.0, seed=child_seed()
            )
            notes = humanize_velocity(notes, amount=0.08, seed=child_seed())
            track.extend(notes)

        elif role == "comp":
            # Chord comping
            for root, shape in expanded_prog:
                track.add(Chord(root, shape, 3, duration=4.0))

        elif role == "pad":
            # Sustained chord pads
            for root, shape in expanded_prog:
                track.add(Chord(root, shape, 3, duration=4.0))

        elif role in ("jazz", "rock", "electronic"):
            drums = generate_drums(genre=role, bars=total_bars, seed=child_seed())
            track.extend(drums.get("hat", drums.get("kick", [])))

        elif role == "lead":
            # Scale melody with contour variety
            contours = ["arch", "descending", "wave", "ascending"]
            section_len = max(4, total_bars // 4)
            for i in range(0, total_bars, section_len):
                chunk = min(section_len, total_bars - i)
                contour = contours[i // section_len % len(contours)]
                melody = generate_scale_melody(
                    key=key,
                    scale_name=scale_name,
                    length=chunk * 4,
                    octave=5,
                    duration=1.0,
                    contour=contour,
                    seed=child_seed(),
                )
                melody = humanize_velocity(melody, amount=0.1, seed=child_seed())
                track.extend(melody)

        elif role == "accent":
            # Sparse accent hits on downbeats
            for i, (root, shape) in enumerate(expanded_prog):
                density = density_values[i] if i < len(density_values) else 0.5
                if density > 0.5:
                    track.add(Chord(root, shape, 4, duration=4.0))
                else:
                    track.add(Note.rest(4.0))

    return song


# ---------------------------------------------------------------------------
# Style transfer (v132.0)
# ---------------------------------------------------------------------------

# Genre → preferred scale/shape mappings for reharmonization
_RESTYLE_HARMONY: dict[str, dict] = {
    "jazz": {"shapes": {"maj": "maj7", "min": "min7", "dom7": "dom9"}, "scale": "dorian"},
    "pop": {"shapes": {"maj7": "maj", "min7": "min", "dom9": "dom7"}, "scale": "major"},
    "rock": {"shapes": {"maj7": "maj", "min7": "min"}, "scale": "pentatonic_minor"},
    "blues": {"shapes": {"maj": "dom7", "min": "dom7", "maj7": "dom7"}, "scale": "blues"},
    "classical": {"shapes": {"dom7": "maj", "min7": "min", "dom9": "dom7"}, "scale": "major"},
    "electronic": {"shapes": {"maj7": "min", "dom7": "min"}, "scale": "aeolian"},
    "ambient": {"shapes": {"maj": "sus2", "min": "sus4", "dom7": "maj7"}, "scale": "lydian"},
    "r&b": {"shapes": {"maj": "maj9", "min": "min9", "dom7": "dom9"}, "scale": "dorian"},
    "latin": {"shapes": {"maj7": "dom7", "min7": "min"}, "scale": "mixolydian"},
    "metal": {"shapes": {"maj": "min", "dom7": "min"}, "scale": "phrygian"},
}


def restyle(
    song: "Song",
    target_genre: str,
    key: str | None = None,
    bpm: int | None = None,
    seed: int | None = None,
) -> "Song":
    """Transform a song's style to a different genre.

    Extracts the chord progression from the original song, reharmonizes
    it for the target genre (e.g. triads -> sevenths for jazz), then
    builds a fresh arrangement using auto_arrange with genre-appropriate
    instruments, bass style, drum patterns, and swing.

    This is the musical equivalent of "play that pop song as jazz" or
    "give me the rock version of this classical piece."

    Args:
        song:         Source Song object.
        target_genre: Target genre: 'jazz', 'pop', 'rock', 'blues',
                      'classical', 'electronic', 'ambient', etc.
        key:          Override key (if None, keeps original).
        bpm:          Override tempo (if None, uses genre default).
        seed:         Random seed for reproducibility.

    Returns:
        A new Song arranged in the target genre's style.

    Example::

        >>> pop_song = generate_full_song("pop", key="C", bpm=120, seed=1)
        >>> jazz_version = restyle(pop_song, "jazz")
        >>> jazz_version.title
        'Jazz Restyle'
    """
    from ..engine import Chord

    # Extract chord progression from the original song
    original_prog: list[tuple[str, str]] = []
    for track in song.tracks:
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Chord):
                original_prog.append((beat.event.root, beat.event.shape))
        if original_prog:
            break  # use first track with chords

    if not original_prog:
        # No chords found — return a fresh song in the target genre
        return generate_full_song(
            genre=target_genre,
            key=key or "C",
            bpm=bpm or 120,
            seed=seed,
        )

    # Reharmonize: transform chord shapes for the target genre
    restyle_map = _RESTYLE_HARMONY.get(target_genre, {}).get("shapes", {})
    restyled_prog: list[tuple[str, str]] = []
    for root, shape in original_prog:
        new_shape = restyle_map.get(shape, shape)
        restyled_prog.append((root, new_shape))

    # Transpose if key override requested
    if key is not None and restyled_prog:
        current_root_semi = _semi(restyled_prog[0][0])
        target_semi = _semi(key)
        shift = (target_semi - current_root_semi) % 12
        if shift != 0:
            restyled_prog = transpose_progression(restyled_prog, shift)

    # Map genre to auto_arrange style
    genre_to_style = {
        "jazz": "jazz_combo",
        "rock": "rock_band",
        "classical": "orchestral",
        "electronic": "electronic",
        "pop": "rock_band",
        "blues": "jazz_combo",
        "ambient": "electronic",
        "r&b": "jazz_combo",
        "latin": "jazz_combo",
        "metal": "rock_band",
    }
    style = genre_to_style.get(target_genre, "rock_band")

    # Use genre-appropriate BPM if not specified
    if bpm is None:
        genre_bpms = {
            "jazz": 140,
            "pop": 120,
            "rock": 130,
            "blues": 110,
            "classical": 100,
            "electronic": 128,
            "ambient": 70,
            "r&b": 90,
            "latin": 120,
            "metal": 160,
        }
        bpm = genre_bpms.get(target_genre, 120)

    effective_key = key or (original_prog[0][0] if original_prog else "C")

    result = auto_arrange(
        progression=restyled_prog,
        key=effective_key,
        bpm=bpm,
        style=style,
        seed=seed,
    )
    result.title = f"{target_genre.title()} Restyle"
    return result
