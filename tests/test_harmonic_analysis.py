"""Tests for v50.0 — functional_analysis, detect_cadences, detect_key."""

from code_music.theory import detect_cadences, detect_key, functional_analysis


class TestFunctionalAnalysis:
    def test_basic_progression(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        result = functional_analysis(prog, key="C")
        assert len(result) == 4
        assert result[0]["roman"] == "I"
        assert result[0]["function"] == "T"
        assert result[1]["roman"] == "IV"
        assert result[1]["function"] == "S"
        assert result[2]["roman"] == "V"
        assert result[2]["function"] == "D"

    def test_minor_chords(self):
        prog = [("A", "min"), ("D", "min")]
        result = functional_analysis(prog, key="C")
        assert result[0]["roman"] == "vi"
        assert result[0]["function"] == "T"  # vi is tonic function
        assert result[1]["roman"] == "ii"
        assert result[1]["function"] == "S"  # ii is subdominant

    def test_chromatic_chord(self):
        prog = [("Eb", "maj")]
        result = functional_analysis(prog, key="C")
        assert result[0]["function"] == "chromatic"

    def test_different_key(self):
        prog = [("G", "maj"), ("C", "maj"), ("D", "dom7")]
        result = functional_analysis(prog, key="G")
        assert result[0]["roman"] == "I"
        assert result[1]["roman"] == "IV"
        assert result[2]["roman"] == "V"


class TestDetectCadences:
    def test_authentic_cadence(self):
        prog = [("G", "dom7"), ("C", "maj")]
        cads = detect_cadences(prog, key="C")
        assert len(cads) == 1
        assert cads[0]["type"] == "authentic"

    def test_plagal_cadence(self):
        prog = [("F", "maj"), ("C", "maj")]
        cads = detect_cadences(prog, key="C")
        assert len(cads) == 1
        assert cads[0]["type"] == "plagal"

    def test_half_cadence(self):
        prog = [("C", "maj"), ("G", "dom7")]
        cads = detect_cadences(prog, key="C")
        assert any(c["type"] == "half" for c in cads)

    def test_deceptive_cadence(self):
        prog = [("G", "dom7"), ("A", "min")]
        cads = detect_cadences(prog, key="C")
        assert len(cads) == 1
        assert cads[0]["type"] == "deceptive"

    def test_no_cadence(self):
        prog = [("C", "maj"), ("D", "min")]
        cads = detect_cadences(prog, key="C")
        assert len(cads) == 0

    def test_multiple_cadences(self):
        prog = [("G", "dom7"), ("C", "maj"), ("F", "maj"), ("C", "maj")]
        cads = detect_cadences(prog, key="C")
        types = [c["type"] for c in cads]
        assert "authentic" in types
        assert "plagal" in types

    def test_position_tracking(self):
        prog = [("C", "maj"), ("G", "dom7"), ("C", "maj")]
        cads = detect_cadences(prog, key="C")
        auth = [c for c in cads if c["type"] == "authentic"]
        assert auth[0]["position"] == 1


class TestDetectKey:
    def test_c_major(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")]
        assert detect_key(prog) == "C"

    def test_g_major(self):
        prog = [("G", "maj"), ("C", "maj"), ("D", "dom7"), ("G", "maj")]
        assert detect_key(prog) == "G"

    def test_single_chord(self):
        prog = [("A", "min")]
        key = detect_key(prog)
        assert isinstance(key, str)

    def test_blues_in_e(self):
        prog = (
            [("E", "dom7")] * 4
            + [("A", "dom7")] * 2
            + [("E", "dom7")] * 2
            + [("B", "dom7"), ("A", "dom7"), ("E", "dom7"), ("B", "dom7")]
        )
        # E blues — roots E, A, B are all diatonic to E major
        assert detect_key(prog) == "E"
