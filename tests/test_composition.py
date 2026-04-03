"""Tests for composition tools: melody continuation, sections, lead sheets."""

from __future__ import annotations

import numpy as np

from code_music import Chord, Note, Song, Track
from code_music.composition import (
    Bridge,
    Chorus,
    Intro,
    Outro,
    Verse,
    analyze_song,
    continue_melody,
    generate_arrangement,
    generate_fill,
    generate_intro,
    generate_outro,
    generate_riser,
    quantize_track,
    render_preview,
    song_map,
    song_summary,
    tempo_map,
    to_abc,
    to_html,
    to_lead_sheet,
    to_svg_waveform,
    to_tab,
)
from code_music.theory import analyze_harmony, generate_chord_voicing, generate_variation

SR = 22050


class TestContinueMelody:
    def test_basic_continuation(self):
        seed = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        result = continue_melody(seed, bars=2, key="C", mode="major", seed_rng=42)
        assert len(result) > len(seed)

    def test_returns_notes(self):
        seed = [Note("A", 4, 0.5), Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, seed_rng=42)
        assert all(isinstance(n, Note) for n in result)

    def test_includes_seed(self):
        seed = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        result = continue_melody(seed, bars=1, seed_rng=42)
        # First notes should be the seed
        assert result[0].pitch == "C"
        assert result[1].pitch == "E"

    def test_reproducible(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5)]
        a = continue_melody(seed, bars=2, seed_rng=42)
        b = continue_melody(seed, bars=2, seed_rng=42)
        assert [n.pitch for n in a] == [n.pitch for n in b]

    def test_different_seeds_differ(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5)]
        a = continue_melody(seed, bars=2, seed_rng=42)
        b = continue_melody(seed, bars=2, seed_rng=99)
        assert [n.pitch for n in a] != [n.pitch for n in b]

    def test_minor_key(self):
        seed = [Note("A", 4, 0.5), Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, key="A", mode="minor", seed_rng=42)
        assert len(result) > 2

    def test_pentatonic(self):
        seed = [Note("C", 5, 0.5)]
        result = continue_melody(seed, bars=1, key="C", mode="pentatonic", seed_rng=42)
        assert len(result) > 1

    def test_empty_seed(self):
        result = continue_melody([], bars=1, key="C", seed_rng=42)
        assert len(result) > 0

    def test_in_song(self):
        seed = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
        melody = continue_melody(seed, bars=2, seed_rng=42)
        song = Song(title="Melody Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        tr.extend(melody)
        audio = song.render()
        assert np.max(np.abs(audio)) > 0.0

    def test_order_2(self):
        seed = [Note("C", 5, 0.5), Note("D", 5, 0.5), Note("E", 5, 0.5), Note("F", 5, 0.5)]
        result = continue_melody(seed, bars=2, order=2, seed_rng=42)
        assert len(result) > len(seed)


class TestNamedSections:
    def test_verse(self):
        v = Verse(bars=8)
        assert v.name == "verse"
        assert v.bars == 8

    def test_chorus(self):
        c = Chorus(bars=8)
        assert c.name == "chorus"

    def test_bridge(self):
        b = Bridge(bars=4)
        assert b.name == "bridge"

    def test_intro(self):
        i = Intro(bars=4)
        assert i.name == "intro"

    def test_outro(self):
        o = Outro(bars=4)
        assert o.name == "outro"

    def test_verse_add_track(self):
        v = Verse(bars=4)
        v.add_track("lead", [Note("C", 5, 1.0)])
        assert "lead" in v.tracks

    def test_chorus_repeat(self):
        c = Chorus(bars=4)
        reps = c.repeat(3)
        assert len(reps) == 3
        assert all(r.name == "chorus" for r in reps)

    def test_repr(self):
        v = Verse(bars=8)
        assert "verse" in repr(v)


class TestLeadSheet:
    def test_basic(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        lead = song.add_track(Track(name="lead", instrument="piano"))
        for n in ["C", "Eb", "G", "Bb"]:
            lead.add(Note(n, 5, 1.0))
        for n in ["G", "B", "D", "F"]:
            lead.add(Note(n, 5, 1.0))

        result = to_lead_sheet(song)
        assert "Lead Sheet" in result
        assert "Cmin7" in result
        assert "Gdom7" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = to_lead_sheet(song)
        assert "empty song" in result

    def test_title_and_bpm(self):
        song = Song(title="My Song", bpm=140, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        result = to_lead_sheet(song)
        assert "My Song" in result
        assert "140" in result

    def test_melody_notes_appear(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("E", 5, 1.0))
        tr.add(Note("G", 5, 1.0))
        result = to_lead_sheet(song)
        assert "E" in result
        assert "G" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(to_lead_sheet(song), str)


class TestToTab:
    def test_basic_guitar(self):
        song = Song(title="Tab Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("E", 4, 1.0))
        tr.add(Note("A", 4, 1.0))
        result = to_tab(song, tuning="guitar")
        assert "TAB" in result
        assert "Guitar" in result

    def test_bass_tuning(self):
        song = Song(title="Tab Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="bass", instrument="bass"))
        tr.add(Note("E", 2, 1.0))
        result = to_tab(song, tuning="bass")
        assert "Bass" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = to_tab(song)
        assert "no melodic track" in result

    def test_specific_track(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 1.0))
        song.add_track(Track(name="lead", instrument="piano")).add(Note("E", 4, 1.0))
        result = to_tab(song, track_name="lead")
        assert "TAB" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 1.0))
        assert isinstance(to_tab(song), str)


class TestSongMap:
    def test_basic(self):
        song = Song(title="Map Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        for _ in range(8):
            tr.add(Note("C", 5, 1.0))
        result = song_map(song)
        assert "Song Map" in result
        assert "lead" in result

    def test_multiple_tracks(self):
        song = Song(title="Multi", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).add(Note("C", 2, 4.0))
        song.add_track(Track(name="pad", instrument="pad")).add(Chord("C", "min7", 3, duration=4.0))
        result = song_map(song)
        assert "kick" in result
        assert "pad" in result

    def test_empty_song(self):
        song = Song(title="Empty", bpm=120, sample_rate=SR)
        result = song_map(song)
        assert "Song Map" in result

    def test_returns_string(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(song_map(song), str)


class TestSongSummary:
    def test_basic(self):
        song = Song(title="Test Song", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano", volume=0.5))
        result = song_summary(song)
        assert "Test Song" in result
        assert "120" in result

    def test_includes_tracks(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
        song.add_track(Track(name="pad", instrument="pad", volume=0.4))
        result = song_summary(song)
        assert "kick" in result
        assert "pad" in result
        assert "Tracks: 2" in result

    def test_returns_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        assert isinstance(song_summary(song), str)

    def test_box_drawing(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        result = song_summary(song)
        assert "╔" in result
        assert "╚" in result


class TestAnalyzeHarmony:
    def test_basic_progression(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "maj7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert len(result) == 2
        assert result[0]["roman"] == "I"
        assert result[1]["roman"] == "V"

    def test_minor_chords(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("D", "min7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert result[0]["roman"] == "ii"  # lowercase for minor

    def test_function_labels(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "maj7", 3, duration=4.0))
        tr.add(Chord("F", "maj7", 3, duration=4.0))
        tr.add(Chord("G", "dom7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert result[0]["function"] == "tonic"
        assert result[1]["function"] == "subdominant"
        assert result[2]["function"] == "dominant"

    def test_uses_key_sig(self):
        song = Song(title="Test", bpm=120, sample_rate=SR, key_sig="G")
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("G", "maj7", 3, duration=4.0))
        result = analyze_harmony(song)
        assert result[0]["roman"] == "I"

    def test_returns_list(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="pad", instrument="pad"))
        tr.add(Chord("C", "min7", 3, duration=4.0))
        result = analyze_harmony(song, key="C")
        assert isinstance(result, list)
        assert "beat" in result[0]
        assert "roman" in result[0]

    def test_empty_song(self):
        song = Song(title="Test", bpm=120, sample_rate=SR)
        result = analyze_harmony(song, key="C")
        assert result == []


class TestToABC:
    def test_basic(self):
        song = Song(title="ABC Test", bpm=120, sample_rate=SR, key_sig="C")
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 5, 1.0))
        tr.add(Note("D", 5, 1.0))
        result = to_abc(song)
        assert "X:1" in result
        assert "T:ABC Test" in result
        assert "K:C" in result

    def test_contains_notes(self):
        song = Song(title="T", bpm=120, sample_rate=SR, key_sig="C")
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note("C", 4, 1.0))
        result = to_abc(song)
        assert "C" in result.split("\n")[-1]

    def test_empty_song(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        result = to_abc(song)
        assert "z4" in result

    def test_rests(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        tr.add(Note.rest(1.0))
        tr.add(Note("C", 5, 1.0))
        result = to_abc(song)
        assert "z" in result.split("\n")[-1]

    def test_returns_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 1.0))
        assert isinstance(to_abc(song), str)


class TestGenerateArrangement:
    def test_basic(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick")).extend(
            [Note("C", 2, 1.0) for _ in range(16)]
        )
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note("C", 5, 1.0) for _ in range(16)]
        )
        arr = generate_arrangement(song)
        assert len(arr) > 0
        assert "label" in arr[0]
        assert "start_bar" in arr[0]

    def test_returns_list(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        assert isinstance(generate_arrangement(song), list)

    def test_labels_exist(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note("C", 5, 1.0) for _ in range(16)]
        )
        arr = generate_arrangement(song)
        for section in arr:
            assert section["label"] in ("intro", "verse", "chorus", "breakdown", "outro")


class TestGenerateFill:
    def test_snare_roll(self):
        fill = generate_fill(bars=1, style="snare_roll")
        assert len(fill) > 0
        assert all(isinstance(n, Note) for n in fill)

    def test_buildup(self):
        fill = generate_fill(bars=1, style="buildup")
        assert len(fill) > 0

    def test_crash(self):
        fill = generate_fill(bars=1, style="crash")
        assert fill[0].pitch == "C"

    def test_tom_cascade(self):
        fill = generate_fill(bars=1, style="tom_cascade")
        assert len(fill) > 0


class TestGenerateRiser:
    def test_basic(self):
        riser = generate_riser(bars=1)
        assert len(riser) > 0
        assert all(isinstance(n, Note) for n in riser)

    def test_ascending(self):
        riser = generate_riser(bars=1, start_note="C", octave=3)
        # Should be chromatic ascending
        assert riser[0].pitch == "C"
        assert riser[1].pitch == "C#"

    def test_custom_start(self):
        riser = generate_riser(bars=1, start_note="G")
        assert riser[0].pitch == "G"


class TestAnalyzeSong:
    def test_basic(self):
        song = Song(title="Test", bpm=120, sample_rate=SR, key_sig="C")
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        result = analyze_song(song)
        assert result["title"] == "Test"
        assert result["bpm"] == 120
        assert result["tracks"] == 1
        assert "lead" in result["track_names"]

    def test_includes_harmony(self):
        song = Song(title="T", bpm=120, sample_rate=SR, key_sig="C")
        song.add_track(Track(name="pad", instrument="pad")).add(Chord("C", "maj7", 3, duration=4.0))
        result = analyze_song(song)
        assert isinstance(result["harmony"], list)

    def test_includes_density(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(name="lead", instrument="piano"))
        for _ in range(8):
            tr.add(Note("C", 5, 1.0))
        result = analyze_song(song)
        assert result["density_per_track"]["lead"] == 8

    def test_returns_dict(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        assert isinstance(analyze_song(song), dict)


class TestGenerateIntro:
    def test_basic(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        )
        intro = generate_intro(song, bars=2)
        assert len(intro) > 0
        assert all(isinstance(n, Note) for n in intro)

    def test_sparse_pattern(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note(n, 5, 1.0) for n in ["C", "D", "E", "F"]]
        )
        intro = generate_intro(song, bars=2)
        rests = sum(1 for n in intro if n.pitch is None)
        assert rests > 0  # should have rests for sparse intro

    def test_empty_song(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        intro = generate_intro(song, bars=2)
        assert len(intro) > 0

    def test_reduced_velocity(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 1.0, velocity=0.8))
        intro = generate_intro(song, bars=1)
        pitched = [n for n in intro if n.pitch is not None]
        if pitched:
            assert pitched[0].velocity < 0.8


class TestGenerateOutro:
    def test_basic(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        )
        outro = generate_outro(song, bars=2)
        assert len(outro) > 0

    def test_fading_velocity(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).extend(
            [Note(n, 5, 1.0, velocity=0.8) for n in ["C", "D", "E", "F"]]
        )
        outro = generate_outro(song, bars=2)
        velocities = [n.velocity for n in outro if n.pitch is not None]
        if len(velocities) > 1:
            assert velocities[-1] < velocities[0]  # fading

    def test_empty_song(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        outro = generate_outro(song, bars=2)
        assert len(outro) > 0


class TestToHtml:
    def test_basic(self):
        song = Song(title="HTML Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 4.0))
        html = to_html(song)
        assert "<!DOCTYPE html>" in html
        assert "HTML Test" in html

    def test_includes_tracks(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="kick", instrument="drums_kick"))
        song.add_track(Track(name="pad", instrument="pad"))
        html = to_html(song)
        assert "kick" in html
        assert "pad" in html

    def test_includes_json(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 1.0))
        html = to_html(song)
        assert '"title"' in html

    def test_returns_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        assert isinstance(to_html(song), str)


class TestToSvgWaveform:
    def test_basic(self):
        song = Song(title="SVG Test", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        svg = to_svg_waveform(song)
        assert "<svg" in svg
        assert "SVG Test" in svg

    def test_includes_polygon(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        svg = to_svg_waveform(song)
        assert "<polygon" in svg

    def test_custom_dimensions(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        svg = to_svg_waveform(song, width=400, height=100)
        assert 'width="400"' in svg

    def test_returns_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        assert isinstance(to_svg_waveform(song), str)


class TestTempoMap:
    def test_constant_tempo(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        result = tempo_map(song)
        assert "120 BPM" in result
        assert "constant" in result

    def test_returns_string(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        assert isinstance(tempo_map(song), str)

    def test_includes_title(self):
        song = Song(title="Tempo Test", bpm=90, sample_rate=SR)
        result = tempo_map(song)
        assert "Tempo Test" in result


class TestGenerateVariation:
    def test_retrograde(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        var = generate_variation(melody, "retrograde")
        assert len(var) == 3
        assert var[0].pitch == "G"
        assert var[2].pitch == "C"

    def test_inversion(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        var = generate_variation(melody, "inversion")
        assert len(var) == 2
        assert var[0].pitch == "C"  # anchor stays

    def test_augmentation(self):
        melody = [Note("C", 5, 1.0)]
        var = generate_variation(melody, "augmentation")
        assert var[0].duration == 2.0

    def test_diminution(self):
        melody = [Note("C", 5, 1.0)]
        var = generate_variation(melody, "diminution")
        assert var[0].duration == 0.5

    def test_sequence(self):
        melody = [Note("C", 5, 1.0)]
        var = generate_variation(melody, "sequence")
        assert var[0].pitch == "D"  # up a whole step

    def test_ornamental(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0)]
        var = generate_variation(melody, "ornamental", seed=42)
        assert len(var) > len(melody)  # passing tones added

    def test_retrograde_inversion(self):
        melody = [Note("C", 5, 1.0), Note("E", 5, 1.0), Note("G", 5, 1.0)]
        var = generate_variation(melody, "retrograde_inversion")
        assert len(var) == 3

    def test_rests_preserved(self):
        melody = [Note("C", 5, 1.0), Note.rest(1.0), Note("E", 5, 1.0)]
        var = generate_variation(melody, "retrograde")
        assert var[1].pitch is None

    def test_empty_melody(self):
        assert generate_variation([], "retrograde") == []

    def test_unknown_raises(self):
        import pytest

        with pytest.raises(ValueError):
            generate_variation([Note("C", 5, 1.0)], "yodel")


class TestRenderPreview:
    def test_returns_mono(self):
        song = Song(title="T", bpm=120, sample_rate=SR)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        preview = render_preview(song)
        assert preview.ndim == 1

    def test_shorter_than_full(self):
        song = Song(title="T", bpm=120, sample_rate=44100)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        preview = render_preview(song)
        full = song.render()
        assert len(preview) < len(full) if full.ndim == 1 else full.shape[0]

    def test_restores_sample_rate(self):
        song = Song(title="T", bpm=120, sample_rate=44100)
        song.add_track(Track(name="lead", instrument="piano")).add(Note("C", 5, 2.0))
        render_preview(song)
        assert song.sample_rate == 44100


class TestQuantizeTrack:
    def test_snap_to_grid(self):
        notes = [Note("C", 5, 0.37), Note("E", 5, 0.63)]
        q = quantize_track(notes, grid=0.5)
        assert q[0].duration == 0.5
        assert q[1].duration == 0.5

    def test_preserves_pitch(self):
        notes = [Note("C", 5, 0.3)]
        q = quantize_track(notes, grid=0.25)
        assert q[0].pitch == "C"

    def test_rests(self):
        notes = [Note.rest(0.37)]
        q = quantize_track(notes, grid=0.5)
        assert q[0].pitch is None
        assert q[0].duration == 0.5

    def test_quarter_grid(self):
        notes = [Note("C", 5, 0.8)]
        q = quantize_track(notes, grid=1.0)
        assert q[0].duration == 1.0


class TestGenerateChordVoicing:
    def test_close(self):
        v = generate_chord_voicing("C", "maj", voicing="close")
        assert len(v) == 3
        assert all(isinstance(n, Note) for n in v)

    def test_spread(self):
        v = generate_chord_voicing("C", "maj", voicing="spread")
        assert len(v) == 3
        octaves = [n.octave for n in v]
        assert octaves[-1] > octaves[0]

    def test_drop2(self):
        v = generate_chord_voicing("C", "dom7", voicing="drop2")
        assert len(v) == 4

    def test_rootless(self):
        v = generate_chord_voicing("C", "dom7", voicing="rootless")
        assert len(v) == 3  # root omitted from 4-note chord
        pitches = [n.pitch for n in v]
        assert "C" not in pitches

    def test_unknown_voicing_raises(self):
        import pytest

        with pytest.raises(ValueError):
            generate_chord_voicing("C", "maj", voicing="jazz_cluster")

    def test_unknown_shape_raises(self):
        import pytest

        with pytest.raises(ValueError):
            generate_chord_voicing("C", "imaginary")
