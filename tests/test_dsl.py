"""Tests for v87.0 — parse_chord_line, parse_melody_line, song_from_dsl."""

from code_music.theory import parse_chord_line, parse_melody_line, song_from_dsl


class TestParseChordLine:
    def test_basic(self):
        chords = parse_chord_line("| C | Am | F | G |")
        assert len(chords) == 4
        assert chords[0] == ("C", "maj")
        assert chords[1] == ("A", "min")

    def test_seventh_chords(self):
        chords = parse_chord_line("| Cmaj7 | Dm7 | G7 |")
        assert chords[0] == ("C", "maj7")
        assert chords[1] == ("D", "min7")
        assert chords[2] == ("G", "dom7")

    def test_sharps_flats(self):
        chords = parse_chord_line("| F# | Bbm |")
        assert chords[0] == ("F#", "maj")
        assert chords[1] == ("Bb", "min")

    def test_empty(self):
        assert parse_chord_line("") == []


class TestParseMelodyLine:
    def test_basic(self):
        notes = parse_melody_line("C5 D5 E5")
        assert len(notes) == 3
        assert notes[0].pitch == "C"
        assert notes[0].octave == 5

    def test_rest(self):
        notes = parse_melody_line("C5 - E5")
        assert notes[1].pitch is None

    def test_default_octave(self):
        notes = parse_melody_line("C D E", octave=4)
        assert all(n.octave == 4 for n in notes)

    def test_sharps(self):
        notes = parse_melody_line("C#5 Eb5")
        assert notes[0].pitch == "C#"
        assert notes[1].pitch == "Eb"


class TestSongFromDSL:
    def test_basic(self):
        dsl = """
[verse]
chords: | C | Am | F | G |
melody: C5 D5 E5 F5 G5 A5 B5 C6
"""
        result = song_from_dsl(dsl)
        assert result["bpm"] == 120
        assert len(result["sections"]) == 1
        assert result["sections"][0]["name"] == "verse"
        assert len(result["sections"][0]["chords"]) == 4
        assert len(result["sections"][0]["melody"]) == 8

    def test_multiple_sections(self):
        dsl = """
[verse]
chords: | C | G |

[chorus]
chords: | F | C |
"""
        result = song_from_dsl(dsl)
        assert len(result["sections"]) == 2

    def test_custom_bpm(self):
        result = song_from_dsl("[intro]\nchords: | C |", bpm=140)
        assert result["bpm"] == 140

    def test_empty(self):
        result = song_from_dsl("")
        assert result["sections"] == []
