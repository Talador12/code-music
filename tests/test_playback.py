"""Tests for the playback module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from code_music import Note, Song, Track
from code_music.playback import (
    _has_sounddevice,
    _play_fallback,
    _play_sounddevice,
    _system_player,
    play,
)


class TestHasSounddevice:
    def test_returns_bool(self):
        result = _has_sounddevice()
        assert isinstance(result, bool)


class TestSystemPlayer:
    def test_returns_string_or_none(self):
        result = _system_player()
        assert result is None or isinstance(result, str)

    @patch("shutil.which", return_value=None)
    def test_returns_none_when_nothing_found(self, _mock):
        assert _system_player() is None

    @patch("shutil.which", side_effect=lambda cmd: "/usr/bin/afplay" if cmd == "afplay" else None)
    def test_finds_afplay(self, _mock):
        assert _system_player() == "afplay"


class TestPlaySounddevice:
    def test_calls_sd_play_and_wait(self, monkeypatch):
        mock_sd = MagicMock()
        monkeypatch.setitem(__import__("sys").modules, "sounddevice", mock_sd)

        samples = np.zeros((44100, 2), dtype=np.float64)
        _play_sounddevice(samples, 44100, "Test")
        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()
        # Verify float32 conversion
        call_args = mock_sd.play.call_args
        assert call_args[0][0].dtype == np.float32


class TestPlayFallback:
    @patch("shutil.which", return_value=None)
    def test_prints_error_when_no_player(self, _mock, capsys):
        samples = np.zeros((22050, 2), dtype=np.float64)
        _play_fallback(samples, 22050, "Test")
        captured = capsys.readouterr()
        assert "no audio player found" in captured.err

    @patch("subprocess.run")
    @patch("shutil.which", side_effect=lambda cmd: "/usr/bin/afplay" if cmd == "afplay" else None)
    def test_creates_temp_wav_and_plays(self, _which, mock_run):
        samples = np.random.randn(22050, 2).astype(np.float64) * 0.1
        _play_fallback(samples, 22050, "Test")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "afplay"
        assert args[1].endswith(".wav")


class TestPlay:
    def test_play_renders_and_dispatches(self, monkeypatch):
        rendered = []

        def fake_render(self, song):
            result = np.zeros((22050, 2), dtype=np.float64)
            rendered.append(True)
            return result

        monkeypatch.setattr("code_music.synth.Synth.render_song", fake_render)
        monkeypatch.setattr("code_music.playback._has_sounddevice", lambda: False)
        monkeypatch.setattr("code_music.playback._play_fallback", lambda *a, **kw: None)

        song = Song(title="Test Play", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))

        play(song)
        assert len(rendered) == 1

    def test_play_with_bpm_override(self, monkeypatch):
        monkeypatch.setattr(
            "code_music.synth.Synth.render_song",
            lambda self, song: np.zeros((22050, 2), dtype=np.float64),
        )
        monkeypatch.setattr("code_music.playback._has_sounddevice", lambda: False)
        monkeypatch.setattr("code_music.playback._play_fallback", lambda *a, **kw: None)

        song = Song(title="BPM Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))

        play(song, bpm=90)
        assert song.bpm == 90
