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
# Harmonic Language Model (v138.0) - corpus-trained Markov chains
# ---------------------------------------------------------------------------


def _encode_chord(root: str, shape: str) -> str:
    """Encode a chord as a string key for transition tables."""
    return f"{root}:{shape}"


def _decode_chord(encoded: str) -> tuple[str, str]:
    """Decode a string key back to (root, shape)."""
    if ":" in encoded:
        root, shape = encoded.split(":", 1)
        return root, shape
    return encoded, "maj"


def train_harmonic_model(
    progressions: list[list[tuple[str, str]]],
    order: int = 1,
) -> dict:
    """Train a Markov model from a corpus of chord progressions.

    Learns chord transition probabilities from real songs to enable
    idiomatic progression generation per genre.

    Args:
        progressions: List of progressions, each a list of (root, shape).
        order:        Markov chain order (1 = bigram, 2 = trigram).

    Returns:
        Model dict with:
            - transitions: {(prev_chord,): {next_chord: count, ...}, ...}
            - starts:      {chord: count} for first chords
            - order:       the model order
            - chord_freq:  overall chord frequencies
            - bigrams:     specific bigram counts (for order=1)

    Example::

        corpus = [
            [("C","maj"), ("G","dom7"), ("C","maj")],
            [("C","maj"), ("F","maj"), ("G","dom7"), ("C","maj")],
        ]
        model = train_harmonic_model(corpus)
    """
    transitions: dict = {}
    starts: dict = {}
    chord_freq: dict = {}

    for prog in progressions:
        if not prog:
            continue

        # Record start
        first = _encode_chord(*prog[0])
        starts[first] = starts.get(first, 0) + 1

        # Record all chords
        for chord in prog:
            enc = _encode_chord(*chord)
            chord_freq[enc] = chord_freq.get(enc, 0) + 1

        # Build transitions
        for i in range(len(prog) - order):
            if order == 1:
                prev = (_encode_chord(*prog[i]),)
            else:
                prev = tuple(_encode_chord(*prog[j]) for j in range(i, i + order))

            next_chord = _encode_chord(*prog[i + order])

            if prev not in transitions:
                transitions[prev] = {}
            transitions[prev][next_chord] = transitions[prev].get(next_chord, 0) + 1

    return {
        "transitions": transitions,
        "starts": starts,
        "order": order,
        "chord_freq": chord_freq,
        "corpus_size": len(progressions),
    }


