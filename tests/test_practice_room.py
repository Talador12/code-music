"""Tests for v76.0 — click_track, backing_track, tempo_trainer."""

from code_music.theory import backing_track, click_track, tempo_trainer


class TestClickTrack:
    def test_correct_count(self):
        notes = click_track(bpm=120, bars=4, beats_per_bar=4)
        assert len(notes) == 16  # 4 bars * 4 beats

    def test_beat_1_accented(self):
        notes = click_track(bpm=120, bars=1, beats_per_bar=4)
        assert notes[0].velocity == 100

    def test_other_beats_softer(self):
        notes = click_track(bpm=120, bars=1, beats_per_bar=4)
        assert notes[1].velocity < notes[0].velocity

    def test_subdivisions(self):
        notes = click_track(bpm=120, bars=1, beats_per_bar=4, subdivisions=2)
        assert len(notes) == 8  # 4 beats * 2 subdivisions

    def test_3_4_time(self):
        notes = click_track(bpm=120, bars=2, beats_per_bar=3)
        assert len(notes) == 6


class TestBackingTrack:
    def test_returns_all_parts(self):
        prog = [("C", "maj"), ("G", "dom7")]
        result = backing_track(prog, style="rock")
        assert "bass" in result
        assert "chords" in result
        assert "kick" in result
        assert "snare" in result
        assert "hat" in result

    def test_jazz_style(self):
        prog = [("D", "min7"), ("G", "dom7")]
        result = backing_track(prog, style="jazz", seed=42)
        assert len(result["bass"]) > 0

    def test_funk_style(self):
        prog = [("E", "min7")]
        result = backing_track(prog, style="funk", seed=42)
        assert len(result["bass"]) > 0

    def test_latin_style(self):
        prog = [("A", "min")]
        result = backing_track(prog, style="latin", seed=42)
        assert len(result["bass"]) > 0


class TestTempoTrainer:
    def test_sections(self):
        plan = tempo_trainer(start_bpm=80, end_bpm=120, bpm_increment=10)
        assert len(plan) == 5  # 80, 90, 100, 110, 120

    def test_first_section_bpm(self):
        plan = tempo_trainer(start_bpm=60, end_bpm=100, bpm_increment=20)
        assert plan[0]["bpm"] == 60.0

    def test_last_section_bpm(self):
        plan = tempo_trainer(start_bpm=60, end_bpm=100, bpm_increment=20)
        assert plan[-1]["bpm"] == 100.0

    def test_each_has_click(self):
        plan = tempo_trainer(start_bpm=100, end_bpm=120, bpm_increment=10)
        for section in plan:
            assert "click" in section
            assert len(section["click"]) > 0
