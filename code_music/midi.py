"""MIDI export — write a Song to a standard .mid file (no external deps).

Implements a minimal subset of the MIDI spec (SMF type 1) using only
the Python standard library. No mido, no music21 required.

Usage::

    from code_music.midi import export_midi
    export_midi(song, "my_song.mid")
"""

from __future__ import annotations

import struct
from pathlib import Path

from .engine import Chord, Note, Song, Track

# ---------------------------------------------------------------------------
# MIDI constants
# ---------------------------------------------------------------------------

MIDI_NOTE_ON = 0x90
MIDI_NOTE_OFF = 0x80
MIDI_TEMPO = 0xFF5103  # meta event
MIDI_EOT = 0xFF2F00  # end of track

# General MIDI program numbers (0-indexed)
GM_PROGRAMS: dict[str, int] = {
    # Keyboards
    "piano": 0,
    "harpsichord": 6,
    "celesta": 8,
    "organ": 16,
    "rhodes": 4,
    "wurlitzer": 4,
    # Strings
    "strings": 48,
    "violin": 40,
    "cello": 42,
    "contrabass": 43,
    "pizzicato": 45,
    # Brass
    "trumpet": 56,
    "trombone": 57,
    "french_horn": 60,
    "tuba": 58,
    "brass_section": 61,
    # Woodwinds
    "flute": 73,
    "oboe": 68,
    "clarinet": 71,
    "bassoon": 70,
    "saxophone": 65,
    "piccolo": 72,
    # Plucked
    "guitar_acoustic": 25,
    "guitar_electric": 27,
    "harp": 46,
    "pluck": 46,
    # Mallet percussion
    "marimba": 12,
    "vibraphone": 11,
    "xylophone": 13,
    # Orchestral perc (channel 10, program ignored)
    "timpani": 47,
    "drums_kick": 0,
    "drums_snare": 0,
    "drums_hat": 0,
    "drums_clap": 0,
    "drums_tom": 0,
    "drums_ride": 0,
    "drums_crash": 0,
    "drums_808": 0,
    # Choir / Vocal
    "choir_aah": 52,
    "choir_ooh": 53,
    "vox_pad": 54,
    # Synths
    "bass": 38,
    "pad": 88,
    "supersaw": 81,
    "reese_bass": 38,
    "acid": 81,
    "hoover": 81,
    "stab": 80,
    "lead_edm": 80,
    "sawtooth": 81,
    "square": 80,
    "sine": 88,
    "triangle": 88,
}

# GM drum note numbers (channel 10)
GM_DRUMS: dict[str, int] = {
    "drums_kick": 36,  # Bass Drum 1
    "drums_snare": 38,  # Acoustic Snare
    "drums_hat": 42,  # Closed Hi-Hat
    "drums_clap": 39,  # Hand Clap
    "drums_tom": 47,  # Low-Mid Tom
    "drums_ride": 51,  # Ride Cymbal 1
    "drums_crash": 49,  # Crash Cymbal 1
    "drums_808": 36,  # Bass Drum 1 (808 sub)
    "snare_orch": 38,
    "cymbals": 57,  # Crash Cymbal 2
    "timpani": 41,  # Low Floor Tom (approximation)
    "gong": 54,  # Tambourine (closest)
}

_DRUM_CHANNEL = 9  # 0-indexed; channel 10 in MIDI is 0-indexed 9


# ---------------------------------------------------------------------------
# Variable-length encoding
# ---------------------------------------------------------------------------


def _var_len(value: int) -> bytes:
    """Encode an integer as MIDI variable-length quantity."""
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


# ---------------------------------------------------------------------------
# Track chunk builder
# ---------------------------------------------------------------------------