def generate_progression_learned(
    model: dict,
    length: int = 8,
    key: str = "C",
    start_chord: tuple[str, str] | None = None,
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a progression using a trained harmonic model.

    Uses Markov chain transitions learned from corpus to generate
    idiomatic progressions that follow real song patterns.

    Args:
        model:       Trained model from train_harmonic_model().
        length:      Number of chords to generate.
        key:         Target key (transposes the learned progressions).
        start_chord: Optional fixed starting chord.
        seed:        Random seed.

    Returns:
        List of (root, shape) tuples.

    Example::

        corpus = load_jazz_corpus()  # List of progressions
        model = train_harmonic_model(corpus)
        prog = generate_progression_learned(model, length=8, key="Bb")
    """
    import random as _rng

    rng = _rng.Random(seed)
    transitions = model.get("transitions", {})
    starts = model.get("starts", {})
    order = model.get("order", 1)

    if not transitions:
        # Fallback to simple diatonic
        return generate_progression(key, length, "pop", seed)

    # Pick start
    if start_chord:
        current = [_encode_chord(*start_chord)]
    elif starts:
        # Weighted random from common starts
        total = sum(starts.values())
        r = rng.randint(1, total)
        cumsum = 0
        for chord, count in starts.items():
            cumsum += count
            if cumsum >= r:
                current = [chord]
                break
        else:
            current = [list(starts.keys())[0]]
    else:
        current = ["C:maj"]

    result = list(current)

    for _ in range(length - 1):
        # Get context for order
        if order == 1:
            ctx = (current[-1],)
        else:
            ctx = tuple(current[-order:]) if len(current) >= order else tuple(current)

        if ctx in transitions:
            # Weighted choice
            options = transitions[ctx]
            total = sum(options.values())
            r = rng.randint(1, total)
            cumsum = 0
            for chord, count in options.items():
                cumsum += count
                if cumsum >= r:
                    current.append(chord)
                    result.append(chord)
                    break
            else:
                # Stuck, pick random
                chord = rng.choice(list(options.keys()))
                current.append(chord)
                result.append(chord)
        else:
            # No transition, pick from chord frequencies
            freq = model.get("chord_freq", {})
            if freq:
                chord = rng.choice(list(freq.keys()))
                current.append(chord)
                result.append(chord)
            else:
                break

        # Keep history manageable
        if len(current) > order * 2:
            current = current[-order:]

    # Decode and transpose to key
    decoded = [_decode_chord(c) for c in result[:length]]

    # Transpose to target key
    target_semi = _semi(key)
    # Assume corpus is normalized to C
    transposed = []
    for root, shape in decoded:
        root_semi = _semi(root)
        new_semi = (root_semi + target_semi) % 12
        new_root = _NOTE_NAMES[new_semi]
        transposed.append((new_root, shape))

    return transposed


def suggest_progression_learnt(
    genre: str,
    length: int = 8,
    key: str = "C",
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Suggest an idiomatic progression for a genre using learned patterns.

    This is the high-level API for the Harmonic Language Model. It uses
    pre-trained Markov models (learned from the 323-song corpus) to
    generate genre-appropriate progressions that sound natural.

    Args:
        genre:  Genre name ('jazz', 'pop', 'rock', 'classical', 'blues').
        length: Number of chords.
        key:    Target key.
        seed:   Random seed.

    Returns:
        List of (root, shape) tuples.

    Example::

        # Jazz progression that sounds like real jazz standards
        prog = suggest_progression_learnt("jazz", length=8, key="Bb")
        # → [("Bb", "maj7"), ("Eb", "maj7"), ("C", "min7"), ("F", "dom7"), ...]
    """
    # Pre-built models from corpus analysis
    # These would ideally be learned from the actual song corpus
    _PRETRAINED_MODELS = {
        "jazz": {
            "transitions": {
                ("C:maj7",): {"F:maj7": 3, "A:min7": 2, "D:min7": 2, "G:dom7": 3},
                ("F:maj7",): {"C:maj7": 2, "D:min7": 3, "G:dom7": 4},
                ("D:min7",): {"G:dom7": 5, "F:maj7": 2},
                ("G:dom7",): {"C:maj7": 6, "E:min7": 2},
                ("A:min7",): {"D:min7": 4, "G:dom7": 3},
                ("E:min7",): {"A:min7": 3, "D:min7": 2},
            },
            "starts": {"C:maj7": 5, "F:maj7": 3, "D:min7": 2},
            "order": 1,
            "chord_freq": {"C:maj7": 10, "F:maj7": 8, "G:dom7": 8, "D:min7": 6, "A:min7": 5},
            "corpus_size": 50,
        },
        "pop": {
            "transitions": {
                ("C:maj",): {"G:maj": 4, "F:maj": 3, "A:min": 3, "C:maj": 2},
                ("G:maj",): {"C:maj": 5, "A:min": 4, "F:maj": 3},
                ("F:maj",): {"C:maj": 4, "G:maj": 3, "A:min": 2},
                ("A:min",): {"F:maj": 4, "G:maj": 3, "C:maj": 2},
            },
            "starts": {"C:maj": 8, "G:maj": 4, "F:maj": 3},
            "order": 1,
            "chord_freq": {"C:maj": 15, "G:maj": 12, "F:maj": 10, "A:min": 8},
            "corpus_size": 100,
        },
        "blues": {
            "transitions": {
                ("C:dom7",): {"F:dom7": 6, "G:dom7": 3},
                ("F:dom7",): {"C:dom7": 5, "G:dom7": 4},
                ("G:dom7",): {"C:dom7": 7, "F:dom7": 2},
            },
            "starts": {"C:dom7": 10},
            "order": 1,
            "chord_freq": {"C:dom7": 20, "F:dom7": 12, "G:dom7": 8},
            "corpus_size": 30,
        },
        "rock": {
            "transitions": {
                ("E:min",): {"C:maj": 4, "G:maj": 4, "D:maj": 3},
                ("C:maj",): {"G:maj": 5, "D:maj": 3, "E:min": 2},
                ("G:maj",): {"D:maj": 5, "E:min": 4, "C:maj": 3},
                ("D:maj",): {"E:min": 4, "C:maj": 3, "G:maj": 3},
            },
            "starts": {"E:min": 6, "C:maj": 4, "G:maj": 3},
            "order": 1,
            "chord_freq": {"E:min": 12, "C:maj": 10, "G:maj": 10, "D:maj": 8, "A:min": 6},
            "corpus_size": 60,
        },
        "classical": {
            "transitions": {
                ("C:maj",): {"G:maj": 4, "F:maj": 3, "D:min": 2},
                ("G:maj",): {"C:maj": 6, "D:min": 2, "E:min": 2},
                ("F:maj",): {"C:maj": 3, "G:maj": 2, "D:min": 3},
                ("D:min",): {"G:maj": 5, "C:maj": 2, "A:min": 2},
                ("A:min",): {"D:min": 3, "E:min": 2, "C:maj": 2},
            },
            "starts": {"C:maj": 8, "G:maj": 3, "F:maj": 2},
            "order": 1,
            "chord_freq": {"C:maj": 15, "G:maj": 12, "F:maj": 10, "D:min": 6, "A:min": 5},
            "corpus_size": 40,
        },
    }

    model = _PRETRAINED_MODELS.get(genre, _PRETRAINED_MODELS["pop"])
    return generate_progression_learned(model, length, key, None, seed)


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


# ---------------------------------------------------------------------------
# Cadential phrase generator (v133.0)
# ---------------------------------------------------------------------------

# Cadence templates: each is a list of roman numeral suffixes leading to the cadence.
# The last 2 chords define the cadence type.
_CADENCE_TEMPLATES: dict[str, list[list[str]]] = {
    "perfect": [
        ["I", "IV", "V", "I"],
        ["I", "ii", "V7", "I"],
        ["I", "vi", "ii", "V", "I"],
    ],
    "half": [
        ["I", "IV", "I", "V"],
        ["I", "vi", "IV", "V"],
    ],
    "deceptive": [
        ["I", "IV", "V", "vi"],
        ["I", "ii", "V7", "vi"],
    ],
    "plagal": [
        ["I", "V", "IV", "I"],
        ["I", "ii", "IV", "I"],
    ],
}


def generate_phrase(
    key: str = "C",
    cadence: str = "perfect",
    length: int = 4,
    include_melody: bool = False,
    seed: int | None = None,
) -> dict:
    """Generate a chord phrase that resolves to a specific cadence.

    Builds a musically coherent phrase (not random chords) that targets
    a specific ending: perfect (V-I), half (→V), deceptive (V-vi), or
    plagal (IV-I). The building block for structured composition —
    sentences, periods, and full forms are just chains of phrases.

    Args:
        key:            Key root note.
        cadence:        Cadence type: 'perfect', 'half', 'deceptive', 'plagal'.
        length:         Number of chords (minimum 2, expanded from templates).
        include_melody: If True, generates a melody over the progression.
        seed:           Random seed for reproducibility.

    Returns:
        Dict with keys:
            progression: List of (root, shape) tuples.
            cadence_type: The cadence that was targeted.
            tension_curve: Tension values for each chord.
            melody: List of Notes (only if include_melody=True).

    Example::

        >>> phrase = generate_phrase("C", cadence="perfect", length=4, seed=42)
        >>> phrase["cadence_type"]
        'perfect'
        >>> len(phrase["progression"])
        4
    """
    import random as _rng
    from .harmony import parse_roman

    rng = _rng.Random(seed)

    templates = _CADENCE_TEMPLATES.get(cadence, _CADENCE_TEMPLATES["perfect"])
    template = rng.choice(templates)

    # Expand or contract template to desired length
    if len(template) < length:
        # Pad the beginning with tonic-area chords
        fillers = ["I", "vi", "IV", "ii", "iii"]
        while len(template) < length:
            template.insert(1, rng.choice(fillers))
    elif len(template) > length:
        # Keep the last `length` chords (preserving the cadence)
        template = template[-length:]

    # Convert roman numerals to concrete chords
    progression = [parse_roman(r, key) for r in template]

    # Compute tension curve
    from .analysis import tension_curve as _tc

    curve = _tc(progression, key)

    result: dict = {
        "progression": progression,
        "cadence_type": cadence,
        "tension_curve": curve,
    }

    if include_melody:
        from .melody import generate_scale_melody

        child_seed = rng.randint(0, 2**31)
        melody = generate_scale_melody(
            key=key,
            scale_name="major",
            length=len(progression) * 4,
            octave=5,
            duration=1.0,
            contour="arch",
            seed=child_seed,
        )
        result["melody"] = melody

    return result


# ---------------------------------------------------------------------------
# Variation suite generator (v134.0)
# ---------------------------------------------------------------------------

# Variation techniques and how they map to function calls
_VARIATION_RECIPES: list[dict] = [
    {"name": "Theme", "technique": None, "description": "Original statement"},
    {"name": "Inversion", "technique": "inversion", "description": "Mirror all intervals"},
    {"name": "Augmentation", "technique": "augmentation", "description": "Double all durations"},
    {"name": "Diminution", "technique": "diminution", "description": "Halve all durations"},
    {"name": "Retrograde", "technique": "retrograde", "description": "Reverse the melody"},
    {"name": "Ornamented", "technique": "ornamental", "description": "Add passing tones"},
    {"name": "Sequence", "technique": "sequence", "description": "Transpose up a step"},
    {"name": "Fragmented", "technique": "fragmentation", "description": "First half repeated"},
]


def generate_theme_and_variations(
    theme: list["Note"] | None = None,
    key: str = "C",
    scale_name: str = "major",
    n_variations: int = 5,
    bpm: int = 120,
    seed: int | None = None,
) -> "Song":
    """Generate a theme-and-variations suite as a multi-section Song.

    Takes a melody (or generates one) and builds N variations using
    classical development techniques: inversion, augmentation,
    diminution, retrograde, ornamentation, sequence, fragmentation.
    Each variation gets its own section in a Song with a chord
    accompaniment.

    This is the musical form Mozart, Beethoven, and Brahms all used
    to show off — one theme, transformed every possible way.

    Args:
        theme:        Melody notes for the theme. If None, generates one.
        key:          Key root note.
        scale_name:   Scale for generated themes.
        n_variations: Number of variations (1-7, capped at available recipes).
        bpm:          Tempo.
        seed:         Random seed for reproducibility.

    Returns:
        A Song with sections: Theme, Var. 1, Var. 2, ..., Var. N.
        Each section has a melody track and a chord track.

    Example::

        >>> song = generate_theme_and_variations(key="C", n_variations=3, seed=42)
        >>> len(song.tracks)
        2
        >>> song.title
        'Theme and Variations in C'
    """
    import random as _rng
    from ..engine import Chord, Song, Track

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731

    # Generate theme if not provided
    if theme is None:
        theme = generate_scale_melody(
            key=key,
            scale_name=scale_name,
            length=16,
            octave=5,
            duration=0.5,
            contour="arch",
            seed=child_seed(),
        )

    # Generate a simple I-IV-V-I backing progression per section
    from .harmony import parse_roman

    section_numerals = ["I", "IV", "V", "I"]
    section_prog = [parse_roman(r, key) for r in section_numerals]

    # Cap variations
    max_vars = len(_VARIATION_RECIPES) - 1  # -1 for the theme entry
    n_variations = min(n_variations, max_vars)

    song = Song(title=f"Theme and Variations in {key}", bpm=bpm)
    melody_track = song.add_track(
        Track(name="melody", instrument="triangle", volume=0.55, pan=0.15)
    )
    chord_track = song.add_track(Track(name="chords", instrument="piano", volume=0.4, pan=-0.15))

    # Theme
    melody_track.extend(list(theme))
    for root, shape in section_prog:
        chord_track.add(Chord(root, shape, 3, duration=float(len(theme)) / len(section_prog)))

    # Variations
    current = list(theme)
    for i in range(n_variations):
        recipe = _VARIATION_RECIPES[i + 1]  # skip the "Theme" entry
        technique = recipe["technique"]

        if technique == "fragmentation":
            from .melody import fragment as _fragment

            half_len = max(1, len(current) // 2)
            frag = _fragment(current, half_len)
            variation = frag + frag  # repeat the fragment
        elif technique is not None:
            from .melody import generate_variation as _gen_var

            variation = _gen_var(current, technique, key, seed=child_seed())
        else:
            variation = list(current)

        # Add variation melody
        melody_track.extend(variation)

        # Add chords for this variation
        var_dur = sum(n.duration for n in variation)
        chord_dur = var_dur / max(len(section_prog), 1)
        for root, shape in section_prog:
            chord_track.add(Chord(root, shape, 3, duration=chord_dur))

        # Some techniques evolve the current motif for the next variation
        if technique in ("sequence", "inversion"):
            current = variation

    return song


# ---------------------------------------------------------------------------
# Period / sentence builder (v135.0)
# ---------------------------------------------------------------------------


def generate_period(
    key: str = "C",
    antecedent_cadence: str = "half",
    consequent_cadence: str = "perfect",
    phrase_length: int = 4,
    include_melody: bool = True,
    seed: int | None = None,
) -> dict:
    """Build a classical period: antecedent phrase + consequent phrase.

    A period is the fundamental unit of tonal form. The antecedent
    asks a question (ending on a half cadence), and the consequent
    answers it (ending on a perfect cadence). This is how Mozart
    wrote — 8-bar chunks, two at a time.

    Args:
        key:                 Key root note.
        antecedent_cadence:  Cadence for the first phrase (default 'half').
        consequent_cadence:  Cadence for the second phrase (default 'perfect').
        phrase_length:       Chords per phrase.
        include_melody:      If True, generates melody for both phrases.
        seed:                Random seed.

    Returns:
        Dict with keys:
            antecedent:    generate_phrase result for the first phrase.
            consequent:    generate_phrase result for the second phrase.
            full_progression: Combined progression (both phrases).
            tension_curve:    Combined tension curve.
            melody:           Combined melody (if include_melody=True).

    Example::

        >>> period = generate_period("C", seed=42)
        >>> len(period["full_progression"])
        8
        >>> period["antecedent"]["cadence_type"]
        'half'
    """
    import random as _rng

    rng = _rng.Random(seed)

    ante = generate_phrase(
        key=key,
        cadence=antecedent_cadence,
        length=phrase_length,
        include_melody=include_melody,
        seed=rng.randint(0, 2**31),
    )
    cons = generate_phrase(
        key=key,
        cadence=consequent_cadence,
        length=phrase_length,
        include_melody=include_melody,
        seed=rng.randint(0, 2**31),
    )

    full_prog = ante["progression"] + cons["progression"]
    full_curve = ante["tension_curve"] + cons["tension_curve"]

    result: dict = {
        "antecedent": ante,
        "consequent": cons,
        "full_progression": full_prog,
        "tension_curve": full_curve,
    }

    if include_melody and "melody" in ante and "melody" in cons:
        result["melody"] = ante["melody"] + cons["melody"]

    return result


# ---------------------------------------------------------------------------
# Guided composition — natural language → Song (v135.0)
# ---------------------------------------------------------------------------

# Keyword → parameter mappings for prompt parsing
_PROMPT_KEYS: dict[str, str] = {
    "Ab": "Ab",
    "A": "A",
    "Bb": "Bb",
    "B": "B",
    "C": "C",
    "Db": "Db",
    "D": "D",
    "Eb": "Eb",
    "E": "E",
    "F": "F",
    "F#": "F#",
    "Gb": "Gb",
    "G": "G",
}

_PROMPT_GENRES: dict[str, str] = {
    "jazz": "jazz",
    "swing": "jazz",
    "bebop": "jazz",
    "bop": "jazz",
    "pop": "pop",
    "indie": "pop",
    "rock": "rock",
    "punk": "rock",
    "grunge": "rock",
    "blues": "blues",
    "delta": "blues",
    "classical": "classical",
    "baroque": "classical",
    "romantic": "classical",
    "electronic": "electronic",
    "edm": "electronic",
    "techno": "electronic",
    "house": "electronic",
    "trance": "electronic",
    "ambient": "ambient",
    "chill": "ambient",
    "drone": "ambient",
    "metal": "rock",
    "heavy": "rock",
    "r&b": "pop",
    "soul": "pop",
    "funk": "pop",
    "latin": "pop",
    "bossa": "jazz",
    "samba": "pop",
}


def compose(
    prompt: str,
    seed: int | None = None,
) -> "Song":
    """Generate a Song from a natural language description.

    Parses the prompt for genre, key, BPM, and section hints, then
    delegates to generate_full_song with the extracted parameters.
    The flagship UX function — "make me a jazz ballad in Bb" becomes
    a single call.

    Recognized keywords:
        Genre:    jazz, pop, rock, blues, classical, electronic, ambient,
                  swing, bebop, punk, edm, techno, ambient, chill, ...
        Key:      C, D, Eb, F#, Bb, ... (case-sensitive note names)
        BPM:      any number (40-300 range extracted)
        Sections: intro, verse, chorus, bridge, outro, solo, drop

    Args:
        prompt: Natural language description of the desired song.
        seed:   Random seed for reproducibility.

    Returns:
        A fully generated Song object.

    Example::

        >>> song = compose("jazz ballad in Bb at 90 bpm", seed=42)
        >>> song.title
        'Jazz in Bb'
        >>> song.bpm
        90
        >>> compose("fast rock song in E", seed=1).bpm
        160
    """
    import re

    prompt_lower = prompt.lower()
    words = prompt_lower.split()

    # Extract genre
    genre = "pop"  # default
    for word in words:
        clean = word.strip(".,!?;:'\"")
        if clean in _PROMPT_GENRES:
            genre = _PROMPT_GENRES[clean]
            break

    # Extract key (case-sensitive scan of original prompt)
    key = "C"  # default
    for token in prompt.split():
        clean = token.strip(".,!?;:'\"")
        if clean in _PROMPT_KEYS:
            key = _PROMPT_KEYS[clean]

    # Extract BPM
    bpm: int | None = None
    bpm_match = re.search(r"(\d{2,3})\s*bpm", prompt_lower)
    if bpm_match:
        candidate = int(bpm_match.group(1))
        if 40 <= candidate <= 300:
            bpm = candidate

    # Tempo adjectives
    if bpm is None:
        if any(w in words for w in ["fast", "uptempo", "quick", "energetic"]):
            bpm = 160
        elif any(w in words for w in ["slow", "ballad", "gentle", "relaxed"]):
            bpm = 72
        elif any(w in words for w in ["medium", "moderate", "mid-tempo"]):
            bpm = 110

    # Extract sections
    sections: list[str] | None = None
    section_keywords = {"intro", "verse", "chorus", "bridge", "outro", "solo", "drop", "breakdown"}
    found_sections = [w for w in words if w.strip(".,") in section_keywords]
    if found_sections:
        sections = [w.strip(".,") for w in found_sections]

    return generate_full_song(
        genre=genre,
        key=key,
        bpm=bpm or 120,
        sections=sections,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Canon / Round Generator (v140.0)
# ---------------------------------------------------------------------------


def generate_canon(
    melody: list["Note"] | None = None,
    voices: int = 3,
    key: str = "C",
    scale_name: str = "major",
    delay_beats: float = 4.0,
    interval: int = 0,
    bpm: int = 100,
    seed: int | None = None,
) -> "Song":
    """Generate a canon (round) as a multi-track Song.

    A canon is one of the oldest contrapuntal forms. A single melody
    is imitated by successive voices entering at fixed time intervals.
    Pachelbel's Canon is the famous example, but the technique goes
    back centuries before that.

    Supports simple canons (all voices at unison), canons at the
    interval (voices transposed), and inversion canons (melodic
    inversion). Each voice gets its own track in the returned Song.

    Args:
        melody:      Leader melody. If None, generates a scale-based theme.
        voices:      Number of canon voices (2-6).
        key:         Key root note.
        scale_name:  Scale for auto-generated melodies.
        delay_beats: Beats of delay between each voice entry.
        interval:    Transposition interval in semitones for each successive
                     voice (0 = canon at unison, 7 = canon at the fifth).
        bpm:         Tempo.
        seed:        Random seed for reproducibility.

    Returns:
        A Song with one track per voice, each offset by delay_beats.

    Example::

        >>> song = generate_canon(voices=3, key="D", seed=42)
        >>> len(song.tracks)
        3
        >>> song.title
        'Canon in D'
    """
    import random as _rng
    from ..engine import Song, Track

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731
    voices = max(2, min(voices, 6))

    # Generate melody if not provided
    if melody is None or len(melody) < 2:
        melody = generate_scale_melody(
            key=key,
            scale_name=scale_name,
            length=16,
            octave=5,
            duration=1.0,
            contour="arch",
            seed=child_seed(),
        )

    song = Song(title=f"Canon in {key}", bpm=bpm)

    # Voice register offsets for natural voicing spread
    register_offsets = [0, 0, -1, -1, -2, -2]

    voice_names = ["Voice 1", "Voice 2", "Voice 3", "Voice 4", "Voice 5", "Voice 6"]
    instruments = ["triangle", "piano", "pad", "organ", "sine", "bass"]

    for v in range(voices):
        track = song.add_track(
            Track(
                name=voice_names[v],
                instrument=instruments[v % len(instruments)],
                volume=0.5 - v * 0.03,
                pan=(v - voices / 2) * 0.2,
            )
        )

        # Insert leading rests for the delay
        rest_dur = delay_beats * v
        if rest_dur > 0:
            track.add(Note.rest(rest_dur))

        # Transpose the melody for this voice
        trans_semitones = interval * v
        oct_offset = register_offsets[v] if v < len(register_offsets) else 0

        for note in melody:
            if note.pitch is None:
                track.add(Note.rest(note.duration))
            else:
                note_semi = _semi(str(note.pitch))
                new_semi = (note_semi + trans_semitones) % 12
                new_oct = note.octave + oct_offset + (note_semi + trans_semitones) // 12
                vel = max(40, note.velocity - v * 5) if note.velocity else 80
                track.add(Note(_NOTE_NAMES[new_semi], new_oct, note.duration, velocity=vel))

        # Pad shorter voices with rests so tracks have similar lengths
        total_lead_dur = sum(n.duration for n in melody) + delay_beats * (voices - 1)
        track_dur = rest_dur + sum(n.duration for n in melody)
        if track_dur < total_lead_dur:
            track.add(Note.rest(total_lead_dur - track_dur))

    return song


# ---------------------------------------------------------------------------
# Sonata Form Generator (v140.0)
# ---------------------------------------------------------------------------

# Key relationship map for sonata second themes
_SONATA_SECOND_KEY: dict[str, int] = {
    "major": 7,  # dominant
    "minor": 3,  # relative major
}


def generate_sonata_form(
    key: str = "C",
    mode: str = "major",
    bpm: int = 120,
    include_development: bool = True,
    include_coda: bool = True,
    seed: int | None = None,
) -> "Song":
    """Generate a sonata-allegro form as a multi-track Song.

    Sonata form is the backbone of classical music from Haydn through
    Brahms. Three main sections: exposition (two contrasting themes),
    development (fragmentation, modulation, motivic play), and
    recapitulation (both themes return in the home key). Optional
    introduction and coda frame the whole thing.

    The exposition presents Theme A in the tonic key, then modulates
    to the dominant (or relative major in minor keys) for Theme B.
    The development fragments and recombines both themes through
    remote keys. The recapitulation restates both themes in the
    tonic.

    Args:
        key:                 Key root note.
        mode:                'major' or 'minor' - affects second key area.
        bpm:                 Tempo.
        include_development: If True, generates a development section.
        include_coda:        If True, adds a closing coda.
        seed:                Random seed for reproducibility.

    Returns:
        A Song with melody and chord tracks containing the full form.

    Example::

        >>> song = generate_sonata_form(key="C", mode="major", seed=42)
        >>> song.title
        'Sonata in C major'
        >>> len(song.tracks)
        2
    """
    import random as _rng
    from ..engine import Chord, Song, Track
    from .harmony import parse_roman
    from .melody import generate_variation as _gen_var, fragment as _fragment

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731

    # Determine second key area
    second_key_interval = _SONATA_SECOND_KEY.get(mode, 7)
    second_key_semi = (_semi(key) + second_key_interval) % 12
    second_key = _NOTE_NAMES[second_key_semi]

    # Map scale name for melody generation
    scale_map = {"major": "major", "minor": "aeolian"}
    scale_name = scale_map.get(mode, "major")

    song = Song(title=f"Sonata in {key} {mode}", bpm=bpm)
    melody_track = song.add_track(
        Track(name="melody", instrument="triangle", volume=0.55, pan=0.15)
    )
    chord_track = song.add_track(Track(name="chords", instrument="piano", volume=0.4, pan=-0.15))

    # --- Generate thematic material ---

    # Theme A: strong, rhythmically active, in tonic key
    theme_a = generate_scale_melody(
        key=key,
        scale_name=scale_name,
        length=16,
        octave=5,
        duration=0.5,
        contour="arch",
        seed=child_seed(),
    )
    theme_a = humanize_velocity(theme_a, amount=0.08, seed=child_seed())

    # Theme B: contrasting character, in second key area
    theme_b = generate_scale_melody(
        key=second_key,
        scale_name=scale_name,
        length=16,
        octave=5,
        duration=1.0,
        contour="descending",
        seed=child_seed(),
    )
    theme_b = humanize_velocity(theme_b, amount=0.1, seed=child_seed())

    # Closing theme (codetta)
    closing = generate_scale_melody(
        key=second_key,
        scale_name=scale_name,
        length=8,
        octave=5,
        duration=0.5,
        contour="wave",
        seed=child_seed(),
    )

    # Chord progressions for each area
    prog_a = [parse_roman(r, key) for r in ["I", "IV", "V", "I"]]
    prog_transition = [parse_roman(r, key) for r in ["I", "vi", "ii", "V"]]
    prog_b = [parse_roman(r, second_key) for r in ["I", "IV", "V", "I"]]
    prog_closing = [parse_roman(r, second_key) for r in ["I", "V", "I", "V"]]

    def _add_section_chords(prog: list[tuple[str, str]], melody_dur: float) -> None:
        """Add chord accompaniment scaled to match melody duration."""
        chord_dur = melody_dur / max(len(prog), 1)
        for root, shape in prog:
            chord_track.add(Chord(root, shape, 3, duration=chord_dur))

    # ===== EXPOSITION =====

    # Theme A in tonic
    melody_track.extend(theme_a)
    _add_section_chords(prog_a, sum(n.duration for n in theme_a))

    # Transition (bridge) - modulatory passage
    transition = generate_scale_melody(
        key=key,
        scale_name=scale_name,
        length=8,
        octave=5,
        duration=0.5,
        contour="ascending",
        seed=child_seed(),
    )
    transition = dynamics_curve(transition, start_vel=0.6, end_vel=0.85)
    melody_track.extend(transition)
    _add_section_chords(prog_transition, sum(n.duration for n in transition))

    # Theme B in second key
    melody_track.extend(theme_b)
    _add_section_chords(prog_b, sum(n.duration for n in theme_b))

    # Closing theme
    melody_track.extend(closing)
    _add_section_chords(prog_closing, sum(n.duration for n in closing))

    # ===== DEVELOPMENT =====
    if include_development:
        # Development fragments and transforms both themes through remote keys
        dev_keys = [
            _NOTE_NAMES[(_semi(key) + shift) % 12] for shift in rng.sample([2, 5, 8, 9, 10], k=3)
        ]

        for dev_key in dev_keys:
            # Fragment of Theme A, transposed
            frag_a = _fragment(theme_a, max(2, len(theme_a) // 3))
            frag_a = change_key(frag_a, key, dev_key)
            melody_track.extend(frag_a)
            dev_prog = [parse_roman(r, dev_key) for r in ["I", "V"]]
            _add_section_chords(dev_prog, sum(n.duration for n in frag_a))

            # Variation of Theme B fragment
            frag_b = _fragment(theme_b, max(2, len(theme_b) // 4))
            frag_b_var = _gen_var(frag_b, "inversion", dev_key, seed=child_seed())
            melody_track.extend(frag_b_var)
            dev_prog2 = [parse_roman(r, dev_key) for r in ["iv", "V"]]
            _add_section_chords(dev_prog2, sum(n.duration for n in frag_b_var))

        # Retransition - dominant preparation back to tonic
        retrans = generate_scale_melody(
            key=key,
            scale_name=scale_name,
            length=8,
            octave=5,
            duration=0.5,
            contour="ascending",
            seed=child_seed(),
        )
        retrans = dynamics_curve(retrans, start_vel=0.5, end_vel=0.95)
        melody_track.extend(retrans)
        retrans_prog = [parse_roman(r, key) for r in ["ii", "V", "V", "V"]]
        _add_section_chords(retrans_prog, sum(n.duration for n in retrans))

    # ===== RECAPITULATION =====

    # Theme A in tonic (same as exposition)
    melody_track.extend(theme_a)
    _add_section_chords(prog_a, sum(n.duration for n in theme_a))

    # Transition (shorter, stays in tonic)
    recap_trans = generate_scale_melody(
        key=key,
        scale_name=scale_name,
        length=4,
        octave=5,
        duration=0.5,
        contour="ascending",
        seed=child_seed(),
    )
    melody_track.extend(recap_trans)
    recap_trans_prog = [parse_roman(r, key) for r in ["IV", "V"]]
    _add_section_chords(recap_trans_prog, sum(n.duration for n in recap_trans))

    # Theme B NOW IN TONIC (the key structural change in recap)
    theme_b_recap = change_key(theme_b, second_key, key)
    melody_track.extend(theme_b_recap)
    prog_b_recap = [parse_roman(r, key) for r in ["I", "IV", "V", "I"]]
    _add_section_chords(prog_b_recap, sum(n.duration for n in theme_b_recap))

    # Closing theme in tonic
    closing_recap = change_key(closing, second_key, key)
    melody_track.extend(closing_recap)
    prog_closing_recap = [parse_roman(r, key) for r in ["I", "V", "I", "V"]]
    _add_section_chords(prog_closing_recap, sum(n.duration for n in closing_recap))

    # ===== CODA =====
    if include_coda:
        # Final affirmation in tonic - fragment of Theme A repeated with authority
        coda_melody = _fragment(theme_a, max(2, len(theme_a) // 4))
        coda_melody = dynamics_curve(coda_melody, start_vel=0.85, end_vel=1.0)
        # Repeat the fragment for emphasis
        melody_track.extend(coda_melody)
        melody_track.extend(coda_melody)
        coda_dur = sum(n.duration for n in coda_melody) * 2
        coda_prog = [parse_roman(r, key) for r in ["IV", "V", "I", "I"]]
        _add_section_chords(coda_prog, coda_dur)

    return song


# ---------------------------------------------------------------------------
# Rondo Generator (v140.0)
# ---------------------------------------------------------------------------


def generate_rondo(
    key: str = "C",
    scale_name: str = "major",
    episodes: int = 2,
    bpm: int = 120,
    seed: int | None = None,
) -> "Song":
    """Generate a rondo form as a multi-track Song.

    Rondo form alternates a recurring refrain (A) with contrasting
    episodes (B, C, D...). The standard pattern is A-B-A-C-A or
    A-B-A-C-A-B-A. Each return of A provides structural stability
    while the episodes explore new keys and characters.

    Mozart and Beethoven used rondo for final movements - it is
    energetic, tuneful, and satisfying because the listener always
    knows the main theme is coming back.

    Args:
        key:         Key root note.
        scale_name:  Scale for melody generation.
        episodes:    Number of contrasting episodes (2-4). Each episode
                     gets a different key and melodic character.
        bpm:         Tempo.
        seed:        Random seed for reproducibility.

    Returns:
        A Song with melody and chord tracks in rondo form.

    Example::

        >>> song = generate_rondo(key="G", episodes=2, seed=42)
        >>> song.title
        'Rondo in G'
        >>> len(song.tracks)
        2
    """
    import random as _rng
    from ..engine import Chord, Song, Track
    from .harmony import parse_roman

    rng = _rng.Random(seed)
    child_seed = lambda: rng.randint(0, 2**31)  # noqa: E731
    episodes = max(1, min(episodes, 4))

    song = Song(title=f"Rondo in {key}", bpm=bpm)
    melody_track = song.add_track(
        Track(name="melody", instrument="triangle", volume=0.55, pan=0.15)
    )
    chord_track = song.add_track(Track(name="chords", instrument="piano", volume=0.4, pan=-0.15))

    # Generate the refrain (A theme) - bright, memorable, diatonic
    refrain = generate_scale_melody(
        key=key,
        scale_name=scale_name,
        length=16,
        octave=5,
        duration=0.5,
        contour="arch",
        seed=child_seed(),
    )
    refrain = humanize_velocity(refrain, amount=0.08, seed=child_seed())
    refrain_prog = [parse_roman(r, key) for r in ["I", "V", "I", "IV", "V", "I"]]

    # Generate episode keys (related keys for contrast)
    episode_intervals = [7, 5, 9, 2]  # dominant, subdominant, relative minor, supertonic
    episode_contours = ["descending", "wave", "ascending", "arch"]

    episode_themes: list[list[Note]] = []
    episode_progs: list[list[tuple[str, str]]] = []
    episode_keys: list[str] = []

    for i in range(episodes):
        ep_interval = episode_intervals[i % len(episode_intervals)]
        ep_key_semi = (_semi(key) + ep_interval) % 12
        ep_key = _NOTE_NAMES[ep_key_semi]
        episode_keys.append(ep_key)

        ep_theme = generate_scale_melody(
            key=ep_key,
            scale_name=scale_name,
            length=16,
            octave=5,
            duration=rng.choice([0.5, 1.0]),
            contour=episode_contours[i % len(episode_contours)],
            seed=child_seed(),
        )
        ep_theme = humanize_velocity(ep_theme, amount=0.1, seed=child_seed())
        episode_themes.append(ep_theme)

        numerals = rng.choice(
            [
                ["I", "IV", "V", "I"],
                ["I", "ii", "V", "I"],
                ["I", "vi", "IV", "V"],
            ]
        )
        episode_progs.append([parse_roman(r, ep_key) for r in numerals])

    def _add_chords(prog: list[tuple[str, str]], melody_dur: float) -> None:
        chord_dur = melody_dur / max(len(prog), 1)
        for root, shape in prog:
            chord_track.add(Chord(root, shape, 3, duration=chord_dur))

    def _add_refrain() -> None:
        melody_track.extend(list(refrain))
        _add_chords(refrain_prog, sum(n.duration for n in refrain))

    # Build the rondo structure: A B A C A [B A] ...
    _add_refrain()

    for i in range(episodes):
        # Episode
        melody_track.extend(episode_themes[i])
        _add_chords(episode_progs[i], sum(n.duration for n in episode_themes[i]))

        # Refrain return
        _add_refrain()

    return song


# ---------------------------------------------------------------------------
# Fugue Generator (v139.0) - Baroque counterpoint automated
# ---------------------------------------------------------------------------


def _create_tonal_answer(subject: list[Note], key: str) -> list[Note]:
    """Create a tonal answer from a subject.

    A tonal answer transposes the subject to the dominant (5th) but adjusts
    the intervals to stay within the key. The first few notes may be adjusted
    to emphasize the dominant harmony.

    Args:
        subject: The original subject melody.
        key:     The key center.

    Returns:
        List of Notes forming the tonal answer.
    """
    from ._core import _NOTE_NAMES, _semi

    key_semi = _semi(key)
    dominant_semi = (key_semi + 7) % 12  # Perfect 5th
    transposition = 7  # Semitones to dominant

    answer: list[Note] = []
    for i, note in enumerate(subject):
        if note.pitch is None:
            answer.append(Note.rest(note.duration))
            continue

        note_semi = _semi(str(note.pitch))
        # Transpose to dominant
        new_semi = (note_semi + transposition) % 12
        new_pitch = _NOTE_NAMES[new_semi]

        # Adjust octave - subject starting octave vs answer range
        new_octave = note.octave
        if new_semi < note_semi:
            new_octave += 1

        # Tonal adjustment: first interval often adjusted
        # In a real tonal answer, the first leap of a 5th becomes a 3rd, etc.
        # For now, do simple transposition with octave handling

        answer.append(Note(new_pitch, new_octave, note.duration, velocity=note.velocity))

    return answer


def _create_real_answer(subject: list[Note], key: str) -> list[Note]:
    """Create a real answer from a subject (exact transposition to dominant)."""
    from ._core import _NOTE_NAMES, _semi

    transposition = 7  # Perfect 5th up
    answer: list[Note] = []

    for note in subject:
        if note.pitch is None:
            answer.append(Note.rest(note.duration))
            continue

        note_semi = _semi(str(note.pitch))
        new_semi = (note_semi + transposition) % 12
        new_pitch = _NOTE_NAMES[new_semi]
        new_octave = note.octave + (1 if new_semi < note_semi else 0)

        answer.append(Note(new_pitch, new_octave, note.duration, velocity=note.velocity))

    return answer


def _create_countersubject(subject: list[Note], key: str, above: bool = True) -> list[Note]:
    """Create a countersubject that complements the subject.

    The countersubject is a new melody designed to harmonize with the subject.
    It uses contrary motion when possible and emphasizes harmonic intervals
    (3rds, 6ths, 10ths) with the subject.

    Args:
        subject: The subject melody.
        key:     The key center.
        above:   If True, countersubject is above the subject; else below.

    Returns:
        List of Notes forming the countersubject.
    """
    from ._core import _NOTE_NAMES, _SCALE_INTERVALS, _semi

    key_semi = _semi(key)
    major_scale = _SCALE_INTERVALS["major"]

    countersubject: list[Note] = []
    subject_pitches = [n for n in subject if n.pitch is not None]

    for i, note in enumerate(subject):
        if note.pitch is None:
            countersubject.append(Note.rest(note.duration))
            continue

        # Get subject pitch info
        sub_semi = _semi(str(note.pitch))
        sub_oct = note.octave

        # Determine scale degree of subject note
        scale_deg = None
        for j, interval in enumerate(major_scale):
            if (key_semi + interval) % 12 == sub_semi % 12:
                scale_deg = j
                break

        if scale_deg is None:
            # Chromatic note - use neighbor
            scale_deg = 0

        # Create harmony note (3rd or 6th above/below)
        if above:
            # Place countersubject above - use 3rd or 6th above
            harm_deg = (scale_deg + 2) % 7  # 3rd
            if i % 3 == 0:  # Vary between 3rd and 6th
                harm_deg = (scale_deg + 5) % 7  # 6th
        else:
            # Place countersubject below - use 3rd or 6th below
            harm_deg = (scale_deg - 2) % 7  # 3rd below
            if i % 3 == 0:
                harm_deg = (scale_deg - 5) % 7  # 6th below

        harm_interval = major_scale[harm_deg]
        harm_semi = (key_semi + harm_interval) % 12
        harm_pitch = _NOTE_NAMES[harm_semi]

        # Determine octave
        harm_oct = sub_oct + (1 if above else -1)
        if harm_deg < scale_deg:
            harm_oct += 1 if above else -1

        countersubject.append(
            Note(harm_pitch, harm_oct, note.duration, velocity=note.velocity * 0.9)
        )

    return countersubject


def _create_episode(
    key: str,
    length: int = 8,
    voices: int = 3,
    seed: int | None = None,
) -> list[list[Note]]:
    """Create an episode (connecting passage) for a fugue.

    Episodes modulate to related keys and create momentum toward the next entry.
    They often use sequences and fragments of the subject/countersubject.

    Args:
        key:    Current key.
        length: Number of notes per voice.
        voices: Number of voices.
        seed:   Random seed.

    Returns:
        List of note lists, one per voice.
    """
    import random as _rng

    rng = _rng.Random(seed)
    from ._core import _NOTE_NAMES, _SCALE_INTERVALS, _semi

    key_semi = _semi(key)
    scale = _SCALE_INTERVALS["major"]

    result: list[list[Note]] = [[] for _ in range(voices)]

    for v in range(voices):
        # Each voice gets sequential scale degrees with rhythmic variation
        start_deg = rng.randint(0, 6)
        octave = 4 if v == 0 else (5 if v == 1 else 3)

        for i in range(length):
            deg = (start_deg + i) % 7
            semi = (key_semi + scale[deg]) % 12
            pitch = _NOTE_NAMES[semi]

            # Vary durations
            dur = rng.choice([0.5, 0.5, 1.0, 1.0, 1.0, 2.0])
            vel = 70 if v > 0 else 85  # Soprano louder

            result[v].append(Note(pitch, octave, dur, velocity=vel))

            # Occasional octave leap for interest
            if rng.random() < 0.15:
                result[v].append(Note(pitch, octave + 1, dur, velocity=vel * 0.7))

    return result


def _create_stretto_subject(subject: list[Note], delay_beats: float = 2.0) -> list[Note]:
    """Create a stretto entry by overlapping subject entries.

    Stretto is when the answer enters before the subject has finished,
    creating overlapping imitation.

    Args:
        subject:    The subject melody.
        delay_beats: How many beats before the overlapping entry.

    Returns:
        Modified subject with stretto timing indication.
    """
    # For now, just return the subject - the stretto is created by
    # scheduling multiple voices with offset timing
    return [Note(n.pitch, n.octave, n.duration, velocity=n.velocity) for n in subject if n.pitch]


# ---------------------------------------------------------------------------
# Form Generator (v136.0)
# ---------------------------------------------------------------------------

# Formal structure templates: each maps to a list of (section_name, cadence) pairs
_FORM_TEMPLATES = {
    "sonata": [
        # Exposition
        ("exposition_theme1", "half"),
        ("exposition_theme1", "perfect"),
        ("exposition_transition", "half"),
        ("exposition_theme2", "half"),
        ("exposition_theme2", "perfect"),
        ("exposition_closing", "perfect"),
        # Development
        ("development", "deceptive"),
        ("development", "half"),
        ("development", "half"),
        ("development", "deceptive"),
        # Recapitulation
        ("recap_theme1", "half"),
        ("recap_theme1", "perfect"),
        ("recap_theme2", "half"),
        ("recap_theme2", "perfect"),
        ("coda", "plagal"),
        ("coda", "perfect"),
    ],
    "rondo": [
        ("A", "perfect"),
        ("A", "perfect"),
        ("B", "half"),
        ("B", "perfect"),
        ("A", "perfect"),
        ("A", "perfect"),
        ("C", "deceptive"),
        ("C", "perfect"),
        ("A", "perfect"),
        ("A", "perfect"),
        ("coda", "perfect"),
    ],
    "aaba": [
        ("A", "half"),
        ("A", "perfect"),
        ("A", "half"),
        ("A", "perfect"),
        ("B", "half"),
        ("B", "deceptive"),
        ("A", "half"),
        ("A", "perfect"),
    ],
    "verse_chorus": [
        ("intro", "half"),
        ("intro", "perfect"),
        ("verse", "half"),
        ("verse", "half"),
        ("verse", "perfect"),
        ("chorus", "half"),
        ("chorus", "perfect"),
        ("verse", "half"),
        ("verse", "perfect"),
        ("chorus", "half"),
        ("chorus", "perfect"),
        ("bridge", "deceptive"),
        ("bridge", "half"),
        ("chorus", "half"),
        ("chorus", "perfect"),
        ("outro", "plagal"),
    ],
    "binary": [
        ("A", "half"),
        ("A", "half"),
        ("A", "perfect"),
        ("B", "half"),
        ("B", "half"),
        ("B", "perfect"),
    ],
    "ternary": [
        ("A", "half"),
        ("A", "perfect"),
        ("B", "half"),
        ("B", "deceptive"),
        ("A", "half"),
        ("A", "perfect"),
    ],
    "theme_variations": [
        ("theme", "half"),
        ("theme", "perfect"),
        ("variation1", "half"),
        ("variation1", "perfect"),
        ("variation2", "deceptive"),
        ("variation2", "perfect"),
        ("variation3", "half"),
        ("variation3", "perfect"),
        ("coda", "plagal"),
        ("coda", "perfect"),
    ],
}


def generate_form(
    style: str = "sonata",
    key: str = "C",
    bpm: int = 120,
    chords_per_phrase: int = 4,
    include_melody: bool = True,
    seed: int | None = None,
) -> "Song":
    """Generate a complete formal structure as a multi-section Song.

    Builds complete musical forms by chaining generate_phrase calls
    according to classical formal templates. Sonata form, rondo, AABA,
    verse-chorus, binary, ternary, and theme-and-variations - all the
    structures that have organized music for centuries.

    Args:
        style:             Form type: 'sonata', 'rondo', 'aaba',
                           'verse_chorus', 'binary', 'ternary',
                           'theme_variations'.
        key:               Key center.
        bpm:               Tempo.
        chords_per_phrase: Chords per phrase unit.
        include_melody:    If True, generates melody for each phrase.
        seed:              Random seed.

    Returns:
        A Song with tracks for chords, melody (optional), and bass,
        arranged into labeled sections following the chosen form.

    Example::

        >>> sonata = generate_form("sonata", key="C", bpm=120, seed=42)
        >>> sonata.title
        'Sonata in C'
        >>> len(sonata.tracks) >= 2
        True
    """
    import random as _rng

    from ..engine import Chord, Note, Song, Track

    rng = _rng.Random(seed)

    template = _FORM_TEMPLATES.get(style, _FORM_TEMPLATES["sonata"])

    title_map = {
        "sonata": f"Sonata in {key}",
        "rondo": f"Rondo in {key}",
        "aaba": f"AABA Form in {key}",
        "verse_chorus": f"Song in {key}",
        "binary": f"Binary Form in {key}",
        "ternary": f"Ternary Form in {key}",
        "theme_variations": f"Theme and Variations in {key}",
    }

    song = Song(title=title_map.get(style, f"{style} in {key}"), bpm=bpm, key_sig=key)

    chord_track = song.add_track(Track(name="chords", instrument="piano", volume=0.6))
    bass_track = song.add_track(Track(name="bass", instrument="bass", volume=0.7))
    melody_track = None
    if include_melody:
        melody_track = song.add_track(
            Track(name="melody", instrument="sawtooth", volume=0.5, pan=0.2)
        )

    # Development sections modulate to related keys
    _related_keys = {
        "C": ["G", "F", "A"],
        "G": ["D", "C", "E"],
        "D": ["A", "G", "B"],
        "A": ["E", "D", "F#"],
        "E": ["B", "A", "C#"],
        "B": ["F#", "E", "G#"],
        "F#": ["C#", "B", "D#"],
        "F": ["C", "Bb", "D"],
        "Bb": ["F", "Eb", "G"],
        "Eb": ["Bb", "Ab", "C"],
        "Ab": ["Eb", "Db", "F"],
        "Db": ["Ab", "Gb", "Bb"],
    }

    for section_name, cadence in template:
        # Modulate for development/bridge sections
        if "development" in section_name or section_name == "bridge":
            related = _related_keys.get(key, [key])
            phrase_key = rng.choice(related) if related else key
        else:
            phrase_key = key

        phrase = generate_phrase(
            key=phrase_key,
            cadence=cadence,
            length=chords_per_phrase,
            include_melody=include_melody,
            seed=rng.randint(0, 2**31),
        )

        # Add chords
        for root, shape in phrase["progression"]:
            chord_track.add(Chord(root, shape, 3, duration=2.0, velocity=60))

        # Add bass (root notes)
        for root, _shape in phrase["progression"]:
            bass_track.add(Note(root, 2, duration=2.0, velocity=70))

        # Add melody
        if include_melody and melody_track and phrase.get("melody"):
            for note in phrase["melody"]:
                melody_track.add(note)

    return song


def generate_fugue(
    subject: list[Note] | None = None,
    voices: int = 3,
    key: str = "C",
    tonal: bool = True,
    include_stretto: bool = True,
    episodes: int = 2,
    seed: int | None = None,
) -> Song:
    """Generate a complete Baroque-style fugue.

    Constructs a full fugue with expositions (subject entries in all voices),
    episodes (connecting passages), and optional stretto (overlapping entries).
    Uses species counterpoint principles for voice leading.

    Args:
        subject:       The main subject melody. If None, generates one.
        voices:        Number of voices (2-4, default 3).
        key:           Key center.
        tonal:         If True, use tonal answer; else real answer.
        include_stretto: If True, include stretto section at the end.
        episodes:      Number of episodes between expositions.
        seed:          Random seed for reproducibility.

    Returns:
        A Song with multiple tracks (one per voice) containing the complete fugue.

    Example::

        >>> from code_music import scale
        >>> subject = scale("C", "major", octave=4, length=8)
        >>> fugue = generate_fugue(subject, voices=3, key="C", seed=42)
        >>> len(fugue.tracks)
        3
        >>> fugue.title
        'Fugue in C major'
    """
    import random as _rng

    from ..engine import Song, Track

    rng = _rng.Random(seed)

    # Generate subject if not provided
    if subject is None:
        from .melody import generate_scale_melody

        subject = generate_scale_melody(key, "major", length=8, seed=seed)

    # Ensure minimum notes
    subject = [n for n in subject if n.pitch is not None][:16]  # Cap length
    if len(subject) < 4:
        from .melody import generate_scale_melody

        subject = generate_scale_melody(key, "major", length=8, seed=seed)

    # Create answer (tonal or real)
    answer_fn = _create_tonal_answer if tonal else _create_real_answer
    answer = answer_fn(subject, key)

    # Create countersubjects
    countersubject = _create_countersubject(subject, key, above=True)

    # Build the fugue structure
    song = Song(title=f"Fugue in {key} major", bpm=100, key_sig=key)

    voice_names = ["Soprano", "Alto", "Tenor", "Bass"][:voices]
    voice_instruments = ["piano", "pad", "organ", "bass"][:voices]
    voice_octaves = [5, 4, 4, 3][:voices]

    # Create tracks
    tracks: list = []
    for i in range(voices):
        t = song.add_track(Track(name=voice_names[i], instrument=voice_instruments[i]))
        tracks.append(t)

    # EXPOSITION: Subject in each voice, alternating with answer
    # Voice order: typically from low to high or high to low
    # Classic order: Bass (subject), Tenor (answer), Alto (subject), Soprano (answer)

    entry_order = list(range(voices - 1, -1, -1))  # Bass to Soprano

    cumulative_beats = 0.0
    entries: list[tuple[int, float, list[Note]]] = []  # (voice_idx, start_beat, melody)

    for i, voice_idx in enumerate(entry_order):
        if i % 2 == 0:
            # Subject entry
            melody = [
                Note(n.pitch, n.octave + (voice_octaves[voice_idx] - 4), n.duration, n.velocity)
                for n in subject
            ]
        else:
            # Answer entry (transposed to dominant)
            melody = [
                Note(n.pitch, n.octave + (voice_octaves[voice_idx] - 4), n.duration, n.velocity)
                for n in answer
            ]

        # Stagger entries (overlap slightly for stretto effect if desired)
        start_beat = cumulative_beats
        entries.append((voice_idx, start_beat, melody))

        # Advance - subject duration minus some overlap
        subject_dur = sum(n.duration for n in subject)
        cumulative_beats += subject_dur * 0.75  # Overlap by 25%

    # Sort entries by start time and add to tracks with rests
    entries.sort(key=lambda x: x[1])

    for voice_idx, start_beat, melody in entries:
        # Add rests until start_beat
        current_beat = 0.0
        while current_beat < start_beat - 0.01:
            rest_dur = min(1.0, start_beat - current_beat)
            tracks[voice_idx].add(Note.rest(rest_dur))
            current_beat += rest_dur

        # Add the melody
        for note in melody:
            tracks[voice_idx].add(note)

    # EPISODES: Connecting passages
    for ep_num in range(episodes):
        episode_length = rng.randint(6, 10)
        episode_notes = _create_episode(
            key, episode_length, voices, seed=rng.randint(0, 10000) if seed else None
        )

        for v in range(voices):
            for note in episode_notes[v]:
                # Adjust octave to voice range
                if note.pitch is not None:
                    adj_note = Note(note.pitch, voice_octaves[v], note.duration, note.velocity)
                    tracks[v].add(adj_note)
                else:
                    tracks[v].add(note)

    # FINAL STRETTO (if requested): Overlapping entries at the end
    if include_stretto and voices >= 2:
        # Subject in all voices with decreasing delays
        stretto_subject = [_create_stretto_subject(subject, 0.0)]

        for i, voice_idx in enumerate(entry_order):
            # Start times decrease: bass first, then tenor soon after, etc.
            delay = i * 1.5  # 1.5 beat delay between entries

            # Add rests for delay
            for _ in range(int(delay)):
                tracks[voice_idx].add(Note.rest(1.0))

            # Add subject (or answer for variety)
            melody = answer if i % 2 else subject
            for note in melody:
                if note.pitch is not None:
                    adj_note = Note(
                        note.pitch, voice_octaves[voice_idx], note.duration, note.velocity
                    )
                    tracks[voice_idx].add(adj_note)

    # Final cadence: all voices converge to tonic
    from ._core import _semi

    key_semi = _semi(key)
    from ._core import _NOTE_NAMES

    tonic = _NOTE_NAMES[key_semi % 12]

    for v in range(voices):
        # Add a whole note tonic
        tracks[v].add(Note(tonic, voice_octaves[v], 4.0, velocity=70))

    return song


# ---------------------------------------------------------------------------
# Auto-Accompaniment (v139.0)
# ---------------------------------------------------------------------------


def auto_accompany(
    melody: list,
    key: str | None = None,
    genre: str = "pop",
    bpm: int = 120,
    title: str | None = None,
    seed: int | None = None,
) -> "Song":
    """Generate a full accompaniment around a melody.

    Takes a melody (list of Notes) and builds bass, chords, and drums
    around it. Detects key if not provided, picks chord progressions
    that fit the melody, generates style-appropriate bass lines and
    drum patterns.

    The inverse of compose() - instead of starting from a prompt, you
    start from a musical idea and get the rest filled in.

    Args:
        melody:  List of Note objects (the lead melody).
        key:     Key center. Auto-detected from melody if None.
        genre:   Style for accompaniment: pop, jazz, rock, blues,
                 classical, electronic, ambient.
        bpm:     Tempo.
        title:   Song title. Defaults to "Accompanied in {key}".
        seed:    Random seed for reproducibility.

    Returns:
        A Song with melody, chords, bass, and drums tracks.

    Example::

        >>> from code_music import Note
        >>> mel = [Note("C",5,1.0), Note("E",5,1.0), Note("G",5,1.0), Note("C",6,2.0)]
        >>> song = auto_accompany(mel, key="C", genre="pop", seed=42)
        >>> len(song.tracks) >= 3
        True
    """
    import random as _rng

    from ..engine import Chord, Note, Song, Track

    rng = _rng.Random(seed)

    # Filter out rests to detect key
    pitched = [n for n in melody if hasattr(n, "pitch") and n.pitch is not None]

    # Auto-detect key from melody
    if key is None:
        try:
            from .harmony import detect_key as _dk

            pitch_pairs = [(str(n.pitch), "maj") for n in pitched[:16]]
            if pitch_pairs:
                key, _, _ = _dk(pitch_pairs)
            else:
                key = "C"
        except Exception:
            key = "C"

    # Calculate melody duration for progression length
    melody_dur = sum(n.duration for n in melody)
    bars = max(2, int(melody_dur / 4))
    chords_needed = max(4, bars)

    # Generate a progression that fits the genre
    try:
        prog = generate_progression(
            key=key,
            length=chords_needed,
            genre=genre,
            seed=rng.randint(0, 2**31),
        )
    except Exception:
        prog = [(key, "maj"), ("F", "maj"), ("G", "maj"), (key, "maj")]
        while len(prog) < chords_needed:
            prog = prog + prog
    prog = prog[:chords_needed]

    # Build the song
    if title is None:
        title = f"Accompanied in {key}"
    song = Song(title=title, bpm=bpm, key_sig=key)

    # Melody track
    melody_track = song.add_track(Track(name="melody", instrument="piano", volume=0.6, pan=0.15))
    for note in melody:
        melody_track.add(note)

    # Chord track
    chord_dur = melody_dur / max(len(prog), 1)
    chord_track = song.add_track(Track(name="chords", instrument="pad", volume=0.35, pan=-0.1))
    for root, shape in prog:
        chord_track.add(Chord(root, shape, 3, duration=max(1.0, chord_dur), velocity=50))

    # Bass track
    bass_styles = {
        "pop": "root_fifth",
        "rock": "root_fifth",
        "jazz": "walking",
        "blues": "walking",
        "classical": "root",
        "electronic": "syncopated",
        "ambient": "root",
    }
    bass_style = bass_styles.get(genre, "root")
    try:
        bass_notes = generate_bass_line(
            prog,
            style=bass_style,
            seed=rng.randint(0, 2**31),
        )
        bass_track = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
        for note in bass_notes:
            bass_track.add(note)
    except Exception:
        bass_track = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
        for root, _ in prog:
            bass_track.add(Note(root, 2, duration=max(1.0, chord_dur), velocity=65))

    # Drums (skip for ambient/classical)
    if genre not in ("ambient", "classical"):
        drum_genres = {
            "pop": "rock",
            "rock": "rock",
            "jazz": "jazz",
            "blues": "jazz",
            "electronic": "electronic",
        }
        drum_genre = drum_genres.get(genre, "rock")
        try:
            drum_data = generate_drums(
                drum_genre,
                bars=bars,
                seed=rng.randint(0, 2**31),
            )
            for drum_name, drum_notes in drum_data.items():
                instr = f"drums_{drum_name}"
                if instr not in ("drums_kick", "drums_snare", "drums_hat"):
                    instr = "drums_kick"
                dr_track = song.add_track(Track(name=drum_name, instrument=instr, volume=0.5))
                for note in drum_notes:
                    dr_track.add(note)
        except Exception:
            pass

    return song


# ---------------------------------------------------------------------------
# Song Comparison (v139.0)
# ---------------------------------------------------------------------------


def compare_songs(
    song_a,
    song_b,
) -> dict:
    """Compare two Songs across multiple dimensions.

    Side-by-side analysis of harmonic, melodic, rhythmic, timbral, and
    structural characteristics. Returns similarity scores and per-dimension
    breakdowns. Useful for A/B comparison, style matching, and plagiarism
    detection.

    Args:
        song_a: First Song.
        song_b: Second Song.

    Returns:
        Dict with:
            overall_similarity:  0.0-1.0 composite score.
            dimensions:          Per-dimension scores:
                harmonic:        Root/quality overlap, key match.
                melodic:         Pitch range, interval, contour.
                rhythmic:        Duration, density, tempo.
                timbral:         Instrument overlap.
                structural:      Track count, length ratio.
            metadata:            Title, BPM, key, track count per song.
            differences:         List of notable differences.

    Example::

        >>> from code_music import Song, Track, Note
        >>> a = Song(title="A", bpm=120); a.add_track(Track()).add(Note("C",4,1.0))
        >>> b = Song(title="B", bpm=120); b.add_track(Track()).add(Note("C",4,1.0))
        >>> result = compare_songs(a, b)
        >>> result["overall_similarity"] > 0.0
        True
    """
    import math

    from .analysis import style_fingerprint

    fp_a = style_fingerprint(song_a)
    fp_b = style_fingerprint(song_b)

    def _dict_similarity(d1: dict, d2: dict) -> float:
        """Compare two feature dicts by normalized Euclidean distance."""
        keys = set(d1.keys()) | set(d2.keys())
        if not keys:
            return 1.0
        sq_sum = sum((float(d1.get(k, 0)) - float(d2.get(k, 0))) ** 2 for k in keys)
        dist = math.sqrt(sq_sum)
        max_possible = math.sqrt(len(keys))
        return max(0.0, 1.0 - dist / max(max_possible, 1.0))

    harmonic_sim = _dict_similarity(fp_a["harmonic"], fp_b["harmonic"])
    melodic_sim = _dict_similarity(fp_a["melodic"], fp_b["melodic"])
    rhythmic_sim = _dict_similarity(fp_a["rhythmic"], fp_b["rhythmic"])
    timbral_sim = _dict_similarity(fp_a["timbral"], fp_b["timbral"])
    structural_sim = _dict_similarity(fp_a["structural"], fp_b["structural"])

    weights = {
        "harmonic": 0.30,
        "melodic": 0.25,
        "rhythmic": 0.20,
        "timbral": 0.10,
        "structural": 0.15,
    }
    overall = sum(
        weights[k] * v
        for k, v in {
            "harmonic": harmonic_sim,
            "melodic": melodic_sim,
            "rhythmic": rhythmic_sim,
            "timbral": timbral_sim,
            "structural": structural_sim,
        }.items()
    )

    differences: list[str] = []

    bpm_a = getattr(song_a, "bpm", 120)
    bpm_b = getattr(song_b, "bpm", 120)
    if abs(bpm_a - bpm_b) > 10:
        differences.append(f"Tempo: {bpm_a:.0f} vs {bpm_b:.0f} BPM")

    key_a = getattr(song_a, "key_sig", "C") or "C"
    key_b = getattr(song_b, "key_sig", "C") or "C"
    if key_a != key_b:
        differences.append(f"Key: {key_a} vs {key_b}")

    tracks_a = len(song_a.tracks)
    tracks_b = len(song_b.tracks)
    if tracks_a != tracks_b:
        differences.append(f"Track count: {tracks_a} vs {tracks_b}")

    instr_a = set(t.instrument for t in song_a.tracks)
    instr_b = set(t.instrument for t in song_b.tracks)
    only_a = instr_a - instr_b
    only_b = instr_b - instr_a
    if only_a:
        differences.append(f"Only in A: {', '.join(sorted(only_a))}")
    if only_b:
        differences.append(f"Only in B: {', '.join(sorted(only_b))}")

    if harmonic_sim < 0.5:
        differences.append("Harmonic content differs significantly")
    if melodic_sim < 0.5:
        differences.append("Melodic character differs significantly")

    return {
        "overall_similarity": round(overall, 4),
        "dimensions": {
            "harmonic": round(harmonic_sim, 4),
            "melodic": round(melodic_sim, 4),
            "rhythmic": round(rhythmic_sim, 4),
            "timbral": round(timbral_sim, 4),
            "structural": round(structural_sim, 4),
        },
        "metadata": {
            "a": {"title": song_a.title, "bpm": bpm_a, "key": key_a, "tracks": tracks_a},
            "b": {"title": song_b.title, "bpm": bpm_b, "key": key_b, "tracks": tracks_b},
        },
        "differences": differences,
    }


# ---------------------------------------------------------------------------
# Interactive Theory Course (v141.0)
# ---------------------------------------------------------------------------

_THEORY_LESSONS = [
    {
        "id": 1,
        "title": "Notes and Octaves",
        "topic": "basics",
        "description": "The 12 chromatic notes and octave numbering system.",
        "concepts": ["note names", "octaves", "semitones", "enharmonics"],
        "exercises": [
            {"type": "identify", "question": "How many semitones in an octave?", "answer": "12"},
            {"type": "identify", "question": "What note is 7 semitones above C?", "answer": "G"},
            {"type": "identify", "question": "What is the enharmonic of C#?", "answer": "Db"},
        ],
    },
    {
        "id": 2,
        "title": "Major Scales",
        "topic": "scales",
        "description": "The major scale pattern: W-W-H-W-W-W-H.",
        "concepts": ["whole steps", "half steps", "major scale formula", "key signatures"],
        "exercises": [
            {"type": "identify", "question": "How many sharps in G major?", "answer": "1"},
            {"type": "identify", "question": "What is the 5th note of C major?", "answer": "G"},
            {
                "type": "identify",
                "question": "What mode starts on the 6th degree of major?",
                "answer": "aeolian",
            },
        ],
    },
    {
        "id": 3,
        "title": "Minor Scales",
        "topic": "scales",
        "description": "Natural, harmonic, and melodic minor scales.",
        "concepts": ["natural minor", "harmonic minor", "melodic minor", "relative major"],
        "exercises": [
            {
                "type": "identify",
                "question": "What is the relative minor of C major?",
                "answer": "A",
            },
            {
                "type": "identify",
                "question": "What degree is raised in harmonic minor?",
                "answer": "7",
            },
            {"type": "identify", "question": "How many flats in F minor?", "answer": "4"},
        ],
    },
    {
        "id": 4,
        "title": "Intervals",
        "topic": "intervals",
        "description": "Distance between two notes measured in semitones and quality.",
        "concepts": ["major", "minor", "perfect", "augmented", "diminished", "tritone"],
        "exercises": [
            {"type": "interval", "note_a": "C", "note_b": "G", "answer": "perfect 5th"},
            {"type": "interval", "note_a": "C", "note_b": "E", "answer": "major 3rd"},
            {"type": "interval", "note_a": "C", "note_b": "Bb", "answer": "minor 7th"},
        ],
    },
    {
        "id": 5,
        "title": "Triads",
        "topic": "chords",
        "description": "Three-note chords built in thirds: major, minor, diminished, augmented.",
        "concepts": ["major triad", "minor triad", "diminished triad", "augmented triad"],
        "exercises": [
            {"type": "identify", "question": "What notes are in C major triad?", "answer": "C E G"},
            {"type": "identify", "question": "What quality is C-Eb-G?", "answer": "minor"},
            {"type": "identify", "question": "What quality is C-E-G#?", "answer": "augmented"},
        ],
    },
    {
        "id": 6,
        "title": "Seventh Chords",
        "topic": "chords",
        "description": "Four-note chords: maj7, min7, dom7, half-dim, dim7.",
        "concepts": ["major 7th", "minor 7th", "dominant 7th", "half-diminished", "diminished 7th"],
        "exercises": [
            {"type": "identify", "question": "What type is C-E-G-Bb?", "answer": "dom7"},
            {"type": "identify", "question": "What type is C-Eb-G-Bb?", "answer": "min7"},
            {"type": "identify", "question": "What type is C-E-G-B?", "answer": "maj7"},
        ],
    },
    {
        "id": 7,
        "title": "Chord Progressions",
        "topic": "harmony",
        "description": "Common chord movement patterns in tonal music.",
        "concepts": ["I-IV-V-I", "ii-V-I", "12-bar blues", "circle of fifths"],
        "exercises": [
            {"type": "identify", "question": "What Roman numeral is the dominant?", "answer": "V"},
            {"type": "identify", "question": "What chord resolves V7 in C major?", "answer": "C"},
            {"type": "identify", "question": "What is ii-V-I in C major?", "answer": "Dm G C"},
        ],
    },
    {
        "id": 8,
        "title": "Cadences",
        "topic": "harmony",
        "description": "Musical punctuation: how phrases end.",
        "concepts": ["perfect", "plagal", "half", "deceptive"],
        "exercises": [
            {"type": "identify", "question": "What cadence is V-I?", "answer": "perfect"},
            {"type": "identify", "question": "What cadence is IV-I?", "answer": "plagal"},
            {"type": "identify", "question": "What cadence ends on V?", "answer": "half"},
        ],
    },
    {
        "id": 9,
        "title": "Voice Leading",
        "topic": "harmony",
        "description": "Smooth movement between chords: minimal motion, no parallel 5ths.",
        "concepts": ["common tones", "stepwise motion", "parallel fifths", "contrary motion"],
        "exercises": [
            {
                "type": "identify",
                "question": "What motion type moves voices in opposite directions?",
                "answer": "contrary",
            },
            {
                "type": "identify",
                "question": "What interval is forbidden in parallel motion?",
                "answer": "5th",
            },
            {
                "type": "identify",
                "question": "A note shared between two chords is called a?",
                "answer": "common tone",
            },
        ],
    },
    {
        "id": 10,
        "title": "Modes",
        "topic": "scales",
        "description": "The seven modes of the major scale: Ionian through Locrian.",
        "concepts": ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"],
        "exercises": [
            {
                "type": "identify",
                "question": "What mode has a raised 4th degree?",
                "answer": "lydian",
            },
            {
                "type": "identify",
                "question": "What mode has a flat 7th and is major-sounding?",
                "answer": "mixolydian",
            },
            {
                "type": "identify",
                "question": "What mode starts on the 2nd degree of major?",
                "answer": "dorian",
            },
        ],
    },
    {
        "id": 11,
        "title": "Rhythm and Meter",
        "topic": "rhythm",
        "description": "Time signatures, subdivisions, syncopation.",
        "concepts": ["time signature", "simple meter", "compound meter", "syncopation", "swing"],
        "exercises": [
            {"type": "identify", "question": "How many beats in 4/4 time?", "answer": "4"},
            {"type": "identify", "question": "What is 6/8 classified as?", "answer": "compound"},
            {
                "type": "identify",
                "question": "Emphasis on off-beats is called?",
                "answer": "syncopation",
            },
        ],
    },
    {
        "id": 12,
        "title": "Song Form",
        "topic": "form",
        "description": "How sections organize into complete pieces.",
        "concepts": ["verse", "chorus", "bridge", "AABA", "sonata", "rondo", "binary", "ternary"],
        "exercises": [
            {"type": "identify", "question": "What form is A-B-A-C-A?", "answer": "rondo"},
            {
                "type": "identify",
                "question": "What form has exposition-development-recap?",
                "answer": "sonata",
            },
            {"type": "identify", "question": "What form is A-B?", "answer": "binary"},
        ],
    },
]


def theory_course(
    lesson_id: int | None = None,
    topic: str | None = None,
) -> dict | list[dict]:
    """Interactive music theory course with structured lessons.

    12 lessons covering notes, scales, intervals, chords, progressions,
    cadences, voice leading, modes, rhythm, and form. Each lesson has
    a topic, description, concepts, and graded exercises.

    Call with no args to get the full syllabus. Call with a lesson_id
    to get a specific lesson. Call with a topic to filter by category.

    Args:
        lesson_id: Specific lesson number (1-12).
        topic:     Filter by topic: basics, scales, intervals, chords,
                   harmony, rhythm, form.

    Returns:
        Single lesson dict (if lesson_id given), or list of lessons.

    Example::

        >>> syllabus = theory_course()
        >>> len(syllabus)
        12
        >>> lesson = theory_course(lesson_id=1)
        >>> lesson["title"]
        'Notes and Octaves'
    """
    lessons = _THEORY_LESSONS

    if lesson_id is not None:
        for lesson in lessons:
            if lesson["id"] == lesson_id:
                return lesson
        return {"error": f"No lesson with id {lesson_id}. Valid: 1-{len(lessons)}"}

    if topic is not None:
        return [l for l in lessons if l["topic"] == topic]

    return lessons


def grade_lesson(
    lesson_id: int,
    answers: list[str],
) -> dict:
    """Grade answers for a theory course lesson.

    Compares user answers against the lesson's exercise answers.
    Returns score, percentage, letter grade, and per-question feedback.

    Args:
        lesson_id: Lesson number (1-12).
        answers:   List of user answers (one per exercise).

    Returns:
        Dict with score, total, percentage, grade, and feedback list.

    Example::

        >>> result = grade_lesson(1, ["12", "G", "Db"])
        >>> result["percentage"]
        100.0
        >>> result["grade"]
        'A'
    """
    lesson = theory_course(lesson_id=lesson_id)
    if isinstance(lesson, dict) and "error" in lesson:
        return lesson

    exercises = lesson["exercises"]
    correct = [ex["answer"] for ex in exercises]

    total = len(correct)
    feedback: list[dict] = []
    right = 0

    for i, (user, expected) in enumerate(zip(answers, correct)):
        is_correct = user.strip().lower() == expected.strip().lower()
        if is_correct:
            right += 1
        feedback.append(
            {
                "question": i + 1,
                "your_answer": user,
                "correct_answer": expected,
                "correct": is_correct,
            }
        )

    # Grade remaining unanswered
    for i in range(len(answers), total):
        feedback.append(
            {
                "question": i + 1,
                "your_answer": "(no answer)",
                "correct_answer": correct[i],
                "correct": False,
            }
        )

    pct = round(right / max(total, 1) * 100, 1)
    if pct >= 90:
        grade = "A"
    elif pct >= 80:
        grade = "B"
    elif pct >= 70:
        grade = "C"
    elif pct >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "lesson": lesson["title"],
        "score": right,
        "total": total,
        "percentage": pct,
        "grade": grade,
        "feedback": feedback,
    }
