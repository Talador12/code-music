"""Sheet music notation exporters: LilyPond, ABC, MusicXML.

LilyPond (.ly)   — Compiles to publication-quality PDF/SVG via `lilypond` CLI.
                   Human-readable text. The best looking output.
                   Install: brew install lilypond

ABC Notation (.abc) — Plain text, web-native. Renderable in any browser with
                       abcjs (https://paulrosen.github.io/abcjs/).
                       Paste into https://abc.rectanglered.com to see it.

MusicXML (.xml)  — Universal compatibility. Opens in MuseScore, Sibelius,
                   Finale, Dorico, Noteflight, Guitar Pro, etc.
                   The oldest and most widely supported format (2004, still the standard).

Usage::

    from code_music.notation import export_lilypond, export_abc, export_musicxml
    export_lilypond(song, "my_song.ly")   # then: lilypond my_song.ly
    export_abc(song, "my_song.abc")
    export_musicxml(song, "my_song.xml")
"""

from __future__ import annotations

from pathlib import Path

from .engine import Beat, Chord, Note, Song

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# ---------------------------------------------------------------------------
# Duration helpers
# ---------------------------------------------------------------------------

# Map beat-count → (lily_duration, dots)
# 1 beat = quarter note.  Lily uses 1=whole, 2=half, 4=quarter, 8=eighth ...
_BEAT_TO_LILY: list[tuple[float, str]] = [
    (4.0, "1"),
    (3.0, "2."),
    (2.0, "2"),
    (1.5, "4."),
    (1.0, "4"),
    (0.75, "8."),
    (0.5, "8"),
    (0.375, "16."),
    (0.25, "16"),
    (0.1875, "32."),
    (0.125, "32"),
    (0.0625, "64"),
]

_BEAT_TO_ABC: list[tuple[float, str]] = [
    # ABC unit = 1/8 note by default (L:1/8).  1 beat (quarter) = 2 units.
    (4.0, "8"),  # whole      = 8 units
    (3.0, "6"),  # dot half   = 6
    (2.0, "4"),  # half       = 4
    (1.5, "3"),  # dot quarter= 3
    (1.0, "2"),  # quarter    = 2
    (0.75, "3/2"),  # dot 8th    = 3/2
    (0.5, ""),  # eighth     = 1 (the unit)
    (0.25, "/2"),  # sixteenth  = 1/2
    (0.125, "/4"),  # 32nd       = 1/4
]

_BEAT_TO_XML_TYPE: list[tuple[float, tuple[str, int]]] = [
    (4.0, ("whole", 0)),
    (3.0, ("half", 1)),
    (2.0, ("half", 0)),
    (1.5, ("quarter", 1)),
    (1.0, ("quarter", 0)),
    (0.75, ("eighth", 1)),
    (0.5, ("eighth", 0)),
    (0.375, ("16th", 1)),
    (0.25, ("16th", 0)),
    (0.125, ("32nd", 0)),
    (0.0625, ("64th", 0)),
]


def _closest_str(table: list[tuple[float, str]], dur: float) -> str:
    return min(table, key=lambda x: abs(x[0] - dur))[1]


def _closest_xml(dur: float) -> tuple[str, int]:
    return min(_BEAT_TO_XML_TYPE, key=lambda x: abs(x[0] - dur))[1]


def _midi_to_name_octave(midi: int) -> tuple[str, int]:
    name = NOTE_NAMES[midi % 12]
    octave = midi // 12 - 1
    return name, octave


# ---------------------------------------------------------------------------
# LilyPond export
# ---------------------------------------------------------------------------

# Note name mapping: sharps for Lily (c d e f g a b, with is/es suffix)
_LILY_NAMES = {
    "C": "c",
    "C#": "cis",
    "D": "d",
    "D#": "dis",
    "E": "e",
    "F": "f",
    "F#": "fis",
    "G": "g",
    "G#": "gis",
    "A": "a",
    "A#": "ais",
    "B": "b",
}

# Lily key signatures
_LILY_KEYS = {
    "C": "c",
    "G": "g",
    "D": "d",
    "A": "a",
    "E": "e",
    "B": "b",
    "F#": "fis",
    "C#": "cis",
    "F": "f",
    "Bb": "bes",
    "Eb": "ees",
    "Ab": "aes",
    "Db": "des",
    "Gb": "ges",
}

_LILY_MODES = {"major": r"\major", "minor": r"\minor"}


