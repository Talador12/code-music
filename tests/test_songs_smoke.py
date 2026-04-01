"""Smoke test: verify all songs import without error and define a song variable."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SONGS_DIR = ROOT / "songs"

# Collect all song files excluding templates
SONG_FILES = sorted(
    p for p in SONGS_DIR.glob("*.py") if not p.name.startswith("_") and p.name != "__init__.py"
)


@pytest.mark.parametrize("song_file", SONG_FILES, ids=lambda p: p.stem)
def test_song_imports_and_has_song_variable(song_file: Path) -> None:
    """Each song script must import without error and define `song`."""
    module_name = f"_smoke_{song_file.stem}"

    # Remove stale module if re-running
    sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(module_name, song_file)
    assert spec is not None, f"Could not create spec for {song_file}"
    assert spec.loader is not None

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    assert hasattr(mod, "song"), f"{song_file.name} does not define a `song` variable"

    song = mod.song
    assert hasattr(song, "title"), f"{song_file.name}: song has no title"
    assert hasattr(song, "bpm"), f"{song_file.name}: song has no bpm"
    assert hasattr(song, "tracks"), f"{song_file.name}: song has no tracks"
    assert song.bpm > 0, f"{song_file.name}: bpm must be positive"

    # Cleanup
    del sys.modules[module_name]
