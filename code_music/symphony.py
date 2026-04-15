"""Symphony and orchestral composition system.

Build multi-movement orchestral works with full score export to sheet music.
Handles transposing instruments, orchestral families, score order, part
extraction, and movement-level structure.

Example::

    from code_music.symphony import Symphony, Movement, OrchestraScore
    from code_music import Note, Chord, Track, Song

    sym = Symphony(title="Symphony No. 1", composer="K. Adler", key="C", bpm=120)

    # First movement: Allegro
    mvt1 = sym.add_movement("I. Allegro", bpm=132, time_sig=(4, 4), key="C")
    mvt1.add_part("flute", instrument="flute")
    mvt1.add_part("oboe", instrument="oboe")
    mvt1.add_part("violin_1", instrument="violin")
    mvt1.add_part("violin_2", instrument="violin")
    mvt1.add_part("viola", instrument="viola")
    mvt1.add_part("cello", instrument="cello")
    mvt1.add_part("contrabass", instrument="contrabass")

    # Add notes to parts
    mvt1.parts["flute"].extend(scale("C", "major", 6, length=16))
    # ...

    # Export full orchestral score
    sym.export_score("symphony_no1.xml", format="musicxml")
    sym.export_score("symphony_no1.ly", format="lilypond")

    # Export individual parts for performers
    sym.export_part("flute", "flute_part.xml")

    # Render audio
    song = sym.render()
    song.render()
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Sequence

from .engine import (
    Beat,
    Chord,
    Note,
    Song,
    Track,
    note_name_to_midi,
    midi_to_note_name,
)


# ---------------------------------------------------------------------------
# Orchestral family definitions and score ordering
# ---------------------------------------------------------------------------

# Standard orchestral score order (top to bottom of a full score)
SCORE_ORDER = [
    # Woodwinds
    "piccolo",
    "flute",
    "alto_flute",
    "oboe",
    "cor_anglais",
    "english_horn",
    "clarinet",
    "bass_clarinet",
    "bassoon",
    "contrabassoon",
    # Brass
    "french_horn",
    "trumpet",
    "piccolo_trumpet",
    "cornet",
    "flugelhorn",
    "trombone",
    "bass_trombone",
    "euphonium",
    "tuba",
    # Percussion
    "timpani",
    "snare_orch",
    "cymbals",
    "triangle_perc",
    "gong",
    "xylophone",
    "marimba",
    "vibraphone",
    "glockenspiel",
    "celesta",
    # Keyboards
    "piano",
    "organ",
    "harpsichord",
    "harp",
    # Voices
    "soprano_voice",
    "alto_voice",
    "tenor_voice",
    "bass_voice",
    "choir_aah",
    "choir_ooh",
    # Strings
    "violin_1",
    "violin_2",
    "viola",
    "cello",
    "contrabass",
    # Aliases for common naming
    "violin",
    "strings",
    "string_section",
]

# Instrument families for grouping in score layout
FAMILIES = {
    "woodwinds": [
        "piccolo",
        "flute",
        "alto_flute",
        "oboe",
        "cor_anglais",
        "english_horn",
        "clarinet",
        "bass_clarinet",
        "bassoon",
        "contrabassoon",
        "soprano_sax",
        "tenor_sax",
        "bari_sax",
        "saxophone",
    ],
    "brass": [
        "french_horn",
        "trumpet",
        "piccolo_trumpet",
        "cornet",
        "flugelhorn",
        "trombone",
        "bass_trombone",
        "euphonium",
        "tuba",
        "horn_section",
        "brass_section",
    ],
    "percussion": [
        "timpani",
        "snare_orch",
        "cymbals",
        "triangle_perc",
        "gong",
        "xylophone",
        "marimba",
        "vibraphone",
        "glockenspiel",
        "drums_kick",
        "drums_snare",
        "drums_hat",
        "taiko",
        "tabla",
        "djembe",
        "cajon",
        "bongo",
        "conga",
        "tambourine",
        "cowbell",
        "woodblock",
        "timbales",
        "surdo",
        "shaker",
    ],
    "keyboards": [
        "piano",
        "organ",
        "harpsichord",
        "celesta",
        "rhodes",
        "wurlitzer",
        "accordion",
        "bandoneon",
        "harmonica",
    ],
    "strings": [
        "violin",
        "violin_1",
        "violin_2",
        "viola",
        "cello",
        "contrabass",
        "strings",
        "string_section",
        "string_tremolo",
        "string_harmonics",
        "harp",
        "guitar_acoustic",
        "guitar_electric",
    ],
    "voices": [
        "soprano_voice",
        "alto_voice",
        "tenor_voice",
        "bass_voice",
        "choir_aah",
        "choir_ooh",
        "vox_pad",
    ],
}

# Transposing instruments: key they are pitched in (concert pitch offset in semitones)
TRANSPOSING_INSTRUMENTS = {
    "clarinet": -2,  # Bb clarinet: sounds M2 lower than written
    "bass_clarinet": -14,  # Bb bass clarinet: sounds M9 lower
    "trumpet": -2,  # Bb trumpet: sounds M2 lower
    "cornet": -2,  # Bb cornet
    "flugelhorn": -2,  # Bb flugelhorn
    "french_horn": -7,  # F horn: sounds P5 lower
    "english_horn": -7,  # F english horn
    "cor_anglais": -7,  # F cor anglais (same as english horn)
    "soprano_sax": -2,  # Bb soprano sax
    "tenor_sax": -14,  # Bb tenor sax (sounds M9 lower)
    "piccolo": 12,  # sounds octave higher (written octave lower)
    "contrabass": -12,  # sounds octave lower than written
    "piccolo_trumpet": 2,  # D piccolo trumpet (or Bb - varies)
    "glockenspiel": 24,  # sounds 2 octaves higher
    "xylophone": 12,  # sounds octave higher
    "celesta": 12,  # sounds octave higher
}

# Standard instrument ranges (MIDI note numbers)
INSTRUMENT_RANGES = {
    "piccolo": (74, 108),
    "flute": (60, 96),
    "alto_flute": (55, 91),
    "oboe": (58, 91),
    "cor_anglais": (52, 84),
    "english_horn": (52, 84),
    "clarinet": (50, 94),
    "bass_clarinet": (38, 77),
    "bassoon": (34, 75),
    "contrabassoon": (22, 58),
    "soprano_sax": (56, 88),
    "saxophone": (49, 81),
    "tenor_sax": (44, 76),
    "bari_sax": (36, 69),
    "french_horn": (34, 77),
    "trumpet": (55, 82),
    "piccolo_trumpet": (59, 89),
    "cornet": (55, 82),
    "flugelhorn": (55, 80),
    "trombone": (34, 72),
    "bass_trombone": (29, 67),
    "euphonium": (29, 72),
    "tuba": (24, 60),
    "timpani": (40, 55),
    "xylophone": (65, 108),
    "marimba": (45, 96),
    "vibraphone": (53, 89),
    "glockenspiel": (79, 108),
    "celesta": (60, 108),
    "piano": (21, 108),
    "organ": (36, 96),
    "harpsichord": (29, 89),
    "harp": (24, 103),
    "violin": (55, 103),
    "violin_1": (55, 103),
    "violin_2": (55, 103),
    "viola": (48, 91),
    "cello": (36, 84),
    "contrabass": (28, 67),
    "soprano_voice": (60, 84),
    "alto_voice": (53, 77),
    "tenor_voice": (48, 72),
    "bass_voice": (40, 65),
}


def get_family(instrument: str) -> str:
    """Return the orchestral family for an instrument name."""
    for family, members in FAMILIES.items():
        if instrument in members:
            return family
    return "other"


def score_sort_key(part_name: str) -> int:
    """Return a sort key for orchestral score ordering."""
    base = part_name.split("_")[0] if "_" in part_name else part_name
    for i, name in enumerate(SCORE_ORDER):
        if name == part_name or name == base:
            return i
    return len(SCORE_ORDER) + 1


# ---------------------------------------------------------------------------
# Part — a single instrument line within a movement
# ---------------------------------------------------------------------------


@dataclass
class Part:
    """A single instrument part within a movement.

    Wraps a Track with orchestral metadata: instrument family, transposition,
    range, and clef information.
    """

    name: str
    instrument: str = "violin"
    notes: list = field(default_factory=list)
    volume: float = 0.7
    pan: float = 0.0

    def add(self, event: Note | Chord | None) -> "Part":
        """Append a note, chord, or rest."""
        self.notes.append(event)
        return self

    def extend(self, events: Sequence[Note | Chord | None]) -> "Part":
        """Append multiple events."""
        for e in events:
            self.notes.append(e)
        return self

    def to_track(self) -> Track:
        """Convert this Part to a Track for audio rendering."""
        track = Track(
            name=self.name,
            instrument=self.instrument,
            volume=self.volume,
            pan=self.pan,
        )
        track.extend(self.notes)
        return track

    def transpose_for_score(self) -> list:
        """Return notes transposed for a transposing instrument's written pitch.

        Concert pitch C4 on a Bb clarinet is written as D4 (up a major 2nd).
        This returns the written pitches for sheet music export.
        """
        offset = TRANSPOSING_INSTRUMENTS.get(self.instrument, 0)
        if offset == 0:
            return list(self.notes)
        result = []
        for event in self.notes:
            if event is None or (isinstance(event, Note) and event.pitch is None):
                result.append(event)
            elif isinstance(event, Note):
                midi = event.midi
                if midi is not None:
                    written_midi = midi - offset
                    name, octave = midi_to_note_name(written_midi)
                    result.append(Note(name, octave, event.duration, event.velocity))
                else:
                    result.append(event)
            elif isinstance(event, Chord):
                result.append(event)
            else:
                result.append(event)
        return result

    def in_range(self) -> bool:
        """Check if all notes are within the instrument's playable range."""
        rng = INSTRUMENT_RANGES.get(self.instrument)
        if rng is None:
            return True
        lo, hi = rng
        for event in self.notes:
            if isinstance(event, Note) and event.midi is not None:
                if event.midi < lo or event.midi > hi:
                    return False
        return True

    @property
    def total_beats(self) -> float:
        """Total duration in beats."""
        return sum(getattr(e, "duration", 1.0) for e in self.notes if e is not None)


