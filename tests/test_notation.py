"""Tests for notation exporters: LilyPond, ABC, MusicXML."""

import tempfile
from pathlib import Path

import pytest

from code_music.engine import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    SIXTEENTH,
    THIRTY_SECOND,
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    doit,
    fall,
    flip,
    grace_note,
    mordent,
    shake,
    trill,
    triplet,
    triplets,
    tuplet,
    tuplets,
    turn,
    upper_mordent,
)
from code_music.notation import export_abc, export_lilypond, export_musicxml

# ---------------------------------------------------------------------------
# Duration constants
# ---------------------------------------------------------------------------


class TestDurationConstants:
    def test_whole_is_four_beats(self):
        assert WHOLE == 4.0

    def test_half_is_two_beats(self):
        assert HALF == 2.0

    def test_quarter_is_one_beat(self):
        assert QUARTER == 1.0

    def test_eighth_is_half_beat(self):
        assert EIGHTH == 0.5

    def test_sixteenth(self):
        assert SIXTEENTH == 0.25

    def test_thirty_second(self):
        assert THIRTY_SECOND == 0.125

    def test_dotted_quarter(self):
        assert DOTTED_QUARTER == 1.5

    def test_durations_halve_each_step(self):
        assert HALF == WHOLE / 2
        assert QUARTER == HALF / 2
        assert EIGHTH == QUARTER / 2
        assert SIXTEENTH == EIGHTH / 2
        assert THIRTY_SECOND == SIXTEENTH / 2


# ---------------------------------------------------------------------------
# Tuplet helpers
# ---------------------------------------------------------------------------


class TestTuplets:
    def test_triplet_quarter(self):
        # triplet(QUARTER): 3 notes fill 2 quarter notes → each = 2/3 of a quarter
        assert abs(triplet(QUARTER) - 2 / 3) < 0.001

    def test_triplet_eighth(self):
        # triplet(EIGHTH): 3 notes fill 2 eighth notes → each = 1/3 of a quarter
        assert abs(triplet(EIGHTH) - 1 / 3) < 0.001

    def test_tuplet_quintuplet(self):
        assert abs(tuplet(QUARTER, 5) - 0.2) < 0.001

    def test_tuplet_sextuplet(self):
        assert abs(tuplet(QUARTER, 6) - 1 / 6) < 0.001

    def test_triplets_list_length(self):
        result = triplets(["C", "E", "G"], octave=4)
        assert len(result) == 3
        assert all(abs(n.duration - triplet(QUARTER)) < 0.001 for n in result)

    def test_triplets_rest(self):
        result = triplets(["C", None, "G"])
        assert result[1].pitch is None  # None → rest

    def test_tuplets_quintuplet(self):
        result = tuplets(["C", "D", "E", "F", "G"], n=5)
        assert len(result) == 5
        assert all(abs(n.duration - tuplet(QUARTER, 5)) < 0.001 for n in result)

    def test_tuplets_custom_base(self):
        result = tuplets(["C", "D", "E"], n=3, base=HALF)
        expected_dur = tuplet(HALF, 3)
        assert all(abs(n.duration - expected_dur) < 0.001 for n in result)


# ---------------------------------------------------------------------------
# Ornaments
# ---------------------------------------------------------------------------


