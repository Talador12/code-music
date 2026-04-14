"""Tests for v166.0: VocalTrack, flow patterns, TTS backends."""

import unittest

import numpy as np

from code_music import (
    FlowBeat,
    Song,
    VocalEvent,
    VocalTrack,
    apply_flow_to_lyrics,
    flow_summary,
    generate_flow,
    list_tts_backends,
)


class TestVocalTrack(unittest.TestCase):
    def test_create(self):
        vt = VocalTrack(name="vocals")
        assert len(vt) == 0

    def test_say(self):
        vt = VocalTrack()
        vt.say("hello world", at_beat=0, duration_beats=2)
        assert len(vt) == 1
        assert vt.events[0].text == "hello world"

    def test_chaining(self):
        vt = VocalTrack().say("a", at_beat=0).say("b", at_beat=2)
        assert len(vt) == 2

    def test_render_formant_fallback(self):
        vt = VocalTrack(backend="formant")
        vt.say("test", at_beat=0, duration_beats=2)
        audio = vt.render(bpm=120, sample_rate=22050)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.001

    def test_render_empty(self):
        vt = VocalTrack()
        audio = vt.render(bpm=120, sample_rate=22050)
        assert len(audio) > 0

    def test_set_backend(self):
        vt = VocalTrack()
        vt.set_backend("formant")
        assert vt.backend == "formant"

    def test_invalid_backend(self):
        vt = VocalTrack()
        with self.assertRaises(ValueError):
            vt.set_backend("nonexistent_tts_engine")

    def test_multiple_events(self):
        vt = VocalTrack(backend="formant")
        vt.say("one", at_beat=0, duration_beats=2)
        vt.say("two", at_beat=4, duration_beats=2)
        vt.say("three", at_beat=8, duration_beats=2)
        audio = vt.render(bpm=120, sample_rate=22050)
        assert len(audio) > 22050  # > 1 second

    def test_repr(self):
        vt = VocalTrack(name="vox")
        vt.say("hi")
        r = repr(vt)
        assert "vox" in r
        assert "1 events" in r

    def test_add_to_song(self):
        song = Song(title="Vocal Test", bpm=120, sample_rate=22050)
        vt = VocalTrack(name="vocals")
        vt.say("hello", at_beat=0)
        song.add_vocal_track(vt)
        assert hasattr(song, "_vocal_tracks")
        assert len(song._vocal_tracks) == 1


class TestTTSBackends(unittest.TestCase):
    def test_list_backends(self):
        backends = list_tts_backends()
        assert isinstance(backends, list)
        names = [b["name"] for b in backends]
        assert "formant" in names
        assert "system" in names

    def test_formant_always_available(self):
        backends = list_tts_backends()
        formant = [b for b in backends if b["name"] == "formant"][0]
        assert formant["available"] is True


class TestFlowPatterns(unittest.TestCase):
    def test_boom_bap(self):
        pattern = generate_flow("boom_bap", bars=4, seed=42)
        assert len(pattern) > 0
        assert all(isinstance(fb, FlowBeat) for fb in pattern)

    def test_triplet(self):
        pattern = generate_flow("triplet", bars=2, seed=42)
        assert len(pattern) > 0

    def test_double_time(self):
        pattern = generate_flow("double_time", bars=2, seed=42)
        syllables = [fb for fb in pattern if not fb.rest]
        # Double time should be dense
        assert len(syllables) > 10

    def test_laid_back(self):
        pattern = generate_flow("laid_back", bars=2, seed=42)
        assert len(pattern) > 0

    def test_syncopated(self):
        pattern = generate_flow("syncopated", bars=2, seed=42)
        assert len(pattern) > 0

    def test_southern(self):
        pattern = generate_flow("southern", bars=2, seed=42)
        assert len(pattern) > 0

    def test_all_styles(self):
        for style in ["boom_bap", "triplet", "double_time", "laid_back", "syncopated", "southern"]:
            p = generate_flow(style, bars=2, seed=42)
            assert len(p) > 0, f"{style} produced empty pattern"

    def test_apply_lyrics(self):
        pattern = generate_flow("boom_bap", bars=4, seed=42)
        events = apply_flow_to_lyrics(["yo", "check it", "one two"], pattern)
        assert len(events) == 3
        assert events[0]["text"] == "yo"

    def test_flow_summary(self):
        s = flow_summary("triplet", bars=4, seed=42)
        assert s["style"] == "triplet"
        assert s["syllable_count"] > 0
        assert s["density"] > 0

    def test_deterministic(self):
        p1 = generate_flow("boom_bap", bars=4, seed=99)
        p2 = generate_flow("boom_bap", bars=4, seed=99)
        assert len(p1) == len(p2)


class TestImports(unittest.TestCase):
    def test_all_imports(self):
        from code_music import (
            FlowBeat,
            VocalTrack,
            apply_flow_to_lyrics,
            flow_summary,
            generate_flow,
            list_tts_backends,
            register_tts_backend,
        )

        for obj in [
            FlowBeat,
            VocalEvent,
            VocalTrack,
            apply_flow_to_lyrics,
            flow_summary,
            generate_flow,
            list_tts_backends,
            register_tts_backend,
        ]:
            assert obj is not None


if __name__ == "__main__":
    unittest.main()