# ---------------------------------------------------------------------------
# Movement — a single movement of a symphony
# ---------------------------------------------------------------------------


@dataclass
class Movement:
    """One movement of a multi-movement work.

    Each movement has its own tempo, time signature, key, and set of
    instrument parts.
    """

    title: str = "Untitled Movement"
    bpm: float = 120.0
    time_sig: tuple[int, int] = (4, 4)
    key: str = "C"
    parts: dict[str, Part] = field(default_factory=dict)
    tempo_markings: list[tuple[float, str, float]] = field(default_factory=list)

    def add_part(
        self,
        name: str,
        instrument: str | None = None,
        volume: float = 0.7,
        pan: float = 0.0,
    ) -> Part:
        """Add an instrument part to this movement.

        Args:
            name:       Part name (e.g. "flute", "violin_1", "timpani").
            instrument: Synth preset name. Defaults to the part name.
            volume:     Part volume.
            pan:        Stereo position.

        Returns:
            The new Part object.
        """
        inst = instrument or name
        part = Part(name=name, instrument=inst, volume=volume, pan=pan)
        self.parts[name] = part
        return part

    def add_tempo_marking(self, at_beat: float, marking: str, bpm: float) -> "Movement":
        """Add a tempo change within the movement.

        Args:
            at_beat:  Beat position for the tempo change.
            marking:  Text marking (e.g. "Allegro", "Adagio", "rit.").
            bpm:      New tempo.

        Returns:
            self for chaining.
        """
        self.tempo_markings.append((at_beat, marking, bpm))
        self.tempo_markings.sort(key=lambda x: x[0])
        return self

    def to_song(self) -> Song:
        """Convert this movement to a Song for audio rendering."""
        song = Song(
            title=self.title,
            bpm=self.bpm,
            time_sig=self.time_sig,
            key_sig=self.key,
        )
        # Add parts in score order
        sorted_parts = sorted(self.parts.values(), key=lambda p: score_sort_key(p.name))
        for part in sorted_parts:
            song.add_track(part.to_track())
        return song

    @property
    def total_beats(self) -> float:
        """Duration of the longest part in beats."""
        if not self.parts:
            return 0.0
        return max(p.total_beats for p in self.parts.values())

    @property
    def duration_sec(self) -> float:
        """Approximate duration in seconds."""
        return self.total_beats * 60.0 / self.bpm


