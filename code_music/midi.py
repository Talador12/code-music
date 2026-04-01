"""MIDI import/export — read and write standard .mid files (no external deps).

Implements a minimal subset of the MIDI spec (SMF type 0 and 1) using only
the Python standard library. No mido, no music21 required.

Usage::

    from code_music.midi import export_midi, import_midi
    export_midi(song, "my_song.mid")

    song = import_midi("existing.mid")
    song.bpm = 140  # re-tempo
"""

from __future__ import annotations

import struct
from pathlib import Path

from .engine import Chord, Note, Song, Track, midi_to_note_name

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

    # ── Tempo track (track 0) — includes tempo + time signature events ────
    import math

    tempo_data = bytearray()
    # Tempo at tick 0
    tempo_data += b"\x00\xff\x51\x03" + struct.pack(">I", tempo_us)[1:]
    # Initial time signature at tick 0
    num, den = song.time_sig
    den_pow = max(0, int(math.log2(den))) if den > 0 else 2
    tempo_data += b"\x00\xff\x58\x04" + bytes([num, den_pow, 24, 8])

    # Time signature changes from time_sig_map
    prev_tick = 0
    for at_beat, ts_num, ts_den in getattr(song, "time_sig_map", []):
        tick = int(at_beat * ticks_per_beat)
        delta = tick - prev_tick
        prev_tick = tick
        ts_den_pow = max(0, int(math.log2(ts_den))) if ts_den > 0 else 2
        tempo_data += _var_len(delta) + b"\xff\x58\x04" + bytes([ts_num, ts_den_pow, 24, 8])

    # End of track
    tempo_data += b"\x00\xff\x2f\x00"
    tempo_track = b"MTrk" + struct.pack(">I", len(tempo_data)) + bytes(tempo_data)

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


# ---------------------------------------------------------------------------
# MIDI Import — parse .mid → Song
# ---------------------------------------------------------------------------


def _read_var_len(data: bytes, offset: int) -> tuple[int, int]:
    """Read a MIDI variable-length quantity. Returns (value, new_offset)."""
    value = 0
    while True:
        b = data[offset]
        value = (value << 7) | (b & 0x7F)
        offset += 1
        if not (b & 0x80):
            break
    return value, offset


def _parse_track_chunk(data: bytes, offset: int) -> tuple[list[tuple[int, bytes]], int]:
    """Parse a single MTrk chunk into (events, new_offset).

    Each event is (absolute_tick, raw_event_bytes).
    """
    if data[offset : offset + 4] != b"MTrk":
        raise ValueError(f"Expected MTrk at offset {offset}")
    length = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
    chunk_end = offset + 8 + length
    pos = offset + 8

    events: list[tuple[int, bytes]] = []
    abs_tick = 0
    running_status = 0

    while pos < chunk_end:
        delta, pos = _read_var_len(data, pos)
        abs_tick += delta

        byte = data[pos]

        # Meta event
        if byte == 0xFF:
            meta_type = data[pos + 1]
            meta_len, pos = _read_var_len(data, pos + 2)
            meta_data = data[pos : pos + meta_len]
            pos += meta_len
            # Store tempo meta events for BPM extraction
            events.append((abs_tick, bytes([0xFF, meta_type]) + meta_data))
            continue

        # SysEx
        if byte in (0xF0, 0xF7):
            sysex_len, pos = _read_var_len(data, pos + 1)
            pos += sysex_len
            continue

        # Channel event
        if byte & 0x80:
            running_status = byte
            pos += 1
        else:
            byte = running_status

        msg_type = byte & 0xF0
        if msg_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
            # Two data bytes
            d1 = data[pos]
            d2 = data[pos + 1]
            pos += 2
            events.append((abs_tick, bytes([byte, d1, d2])))
        elif msg_type in (0xC0, 0xD0):
            # One data byte
            d1 = data[pos]
            pos += 1
            events.append((abs_tick, bytes([byte, d1])))

    return events, chunk_end


def _reverse_gm_program(program: int) -> str:
    """Map a GM program number back to a code-music instrument name."""
    # Build reverse lookup (prefer shorter/more-common names)
    _REVERSE: dict[int, str] = {}
    preferred = [
        "piano",
        "organ",
        "strings",
        "violin",
        "cello",
        "contrabass",
        "trumpet",
        "trombone",
        "french_horn",
        "tuba",
        "flute",
        "oboe",
        "clarinet",
        "bassoon",
        "saxophone",
        "guitar_acoustic",
        "harp",
        "bass",
        "pad",
        "sawtooth",
        "square",
        "sine",
    ]
    for name in reversed(preferred):
        if name in GM_PROGRAMS:
            _REVERSE[GM_PROGRAMS[name]] = name
    for name, prog in GM_PROGRAMS.items():
        if prog not in _REVERSE:
            _REVERSE[prog] = name
    return _REVERSE.get(program, "piano")


