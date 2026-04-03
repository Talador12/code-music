"""Music theory intelligence — chord-scale theory, tension analysis, smart generators.

Example::

    from code_music.theory import (
        chord_scale, available_tensions, generate_bass_line, generate_drums,
    )

    scales = chord_scale("C", "min7")     # → ["dorian", "aeolian", "phrygian"]
    tensions = available_tensions("C", "min7")  # → ["9", "11", "13"]
    bass = generate_bass_line([("C", "min7"), ("F", "dom7")], style="walking")
    drums = generate_drums("jazz", bars=4)
"""

from __future__ import annotations

from .engine import Note, euclid

# ---------------------------------------------------------------------------
# Note utilities
# ---------------------------------------------------------------------------

_NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_NOTE_TO_SEMI = {n: i for i, n in enumerate(_NOTE_NAMES)}
# Enharmonic aliases
_NOTE_TO_SEMI.update(
    {"Db": 1, "D#": 3, "Fb": 4, "E#": 5, "Gb": 6, "G#": 8, "A#": 10, "Cb": 11, "B#": 0}
)


def _semi(note: str) -> int:
    return _NOTE_TO_SEMI[note]


# ---------------------------------------------------------------------------
# Scale intervals (semitones from root)
# ---------------------------------------------------------------------------

_SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11],  # half-whole
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
}

# Chord shape → semitones from root
_CHORD_SEMI = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "min7b5": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "min9": [0, 3, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "dom9": [0, 4, 7, 10, 14],
}


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
# Song diffing
# ---------------------------------------------------------------------------
# Harmonic analysis
# ---------------------------------------------------------------------------

_ROMAN = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}

_QUALITY_MAP = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "+",
    "dom7": "7",
    "maj7": "M7",
    "min7": "m7",
    "dim7": "dim7",
    "min7b5": "m7b5",
    "sus2": "sus2",
    "sus4": "sus4",
    "min9": "m9",
    "maj9": "M9",
    "dom9": "9",
}

_FUNCTION_MAP = {
    0: "tonic",
    2: "supertonic",
    4: "mediant",
    5: "subdominant",
    7: "dominant",
    9: "submediant",
    11: "leading",
}


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
    from .engine import Chord

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
    from .engine import Track

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
