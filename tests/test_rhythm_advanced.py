"""Tests for v40.0 — quintuplet, septuplet, generate_polyrhythm, metric_modulation."""

from code_music.engine import Note
from code_music.theory import generate_polyrhythm, metric_modulation, quintuplet, septuplet


class TestQuintuplet:
    def test_five_notes_fit(self):
        notes = [Note("C", 5, 1.0) for _ in range(5)]
        result = quintuplet(notes, total_duration=2.0)
        assert len(result) == 5

    def test_duration_is_total_over_five(self):
        notes = [Note("C", 5, 1.0) for _ in range(5)]
        result = quintuplet(notes, total_duration=2.0)
        assert abs(result[0].duration - 0.4) < 1e-9

    def test_fewer_than_five(self):
        notes = [Note("C", 5, 1.0) for _ in range(3)]
        result = quintuplet(notes, total_duration=1.0)
        assert len(result) == 3
        assert abs(result[0].duration - 0.2) < 1e-9

    def test_more_than_five_truncates(self):
        notes = [Note("C", 5, 1.0) for _ in range(8)]
        result = quintuplet(notes, total_duration=1.0)
        assert len(result) == 5

    def test_preserves_pitch(self):
        notes = [Note("E", 4, 1.0), Note("G", 4, 1.0)]
        result = quintuplet(notes)
        assert result[0].pitch == "E"
        assert result[1].pitch == "G"


class TestSeptuplet:
    def test_seven_notes_fit(self):
        notes = [Note("D", 4, 1.0) for _ in range(7)]
        result = septuplet(notes, total_duration=2.0)
        assert len(result) == 7

    def test_duration_is_total_over_seven(self):
        notes = [Note("D", 4, 1.0) for _ in range(7)]
        result = septuplet(notes, total_duration=2.0)
        assert abs(result[0].duration - 2.0 / 7) < 1e-9

    def test_fewer_than_seven(self):
        notes = [Note("D", 4, 1.0) for _ in range(4)]
        result = septuplet(notes, total_duration=2.0)
        assert len(result) == 4

    def test_more_than_seven_truncates(self):
        notes = [Note("D", 4, 1.0) for _ in range(10)]
        result = septuplet(notes, total_duration=2.0)
        assert len(result) == 7


class TestGeneratePolyrhythm:
    def test_three_against_four(self):
        a, b = generate_polyrhythm("C", rhythm_a=3, rhythm_b=4, bars=1)
        assert len(a) == 3
        assert len(b) == 4

    def test_durations_fill_bar(self):
        a, b = generate_polyrhythm("C", rhythm_a=3, rhythm_b=4, bars=1)
        total_a = sum(n.duration for n in a)
        total_b = sum(n.duration for n in b)
        assert abs(total_a - total_b) < 1e-9  # both fill the same bar

    def test_multiple_bars(self):
        a, b = generate_polyrhythm("E", rhythm_a=5, rhythm_b=4, bars=2)
        assert len(a) == 10
        assert len(b) == 8

    def test_octave_offset(self):
        a, b = generate_polyrhythm("C", octave=3)
        assert a[0].octave == 3
        assert b[0].octave == 4


class TestMetricModulation:
    def test_triplets_to_straight(self):
        # 120 BPM, triplets (3) become straight (2) = 120 * 3/2 = 180
        new_bpm = metric_modulation(120.0, old_subdivision=3, new_subdivision=2)
        assert abs(new_bpm - 180.0) < 1e-9

    def test_sixteenths_to_triplets(self):
        # 120 BPM, 16ths (4) become triplets (3) = 120 * 4/3 = 160
        new_bpm = metric_modulation(120.0, old_subdivision=4, new_subdivision=3)
        assert abs(new_bpm - 160.0) < 1e-9

    def test_identity(self):
        new_bpm = metric_modulation(100.0, old_subdivision=4, new_subdivision=4)
        assert abs(new_bpm - 100.0) < 1e-9

    def test_slow_down(self):
        # 4→6 = slower
        new_bpm = metric_modulation(120.0, old_subdivision=4, new_subdivision=6)
        assert new_bpm < 120.0
