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


class TestVoiceClipPresets:
    def test_narration_factory_defaults(self):
        clip = VoiceClip.narration("welcome to the long-form version")
        assert clip.rate == 92
        assert clip.pause_short_sec == 0.18
        assert clip.pause_terminal_sec == 0.34

    def test_rap_factory_defaults(self):
        clip = VoiceClip.rap("bars on bars")
        assert clip.rate == 148
        assert clip.pause_short_sec == 0.04
        assert clip.pause_terminal_sec == 0.09

    def test_factory_kwargs_override_defaults(self):
        clip = VoiceClip.narration(
            "custom narrator",
            voice="Daniel",
            rate=105,
            pause_short_sec=0.2,
            backend="say",
        )
        assert clip.voice == "Daniel"
        assert clip.rate == 105
        assert clip.pause_short_sec == 0.2
        assert clip.backend == "say"


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


class TestVoiceTrackEstimate:
    def test_empty_is_zero(self):
        track = VoiceTrack(name="vox")
        assert track.estimate_total_beats(bpm=120) == 0.0

    def test_includes_beat_offset(self):
        track = VoiceTrack(name="vox")
        track.add(VoiceClip("short phrase", rate=100), beat_offset=6.0)
        assert track.estimate_total_beats(bpm=120) > 6.0

    def test_slower_rate_estimates_longer(self):
        text = "this is a somewhat longer phrase for timing estimation"
        slow = VoiceTrack(name="slow").add(VoiceClip(text, rate=70), beat_offset=0.0)
        fast = VoiceTrack(name="fast").add(VoiceClip(text, rate=170), beat_offset=0.0)
        assert slow.estimate_total_beats(bpm=120) > fast.estimate_total_beats(bpm=120)

    def test_punctuation_adds_pause_time(self):
        plain = VoiceTrack(name="plain").add(
            VoiceClip("hello world this is flowing", rate=100), beat_offset=0.0
        )
        punct = VoiceTrack(name="punct").add(
            VoiceClip("hello, world. this is flowing!", rate=100), beat_offset=0.0
        )
        assert punct.estimate_total_beats(bpm=120) > plain.estimate_total_beats(bpm=120)

    def test_terminal_punctuation_matters(self):
        no_stop = VoiceTrack(name="nostop").add(
            VoiceClip("we keep going and going", rate=100), beat_offset=0.0
        )
        with_stop = VoiceTrack(name="withstop").add(
            VoiceClip("we keep going and going.", rate=100), beat_offset=0.0
        )
        assert with_stop.estimate_total_beats(bpm=120) > no_stop.estimate_total_beats(bpm=120)

    def test_pause_overrides_can_shorten_estimate(self):
        text = "pause, pause."
        default = VoiceTrack(name="default").add(VoiceClip(text, rate=100), beat_offset=0.0)
        clipped = VoiceTrack(name="clipped").add(
            VoiceClip(text, rate=100, pause_short_sec=0.0, pause_terminal_sec=0.0),
            beat_offset=0.0,
        )
        assert clipped.estimate_total_beats(bpm=120) < default.estimate_total_beats(bpm=120)

    def test_pause_overrides_can_lengthen_estimate(self):
        text = "wait, wait?"
        default = VoiceTrack(name="default").add(VoiceClip(text, rate=100), beat_offset=0.0)
        stretched = VoiceTrack(name="stretched").add(
            VoiceClip(text, rate=100, pause_short_sec=0.4, pause_terminal_sec=0.8),
            beat_offset=0.0,
        )
        assert stretched.estimate_total_beats(bpm=120) > default.estimate_total_beats(bpm=120)


class TestLyrics:
    def test_from_text_parses_lines(self):
        from code_music.voice import Lyrics

        lyrics = Lyrics.from_text(
            """
            hello world
            second line
            third line
        """,
            start_beat=0.0,
            beats_per_line=4.0,
        )
        assert len(lyrics.lines) == 3
        assert lyrics.lines[0] == (0.0, "hello world")
        assert lyrics.lines[1] == (4.0, "second line")
        assert lyrics.lines[2] == (8.0, "third line")

    def test_from_text_custom_start(self):
        from code_music.voice import Lyrics

        lyrics = Lyrics.from_text("one\ntwo", start_beat=8.0, beats_per_line=2.0)
        assert lyrics.lines[0][0] == 8.0
        assert lyrics.lines[1][0] == 10.0

    def test_from_text_skips_empty_lines(self):
        from code_music.voice import Lyrics

        lyrics = Lyrics.from_text("""
            line one

            line two
        """)
        assert len(lyrics.lines) == 2

    def test_manual_lyrics(self):
        from code_music.voice import Lyrics

        lyrics = Lyrics([(0.0, "hello"), (2.5, "world")])
        assert len(lyrics.lines) == 2
        assert lyrics.lines[1] == (2.5, "world")

    def test_to_voice_track(self):
        from code_music.voice import Lyrics, VoiceTrack

        lyrics = Lyrics.from_text("hello\nworld", beats_per_line=4.0)
        vt = lyrics.to_voice_track(name="vox", voice="Samantha", backend="say")
        assert isinstance(vt, VoiceTrack)
        assert vt.name == "vox"
        assert len(vt.clips) == 2
        assert vt.clips[0][0].text == "hello"
        assert vt.clips[0][1] == 0.0  # beat offset
        assert vt.clips[1][0].text == "world"
        assert vt.clips[1][1] == 4.0

    def test_to_voice_track_voice_params(self):
        from code_music.voice import Lyrics

        lyrics = Lyrics([(0.0, "test")])
        vt = lyrics.to_voice_track(voice="Zarvox", rate=80, volume=0.5, pan=-0.3)
        clip = vt.clips[0][0]
        assert clip.voice == "Zarvox"
        assert clip.rate == 80
        assert clip.volume == 0.5
        assert clip.pan == -0.3