def _note_to_lily(note: Note) -> str:
    if note.pitch is None:
        dur = _closest_str(_BEAT_TO_LILY, note.duration)
        return f"r{dur}"

    midi = note.midi or 60
    name, octave = _midi_to_name_octave(midi)
    lily_name = _LILY_NAMES.get(name, "c")
    dur = _closest_str(_BEAT_TO_LILY, note.duration)

    # LilyPond octave: middle C is c' (octave 4 = one tick up from c)
    # c without ticks = octave 3. c' = 4, c'' = 5, c, = 2, c,, = 1
    ticks = octave - 3
    if ticks > 0:
        lily_name += "'" * ticks
    elif ticks < 0:
        lily_name += "," * (-ticks)

    return f"{lily_name}{dur}"


def _chord_to_lily(chord: Chord) -> str:
    notes = chord.notes
    if not notes:
        return "r4"
    dur = _closest_str(_BEAT_TO_LILY, chord.duration)
    pitches = []
    for n in notes:
        midi = n.midi or 60
        name, octave = _midi_to_name_octave(midi)
        lily_name = _LILY_NAMES.get(name, "c")
        ticks = octave - 3
        if ticks > 0:
            lily_name += "'" * ticks
        elif ticks < 0:
            lily_name += "," * (-ticks)
        pitches.append(lily_name)
    return f"<{' '.join(pitches)}>{dur}"


