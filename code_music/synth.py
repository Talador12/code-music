"""Audio synthesis: convert Notes/Chords/Tracks to numpy sample arrays."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .engine import Chord, Note, Song, Track

FloatArray = NDArray[np.float64]


class Synth:
    """Renders a Song or Track to a raw float32 stereo sample array.

    Each instrument preset is a simple additive/waveform synthesizer with
    an ADSR amplitude envelope.
    """

    PRESETS: dict[str, dict] = {
        # ── Basic waveforms ───────────────────────────────────────────────────
        "sine": {"wave": "sine", "harmonics": 1, "A": 0.01, "D": 0.1, "S": 0.9, "R": 0.3},
        "square": {"wave": "square", "harmonics": 8, "A": 0.01, "D": 0.05, "S": 0.8, "R": 0.2},
        "sawtooth": {"wave": "sawtooth", "harmonics": 12, "A": 0.02, "D": 0.1, "S": 0.7, "R": 0.4},
        "triangle": {"wave": "triangle", "harmonics": 6, "A": 0.02, "D": 0.08, "S": 0.85, "R": 0.3},
        # ── Keyboards ─────────────────────────────────────────────────────────
        "piano": {"wave": "sine", "harmonics": 5, "A": 0.005, "D": 0.3, "S": 0.4, "R": 0.8},
        "organ": {"wave": "sine", "harmonics": 4, "A": 0.01, "D": 0.0, "S": 1.0, "R": 0.1},
        "harpsichord": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.001,
            "D": 0.15,
            "S": 0.0,
            "R": 0.2,
        },
        "rhodes": {"wave": "triangle", "harmonics": 4, "A": 0.005, "D": 0.2, "S": 0.5, "R": 1.0},
        "wurlitzer": {
            "wave": "triangle",
            "harmonics": 5,
            "A": 0.005,
            "D": 0.25,
            "S": 0.45,
            "R": 0.9,
        },
        "celesta": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.08, "S": 0.0, "R": 0.6},
        # ── Strings ───────────────────────────────────────────────────────────
        "strings": {"wave": "sawtooth", "harmonics": 10, "A": 0.12, "D": 0.05, "S": 0.9, "R": 0.4},
        "violin": {"wave": "sawtooth", "harmonics": 14, "A": 0.08, "D": 0.02, "S": 0.95, "R": 0.3},
        "cello": {"wave": "sawtooth", "harmonics": 10, "A": 0.1, "D": 0.03, "S": 0.9, "R": 0.5},
        "contrabass": {
            "wave": "sawtooth",
            "harmonics": 8,
            "A": 0.12,
            "D": 0.04,
            "S": 0.85,
            "R": 0.6,
        },
        "pizzicato": {
            "wave": "sawtooth",
            "harmonics": 6,
            "A": 0.001,
            "D": 0.12,
            "S": 0.0,
            "R": 0.3,
        },
        # ── Brass ─────────────────────────────────────────────────────────────
        "trumpet": {"wave": "square", "harmonics": 12, "A": 0.04, "D": 0.05, "S": 0.85, "R": 0.15},
        "trombone": {"wave": "square", "harmonics": 10, "A": 0.06, "D": 0.04, "S": 0.85, "R": 0.2},
        "french_horn": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.1,
            "D": 0.05,
            "S": 0.8,
            "R": 0.3,
        },
        "tuba": {"wave": "square", "harmonics": 8, "A": 0.08, "D": 0.05, "S": 0.8, "R": 0.25},
        "brass_section": {
            "wave": "square",
            "harmonics": 10,
            "A": 0.05,
            "D": 0.04,
            "S": 0.88,
            "R": 0.18,
        },
        # ── Woodwinds ─────────────────────────────────────────────────────────
        "flute": {"wave": "sine", "harmonics": 2, "A": 0.06, "D": 0.02, "S": 0.9, "R": 0.2},
        "oboe": {"wave": "square", "harmonics": 8, "A": 0.04, "D": 0.02, "S": 0.88, "R": 0.15},
        "clarinet": {"wave": "square", "harmonics": 6, "A": 0.05, "D": 0.02, "S": 0.9, "R": 0.18},
        "bassoon": {"wave": "sawtooth", "harmonics": 8, "A": 0.06, "D": 0.03, "S": 0.85, "R": 0.2},
        "saxophone": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.04,
            "D": 0.03,
            "S": 0.88,
            "R": 0.2,
        },
        "piccolo": {"wave": "sine", "harmonics": 2, "A": 0.03, "D": 0.01, "S": 0.9, "R": 0.15},
        # ── Plucked / Struck ──────────────────────────────────────────────────
        "guitar_acoustic": {
            "wave": "sawtooth",
            "harmonics": 8,
            "A": 0.002,
            "D": 0.3,
            "S": 0.2,
            "R": 0.7,
        },
        "guitar_electric": {
            "wave": "sawtooth",
            "harmonics": 14,
            "A": 0.005,
            "D": 0.15,
            "S": 0.5,
            "R": 0.5,
        },
        "harp": {"wave": "triangle", "harmonics": 7, "A": 0.002, "D": 0.25, "S": 0.1, "R": 1.0},
        "marimba": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.2, "S": 0.0, "R": 0.5},
        "vibraphone": {"wave": "sine", "harmonics": 3, "A": 0.002, "D": 0.3, "S": 0.2, "R": 1.2},
        "xylophone": {
            "wave": "triangle",
            "harmonics": 4,
            "A": 0.001,
            "D": 0.12,
            "S": 0.0,
            "R": 0.3,
        },
        # ── Orchestral percussion ─────────────────────────────────────────────
        "timpani": {"wave": "sine", "harmonics": 2, "A": 0.005, "D": 0.4, "S": 0.1, "R": 1.0},
        "gong": {"wave": "triangle", "harmonics": 5, "A": 0.01, "D": 0.5, "S": 0.3, "R": 2.0},
        "snare_orch": {"wave": "square", "harmonics": 3, "A": 0.001, "D": 0.12, "S": 0.0, "R": 0.1},
        "cymbals": {"wave": "square", "harmonics": 20, "A": 0.005, "D": 0.8, "S": 0.1, "R": 1.5},
        # ── Extended Woodwinds (v170) ─────────────────────────────────────────
        "cor_anglais": {
            "wave": "square",
            "harmonics": 8,
            "A": 0.05,
            "D": 0.02,
            "S": 0.87,
            "R": 0.18,
        },
        "bass_clarinet": {
            "wave": "square",
            "harmonics": 5,
            "A": 0.06,
            "D": 0.03,
            "S": 0.88,
            "R": 0.22,
        },
        "contrabassoon": {
            "wave": "sawtooth",
            "harmonics": 6,
            "A": 0.08,
            "D": 0.04,
            "S": 0.82,
            "R": 0.25,
        },
        "alto_flute": {"wave": "sine", "harmonics": 2, "A": 0.07, "D": 0.02, "S": 0.88, "R": 0.22},
        "english_horn": {
            "wave": "square",
            "harmonics": 7,
            "A": 0.05,
            "D": 0.02,
            "S": 0.86,
            "R": 0.17,
        },
        "soprano_sax": {
            "wave": "sawtooth",
            "harmonics": 12,
            "A": 0.03,
            "D": 0.02,
            "S": 0.9,
            "R": 0.15,
        },
        "tenor_sax": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.04,
            "D": 0.03,
            "S": 0.87,
            "R": 0.2,
        },
        "bari_sax": {
            "wave": "sawtooth",
            "harmonics": 8,
            "A": 0.05,
            "D": 0.04,
            "S": 0.85,
            "R": 0.22,
        },
        # ── Extended Brass (v170) ─────────────────────────────────────────────
        "euphonium": {"wave": "square", "harmonics": 9, "A": 0.07, "D": 0.04, "S": 0.83, "R": 0.22},
        "cornet": {"wave": "square", "harmonics": 11, "A": 0.04, "D": 0.04, "S": 0.86, "R": 0.16},
        "flugelhorn": {
            "wave": "sawtooth",
            "harmonics": 8,
            "A": 0.05,
            "D": 0.05,
            "S": 0.82,
            "R": 0.2,
        },
        "piccolo_trumpet": {
            "wave": "square",
            "harmonics": 14,
            "A": 0.03,
            "D": 0.04,
            "S": 0.87,
            "R": 0.12,
        },
        "bass_trombone": {
            "wave": "square",
            "harmonics": 8,
            "A": 0.07,
            "D": 0.05,
            "S": 0.83,
            "R": 0.25,
        },
        "horn_section": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.06,
            "D": 0.04,
            "S": 0.85,
            "R": 0.2,
        },
        # ── Extended Strings (v170) ───────────────────────────────────────────
        "viola": {"wave": "sawtooth", "harmonics": 12, "A": 0.09, "D": 0.03, "S": 0.92, "R": 0.35},
        "string_section": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.14,
            "D": 0.05,
            "S": 0.88,
            "R": 0.45,
        },
        "string_tremolo": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.02,
            "D": 0.01,
            "S": 0.95,
            "R": 0.15,
        },
        "string_harmonics": {
            "wave": "sine",
            "harmonics": 2,
            "A": 0.01,
            "D": 0.15,
            "S": 0.3,
            "R": 0.8,
        },
        # ── World Instruments (v170) ──────────────────────────────────────────
        "erhu": {"wave": "sawtooth", "harmonics": 12, "A": 0.06, "D": 0.02, "S": 0.93, "R": 0.3},
        "shamisen": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.7},
        "oud": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.1},
        "bouzouki": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.8},
        "dulcimer": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.5},
        "guzheng": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.3},
        "balalaika": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.6},
        "ukulele": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.5},
        "mandolin": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.45},
        "steelpan": {"wave": "sine", "harmonics": 4, "A": 0.001, "D": 0.25, "S": 0.15, "R": 0.8},
        "kalimba": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.2, "S": 0.05, "R": 0.6},
        "gamelan": {"wave": "triangle", "harmonics": 6, "A": 0.002, "D": 0.35, "S": 0.1, "R": 1.5},
        "didgeridoo": {"wave": "sawtooth", "harmonics": 4, "A": 0.15, "D": 0.0, "S": 1.0, "R": 0.3},
        "bagpipe": {"wave": "square", "harmonics": 8, "A": 0.15, "D": 0.0, "S": 1.0, "R": 0.2},
        "harmonica": {"wave": "square", "harmonics": 6, "A": 0.02, "D": 0.01, "S": 0.92, "R": 0.1},
        "accordion": {"wave": "square", "harmonics": 8, "A": 0.03, "D": 0.0, "S": 1.0, "R": 0.12},
        "bandoneon": {"wave": "square", "harmonics": 6, "A": 0.04, "D": 0.0, "S": 1.0, "R": 0.15},
        # ── World Percussion (v170) ───────────────────────────────────────────
        "cajon": {"wave": "sine", "harmonics": 2, "A": 0.001, "D": 0.18, "S": 0.0, "R": 0.2},
        "bongo": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.1, "S": 0.0, "R": 0.15},
        "conga": {"wave": "sine", "harmonics": 2, "A": 0.001, "D": 0.15, "S": 0.0, "R": 0.2},
        "shaker": {"wave": "noise", "harmonics": 1, "A": 0.001, "D": 0.03, "S": 0.0, "R": 0.02},
        "tambourine": {"wave": "noise", "harmonics": 1, "A": 0.001, "D": 0.08, "S": 0.0, "R": 0.1},
        "cowbell": {"wave": "square", "harmonics": 4, "A": 0.001, "D": 0.15, "S": 0.0, "R": 0.2},
        "woodblock": {"wave": "square", "harmonics": 3, "A": 0.001, "D": 0.05, "S": 0.0, "R": 0.05},
        "triangle_perc": {"wave": "sine", "harmonics": 5, "A": 0.001, "D": 0.5, "S": 0.1, "R": 1.0},
        "timbales": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.12, "S": 0.0, "R": 0.15},
        "surdo": {"wave": "sine", "harmonics": 1, "A": 0.002, "D": 0.3, "S": 0.05, "R": 0.4},
        # ── Choir / Vocal ─────────────────────────────────────────────────────
        "choir_aah": {"wave": "sawtooth", "harmonics": 6, "A": 0.15, "D": 0.1, "S": 0.85, "R": 0.5},
        "choir_ooh": {"wave": "sine", "harmonics": 4, "A": 0.2, "D": 0.08, "S": 0.9, "R": 0.6},
        "vox_pad": {"wave": "triangle", "harmonics": 5, "A": 0.35, "D": 0.1, "S": 0.85, "R": 0.8},
        # ── Extended Synths (v170) ────────────────────────────────────────────
        "pulse": {"wave": "square", "harmonics": 10, "A": 0.01, "D": 0.05, "S": 0.85, "R": 0.2},
        "sync_lead": {
            "wave": "sawtooth",
            "harmonics": 16,
            "A": 0.005,
            "D": 0.05,
            "S": 0.9,
            "R": 0.15,
        },
        "trance_lead": {
            "wave": "sawtooth",
            "harmonics": 12,
            "A": 0.005,
            "D": 0.08,
            "S": 0.85,
            "R": 0.2,
        },
        "chiptune": {"wave": "square", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.02},
        "ambient_pad": {"wave": "sine", "harmonics": 4, "A": 0.5, "D": 0.0, "S": 1.0, "R": 1.5},
        "dark_pad": {"wave": "sawtooth", "harmonics": 6, "A": 0.4, "D": 0.1, "S": 0.9, "R": 1.2},
        "glass_pad": {"wave": "triangle", "harmonics": 8, "A": 0.3, "D": 0.15, "S": 0.7, "R": 1.0},
        "warm_pad": {"wave": "sawtooth", "harmonics": 4, "A": 0.4, "D": 0.05, "S": 0.95, "R": 1.0},
        "poly_synth": {
            "wave": "sawtooth",
            "harmonics": 8,
            "A": 0.01,
            "D": 0.15,
            "S": 0.6,
            "R": 0.4,
        },
        "fm_keys": {
            "wave": "fm",
            "harmonics": 4,
            "mod_ratio": 2.0,
            "A": 0.005,
            "D": 0.2,
            "S": 0.4,
            "R": 0.8,
        },
        "fm_pad": {
            "wave": "fm",
            "harmonics": 2,
            "mod_ratio": 1.5,
            "A": 0.3,
            "D": 0.0,
            "S": 1.0,
            "R": 1.0,
        },
        # ── Extended Drums (v170) ─────────────────────────────────────────────
        "drums_rimshot": {
            "wave": "square",
            "harmonics": 4,
            "A": 0.001,
            "D": 0.03,
            "S": 0.0,
            "R": 0.03,
        },
        "drums_open_hat": {
            "wave": "square",
            "harmonics": 16,
            "A": 0.001,
            "D": 0.3,
            "S": 0.05,
            "R": 0.4,
        },
        "drums_low_tom": {
            "wave": "sine",
            "harmonics": 2,
            "A": 0.003,
            "D": 0.25,
            "S": 0.0,
            "R": 0.35,
        },
        "drums_floor_tom": {
            "wave": "sine",
            "harmonics": 1,
            "A": 0.003,
            "D": 0.3,
            "S": 0.0,
            "R": 0.4,
        },
        "drums_splash": {
            "wave": "square",
            "harmonics": 14,
            "A": 0.003,
            "D": 0.4,
            "S": 0.05,
            "R": 0.8,
        },
        "drums_china": {
            "wave": "square",
            "harmonics": 18,
            "A": 0.002,
            "D": 0.5,
            "S": 0.08,
            "R": 1.0,
        },
        "drums_ghost_snare": {
            "wave": "square",
            "harmonics": 2,
            "A": 0.001,
            "D": 0.06,
            "S": 0.0,
            "R": 0.04,
        },
        "drums_brush": {
            "wave": "noise",
            "harmonics": 1,
            "A": 0.003,
            "D": 0.15,
            "S": 0.05,
            "R": 0.2,
        },
        # ── EDM synths ────────────────────────────────────────────────────────
        "bass": {"wave": "sawtooth", "harmonics": 6, "A": 0.02, "D": 0.2, "S": 0.6, "R": 0.3},
        "pad": {"wave": "sine", "harmonics": 3, "A": 0.3, "D": 0.0, "S": 1.0, "R": 0.8},
        "pluck": {"wave": "sawtooth", "harmonics": 8, "A": 0.001, "D": 0.4, "S": 0.1, "R": 0.5},
        # Karplus-Strong physical models — most realistic plucked/struck sounds
        "guitar_ks": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.2},
        "banjo_ks": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.6},
        "harp_ks": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.8},
        "sitar_ks": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 1.0},
        "koto_ks": {"wave": "karplus", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.9},
        "supersaw": {"wave": "supersaw", "harmonics": 7, "A": 0.02, "D": 0.05, "S": 0.9, "R": 0.3},
        "reese_bass": {"wave": "reese", "harmonics": 6, "A": 0.03, "D": 0.1, "S": 0.8, "R": 0.4},
        "acid": {"wave": "sawtooth", "harmonics": 10, "A": 0.005, "D": 0.2, "S": 0.3, "R": 0.15},
        "hoover": {"wave": "hoover", "harmonics": 8, "A": 0.05, "D": 0.3, "S": 0.6, "R": 0.5},
        "stab": {"wave": "square", "harmonics": 6, "A": 0.005, "D": 0.08, "S": 0.0, "R": 0.1},
        # wobble: sawtooth with per-note LFO filter — the dubstep bass sound
        "wobble": {
            "wave": "sawtooth",
            "harmonics": 14,
            "A": 0.01,
            "D": 0.05,
            "S": 0.9,
            "R": 0.2,
            "lfo_rate": 2.0,
            "lfo_min_cutoff": 80.0,
            "lfo_max_cutoff": 3500.0,
        },
        # portamento: sawtooth with pitch glide between notes
        "portamento": {"wave": "porta", "harmonics": 8, "A": 0.01, "D": 0.0, "S": 1.0, "R": 0.15},
        # fm_bell: frequency-modulated metallic bell tone
        "fm_bell": {"wave": "fm", "harmonics": 3, "A": 0.001, "D": 0.4, "S": 0.1, "R": 1.5},
        # formant: vowel-shaped filter over sawtooth (choir/vocal synth)
        "formant_a": {
            "wave": "formant",
            "harmonics": 8,
            "A": 0.06,
            "D": 0.05,
            "S": 0.9,
            "R": 0.3,
            "formant": "a",
        },
        "formant_o": {
            "wave": "formant",
            "harmonics": 8,
            "A": 0.08,
            "D": 0.05,
            "S": 0.9,
            "R": 0.4,
            "formant": "o",
        },
        "formant_e": {
            "wave": "formant",
            "harmonics": 8,
            "A": 0.05,
            "D": 0.05,
            "S": 0.9,
            "R": 0.25,
            "formant": "e",
        },
        # taiko: deep pitched drum for cinematic trailer hits
        "taiko": {"wave": "sine", "harmonics": 2, "A": 0.001, "D": 0.3, "S": 0.05, "R": 0.4},
        # ethnic percussion
        "tabla": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.15, "S": 0.0, "R": 0.2},
        "djembe": {"wave": "triangle", "harmonics": 4, "A": 0.001, "D": 0.2, "S": 0.0, "R": 0.3},
        # synth bass variants
        "moog_bass": {"wave": "moog", "harmonics": 10, "A": 0.01, "D": 0.15, "S": 0.7, "R": 0.2},
        "sub_bass": {"wave": "sine", "harmonics": 1, "A": 0.02, "D": 0.05, "S": 1.0, "R": 0.3},
        "lead_edm": {
            "wave": "sawtooth",
            "harmonics": 10,
            "A": 0.01,
            "D": 0.05,
            "S": 0.85,
            "R": 0.2,
        },
        "noise_sweep": {"wave": "noise", "harmonics": 1, "A": 1.0, "D": 0.0, "S": 1.0, "R": 0.5},
        # ── Drum kit ──────────────────────────────────────────────────────────
        "drums_kick": {"wave": "sine", "harmonics": 1, "A": 0.001, "D": 0.15, "S": 0.0, "R": 0.1},
        "drums_snare": {
            "wave": "square",
            "harmonics": 2,
            "A": 0.001,
            "D": 0.1,
            "S": 0.0,
            "R": 0.08,
        },
        "drums_hat": {
            "wave": "square",
            "harmonics": 16,
            "A": 0.001,
            "D": 0.04,
            "S": 0.0,
            "R": 0.03,
        },
        "drums_clap": {"wave": "noise", "harmonics": 1, "A": 0.001, "D": 0.06, "S": 0.0, "R": 0.05},
        "drums_tom": {"wave": "sine", "harmonics": 2, "A": 0.003, "D": 0.2, "S": 0.0, "R": 0.3},
        "drums_ride": {
            "wave": "square",
            "harmonics": 12,
            "A": 0.002,
            "D": 0.6,
            "S": 0.05,
            "R": 1.0,
        },
        "drums_crash": {
            "wave": "square",
            "harmonics": 18,
            "A": 0.003,
            "D": 0.8,
            "S": 0.05,
            "R": 2.0,
        },
        "drums_808": {"wave": "sine", "harmonics": 1, "A": 0.001, "D": 0.6, "S": 0.0, "R": 0.5},
    }

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    # ------------------------------------------------------------------
    # Waveform generators
    # ------------------------------------------------------------------

    _harmonics_cache: dict[str, int] = {}
    _custom_instruments: dict[str, object] = {}  # name → SoundDesigner

    @classmethod
    def register(cls, name: str, designer: object) -> None:
        """Register a SoundDesigner as a playable instrument.

        After registration, any Track with ``instrument=name`` will use the
        designer's ``render(freq, duration, sr)`` method instead of the
        built-in additive synthesis.
        """
        cls._custom_instruments[name] = designer

    def _wave(self, wave: str, freq: float, n_samples: int) -> FloatArray:
        """Generate waveform using band-limited additive synthesis.

        Harmonic count is dynamically calculated per note: we use as many
        harmonics as will fit below the Nyquist frequency. A 100 Hz saw at
        44.1 kHz gets 220 harmonics (rich, full). A 4000 Hz saw gets 5
        harmonics (still band-limited, no aliasing). This is the key to
        both clarity and warmth - maximum harmonic content without aliasing.
        """
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        # Cache preset harmonics as the MINIMUM (floor) count
        if wave not in self._harmonics_cache:
            self._harmonics_cache[wave] = next(
                (p["harmonics"] for p in self.PRESETS.values() if p.get("wave") == wave),
                8,
            )
        preset_harmonics = self._harmonics_cache[wave]

        # Dynamic harmonic count: fill up to Nyquist for maximum richness
        nyquist = self.sample_rate / 2.0
        if freq > 0:
            max_safe = max(1, int(nyquist / freq) - 1)
        else:
            max_safe = preset_harmonics
        harmonics = min(max_safe, max(preset_harmonics, max_safe))

        if wave == "sine":
            return np.sin(2 * np.pi * freq * t)

        elif wave == "square":
            n_odd = max(1, (harmonics + 1) // 2)
            ks = np.arange(1, 2 * n_odd, 2)
            # Only keep harmonics below Nyquist
            ks = ks[ks * freq < nyquist]
            if len(ks) == 0:
                return np.sin(2 * np.pi * freq * t)
            return (4 / np.pi) * np.sum(
                (1 / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t), axis=0
            )

        elif wave == "sawtooth":
            ks = np.arange(1, harmonics + 1)
            ks = ks[ks * freq < nyquist]
            if len(ks) == 0:
                return np.sin(2 * np.pi * freq * t)
            signs = (-1) ** (ks + 1)
            return (2 / np.pi) * np.sum(
                (signs / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t), axis=0
            )

        elif wave == "triangle":
            ks_base = np.arange(0, harmonics)
            ns = 2 * ks_base + 1
            mask = ns * freq < nyquist
            ns = ns[mask]
            ks_base = ks_base[mask]
            if len(ns) == 0:
                return np.sin(2 * np.pi * freq * t)
            signs = (-1) ** ks_base
            return (8 / np.pi**2) * np.sum(
                (signs / ns**2)[:, None] * np.sin(2 * np.pi * freq * ns[:, None] * t), axis=0
            )

        elif wave == "supersaw":
            # Detune 7 sawtooths ±25 cents around centre freq for the Zedd/trance wall sound
            detune_cents = np.array([-25, -17, -8, 0, 8, 17, 25])
            result = np.zeros(n_samples)
            for dc in detune_cents:
                f_det = freq * (2 ** (dc / 1200))
                ks = np.arange(1, harmonics + 1)
                result += (2 / np.pi) * np.sum(
                    ((-1) ** (ks + 1) / ks)[:, None] * np.sin(2 * np.pi * f_det * ks[:, None] * t),
                    axis=0,
                )
            return result / len(detune_cents)

        elif wave == "reese":
            # Two slightly detuned sawtooths — classic DnB/techno Reese bass
            f1 = freq * (2 ** (-7 / 1200))
            f2 = freq * (2 ** (7 / 1200))
            ks = np.arange(1, harmonics + 1)
            saw1 = (2 / np.pi) * np.sum(
                ((-1) ** (ks + 1) / ks)[:, None] * np.sin(2 * np.pi * f1 * ks[:, None] * t), axis=0
            )
            saw2 = (2 / np.pi) * np.sum(
                ((-1) ** (ks + 1) / ks)[:, None] * np.sin(2 * np.pi * f2 * ks[:, None] * t), axis=0
            )
            return (saw1 + saw2) * 0.5

        elif wave == "hoover":
            # Hoover: detuned square waves — iconic rave/gabber/Mord Fustang sound
            detune = np.array([-12, -5, 0, 5, 12])
            result = np.zeros(n_samples)
            for dc in detune:
                f_det = freq * (2 ** (dc / 1200))
                ks = np.arange(1, harmonics + 1, 2)
                result += (4 / np.pi) * np.sum(
                    (1 / ks)[:, None] * np.sin(2 * np.pi * f_det * ks[:, None] * t), axis=0
                )
            return result / len(detune)

        elif wave == "noise":
            # White noise — for sweeps, snare body, cymbals
            rng = np.random.default_rng(int(freq * 1000) % (2**31))
            return rng.standard_normal(n_samples)

        elif wave == "moog":
            # Moog-style: sawtooth with cascaded LP character (2nd-order rolloff baked in)
            ks = np.arange(1, harmonics + 1)
            # Weight higher harmonics down faster than regular saw (ladder filter feel)
            weights = (-1) ** (ks + 1) / (ks * np.sqrt(ks))
            return (2.0) * np.sum(
                weights[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t), axis=0
            )

        elif wave == "fm":
            # 2-operator FM: carrier modulated by a sine at configurable ratio/index
            # Presets can specify mod_ratio and mod_index for different FM timbres.
            # mod_ratio: integer = harmonic, non-integer = metallic/bell-like
            # mod_index (harmonics field): 0 = pure sine, higher = more overtones
            mod_ratio = self._fm_ratio_hint or 2.0
            mod_index = max(0.1, harmonics * 0.3) if harmonics > 0 else 0.8
            mod_depth = freq * mod_index
            mod = mod_depth * np.sin(2 * np.pi * freq * mod_ratio * t)
            return np.sin(2 * np.pi * freq * t + mod)

        elif wave == "formant":
            # Sawtooth with formant frequency peaks (vowel character)
            # Preset key carries "formant" field: "a", "o", "e", "i", "u"
            ks = np.arange(1, harmonics + 1)
            raw = (2 / np.pi) * np.sum(
                ((-1) ** (ks + 1) / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t),
                axis=0,
            )
            return raw  # filter applied in _render_note based on preset["formant"]

        elif wave == "porta":
            # Portamento sawtooth — the glide is handled in _render_note via
            # cumulative phase integration (here we just do standard saw)
            ks = np.arange(1, harmonics + 1)
            return (2 / np.pi) * np.sum(
                ((-1) ** (ks + 1) / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t),
                axis=0,
            )

        elif wave == "karplus":
            # Karplus-Strong plucked string synthesis.
            # Seeds a short buffer with noise, then applies a feedback loop
            # with a simple averaging filter — models a vibrating string.
            period = max(2, int(self.sample_rate / max(freq, 1.0)))
            out = np.zeros(n_samples)
            # Seed: short burst of white noise at pitch frequency
            rng = np.random.default_rng(int(freq * 137) % (2**31))
            buf = rng.uniform(-1.0, 1.0, period)
            # Frequency-dependent loss: high strings decay faster than low strings
            # (physics: shorter wavelength = more energy dissipation per cycle)
            base_loss = 0.998
            freq_factor = min(freq / 4000.0, 0.01)  # higher freq = more loss
            loss = max(0.98, base_loss - freq_factor)
            for i in range(n_samples):
                out[i] = buf[i % period]
                buf[i % period] = loss * 0.5 * (buf[i % period] + buf[(i + 1) % period])
            return out

        else:
            return np.sin(2 * np.pi * freq * t)

    def _adsr(self, n_samples: int, A: float, D: float, S: float, R: float) -> FloatArray:
        """Build ADSR amplitude envelope with exponential curves.

        Real synths use exponential attack/decay/release, not linear ramps.
        Linear envelopes sound mechanical - a straight line from 0 to 1 is
        not how any acoustic instrument behaves. Exponential attack starts
        fast then slows (like a struck string). Exponential decay and release
        are the natural behavior of damped oscillators (everything in physics).

        Also applies 2ms micro-fades at note start/end to prevent click
        artifacts from non-zero-crossing boundaries.
        """
        sr = self.sample_rate
        a_s = min(int(A * sr), n_samples)
        d_s = min(int(D * sr), n_samples - a_s)
        r_s = min(int(R * sr), n_samples - a_s - d_s)
        s_s = max(0, n_samples - a_s - d_s - r_s)

        env = np.zeros(n_samples)

        # Attack: exponential rise (starts fast, slows near peak)
        if a_s > 0:
            t = np.linspace(0, 1, a_s)
            env[:a_s] = 1.0 - np.exp(-4.0 * t)  # ~98% at t=1
            peak = env[a_s - 1] if a_s > 0 else 1.0
            if peak > 0:
                env[:a_s] /= peak  # normalize to reach exactly 1.0

        # Decay: exponential fall from 1.0 to sustain level
        if d_s > 0:
            t = np.linspace(0, 1, d_s)
            env[a_s : a_s + d_s] = S + (1.0 - S) * np.exp(-5.0 * t)

        # Sustain: flat at sustain level
        if s_s > 0:
            env[a_s + d_s : a_s + d_s + s_s] = S

        # Release: exponential decay from sustain to zero
        if r_s > 0:
            start = a_s + d_s + s_s
            t = np.linspace(0, 1, r_s)
            env[start : start + r_s] = S * np.exp(-5.0 * t)

        # Micro-fade at boundaries to prevent clicks (2ms)
        fade_samples = min(int(0.002 * sr), n_samples // 4, 88)
        if fade_samples > 1:
            # Fade in at the very start
            env[:fade_samples] *= np.linspace(0, 1, fade_samples)
            # Fade out at the very end
            env[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return env

    # ------------------------------------------------------------------
    # Per-note rendering
    # ------------------------------------------------------------------

    def _render_note(
        self, note: Note, n_samples: int, preset: dict, instrument_name: str = ""
    ) -> FloatArray:
        freq = note.freq
        if freq is None or freq <= 0:
            return np.zeros(n_samples)

        # Check for custom SoundDesigner instruments first
        designer = self._custom_instruments.get(instrument_name)
        if designer is not None and hasattr(designer, "render"):
            duration = n_samples / self.sample_rate
            return designer.render(freq, duration, self.sample_rate)[:n_samples]

        wave_type = preset.get("wave", "sine")
        # Pitch-drop envelope: kick drums, 808, timpani, tom
        pitch_drop_presets = {"drums_kick", "drums_808", "drums_tom", "timpani"}
        is_pitch_drop = any(k in str(preset) for k in pitch_drop_presets) or (
            wave_type == "sine" and preset.get("A", 0.01) < 0.005
        )

        if is_pitch_drop:
            t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            drop_rate = 30.0 if "808" in str(preset) else 50.0
            freq_env = freq * np.exp(-drop_rate * t)
            raw = np.sin(2 * np.pi * np.cumsum(freq_env) / self.sample_rate)
        else:
            # Pass FM ratio hint from preset (fm_keys uses 3.0, fm_bell uses 1.414, etc.)
            self._fm_ratio_hint = preset.get("mod_ratio", None)
            raw = self._wave(wave_type, freq, n_samples)
            self._fm_ratio_hint = None

        # Noise layer for snare / clap / cymbals / crash / ride
        noise_presets = {"snare", "clap", "cymbals", "crash", "ride"}
        if any(k in str(preset) for k in noise_presets):
            rng = np.random.default_rng(int(freq * 137) % (2**31))
            noise = rng.standard_normal(n_samples)
            raw = raw * 0.5 + noise * 0.5

        # ── Per-note LFO filter (wobble bass + formant) ──────────────────
        from scipy import signal as _sig

        if "lfo_rate" in preset:
            # Dubstep wobble: LFO sweeps a lowpass filter over the note
            lfo_rate = preset.get("lfo_rate", 2.0)
            lfo_min = preset.get("lfo_min_cutoff", 80.0)
            lfo_max = preset.get("lfo_max_cutoff", 4000.0)
            t_note = np.arange(n_samples) / self.sample_rate
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * lfo_rate * t_note)
            cutoffs = lfo_min + lfo * (lfo_max - lfo_min)
            block = 256
            filtered = np.zeros(n_samples)
            for start in range(0, n_samples, block):
                end_b = min(start + block, n_samples)
                cutoff = float(
                    np.clip(np.mean(cutoffs[start:end_b]), 20.0, self.sample_rate / 2 - 1)
                )
                sos = _sig.butter(2, cutoff, btype="low", fs=self.sample_rate, output="sos")
                filtered[start:end_b] = _sig.sosfilt(sos, raw[start:end_b])
            raw = filtered

        elif preset.get("formant"):
            # Formant filter: vowel resonances via three bandpass peaks
            FORMANTS = {
                #       F1     F2     F3   (Hz)
                "a": [(800, 0.8), (1200, 0.5), (2600, 0.3)],
                "e": [(400, 0.9), (2300, 0.7), (3000, 0.3)],
                "i": [(300, 0.9), (2800, 0.8), (3400, 0.3)],
                "o": [(550, 0.9), (1000, 0.6), (2500, 0.2)],
                "u": [(350, 0.9), (700, 0.5), (2200, 0.2)],
            }
            vowel = preset.get("formant", "a")
            fmts = FORMANTS.get(vowel, FORMANTS["a"])
            result = np.zeros(n_samples)
            for f_center, gain in fmts:
                f_center = min(f_center, self.sample_rate / 2 - 1)
                bw = f_center * 0.25
                low = max(20.0, f_center - bw / 2)
                high = min(self.sample_rate / 2 - 1, f_center + bw / 2)
                if low < high:
                    sos = _sig.butter(
                        2, [low, high], btype="band", fs=self.sample_rate, output="sos"
                    )
                    result += _sig.sosfilt(sos, raw) * gain
            # Blend with small amount of dry for body
            raw = raw * 0.2 + result * 0.8

        # ── Taiko / djembe: pitch drop with noise attack ─────────────────
        if wave_type in ("taiko", "djembe", "tabla"):
            rng = np.random.default_rng(int(freq * 99) % (2**31))
            attack_noise = rng.standard_normal(n_samples)
            # Short attack noise burst
            noise_env = np.zeros(n_samples)
            attack_end = min(int(0.02 * self.sample_rate), n_samples)
            noise_env[:attack_end] = np.linspace(1, 0, attack_end)
            raw = raw * 0.75 + attack_noise * noise_env * 0.4

        # ── Articulation-aware envelope and timbre (v170) ─────────────────
        art = getattr(note, "articulation", None)
        A, D, S, R = preset["A"], preset["D"], preset["S"], preset["R"]

        if art is not None:
            A, D, S, R, raw = self._apply_articulation(
                raw,
                art,
                A,
                D,
                S,
                R,
                wave_type,
                n_samples,
                _sig,
            )

        env = self._adsr(n_samples, A, D, S, R)

        # ── Velocity-to-timbre: every instrument family responds differently ──
        # Real instruments change spectral content with dynamics, not just volume.
        # Soft = darker/rounder, loud = brighter/edgier. The amount and character
        # of this change depends on the instrument family.
        vel = note.velocity
        if vel > 0.01 and n_samples > 64:
            raw = self._apply_velocity_timbre(raw, vel, wave_type, preset, instrument_name, _sig)

        return raw * env * vel

    # ------------------------------------------------------------------
    # Velocity-dependent timbre shaping
    # ------------------------------------------------------------------

    # Instrument family classification for timbre response
    _TIMBRE_FAMILIES = {
        "brass": {
            "instruments": {
                "trumpet",
                "trombone",
                "french_horn",
                "tuba",
                "brass_section",
                "euphonium",
                "cornet",
                "flugelhorn",
                "piccolo_trumpet",
                "bass_trombone",
                "horn_section",
            },
            # Brass: soft = dark and mellow, loud = bright and biting
            # At ff the upper partials explode. At pp it sounds almost like a flute.
            "lp_range": (1500.0, 12000.0),  # LP cutoff: pp to ff
            "hp_boost": 0.5,  # high shelf boost at forte
            "attack_bite": 0.3,  # transient edge at high velocity
        },
        "woodwind": {
            "instruments": {
                "flute",
                "oboe",
                "clarinet",
                "bassoon",
                "saxophone",
                "piccolo",
                "cor_anglais",
                "bass_clarinet",
                "contrabassoon",
                "alto_flute",
                "english_horn",
                "soprano_sax",
                "tenor_sax",
                "bari_sax",
                "harmonica",
                "accordion",
                "bandoneon",
                "bagpipe",
            },
            # Woodwinds: soft = breathy, loud = focused and reedy
            "lp_range": (2000.0, 10000.0),
            "hp_boost": 0.35,
            "attack_bite": 0.15,
        },
        "string": {
            "instruments": {
                "strings",
                "violin",
                "cello",
                "contrabass",
                "pizzicato",
                "viola",
                "string_section",
                "string_tremolo",
                "string_harmonics",
                "erhu",
            },
            # Strings: soft = silky sul tasto, loud = bright sul ponticello edge
            "lp_range": (2500.0, 11000.0),
            "hp_boost": 0.4,
            "attack_bite": 0.2,
        },
        "plucked": {
            "instruments": {
                "guitar_acoustic",
                "guitar_electric",
                "harp",
                "guitar_ks",
                "banjo_ks",
                "harp_ks",
                "sitar_ks",
                "koto_ks",
                "shamisen",
                "oud",
                "bouzouki",
                "dulcimer",
                "guzheng",
                "balalaika",
                "ukulele",
                "mandolin",
            },
            # Plucked: soft = round and warm, loud = bright attack with overtones
            "lp_range": (2000.0, 12000.0),
            "hp_boost": 0.45,
            "attack_bite": 0.25,
        },
        "keys": {
            "instruments": {
                "piano",
                "rhodes",
                "wurlitzer",
                "celesta",
                "organ",
                "harpsichord",
                "marimba",
                "vibraphone",
                "xylophone",
                "steelpan",
                "kalimba",
                "gamelan",
                "fm_keys",
            },
            # Keys: soft = mellow and dark, loud = bell-like clarity
            "lp_range": (1800.0, 14000.0),
            "hp_boost": 0.4,
            "attack_bite": 0.2,
        },
        "choir": {
            "instruments": {
                "choir_aah",
                "choir_ooh",
                "vox_pad",
            },
            # Choir: soft = covered/dark, loud = open and brilliant (singer's formant)
            "lp_range": (2000.0, 8000.0),
            "hp_boost": 0.5,
            "attack_bite": 0.1,
        },
    }

    def _apply_velocity_timbre(
        self,
        raw: FloatArray,
        vel: float,
        wave_type: str,
        preset: dict,
        instrument_name: str,
        _sig,
    ) -> FloatArray:
        """Apply velocity-dependent timbral shaping.

        Real instruments do not just get louder when played harder.
        They change character. This function applies a velocity-controlled
        low-pass filter (darker at low velocity) and high-frequency boost
        (brighter at high velocity) based on the instrument family.
        """
        # Determine which family this instrument belongs to
        family_config = None
        for family_name, config in self._TIMBRE_FAMILIES.items():
            if instrument_name in config["instruments"]:
                family_config = config
                break

        # Fallback: basic brightness scaling for unclassified instruments
        if family_config is None:
            # Still apply gentle brightness scaling for everything
            brightness = max(0.0, (vel - 0.5) * 2.0)
            if brightness > 0.05:
                cutoff = min(self.sample_rate / 2 - 1, 2000.0 + brightness * 8000.0)
                sos_hi = _sig.butter(1, cutoff, btype="high", fs=self.sample_rate, output="sos")
                hi_shelf = _sig.sosfilt(sos_hi, raw)
                raw = raw + hi_shelf * brightness * 0.3
            elif vel < 0.4:
                # Darken at low velocity
                darkness = (0.4 - vel) / 0.4
                cutoff = min(self.sample_rate / 2 - 1, max(500.0, 8000.0 - darkness * 5000.0))
                sos_lp = _sig.butter(2, cutoff, btype="low", fs=self.sample_rate, output="sos")
                raw = raw * (1.0 - darkness * 0.6) + _sig.sosfilt(sos_lp, raw) * darkness * 0.6
            return raw

        lp_low, lp_high = family_config["lp_range"]
        hp_boost = family_config["hp_boost"]
        attack_bite = family_config["attack_bite"]

        # 1. Velocity-controlled low-pass filter
        # At vel=0.1, cutoff is near lp_low (dark). At vel=1.0, near lp_high (bright).
        lp_cutoff = lp_low + vel * (lp_high - lp_low)
        lp_cutoff = min(lp_cutoff, self.sample_rate / 2 - 1)
        lp_cutoff = max(lp_cutoff, 200.0)
        sos_lp = _sig.butter(2, lp_cutoff, btype="low", fs=self.sample_rate, output="sos")
        filtered = _sig.sosfilt(sos_lp, raw)

        # Blend between filtered and raw based on velocity
        # At pp: mostly filtered (dark). At ff: mostly raw (full spectrum).
        blend = vel**0.7  # non-linear: stays dark longer, then opens up
        raw = filtered * (1.0 - blend) + raw * blend

        # 2. High-frequency boost at forte and above
        if vel > 0.6 and hp_boost > 0:
            boost_amount = (vel - 0.6) / 0.4 * hp_boost
            hp_freq = min(self.sample_rate / 2 - 1, max(1000.0, lp_high * 0.5))
            sos_hi = _sig.butter(1, hp_freq, btype="high", fs=self.sample_rate, output="sos")
            hi_content = _sig.sosfilt(sos_hi, raw)
            raw = raw + hi_content * boost_amount

        # 3. Attack transient bite at high velocity (brass/plucked especially)
        if vel > 0.7 and attack_bite > 0:
            bite_amount = (vel - 0.7) / 0.3 * attack_bite
            # Short noise burst at the start of the note
            attack_len = min(int(0.015 * self.sample_rate), len(raw))
            if attack_len > 0:
                attack_env = np.linspace(1.0, 0.0, attack_len)
                rng = np.random.default_rng(int(vel * 1000) % (2**31))
                attack_noise = rng.standard_normal(attack_len) * bite_amount * 0.2
                raw[:attack_len] += attack_noise * attack_env

        return raw

    # ------------------------------------------------------------------
    # Articulation-aware synthesis (v170)
    # ------------------------------------------------------------------

    def _apply_articulation(
        self,
        raw: FloatArray,
        art: str,
        A: float,
        D: float,
        S: float,
        R: float,
        wave_type: str,
        n_samples: int,
        _sig,
    ) -> tuple[float, float, float, float, FloatArray]:
        """Modify ADSR and timbre based on articulation marking.

        Returns (A, D, S, R, modified_raw). The caller uses the returned
        ADSR values for envelope generation. The raw waveform may also be
        filtered or modified for timbral changes.

        This is where "how you play" becomes audible. A pizzicato note
        does not just get shorter - it gets a percussive burst with
        reduced harmonics. A muted brass note does not just get quieter -
        it gets a nasal, dark, stuffy quality.
        """
        sr = self.sample_rate
        nyq = sr / 2 - 1

        # ── String articulations ─────────────────────────────────────
        if art == "pizzicato":
            # Percussive pluck: instant attack, no sustain, fast decay
            A = 0.001
            D = max(0.08, D)
            S = 0.0
            R = min(R, 0.3)
            # Reduce upper harmonics (pluck is darker than bow)
            cutoff = min(nyq, 3000.0)
            sos = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos, raw)

        elif art == "spiccato":
            # Bouncing bow: short but more resonant than staccato
            A = max(0.002, A * 0.3)
            D = max(0.05, D)
            S = max(0.0, S * 0.2)
            R = min(R, 0.15)

        elif art == "tremolo":
            # Rapid bow tremolo: amplitude modulation at ~12-16 Hz
            t = np.arange(n_samples) / sr
            trem_rate = 14.0
            trem = 0.7 + 0.3 * np.sin(2 * np.pi * trem_rate * t)
            raw = raw * trem

        elif art == "harmonics":
            # Natural harmonics: pure sine, octave up, bell-like
            A = max(0.005, A)
            D = 0.15
            S = 0.2
            R = max(R, 0.8)
            # Filter to near-sine (kill most harmonics)
            freq = 440.0  # approximate, the actual freq is in the waveform
            cutoff = min(nyq, 2000.0)
            sos = _sig.butter(4, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos, raw)

        elif art == "sul_ponticello":
            # Bow near bridge: glassy, harsh, harmonic-rich
            cutoff = min(nyq, max(2000.0, 5000.0))
            sos = _sig.butter(2, cutoff, btype="high", fs=sr, output="sos")
            hi = _sig.sosfilt(sos, raw)
            raw = raw * 0.5 + hi * 0.6  # boost upper partials

        elif art == "sul_tasto":
            # Bow over fingerboard: breathy, dark, flute-like
            cutoff = min(nyq, 2500.0)
            sos = _sig.butter(3, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos, raw)
            A = max(A, 0.08)  # softer attack

        elif art == "col_legno":
            # Wood of the bow: percussive click with minimal pitch
            A = 0.001
            D = 0.05
            S = 0.0
            R = 0.05
            # Mostly noise burst
            rng = np.random.default_rng(42)
            noise = rng.standard_normal(n_samples)
            raw = raw * 0.2 + noise * 0.4
            cutoff = min(nyq, 4000.0)
            sos = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos, raw)

        elif art == "con_sordino":
            # Muted strings: darker, covered, reduced volume
            cutoff = min(nyq, 3000.0)
            sos = _sig.butter(3, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos, raw) * 0.7
            A = max(A, A * 1.3)  # slightly slower attack

        # ── Brass articulations ──────────────────────────────────────
        elif art == "muted":
            # Straight mute: nasal, stuffy, thin
            cutoff = min(nyq, 2500.0)
            sos_lp = _sig.butter(3, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.6
            # Add nasal resonance peak around 1500 Hz
            peak = min(1500.0, nyq)
            bw = 300.0
            lo = max(20.0, peak - bw)
            hi = min(nyq, peak + bw)
            if lo < hi:
                sos_bp = _sig.butter(2, [lo, hi], btype="band", fs=sr, output="sos")
                nasal = _sig.sosfilt(sos_bp, raw)
                raw = raw + nasal * 0.5

        elif art == "harmon_mute":
            # Harmon mute (wah-wah): very nasal, focused, Miles Davis tone
            cutoff = min(nyq, 2000.0)
            sos_lp = _sig.butter(4, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.5
            peak = min(1200.0, nyq)
            bw = 200.0
            lo = max(20.0, peak - bw)
            hi = min(nyq, peak + bw)
            if lo < hi:
                sos_bp = _sig.butter(2, [lo, hi], btype="band", fs=sr, output="sos")
                nasal = _sig.sosfilt(sos_bp, raw)
                raw = raw + nasal * 0.8

        elif art == "cup_mute":
            # Cup mute: warmer than straight mute, less nasal
            cutoff = min(nyq, 3500.0)
            sos_lp = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.65

        elif art == "stopped":
            # Hand-stopped horn: very stuffy, raised pitch feel
            cutoff = min(nyq, 1800.0)
            sos_lp = _sig.butter(4, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.4

        elif art == "flutter_tongue":
            # Flutter tongue: rapid roll, buzzy tremolo
            t = np.arange(n_samples) / sr
            flutter = 0.6 + 0.4 * np.sin(2 * np.pi * 25.0 * t)  # ~25 Hz roll
            raw = raw * flutter

        elif art == "sforzando":
            # Sforzando: hard attack burst then immediate drop
            A = 0.001
            D = 0.08
            S = max(S * 0.3, 0.0)

        # ── Woodwind articulations ───────────────────────────────────
        elif art == "overblown":
            # Overblown: playing in upper register, more harmonics
            cutoff = min(nyq, max(3000.0, 6000.0))
            sos_hp = _sig.butter(1, cutoff, btype="high", fs=sr, output="sos")
            hi = _sig.sosfilt(sos_hp, raw)
            raw = raw + hi * 0.4

        elif art == "subtone":
            # Subtone: breathy, soft, minimal overtones (jazz sax ballad)
            cutoff = min(nyq, 2000.0)
            sos_lp = _sig.butter(3, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.6
            # Add breath noise
            rng = np.random.default_rng(42)
            breath = rng.standard_normal(n_samples) * 0.08
            cutoff_b = min(nyq, 6000.0)
            sos_b = _sig.butter(2, cutoff_b, btype="low", fs=sr, output="sos")
            raw = raw + _sig.sosfilt(sos_b, breath)
            A = max(A, 0.06)

        elif art == "slap_tongue":
            # Slap tongue: percussive pop on attack (funk sax)
            A = 0.001
            D = max(0.03, D)
            attack_len = min(int(0.01 * sr), n_samples)
            if attack_len > 0:
                rng = np.random.default_rng(42)
                pop = rng.standard_normal(attack_len) * 0.5
                pop_env = np.linspace(1.0, 0.0, attack_len)
                raw[:attack_len] += pop * pop_env

        # ── Keyboard articulations ───────────────────────────────────
        elif art == "damped":
            # Piano with damper: very short sustain
            S = 0.0
            D = max(0.05, D * 0.3)
            R = min(R, 0.1)

        elif art == "una_corda":
            # Soft pedal: darker, fewer harmonics, quieter
            cutoff = min(nyq, 3000.0)
            sos_lp = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw) * 0.7

        elif art == "prepared":
            # Prepared piano: objects on strings, metallic/percussive
            rng = np.random.default_rng(42)
            metallic = rng.standard_normal(n_samples) * 0.15
            raw = raw * 0.5 + metallic * 0.3
            D = max(0.1, D)
            S = max(S * 0.3, 0.0)

        # ── Percussion implement articulations ───────────────────────
        elif art == "brush":
            # Brushes: swishy, softer attack, sustained wash
            rng = np.random.default_rng(42)
            swish = rng.standard_normal(n_samples) * 0.3
            cutoff = min(nyq, 8000.0)
            sos_lp = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            swish = _sig.sosfilt(sos_lp, swish)
            raw = raw * 0.3 + swish * 0.5
            A = max(A, 0.005)
            D = max(D, 0.15)

        elif art == "mallet":
            # Soft mallet: warmer, rounder attack, less stick click
            cutoff = min(nyq, 4000.0)
            sos_lp = _sig.butter(2, cutoff, btype="low", fs=sr, output="sos")
            raw = _sig.sosfilt(sos_lp, raw)
            A = max(A, 0.003)

        elif art == "rod" or art == "hot_rod":
            # Rods/hot rods: between stick and brush
            rng = np.random.default_rng(42)
            rod_noise = rng.standard_normal(n_samples) * 0.1
            raw = raw * 0.7 + rod_noise * 0.15

        elif art == "cross_stick" or art == "rim_click":
            # Cross-stick: sharp, woody click
            A = 0.001
            D = 0.03
            S = 0.0
            R = 0.03
            rng = np.random.default_rng(42)
            click = rng.standard_normal(n_samples) * 0.4
            cutoff = min(nyq, 5000.0)
            lo = max(20.0, 800.0)
            if lo < cutoff:
                sos_bp = _sig.butter(2, [lo, cutoff], btype="band", fs=sr, output="sos")
                raw = _sig.sosfilt(sos_bp, click)

        elif art == "rimshot":
            # Rimshot: loud crack, head + rim simultaneously
            rng = np.random.default_rng(42)
            crack = rng.standard_normal(n_samples) * 0.5
            raw = raw * 0.6 + crack * 0.4
            A = 0.001

        elif art == "dead_stroke":
            # Dead stroke: hit and immediately dampen
            A = 0.001
            D = 0.02
            S = 0.0
            R = 0.01

        elif art == "flam":
            # Flam: grace note before the main hit
            grace_len = min(int(0.025 * sr), n_samples // 4)
            if grace_len > 0:
                grace = raw[:grace_len].copy() * 0.4
                # Shift main hit slightly later
                shifted = np.zeros(n_samples)
                shifted[grace_len:] = raw[: n_samples - grace_len]
                shifted[:grace_len] = grace
                raw = shifted

        elif art == "roll":
            # Drum roll: rapid repeated hits via amplitude modulation
            t = np.arange(n_samples) / sr
            roll_rate = 20.0  # hits per second
            roll_env = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * roll_rate * t))
            raw = raw * roll_env

        # ── Generic articulations ────────────────────────────────────
        elif art == "staccato":
            # Staccato: sharper release, slightly shorter envelope
            R = min(R, 0.08)
            S = max(S * 0.3, 0.0)

        elif art == "legato":
            # Legato: slower attack, longer release, smoother
            A = max(A, A * 1.5)
            R = max(R, R * 1.5)

        return A, D, S, R, raw

    # ------------------------------------------------------------------
    # Track → mono array
    # ------------------------------------------------------------------

    def render_track(
        self,
        track: Track,
        bpm: float,
        total_beats: float,
        bpm_map: list[float] | None = None,
    ) -> FloatArray:
        """Render one track to a mono float64 array."""
        preset_key = track.instrument if track.instrument in self.PRESETS else "sine"
        preset = self.PRESETS[preset_key]
        beat_sec = 60.0 / bpm
        eighth_sec = beat_sec / 2.0  # one 8th note duration in seconds
        total_samples = (
            int(total_beats * beat_sec * self.sample_rate) + self.sample_rate
        )  # +1s tail
        buf = np.zeros(total_samples)

        # Density: random note dropout per track
        import random as _random

        density_rng = _random.Random(track.density_seed)
        use_density = track.density < 1.0 - 1e-6

        cursor = 0
        beat_idx = 0  # counts 8th-note grid steps for swing
        cumulative_beat = 0.0
        for beat in track.beats:
            # Use per-beat BPM from map if available
            if bpm_map:
                map_idx = min(int(cumulative_beat), len(bpm_map) - 1)
                local_bpm = bpm_map[map_idx] if map_idx >= 0 else bpm
                local_beat_sec = 60.0 / local_bpm
            else:
                local_beat_sec = beat_sec
            dur_sec = beat.duration * local_beat_sec
            cumulative_beat += beat.duration

            # Swing: delay every odd (2nd, 4th, ...) 8th-note step
            swing_offset = 0
            if track.swing > 0 and beat.duration <= 0.5:
                if beat_idx % 2 == 1:
                    swing_offset = int(track.swing * eighth_sec * self.sample_rate)
            beat_idx += max(1, int(beat.duration / 0.5))

            n_samples = int(dur_sec * self.sample_rate)
            event = beat.event

            if event is None:
                cursor += n_samples
                continue

            # Density: randomly skip this note/chord
            if use_density and density_rng.random() > track.density:
                cursor += n_samples
                continue

            if isinstance(event, Note):
                notes = [event]
            elif isinstance(event, Chord):
                notes = event.notes
            else:
                cursor += n_samples
                continue

            # Mix all notes in the beat
            mixed = np.zeros(n_samples)
            for note in notes:
                mixed += self._render_note(
                    note, n_samples, preset, instrument_name=track.instrument
                )
            if len(notes) > 1:
                mixed /= len(notes) ** 0.5  # RMS normalization

            write_pos = cursor + swing_offset
            end = min(write_pos + n_samples, total_samples)
            if end > write_pos:
                buf[write_pos:end] += mixed[: end - write_pos] * track.volume
            cursor += n_samples

        return buf

    def render_polytrack(
        self,
        ptrack,  # PolyphonicTrack
        bpm: float,
        total_beats: float,
        total_samples: int,
    ) -> FloatArray:
        """Render a PolyphonicTrack by summing all its notes into a stereo buffer.

        Each (Note, start_beat) pair is rendered independently and mixed at the
        correct time position. Notes that overlap play simultaneously.
        """
        import math

        preset_key = ptrack.instrument if ptrack.instrument in self.PRESETS else "sine"
        preset = self.PRESETS[preset_key]
        beat_sec = 60.0 / bpm
        buf = np.zeros((total_samples, 2))

        angle = (ptrack.pan + 1) / 2 * math.pi / 2
        l_gain = math.cos(angle)
        r_gain = math.sin(angle)

        for note, start_beat in ptrack.events:
            if note.pitch is None:
                continue
            start_sample = int(start_beat * beat_sec * self.sample_rate)
            n_samples = int(note.duration * beat_sec * self.sample_rate)
            if n_samples < 1 or start_sample >= total_samples:
                continue
            rendered = self._render_note(note, n_samples, preset, instrument_name=ptrack.instrument)
            end_sample = min(start_sample + n_samples, total_samples)
            clip_len = end_sample - start_sample
            buf[start_sample:end_sample, 0] += rendered[:clip_len] * l_gain * ptrack.volume
            buf[start_sample:end_sample, 1] += rendered[:clip_len] * r_gain * ptrack.volume

        return buf.astype(np.float64)

    # ------------------------------------------------------------------
    # Song → stereo array
    # ------------------------------------------------------------------

    def render_song(self, song: Song) -> FloatArray:
        """Render all tracks + voice tracks to a stereo float64 array, shape (N, 2).

        If song._effects is a dict mapping track name → callable(stereo, sr),
        each named track's stereo contribution is passed through its effect
        chain before being mixed into the master bus.
        """
        import math

        # Register song-level custom instruments
        for name, designer in getattr(song, "_custom_instruments", {}).items():
            self._custom_instruments[name] = designer

        has_instrument_tracks = bool(song.tracks)
        has_poly_tracks = bool(getattr(song, "poly_tracks", []))
        has_sample_tracks = bool(getattr(song, "sample_tracks", []))
        has_voice_tracks = bool(getattr(song, "voice_tracks", []))

        if (
            not has_instrument_tracks
            and not has_poly_tracks
            and not has_sample_tracks
            and not has_voice_tracks
        ):
            return np.zeros((self.sample_rate, 2))  # 1s silence

        # EffectsChain objects and plain callables are both accepted as values.
        # Legacy song._effects is redirected to song.effects via __setattr__/__getattr__.
        effects: dict = getattr(song, "effects", {}) or {}
        has_timed_tracks = (
            has_instrument_tracks or has_poly_tracks or has_sample_tracks or has_voice_tracks
        )
        total_beats = song.total_beats if has_timed_tracks else 8.0
        beat_sec = 60.0 / song.bpm
        total_samples = int(total_beats * beat_sec * self.sample_rate) + self.sample_rate

        stereo_mix = np.zeros((total_samples, 2))

        # ── Instrument tracks ──────────────────────────────────────────────
        for track in song.tracks:
            bmap = getattr(song, "bpm_map", None) or None
            mono = self.render_track(track, song.bpm, total_beats, bpm_map=bmap)
            n = min(len(mono), total_samples)
            angle = (track.pan + 1) / 2 * math.pi / 2
            l_gain = math.cos(angle)
            r_gain = math.sin(angle)
            track_stereo = np.zeros((total_samples, 2))
            track_stereo[:n, 0] = mono[:n] * l_gain
            track_stereo[:n, 1] = mono[:n] * r_gain
            if track.name in effects:
                try:
                    track_stereo = effects[track.name](track_stereo, self.sample_rate)
                except Exception:
                    pass
            stereo_mix += track_stereo

        # ── Polyphonic tracks ──────────────────────────────────────────────
        for ptrack in getattr(song, "poly_tracks", []):
            try:
                poly_stereo = self.render_polytrack(ptrack, song.bpm, total_beats, total_samples)
                if ptrack.name in effects:
                    try:
                        poly_stereo = effects[ptrack.name](poly_stereo, self.sample_rate)
                    except Exception:
                        pass
                stereo_mix += poly_stereo
            except Exception as e:
                print(f"[poly] track '{getattr(ptrack, 'name', '?')}' failed: {e}")

        # ── Sample tracks ──────────────────────────────────────────────────
        for strack in getattr(song, "sample_tracks", []):
            try:
                raw = strack.load_audio(self.sample_rate)
                beat_sec = 60.0 / song.bpm
                angle = (strack.pan + 1) / 2 * math.pi / 2
                l_gain = math.cos(angle) * strack.volume
                r_gain = math.sin(angle) * strack.volume
                for at_beat, semitones, velocity in strack.triggers:
                    # Pitch shift if needed
                    if semitones != 0:
                        from scipy import signal as _sig

                        ratio = 2 ** (semitones / 12.0)
                        shifted = _sig.resample(raw, max(1, int(len(raw) / ratio)))
                    else:
                        shifted = raw
                    start = int(at_beat * beat_sec * self.sample_rate)
                    end = min(start + len(shifted), total_samples)
                    clip = end - start
                    if clip > 0:
                        stereo_mix[start:end, 0] += shifted[:clip] * l_gain * velocity
                        stereo_mix[start:end, 1] += shifted[:clip] * r_gain * velocity
            except Exception as e:
                print(f"[sample] track '{getattr(strack, 'name', '?')}' failed: {e}")

        # ── Voice tracks ───────────────────────────────────────────────────
        from .voice import render_voice_track

        for vtrack in getattr(song, "voice_tracks", []):
            try:
                voice_stereo = render_voice_track(vtrack, song.bpm, total_beats, self.sample_rate)
                n = min(len(voice_stereo), total_samples)
                stereo_mix[:n] += voice_stereo[:n]
            except Exception as e:
                print(f"[voice] track '{getattr(vtrack, 'name', '?')}' failed: {e}")

        # DC offset removal: highpass at 5 Hz removes accumulated DC from filter chains
        try:
            from scipy import signal as _dc_sig

            sos_dc = _dc_sig.butter(1, 5.0, btype="high", fs=self.sample_rate, output="sos")
            stereo_mix[:, 0] = _dc_sig.sosfilt(sos_dc, stereo_mix[:, 0])
            stereo_mix[:, 1] = _dc_sig.sosfilt(sos_dc, stereo_mix[:, 1])
        except Exception:
            pass

        # Soft clip / normalize master bus
        # Use a smooth polynomial soft-clipper instead of tanh. tanh is
        # harsh at the knee - it introduces odd-harmonic distortion abruptly.
        # This curve is flatter in the passband and gentler at the clip point,
        # preserving dynamics better while still preventing overs.
        peak = np.max(np.abs(stereo_mix))
        if peak > 0:
            stereo_mix /= peak
        x = stereo_mix * 0.95
        # Smooth soft clip: y = x - (x^3)/3 for |x| < 1, clamped otherwise
        # (softer than tanh, preserves more of the original dynamic shape)
        stereo_mix = np.where(
            np.abs(x) < 1.0,
            x - (x**3) / 3.0,
            np.sign(x) * 2.0 / 3.0,
        )
        # Renormalize to use full range
        clip_peak = np.max(np.abs(stereo_mix))
        if clip_peak > 0:
            stereo_mix /= clip_peak

        # Apply master chain if set: EQ → compress → limit
        master = getattr(song, "_master_chain", None)
        if master:
            from .effects import compress, eq, limiter

            stereo_mix = eq(stereo_mix, self.sample_rate, bands=master["eq_bands"])
            stereo_mix = compress(
                stereo_mix,
                self.sample_rate,
                threshold=master["compress_threshold"],
                ratio=master["compress_ratio"],
            )
            stereo_mix = limiter(
                stereo_mix,
                self.sample_rate,
                ceiling=master["ceiling"],
            )

        return stereo_mix.astype(np.float64)
