"""Tests for Song Builder DSL v2 - full song definition language."""


from code_music import Song, parse_song_dsl, song_from_dsl_v2


class TestParseSongDsl:
    """Test suite for parse_song_dsl function."""

    def test_empty_dsl(self):
        """Test parsing empty DSL returns defaults."""
        spec = parse_song_dsl("")

        assert spec["bpm"] == 120
        assert spec["time_sig"] == (4, 4)
        assert spec["key_sig"] == "C"
        assert spec["title"] == "Untitled"
        assert spec["tracks"] == []

    def test_basic_globals(self):
        """Test parsing global settings."""
        dsl = """
            bpm: 140
            time: 3/4
            key: Am
            title: My Test Song
        """
        spec = parse_song_dsl(dsl)

        assert spec["bpm"] == 140
        assert spec["time_sig"] == (3, 4)
        assert spec["key_sig"] == "Am"
        assert spec["title"] == "My Test Song"

    def test_single_track(self):
        """Test parsing a single track."""
        dsl = """
            track lead piano:
              | C4 E4 G4 |
        """
        spec = parse_song_dsl(dsl)

        assert len(spec["tracks"]) == 1
        assert spec["tracks"][0]["name"] == "lead"
        assert spec["tracks"][0]["instrument"] == "piano"

    def test_multiple_tracks(self):
        """Test parsing multiple tracks."""
        dsl = """
            track melody sawtooth:
              | C4 D4 E4 |

            track bass bass:
              | C3 G3 |
        """
        spec = parse_song_dsl(dsl)

        assert len(spec["tracks"]) == 2
        assert spec["tracks"][0]["name"] == "melody"
        assert spec["tracks"][0]["instrument"] == "sawtooth"
        assert spec["tracks"][1]["name"] == "bass"
        assert spec["tracks"][1]["instrument"] == "bass"

    def test_comments_ignored(self):
        """Test that comments are ignored."""
        dsl = """
            # This is a comment
            bpm: 100
            # Another comment
            track lead piano:
              | C4 |
        """
        spec = parse_song_dsl(dsl)

        assert spec["bpm"] == 100
        assert len(spec["tracks"]) == 1


class TestSongFromDslV2:
    """Test suite for song_from_dsl_v2 function."""

    def test_empty_song(self):
        """Test creating song from minimal DSL."""
        song = song_from_dsl_v2("")

        assert isinstance(song, Song)
        assert song.title == "Untitled"
        assert song.bpm == 120

    def test_single_note_track(self):
        """Test song with single note."""
        dsl = """
            title: Single Note
            track lead piano:
              | C4 |
        """
        song = song_from_dsl_v2(dsl)

        assert song.title == "Single Note"
        assert len(song.tracks) == 1
        track = song.tracks[0]
        assert track.name == "lead"
        assert track.instrument == "piano"

    def test_multiple_bars(self):
        """Test song with multiple bars."""
        dsl = """
            track lead piano:
              | C4 | E4 | G4 |
        """
        song = song_from_dsl_v2(dsl)

        assert len(song.tracks) == 1

    def test_rests_in_track(self):
        """Test that rests are parsed correctly."""
        dsl = """
            track lead piano:
              | C4 - E4 - |
        """
        song = song_from_dsl_v2(dsl)

        assert len(song.tracks) == 1
        # Should have notes and rests

    def test_chord_notation(self):
        """Test chord notation in DSL."""
        dsl = """
            track chords pad:
              | [C4 E4 G4] |
        """
        song = song_from_dsl_v2(dsl)

        assert len(song.tracks) == 1
        # Chord should be created

    def test_complex_song(self):
        """Test a more complete song definition."""
        dsl = """
            title: Jazz Progression
            bpm: 110
            key: Bb
            time: 4/4

            track chords piano:
              | [Bb3 D4 F4] - - - | [Eb3 G3 Bb3] - - - |

            track bass bass:
              | Bb2 - - - | Eb2 - - - |
        """
        song = song_from_dsl_v2(dsl)

        assert song.title == "Jazz Progression"
        assert song.bpm == 110
        assert song.key_sig == "Bb"
        assert len(song.tracks) == 2
        assert song.tracks[0].name == "chords"
        assert song.tracks[1].name == "bass"


class TestDslEdgeCases:
    """Edge case tests for DSL parsing."""

    def test_whitespace_variations(self):
        """Test DSL with varying whitespace."""
        dsl = """
track lead piano:
  | C4 |
        """
        spec = parse_song_dsl(dsl)
        assert len(spec["tracks"]) == 1

    def test_empty_lines(self):
        """Test DSL with empty lines."""
        dsl = """
            bpm: 130

            track lead piano:

              | C4 |
        """
        spec = parse_song_dsl(dsl)
        assert spec["bpm"] == 130
        assert len(spec["tracks"]) == 1

    def test_sharp_and_flat_notes(self):
        """Test parsing sharp and flat notes."""
        dsl = """
            track lead piano:
              | C#4 Eb5 F#5 Bb3 |
        """
        song = song_from_dsl_v2(dsl)

        assert len(song.tracks) == 1

    def test_various_octaves(self):
        """Test notes in various octaves."""
        dsl = """
            track lead piano:
              | C2 C3 C4 C5 C6 |
        """
        song = song_from_dsl_v2(dsl)

        assert len(song.tracks) == 1

    def test_track_without_explicit_instrument(self):
        """Test track definition with minimal syntax."""
        dsl = """
            track lead:
              | C4 |
        """
        spec = parse_song_dsl(dsl)

        assert len(spec["tracks"]) == 1
        assert spec["tracks"][0]["name"] == "lead"
