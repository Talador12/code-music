"""Tests for key generated Makefile targets."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_SCALE_STEMS = sorted(p.stem for p in (ROOT / "scales").glob("_*.py"))
INTERNAL_SONG_STEMS = sorted(p.stem for p in (ROOT / "songs").glob("_*.py"))
INTERNAL_ALBUM_STEMS = sorted(p.stem for p in (ROOT / "albums").glob("_*.py"))
INTERNAL_SAMPLE_STEMS = sorted(p.stem for p in (ROOT / "samples").glob("**/_*.py"))


def _run_make(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def _run_make_allow_fail(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_preview_voice_pacing_demo_target_is_listed() -> None:
    result = _run_make("list-samples")
    assert "preview-voice_pacing_demo" in result.stdout


def test_list_samples_has_no_duplicate_target_warning() -> None:
    result = _run_make("list-samples")
    assert "overriding commands for target" not in result.stderr


def test_generated_album_play_target_keeps_shell_vars() -> None:
    result = _run_make("-n", "play-album-anthology")
    assert "dist/albums/anthology/*.wav" in result.stdout
    assert 'echo "  ▶ ${f##*/}"' in result.stdout
    assert '"$f"' in result.stdout


def test_generated_album_play_target_for_non_default_album_keeps_shell_vars() -> None:
    result = _run_make("-n", "play-album-jazz_neosoul")
    assert "dist/albums/jazz_neosoul/*.wav" in result.stdout
    assert 'echo "  ▶ ${f##*/}"' in result.stdout
    assert '"$f"' in result.stdout


def test_generated_song_play_target_renders_expected_wav_path() -> None:
    result = _run_make("-n", "play-trance_odyssey")
    assert "dist/wav/trance_odyssey.wav" in result.stdout
    assert "afplay" in result.stdout


@pytest.mark.parametrize(
    ("song", "wav_path"),
    [
        ("trance_odyssey", "dist/wav/trance_odyssey.wav"),
        ("tank_bebop", "dist/wav/tank_bebop.wav"),
        ("deep_space_drift", "dist/wav/deep_space_drift.wav"),
    ],
)
def test_generated_song_play_targets_exist_for_representative_songs(
    song: str, wav_path: str
) -> None:
    result = _run_make("-n", f"play-{song}")
    assert wav_path in result.stdout


@pytest.mark.parametrize(
    ("sample", "wav_path"),
    [
        ("voice_pacing_demo", "dist/samples/voice_pacing_demo.wav"),
        ("adagio_cello", "dist/samples/adagio_cello.wav"),
        ("pure_sine", "dist/samples/pure_sine.wav"),
    ],
)
def test_generated_sample_preview_targets_exist_for_representative_samples(
    sample: str, wav_path: str
) -> None:
    result = _run_make("-n", f"preview-{sample}")
    assert wav_path in result.stdout
    assert "afplay" in result.stdout


@pytest.mark.parametrize(
    ("scale_name", "wav_path"),
    [
        ("major", "dist/scales/major.wav"),
        ("blues_minor", "dist/scales/blues_minor.wav"),
        ("whole_tone", "dist/scales/whole_tone.wav"),
    ],
)
def test_generated_scale_play_targets_exist_for_representative_scales(
    scale_name: str, wav_path: str
) -> None:
    result = _run_make("-n", f"play-scale-{scale_name}")
    assert wav_path in result.stdout
    assert "afplay" in result.stdout


@pytest.mark.parametrize("stem", INTERNAL_SCALE_STEMS)
def test_internal_underscore_scale_target_is_not_exposed(stem: str) -> None:
    result = _run_make_allow_fail("-n", f"play-scale-{stem}")
    assert result.returncode != 0
    assert "No rule to make target" in result.stderr


def test_circle_of_fifths_friendly_scale_target_is_exposed() -> None:
    result = _run_make("-n", "play-scale-circle_of_fifths")
    assert "dist/scales/circle_of_fifths.wav" in result.stdout
    assert "scales/_circle_of_fifths.py" in result.stdout
    assert "afplay" in result.stdout


@pytest.mark.parametrize("stem", INTERNAL_SONG_STEMS)
def test_internal_song_template_target_is_not_exposed(stem: str) -> None:
    result = _run_make_allow_fail("-n", f"play-{stem}")
    assert result.returncode != 0
    assert "No rule to make target" in result.stderr


@pytest.mark.parametrize("stem", INTERNAL_ALBUM_STEMS)
def test_internal_album_helper_target_is_not_exposed(stem: str) -> None:
    result = _run_make_allow_fail("-n", f"album-{stem}")
    assert result.returncode != 0
    assert "No rule to make target" in result.stderr


def test_internal_sample_targets_are_not_exposed() -> None:
    for stem in INTERNAL_SAMPLE_STEMS:
        result = _run_make_allow_fail("-n", f"preview-{stem}")
        assert result.returncode != 0
        assert "No rule to make target" in result.stderr


def test_make_help_includes_circle_of_fifths_alias() -> None:
    result = _run_make("help")
    assert "play-scale-circle_of_fifths" in result.stdout


def test_make_help_excludes_internal_targets() -> None:
    result = _run_make("help")
    assert "play-scale-_circle_of_fifths" not in result.stdout
    assert "play-_template_beginner" not in result.stdout
    assert "album-_album" not in result.stdout


def test_list_scales_uses_friendly_circle_name_not_internal_stem() -> None:
    result = _run_make("list-scales")
    assert "Circle of Fifths" in result.stdout
    assert "_circle_of_fifths" not in result.stdout


def test_list_songs_excludes_internal_templates() -> None:
    result = _run_make("list-songs")
    assert "_template_" not in result.stdout


def test_list_samples_excludes_internal_preview_stems() -> None:
    result = _run_make("list-samples")
    assert "preview-_" not in result.stdout


@pytest.mark.parametrize(
    ("album", "render_cmd_fragment"),
    [
        ("anthology", "-m albums.render anthology"),
        ("jazz_neosoul", "-m albums.render jazz_neosoul"),
        ("edm_progressive", "-m albums.render edm_progressive"),
    ],
)
def test_generated_album_render_targets_exist_for_representative_albums(
    album: str, render_cmd_fragment: str
) -> None:
    result = _run_make("-n", f"album-{album}")
    assert render_cmd_fragment in result.stdout
