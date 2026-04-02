"""Tests for Pattern class: mini-notation, transforms, polymeter."""

from __future__ import annotations

from code_music import Pattern, Song, Track

SR = 22050


class TestPatternParse:
    def test_simple_notes(self):
        p = Pattern("C4 E4 G4")
        assert len(p) == 3
        assert p.events == ["C4", "E4", "G4"]

    def test_rest_tilde(self):
        p = Pattern("C4 ~ E4")
        assert len(p) == 3
        assert p.events[1] is None

    def test_repeat_star(self):
        p = Pattern("C4*3")
        assert len(p) == 3
        assert all(e == "C4" for e in p.events)

    def test_brackets_flatten(self):
        p = Pattern("[C4 E4] G4")
        assert len(p) == 3
        assert p.events == ["C4", "E4", "G4"]

    def test_empty_string(self):
        p = Pattern("")
        assert len(p) == 0

    def test_from_list(self):
        p = Pattern(["C4", None, "E4"])
        assert len(p) == 3
        assert p.events[1] is None

    def test_case_insensitive_notes(self):
        p = Pattern("c4 e4")
        notes = p.to_notes(0.5)
        assert notes[0].pitch == "C"
        assert notes[1].pitch == "E"

    def test_note_without_octave(self):
        p = Pattern("C E G")
        notes = p.to_notes(0.5, default_octave=5)
        assert all(n.octave == 5 for n in notes)

    def test_sharp_flat(self):
        p = Pattern("C#4 Bb3")
        notes = p.to_notes(0.5)
        assert notes[0].pitch == "C#"
        assert notes[1].pitch == "Bb"  # parsed as uppercase B + b


class TestPatternTransforms:
    def test_reverse(self):
        p = Pattern("C4 E4 G4")
        r = p.reverse()
        assert r.events == ["G4", "E4", "C4"]

    def test_rotate(self):
        p = Pattern("C4 E4 G4")
        r = p.rotate(1)
        assert r.events == ["E4", "G4", "C4"]

    def test_rotate_negative(self):
        p = Pattern("C4 E4 G4")
        r = p.rotate(-1)
        assert r.events == ["G4", "C4", "E4"]

    def test_fast(self):
        p = Pattern("C4 E4")
        f = p.fast(3)
        assert len(f) == 6
        assert f.events == ["C4", "E4", "C4", "E4", "C4", "E4"]

    def test_slow(self):
        p = Pattern("C4 E4")
        s = p.slow(2)
        assert len(s) == 4
        assert s.events == ["C4", None, "E4", None]

    def test_degrade(self):
        p = Pattern("C4 E4 G4 C5 D5 E5 F5 G5")
        d = p.degrade(0.5, seed=42)
        assert len(d) == 8
        # Some should be None, some should survive
        none_count = sum(1 for e in d.events if e is None)
        assert 0 < none_count < 8

    def test_every(self):
        p = Pattern("C4 E4")
        e = p.every(3, lambda x: x.reverse())
        assert len(e) == 6
        # First two reps are normal, third is reversed
        assert e.events[:2] == ["C4", "E4"]
        assert e.events[2:4] == ["C4", "E4"]
        assert e.events[4:6] == ["E4", "C4"]

    def test_choose(self):
        p = Pattern("C4 E4 G4 B4")
        c = p.choose(seed=42)
        assert len(c) == 4
        assert sorted(c.events) == sorted(p.events)

    def test_cat(self):
        a = Pattern("C4 E4")
        b = Pattern("G4 B4")
        c = a.cat(b)
        assert c.events == ["C4", "E4", "G4", "B4"]


class TestPatternPolymeter:
    def test_polymeter_3_2(self):
        a = Pattern("C4 E4 G4")
        b = Pattern("A3 B3")
        poly = Pattern.polymeter(a, b)
        assert len(poly) == 6  # LCM(3,2)

    def test_polymeter_preserves_hits(self):
        a = Pattern("C4 ~ ~")
        b = Pattern("~ D4")
        poly = Pattern.polymeter(a, b)
        # C4 at 0 from a, D4 at 1 from b
        assert poly.events[0] == "C4"
        assert poly.events[1] == "D4"

    def test_polymeter_empty(self):
        assert len(Pattern.polymeter()) == 0


class TestPatternToNotes:
    def test_to_notes_length(self):
        p = Pattern("C4 E4 G4")
        notes = p.to_notes(0.5)
        assert len(notes) == 3

    def test_to_notes_rests(self):
        p = Pattern("C4 ~ E4")
        notes = p.to_notes(1.0)
        assert notes[1].pitch is None
        assert notes[1].duration == 1.0

    def test_to_notes_duration(self):
        p = Pattern("C4 E4")
        notes = p.to_notes(0.25)
        assert all(n.duration == 0.25 for n in notes)

    def test_to_notes_in_song(self):
        p = Pattern("C4 E4 G4 C5")
        song = Song(title="Pattern Test", bpm=120, sample_rate=SR)
        tr = song.add_track(Track(instrument="piano"))
        tr.extend(p.to_notes(1.0))
        audio = song.render()
        assert audio.shape[0] > 0


class TestPatternRepr:
    def test_repr(self):
        p = Pattern("C4 E4 G4")
        r = repr(p)
        assert "Pattern" in r
        assert "len=3" in r