# ---------------------------------------------------------------------------
# Symphony — multi-movement orchestral work
# ---------------------------------------------------------------------------


@dataclass
class Symphony:
    """A multi-movement orchestral work with full score export.

    The top-level container for symphonies, concertos, suites, and other
    multi-movement works. Each movement is a self-contained piece with
    its own tempo, key, and instrumentation. The Symphony provides
    unified rendering and score export.

    Example::

        sym = Symphony("Symphony No. 1 in C", composer="You")
        mvt1 = sym.add_movement("I. Allegro", bpm=132, key="C")
        mvt2 = sym.add_movement("II. Andante", bpm=72, key="F")
        mvt3 = sym.add_movement("III. Menuetto", bpm=120, key="C")
        mvt4 = sym.add_movement("IV. Finale", bpm=144, key="C")

        # Render all movements as one continuous audio file
        song = sym.render()

        # Or render individual movements
        mvt1_song = mvt1.to_song()

        # Export full orchestral score
        sym.export_score("symphony.xml", format="musicxml")
    """

    title: str = "Symphony"
    composer: str = ""
    movements: list[Movement] = field(default_factory=list)
    opus: str = ""

    def add_movement(
        self,
        title: str = "Untitled",
        bpm: float = 120.0,
        time_sig: tuple[int, int] = (4, 4),
        key: str = "C",
    ) -> Movement:
        """Add a new movement to the symphony.

        Returns:
            The new Movement object.
        """
        mvt = Movement(title=title, bpm=bpm, time_sig=time_sig, key=key)
        self.movements.append(mvt)
        return mvt

    def render(self, gap_beats: float = 4.0) -> Song:
        """Render all movements into a single Song with silence gaps between.

        Args:
            gap_beats: Beats of silence between movements.

        Returns:
            A Song containing all movements sequentially.
        """
        if not self.movements:
            return Song(title=self.title, composer=self.composer)

        # Collect all unique part names across all movements
        all_parts: list[str] = []
        for mvt in self.movements:
            for name in mvt.parts:
                if name not in all_parts:
                    all_parts.append(name)
        all_parts.sort(key=score_sort_key)

        # Build one track per part, concatenating across movements
        song = Song(title=self.title, bpm=self.movements[0].bpm, composer=self.composer)
        tracks: dict[str, Track] = {}

        for part_name in all_parts:
            inst = "sine"
            vol = 0.7
            pan = 0.0
            for mvt in self.movements:
                if part_name in mvt.parts:
                    p = mvt.parts[part_name]
                    inst = p.instrument
                    vol = p.volume
                    pan = p.pan
                    break
            tracks[part_name] = Track(
                name=part_name,
                instrument=inst,
                volume=vol,
                pan=pan,
            )

        for mvt_idx, mvt in enumerate(self.movements):
            # Tempo ratio for this movement relative to the song's base BPM
            tempo_ratio = song.bpm / mvt.bpm

            for part_name in all_parts:
                if part_name in mvt.parts:
                    part = mvt.parts[part_name]
                    for event in part.notes:
                        if event is None:
                            tracks[part_name].add(Note.rest(1.0 * tempo_ratio))
                        elif isinstance(event, (Note, Chord)):
                            scaled = copy.copy(event)
                            scaled.duration = event.duration * tempo_ratio
                            tracks[part_name].add(scaled)
                else:
                    # This part does not appear in this movement - add silence
                    mvt_beats = mvt.total_beats * tempo_ratio
                    if mvt_beats > 0:
                        tracks[part_name].add(Note.rest(mvt_beats))

            # Add gap between movements (except after last)
            if mvt_idx < len(self.movements) - 1 and gap_beats > 0:
                for part_name in all_parts:
                    tracks[part_name].add(Note.rest(gap_beats))

        for track in tracks.values():
            song.add_track(track)

        return song

    def export_score(self, path: str, format: str = "musicxml") -> str:
        """Export the full orchestral score to a notation file.

        Args:
            path:   Output file path.
            format: "musicxml" or "lilypond".

        Returns:
            Path of the written file.
        """
        if format == "musicxml":
            return self._export_musicxml(path)
        elif format == "lilypond":
            return self._export_lilypond(path)
        else:
            raise ValueError(f"Unknown format: {format!r}. Use 'musicxml' or 'lilypond'.")

    def export_part(self, part_name: str, path: str, format: str = "musicxml") -> str:
        """Export a single instrument part (for performer use).

        Handles transposing instruments - the exported part shows
        written pitch, not concert pitch.

        Args:
            part_name: Name of the part to extract.
            path:      Output file path.
            format:    "musicxml" or "lilypond".

        Returns:
            Path of the written file.
        """
        from .notation import export_musicxml, export_lilypond

        # Build a Song containing only this part across all movements
        song = Song(title=f"{self.title} - {part_name}", composer=self.composer)

        for mvt in self.movements:
            if part_name in mvt.parts:
                part = mvt.parts[part_name]
                written_notes = part.transpose_for_score()
                track = Track(name=part_name, instrument=part.instrument)
                track.extend(written_notes)
                song.add_track(track)
                song.bpm = mvt.bpm
                song.time_sig = mvt.time_sig
                song.key_sig = mvt.key

        if format == "musicxml":
            return str(export_musicxml(song, path))
        else:
            return str(export_lilypond(song, path))

    def _export_musicxml(self, path: str) -> str:
        """Export full score as MusicXML with orchestral formatting."""
        from pathlib import Path as _Path

        out = _Path(path).with_suffix(".xml")
        out.parent.mkdir(parents=True, exist_ok=True)

        # Collect all parts across all movements
        all_parts: list[str] = []
        for mvt in self.movements:
            for name in mvt.parts:
                if name not in all_parts:
                    all_parts.append(name)
        all_parts.sort(key=score_sort_key)

        divisions = 4
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN"',
            '  "http://www.musicxml.org/dtds/partwise.dtd">',
            '<score-partwise version="4.0">',
            "  <work>",
            f"    <work-title>{self.title}</work-title>",
            "  </work>",
            "  <identification>",
        ]
        if self.composer:
            lines += [
                '    <creator type="composer">' + self.composer + "</creator>",
            ]
        lines += [
            "    <encoding>",
            "      <software>code-music symphony</software>",
            "    </encoding>",
            "  </identification>",
            "  <part-list>",
        ]

        # Group parts by family for score layout
        current_family = None
        group_num = 0
        for part_name in all_parts:
            family = get_family(part_name)
            if family != current_family:
                if current_family is not None:
                    lines.append("    </part-group>")
                group_num += 1
                lines.append(f'    <part-group number="{group_num}" type="start">')
                lines.append(f"      <group-name>{family.title()}</group-name>")
                lines.append("      <group-barline>yes</group-barline>")
                lines.append("    </part-group>")
                current_family = family

            part_id = part_name.replace(" ", "_")
            inst = "sine"
            for mvt in self.movements:
                if part_name in mvt.parts:
                    inst = mvt.parts[part_name].instrument
                    break
            lines += [
                f'    <score-part id="{part_id}">',
                f"      <part-name>{part_name}</part-name>",
                "    </score-part>",
            ]

        if current_family is not None:
            lines.append("    </part-group>")
        lines.append("  </part-list>")

        # Write each part with notes from all movements
        from .notation import _closest_xml, _XML_STEP, _XML_KEY_FIFTHS

        for part_name in all_parts:
            part_id = part_name.replace(" ", "_")
            lines.append(f'  <part id="{part_id}">')

            measure_num = 0
            for mvt_idx, mvt in enumerate(self.movements):
                num, den = mvt.time_sig
                beats_per_bar = num * 4 / den
                fifths = _XML_KEY_FIFTHS.get(mvt.key, 0)

                if part_name in mvt.parts:
                    part = mvt.parts[part_name]
                    notes = part.transpose_for_score()
                else:
                    # Rest for entire movement
                    total = max(1.0, max((p.total_beats for p in mvt.parts.values()), default=4.0))
                    notes = [Note.rest(total)]

                # Split into measures
                measure_notes: list[list] = []
                current_measure: list = []
                bar_beats = 0.0

                for note in notes:
                    if note is None:
                        continue
                    dur = getattr(note, "duration", 1.0)
                    current_measure.append(note)
                    bar_beats += dur
                    if bar_beats >= beats_per_bar - 0.001:
                        measure_notes.append(current_measure)
                        current_measure = []
                        bar_beats = 0.0
                if current_measure:
                    measure_notes.append(current_measure)

                for m_idx, measure in enumerate(measure_notes):
                    measure_num += 1
                    lines.append(f'    <measure number="{measure_num}">')

                    # Attributes on first measure of each movement
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
                            "      </attributes>",
                        ]
                        if m_idx == 0 and mvt_idx == 0:
                            lines += [
                                '      <direction placement="above">',
                                "        <direction-type>",
                                f"          <metronome><beat-unit>quarter</beat-unit>"
                                f"<per-minute>{int(mvt.bpm)}</per-minute></metronome>",
                                "        </direction-type>",
                                "      </direction>",
                            ]

                    for note in measure:
                        if isinstance(note, Note):
                            xml_type, dots = _closest_xml(note.duration)
                            dur_ticks = max(1, round(note.duration * divisions))
                            lines.append("      <note>")
                            if note.pitch is None:
                                lines.append("        <rest/>")
                            else:
                                midi = note.midi or 60
                                name_str = [
                                    "C",
                                    "C#",
                                    "D",
                                    "D#",
                                    "E",
                                    "F",
                                    "F#",
                                    "G",
                                    "G#",
                                    "A",
                                    "A#",
                                    "B",
                                ]
                                note_name = name_str[midi % 12]
                                octave = midi // 12 - 1
                                step, alter = _XML_STEP.get(note_name, ("C", 0))
                                lines += [
                                    "        <pitch>",
                                    f"          <step>{step}</step>",
                                ]
                                if alter:
                                    lines.append(f"          <alter>{alter}</alter>")
                                lines += [
                                    f"          <octave>{octave}</octave>",
                                    "        </pitch>",
                                ]
                            lines += [
                                f"        <duration>{dur_ticks}</duration>",
                                f"        <type>{xml_type}</type>",
                            ]
                            for _ in range(dots):
                                lines.append("        <dot/>")
                            lines.append("      </note>")

                    lines.append("    </measure>")

            lines.append("  </part>")
        lines.append("</score-partwise>")

        out.write_text("\n".join(lines) + "\n")
        return str(out)

    def _export_lilypond(self, path: str) -> str:
        """Export full score as LilyPond with orchestral formatting."""
        from pathlib import Path as _Path

        out = _Path(path).with_suffix(".ly")
        out.parent.mkdir(parents=True, exist_ok=True)

        from .notation import _note_to_lily, _chord_to_lily, _LILY_KEYS

        all_parts: list[str] = []
        for mvt in self.movements:
            for name in mvt.parts:
                if name not in all_parts:
                    all_parts.append(name)
        all_parts.sort(key=score_sort_key)

        lines = [
            '\\version "2.24.0"',
            "\\header {",
            f'  title = "{self.title}"',
        ]
        if self.composer:
            lines.append(f'  composer = "{self.composer}"')
        if self.opus:
            lines.append(f'  opus = "{self.opus}"')
        lines += [
            "}",
            "",
        ]

        # Write each movement as a separate score block
        for mvt_idx, mvt in enumerate(self.movements):
            num, den = mvt.time_sig
            key_root = _LILY_KEYS.get(mvt.key, "c")

            lines += [
                f"% Movement {mvt_idx + 1}: {mvt.title}",
                "\\score {",
                "  <<",
            ]

            for part_name in all_parts:
                if part_name not in mvt.parts:
                    continue
                part = mvt.parts[part_name]
                written = part.transpose_for_score()

                lines.append(f"    % {part_name}")
                lines.append("    \\new Staff {")
                lines.append(f'      \\set Staff.instrumentName = "{part_name}"')
                lines.append("      \\new Voice {")
                lines.append(f"        \\tempo 4 = {int(mvt.bpm)}")
                lines.append(f"        \\time {num}/{den}")
                lines.append(f"        \\key {key_root} \\major")

                tokens = []
                for event in written:
                    if event is None:
                        continue
                    if isinstance(event, Note):
                        tokens.append(_note_to_lily(event))
                    elif isinstance(event, Chord):
                        tokens.append(_chord_to_lily(event))

                # Wrap tokens into lines of ~60 chars
                line_buf = "        "
                for tok in tokens:
                    if len(line_buf) + len(tok) > 72:
                        lines.append(line_buf)
                        line_buf = "        "
                    line_buf += tok + " "
                if line_buf.strip():
                    lines.append(line_buf)

                lines += [
                    "      }",
                    "    }",
                ]

            lines += [
                "  >>",
                f'  \\header {{ piece = "{mvt.title}" }}',
                "  \\layout { }",
                "  \\midi { }",
                "}",
                "",
            ]

        out.write_text("\n".join(lines) + "\n")
        return str(out)

    @property
    def total_duration_sec(self) -> float:
        """Total duration across all movements in seconds."""
        return sum(mvt.duration_sec for mvt in self.movements)

    def __repr__(self) -> str:
        mvts = len(self.movements)
        dur = self.total_duration_sec
        return f"Symphony({self.title!r}, {mvts} movements, {dur:.0f}s)"


