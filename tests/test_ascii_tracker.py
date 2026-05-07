"""Tests for code_music.ascii_tracker."""

from __future__ import annotations

import pytest

from code_music import AsciiTracker, Cell, tracker
from code_music.ascii_tracker import _format_cell, _parse_cell, _parse_velocity
from code_music.engine import Note

# ---------------------------------------------------------------------------
# _parse_cell
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("token", ["~", "-", "...", "..", ".", "", " "])
def test_parse_cell_rest_tokens_produce_rest(token: str) -> None:
    cell = _parse_cell(token)
    assert cell.is_rest


def test_parse_cell_single_note() -> None:
    cell = _parse_cell("C2")
    assert not cell.is_rest
    assert len(cell.notes) == 1
    assert cell.notes[0].pitch == "C"
    assert cell.notes[0].octave == 2


def test_parse_cell_sharp_and_flat() -> None:
    sharp = _parse_cell("F#3").notes[0]
    flat = _parse_cell("Bb4").notes[0]
    assert sharp.pitch == "F#" and sharp.octave == 3
    assert flat.pitch == "Bb" and flat.octave == 4


def test_parse_cell_chord() -> None:
    cell = _parse_cell("C2,E2,G2")
    assert len(cell.notes) == 3
    assert [n.pitch for n in cell.notes] == ["C", "E", "G"]
    assert all(n.octave == 2 for n in cell.notes)


def test_parse_cell_velocity_midi_scale() -> None:
    cell = _parse_cell("C5:80")
    assert cell.notes[0].velocity == pytest.approx(80 / 127, abs=1e-3)


def test_parse_cell_velocity_fraction() -> None:
    cell = _parse_cell("C5:0.6")
    assert cell.notes[0].velocity == pytest.approx(0.6, abs=1e-6)


def test_parse_cell_default_velocity() -> None:
    cell = _parse_cell("C5")
    assert cell.notes[0].velocity == pytest.approx(0.8, abs=1e-6)


def test_parse_cell_invalid_token_raises() -> None:
    with pytest.raises(ValueError):
        _parse_cell("nope")


def test_parse_velocity_clamps_above_one_through_midi_scale() -> None:
    # 200 / 127 > 1 -> clamped to 1.0
    assert _parse_velocity("200") == 1.0


def test_parse_velocity_negative_clamps_to_zero() -> None:
    assert _parse_velocity("-0.5") == 0.0


# ---------------------------------------------------------------------------
# AsciiTracker.from_string
# ---------------------------------------------------------------------------


SAMPLE_GRID = """
     KICK SNARE HAT  BASS
00 | C2   ...   C5   F1
01 | ...  ...   ...  ...
02 | ...  D2    C5   ...
03 | ...  ...   C5   ...
04 | C2   ...   C5   F1
05 | ...  ...   ...  D5
06 | ...  D2    C5   ...
07 | ...  ...   C5   Eb5
"""


def test_from_string_columns_and_steps() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    assert t.column_names == ["KICK", "SNARE", "HAT", "BASS"]
    assert t.num_steps == 8
    assert t.num_voices == 4


def test_from_string_skips_blank_lines_and_comments() -> None:
    grid = """
    # this is a comment
         KICK
    # another comment
    00 | C2

    01 | ...
    """
    t = AsciiTracker.from_string(grid)
    assert t.column_names == ["KICK"]
    assert t.num_steps == 2


def test_from_string_without_step_index() -> None:
    grid = """
     KICK BASS
     C2   F1
     ...  ...
     C2   F1
    """
    t = AsciiTracker.from_string(grid)
    assert t.num_steps == 3
    assert t.cells_for("BASS")[0].notes[0].pitch == "F"


def test_from_string_row_with_wrong_cell_count_raises() -> None:
    bad_grid = """
         KICK SNARE HAT
    00 | C2   ...
    """
    with pytest.raises(ValueError, match="cells"):
        AsciiTracker.from_string(bad_grid)


def test_from_string_empty_grid_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        AsciiTracker.from_string("\n  \n  \n")


def test_from_string_header_only_raises() -> None:
    with pytest.raises(ValueError, match="cells"):
        AsciiTracker.from_string("KICK\nC2 D2")


# ---------------------------------------------------------------------------
# cells_for + tracker() helper
# ---------------------------------------------------------------------------


def test_cells_for_unknown_column_raises() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    with pytest.raises(KeyError):
        t.cells_for("MISSING")