def _build_track(
    track: Track,
    ticks_per_beat: int,
    beat_duration_sec: float,
    channel: int,
    program: int,
) -> bytes:
    """Convert a Track to raw MIDI track chunk bytes."""
    events: list[tuple[int, bytes]] = []  # (tick_abs, event_bytes)

    is_drum = track.instrument in GM_DRUMS or channel == _DRUM_CHANNEL
    ch = _DRUM_CHANNEL if is_drum else channel

    # Program change at tick 0 (skip for drums — GM drums are fixed)
    if not is_drum and program is not None:
        events.append((0, bytes([0xC0 | ch, program & 0x7F])))

    cursor_ticks = 0
    for beat in track.beats:
        dur_ticks = max(1, int(beat.duration * ticks_per_beat))
        event = beat.event

        if event is None:
            cursor_ticks += dur_ticks
            continue

        # Collect notes from beat
        if isinstance(event, Note):
            notes = [event]
        elif isinstance(event, Chord):
            notes = event.notes
        else:
            cursor_ticks += dur_ticks
            continue

        for note in notes:
            if note.pitch is None:
                continue
            if note.midi is None:
                continue
            midi_pitch = note.midi if not is_drum else GM_DRUMS.get(track.instrument, 36)
            midi_pitch = max(0, min(127, midi_pitch))
            velocity = max(1, min(127, int(note.velocity * 127)))

            note_on = bytes([MIDI_NOTE_ON | ch, midi_pitch, velocity])
            note_off = bytes([MIDI_NOTE_OFF | ch, midi_pitch, 0])
            note_dur = max(1, int(note.duration * ticks_per_beat))

            events.append((cursor_ticks, note_on))
            events.append((cursor_ticks + note_dur, note_off))

        cursor_ticks += dur_ticks

    # Sort by tick, then note_offs before note_ons at same tick
    events.sort(key=lambda e: (e[0], 1 if e[1][0] & 0xF0 == 0x90 else 0))

    # Convert absolute ticks → delta ticks and serialize
    track_data = bytearray()
    prev_tick = 0
    for tick, ev in events:
        delta = tick - prev_tick
        prev_tick = tick
        track_data += _var_len(delta)
        track_data += ev

    # End of track
    track_data += b"\x00\xff\x2f\x00"

    # Wrap in chunk header: "MTrk" + length
    return b"MTrk" + struct.pack(">I", len(track_data)) + bytes(track_data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def export_midi(song: Song, path: str | Path, ticks_per_beat: int = 480) -> Path:
    """Write a Song to a Standard MIDI File (SMF type 1).

    Args:
        song:           Song to export.
        path:           Output path (will get .mid extension).
        ticks_per_beat: MIDI resolution (480 is standard, 960 is high-res).

    Returns:
        Resolved Path of the written file.

    Notes:
        - Instruments are mapped to General MIDI programs.
        - Drum tracks (instruments starting with 'drums_') go to channel 10.
        - Up to 15 non-drum tracks supported (MIDI channels 1-9, 11-16).
        - Voice tracks are not included in MIDI export.
    """
    out = Path(path).with_suffix(".mid")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Tempo in microseconds per beat
    bpm = song.bpm
    tempo_us = int(60_000_000 / bpm)

    # ── Header chunk ────────────────────────────────────────────────────────
    n_tracks = len(song.tracks) + 1  # +1 for tempo track
    header = b"MThd" + struct.pack(">IHHH", 6, 1, n_tracks, ticks_per_beat)

    # ── Tempo track (track 0) ──────────────────────────────────────────────
    tempo_event = (
        b"\x00"  # delta time 0
        b"\xff\x51\x03"  # Set Tempo meta event
        + struct.pack(">I", tempo_us)[1:]  # 3 bytes big-endian
        + b"\x00\xff\x2f\x00"  # End of Track
    )
    tempo_track = b"MTrk" + struct.pack(">I", len(tempo_event)) + tempo_event

    # ── Instrument tracks ──────────────────────────────────────────────────
    drum_instruments = set(GM_DRUMS.keys()) | {"snare_orch", "cymbals", "gong", "timpani"}
    non_drum_channel = 0
    track_chunks = []

    for track in song.tracks:
        is_drum = track.instrument in drum_instruments
        if is_drum:
            channel = _DRUM_CHANNEL
        else:
            # Allocate next available non-drum channel (skip channel 9)
            channel = non_drum_channel if non_drum_channel < _DRUM_CHANNEL else non_drum_channel + 1
            non_drum_channel += 1
            if non_drum_channel >= _DRUM_CHANNEL:
                non_drum_channel += 1  # skip drum channel
            channel = min(channel, 15)

        program = GM_PROGRAMS.get(track.instrument, 0)
        beat_sec = 60.0 / song.bpm
        chunk = _build_track(track, ticks_per_beat, beat_sec, channel, program)
        track_chunks.append(chunk)

    # ── Write file ─────────────────────────────────────────────────────────
    out.write_bytes(header + tempo_track + b"".join(track_chunks))
    return out
