"""Tests for __version__ and CLI --version."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_version_is_importable():
    from code_music import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_is_semver_like():
    from code_music import __version__

    # Should be X.Y.Z or X.Y.Z-dev or 0.0.0-dev
    parts = __version__.split("-")[0].split(".")
    assert len(parts) >= 2
    assert all(p.isdigit() for p in parts)


def test_cli_version_flag():
    result = subprocess.run(
        [sys.executable, "-m", "code_music.cli", "--version"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0
    assert "code-music" in result.stdout
