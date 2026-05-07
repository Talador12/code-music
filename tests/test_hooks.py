"""Tests for hook-first generation."""

from code_music.theory import generate_hook, generate_hook_song, hook_progression


def test_circle_of_fifths_progression_uses_ii_v_i_cells():
    progression = hook_progression("C", steps=2)

    assert progression == [
        ("D", "min7"),
        ("G", "dom7"),
        ("C", "maj7"),
        ("A", "min7"),
        ("D", "dom7"),
        ("G", "maj7"),
    ]


def test_circle_of_fifths_minor_uses_half_diminished_pre_dominant():
    progression = hook_progression("A", steps=1, minor=True)

    assert progression == [("B", "min7b5"), ("E", "dom7"), ("A", "min")]


def test_generate_hook_repeats_short_cell():
    hook = generate_hook("C", bars=2, seed=7)

    assert len(hook) == 16
    assert [note.pitch for note in hook[:4]] == ["C", "D", "E", "D"]
    assert hook[0].velocity > hook[1].velocity


def test_generate_hook_song_builds_runnable_edm_arrangement():
    song = generate_hook_song("zedd", key="C", bars=8, seed=42)

    assert song.title == "Hook EDM in C"
    assert song.bpm == 128
    tracks = {track.name: track for track in song.tracks}
    assert {"chords", "bass", "pulse", "hook"}.issubset(tracks)
    assert len(tracks["chords"].beats) == 8
    assert len(tracks["hook"].beats) == 64


def test_generate_hook_song_supports_coltrane_and_symphonic_styles():
    coltrane = generate_hook_song("coltrane", key="C", bars=6, seed=1)
    symphonic = generate_hook_song("symphonic", key="C", bars=6, seed=1)

    assert "Coltrane" in coltrane.title
    assert any(track.name == "pulse" for track in coltrane.tracks)
    assert "Symphony" in symphonic.title
    assert all(track.name != "pulse" for track in symphonic.tracks)