class TestOrnaments:
    def _note(self, pitch="A", octave=4, dur=QUARTER):
        return Note(pitch, octave, dur)

    def test_trill_note_count(self):
        result = trill(self._note(), count=8)
        assert len(result) == 8

    def test_trill_alternates_pitches(self):
        n = self._note("C", 4)
        result = trill(n, semitones=1, count=4)
        pitches = [r.midi for r in result]
        assert pitches[0] != pitches[1]  # alternates
        assert pitches[0] == pitches[2]  # back to original

    def test_trill_rest_passthrough(self):
        result = trill(Note.rest(QUARTER))
        assert len(result) == 1
        assert result[0].pitch is None

    def test_mordent_three_notes(self):
        result = mordent(self._note())
        assert len(result) == 3
        base = result[0].midi
        assert result[1].midi < base  # lower
        assert result[2].midi == base  # back

    def test_upper_mordent_three_notes(self):
        result = upper_mordent(self._note())
        assert len(result) == 3
        base = result[0].midi
        assert result[1].midi > base  # upper
        assert result[2].midi == base  # back

    def test_turn_four_notes(self):
        result = turn(self._note())
        assert len(result) == 4
        base = result[1].midi
        assert result[0].midi > base  # upper
        assert result[2].midi < base  # lower
        assert result[3].midi == base  # back to principal

    def test_grace_note_two_notes(self):
        main = self._note("C", 5, QUARTER)
        result = grace_note("B", main, grace_octave=4)
        assert len(result) == 2
        # Grace note steals time from main
        assert result[0].duration + result[1].duration == pytest.approx(QUARTER)

    def test_doit_rises(self):
        n = Note("C", 4, QUARTER)
        result = doit(n, semitones=2, steps=4)
        assert len(result) == 5  # main + 4 steps
        main_midi = result[0].midi
        assert result[-1].midi > main_midi  # last step is higher

    def test_fall_drops(self):
        n = Note("G", 5, QUARTER)
        result = fall(n, semitones=3, steps=4)
        assert len(result) == 5
        main_midi = result[0].midi
        assert result[-1].midi < main_midi  # falls down

    def test_flip_scoops_up(self):
        n = Note("D", 5, QUARTER)
        result = flip(n, semitones=2)
        # v170: flip now uses 6 micro-steps + final note for smooth scoop
        assert len(result) >= 3
        # Last note is the target pitch
        assert result[-1].midi == n.midi

    def test_shake_is_trill(self):
        n = Note("Bb", 4, HALF)
        result = shake(n, semitones=2, count=4)
        assert len(result) == 4

    def test_ornament_rest_passthrough(self):
        rest = Note.rest(QUARTER)
        for fn in (mordent, upper_mordent, turn, doit, fall, flip):
            result = fn(rest)
            assert result[0].pitch is None


# ---------------------------------------------------------------------------
# LilyPond export
# ---------------------------------------------------------------------------