# ---------------------------------------------------------------------------
# Orchestration helpers
# ---------------------------------------------------------------------------


def orchestrate(
    melody: list[Note],
    key: str = "C",
    style: str = "romantic",
    seed: int | None = None,
) -> Movement:
    """Auto-orchestrate a melody into a full orchestral movement.

    Takes a single-voice melody and creates a full orchestration with
    harmony, bass, and multiple instrument parts. A starting point for
    orchestral writing, not a replacement for taste.

    Args:
        melody: Input melody as a list of Notes.
        key:    Key signature.
        style:  Orchestration style: "romantic" (Brahms-ish full orchestra),
                "classical" (Mozart-ish lighter texture),
                "chamber" (string quartet + winds).
        seed:   Random seed.

    Returns:
        A Movement with multiple orchestral parts.
    """
    import random as _rng

    rng = _rng.Random(seed)

    mvt = Movement(title="Orchestrated", key=key)

    if style == "classical":
        _orchestrate_classical(mvt, melody, key, rng)
    elif style == "chamber":
        _orchestrate_chamber(mvt, melody, key, rng)
    else:
        _orchestrate_romantic(mvt, melody, key, rng)

    return mvt


def _orchestrate_romantic(mvt: Movement, melody: list[Note], key: str, rng) -> None:
    """Romantic-era orchestration: full strings, doubled winds, brass accents."""
    from .engine import scale, transpose

    # Strings carry the melody
    vln1 = mvt.add_part("violin_1", "violin", volume=0.65, pan=-0.3)
    vln1.extend(melody)

    # Second violins: harmony a third below
    vln2 = mvt.add_part("violin_2", "violin", volume=0.55, pan=-0.15)
    harmony = transpose(melody, -4)
    vln2.extend(harmony)

    # Violas: inner voice
    vla = mvt.add_part("viola", "viola", volume=0.5, pan=0.0)
    inner = transpose(melody, -7)
    vla.extend(inner)

    # Cellos: bass line (octave down from melody)
    vc = mvt.add_part("cello", "cello", volume=0.6, pan=0.15)
    bass = transpose(melody, -24)
    vc.extend(bass)

    # Contrabass: doubles cello
    cb = mvt.add_part("contrabass", "contrabass", volume=0.5, pan=0.2)
    cb.extend(transpose(melody, -36))

    # Flute doubles melody
    fl = mvt.add_part("flute", "flute", volume=0.45, pan=-0.2)
    fl.extend(melody)

    # Oboe: countermelody (simplified)
    ob = mvt.add_part("oboe", "oboe", volume=0.4, pan=0.1)
    counter = [
        Note(n.pitch, n.octave, n.duration * 2, n.velocity * 0.8)
        if n.pitch is not None and rng.random() > 0.4
        else Note.rest(n.duration * 2)
        for n in melody[::2]
    ]
    ob.extend(counter)


