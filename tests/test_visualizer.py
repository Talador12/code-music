"""Tests for the real-time CLI visualizer."""

from __future__ import annotations

import numpy as np

from code_music import Chord, Note, Song, Track
from code_music.visualizer import (
    Frame,
    _build_frame,
    _build_timeline,
    _currently_sounding_midis,
    _draw_note_with_stem,
    _draw_staff_panel,
    _format_chord_label,
    _format_time,
    _hsl_to_rgb,
    _identify_chord,
    _midi_range_from_timelines,
    _note_rhythm,
    _Onset,
    _precompute_spectrum,
    _scale_color,
    _sparkle_at_now,
    _staff_row,
    _State,
    _supports_color,
    _track_palette,
    _truecolor,
    _vbar_char,
    _vu_chars,
    play_visual,
)


# ─── Color helpers ───────────────────────────────────────────────────
class TestColor:
    def test_truecolor_format(self):
        assert _truecolor(255, 128, 0) == "\x1b[38;2;255;128;0m"

    def test_hsl_zero_saturation_is_grayscale(self):
        r, g, b = _hsl_to_rgb(0.5, 0.0, 0.5)
        assert r == g == b

    def test_hsl_full_red(self):
        r, g, b = _hsl_to_rgb(0.0, 1.0, 0.5)
        assert r == 255 and g == 0 and b == 0

    def test_hsl_full_green(self):
        r, g, b = _hsl_to_rgb(1.0 / 3, 1.0, 0.5)
        assert g == 255 and r == 0 and b == 0

    def test_track_palette_distinct(self):
        palette = _track_palette(6)
        assert len(palette) == 6
        # All distinct
        assert len(set(palette)) == 6
        # Each in valid 0-255 range
        for r, g, b in palette:
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255

    def test_track_palette_empty(self):
        assert _track_palette(0) == []

    def test_scale_color_clamps(self):
        assert _scale_color((100, 100, 100), 3.0) == (255, 255, 255)
        assert _scale_color((100, 100, 100), 0.0) == (0, 0, 0)
        assert _scale_color((100, 100, 100), -1.0) == (0, 0, 0)


# ─── Frame buffer ────────────────────────────────────────────────────
class TestFrame:
    def test_initial_blank(self):
        f = Frame(5, 3)
        # 3 rows of 5 spaces, separated by newlines, with leading reset
        out = f.render()
        assert out.count("\n") == 2
        # Each row starts with reset, all spaces, ends with reset
        for line in out.split("\n"):
            assert "\x1b[0m" in line
            assert "     " in line

    def test_put_in_bounds(self):
        f = Frame(3, 2)
        f.put(0, 0, "X", (255, 0, 0))
        out = f.render()
        assert "X" in out
        assert "\x1b[38;2;255;0;0m" in out

    def test_put_out_of_bounds_silently_ignored(self):
        f = Frame(3, 2)
        f.put(-1, 0, "X")
        f.put(0, -1, "X")
        f.put(99, 0, "X")
        f.put(0, 99, "X")
        # Renders without crashing, no X appears
        assert "X" not in f.render()

    def test_text_writes_string(self):
        f = Frame(10, 1)
        f.text(2, 0, "hello", (10, 20, 30))
        out = f.render()
        assert "hello" in out
        # Color emitted once for the run, not 5 times
        assert out.count("\x1b[38;2;10;20;30m") == 1

    def test_text_clips_at_right(self):
        f = Frame(5, 1)
        f.text(3, 0, "hello", (10, 20, 30))
        # Only "he" fits at columns 3,4
        out = f.render()
        assert "he" in out
        assert "llo" not in out

    def test_hline(self):
        f = Frame(8, 1)
        f.hline(1, 0, 5, "─", (50, 50, 50))
        out = f.render()
        assert "─────" in out

    def test_color_change_emits_new_escape(self):
        f = Frame(3, 1)
        f.put(0, 0, "A", (255, 0, 0))
        f.put(1, 0, "B", (0, 255, 0))
        f.put(2, 0, "C", (255, 0, 0))
        out = f.render()
        # Both colors should appear
        assert "\x1b[38;2;255;0;0m" in out
        assert "\x1b[38;2;0;255;0m" in out

    def test_render_does_not_crash_on_empty(self):
        f = Frame(1, 1)
        assert isinstance(f.render(), str)


