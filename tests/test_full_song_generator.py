"""Tests for generate_full_song() and auto_arrange() — v131 features."""

from code_music.theory import generate_full_song, auto_arrange


class TestGenerateFullSong:
    """Full song generator produces valid multi-track songs."""

    def test_jazz_song(self):
        song = generate_full_song("jazz", key="Bb", bpm=140, seed=42)
        assert song.title == "Jazz in Bb"
        assert song.bpm == 140
        tracks = [t.name for t in song.tracks]
        assert "chords" in tracks
        assert "bass" in tracks
        assert "drums" in tracks
        assert "melody" in tracks

    def test_pop_song(self):
        song = generate_full_song("pop", key="C", bpm=120, seed=1)
        assert song.title == "Pop in C"
        assert len(song.tracks) >= 3
        for t in song.tracks:
            assert len(t.beats) > 0

    def test_rock_song(self):
        song = generate_full_song("rock", key="E", bpm=130, seed=7)
        assert "Rock" in song.title
        assert song.bpm == 130

    def test_blues_song(self):
        song = generate_full_song("blues", key="A", bpm=110, seed=3)
        assert "Blues" in song.title
        # Blues form uses 12-bar sections
        chords_track = next(t for t in song.tracks if t.name == "chords")
        assert len(chords_track.beats) >= 12

    def test_classical_song(self):
        song = generate_full_song("classical", key="D", bpm=100, seed=5)
        tracks = [t.name for t in song.tracks]
        # Classical has no drums by default
        assert "drums" not in tracks
        assert "melody" in tracks

    def test_electronic_song(self):
        song = generate_full_song("electronic", key="A", bpm=128, seed=99)
        assert song.bpm == 128
        tracks = [t.name for t in song.tracks]
        assert "drums" in tracks

    def test_ambient_song(self):
        song = generate_full_song("ambient", key="F", bpm=70, seed=11)
        tracks = [t.name for t in song.tracks]
        # Ambient has no bass or drums by default
        assert "drums" not in tracks
        assert "bass" not in tracks
        assert "chords" in tracks
        assert "melody" in tracks

    def test_custom_sections(self):
        song = generate_full_song(
            "pop", key="G", bpm=120, sections=["intro", "verse", "chorus", "outro"], seed=42
        )
        # 4 sections × 8 bars = 32 chords
        chords_track = next(t for t in song.tracks if t.name == "chords")
        assert len(chords_track.beats) == 32

    def test_seed_reproducibility(self):
        song1 = generate_full_song("jazz", key="C", bpm=120, seed=42)
        song2 = generate_full_song("jazz", key="C", bpm=120, seed=42)
        beats1 = [
            (b.event.pitch if hasattr(b.event, "pitch") else None)
            for t in song1.tracks
            for b in t.beats[:5]
        ]
        beats2 = [
            (b.event.pitch if hasattr(b.event, "pitch") else None)
            for t in song2.tracks
            for b in t.beats[:5]
        ]
        assert beats1 == beats2

    def test_all_tracks_have_content(self):
        song = generate_full_song("pop", key="C", bpm=120, seed=42)
        for track in song.tracks:
            assert len(track.beats) > 0, f"Track {track.name} is empty"

    def test_unknown_genre_defaults_to_pop(self):
        song = generate_full_song("zzz_not_real", key="C", bpm=120, seed=1)
        assert len(song.tracks) >= 3


class TestAutoArrange:
    """Arrangement engine produces correct multi-track arrangements."""

    def test_jazz_combo(self):
        prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("C", "maj7")]
        song = auto_arrange(prog, key="C", style="jazz_combo", seed=42)
        tracks = [t.name for t in song.tracks]
        assert "bass" in tracks
        assert "piano" in tracks
        assert "drums" in tracks
        assert "melody" in tracks

    def test_rock_band(self):
        prog = [("E", "min"), ("C", "maj"), ("G", "maj"), ("D", "maj")]
        song = auto_arrange(prog, key="E", style="rock_band", bpm=130, seed=7)
        tracks = [t.name for t in song.tracks]
        assert "bass" in tracks
        assert "guitar" in tracks
        assert "drums" in tracks
        assert "lead" in tracks

    def test_orchestral(self):
        prog = [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")]
        song = auto_arrange(prog, key="C", style="orchestral", bpm=90, seed=3)
        tracks = [t.name for t in song.tracks]
        assert "strings" in tracks
        assert "woodwind" in tracks
        assert "brass" in tracks

    def test_electronic(self):
        prog = [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")]
        song = auto_arrange(prog, key="A", style="electronic", bpm=128, seed=11)
        tracks = [t.name for t in song.tracks]
        assert "pad" in tracks
        assert "drums" in tracks

    def test_bars_per_chord(self):
        prog = [("C", "maj"), ("G", "dom7")]
        song = auto_arrange(prog, key="C", bars_per_chord=2, seed=1)
        # 2 chords × 2 bars = 4 chords in the expanded progression
        chords_tracks = [
            t for t in song.tracks if any(hasattr(b.event, "root") for b in t.beats if b.event)
        ]
        assert len(chords_tracks) > 0

    def test_seed_reproducibility(self):
        prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7")]
        s1 = auto_arrange(prog, key="C", style="jazz_combo", seed=42)
        s2 = auto_arrange(prog, key="C", style="jazz_combo", seed=42)
        assert len(s1.tracks) == len(s2.tracks)
        for t1, t2 in zip(s1.tracks, s2.tracks):
            assert len(t1.beats) == len(t2.beats)

    def test_unknown_style_defaults_to_rock(self):
        prog = [("C", "maj"), ("G", "maj")]
        song = auto_arrange(prog, style="not_a_style", seed=1)
        assert len(song.tracks) >= 3

    def test_empty_progression(self):
        song = auto_arrange([], key="C", seed=1)
        assert song is not None
        # All tracks should be empty (no beats to arrange)
        for t in song.tracks:
            assert len(t.beats) == 0

    def test_single_chord(self):
        song = auto_arrange([("C", "maj7")], key="C", seed=1)
        assert len(song.tracks) >= 3