def _orchestrate_classical(mvt: Movement, melody: list[Note], key: str, rng) -> None:
    """Classical-era orchestration: lighter texture, clear voices."""
    from .engine import transpose

    vln1 = mvt.add_part("violin_1", "violin", volume=0.6, pan=-0.3)
    vln1.extend(melody)

    vln2 = mvt.add_part("violin_2", "violin", volume=0.5, pan=-0.1)
    vln2.extend(transpose(melody, -3))

    vla = mvt.add_part("viola", "viola", volume=0.45, pan=0.1)
    vla.extend(transpose(melody, -7))

    vc = mvt.add_part("cello", "cello", volume=0.55, pan=0.2)
    vc.extend(transpose(melody, -19))


def _orchestrate_chamber(mvt: Movement, melody: list[Note], key: str, rng) -> None:
    """Chamber orchestration: string quartet with optional wind doubling."""
    from .engine import transpose

    vln1 = mvt.add_part("violin_1", "violin", volume=0.6, pan=-0.25)
    vln1.extend(melody)

    vln2 = mvt.add_part("violin_2", "violin", volume=0.5, pan=-0.05)
    vln2.extend(transpose(melody, -4))

    vla = mvt.add_part("viola", "viola", volume=0.5, pan=0.05)
    vla.extend(transpose(melody, -7))

    vc = mvt.add_part("cello", "cello", volume=0.55, pan=0.25)
    vc.extend(transpose(melody, -19))