class TestLilyPond:
    def _simple_song(self):
        song = Song(title="Test", bpm=120)
        tr = song.add_track(Track(name="piano", instrument="piano"))
        tr.extend(
            [
                Note("C", 4, QUARTER),
                Note("E", 4, QUARTER),
                Note("G", 4, QUARTER),
                Note("C", 5, QUARTER),
            ]
        )
        return song

    def test_file_created(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_lilypond(song, Path(tmp) / "test.ly")
            assert out.exists()
            assert out.suffix == ".ly"

    def test_contains_version(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_lilypond(song, Path(tmp) / "test.ly")
            text = out.read_text()
            assert r"\version" in text

    def test_contains_title(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_lilypond(song, Path(tmp) / "test.ly")
            assert "Test" in out.read_text()

    def test_contains_tempo(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_lilypond(song, Path(tmp) / "test.ly")
            assert "120" in out.read_text()

    def test_time_signature_44(self):
        song = self._simple_song()
        song.time_sig = (4, 4)
        with tempfile.TemporaryDirectory() as tmp:
            text = export_lilypond(song, Path(tmp) / "test.ly").read_text()
            assert r"\time 4/4" in text

    def test_time_signature_34(self):
        song = self._simple_song()
        song.time_sig = (3, 4)
        with tempfile.TemporaryDirectory() as tmp:
            text = export_lilypond(song, Path(tmp) / "test.ly").read_text()
            assert r"\time 3/4" in text

    def test_rest_exported(self):
        song = Song(title="Rests", bpm=120)
        tr = song.add_track(Track())
        tr.add(Note.rest(QUARTER))
        with tempfile.TemporaryDirectory() as tmp:
            text = export_lilypond(song, Path(tmp) / "r.ly").read_text()
            assert "r4" in text

    def test_extension_forced(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_lilypond(song, Path(tmp) / "test.wav")
            assert out.suffix == ".ly"


# ---------------------------------------------------------------------------
# ABC Notation export
# ---------------------------------------------------------------------------


class TestABC:
    def _simple_song(self):
        song = Song(title="ABC Test", bpm=120)
        tr = song.add_track(Track(name="melody"))
        tr.extend(
            [
                Note("C", 4, QUARTER),
                Note("D", 4, QUARTER),
                Note("E", 4, QUARTER),
                Note("F", 4, QUARTER),
            ]
        )
        return song

    def test_file_created(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_abc(song, Path(tmp) / "test.abc")
            assert out.exists()
            assert out.suffix == ".abc"

    def test_header_fields(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_abc(song, Path(tmp) / "test.abc").read_text()
            assert "X:1" in text
            assert "T:ABC Test" in text
            assert "M:4/4" in text
            assert "Q:1/4=120" in text

    def test_contains_notes(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_abc(song, Path(tmp) / "test.abc").read_text()
            # C D E F should appear as note tokens
            assert "C" in text and "D" in text

    def test_rest_exported(self):
        song = Song(title="R", bpm=120)
        tr = song.add_track(Track())
        tr.add(Note.rest(QUARTER))
        with tempfile.TemporaryDirectory() as tmp:
            text = export_abc(song, Path(tmp) / "r.abc").read_text()
            assert "z" in text

    def test_34_time_sig(self):
        song = Song(title="Waltz", bpm=120, time_sig=(3, 4))
        tr = song.add_track(Track())
        tr.extend([Note("G", 4, QUARTER)] * 3)
        with tempfile.TemporaryDirectory() as tmp:
            text = export_abc(song, Path(tmp) / "w.abc").read_text()
            assert "M:3/4" in text


# ---------------------------------------------------------------------------
# MusicXML export
# ---------------------------------------------------------------------------


class TestMusicXML:
    def _simple_song(self):
        song = Song(title="XML Test", bpm=100)
        tr = song.add_track(Track(name="piano", instrument="piano"))
        tr.extend([Note("C", 4, QUARTER), Note("E", 4, QUARTER), Note("G", 4, HALF)])
        return song

    def test_file_created(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_musicxml(song, Path(tmp) / "test.xml")
            assert out.exists()
            assert out.suffix == ".xml"

    def test_xml_declaration(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert '<?xml version="1.0"' in text

    def test_score_partwise(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert "<score-partwise" in text

    def test_title_in_xml(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert "XML Test" in text

    def test_tempo_in_xml(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert "100" in text

    def test_time_signature_in_xml(self):
        song = self._simple_song()
        song.time_sig = (4, 4)
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert "<beats>4</beats>" in text
            assert "<beat-type>4</beat-type>" in text

    def test_key_signature_in_xml(self):
        song = self._simple_song()
        song.key_sig = "G"
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "t.xml").read_text()
            assert "<fifths>1</fifths>" in text

    def test_rest_in_xml(self):
        song = Song(title="R", bpm=120)
        tr = song.add_track(Track())
        tr.add(Note.rest(QUARTER))
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "r.xml").read_text()
            assert "<rest/>" in text

    def test_chord_in_xml(self):
        song = Song(title="C", bpm=120)
        tr = song.add_track(Track())
        tr.add(Chord("C", "maj", 4, duration=WHOLE))
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "c.xml").read_text()
            assert "<chord/>" in text

    def test_multiple_tracks(self):
        song = Song(title="Multi", bpm=120)
        for _ in range(3):
            tr = song.add_track(Track())
            tr.add(Note("C", 4, WHOLE))
        with tempfile.TemporaryDirectory() as tmp:
            text = export_musicxml(song, Path(tmp) / "m.xml").read_text()
            assert text.count("<part ") == 3

    def test_extension_forced(self):
        song = self._simple_song()
        with tempfile.TemporaryDirectory() as tmp:
            out = export_musicxml(song, Path(tmp) / "test.wav")
            assert out.suffix == ".xml"