# ─── Bar character helpers ───────────────────────────────────────────
class TestBars:
    def test_vu_chars_zero(self):
        assert _vu_chars(0.0, 6) == " " * 6

    def test_vu_chars_full(self):
        assert _vu_chars(1.0, 6) == "█" * 6

    def test_vu_chars_clamp(self):
        # Out-of-range input is clamped, not crashed
        assert _vu_chars(2.0, 4) == "█" * 4
        assert _vu_chars(-1.0, 4) == "    "

    def test_vu_chars_partial_ends_with_block(self):
        bar = _vu_chars(0.5, 6)
        assert len(bar) == 6
        assert "█" in bar or "▆" in bar or "▅" in bar

    def test_vbar_char_levels(self):
        assert _vbar_char(0.0) == " "
        assert _vbar_char(1.0) == "█"
        # Monotonically non-decreasing
        prev = -1
        for level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            ch = _vbar_char(level)
            idx = " ▁▂▃▄▅▆▇█".index(ch)
            assert idx >= prev
            prev = idx


# ─── Time formatter ──────────────────────────────────────────────────
class TestFormatTime:
    def test_seconds(self):
        assert _format_time(7.5) == "0:07.5"

    def test_minutes(self):
        assert _format_time(75.0) == "1:15.0"

    def test_negative_clamps(self):
        assert _format_time(-1.0) == "0:00.0"

    def test_zero(self):
        assert _format_time(0.0) == "0:00.0"


# ─── Chord label ─────────────────────────────────────────────────────
class TestChordLabel:
    def test_string_shape(self):
        assert _format_chord_label("C", "min7") == "Cmin7"

    def test_list_shape(self):
        assert _format_chord_label("A", [0, 4, 7]) == "A*"