def import_midi(
    path: str | Path,
    title: str | None = None,
    instrument: str | None = None,
) -> Song:
    """Parse a Standard MIDI File into a Song.

    Args:
        path:       Path to a .mid or .midi file.
        title:      Optional song title (defaults to filename stem).
        instrument: Force all tracks to use this instrument (otherwise
                    inferred from GM program change events).

    Returns:
        A Song with one Track per MIDI channel that contains note data.

    Notes:
        - Supports SMF type 0 (single track) and type 1 (multi-track).
        - Tempo is extracted from the first tempo meta event.
        - Drum channel (10 / index 9) maps to ``drums_kick`` by default.
        - Velocity is preserved as Note.velocity (0.0–1.0).
    """
    data = Path(path).read_bytes()

    # ── Parse header ──────────────────────────────────────────────────────
    if data[:4] != b"MThd":
        raise ValueError("Not a valid MIDI file (missing MThd header)")
    _hdr_len, fmt, n_tracks, tpb = struct.unpack(">IHHH", data[4:14])
    if fmt > 1:
        raise ValueError(f"SMF type {fmt} is not supported (only type 0 and 1)")

    # ── Parse all track chunks ────────────────────────────────────────────
    all_events: list[list[tuple[int, bytes]]] = []
    pos = 14
    for _ in range(n_tracks):
        events, pos = _parse_track_chunk(data, pos)
        all_events.append(events)

    # ── Extract tempo ─────────────────────────────────────────────────────
    tempo_us = 500_000  # default 120 BPM
    for track_events in all_events:
        for _tick, ev in track_events:
            if len(ev) >= 5 and ev[0] == 0xFF and ev[1] == 0x51:
                tempo_us = int.from_bytes(ev[2:5], "big")
                break

    bpm = 60_000_000 / tempo_us

    # ── Flatten all events into per-channel buckets ───────────────────────
    # (absolute_tick, event_bytes)
    channel_events: dict[int, list[tuple[int, bytes]]] = {}
    channel_program: dict[int, int] = {}

    for track_events in all_events:
        for tick, ev in track_events:
            if not ev or ev[0] == 0xFF:
                continue
            ch = ev[0] & 0x0F
            msg_type = ev[0] & 0xF0

            # Program change
            if msg_type == 0xC0 and len(ev) >= 2:
                channel_program[ch] = ev[1]
                continue

            # Note on / note off
            if msg_type in (0x80, 0x90) and len(ev) >= 3:
                channel_events.setdefault(ch, []).append((tick, ev))

    # ── Convert channel events to Tracks ──────────────────────────────────
    song_title = title or Path(path).stem.replace("_", " ").title()
    song = Song(title=song_title, bpm=round(bpm, 1))

    for ch in sorted(channel_events.keys()):
        events = sorted(channel_events[ch], key=lambda e: e[0])
        is_drum = ch == _DRUM_CHANNEL

        if instrument:
            inst = instrument
        elif is_drum:
            inst = "drums_kick"
        else:
            inst = _reverse_gm_program(channel_program.get(ch, 0))

        track = Track(name=f"ch{ch + 1}", instrument=inst)

        # Build note-on/note-off pairs
        active: dict[int, tuple[int, float]] = {}  # pitch → (start_tick, velocity)
        notes: list[tuple[int, int, float, float]] = []  # (start, end, pitch_midi, vel)

        for tick, ev in events:
            msg_type = ev[0] & 0xF0
            pitch = ev[1]
            vel = ev[2] / 127.0 if len(ev) > 2 else 0.8

            if msg_type == 0x90 and ev[2] > 0:
                active[pitch] = (tick, vel)
            elif msg_type == 0x80 or (msg_type == 0x90 and ev[2] == 0):
                if pitch in active:
                    start_tick, start_vel = active.pop(pitch)
                    notes.append((start_tick, tick, pitch, start_vel))

        # Close any still-active notes at the last event tick
        last_tick = events[-1][0] if events else 0
        for pitch, (start_tick, vel) in active.items():
            notes.append((start_tick, last_tick + tpb, pitch, vel))

        notes.sort(key=lambda n: n[0])

        # Convert to code-music Notes with rest-fill
        cursor_ticks = 0
        for start, end, midi_pitch, vel in notes:
            if start > cursor_ticks:
                gap_beats = (start - cursor_ticks) / tpb
                if gap_beats > 0.001:
                    track.add(Note.rest(gap_beats))

            dur_beats = max(0.0625, (end - start) / tpb)
            if is_drum:
                name, octave = "C", 2
            else:
                name, octave = midi_to_note_name(midi_pitch)
            track.add(Note(name, octave, dur_beats, velocity=vel))
            cursor_ticks = end

        if track.beats:
            song.add_track(track)

    return song