def test_tracker_helper_is_alias() -> None:
    a = tracker(SAMPLE_GRID)
    b = AsciiTracker.from_string(SAMPLE_GRID)
    assert a.column_names == b.column_names
    assert a.num_steps == b.num_steps


# ---------------------------------------------------------------------------
# to_patterns
# ---------------------------------------------------------------------------


def test_to_patterns_returns_one_per_voice() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    pats = t.to_patterns()
    assert set(pats.keys()) == {"KICK", "SNARE", "HAT", "BASS"}
    assert all(len(p) == t.num_steps for p in pats.values())


def test_to_patterns_collapses_chord_to_lowest_note() -> None:
    t = AsciiTracker.from_string(
        """
             PAD
        00 | C3,E3,G3
        01 | ...
        """
    )
    pats = t.to_patterns()
    events = pats["PAD"].events
    assert events[0] == "C3"
    assert events[1] is None


# ---------------------------------------------------------------------------
# to_song
# ---------------------------------------------------------------------------


def test_to_song_creates_one_polytrack_per_voice() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    song = t.to_song(bpm=128)
    assert song.bpm == 128
    assert len(song.poly_tracks) == 4
    assert [tr.name for tr in song.poly_tracks] == ["KICK", "SNARE", "HAT", "BASS"]


def test_to_song_assigns_instruments_from_dict() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    song = t.to_song(
        bpm=128,
        instruments={
            "KICK": "drums_kick",
            "SNARE": "drums_snare",
            "HAT": "drums_hat",
            "BASS": "bass",
        },
    )
    by_name = {tr.name: tr for tr in song.poly_tracks}
    assert by_name["KICK"].instrument == "drums_kick"
    assert by_name["BASS"].instrument == "bass"


def test_to_song_unknown_column_falls_back_to_pad() -> None:
    t = AsciiTracker.from_string(SAMPLE_GRID)
    song = t.to_song(bpm=120)  # no instruments dict
    for tr in song.poly_tracks:
        assert tr.instrument == "pad"


def test_to_song_step_duration_controls_event_timing() -> None:
    t = AsciiTracker.from_string(
        """
             KICK
        00 | C2
        01 | ...
        02 | C2
        """
    )
    song = t.to_song(bpm=120, step_duration=0.5)
    kick = song.poly_tracks[0]
    starts = [at for _, at in kick.events]
    assert starts == [0.0, 1.0]


def test_to_song_chord_cell_emits_simultaneous_notes() -> None:
    t = AsciiTracker.from_string(
        """
             PAD
        00 | C3,E3,G3
        """
    )
    song = t.to_song(bpm=120)
    pad = song.poly_tracks[0]
    assert len(pad.events) == 3
    assert all(at == 0.0 for _, at in pad.events)
    pitches = sorted(n.pitch for n, _ in pad.events)
    assert pitches == ["C", "E", "G"]


# ---------------------------------------------------------------------------
# to_string round-trip
# ---------------------------------------------------------------------------


def test_to_string_round_trip_preserves_columns_and_steps() -> None:
    original = AsciiTracker.from_string(SAMPLE_GRID)
    serialised = original.to_string()
    reparsed = AsciiTracker.from_string(serialised)
    assert original.column_names == reparsed.column_names
    assert original.num_steps == reparsed.num_steps


def test_to_string_round_trip_preserves_chords() -> None:
    original = AsciiTracker.from_string(
        """
             PAD
        00 | C3,E3,G3
        01 | F3,A3,C4
        """
    )
    reparsed = AsciiTracker.from_string(original.to_string())
    pad_original = original.cells_for("PAD")
    pad_reparsed = reparsed.cells_for("PAD")
    for a, b in zip(pad_original, pad_reparsed):
        assert [(n.pitch, n.octave) for n in a.notes] == [(n.pitch, n.octave) for n in b.notes]


def test_format_cell_default_velocity_omits_suffix() -> None:
    cell = Cell(notes=(Note(pitch="C", octave=4),))
    assert _format_cell(cell) == "C4"


def test_format_cell_non_default_velocity_includes_midi_suffix() -> None:
    cell = Cell(notes=(Note(pitch="C", octave=4, velocity=0.5),))
    text = _format_cell(cell)
    assert text.startswith("C4:")
    assert text.split(":")[1] == "64"  # 0.5 * 127 rounds to 64
