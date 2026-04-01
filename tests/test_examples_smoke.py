"""Smoke test: verify all examples import without error and define a song variable."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"

EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.py"))


@pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.stem)
def test_example_imports_and_has_song_variable(example_file: Path) -> None:
    module_name = f"_smoke_ex_{example_file.stem}"
    sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(module_name, example_file)
    assert spec is not None
    assert spec.loader is not None

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    assert hasattr(mod, "song"), f"{example_file.name} does not define a `song` variable"
    assert mod.song.bpm > 0

    del sys.modules[module_name]
