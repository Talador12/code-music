"""Tests for the Fugue Generator."""


from code_music import Note, Song, generate_fugue


class TestGenerateFugue:
    """Test suite for generate_fugue function."""

    def test_basic_fugue_creation(self):
        """Test creating a basic fugue."""
        fugue = generate_fugue(voices=3, key="C", seed=42)

        assert isinstance(fugue, Song)
        assert "Fugue" in fugue.title
        assert len(fugue.tracks) == 3

    def test_fugue_with_custom_subject(self):
        """Test fugue generation with custom subject."""
        subject = [
            Note("C", 4, 1.0),
            Note("E", 4, 1.0),
            Note("G", 4, 1.0),
            Note("C", 5, 2.0),
        ]
        fugue = generate_fugue(subject=subject, voices=3, key="C")

        assert len(fugue.tracks) == 3
        # Subject should be used in the fugue

    def test_voice_counts(self):
        """Test fugue generation with different voice counts."""
        for voices in [2, 3, 4]:
            fugue = generate_fugue(voices=voices, key="G", seed=42)
            assert len(fugue.tracks) == voices

    def test_tonal_vs_real_answer(self):
        """Test fugue with tonal vs real answer."""
        subject = [Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)]

        tonal_fugue = generate_fugue(subject=subject, voices=3, tonal=True, seed=42)
        real_fugue = generate_fugue(subject=subject, voices=3, tonal=False, seed=42)

        assert len(tonal_fugue.tracks) == 3
        assert len(real_fugue.tracks) == 3

    def test_with_and_without_stretto(self):
        """Test fugue with and without stretto."""
        fugue_stretto = generate_fugue(voices=3, include_stretto=True, seed=42)
        fugue_no_stretto = generate_fugue(voices=3, include_stretto=False, seed=42)

        assert len(fugue_stretto.tracks) == 3
        assert len(fugue_no_stretto.tracks) == 3

    def test_episode_counts(self):
        """Test fugue with different episode counts."""
        for episodes in [1, 2, 3]:
            fugue = generate_fugue(voices=3, episodes=episodes, seed=42)
            assert len(fugue.tracks) == 3

    def test_various_keys(self):
        """Test fugue generation in different keys."""
        keys = ["C", "G", "F", "D", "Bb", "A", "E"]
        for key in keys:
            fugue = generate_fugue(voices=3, key=key, seed=42)
            assert key in fugue.title
            assert len(fugue.tracks) == 3

    def test_fugue_has_notes(self):
        """Test that generated fugues contain notes."""
        fugue = generate_fugue(voices=3, key="C", seed=42)

        total_notes = 0
        for track in fugue.tracks:
            for beat in track.beats:
                if beat.event and isinstance(beat.event, Note) and beat.event.pitch is not None:
                    total_notes += 1

        assert total_notes > 0, "Fugue should contain notes"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same fugue structure."""
        fugue1 = generate_fugue(voices=3, key="C", seed=123)
        fugue2 = generate_fugue(voices=3, key="C", seed=123)

        assert fugue1.title == fugue2.title
        assert len(fugue1.tracks) == len(fugue2.tracks)


class TestFugueEdgeCases:
    """Edge case tests for fugue generation."""

    def test_empty_subject(self):
        """Test fugue with no subject (should generate one)."""
        fugue = generate_fugue(subject=[], voices=3, key="C", seed=42)
        assert len(fugue.tracks) == 3

    def test_short_subject(self):
        """Test fugue with very short subject."""
        subject = [Note("C", 4, 1.0), Note("E", 4, 1.0)]
        fugue = generate_fugue(subject=subject, voices=3, key="C")
        assert len(fugue.tracks) == 3

    def test_minimum_voices(self):
        """Test fugue with minimum voices (2)."""
        fugue = generate_fugue(voices=2, key="C", seed=42)
        assert len(fugue.tracks) == 2

    def test_maximum_voices(self):
        """Test fugue with maximum voices (4)."""
        fugue = generate_fugue(voices=4, key="C", seed=42)
        assert len(fugue.tracks) == 4

    def test_zero_episodes(self):
        """Test fugue with no episodes."""
        fugue = generate_fugue(voices=3, episodes=0, seed=42)
        assert len(fugue.tracks) == 3
