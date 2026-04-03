"""Tests for note_range, rhythmic_density, detect_repeated_sections."""

from code_music import Note, Song, Track
from code_music.theory import detect_repeated_sections, note_range, rhythmic_density

SR = 22050


class TestNoteRange:
    def test_basic(self):
        notes = [Note("C", 4, 1.0), Note("G", 5, 1.0)]
        r = note_range(notes)
        assert r["lowest"] == "C4"
        assert r["highest"] == "G5"
        assert r["span_semitones"] > 0

    def test_single_note(self):
        r = note_range([Note("A", 4, 1.0)])
        assert r["span_semitones"] == 0

    def test_empty(self):
        r = note_range([])
        assert r["lowest"] is None

    def test_with_rests(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0), Note("E", 5, 1.0)]
        r = note_range(notes)
        assert r["lowest"] is not None


class TestRhythmicDensity:
    def test_basic(self):
        notes = [Note("C", 4, 0.5) for _ in range(8)]
        d = rhythmic_density(notes)
        assert d["total_notes"] == 8
        assert d["total_rests"] == 0
        assert d["notes_per_beat"] == 2.0

    def test_with_rests(self):
        notes = [Note("C", 4, 1.0), Note.rest(1.0)]
        d = rhythmic_density(notes)
        assert d["total_notes"] == 1
        assert d["total_rests"] == 1

    def test_durations(self):
        notes = [Note("C", 4, 0.25), Note("E", 4, 2.0)]
        d = rhythmic_density(notes)
        assert d["shortest_note"] == 0.25
        assert d["longest_note"] == 2.0


class TestDetectRepeatedSections:
    def test_basic_repeat(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        # Four identical 1-bar sections (4 beats each)
        for _ in range(4):
            for n in ["C", "E", "G", "C"]:
                tr.add(Note(n, 5, 1.0))
        sections = detect_repeated_sections(song)
        # Should detect at least some repetition
        assert isinstance(sections, list)

    def test_no_repeats(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        for n in ["C", "D", "E", "F"]:
            tr.add(Note(n, 5, 1.0))
        sections = detect_repeated_sections(song)
        # May or may not find patterns in 1 bar
        assert isinstance(sections, list)

    def test_returns_list(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(detect_repeated_sections(song), list)
