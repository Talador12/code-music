"""Tests for concept-to-suite generation."""

from code_music.theory import concept_palette, generate_concept_suite


def test_concept_palette_matches_known_album_idea():
    palette = concept_palette("Rasputin remixes")

    assert palette["title"] == "Rasputin Studies"
    assert palette["styles"][:3] == ["zedd", "coltrane", "symphonic"]
    assert palette["keys"][0] == "E"


def test_concept_palette_is_stable_for_unknown_concepts():
    first = concept_palette("glass city after rain")
    second = concept_palette("glass city after rain")

    assert first == second
    assert len(first["styles"]) == 4
    assert len(first["keys"]) == 4


def test_generate_concept_suite_returns_runnable_songs():
    suite = generate_concept_suite("Planets", tracks=3, seed=5)

    assert len(suite) == 3
    assert suite[0].title.startswith("Planetary Sketches 1")
    assert all(song.tracks for song in suite)
    assert {"chords", "bass", "hook"}.issubset({track.name for track in suite[0].tracks})


def test_generate_concept_suite_handles_zero_tracks():
    assert generate_concept_suite("anything", tracks=0) == []
