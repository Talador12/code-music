"""Tests for call_and_response, ostinato."""

from code_music import Note
from code_music.theory import call_and_response, ostinato


class TestCallAndResponse:
    def test_same_length(self):
        call = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 1.0)]
        resp = call_and_response(call, key="C", seed=42)
        assert len(resp) == len(call)

    def test_ends_on_root(self):
        call = [Note("E", 5, 0.5), Note("G", 5, 0.5), Note("A", 5, 1.0)]
        resp = call_and_response(call, key="C", seed=42)
        assert resp[-1].pitch == "C"

    def test_rests_preserved(self):
        call = [Note.rest(1.0), Note("C", 5, 1.0)]
        resp = call_and_response(call, seed=42)
        assert resp[0].pitch is None

    def test_same_rhythm(self):
        call = [Note("C", 5, 0.5), Note("E", 5, 1.0)]
        resp = call_and_response(call, seed=42)
        assert [n.duration for n in resp] == [n.duration for n in call]


class TestOstinato:
    def test_basic(self):
        pat = [Note("C", 4, 0.5), Note("E", 4, 0.5)]
        o = ostinato(pat, repeats=3)
        assert len(o) == 6

    def test_no_variation(self):
        pat = [Note("C", 4, 0.5)]
        o = ostinato(pat, repeats=2, variation=0.0)
        assert all(n.pitch == "C" for n in o)

    def test_with_variation(self):
        pat = [Note("C", 4, 0.5)] * 4
        o = ostinato(pat, repeats=4, variation=0.8, seed=42)
        pitches = [n.pitch for n in o]
        assert not all(p == "C" for p in pitches)  # some should vary

    def test_rests(self):
        pat = [Note.rest(1.0)]
        o = ostinato(pat, repeats=2)
        assert all(n.pitch is None for n in o)