# ---------------------------------------------------------------------------
# Big band orchestration (v170)
# ---------------------------------------------------------------------------

BIG_BAND_SECTIONS = {
    "saxes": ["soprano_sax", "soprano_sax", "tenor_sax", "tenor_sax", "bari_sax"],
    "trumpets": ["trumpet", "trumpet", "trumpet", "trumpet"],
    "trombones": ["trombone", "trombone", "trombone", "bass_trombone"],
    "rhythm": ["piano", "guitar_acoustic", "bass", "drums_kick"],
}


def orchestrate_big_band(
    melody: list[Note],
    progression: list | None = None,
    key: str = "C",
    style: str = "swing",
    seed: int | None = None,
) -> Movement:
    """Orchestrate a melody for big band.

    Creates a full big band arrangement with sax section, brass section,
    and rhythm section. The melody goes to lead trumpet or lead alto
    depending on style. Backgrounds are harmonized in section voicings.

    Styles:
        swing:    Count Basie - sparse hits, walking bass, ride cymbal
        bebop:    Dizzy/Bird big band - unison lines, complex harmony
        latin:    Machito/Tito Puente - montuno piano, tumbao bass, clave
        funk:     Tower of Power/JBs - tight horns, one-chord vamps

    Args:
        melody:      Lead melody.
        progression: Chord progression (list of (root, shape) tuples).
                     Auto-generated if None.
        key:         Key signature.
        style:       "swing", "bebop", "latin", "funk".
        seed:        Random seed.

    Returns:
        A Movement with full big band parts.
    """
    import random as _rng
    from .engine import transpose, Note as _Note, Chord as _Chord

    rng = _rng.Random(seed)
    mvt = Movement(title=f"Big Band ({style.title()})", key=key)

    # Trumpets: lead carries melody, section harmonizes below
    tp1 = mvt.add_part("trumpet_1", "trumpet", volume=0.65, pan=-0.15)
    tp2 = mvt.add_part("trumpet_2", "trumpet", volume=0.55, pan=-0.1)
    tp3 = mvt.add_part("trumpet_3", "trumpet", volume=0.55, pan=-0.05)
    tp4 = mvt.add_part("trumpet_4", "trumpet", volume=0.5, pan=0.0)

    tp1.extend(melody)
    tp2.extend(transpose(melody, -3))  # minor 3rd below
    tp3.extend(transpose(melody, -7))  # perfect 5th below
    tp4.extend(transpose(melody, -12))  # octave below

    # Trombones: pad harmony or rhythmic hits
    tb1 = mvt.add_part("trombone_1", "trombone", volume=0.55, pan=0.05)
    tb2 = mvt.add_part("trombone_2", "trombone", volume=0.5, pan=0.1)
    tb3 = mvt.add_part("trombone_3", "trombone", volume=0.5, pan=0.15)
    tb4 = mvt.add_part("bass_trombone", "bass_trombone", volume=0.5, pan=0.2)

    # Trombones play sustained pads or rhythmic stabs
    tbn_notes = []
    for n in melody:
        if n.pitch is None:
            tbn_notes.append(n)
        else:
            # Hold longer, fewer notes
            tbn_notes.append(
                _Note(n.pitch, n.octave - 1, n.duration * 2, velocity=n.velocity * 0.7)
            )
    # Trim to match melody length
    total_melody_beats = sum(getattr(n, "duration", 1.0) for n in melody)
    tbn_trimmed = []
    tbn_beats = 0.0
    for n in tbn_notes:
        if tbn_beats >= total_melody_beats:
            break
        tbn_trimmed.append(n)
        tbn_beats += getattr(n, "duration", 1.0)

    tb1.extend(tbn_trimmed)
    tb2.extend(transpose(tbn_trimmed, -4))
    tb3.extend(transpose(tbn_trimmed, -7))
    tb4.extend(transpose(tbn_trimmed, -12))

    # Saxes: unison melody or counter-melody
    as1 = mvt.add_part("alto_sax_1", "saxophone", volume=0.55, pan=-0.2)
    as2 = mvt.add_part("alto_sax_2", "saxophone", volume=0.5, pan=-0.15)
    ts1 = mvt.add_part("tenor_sax_1", "tenor_sax", volume=0.5, pan=0.0)
    ts2 = mvt.add_part("tenor_sax_2", "tenor_sax", volume=0.5, pan=0.05)
    bs = mvt.add_part("bari_sax", "bari_sax", volume=0.5, pan=0.1)

    if style == "bebop":
        # Unison melody (Bird with strings vibes)
        as1.extend(melody)
        as2.extend(melody)
        ts1.extend(transpose(melody, -12))
        ts2.extend(transpose(melody, -12))
        bs.extend(transpose(melody, -24))
    else:
        # Harmonized sax soli
        as1.extend(melody)
        as2.extend(transpose(melody, -4))
        ts1.extend(transpose(melody, -7))
        ts2.extend(transpose(melody, -12))
        bs.extend(transpose(melody, -19))

    # Rhythm section
    piano = mvt.add_part("piano", "piano", volume=0.5, pan=0.25)
    bass = mvt.add_part("bass", "bass", volume=0.55, pan=0.2)
    drums = mvt.add_part("drums", "drums_ride", volume=0.5, pan=0.0)

    # Piano comps with shell voicings on 2 and 4
    if progression:
        for root, shape in progression:
            piano.add(_Note.rest(1.0))
            piano.add(
                _Chord(root, "dom7" if "7" in shape else shape, 3, duration=1.0, velocity=0.5)
            )
            piano.add(_Note.rest(1.0))
            piano.add(
                _Chord(root, "dom7" if "7" in shape else shape, 3, duration=1.0, velocity=0.45)
            )
    else:
        # Simple comp on 2 and 4
        for n in melody:
            if n.pitch is not None:
                piano.add(_Note.rest(n.duration * 0.5))
                piano.add(_Note(n.pitch, 3, n.duration * 0.5, velocity=0.45))
            else:
                piano.add(n)

    # Bass: walking for swing/bebop, tumbao for Latin, root-fifth for funk
    if style == "latin":
        for n in melody:
            if n.pitch is not None:
                bass.add(_Note(n.pitch, 2, n.duration, velocity=0.7))
            else:
                bass.add(n)
    elif style == "funk":
        for n in melody:
            if n.pitch is not None:
                bass.add(_Note(n.pitch, 2, n.duration * 0.5, velocity=0.8))
                bass.add(_Note.rest(n.duration * 0.5))
            else:
                bass.add(n)
    else:
        # Walking bass
        for n in melody:
            if n.pitch is not None:
                bass.add(_Note(n.pitch, 2, n.duration, velocity=0.7))
            else:
                bass.add(n)

    # Drums: ride cymbal pattern
    for n in melody:
        dur = getattr(n, "duration", 1.0)
        drums.add(_Note("C", 6, dur, velocity=0.5))

    return mvt
