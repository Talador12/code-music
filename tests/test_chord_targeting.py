"""Tests for v63.0 — target_chord_tones, approach_pattern."""

from code_music.theory import approach_pattern, target_chord_tones


class TestTargetChordTones:
    def test_correct_length(self):
        prog = [("C", "maj"), ("G", "dom7")]
        notes = target_chord_tones(prog, notes_per_chord=4, seed=42)
        assert len(notes) == 8  # 2 chords * 4 notes

    def test_strong_beats_are_chord_tones(self):
        prog = [("C", "maj")]
        notes = target_chord_tones(prog, key="C", notes_per_chord=4, seed=42)
        # Beat 0 and 2 should be chord tones (C, E, or G)
        c_chord = {"C", "E", "G"}
        assert notes[0].pitch in c_chord
        assert notes[2].pitch in c_chord

    def test_deterministic(self):
        prog = [("C", "maj"), ("F", "maj")]
        a = target_chord_tones(prog, seed=99)
        b = target_chord_tones(prog, seed=99)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_different_seeds_differ(self):
        prog = [("C", "maj")] * 4
        a = target_chord_tones(prog, seed=1)
        b = target_chord_tones(prog, seed=2)
        assert [n.pitch for n in a] != [n.pitch for n in b]


class TestApproachPattern:
    def test_returns_three_notes(self):
        notes = approach_pattern("C")
        assert len(notes) == 3

    def test_ends_on_target(self):
        notes = approach_pattern("G")
        assert notes[-1].pitch == "G"

    def test_chromatic(self):
        notes = approach_pattern("C", direction="chromatic")
        # Above by 1 semitone = C#, below by 1 = B
        assert notes[0].pitch == "C#"
        assert notes[1].pitch == "B"

    def test_diatonic(self):
        notes = approach_pattern("C", direction="diatonic")
        assert notes[0].pitch == "D"  # 2 semitones up
        assert notes[1].pitch == "Bb"  # 2 semitones down

    def test_enclosure(self):
        notes = approach_pattern("C", direction="enclosure")
        assert len(notes) == 3
        assert notes[-1].pitch == "C"

    def test_target_longer(self):
        notes = approach_pattern("E", duration=0.25)
        assert notes[-1].duration == 0.5  # target is 2x approach duration
