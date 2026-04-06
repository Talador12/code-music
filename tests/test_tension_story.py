"""Tests for tension_story() — natural language tension narrative."""

from code_music.theory import tension_story


class TestTensionStory:
    """Tension narrative produces readable, accurate descriptions."""

    def test_basic_progression(self):
        story = tension_story([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")], "C")
        assert isinstance(story, str)
        assert len(story) > 50  # meaningful narrative

    def test_contains_opening(self):
        story = tension_story([("C", "maj"), ("G", "dom7"), ("C", "maj")], "C")
        assert "Opens" in story

    def test_contains_ending(self):
        story = tension_story([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")], "C")
        assert "Ends" in story or "ends" in story

    def test_contains_overall(self):
        story = tension_story([("C", "maj"), ("G", "dom7"), ("C", "maj")], "C")
        assert "Overall" in story

    def test_empty_progression(self):
        story = tension_story([], "C")
        assert "Empty" in story or "empty" in story

    def test_single_chord(self):
        story = tension_story([("C", "maj")], "C")
        assert "Single" in story or "single" in story

    def test_high_tension_progression(self):
        # Chromatic chords → high tension
        prog = [("C", "dim7"), ("F#", "dom7"), ("Bb", "aug"), ("E", "dim")]
        story = tension_story(prog, "C")
        assert "tension" in story.lower()

    def test_calm_progression(self):
        story = tension_story([("C", "maj"), ("F", "maj"), ("C", "maj"), ("G", "maj")], "C")
        # Should mention stability
        assert any(w in story.lower() for w in ["stable", "calm", "rest", "moderate", "resolved"])

    def test_long_progression(self):
        prog = [
            ("C", "maj"),
            ("A", "min"),
            ("D", "min"),
            ("G", "dom7"),
            ("C", "maj"),
            ("F", "maj"),
            ("G", "dom7"),
            ("C", "maj"),
        ]
        story = tension_story(prog, "C")
        assert "climax" in story.lower() or "peak" in story.lower() or "builds" in story.lower()

    def test_different_key(self):
        story = tension_story([("G", "maj"), ("C", "maj"), ("D", "dom7"), ("G", "maj")], "G")
        assert isinstance(story, str)
        assert len(story) > 30

    def test_bars_per_chord(self):
        story = tension_story(
            [("C", "maj"), ("G", "dom7"), ("C", "maj"), ("F", "maj")],
            "C",
            bars_per_chord=2,
        )
        # Bar numbers should be doubled
        assert "bar" in story.lower()

    def test_cadence_mentioned(self):
        # V-I should trigger cadence detection
        story = tension_story([("C", "maj"), ("F", "maj"), ("G", "dom7"), ("C", "maj")], "C")
        # Should mention some kind of cadence
        assert any(
            w in story.lower() for w in ["cadence", "resolves", "closure", "resolution", "dominant"]
        )

    def test_unresolved_ending(self):
        # End on V (dominant) — should mention unresolved
        prog = [("C", "maj"), ("F", "maj"), ("G", "dom7")]
        story = tension_story(prog, "C")
        assert any(
            w in story.lower() for w in ["unresolved", "tension", "open", "ambiguous", "mild"]
        )
