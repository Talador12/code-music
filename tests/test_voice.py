"""Tests for voice.py — backend detection, clip generation, VoiceTrack render."""

import numpy as np
import pytest

from code_music.voice import (
    VoiceClip,
    VoiceTrack,
    detect_backends,
    generate,
    list_voices,
    render_voice_track,
)

SR = 22050


class TestDetectBackends:
    def test_returns_list(self):
        backends = detect_backends()
        assert isinstance(backends, list)

    def test_say_available_on_macos(self):
        import shutil
        import sys

        if sys.platform == "darwin" and shutil.which("say") and shutil.which("afconvert"):
            assert "say" in detect_backends()


class TestListVoices:
    def test_bark_voices_known(self):
        voices = list_voices("bark")
        assert "narrator" in voices
        assert len(voices) > 0

    def test_openai_voices_known(self):
        voices = list_voices("openai")
        assert "alloy" in voices
        assert len(voices) == 6

    def test_elevenlabs_voices_known(self):
        voices = list_voices("elevenlabs")
        assert "rachel" in voices

    def test_say_voices_on_macos(self):
        import sys

        if sys.platform == "darwin":
            voices = list_voices("say")
            assert len(voices) > 10


class TestVoiceClipDefaults:
    def test_defaults(self):
        clip = VoiceClip("hello")
        assert clip.text == "hello"
        assert clip.volume == 0.8
        assert clip.pan == 0.0
        assert clip.pitch == 0.0
        assert clip.backend == "auto"


class TestGenerateSayBackend:
    """These tests only run on macOS where say + afconvert are available."""

    @pytest.fixture(autouse=True)
    def skip_if_no_say(self):
        import shutil
        import sys

        if sys.platform != "darwin" or not shutil.which("say") or not shutil.which("afconvert"):
            pytest.skip("say backend requires macOS with Xcode CLT")

    def test_basic_generation(self):
        clip = VoiceClip("hello", voice="Samantha", backend="say")
        samples = generate(clip, sample_rate=SR)
        assert samples.ndim == 2
        assert samples.shape[1] == 2
        assert samples.shape[0] > SR // 4  # at least 0.25s

    def test_output_clamped(self):
        clip = VoiceClip("test", voice="Samantha", backend="say")
        samples = generate(clip, sample_rate=SR)
        assert np.max(np.abs(samples)) <= 1.0 + 1e-6

    def test_volume_applied(self):
        clip_loud = VoiceClip("test", voice="Samantha", backend="say", volume=0.9)
        clip_quiet = VoiceClip("test", voice="Samantha", backend="say", volume=0.1)
        loud = generate(clip_loud, sample_rate=SR)
        quiet = generate(clip_quiet, sample_rate=SR)
        assert np.max(np.abs(loud)) > np.max(np.abs(quiet))

    def test_pan_left(self):
        clip = VoiceClip("ah", voice="Samantha", backend="say", pan=-0.9)
        samples = generate(clip, sample_rate=SR)
        assert np.mean(np.abs(samples[:, 0])) > np.mean(np.abs(samples[:, 1]))

    def test_pan_right(self):
        clip = VoiceClip("ah", voice="Samantha", backend="say", pan=0.9)
        samples = generate(clip, sample_rate=SR)
        assert np.mean(np.abs(samples[:, 1])) > np.mean(np.abs(samples[:, 0]))

    def test_unknown_voice_falls_back_or_raises(self):
        # macOS say silently uses a fallback voice for unknown names,
        # so we accept either behavior: valid audio or an exception
        clip = VoiceClip("test", voice="NonExistentVoiceXXX999", backend="say")
        try:
            samples = generate(clip, sample_rate=SR)
            assert samples.shape[0] > 0  # fell back gracefully
        except (RuntimeError, OSError):
            pass  # raising is also acceptable

    def test_zarvox_voice(self):
        clip = VoiceClip("la la la", voice="Zarvox", backend="say")
        samples = generate(clip, sample_rate=SR)
        assert samples.shape[0] > 0

    def test_cellos_voice(self):
        clip = VoiceClip("aaah ooooh", voice="Cellos", backend="say", rate=80)
        samples = generate(clip, sample_rate=SR)
        assert samples.shape[0] > 0


class TestVoiceTrack:
    @pytest.fixture(autouse=True)
    def skip_if_no_say(self):
        import shutil
        import sys

        if sys.platform != "darwin" or not shutil.which("say") or not shutil.which("afconvert"):
            pytest.skip("say backend requires macOS")

    def test_render_empty_track(self):
        track = VoiceTrack(name="empty")
        result = render_voice_track(track, bpm=120, total_beats=8.0, sample_rate=SR)
        assert result.ndim == 2
        assert result.shape[1] == 2

    def test_render_with_clip(self):
        track = VoiceTrack(name="vox")
        track.add(VoiceClip("hello", voice="Samantha", backend="say"), beat_offset=0.0)
        result = render_voice_track(track, bpm=120, total_beats=8.0, sample_rate=SR)
        assert np.max(np.abs(result)) > 0.0

    def test_clip_placed_at_beat_offset(self):
        track = VoiceTrack(name="vox")
        # Place at beat 4 — first 2s (4 beats @120bpm = 2s) should be silent
        track.add(VoiceClip("hi", voice="Samantha", backend="say"), beat_offset=4.0)
        result = render_voice_track(track, bpm=120, total_beats=8.0, sample_rate=SR)
        beat_sec = 60.0 / 120.0
        silent_end = int(3.0 * beat_sec * SR)  # 3 beats before clip starts
        assert np.max(np.abs(result[:silent_end])) < 0.01

    def test_multiple_clips(self):
        track = VoiceTrack(name="vox")
        track.add(VoiceClip("one", voice="Samantha", backend="say"), beat_offset=0.0)
        track.add(VoiceClip("two", voice="Zarvox", backend="say"), beat_offset=4.0)
        result = render_voice_track(track, bpm=120, total_beats=8.0, sample_rate=SR)
        assert result.shape[0] > 0
