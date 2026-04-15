"""Tests for rhythm game chart exporters (StepMania/DDR + Clone Hero/Guitar Hero)."""

import pytest

from code_music.engine import Chord, Note, Song, Track, scale
from code_music.rhythm_game import (
    export_stepmania,
    export_clone_hero,
    list_difficulties,
    _extract_onsets,
    _filter_onsets_by_difficulty,
)


def _make_test_song() -> Song:
    """Build a simple song for chart testing."""
    song = Song(title="Chart Test", bpm=120, sample_rate=22050)
    lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.7))
    lead.extend(scale("C", "major", 5, length=16))
    chords = song.add_track(Track(name="chords", instrument="piano"))
    chords.add(Chord("C", "maj", 4, duration=4.0))
    chords.add(Chord("G", "dom7", 4, duration=4.0))
    chords.add(Chord("F", "maj", 4, duration=4.0))
    chords.add(Chord("C", "maj", 4, duration=4.0))
    kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
    kick.extend([Note("C", 2, 1.0)] * 16)
    return song


class TestOnsetExtraction:
    def test_extracts_notes(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        assert len(onsets) > 0

    def test_onsets_are_sorted(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        beats = [o["beat"] for o in onsets]
        assert beats == sorted(beats)

    def test_onsets_have_required_fields(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        for o in onsets:
            assert "beat" in o
            assert "duration" in o
            assert "track" in o


class TestDifficultyScaling:
    def test_expert_keeps_all(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        filtered = _filter_onsets_by_difficulty(onsets, "expert")
        assert len(filtered) == len(onsets)

    def test_beginner_reduces(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        filtered = _filter_onsets_by_difficulty(onsets, "beginner")
        assert len(filtered) < len(onsets)

    def test_hard_more_than_easy(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        easy = _filter_onsets_by_difficulty(onsets, "easy")
        hard = _filter_onsets_by_difficulty(onsets, "hard")
        assert len(hard) >= len(easy)

    def test_difficulty_ordering(self):
        song = _make_test_song()
        onsets = _extract_onsets(song)
        counts = {}
        for diff in ["beginner", "easy", "medium", "hard", "expert"]:
            counts[diff] = len(_filter_onsets_by_difficulty(onsets, diff))
        assert counts["beginner"] <= counts["easy"]
        assert counts["easy"] <= counts["medium"]
        assert counts["medium"] <= counts["hard"]
        assert counts["hard"] <= counts["expert"]


class TestStepManiaExport:
    def test_creates_file(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.sm")
        result = export_stepmania(song, path)
        assert result.endswith(".sm")
        assert (tmp_path / "test.sm").exists()

    def test_file_has_header(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.sm")
        export_stepmania(song, path)
        content = (tmp_path / "test.sm").read_text()
        assert "#TITLE:Chart Test;" in content
        assert f"#BPMS:0.000={song.bpm:.3f};" in content

    def test_file_has_notes(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.sm")
        export_stepmania(song, path)
        content = (tmp_path / "test.sm").read_text()
        # Should have at least some non-zero rows
        assert "1" in content

    def test_file_has_measures(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.sm")
        export_stepmania(song, path)
        content = (tmp_path / "test.sm").read_text()
        # Measures separated by commas
        assert "," in content

    @pytest.mark.parametrize("difficulty", ["beginner", "easy", "medium", "hard", "expert"])
    def test_all_difficulties(self, tmp_path, difficulty):
        song = _make_test_song()
        path = str(tmp_path / f"test_{difficulty}.sm")
        result = export_stepmania(song, path, difficulty=difficulty)
        assert (tmp_path / f"test_{difficulty}.sm").exists()

    def test_single_track_chart(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "lead_only.sm")
        export_stepmania(song, path, track_name="lead")
        content = (tmp_path / "lead_only.sm").read_text()
        assert len(content) > 0

    def test_four_arrow_columns(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.sm")
        export_stepmania(song, path)
        content = (tmp_path / "test.sm").read_text()
        lines = content.split("\n")
        # Arrow rows should be exactly 4 characters (dance-single)
        arrow_lines = [l for l in lines if len(l) == 4 and all(c in "01" for c in l)]
        assert len(arrow_lines) > 0


class TestCloneHeroExport:
    def test_creates_file(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.chart")
        result = export_clone_hero(song, path)
        assert result.endswith(".chart")
        assert (tmp_path / "test.chart").exists()

    def test_file_has_song_section(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.chart")
        export_clone_hero(song, path)
        content = (tmp_path / "test.chart").read_text()
        assert "[Song]" in content
        assert '"Chart Test"' in content

    def test_file_has_sync_track(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.chart")
        export_clone_hero(song, path)
        content = (tmp_path / "test.chart").read_text()
        assert "[SyncTrack]" in content
        assert f"B {int(song.bpm * 1000)}" in content

    def test_file_has_note_events(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.chart")
        export_clone_hero(song, path)
        content = (tmp_path / "test.chart").read_text()
        assert "= N " in content

    def test_fret_range_0_to_4(self, tmp_path):
        song = _make_test_song()
        path = str(tmp_path / "test.chart")
        export_clone_hero(song, path)
        content = (tmp_path / "test.chart").read_text()
        # Parse note lines
        for line in content.split("\n"):
            if "= N " in line:
                parts = line.strip().split("= N ")
                fret = int(parts[1].split()[0])
                assert 0 <= fret <= 4

    @pytest.mark.parametrize("difficulty", ["beginner", "easy", "medium", "hard", "expert"])
    def test_all_difficulties(self, tmp_path, difficulty):
        song = _make_test_song()
        path = str(tmp_path / f"test_{difficulty}.chart")
        export_clone_hero(song, path, difficulty=difficulty)
        assert (tmp_path / f"test_{difficulty}.chart").exists()

    def test_expert_has_more_notes_than_easy(self, tmp_path):
        song = _make_test_song()
        p_easy = str(tmp_path / "easy.chart")
        p_expert = str(tmp_path / "expert.chart")
        export_clone_hero(song, p_easy, difficulty="easy")
        export_clone_hero(song, p_expert, difficulty="expert")
        easy_notes = open(p_easy).read().count("= N ")
        expert_notes = open(p_expert).read().count("= N ")
        assert expert_notes >= easy_notes

    def test_chords_produce_multiple_frets(self, tmp_path):
        song = Song(title="Chord Test", bpm=120, sample_rate=22050)
        tr = song.add_track(Track(name="chords", instrument="piano"))
        tr.add(Chord("C", "maj", 4, duration=4.0))
        path = str(tmp_path / "chord.chart")
        export_clone_hero(song, path, difficulty="expert")
        content = open(path).read()
        # A chord should produce 2+ N lines at the same tick
        lines = [l.strip() for l in content.split("\n") if "= N " in l]
        if len(lines) >= 2:
            # Check if any two lines share the same tick
            ticks = [l.split("=")[0].strip() for l in lines]
            assert len(ticks) != len(set(ticks)), "Chords should map to multiple frets"


class TestListDifficulties:
    def test_returns_five(self):
        assert len(list_difficulties()) == 5

    def test_ordering(self):
        diffs = list_difficulties()
        assert diffs[0] == "beginner"
        assert diffs[-1] == "expert"
