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
        "violin": {
            "wave": "sawtooth",
            "harmonics": 14,
            "vibrato_rate": 5.5,
            "vibrato_depth": 20,
            "vibrato_delay": 0.25,
            "A": 0.08,
            "D": 0.02,
            "S": 0.95,
            "R": 0.3,
        },
        "cello": {
            "wave": "sawtooth",
            "harmonics": 10,
            "vibrato_rate": 5.0,
            "vibrato_depth": 18,
            "vibrato_delay": 0.3,
            "A": 0.1,
            "D": 0.03,
            "S": 0.9,
            "R": 0.5,
        },
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
        "trumpet": {
            "wave": "square",
            "harmonics": 12,
            "vibrato_rate": 5.5,
            "vibrato_depth": 15,
            "vibrato_delay": 0.35,
            "A": 0.04,
            "D": 0.05,
            "S": 0.85,
            "R": 0.15,
        },
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
        "flute": {
            "wave": "sine",
            "harmonics": 2,
            "vibrato_rate": 5.0,
            "vibrato_depth": 15,
            "vibrato_delay": 0.2,
            "A": 0.06,
            "D": 0.02,
            "S": 0.9,
            "R": 0.2,
        },
        "oboe": {
            "wave": "square",
            "harmonics": 8,
            "vibrato_rate": 5.2,
            "vibrato_depth": 18,
            "vibrato_delay": 0.2,
            "A": 0.04,
            "D": 0.02,
            "S": 0.88,
            "R": 0.15,
        },
        "clarinet": {
            "wave": "square",
            "harmonics": 6,
            "vibrato_rate": 5.0,
            "vibrato_depth": 12,
            "vibrato_delay": 0.3,
            "A": 0.05,
            "D": 0.02,
            "S": 0.9,
            "R": 0.18,
        },
        "bassoon": {"wave": "sawtooth", "harmonics": 8, "A": 0.06, "D": 0.03, "S": 0.85, "R": 0.2},
        "saxophone": {
            "wave": "sawtooth",
            "harmonics": 10,
            "vibrato_rate": 5.3,
            "vibrato_depth": 22,
            "vibrato_delay": 0.2,
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
        "viola": {
            "wave": "sawtooth",
            "harmonics": 12,
            "vibrato_rate": 5.2,
            "vibrato_depth": 18,
            "vibrato_delay": 0.25,
            "A": 0.09,
            "D": 0.03,
            "S": 0.92,
            "R": 0.35,
        },
        "string_section": {
            "wave": "sawtooth",
            "harmonics": 10,
            "unison": 6,
            "detune_cents": 10,
            "vibrato_rate": 4.8,
            "vibrato_depth": 15,
            "vibrato_delay": 0.3,
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
        "erhu": {
            "wave": "sawtooth",
            "harmonics": 12,
            "vibrato_rate": 5.8,
            "vibrato_depth": 30,
            "vibrato_delay": 0.15,
            "A": 0.06,
            "D": 0.02,
            "S": 0.93,
            "R": 0.3,
        },
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
        "choir_aah": {
            "wave": "sawtooth",
            "harmonics": 6,
            "vibrato_rate": 5.5,
            "vibrato_depth": 25,
            "vibrato_delay": 0.3,
            "A": 0.15,
            "D": 0.1,
            "S": 0.85,
            "R": 0.5,
        },
        "choir_ooh": {"wave": "sine", "harmonics": 4, "A": 0.2, "D": 0.08, "S": 0.9, "R": 0.6},
        "vox_pad": {"wave": "triangle", "harmonics": 5, "A": 0.35, "D": 0.1, "S": 0.85, "R": 0.8},
        # ── Extended Synths (v170) ────────────────────────────────────────────
        "pulse": {"wave": "square", "harmonics": 10, "A": 0.01, "D": 0.05, "S": 0.85, "R": 0.2},
        "sync_lead": {
            "wave": "sawtooth",
            "harmonics": 16,
            "unison": 3,
            "detune_cents": 8,
            "A": 0.005,
            "D": 0.05,
            "S": 0.9,
            "R": 0.15,
        },
        "trance_lead": {
            "wave": "sawtooth",
            "harmonics": 12,
            "unison": 5,
            "detune_cents": 15,
            "A": 0.005,
            "D": 0.08,
            "S": 0.85,
            "R": 0.2,
        },
        "chiptune": {"wave": "square", "harmonics": 1, "A": 0.001, "D": 0.0, "S": 1.0, "R": 0.02},
        "ambient_pad": {"wave": "sine", "harmonics": 4, "A": 0.5, "D": 0.0, "S": 1.0, "R": 1.5},
        "dark_pad": {"wave": "sawtooth", "harmonics": 6, "A": 0.4, "D": 0.1, "S": 0.9, "R": 1.2},
        "glass_pad": {"wave": "triangle", "harmonics": 8, "A": 0.3, "D": 0.15, "S": 0.7, "R": 1.0},
        "warm_pad": {
            "wave": "sawtooth",
            "harmonics": 4,
            "unison": 4,
            "detune_cents": 6,
            "A": 0.4,
            "D": 0.05,
            "S": 0.95,
            "R": 1.0,
        },
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
        "pluck": {
            "wave": "sawtooth",
            "harmonics": 8,
            "filter_env": {
                "start": 200,
                "peak": 10000,
                "sustain": 1500,
                "end": 200,
                "attack": 0.005,
                "decay": 0.15,
                "release": 0.3,
            },
            "A": 0.001,
            "D": 0.4,
            "S": 0.1,
            "R": 0.5,
        },
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
        # Growl bass: formant-modulated bass, Skrillex monster sound
        # LFO sweeps between vowel formant shapes for that aggressive,
        # vocal quality. The sound that made Scary Monsters happen.
        "growl_bass": {
            "wave": "sawtooth",
            "harmonics": 16,
            "sub_osc": True,
            "sub_level": 0.3,
            "lfo_rate": 4.0,
            "lfo_min_cutoff": 200.0,
            "lfo_max_cutoff": 5000.0,
            "A": 0.005,
            "D": 0.1,
            "S": 0.85,
            "R": 0.15,
        },
        # Reese bass on steroids: 5-voice detuned for massive width
        "massive_bass": {
            "wave": "sawtooth",
            "harmonics": 12,
            "unison": 5,
            "detune_cents": 20,
            "sub_osc": True,
            "sub_level": 0.35,
            "filter_env": {
                "start": 150,
                "peak": 3000,
                "sustain": 800,
                "end": 150,
                "attack": 0.01,
                "decay": 0.15,
                "release": 0.2,
            },
            "A": 0.005,
            "D": 0.15,
            "S": 0.8,
            "R": 0.2,
        },
        # Screech lead: aggressive high-pitched lead for drops
        "screech_lead": {
            "wave": "square",
            "harmonics": 20,
            "unison": 3,
            "detune_cents": 15,
            "filter_env": {
                "start": 500,
                "peak": 12000,
                "sustain": 6000,
                "end": 500,
                "attack": 0.002,
                "decay": 0.08,
                "release": 0.15,
            },
            "A": 0.002,
            "D": 0.05,
            "S": 0.9,
            "R": 0.1,
        },
        # Acid bass: resonant square wave, TB-303 character
        "acid_303": {
            "wave": "square",
            "harmonics": 8,
            "filter_env": {
                "start": 100,
                "peak": 6000,
                "sustain": 400,
                "end": 100,
                "attack": 0.003,
                "decay": 0.08,
                "release": 0.1,
            },
            "A": 0.001,
            "D": 0.15,
            "S": 0.4,
            "R": 0.1,
        },
        # EDM supersaw lead: wide, bright, cutting through the mix
        "supersaw_lead": {
            "wave": "supersaw",
            "harmonics": 10,
            "filter_env": {
                "start": 2000,
                "peak": 14000,
                "sustain": 8000,
                "end": 2000,
                "attack": 0.005,
                "decay": 0.1,
                "release": 0.3,
            },
            "A": 0.005,
            "D": 0.08,
            "S": 0.85,
            "R": 0.3,
        },
        # Pad with slow filter sweep for atmospheric builds
        "evolving_pad": {
            "wave": "sawtooth",
            "harmonics": 6,
            "unison": 4,
            "detune_cents": 8,
            "filter_env": {
                "start": 300,
                "peak": 3000,
                "sustain": 2000,
                "end": 300,
                "attack": 1.0,
                "decay": 0.5,
                "release": 1.0,
            },
            "vibrato_rate": 3.5,
            "vibrato_depth": 8,
            "vibrato_delay": 0.5,
            "A": 0.5,
            "D": 0.0,
            "S": 1.0,
            "R": 1.5,
        },
        # EDM pluck: short, bright, percussive (for arpeggios)
        "edm_pluck": {
            "wave": "sawtooth",
            "harmonics": 10,
            "filter_env": {
                "start": 200,
                "peak": 12000,
                "sustain": 800,
                "end": 200,
                "attack": 0.001,
                "decay": 0.06,
                "release": 0.15,
            },
            "A": 0.001,
            "D": 0.2,
            "S": 0.0,
            "R": 0.3,
        },
        # Reese bass: deep, wide, menacing (DnB/dubstep)
        "deep_reese": {
            "wave": "reese",
            "harmonics": 8,
            "sub_osc": True,
            "sub_level": 0.4,
            "A": 0.01,
            "D": 0.0,
            "S": 1.0,
            "R": 0.2,
        },
        # ── Cinematic / SFX presets (v170) ────────────────────────────────
        "cinematic_hit": {
            "wave": "noise",
            "harmonics": 1,
            "sub_osc": True,
            "sub_level": 0.5,
            "A": 0.001,
            "D": 0.5,
            "S": 0.0,
            "R": 1.5,
        },
        "cinematic_drone": {
            "wave": "sawtooth",
            "harmonics": 4,
            "unison": 6,
            "detune_cents": 15,
            "vibrato_rate": 0.3,
            "vibrato_depth": 5,
            "vibrato_delay": 0.0,
            "A": 2.0,
            "D": 0.0,
            "S": 1.0,
            "R": 3.0,
        },
        "texture_grain": {
            "wave": "pink_noise",
            "harmonics": 1,
            "A": 0.5,
            "D": 0.0,
            "S": 1.0,
            "R": 1.0,
        },
        "texture_metal": {
            "wave": "square",
            "harmonics": 20,
            "A": 0.001,
            "D": 0.8,
            "S": 0.05,
            "R": 2.0,
        },
        "riser_synth": {
            "wave": "sawtooth",
            "harmonics": 12,
            "unison": 3,
            "detune_cents": 25,
            "filter_env": {
                "start": 100,
                "peak": 16000,
                "sustain": 14000,
                "end": 100,
                "attack": 2.0,
                "decay": 0.1,
                "release": 0.5,
            },
            "A": 0.3,
            "D": 0.0,
            "S": 1.0,
            "R": 0.5,
        },
        "sub_drop": {
            "wave": "sine",
            "harmonics": 1,
            "sub_osc": True,
            "sub_level": 0.6,
            "A": 0.001,
            "D": 1.0,
            "S": 0.0,
            "R": 0.5,
        },
        "horror_pad": {
            "wave": "sawtooth",
            "harmonics": 6,
            "unison": 4,
            "detune_cents": 30,
            "vibrato_rate": 4.0,
            "vibrato_depth": 40,
            "vibrato_delay": 0.0,
            "A": 1.0,
            "D": 0.0,
            "S": 1.0,
            "R": 2.0,
        },
        "sci_fi_sweep": {
            "wave": "square",
            "harmonics": 10,
            "filter_env": {
                "start": 100,
                "peak": 12000,
                "sustain": 8000,
                "end": 100,
                "attack": 0.5,
                "decay": 0.3,
                "release": 1.0,
            },
            "A": 0.1,
            "D": 0.0,
            "S": 1.0,
            "R": 0.5,
        },
        "bell_tone": {
            "wave": "fm",
            "harmonics": 5,
            "mod_ratio": 1.414,
            "A": 0.001,
            "D": 0.5,
            "S": 0.1,
            "R": 2.0,
        },
        "metallic_hit": {
            "wave": "fm",
            "harmonics": 8,
            "mod_ratio": 3.14159,
            "A": 0.001,
            "D": 0.3,
            "S": 0.0,
            "R": 0.8,
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
        "formant_i": {
            "wave": "formant",
            "harmonics": 8,
            "A": 0.05,
            "D": 0.04,
            "S": 0.92,
            "R": 0.25,
            "formant": "i",
        },
        "formant_u": {
            "wave": "formant",
            "harmonics": 8,
            "A": 0.07,
            "D": 0.05,
            "S": 0.88,
            "R": 0.35,
            "formant": "u",
        },
        # taiko: deep pitched drum for cinematic trailer hits
        "taiko": {"wave": "sine", "harmonics": 2, "A": 0.001, "D": 0.3, "S": 0.05, "R": 0.4},
        # ethnic percussion
        "tabla": {"wave": "sine", "harmonics": 3, "A": 0.001, "D": 0.15, "S": 0.0, "R": 0.2},
        "djembe": {"wave": "triangle", "harmonics": 4, "A": 0.001, "D": 0.2, "S": 0.0, "R": 0.3},
        # synth bass variants
        "moog_bass": {
            "wave": "moog",
            "harmonics": 10,
            "sub_osc": True,
            "sub_level": 0.25,
            "A": 0.01,
            "D": 0.15,
            "S": 0.7,
            "R": 0.2,
        },
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
            "_snare_pitch_drop": True,
        },
        "drums_hat": {
            "wave": "noise",
            "harmonics": 1,
            "A": 0.001,
            "D": 0.04,
            "S": 0.0,
            "R": 0.03,
            "_metallic": True,
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
        "drums_808": {
            "wave": "sine",
            "harmonics": 1,
            "A": 0.001,
            "D": 0.8,
            "S": 0.05,
            "R": 0.6,
            "_808_saturate": True,
        },
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
            # JP-8000 supersaw: 7 detuned sawtooths. Center voice louder than
            # detuned voices for clear pitch with width. Weights from Roland docs.
            detune_cents = np.array([-25, -17, -8, 0, 8, 17, 25])
            weights = np.array([0.5, 0.6, 0.8, 1.0, 0.8, 0.6, 0.5])
            total_weight = np.sum(weights)
            nyq = self.sample_rate / 2.0
            result = np.zeros(n_samples)
            for dc, w in zip(detune_cents, weights):
                f_det = freq * (2 ** (dc / 1200))
                max_k = max(1, int(nyq / f_det) - 1)
                ks = np.arange(1, min(harmonics + 1, max_k + 1))
                if len(ks) == 0:
                    continue
                result += (
                    w
                    * (2 / np.pi)
                    * np.sum(
                        ((-1) ** (ks + 1) / ks)[:, None]
                        * np.sin(2 * np.pi * f_det * ks[:, None] * t),
                        axis=0,
                    )
                )
            return result / total_weight

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
            # White noise — flat spectrum, equal energy per Hz
            rng = np.random.default_rng(int(freq * 1000) % (2**31))
            return rng.standard_normal(n_samples)

        elif wave == "pink_noise":
            # Pink noise (1/f) — equal energy per octave. Warmer, more natural.
            # Sounds like rain, waterfall, wind. Better for snares and cymbals
            # than white noise. Uses the Voss-McCartney algorithm.
            rng = np.random.default_rng(int(freq * 1000) % (2**31))
            white = rng.standard_normal(n_samples)
            # Approximate 1/f filter: cumulative sum of rows in a binary counter
            n_rows = 16
            rows = np.zeros(n_rows)
            pink = np.zeros(n_samples)
            for i in range(n_samples):
                # Find the lowest set bit position
                bit = 0
                n = i
                while n > 0 and n % 2 == 0:
                    bit += 1
                    n //= 2
                if bit < n_rows:
                    rows[bit] = rng.standard_normal()
                pink[i] = np.sum(rows) + white[i]
            # Normalize
            pk = np.max(np.abs(pink))
            if pk > 0:
                pink /= pk
            return pink

        elif wave == "brown_noise":
            # Brown noise (1/f^2) — deep, rumbling, like thunder.
            # Brownian motion: each sample is previous + random step.
            # Strongest in low frequencies. Great for sub-bass rumble
            # and thunder effects.
            rng = np.random.default_rng(int(freq * 1000) % (2**31))
            white = rng.standard_normal(n_samples)
            brown = np.cumsum(white)
            # Normalize and remove DC offset
            brown -= np.mean(brown)
            pk = np.max(np.abs(brown))
            if pk > 0:
                brown /= pk
            return brown

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
            # Karplus-Strong plucked string with body resonance.
            # The string vibration alone sounds thin and electric. A real guitar
            # or piano has a body that resonates sympathetically, adding warmth
            # and character. The body acts as a bandpass filter centered around
            # the instrument's resonant frequencies.
            period = max(2, int(self.sample_rate / max(freq, 1.0)))
            out = np.zeros(n_samples)
            rng = np.random.default_rng(int(freq * 137) % (2**31))
            buf = rng.uniform(-1.0, 1.0, period)
            # Frequency-dependent loss
            base_loss = 0.998
            freq_factor = min(freq / 4000.0, 0.01)
            loss = max(0.98, base_loss - freq_factor)
            for i in range(n_samples):
                out[i] = buf[i % period]
                buf[i % period] = loss * 0.5 * (buf[i % period] + buf[(i + 1) % period])

            # Body resonance: simulate the instrument body's resonant cavity.
            # Different instruments have different body shapes and materials
            # that create characteristic resonance patterns.
            from scipy import signal as _ks_sig

            nyq_ks = self.sample_rate / 2 - 1

            # Select body model based on instrument name
            _BODY_MODELS = {
                # Acoustic guitar: large body, spruce top, rosewood back
                "guitar_acoustic": [
                    (100.0, 60.0, 0.18),
                    (250.0, 80.0, 0.12),
                    (500.0, 120.0, 0.10),
                    (1200.0, 200.0, 0.06),
                ],
                "guitar_ks": [
                    (100.0, 60.0, 0.18),
                    (250.0, 80.0, 0.12),
                    (500.0, 120.0, 0.10),
                    (1200.0, 200.0, 0.06),
                ],
                # Classical/nylon guitar: wider body, cedar top, warmer
                "guitar_classical": [
                    (90.0, 50.0, 0.20),
                    (220.0, 70.0, 0.14),
                    (450.0, 100.0, 0.10),
                    (900.0, 160.0, 0.05),
                ],
                # Ukulele: tiny body, bright
                "ukulele": [(350.0, 100.0, 0.15), (700.0, 120.0, 0.10), (1500.0, 200.0, 0.08)],
                # Mandolin: small body, bright and cutting
                "mandolin": [(300.0, 80.0, 0.14), (600.0, 100.0, 0.10), (1800.0, 200.0, 0.08)],
                # Banjo: drum-head body, bright and punchy
                "banjo_ks": [(400.0, 100.0, 0.16), (800.0, 150.0, 0.12), (2000.0, 250.0, 0.08)],
                # Upright bass: huge body, deep resonance
                "contrabass": [
                    (60.0, 40.0, 0.20),
                    (150.0, 60.0, 0.15),
                    (350.0, 80.0, 0.08),
                    (700.0, 120.0, 0.04),
                ],
                "bass": [(80.0, 50.0, 0.16), (200.0, 70.0, 0.12), (500.0, 100.0, 0.06)],
                # Harp: tall soundboard, wide range
                "harp": [
                    (120.0, 60.0, 0.14),
                    (300.0, 80.0, 0.10),
                    (800.0, 150.0, 0.07),
                    (1500.0, 200.0, 0.04),
                ],
                "harp_ks": [
                    (120.0, 60.0, 0.14),
                    (300.0, 80.0, 0.10),
                    (800.0, 150.0, 0.07),
                    (1500.0, 200.0, 0.04),
                ],
                # Sitar: long neck, gourd body, bright buzzing bridge
                "sitar_ks": [
                    (150.0, 50.0, 0.16),
                    (400.0, 80.0, 0.12),
                    (1000.0, 150.0, 0.10),
                    (2500.0, 250.0, 0.08),
                ],
                # Koto: wooden body, silk strings
                "koto_ks": [(200.0, 70.0, 0.14), (500.0, 100.0, 0.10), (1100.0, 180.0, 0.06)],
            }
            # Select model based on current instrument (set by _render_note)
            inst_name = getattr(self, "_current_instrument", None) or ""
            body_freqs = _BODY_MODELS.get(
                inst_name, [(180.0, 80.0, 0.15), (500.0, 120.0, 0.10), (1200.0, 200.0, 0.06)]
            )
            body = np.zeros(n_samples)
            for center, bw, gain in body_freqs:
                lo = max(20.0, min(center - bw / 2, nyq_ks))
                hi = min(center + bw / 2, nyq_ks)
                if lo < hi:
                    sos = _ks_sig.butter(
                        2, [lo, hi], btype="band", fs=self.sample_rate, output="sos"
                    )
                    body += _ks_sig.sosfilt(sos, out) * gain
            out = out * 0.8 + body  # blend body with direct string
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
        self,
        note: Note,
        n_samples: int,
        preset: dict,
        instrument_name: str = "",
        prev_freq: float = 0.0,
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
            # Add attack transient for punch (noise burst in first 5ms)
            click_len = min(int(0.005 * self.sample_rate), n_samples)
            if click_len > 0:
                rng = np.random.default_rng(int(freq * 77) % (2**31))
                click = rng.standard_normal(click_len) * 0.3
                click *= np.linspace(1.0, 0.0, click_len)
                raw[:click_len] += click
            # 808 saturation: gentle overdrive for that warm, fuzzy sub-bass character
            if preset.get("_808_saturate"):
                raw = np.tanh(raw * 1.8) * 0.8  # soft clip at mild drive
        # Snare pitch-drop: tone body drops slightly in pitch (like real snare head)
        if preset.get("_snare_pitch_drop") and not is_pitch_drop:
            t_sn = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            freq_env_sn = freq * np.exp(-15.0 * t_sn)  # gentle drop
            tone = np.sin(2 * np.pi * np.cumsum(freq_env_sn) / self.sample_rate)
            # Will be mixed with filtered noise later in the noise_presets section
            raw = tone

        # Clap multi-transient: 3-4 rapid hits (real handclap is multiple fingers landing)
        if "clap" in str(instrument_name).lower() and n_samples > 200:
            rng_clap = np.random.default_rng(int(freq * 55) % (2**31))
            clap_noise = rng_clap.standard_normal(n_samples)
            # 3 rapid transients at 0ms, 10ms, 20ms
            multi = np.zeros(n_samples)
            for delay_ms, gain in [(0, 0.6), (10, 0.8), (20, 1.0)]:
                pos = int(delay_ms * self.sample_rate / 1000)
                if pos < n_samples:
                    attack_len = min(int(0.005 * self.sample_rate), n_samples - pos)
                    if attack_len > 0:
                        env_hit = np.exp(-np.linspace(0, 8, attack_len))
                        multi[pos : pos + attack_len] += (
                            clap_noise[pos : pos + attack_len] * env_hit * gain
                        )
            raw = multi

        if wave_type == "porta" and prev_freq > 0 and abs(prev_freq - freq) > 0.5:
            # Portamento: smooth glide from previous note's frequency to this note.
            # The glide takes ~50ms then holds at the target. Uses exponential
            # interpolation (sounds more natural than linear for pitch).
            t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            glide_time = preset.get("porta_time", 0.05)
            glide_samples = min(int(glide_time * self.sample_rate), n_samples)
            freq_curve = np.full(n_samples, freq)
            if glide_samples > 1:
                # Exponential interpolation from prev_freq to freq
                glide_t = np.linspace(0, 1, glide_samples)
                # Log-space interpolation (pitch is logarithmic)
                log_start = np.log2(max(prev_freq, 20.0))
                log_end = np.log2(max(freq, 20.0))
                log_curve = log_start + (log_end - log_start) * (1 - np.exp(-5 * glide_t))
                log_curve[-1] = log_end
                freq_curve[:glide_samples] = 2**log_curve
            # Generate waveform with time-varying frequency via phase accumulation
            phase = np.cumsum(freq_curve / self.sample_rate) * 2 * np.pi
            harmonics = self._harmonics_cache.get(wave_type, 8)
            nyq = self.sample_rate / 2.0
            # Sawtooth with gliding fundamental
            ks = np.arange(1, min(harmonics + 1, max(2, int(nyq / max(freq, 20)))))
            raw = np.zeros(n_samples)
            for k in ks:
                raw += ((-1) ** (k + 1) / k) * np.sin(k * phase)
            raw *= 2 / np.pi
        else:
            # Pass FM ratio hint and instrument name to _wave
            self._fm_ratio_hint = preset.get("mod_ratio", None)
            self._current_instrument = instrument_name
            raw = self._wave(wave_type, freq, n_samples)
            self._fm_ratio_hint = None
            self._current_instrument = None

        # ── Unison/detune: stack multiple detuned copies for fat sounds ──
        unison_voices = preset.get("unison", 0)
        if unison_voices > 1:
            detune_cents = preset.get("detune_cents", 10)
            stack = raw.copy()
            for v in range(1, unison_voices):
                # Spread detune evenly: -detune to +detune
                frac = (v / (unison_voices - 1)) * 2 - 1  # -1 to +1
                cents = frac * detune_cents
                f_det = freq * (2 ** (cents / 1200.0))
                self._fm_ratio_hint = preset.get("mod_ratio", None)
                voice = self._wave(wave_type, f_det, n_samples)
                self._fm_ratio_hint = None
                stack += voice
            raw = stack / unison_voices

        # ── Sub-oscillator: sine one octave below for bass weight ────────
        if preset.get("sub_osc", False):
            sub_level = preset.get("sub_level", 0.3)
            t_sub = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            sub = np.sin(2 * np.pi * (freq / 2) * t_sub) * sub_level
            raw = raw + sub

        # Noise layer for snare / clap / cymbals / crash / ride / hat
        from scipy import signal as _sig_drum

        noise_presets = {"snare", "clap", "cymbals", "crash", "ride", "hat"}
        instrument_str = str(instrument_name).lower()
        if any(k in instrument_str for k in noise_presets):
            rng = np.random.default_rng(int(freq * 137) % (2**31))
            noise = rng.standard_normal(n_samples)

            if "snare" in instrument_str:
                # Bandpass filter noise for snare wire character (2-8 kHz)
                bp_lo = min(2000.0, self.sample_rate / 2 - 1)
                bp_hi = min(8000.0, self.sample_rate / 2 - 1)
                if bp_lo < bp_hi:
                    sos_bp = _sig_drum.butter(
                        2, [bp_lo, bp_hi], btype="band", fs=self.sample_rate, output="sos"
                    )
                    noise = _sig_drum.sosfilt(sos_bp, noise)
                raw = raw * 0.4 + noise * 0.6

            elif "hat" in instrument_str or preset.get("_metallic"):
                # Metallic hi-hat: ring-modulated noise for inharmonic character
                # Real hi-hats are two cymbals vibrating against each other
                t_hat = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
                # 6 inharmonic frequencies (non-integer ratios = metallic)
                metal_freqs = [205.3, 304.4, 369.6, 522.7, 800.0, 1053.0]
                ring = np.zeros(n_samples)
                for mf in metal_freqs:
                    ring += np.sin(2 * np.pi * mf * t_hat) * 0.15
                raw = noise * 0.5 + (noise * ring) * 0.5
                # Highpass to remove low rumble
                hp_freq = min(4000.0, self.sample_rate / 2 - 1)
                sos_hp = _sig_drum.butter(
                    2, hp_freq, btype="high", fs=self.sample_rate, output="sos"
                )
                raw = _sig_drum.sosfilt(sos_hp, raw)

            elif (
                "cymbal" in instrument_str or "crash" in instrument_str or "ride" in instrument_str
            ):
                # Cymbals: noise + inharmonic ring mod (like hi-hat but lower, wider)
                t_cym = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
                metal_freqs = [340.0, 467.0, 581.0, 728.0, 1043.0]
                ring = np.zeros(n_samples)
                for mf in metal_freqs:
                    ring += np.sin(2 * np.pi * mf * t_cym) * 0.18
                raw = raw * 0.3 + noise * 0.3 + (noise * ring) * 0.4

            else:
                raw = raw * 0.5 + noise * 0.5

        # ── Acoustic realism noise layers ─────────────────────────────────
        # Real instruments have non-pitched noise components that make them
        # sound alive: breath in a flute, rosin on a bow, hammer thump on a
        # piano, fret buzz on a bass. Without these, synthesis sounds sterile.
        from scipy import signal as _sig

        inst = instrument_name.lower()

        # Breath noise for woodwinds (highpass filtered noise blended at attack)
        _BREATH_INSTRUMENTS = {
            "flute",
            "alto_flute",
            "oboe",
            "clarinet",
            "bass_clarinet",
            "bassoon",
            "contrabassoon",
            "cor_anglais",
            "english_horn",
            "saxophone",
            "soprano_sax",
            "tenor_sax",
            "bari_sax",
            "harmonica",
            "accordion",
            "bandoneon",
            "bagpipe",
        }
        if inst in _BREATH_INSTRUMENTS and n_samples > 100:
            rng_b = np.random.default_rng(int(freq * 200) % (2**31))
            breath = rng_b.standard_normal(n_samples) * 0.06
            # Shape: louder at attack, fades to sustain level
            breath_env = np.ones(n_samples) * 0.3
            attack_len = min(int(0.04 * self.sample_rate), n_samples)
            if attack_len > 0:
                breath_env[:attack_len] = np.linspace(1.0, 0.3, attack_len)
            breath *= breath_env
            # Highpass to keep only airy component
            hp = min(2000.0, self.sample_rate / 2 - 1)
            sos_hp = _sig.butter(2, hp, btype="high", fs=self.sample_rate, output="sos")
            breath = _sig.sosfilt(sos_hp, breath)
            raw = raw + breath

        # Bow rosin noise for strings (friction texture, strongest at attack)
        _BOW_INSTRUMENTS = {
            "violin",
            "viola",
            "cello",
            "contrabass",
            "erhu",
            "string_section",
            "strings",
        }
        if inst in _BOW_INSTRUMENTS and n_samples > 100:
            art = getattr(note, "articulation", None)
            if art not in ("pizzicato", "col_legno", "harmonics"):
                rng_r = np.random.default_rng(int(freq * 300) % (2**31))
                rosin = rng_r.standard_normal(n_samples) * 0.04
                # Strongest at attack, fades quickly
                rosin_env = np.exp(-np.linspace(0, 8, n_samples))
                rosin_env = np.maximum(rosin_env, 0.15)  # maintain subtle floor
                rosin *= rosin_env
                # Bandpass around 2-6 kHz (rosin friction character)
                bp_lo = min(2000.0, self.sample_rate / 2 - 1)
                bp_hi = min(6000.0, self.sample_rate / 2 - 1)
                if bp_lo < bp_hi:
                    sos_bp = _sig.butter(
                        2, [bp_lo, bp_hi], btype="band", fs=self.sample_rate, output="sos"
                    )
                    rosin = _sig.sosfilt(sos_bp, rosin)
                raw = raw + rosin

        # Brass lip buzz on attack (the 'brrt' that precedes the clean tone)
        _BRASS_INSTRUMENTS = {
            "trumpet",
            "trombone",
            "french_horn",
            "tuba",
            "euphonium",
            "cornet",
            "flugelhorn",
            "piccolo_trumpet",
            "bass_trombone",
            "horn_section",
        }
        if inst in _BRASS_INSTRUMENTS and n_samples > 200:
            art = getattr(note, "articulation", None)
            if art not in ("muted", "harmon_mute", "cup_mute", "stopped"):
                buzz_len = min(int(0.012 * self.sample_rate), n_samples)
                if buzz_len > 0:
                    rng_buzz = np.random.default_rng(int(freq * 250) % (2**31))
                    buzz = rng_buzz.standard_normal(buzz_len) * 0.08
                    # Bandpass the buzz to lip frequency range (100-400 Hz)
                    bp_lo = min(100.0, self.sample_rate / 2 - 1)
                    bp_hi = min(400.0, self.sample_rate / 2 - 1)
                    if bp_lo < bp_hi:
                        sos_bz = _sig.butter(
                            2, [bp_lo, bp_hi], btype="band", fs=self.sample_rate, output="sos"
                        )
                        buzz = _sig.sosfilt(sos_bz, np.pad(buzz, (0, n_samples - buzz_len)))[
                            :buzz_len
                        ]
                    buzz *= np.linspace(1.0, 0.0, buzz_len)
                    raw[:buzz_len] += buzz

        # Reed buzz for sax/clarinet (vibrating reed component, adds edge)
        _REED_INSTRUMENTS = {
            "saxophone",
            "clarinet",
            "bass_clarinet",
            "oboe",
            "soprano_sax",
            "tenor_sax",
            "bari_sax",
            "cor_anglais",
            "english_horn",
            "bassoon",
            "contrabassoon",
        }
        if inst in _REED_INSTRUMENTS and n_samples > 200:
            rng_rd = np.random.default_rng(int(freq * 350) % (2**31))
            reed = rng_rd.standard_normal(n_samples) * 0.03
            # Reed buzz is at the fundamental + odd harmonics
            t_reed = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            reed_tone = np.sin(2 * np.pi * freq * 2.0 * t_reed) * 0.02
            reed += reed_tone
            reed_env = np.ones(n_samples) * 0.4
            att = min(int(0.02 * self.sample_rate), n_samples)
            if att > 0:
                reed_env[:att] = np.linspace(1.0, 0.4, att)
            reed *= reed_env
            # Highpass to keep only the buzzy component
            hp_rd = min(1500.0, self.sample_rate / 2 - 1)
            sos_rd = _sig.butter(2, hp_rd, btype="high", fs=self.sample_rate, output="sos")
            reed = _sig.sosfilt(sos_rd, reed)
            raw = raw + reed

        # Hammond B3 key click (percussive contact noise on attack)
        if inst in ("organ",) and n_samples > 100:
            click_len = min(int(0.003 * self.sample_rate), n_samples)
            if click_len > 0:
                rng_kc = np.random.default_rng(int(freq * 450) % (2**31))
                keyclick = rng_kc.standard_normal(click_len) * 0.15
                keyclick *= np.linspace(1.0, 0.0, click_len)
                # Bandpass the click (1-4 kHz, the characteristic Hammond click)
                kc_lo = min(1000.0, self.sample_rate / 2 - 1)
                kc_hi = min(4000.0, self.sample_rate / 2 - 1)
                if kc_lo < kc_hi:
                    sos_kc = _sig.butter(
                        2, [kc_lo, kc_hi], btype="band", fs=self.sample_rate, output="sos"
                    )
                    keyclick = _sig.sosfilt(sos_kc, np.pad(keyclick, (0, n_samples - click_len)))[
                        :click_len
                    ]
                raw[:click_len] += keyclick

        # Piano hammer thump (short low-frequency bump at attack)
        if inst in ("piano", "rhodes", "wurlitzer") and n_samples > 100:
            thump_len = min(int(0.008 * self.sample_rate), n_samples)
            if thump_len > 0:
                rng_t = np.random.default_rng(int(freq * 400) % (2**31))
                thump = rng_t.standard_normal(thump_len) * 0.12
                thump *= np.linspace(1.0, 0.0, thump_len)
                # Lowpass to keep only the thump (below 500 Hz)
                lp = min(500.0, self.sample_rate / 2 - 1)
                sos_lp = _sig.butter(2, lp, btype="low", fs=self.sample_rate, output="sos")
                thump = _sig.sosfilt(sos_lp, np.pad(thump, (0, n_samples - thump_len)))[:thump_len]
                raw[:thump_len] += thump

        # Sympathetic string resonance for piano
        # When a piano string is struck, other undamped strings that share
        # harmonics with the fundamental ring sympathetically. This is the
        # "bloom" that makes a grand piano sound huge. Without it, each note
        # is isolated. With it, the piano sings as a whole instrument.
        if inst == "piano" and n_samples > 500:
            nyq_sym = self.sample_rate / 2 - 1
            sympathetic = np.zeros(n_samples)
            # Strings at octave, fifth, and double octave resonate most
            sym_ratios = [2.0, 3.0, 4.0, 1.5]  # octave, 12th, double oct, fifth
            for ratio in sym_ratios:
                sym_freq = freq * ratio
                if sym_freq < nyq_sym and sym_freq > 20:
                    # Very quiet sine at the sympathetic frequency with slow decay
                    t_sym = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
                    sym_env = np.exp(-t_sym * 2.0) * 0.02  # very subtle
                    sympathetic += np.sin(2 * np.pi * sym_freq * t_sym) * sym_env
            raw = raw + sympathetic

        # Velocity-sensitive filter for pads and synths (filter opens with velocity)
        _PAD_INSTRUMENTS = {
            "pad",
            "warm_pad",
            "dark_pad",
            "glass_pad",
            "ambient_pad",
            "poly_synth",
            "fm_pad",
        }
        if inst in _PAD_INSTRUMENTS and n_samples > 100:
            vel_cutoff = 800.0 + note.velocity * 11200.0
            vel_cutoff = min(vel_cutoff, self.sample_rate / 2 - 1)
            sos_vf = _sig.butter(2, vel_cutoff, btype="low", fs=self.sample_rate, output="sos")
            raw = _sig.sosfilt(sos_vf, raw)

        # Per-note filter envelope (separate ADSR on cutoff, EDM essential)
        # Presets can define filter_env with start/peak/sustain/end frequencies
        if "filter_env" in preset and n_samples > 200:
            fe = preset["filter_env"]
            nyq_fe = self.sample_rate / 2 - 1
            fe_start = min(fe.get("start", 200), nyq_fe)
            fe_peak = min(fe.get("peak", 8000), nyq_fe)
            fe_sustain = min(fe.get("sustain", 2000), nyq_fe)
            fe_end = min(fe.get("end", 200), nyq_fe)
            fe_attack = int(fe.get("attack", 0.01) * self.sample_rate)
            fe_decay = int(fe.get("decay", 0.2) * self.sample_rate)
            fe_release = int(fe.get("release", 0.3) * self.sample_rate)
            fe_sustain_len = max(0, n_samples - fe_attack - fe_decay - fe_release)

            cutoff_curve = np.zeros(n_samples)
            p = 0
            if fe_attack > 0:
                end_a = min(p + fe_attack, n_samples)
                cutoff_curve[p:end_a] = np.linspace(fe_start, fe_peak, end_a - p)
                p = end_a
            if fe_decay > 0:
                end_d = min(p + fe_decay, n_samples)
                cutoff_curve[p:end_d] = np.linspace(fe_peak, fe_sustain, end_d - p)
                p = end_d
            if fe_sustain_len > 0:
                end_s = min(p + fe_sustain_len, n_samples)
                cutoff_curve[p:end_s] = fe_sustain
                p = end_s
            if fe_release > 0:
                end_r = min(p + fe_release, n_samples)
                cutoff_curve[p:end_r] = np.linspace(fe_sustain, fe_end, end_r - p)
                p = end_r
            cutoff_curve[p:] = fe_end
            cutoff_curve = np.clip(cutoff_curve, 20.0, nyq_fe)

            # Apply in blocks
            block_fe = 128
            filtered_fe = np.zeros(n_samples)
            for s_fe in range(0, n_samples, block_fe):
                e_fe = min(s_fe + block_fe, n_samples)
                c_fe = float(np.mean(cutoff_curve[s_fe:e_fe]))
                c_fe = max(20.0, min(c_fe, nyq_fe))
                sos_fe = _sig.butter(2, c_fe, btype="low", fs=self.sample_rate, output="sos")
                filtered_fe[s_fe:e_fe] = _sig.sosfilt(sos_fe, raw[s_fe:e_fe])
            raw = filtered_fe

        # ── Per-note LFO filter (wobble bass + formant) ──────────────────

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
            # Formant filter: vowel resonances via bandpass peaks.
            # Frequencies from Peterson & Barney (1952), adult male averages.
            # Bandwidths from Fant (1960): F1~60-100Hz, F2~80-120Hz, F3~100-150Hz.
            # F4 added for naturalness (Hillenbrand 1995).
            FORMANTS = {
                #       (freq, gain, bandwidth) for F1, F2, F3, F4
                "a": [(730, 0.9, 80), (1090, 0.6, 90), (2440, 0.3, 120), (3300, 0.15, 150)],
                "e": [(530, 0.9, 70), (1840, 0.7, 100), (2480, 0.3, 120), (3300, 0.15, 150)],
                "i": [(270, 0.9, 60), (2290, 0.8, 100), (3010, 0.3, 130), (3700, 0.15, 160)],
                "o": [(570, 0.9, 70), (840, 0.6, 80), (2410, 0.2, 120), (3300, 0.1, 150)],
                "u": [(300, 0.9, 60), (870, 0.5, 80), (2240, 0.2, 110), (3300, 0.1, 150)],
            }
            vowel = preset.get("formant", "a")
            fmts = FORMANTS.get(vowel, FORMANTS["a"])
            result = np.zeros(n_samples)
            nyq = self.sample_rate / 2 - 1
            for f_center, gain, bw in fmts:
                f_center = min(f_center, nyq)
                low = max(20.0, f_center - bw / 2)
                high = min(nyq, f_center + bw / 2)
                if low < high:
                    sos = _sig.butter(
                        2, [low, high], btype="band", fs=self.sample_rate, output="sos"
                    )
                    result += _sig.sosfilt(sos, raw) * gain
            raw = raw * 0.15 + result * 0.85

        # ── Taiko / djembe: pitch drop with noise attack ─────────────────
        if wave_type in ("taiko", "djembe", "tabla"):
            rng = np.random.default_rng(int(freq * 99) % (2**31))
            attack_noise = rng.standard_normal(n_samples)
            # Short attack noise burst
            noise_env = np.zeros(n_samples)
            attack_end = min(int(0.02 * self.sample_rate), n_samples)
            noise_env[:attack_end] = np.linspace(1, 0, attack_end)
            raw = raw * 0.75 + attack_noise * noise_env * 0.4

        # ── Register-dependent tonal tilt ─────────────────────────────────
        # Low notes are naturally warmer (more low-end energy relative to
        # harmonics). High notes are naturally brighter. This applies a subtle
        # shelving EQ based on where the note sits in its instrument range.
        # Without this, every octave sounds the same. With it, the bass
        # register is warm and the treble register sparkles.
        if freq > 0 and n_samples > 200:
            midi_val = note.midi or 60
            # Center the tilt around middle C (MIDI 60)
            tilt = (midi_val - 60) / 48.0  # -1 at MIDI 12, 0 at 60, +1 at 108
            nyq_tilt = self.sample_rate / 2 - 1
            if tilt < -0.1:
                # Low register: gentle lowpass warmth
                warm_cutoff = min(nyq_tilt, max(1000.0, 6000.0 + tilt * 4000.0))
                sos_warm = _sig.butter(
                    1, warm_cutoff, btype="low", fs=self.sample_rate, output="sos"
                )
                raw = raw * 0.7 + _sig.sosfilt(sos_warm, raw) * 0.3
            elif tilt > 0.1:
                # High register: subtle presence boost
                bright_freq = min(nyq_tilt, max(2000.0, 3000.0 + tilt * 2000.0))
                sos_bright = _sig.butter(
                    1, bright_freq, btype="high", fs=self.sample_rate, output="sos"
                )
                raw = raw + _sig.sosfilt(sos_bright, raw) * tilt * 0.15

        # ── Velocity-sensitive attack time ────────────────────────────────
        # Real instruments respond faster when played harder. A piano key
        # struck fortissimo has a ~2ms attack. The same key at pianissimo
        # has ~15ms. This couples velocity to the ADSR attack time.
        A, D, S, R = preset["A"], preset["D"], preset["S"], preset["R"]
        vel = note.velocity
        if vel > 0.01:
            # Scale attack: pp = 150% of preset attack, ff = 70% of preset attack
            attack_scale = 1.5 - vel * 0.8  # 1.5 at vel=0, 0.7 at vel=1.0
            A = max(0.001, A * attack_scale)

        # ── Pitch drift on sustained notes ────────────────────────────────
        # Real instruments are not perfectly in tune. Strings drift slightly
        # as the player's hand warms the neck. Wind instruments drift with
        # breath pressure. Pianos stay put (they are tuned metal). This adds
        # a very slow, random walk in pitch (max +-5 cents) that makes
        # sustained notes sound alive instead of frozen.
        _DRIFT_INSTRUMENTS = {
            "violin",
            "viola",
            "cello",
            "contrabass",
            "erhu",
            "strings",
            "string_section",
            "flute",
            "oboe",
            "clarinet",
            "saxophone",
            "trumpet",
            "trombone",
            "french_horn",
            "choir_aah",
            "choir_ooh",
            "soprano_sax",
            "tenor_sax",
            "bari_sax",
        }
        if inst in _DRIFT_INSTRUMENTS and n_samples > 2000:
            drift_rng = np.random.default_rng(int(freq * 600) % (2**31))
            # Random walk: cumulative sum of tiny steps, scaled to max +-5 cents
            n_steps = n_samples // 256 + 1
            walk = np.cumsum(drift_rng.normal(0, 1, n_steps))
            # Normalize to +-5 cents
            walk_max = np.max(np.abs(walk))
            if walk_max > 0:
                walk = walk / walk_max * 5.0  # +-5 cents max
            # Upsample to full note length
            drift_cents = np.interp(
                np.linspace(0, 1, n_samples),
                np.linspace(0, 1, n_steps),
                walk,
            )
            # Convert cents to frequency ratio and apply via phase modulation
            drift_ratio = 2 ** (drift_cents / 1200.0) - 1.0
            drift_offset = drift_ratio * self.sample_rate / max(freq, 20.0)
            indices_d = np.clip(
                np.arange(n_samples, dtype=np.float64) - drift_offset, 0, n_samples - 1
            )
            lo_d = np.floor(indices_d).astype(int)
            hi_d = np.minimum(lo_d + 1, n_samples - 1)
            frac_d = indices_d - lo_d
            raw = raw[lo_d] * (1 - frac_d) + raw[hi_d] * frac_d

        # ── Articulation-aware envelope and timbre (v170) ─────────────────
        art = getattr(note, "articulation", None)

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

        # Piano damper release noise (subtle thump when key releases)
        if inst in ("piano",) and R > 0.05 and n_samples > 500:
            r_start = n_samples - int(R * self.sample_rate)
            r_start = max(0, r_start)
            release_len = n_samples - r_start
            if release_len > 50:
                rng_d = np.random.default_rng(int(freq * 500) % (2**31))
                damper = rng_d.standard_normal(release_len) * 0.02
                damper *= np.linspace(1.0, 0.0, release_len)
                lp_d = min(300.0, self.sample_rate / 2 - 1)
                sos_d = _sig.butter(1, lp_d, btype="low", fs=self.sample_rate, output="sos")
                damper = _sig.sosfilt(sos_d, damper)
                raw[r_start : r_start + release_len] += damper[:release_len]

        # String release noise (finger lift, fret buzz, bow lift)
        # When a guitarist lifts their finger, there is a brief squeak from
        # the string sliding on the fret. When a bow lifts, there is a tiny
        # scrape. These release noises are subliminal but their absence
        # makes synthesized strings sound sterile.
        _RELEASE_NOISE_INSTRUMENTS = {
            "guitar_acoustic",
            "guitar_electric",
            "guitar_ks",
            "bass",
            "banjo_ks",
            "ukulele",
            "mandolin",
        }
        if inst in _RELEASE_NOISE_INSTRUMENTS and n_samples > 500:
            r_samples = max(1, int(R * self.sample_rate))
            r_start = max(0, n_samples - r_samples)
            rel_len = n_samples - r_start
            if rel_len > 50:
                rng_rel = np.random.default_rng(int(freq * 700) % (2**31))
                release_noise = rng_rel.standard_normal(rel_len) * 0.04
                release_noise *= np.linspace(0.5, 0.0, rel_len)  # fade out
                # Highpass for string squeak character (2-8 kHz)
                nyq_rn = self.sample_rate / 2 - 1
                hp_rn = min(2000.0, nyq_rn)
                sos_rn = _sig.butter(2, hp_rn, btype="high", fs=self.sample_rate, output="sos")
                padded_rn = np.zeros(n_samples)
                padded_rn[r_start : r_start + rel_len] = release_noise
                padded_rn = _sig.sosfilt(sos_rn, padded_rn)
                raw = raw + padded_rn * env  # apply envelope so it fades naturally

        # ── Velocity-to-timbre: every instrument family responds differently ──
        # Real instruments change spectral content with dynamics, not just volume.
        # Soft = darker/rounder, loud = brighter/edgier. The amount and character
        # of this change depends on the instrument family.
        vel = note.velocity
        if vel > 0.01 and n_samples > 64:
            raw = self._apply_velocity_timbre(raw, vel, wave_type, preset, instrument_name, _sig)

        # ── Per-note vibrato with delayed onset ──────────────────────────
        # Presets can specify vibrato_rate (Hz) and vibrato_depth (cents).
        # vibrato_delay (seconds) controls how long before vibrato fades in
        # (standard for strings, voice - no vibrato at attack, ramps in).
        vib_rate = preset.get("vibrato_rate", 0.0)
        vib_depth = preset.get("vibrato_depth", 0.0)
        if vib_rate > 0 and vib_depth > 0 and n_samples > 100:
            vib_delay = preset.get("vibrato_delay", 0.2)
            t_vib = np.arange(n_samples) / self.sample_rate
            # Fade-in envelope: vibrato ramps in after delay
            delay_samples = int(vib_delay * self.sample_rate)
            vib_env = np.zeros(n_samples)
            ramp_len = min(int(0.15 * self.sample_rate), n_samples - delay_samples)
            if ramp_len > 0 and delay_samples < n_samples:
                vib_env[delay_samples : delay_samples + ramp_len] = np.linspace(0, 1, ramp_len)
                vib_env[delay_samples + ramp_len :] = 1.0
            # Apply pitch vibrato via phase modulation
            depth_ratio = 2 ** (vib_depth / 1200.0) - 1.0
            phase_mod = depth_ratio * np.sin(2 * np.pi * vib_rate * t_vib) * vib_env
            # Modulate the raw signal by time-warping
            offsets = phase_mod * self.sample_rate / max(freq, 20.0)
            indices = np.clip(np.arange(n_samples, dtype=np.float64) - offsets, 0, n_samples - 1)
            lo = np.floor(indices).astype(int)
            hi = np.minimum(lo + 1, n_samples - 1)
            frac = indices - lo
            raw = raw[lo] * (1 - frac) + raw[hi] * frac

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

        # ── Humanization engine ────────────────────────────────────────
        # Real musicians are not perfectly on time or perfectly consistent.
        # Micro-timing jitter, velocity fluctuation, and pitch drift create
        # the feel that separates a live performance from a MIDI playback.
        # These are subtle (3-10ms timing, +-5% velocity) but critical.
        humanize = getattr(track, "humanize", 0.0)  # 0.0 = robot, 1.0 = very human
        h_rng = np.random.default_rng(hash(track.name) % (2**31) if track.name else 42)

        cursor = 0
        beat_idx = 0
        cumulative_beat = 0.0
        prev_freq = 0.0
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
                    note,
                    n_samples,
                    preset,
                    instrument_name=track.instrument,
                    prev_freq=prev_freq,
                )
                if note.freq and note.freq > 0:
                    prev_freq = note.freq
            if len(notes) > 1:
                mixed /= len(notes) ** 0.5  # RMS normalization

            # Humanize: micro-timing jitter + velocity variation
            timing_offset = 0
            if humanize > 0:
                # Micro-timing: +-3ms at humanize=0.3, +-10ms at humanize=1.0
                max_jitter_ms = 3.0 + humanize * 7.0
                jitter_samples = int(
                    h_rng.normal(0, max_jitter_ms * 0.001 * self.sample_rate * 0.3)
                )
                timing_offset = jitter_samples
                # Velocity variation: +-3% at humanize=0.3, +-8% at humanize=1.0
                vel_var = 1.0 + h_rng.normal(0, humanize * 0.03)
                mixed *= np.clip(vel_var, 0.85, 1.15)

            write_pos = cursor + swing_offset + timing_offset
            write_pos = max(0, write_pos)

            # Legato crossfade: when articulation is legato, overlap the start
            # of this note with the tail of the previous by 10ms to create
            # a smooth transition instead of a click at the boundary.
            xfade_len = 0
            if notes and hasattr(notes[0], "articulation") and notes[0].articulation == "legato":
                xfade_len = min(int(0.01 * self.sample_rate), n_samples // 4)
                if xfade_len > 1 and write_pos > xfade_len:
                    # Fade in the start of this note
                    fade_in = np.linspace(0.0, 1.0, xfade_len)
                    mixed[:xfade_len] *= fade_in

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

        # ── Automatic gain staging ────────────────────────────────────────
        # Scale headroom based on track count to prevent clipping from
        # summing too many loud tracks. The more tracks, the more we
        # need to attenuate each one before summing.
        n_tracks = (
            len(song.tracks)
            + len(getattr(song, "poly_tracks", []))
            + len(getattr(song, "sample_tracks", []))
            + len(getattr(song, "voice_tracks", []))
        )
        headroom = 1.0 / max(n_tracks**0.4, 1.0)  # sqrt-ish scaling

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
            stereo_mix += track_stereo * headroom

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

        # Analog-style stereo crosstalk (console channel bleed)
        # Real analog consoles have tiny amounts of signal bleeding between
        # the L and R buses. This creates a subtle stereo coherence that
        # makes the mix feel unified rather than two separate mono signals.
        # Amount is very small (1-3%) but audibly glues the stereo image.
        crosstalk = 0.02
        left = stereo_mix[:, 0].copy()
        right = stereo_mix[:, 1].copy()
        stereo_mix[:, 0] = left + right * crosstalk
        stereo_mix[:, 1] = right + left * crosstalk

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