def export_lilypond(song: Song, path: str | Path) -> Path:
    """Export a Song to a LilyPond (.ly) file.

    Compile to PDF with: ``lilypond my_song.ly``
    Compile to SVG with: ``lilypond --svg my_song.ly``

    Each Track becomes a separate Staff. Voices/Chords are represented.
    Duration quantisation rounds to the nearest standard value.

    Args:
        song: Song to export.
        path: Output file path (gets .ly extension).

    Returns:
        Path of the written file.
    """
    out = Path(path).with_suffix(".ly")
    out.parent.mkdir(parents=True, exist_ok=True)

    num, den = song.time_sig
    key_root = _LILY_KEYS.get(song.key_sig, "c")
    composer = song.composer or ""

    lines = [
        r'\version "2.24.0"',
        r"\header {",
        f'  title = "{song.title}"',
    ]
    if composer:
        lines.append(f'  composer = "{composer}"')
    lines += [
        "}",
        "",
        r"\score {",
        r"  <<",
    ]

    for track in song.tracks:
        lines.append(f"    % Track: {track.name} ({track.instrument})")
        lines.append(r"    \new Staff {")
        lines.append(r"      \new Voice {")
        lines.append(f"        \\tempo 4 = {int(song.bpm)}")
        lines.append(f"        \\time {num}/{den}")
        lines.append(f"        \\key {key_root} \\major")
        lines.append("        {")

        measure: list[str] = []
        measure_beats = 0.0
        beats_per_bar = num * 4 / den  # beats (quarters) per bar

        for beat in track.beats:
            event = beat.event
            if event is None:
                token = f"r{_closest_str(_BEAT_TO_LILY, beat.duration)}"
                dur = beat.duration
            elif isinstance(event, Note):
                token = _note_to_lily(event)
                dur = event.duration
            elif isinstance(event, Chord):
                token = _chord_to_lily(event)
                dur = event.duration
            else:
                continue

            measure.append(token)
            measure_beats += dur

            if measure_beats >= beats_per_bar - 0.001:
                lines.append("          " + " ".join(measure) + " |")
                measure = []
                measure_beats = 0.0

        if measure:
            lines.append("          " + " ".join(measure))

        lines += [
            "        }",
            "      }",
            "    }",
        ]

    lines += [
        "  >>",
        r"  \layout { }",
        r"  \midi { }",
        "}",
    ]

    out.write_text("\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------------------
# ABC Notation export
# ---------------------------------------------------------------------------

_ABC_NOTES = {
    "C": "C",
    "C#": "^C",
    "D": "D",
    "D#": "^D",
    "E": "E",
    "F": "F",
    "F#": "^F",
    "G": "G",
    "G#": "^G",
    "A": "A",
    "A#": "^A",
    "B": "B",
}

# ABC octaves: C,=low C (oct2), C=middle C (oct4?), c=oct5, c'=oct6
# Actually in ABC: CDEFGAB = octave 4 (C4..B4), cdefgab = octave 5
# C, D, etc = octave 3. C,, = octave 2.  c' = octave 6.


def _note_to_abc(note: Note) -> str:
    if note.pitch is None:
        dur = _closest_str(_BEAT_TO_ABC, note.duration)
        return f"z{dur}"

    midi = note.midi or 60
    name, octave = _midi_to_name_octave(midi)
    acc = "^" if "#" in name else ""
    base = name.replace("#", "")

    if octave <= 3:
        abc_name = acc + base.upper() + "," * (4 - octave - 1)
    elif octave == 4:
        abc_name = acc + base.upper()
    elif octave == 5:
        abc_name = acc + base.lower()
    else:
        abc_name = acc + base.lower() + "'" * (octave - 5)

    dur = _closest_str(_BEAT_TO_ABC, note.duration)
    return f"{abc_name}{dur}"


def _chord_to_abc(chord: Chord) -> str:
    notes = chord.notes
    if not notes:
        dur = _closest_str(_BEAT_TO_ABC, chord.duration)
        return f"z{dur}"
    inner = "".join(_note_to_abc(n).rstrip("0123456789/") for n in notes)
    dur = _closest_str(_BEAT_TO_ABC, chord.duration)
    return f"[{inner}]{dur}"


def export_abc(song: Song, path: str | Path) -> Path:
    """Export a Song to ABC notation (.abc).

    ABC is plain text and web-renderable. Paste the output into:
    https://abc.rectanglered.com  or  https://abcjs.net/abcjs-editor.html

    Each Track becomes a separate voice.

    Args:
        song: Song to export.
        path: Output file path (gets .abc extension).

    Returns:
        Path of the written file.
    """
    out = Path(path).with_suffix(".abc")
    out.parent.mkdir(parents=True, exist_ok=True)

    num, den = song.time_sig
    # Compute default note length: L:1/8 means 8th note = 1 unit
    # 1 beat (quarter) = 2 units when L:1/8
    lines = [
        "X:1",
        f"T:{song.title}",
    ]
    if song.composer:
        lines.append(f"C:{song.composer}")
    lines += [
        f"M:{num}/{den}",
        "L:1/8",
        f"Q:1/4={int(song.bpm)}",
        f"K:{song.key_sig}",
        "",
    ]

    beats_per_bar = num * 4 / den

    for i, track in enumerate(song.tracks):
        if i > 0:
            lines.append("")
        lines.append(f"% Voice: {track.name} ({track.instrument})")
        if len(song.tracks) > 1:
            lines.append(f'V:{i + 1} name="{track.name}"')

        bar_tokens: list[str] = []
        bar_beats = 0.0
        bars: list[str] = []

        for beat in track.beats:
            event = beat.event
            if event is None:
                token = f"z{_closest_str(_BEAT_TO_ABC, beat.duration)}"
                dur = beat.duration
            elif isinstance(event, Note):
                token = _note_to_abc(event)
                dur = event.duration
            elif isinstance(event, Chord):
                token = _chord_to_abc(event)
                dur = event.duration
            else:
                continue

            bar_tokens.append(token)
            bar_beats += dur

            if bar_beats >= beats_per_bar - 0.001:
                bars.append(" ".join(bar_tokens))
                bar_tokens = []
                bar_beats = 0.0

        if bar_tokens:
            bars.append(" ".join(bar_tokens))

        # Wrap at ~72 chars
        line = ""
        for j, bar in enumerate(bars):
            segment = bar + " | "
            if len(line) + len(segment) > 72 and line:
                lines.append(line.rstrip())
                line = ""
            line += segment
        if line:
            lines.append(line.rstrip(" |") + " |]")

    out.write_text("\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------------------
# MusicXML export
# ---------------------------------------------------------------------------

_XML_STEP = {
    "C": ("C", 0),
    "C#": ("C", 1),
    "D": ("D", 0),
    "D#": ("D", 1),
    "E": ("E", 0),
    "F": ("F", 0),
    "F#": ("F", 1),
    "G": ("G", 0),
    "G#": ("G", 1),
    "A": ("A", 0),
    "A#": ("A", 1),
    "B": ("B", 0),
}

_XML_KEY_FIFTHS = {
    "C": 0,
    "G": 1,
    "D": 2,
    "A": 3,
    "E": 4,
    "B": 5,
    "F#": 6,
    "F": -1,
    "Bb": -2,
    "Eb": -3,
    "Ab": -4,
    "Db": -5,
    "Gb": -6,
    "C#": 7,
}


def _beat_to_xml_duration(beats: float, divisions: int = 4) -> int:
    """Convert beat count to MusicXML duration ticks (divisions per quarter)."""
    return max(1, round(beats * divisions))


def _note_to_xml(note: Note, divisions: int = 4, is_chord: bool = False) -> list[str]:
    dur_ticks = _beat_to_xml_duration(note.duration, divisions)
    xml_type, dots = _closest_xml(note.duration)
    lines = ["    <note>"]
    if is_chord:
        lines.append("      <chord/>")
    if note.pitch is None:
        lines.append("      <rest/>")
    else:
        midi = note.midi or 60
        name, octave = _midi_to_name_octave(midi)
        step, alter = _XML_STEP.get(name, ("C", 0))
        lines += [
            "      <pitch>",
            f"        <step>{step}</step>",
        ]
        if alter:
            lines.append(f"        <alter>{alter}</alter>")
        lines += [
            f"        <octave>{octave}</octave>",
            "      </pitch>",
        ]
    lines += [
        f"      <duration>{dur_ticks}</duration>",
        f"      <type>{xml_type}</type>",
    ]
    for _ in range(dots):
        lines.append("      <dot/>")
    lines.append("    </note>")
    return lines
    return lines


def export_musicxml(song: Song, path: str | Path) -> Path:
    """Export a Song to MusicXML (.xml).

    Opens in MuseScore, Sibelius, Dorico, Finale, Noteflight, Guitar Pro.
    MusicXML is the universal sheet music interchange format.

    Args:
        song: Song to export.
        path: Output file path (gets .xml extension).

    Returns:
        Path of the written file.
    """
    out = Path(path).with_suffix(".xml")
    out.parent.mkdir(parents=True, exist_ok=True)

    divisions = 4  # ticks per quarter note
    num, den = song.time_sig
    fifths = _XML_KEY_FIFTHS.get(song.key_sig, 0)
    beats_per_bar = num * 4 / den

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN"',
        '  "http://www.musicxml.org/dtds/partwise.dtd">',
        '<score-partwise version="4.0">',
        "  <work>",
        f"    <work-title>{song.title}</work-title>",
        "  </work>",
        "  <identification>",
        "    <encoding>",
        "      <software>code-music</software>",
        "    </encoding>",
        "  </identification>",
        "  <part-list>",
    ]

    for i, track in enumerate(song.tracks):
        part_id = f"P{i + 1}"
        lines += [
            f'    <score-part id="{part_id}">',
            f"      <part-name>{track.name}</part-name>",
            "    </score-part>",
        ]

    lines.append("  </part-list>")

    for i, track in enumerate(song.tracks):
        part_id = f"P{i + 1}"
        lines.append(f'  <part id="{part_id}">')

        # Split beats into measures
        measures: list[list[Beat]] = []
        current: list[Beat] = []
        bar_beats = 0.0
        for beat in track.beats:
            current.append(beat)
            bar_beats += beat.duration
            if bar_beats >= beats_per_bar - 0.001:
                measures.append(current)
                current = []
                bar_beats = 0.0
        if current:
            measures.append(current)

        for m_idx, measure_beats in enumerate(measures):
            lines.append(f'    <measure number="{m_idx + 1}">')
            if m_idx == 0:
                lines += [
                    "      <attributes>",
                    f"        <divisions>{divisions}</divisions>",
                    "        <key>",
                    f"          <fifths>{fifths}</fifths>",
                    "        </key>",
                    "        <time>",
                    f"          <beats>{num}</beats>",
                    f"          <beat-type>{den}</beat-type>",
                    "        </time>",
                    "        <clef>",
                    "          <sign>G</sign>",
                    "          <line>2</line>",
                    "        </clef>",
                    "      </attributes>",
                    '      <direction placement="above">',
                    "        <direction-type>",
                    f"          <metronome><beat-unit>quarter</beat-unit>"
                    f"<per-minute>{int(song.bpm)}</per-minute></metronome>",
                    "        </direction-type>",
                    "      </direction>",
                ]

            for beat in measure_beats:
                event = beat.event
                if event is None:
                    n = Note.rest(beat.duration)
                    lines.extend("      " + ln for ln in _note_to_xml(n, divisions))
                elif isinstance(event, Note):
                    lines.extend("      " + ln for ln in _note_to_xml(event, divisions))
                elif isinstance(event, Chord):
                    chord_notes = event.notes
                    if chord_notes:
                        first = _note_to_xml(chord_notes[0], divisions)
                        lines.extend("      " + ln for ln in first)
                        for cn in chord_notes[1:]:
                            lines.extend(
                                "      " + ln for ln in _note_to_xml(cn, divisions, is_chord=True)
                            )

            lines.append("    </measure>")

        lines.append("  </part>")

    lines.append("</score-partwise>")
    out.write_text("\n".join(lines) + "\n")
    return out
