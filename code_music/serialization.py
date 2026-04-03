"""Song JSON serialization — full round-trip save/load for songs.

Serialize any Song to a JSON-compatible dict (or JSON string/file), including
tracks, notes, chords, effects references, custom instruments, and metadata.
Enables collaboration, web export, versioning, and caching.

Example::

    from code_music.serialization import song_to_json, song_from_json

    data = song_to_json(song)                  # → dict
    json_str = song_to_json(song, as_string=True)  # → JSON string
    song_to_json(song, path="my_song.json")    # → write to file

    restored = song_from_json(data)            # from dict
    restored = song_from_json("my_song.json")  # from file path
"""

from __future__ import annotations

import json
from pathlib import Path


def _note_to_dict(note) -> dict:
    return {
        "pitch": note.pitch,
        "octave": note.octave,
        "duration": note.duration,
        "velocity": note.velocity,
    }


def _chord_to_dict(chord) -> dict:
    return {
        "type": "chord",
        "root": chord.root,
        "shape": chord.shape if isinstance(chord.shape, str) else list(chord.shape),
        "octave": chord.octave,
        "duration": chord.duration,
        "velocity": chord.velocity,
        "inversion": getattr(chord, "inversion", 0),
    }


def _beat_to_dict(beat) -> dict:
    event = beat.event
    if event is None:
        return {"event": None}
    from .engine import Chord

    if isinstance(event, Chord):
        return {"event": _chord_to_dict(event)}
    # Note
    return {"event": _note_to_dict(event)}


def _track_to_dict(track) -> dict:
    return {
        "name": track.name,
        "instrument": track.instrument,
        "volume": track.volume,
        "pan": track.pan,
        "swing": track.swing,
        "density": track.density,
        "density_seed": track.density_seed,
        "beats": [_beat_to_dict(b) for b in track.beats],
    }


def _designer_to_dict(designer) -> dict | None:
    if hasattr(designer, "to_dict"):
        return designer.to_dict()
    return None


def song_to_json(song, path: str | Path | None = None, as_string: bool = False) -> dict | str:
    """Serialize a Song to a JSON-compatible dict.

    Args:
        song:      Song object.
        path:      If provided, write JSON to this file path.
        as_string: If True, return a JSON string instead of a dict.

    Returns:
        Dict (default), JSON string (if as_string=True), or dict (if path provided).
    """
    data = {
        "version": "1.0",
        "title": song.title,
        "bpm": song.bpm,
        "sample_rate": song.sample_rate,
        "time_sig": list(song.time_sig),
        "composer": song.composer,
        "key_sig": song.key_sig,
        "tracks": [_track_to_dict(t) for t in song.tracks],
        "custom_instruments": {
            name: _designer_to_dict(d)
            for name, d in song._custom_instruments.items()
            if _designer_to_dict(d) is not None
        },
        "bpm_map": song.bpm_map if song.bpm_map else [],
    }

    if path is not None:
        Path(path).write_text(json.dumps(data, indent=2))
    if as_string:
        return json.dumps(data, indent=2)
    return data


def song_from_json(source: dict | str | Path):
    """Reconstruct a Song from a JSON dict, string, or file path.

    Args:
        source: Dict, JSON string, or path to a .json file.

    Returns:
        Reconstructed Song object.
    """
    from .engine import Beat, Chord, Note, Song, Track

    if isinstance(source, Path):
        data = json.loads(source.read_text())
    elif isinstance(source, str):
        # Distinguish file path from JSON string: paths are short, JSON starts with {
        if not source.strip().startswith("{") and len(source) < 500:
            path = Path(source)
            if path.exists():
                data = json.loads(path.read_text())
            else:
                data = json.loads(source)
        else:
            data = json.loads(source)
    else:
        data = source

    song = Song(
        title=data.get("title", "untitled"),
        bpm=data.get("bpm", 120.0),
        sample_rate=data.get("sample_rate", 44100),
    )
    song.time_sig = tuple(data.get("time_sig", [4, 4]))
    song.composer = data.get("composer", "")
    song.key_sig = data.get("key_sig", "C")
    song.bpm_map = data.get("bpm_map", [])

    # Restore custom instruments
    custom = data.get("custom_instruments", {})
    if custom:
        from .sound_design import SoundDesigner

        for name, design_data in custom.items():
            if design_data:
                designer = SoundDesigner.from_dict(design_data)
                song.register_instrument(name, designer)

    # Restore tracks
    for td in data.get("tracks", []):
        track = Track(
            name=td.get("name", "track"),
            instrument=td.get("instrument", "sine"),
            volume=td.get("volume", 0.8),
            pan=td.get("pan", 0.0),
            swing=td.get("swing", 0.0),
            density=td.get("density", 1.0),
            density_seed=td.get("density_seed"),
        )
        for bd in td.get("beats", []):
            event_data = bd.get("event")
            if event_data is None:
                track.beats.append(Beat(event=None))
            elif event_data.get("type") == "chord":
                chord = Chord(
                    root=event_data["root"],
                    shape=event_data.get("shape", "maj"),
                    octave=event_data.get("octave", 3),
                    duration=event_data.get("duration", 4.0),
                    velocity=event_data.get("velocity", 0.65),
                )
                if event_data.get("inversion", 0) != 0:
                    chord.inversion = event_data["inversion"]
                track.beats.append(Beat(event=chord))
            else:
                note = Note(
                    pitch=event_data.get("pitch"),
                    octave=event_data.get("octave", 4),
                    duration=event_data.get("duration", 1.0),
                    velocity=event_data.get("velocity", 0.8),
                )
                track.beats.append(Beat(event=note))
        song.add_track(track)

    return song
