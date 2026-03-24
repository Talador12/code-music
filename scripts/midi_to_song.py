"""MIDI reverse compiler: read a .mid file → generate a code-music song script.

Reads Standard MIDI File (SMF) and outputs a Python song script that
reproduces the same notes, rhythms, and structure. The output is clean,
readable code that you can edit and extend.

Usage:
    python scripts/midi_to_song.py my_song.mid
    python scripts/midi_to_song.py my_song.mid --out songs/from_midi.py
    python scripts/midi_to_song.py my_song.mid --bpm 128 --title "My Import"
    make midi-to-song MIDI=my_song.mid

Output format:
    from code_music import Song, Track, Note, Chord, QUARTER, EIGHTH, ...
    song = Song(title="...", bpm=120)
    tr0 = song.add_track(Track(name="track_0", instrument="piano"))
    tr0.add(Note("C", 4, 1.0))
    ...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# General MIDI program → instrument preset
GM_TO_PRESET: dict[int, str] = {
    0: "piano",
    1: "piano",
    2: "piano",
    3: "piano",
    4: "rhodes",
    5: "rhodes",
    6: "harpsichord",
    7: "piano",
    8: "celesta",
    11: "vibraphone",
    12: "marimba",
    13: "xylophone",
    16: "organ",
    17: "organ",
    18: "organ",
    19: "organ",
    24: "guitar_acoustic",
    25: "guitar_acoustic",
    26: "guitar_electric",
    27: "guitar_electric",
    32: "contrabass",
    33: "bass",
    34: "bass",
    35: "bass",
    40: "violin",
    41: "violin",
    42: "cello",
    43: "contrabass",
    44: "strings",
    45: "pizzicato",
    46: "harp",
    47: "timpani",
    48: "strings",
    49: "strings",
    50: "strings",
    51: "strings",
    52: "choir_ooh",
    53: "choir_aah",
    54: "vox_pad",
    56: "trumpet",
    57: "trombone",
    58: "tuba",
    60: "french_horn",
    61: "brass_section",
    65: "saxophone",
    66: "saxophone",
    67: "saxophone",
    68: "oboe",
    70: "bassoon",
    71: "clarinet",
    72: "piccolo",
    73: "flute",
    74: "flute",
    75: "flute",
    80: "lead_edm",
    81: "sawtooth",
    82: "square",
    88: "pad",
    89: "pad",
    90: "pad",
}

# GM drum note → instrument name
GM_DRUMS: dict[int, str] = {
    35: "drums_kick",
    36: "drums_kick",
    38: "drums_snare",
    40: "drums_snare",
    42: "drums_hat",
    44: "drums_hat",
    46: "drums_hat",
    49: "drums_crash",
    51: "drums_ride",
    57: "drums_crash",
    47: "drums_tom",
    48: "drums_tom",
    45: "drums_tom",
    39: "drums_clap",
}


# ── MIDI parsing ──────────────────────────────────────────────────────────


def _var_len_read(data: bytes, pos: int) -> tuple[int, int]:
    """Read a variable-length quantity. Returns (value, new_pos)."""
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, pos


def parse_midi(path: Path) -> dict:
    """Parse a MIDI file into a structured dict."""
    data = path.read_bytes()
    pos = 0

    def read(n):
        nonlocal pos
        chunk = data[pos : pos + n]
        pos += n
        return chunk

    def read_uint(n):
        return int.from_bytes(read(n), "big")

    # Header
    assert read(4) == b"MThd", "Not a MIDI file"
    fmt = read_uint(2)
    n_tracks = read_uint(2)
    ticks_ppq = read_uint(2)  # ticks per quarter note

    tracks = []
    for _ in range(n_tracks):
        tag = read(4)
        if tag != b"MTrk":
            chunk_len = read_uint(4)
            read(chunk_len)
            continue
        chunk_len = read_uint(4)
        chunk_end = pos + chunk_len
        events = []
        abs_tick = 0
        running_status = 0
        while pos < chunk_end:
            delta, pos = _var_len_read(data, pos)
            abs_tick += delta
            byte = data[pos]
            if byte == 0xFF:  # Meta
                pos += 1
                meta_type = data[pos]
                pos += 1
                length, pos = _var_len_read(data, pos)
                meta_data = data[pos : pos + length]
                pos += length
                if meta_type == 0x51 and length == 3:
                    tempo_us = int.from_bytes(meta_data, "big")
                    events.append(("tempo", abs_tick, tempo_us))
                elif meta_type == 0x03:
                    events.append(("name", abs_tick, meta_data.decode("utf-8", errors="replace")))
            elif byte == 0xF0 or byte == 0xF7:  # Sysex
                pos += 1
                length, pos = _var_len_read(data, pos)
                pos += length
            else:
                if byte & 0x80:
                    running_status = byte
                    pos += 1
                status = running_status
                cmd = status & 0xF0
                ch = status & 0x0F
                if cmd in (0x80, 0x90, 0xA0):
                    note = data[pos]
                    vel = data[pos + 1]
                    pos += 2
                    if cmd == 0x90 and vel > 0:
                        events.append(("note_on", abs_tick, ch, note, vel))
                    else:
                        events.append(("note_off", abs_tick, ch, note))
                elif cmd in (0xB0, 0xE0):
                    pos += 2
                elif cmd == 0xC0:
                    program = data[pos]
                    pos += 1
                    events.append(("program", abs_tick, ch, program))
                elif cmd == 0xD0:
                    pos += 1
                else:
                    pos += 1
        tracks.append(events)

    return {"format": fmt, "ticks_ppq": ticks_ppq, "tracks": tracks}


def midi_to_script(
    midi: dict, title: str = "Imported Song", bpm_override: float | None = None
) -> str:
    """Convert parsed MIDI to a code-music Python script string."""
    ticks_ppq = midi["ticks_ppq"]

    # Find first tempo (default 120 BPM)
    tempo_us = 500_000  # 120 BPM
    for track in midi["tracks"]:
        for ev in track:
            if ev[0] == "tempo":
                tempo_us = ev[2]
                break
        else:
            continue
        break
    bpm = bpm_override or round(60_000_000 / tempo_us, 1)

    def ticks_to_beats(ticks: int) -> float:
        return round(ticks / ticks_ppq, 4)

    def midi_pitch_to_name(pitch: int) -> tuple[str, int]:
        return NOTE_NAMES[pitch % 12], pitch // 12 - 1

    def beats_to_const(beats: float) -> str:
        """Convert beat duration to nearest named constant."""
        table = [
            (4.0, "WHOLE"),
            (3.0, "DOTTED_HALF"),
            (2.0, "HALF"),
            (1.5, "DOTTED_QUARTER"),
            (1.0, "QUARTER"),
            (0.75, "DOTTED_EIGHTH"),
            (0.5, "EIGHTH"),
            (0.375, "DOTTED_SIXTEENTH"),
            (0.25, "SIXTEENTH"),
            (0.125, "THIRTY_SECOND"),
        ]
        for val, name in table:
            if abs(beats - val) < 0.05:
                return name
        return str(beats)

    lines = [
        '"""Auto-generated from MIDI. Edit freely."""',
        "from code_music import (",
        "    Song, Track, Note, WHOLE, HALF, QUARTER, EIGHTH, SIXTEENTH,",
        "    DOTTED_HALF, DOTTED_QUARTER, DOTTED_EIGHTH, THIRTY_SECOND,",
        ")",
        "",
        f'song = Song(title="{title}", bpm={bpm})',
        "",
    ]

    track_vars = []
    for t_idx, track in enumerate(midi["tracks"]):
        # Get track name
        track_name = f"track_{t_idx}"
        for ev in track:
            if ev[0] == "name" and ev[2].strip():
                track_name = ev[2].strip().replace(" ", "_").lower()[:20]
                break

        # Get instrument
        instrument = "piano"
        is_drum = False
        for ev in track:
            if ev[0] == "program":
                instrument = GM_TO_PRESET.get(ev[3], "piano")
                break
        # Check if this is channel 10 (drums)
        for ev in track:
            if ev[0] in ("note_on",) and ev[2] == 9:
                is_drum = True
                instrument = "drums_kick"
                break

        # Build note timeline: note_on events with durations
        active: dict[int, tuple[int, int]] = {}  # pitch → (on_tick, velocity)
        note_events: list[tuple[float, str, int, float, float]] = []

        for ev in track:
            if ev[0] == "note_on":
                _, tick, ch, pitch, vel = ev
                active[pitch] = (tick, vel)
            elif ev[0] == "note_off":
                _, tick, ch, pitch = ev
                if pitch in active:
                    on_tick, vel = active.pop(pitch)
                    dur = ticks_to_beats(tick - on_tick)
                    start = ticks_to_beats(on_tick)
                    velocity = round(vel / 127, 2)
                    note_events.append((start, pitch, ch, dur, velocity))

        # Close any hanging notes at end
        for pitch, (on_tick, vel) in active.items():
            last_tick = max(
                (ev[1] for ev in track if ev[0] in ("note_on", "note_off")), default=on_tick
            )
            dur = ticks_to_beats(last_tick - on_tick) or 1.0
            start = ticks_to_beats(on_tick)
            note_events.append((start, pitch, 9 if is_drum else 0, dur, round(vel / 127, 2)))

        if not note_events:
            continue

        note_events.sort(key=lambda x: x[0])

        var = f"tr{t_idx}"
        track_vars.append(var)
        lines.append(
            f'{var} = song.add_track('
            f'Track(name="{track_name}", instrument="{instrument}", volume=0.8))'
        )

        # Convert to sequential notes with rests
        cursor = 0.0
        for start, pitch, ch, dur, vel in note_events:
            if start > cursor + 0.01:
                rest_dur = round(start - cursor, 4)
                lines.append(f"{var}.add(Note.rest({beats_to_const(rest_dur)}))")
            if is_drum:
                note_pitch = "C"
                note_oct = 2
            else:
                note_pitch, note_oct = midi_pitch_to_name(pitch)
            dur_str = beats_to_const(dur)
            if vel != 0.8:
                lines.append(
                    f'{var}.add(Note("{note_pitch}", {note_oct}, {dur_str}, velocity={vel}))'
                )
            else:
                lines.append(f'{var}.add(Note("{note_pitch}", {note_oct}, {dur_str}))')
            cursor = start + dur

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a MIDI file to a code-music song script")
    parser.add_argument("midi", type=Path, help="Input .mid file")
    parser.add_argument("--out", type=Path, default=None, help="Output .py file")
    parser.add_argument("--title", default=None, help="Song title")
    parser.add_argument("--bpm", type=float, default=None, help="Override BPM")
    args = parser.parse_args()

    if not args.midi.exists():
        print(f"Error: {args.midi} not found", file=sys.stderr)
        sys.exit(1)

    title = args.title or args.midi.stem.replace("_", " ").title()
    midi = parse_midi(args.midi)
    script = midi_to_script(midi, title=title, bpm_override=args.bpm)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(script)
        print(f"Written to {args.out}")
    else:
        print(script)


if __name__ == "__main__":
    main()