# ─── Timeline extraction ─────────────────────────────────────────────
class TestBuildTimeline:
    def test_single_track_notes(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        timelines, total = _build_timeline(song)
        assert len(timelines) == 1
        assert len(timelines[0]) == 3
        # 1 beat at 120 BPM = 0.5s
        assert timelines[0][0].start == 0.0
        assert abs(timelines[0][0].end - 0.5) < 1e-6
        assert timelines[0][1].start == 0.5
        assert timelines[0][2].label == "G4"
        assert total >= 1.5

    def test_chord_labels(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="pad"))
        tr.add(Chord("A", "min7", 4, duration=2.0))
        timelines, _ = _build_timeline(song)
        onset = timelines[0][0]
        assert onset.label == "Amin7"
        # Chord onsets now expand to the full pitch list (Amin7 = A C E G)
        assert sorted(pc % 12 for pc in onset.midis) == sorted([9, 0, 4, 7])
        # The single `midi` field gets the root for chord-aware display
        assert onset.midi == 69

    def test_rests_skipped_but_advance_time(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.add(Note("C", 4, 1.0))
        tr.add(Note.rest(2.0))
        tr.add(Note("E", 4, 1.0))
        timelines, _ = _build_timeline(song)
        # Two real notes; rest skipped
        assert len(timelines[0]) == 2
        # Second note should land at beat 3 = 1.5s at 120 BPM
        assert abs(timelines[0][1].start - 1.5) < 1e-6

    def test_multi_track(self):
        song = Song(title="t", bpm=120)
        tr1 = song.add_track(Track(name="a", instrument="sine"))
        tr2 = song.add_track(Track(name="b", instrument="square"))
        tr1.add(Note("C", 4, 1.0))
        tr2.add(Note("G", 4, 1.0))
        timelines, _ = _build_timeline(song)
        assert len(timelines) == 2
        assert timelines[0][0].track_idx == 0
        assert timelines[1][0].track_idx == 1


# ─── Spectrum precomputation ─────────────────────────────────────────
class TestSpectrum:
    def test_zero_audio(self):
        samples = np.zeros((22050, 2), dtype=np.float64)
        spec = _precompute_spectrum(samples, 22050, n_bands=8)
        assert spec.shape[1] == 8
        # All zero in / all zero out (after normalization, max is 0 → kept 0)
        assert spec.max() == 0.0

    def test_mono_audio(self):
        samples = np.random.randn(22050).astype(np.float64) * 0.1
        spec = _precompute_spectrum(samples, 22050, n_bands=12)
        assert spec.shape[1] == 12
        assert spec.shape[0] >= 1

    def test_stereo_audio(self):
        samples = np.random.randn(22050, 2).astype(np.float64) * 0.1
        spec = _precompute_spectrum(samples, 22050, n_bands=12)
        assert spec.shape[1] == 12

    def test_spectrum_normalized(self):
        # White noise should have all bands populated
        np.random.seed(42)
        samples = np.random.randn(44100, 2).astype(np.float64) * 0.5
        spec = _precompute_spectrum(samples, 44100, n_bands=12)
        assert (spec <= 1.0).all()
        assert (spec >= 0.0).all()
        # Each band column should reach a meaningful level somewhere
        assert spec.max(axis=0).min() > 0.3


# ─── Frame builder ───────────────────────────────────────────────────
class TestBuildFrame:
    def _state(self, song, w=80, h=20):
        timelines, total = _build_timeline(song)
        palette = _track_palette(len(song.tracks))
        spectrum = np.zeros((10, 12), dtype=np.float32)
        midi_lo, midi_hi = _midi_range_from_timelines(timelines)
        return _State(
            song=song,
            timelines=timelines,
            palette=palette,
            spectrum=spectrum,
            spectrum_hop=0.05,
            total_dur=total,
            width=w,
            height=h,
            midi_lo=midi_lo,
            midi_hi=midi_hi,
        )

    def test_renders_full_frame(self):
        song = Song(title="Demo", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0)])
        state = self._state(song)
        frame = _build_frame(state, t_now=0.0, anim_phase=0.0)
        out = frame.render()
        plain = _strip_ansi(out)
        # Title is per-char colored in the animated header but appears
        # contiguous once ANSI codes are stripped.
        assert "Demo" in plain
        # BPM and box-drawing borders are present
        assert "120 BPM" in plain
        assert "╭" in out and "╮" in out and "╰" in out and "╯" in out

    def test_title_too_long_truncates(self):
        song = Song(title="A" * 200, bpm=120)
        song.add_track(Track(name="x", instrument="sine"))
        state = self._state(song, w=80, h=20)
        frame = _build_frame(state, t_now=0.0, anim_phase=0.0)
        # Render does not crash and respects the width budget
        out = frame.render()
        # Each visible row, after stripping ANSI, should be <= width
        for line in _strip_ansi(out).split("\n"):
            assert len(line) <= 80

    def test_now_line_marker_when_idle(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        # Single note at beat 0 with duration 1 → 0..0.5s
        tr.add(Note("C", 4, 1.0))
        state = self._state(song)
        # At t=10s the song is over, no active note, expect "│" idle marker
        frame = _build_frame(state, t_now=10.0, anim_phase=0.0)
        out = frame.render()
        assert "│" in out

    def test_active_note_label_appears(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.add(Note("F#", 5, 4.0))  # 2 seconds at 120 BPM
        state = self._state(song)
        frame = _build_frame(state, t_now=0.5, anim_phase=0.0)
        plain = _strip_ansi(frame.render())
        # Active marker + label
        assert "▶" in plain
        assert "F#5" in plain

    def test_chord_readout_appears_in_header(self):
        # Three tracks playing C, E, G simultaneously → "C" chord label
        song = Song(title="t", bpm=120)
        for pitch in ("C", "E", "G"):
            tr = song.add_track(Track(name=pitch, instrument="sine"))
            tr.add(Note(pitch, 4, 4.0))
        state = self._state(song)
        plain = _strip_ansi(_build_frame(state, t_now=0.5, anim_phase=0.0).render())
        # Chord readout uses the ♪ marker
        assert "♪ C" in plain

    def test_progress_bar_advances(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.extend([Note("C", 4, 1.0)] * 16)
        state = self._state(song)
        frame_start = _build_frame(state, t_now=0.0, anim_phase=0.0)
        frame_mid = _build_frame(state, t_now=state.total_dur * 0.5, anim_phase=0.0)
        # Mid-song frame contains a higher-percentage indicator
        out_start = _strip_ansi(frame_start.render())
        out_mid = _strip_ansi(frame_mid.render())
        assert "  0%" in out_start or " 0%" in out_start
        assert "50%" in out_mid or "49%" in out_mid or "51%" in out_mid


def _strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences for length-checking visible content."""
    import re

    return re.sub(r"\x1b\[[0-9;]*m", "", s)


# ─── Sheet music staff helpers ───────────────────────────────────────
class TestStaffHelpers:
    def test_midi_range_with_pitches(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.extend([Note("C", 4, 1.0), Note("G", 5, 1.0)])  # midi 60, 79
        timelines, _ = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        # Padded by 1 on each side
        assert lo == 59 and hi == 80

    def test_midi_range_empty_falls_back_to_default(self):
        # Empty timeline → default C4..C5 range
        lo, hi = _midi_range_from_timelines([])
        assert lo == 60 and hi == 72

    def test_midi_range_uses_chord_pitches(self):
        # Chord onsets now expand to their member pitches, so the staff
        # range reflects the actual chord voicing rather than defaulting.
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="pad"))
        tr.add(Chord("C", "maj", 4, duration=2.0))
        timelines, _ = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        # Range should be padded around the chord's actual pitches
        assert hi > lo
        # Range should be near octave 4 territory (well under MIDI 100)
        assert 30 < lo < 80
        assert 30 < hi < 90

    def test_midi_range_single_pitch_widens(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(instrument="sine"))
        tr.extend([Note("A", 4, 1.0)] * 4)  # all midi 69
        timelines, _ = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        # Single pitch should still produce a usable range, not lo == hi
        assert hi > lo
        assert lo <= 69 <= hi

    def test_staff_row_high_note_top(self):
        # midi=80 with range 60..80 should map to row 0 (top)
        assert _staff_row(80, 60, 80, n_rows=7) == 0

    def test_staff_row_low_note_bottom(self):
        assert _staff_row(60, 60, 80, n_rows=7) == 6

    def test_staff_row_middle(self):
        # midi=70 with range 60..80 = halfway → middle row
        row = _staff_row(70, 60, 80, n_rows=7)
        assert row == 3

    def test_staff_row_clamps_out_of_range(self):
        # MIDI outside the declared range should clamp, not crash
        assert _staff_row(120, 60, 80, n_rows=7) == 0
        assert _staff_row(0, 60, 80, n_rows=7) == 6

    def test_staff_row_zero_range(self):
        # Equal lo and hi defaults to middle
        assert _staff_row(60, 60, 60, n_rows=7) == 3

    def test_note_rhythm_whole(self):
        head, stem, flags = _note_rhythm(4.0)
        # Whole note: open head, no stem, no flag
        assert head == "○" and stem == 0 and flags == 0

    def test_note_rhythm_half(self):
        head, stem, flags = _note_rhythm(2.0)
        # Half note: open head, stem, no flag
        assert head == "○" and stem > 0 and flags == 0

    def test_note_rhythm_quarter(self):
        head, stem, flags = _note_rhythm(1.0)
        # Quarter: filled head, stem, no flag
        assert head == "●" and stem > 0 and flags == 0

    def test_note_rhythm_eighth(self):
        head, stem, flags = _note_rhythm(0.5)
        # Eighth: filled head, stem, single flag
        assert head == "●" and stem > 0 and flags == 1

    def test_note_rhythm_sixteenth(self):
        head, stem, flags = _note_rhythm(0.25)
        # Sixteenth: filled head, stem, double flag
        assert head == "●" and stem > 0 and flags == 2


class TestDrawNoteWithStem:
    def test_quarter_renders_filled_head_and_stem(self):
        frame = Frame(20, 10)
        # head_y=5, mid_line=4 → head_y > mid_line → stem up (above head)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=1.0,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        # Filled head present
        assert "●" in plain
        # Stem cells above the head
        assert "│" in plain

    def test_half_renders_open_head_and_stem(self):
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=2.0,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        assert "○" in plain
        assert "│" in plain

    def test_whole_has_no_stem(self):
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=4.0,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        assert "○" in plain
        assert "│" not in plain  # no stem cells

    def test_eighth_has_flag_at_stem_tip(self):
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=0.5,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        # Eighth: filled head + stem + one flag char
        assert "●" in plain
        # Flag glyph for stem-up eighth
        assert "┐" in plain

    def test_sixteenth_has_double_flag(self):
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=0.25,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        # Sixteenth-or-shorter: heavier double-flag glyph
        assert "╗" in plain

    def test_high_note_stems_down(self):
        # head above middle line → stem points DOWN (below head)
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=2,
            duration_beats=1.0,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=0,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        rows = plain.split("\n")
        # Note head is at row 2, stems should be at rows 3 and 4 (below)
        assert "●" in rows[2]
        assert "│" in rows[3] or "│" in rows[4]
        # No stem above the head
        assert "│" not in rows[0]
        assert "│" not in rows[1]

    def test_stems_clipped_to_panel(self):
        # If panel_top is set higher than the would-be stem rows, stems
        # should be clipped — they must not bleed into adjacent panels.
        frame = Frame(20, 10)
        _draw_note_with_stem(
            frame,
            x=5,
            head_y=5,
            duration_beats=1.0,
            color=(200, 200, 200),
            mid_line_y=4,
            panel_top=5,
            panel_bottom=9,
        )
        plain = _strip_ansi(frame.render())
        # Head at row 5 only; stem cells (rows 3, 4) clipped
        rows = plain.split("\n")
        assert "●" in rows[5]
        # rows above panel_top (0..4) should be untouched by stems
        for r in rows[0:5]:
            assert "│" not in r


class TestChordIdentification:
    def test_empty_returns_empty_string(self):
        assert _identify_chord([]) == ""

    def test_single_note_returns_pitch_class(self):
        # Just MIDI 60 = C
        assert _identify_chord([60]) == "C"
        # Multiple Cs across octaves still collapse to "C"
        assert _identify_chord([60, 72, 48]) == "C"

    def test_major_triad(self):
        # C E G — across whatever octaves
        assert _identify_chord([60, 64, 67]) == "C"
        assert _identify_chord([72, 76, 79]) == "C"

    def test_minor_triad(self):
        # A C E
        assert _identify_chord([69, 72, 76]) == "Amin"

    def test_min7_chord(self):
        # A C E G
        result = _identify_chord([69, 72, 76, 79])
        assert result == "Amin7"

    def test_maj7_chord(self):
        # C E G B
        result = _identify_chord([60, 64, 67, 71])
        assert result == "Cmaj7"

    def test_dom7_chord(self):
        # G B D F
        result = _identify_chord([67, 71, 74, 77])
        assert result == "Gdom7"

    def test_random_cluster_falls_back_to_pitch_classes(self):
        # C C# D — no chord shape matches, expect spelled-out pitches
        result = _identify_chord([60, 61, 62])
        assert "C" in result
        assert "C#" in result
        assert "D" in result

    def test_triad_preferred_over_extended(self):
        # C E G — could match "maj" or "maj7" if interpreted lazily;
        # we want the simpler shape
        assert _identify_chord([60, 64, 67]) == "C"


class TestCurrentlySoundingMidis:
    def test_collects_active_notes(self):
        timelines = [
            [_Onset(0, 0.0, 1.0, "C4", 60, 0.8)],
            [_Onset(1, 0.5, 1.5, "E4", 64, 0.8)],
        ]
        # At t=0.7s both notes are active
        result = sorted(_currently_sounding_midis(timelines, 0.7))
        assert result == [60, 64]

    def test_excludes_finished_notes(self):
        timelines = [[_Onset(0, 0.0, 0.5, "C4", 60, 0.8)]]
        assert _currently_sounding_midis(timelines, 1.0) == []

    def test_excludes_chords_without_midi(self):
        timelines = [[_Onset(0, 0.0, 2.0, "Cmaj", None, 0.8)]]
        assert _currently_sounding_midis(timelines, 1.0) == []


class TestSparkleAtNow:
    def test_recent_onset_returns_sparkle(self):
        onsets = [_Onset(0, 0.0, 1.0, "C4", 60, 0.8)]
        result = _sparkle_at_now(onsets, t_now=0.05)
        assert result is not None
        glyph, intensity = result
        assert glyph in ("✦", "✧", "·")
        assert 0.0 < intensity <= 1.0

    def test_no_recent_onset_returns_none(self):
        onsets = [_Onset(0, 0.0, 1.0, "C4", 60, 0.8)]
        # 1.0s after onset, well past the 0.22s sparkle window
        assert _sparkle_at_now(onsets, t_now=1.0) is None

    def test_intensity_decays(self):
        onsets = [_Onset(0, 0.0, 1.0, "C4", 60, 0.8)]
        early = _sparkle_at_now(onsets, t_now=0.02)
        late = _sparkle_at_now(onsets, t_now=0.20)
        assert early is not None and late is not None
        assert early[1] > late[1]

    def test_picks_freshest_onset(self):
        # Two onsets, the more recent should win
        onsets = [
            _Onset(0, 0.00, 1.0, "C4", 60, 0.8),
            _Onset(0, 0.15, 1.0, "E4", 64, 0.8),
        ]
        result = _sparkle_at_now(onsets, t_now=0.18)
        assert result is not None
        # The 0.15s onset (age=0.03) is fresher than 0.00s (age=0.18)
        # so intensity should reflect the fresher hit
        assert result[1] > 0.7


class TestStaffPanel:
    def test_staff_renders_lines_and_clef(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])
        timelines, total = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        state = _State(
            song=song,
            timelines=timelines,
            palette=_track_palette(1),
            spectrum=np.zeros((10, 12), dtype=np.float32),
            spectrum_hop=0.05,
            total_dur=total,
            width=80,
            height=20,
            midi_lo=lo,
            midi_hi=hi,
        )
        frame = Frame(80, 10)
        _draw_staff_panel(frame, state, t_now=0.0, y0=1, panel_h=7, anim_phase=0.0)
        plain = _strip_ansi(frame.render())
        # Five staff lines means at least 5 rows contain horizontal lines
        line_rows = [row for row in plain.split("\n") if "─" in row]
        assert len(line_rows) >= 5
        # Clef glyph should be present
        assert "&" in plain

    def test_staff_renders_notes(self):
        song = Song(title="t", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.add(Note("C", 4, 1.0))  # 1 beat -> quarter glyph
        timelines, total = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        state = _State(
            song=song,
            timelines=timelines,
            palette=_track_palette(1),
            spectrum=np.zeros((10, 12), dtype=np.float32),
            spectrum_hop=0.05,
            total_dur=total,
            width=80,
            height=20,
            midi_lo=lo,
            midi_hi=hi,
        )
        frame = Frame(80, 10)
        _draw_staff_panel(frame, state, t_now=0.0, y0=1, panel_h=7, anim_phase=0.0)
        plain = _strip_ansi(frame.render())
        # The note glyph should be present
        assert "●" in plain

    def test_staff_skips_when_panel_too_short(self):
        # If panel_h < _STAFF_HEIGHT we should bail without crashing
        song = Song(title="t", bpm=120)
        song.add_track(Track(instrument="sine")).add(Note("C", 4, 1.0))
        timelines, total = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        state = _State(
            song=song,
            timelines=timelines,
            palette=_track_palette(1),
            spectrum=np.zeros((10, 12), dtype=np.float32),
            spectrum_hop=0.05,
            total_dur=total,
            width=80,
            height=10,
            midi_lo=lo,
            midi_hi=hi,
        )
        frame = Frame(80, 5)
        _draw_staff_panel(frame, state, t_now=0.0, y0=0, panel_h=3, anim_phase=0.0)
        plain = _strip_ansi(frame.render())
        # No staff content drawn into a too-short panel
        assert "─" not in plain
        assert "&" not in plain

    def test_staff_appears_in_full_frame_when_room(self):
        song = Song(title="Demo", bpm=120)
        tr = song.add_track(Track(name="lead", instrument="sine"))
        tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0)])
        timelines, total = _build_timeline(song)
        lo, hi = _midi_range_from_timelines(timelines)
        state = _State(
            song=song,
            timelines=timelines,
            palette=_track_palette(1),
            spectrum=np.zeros((10, 12), dtype=np.float32),
            spectrum_hop=0.05,
            total_dur=total,
            width=80,
            height=30,
            midi_lo=lo,
            midi_hi=hi,
        )
        plain = _strip_ansi(_build_frame(state, t_now=0.0, anim_phase=0.0).render())
        assert "sheet music" in plain


# ─── play_visual entry point ─────────────────────────────────────────
class TestPlayVisual:
    def test_no_color_fallback_runs_quietly(self, monkeypatch, capsys):
        # Without a TTY, play_visual should fall back to plain audio playback
        monkeypatch.setattr(
            "code_music.synth.Synth.render_song",
            lambda self, song: np.zeros((22050, 2), dtype=np.float64),
        )
        monkeypatch.setattr("code_music.visualizer._supports_color", lambda: False)
        monkeypatch.setattr("code_music.playback._has_sounddevice", lambda: False)
        monkeypatch.setattr("code_music.playback._play_fallback", lambda *a, **kw: None)

        song = Song(title="Quiet", bpm=120, sample_rate=22050)
        song.add_track(Track(instrument="sine")).add(Note("C", 4, 1.0))
        play_visual(song)
        captured = capsys.readouterr()
        assert "Rendering" in captured.out

    def test_bpm_override(self, monkeypatch):
        monkeypatch.setattr(
            "code_music.synth.Synth.render_song",
            lambda self, song: np.zeros((22050, 2), dtype=np.float64),
        )
        monkeypatch.setattr("code_music.visualizer._supports_color", lambda: False)
        monkeypatch.setattr("code_music.playback._has_sounddevice", lambda: False)
        monkeypatch.setattr("code_music.playback._play_fallback", lambda *a, **kw: None)

        song = Song(title="t", bpm=120, sample_rate=22050)
        song.add_track(Track(instrument="sine")).add(Note("C", 4, 1.0))
        play_visual(song, bpm=90)
        assert song.bpm == 90

    def test_supports_color_respects_no_color_env(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert _supports_color() is False
