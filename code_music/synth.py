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
        # ── Choir / Vocal ─────────────────────────────────────────────────────
        "choir_aah": {"wave": "sawtooth", "harmonics": 6, "A": 0.15, "D": 0.1, "S": 0.85, "R": 0.5},
        "choir_ooh": {"wave": "sine", "harmonics": 4, "A": 0.2, "D": 0.08, "S": 0.9, "R": 0.6},
        "vox_pad": {"wave": "triangle", "harmonics": 5, "A": 0.35, "D": 0.1, "S": 0.85, "R": 0.8},
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

    def _wave(self, wave: str, freq: float, n_samples: int) -> FloatArray:
        """Generate waveform using additive/spectral synthesis (fully vectorised)."""
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        # Look up harmonics from ANY matching preset key that uses this wave name
        harmonics = next(
            (p["harmonics"] for p in self.PRESETS.values() if p.get("wave") == wave),
            8,
        )

        if wave == "sine":
            return np.sin(2 * np.pi * freq * t)

        elif wave == "square":
            ks = np.arange(1, harmonics + 1, 2)
            return (4 / np.pi) * np.sum(
                (1 / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t), axis=0
            )

        elif wave == "sawtooth":
            ks = np.arange(1, harmonics + 1)
            signs = (-1) ** (ks + 1)
            return (2 / np.pi) * np.sum(
                (signs / ks)[:, None] * np.sin(2 * np.pi * freq * ks[:, None] * t), axis=0
            )

        elif wave == "triangle":
            ks = np.arange(0, harmonics)
            ns = 2 * ks + 1
            signs = (-1) ** ks
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
            # Simple 2-operator FM synthesis: carrier modulated by a sine at ratio 2
            mod_ratio = 2.0
            mod_depth = freq * 0.8
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
            for i in range(n_samples):
                out[i] = buf[i % period]
                # Averaging filter with loss factor (0.996 ≈ very little damping)
                loss = 0.996
                buf[i % period] = loss * 0.5 * (buf[i % period] + buf[(i + 1) % period])
            return out

        else:
            return np.sin(2 * np.pi * freq * t)

    def _adsr(self, n_samples: int, A: float, D: float, S: float, R: float) -> FloatArray:
        """Build ADSR amplitude envelope over n_samples."""
        sr = self.sample_rate
        a_s = min(int(A * sr), n_samples)
        d_s = min(int(D * sr), n_samples - a_s)
        # Reserve release at the tail; sustain fills the gap
        r_s = min(int(R * sr), n_samples - a_s - d_s)
        s_s = max(0, n_samples - a_s - d_s - r_s)

        env = np.zeros(n_samples)
        if a_s > 0:
            env[:a_s] = np.linspace(0, 1, a_s)
        if d_s > 0:
            env[a_s : a_s + d_s] = np.linspace(1, S, d_s)
        if s_s > 0:
            env[a_s + d_s : a_s + d_s + s_s] = S
        if r_s > 0:
            start = a_s + d_s + s_s
            env[start : start + r_s] = np.linspace(S, 0, r_s)
        return env

    # ------------------------------------------------------------------
    # Per-note rendering
    # ------------------------------------------------------------------

    def _render_note(self, note: Note, n_samples: int, preset: dict) -> FloatArray:
        freq = note.freq
        if freq is None or freq <= 0:
            return np.zeros(n_samples)

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
            raw = self._wave(wave_type, freq, n_samples)

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

        env = self._adsr(n_samples, preset["A"], preset["D"], preset["S"], preset["R"])

        # ── Velocity-to-timbre: louder = brighter (more high harmonics) ──
        # Applies to piano, guitar, and acoustic instruments
        # Use wave_type and preset structure to detect acoustic instruments
        vel_timbre_waves = {"sine", "karplus"}
        is_acoustic = wave_type in vel_timbre_waves and preset.get("A", 0.1) < 0.02
        if is_acoustic and note.velocity > 0.01:
            # Boost high frequencies proportional to velocity
            brightness = max(0.0, (note.velocity - 0.5) * 2.0)  # 0 at vel=0.5, 1 at vel=1.0
            if brightness > 0.05:
                cutoff = min(self.sample_rate / 2 - 1, 1000.0 + brightness * 8000.0)
                sos_hi = _sig.butter(1, cutoff, btype="high", fs=self.sample_rate, output="sos")
                hi_shelf = _sig.sosfilt(sos_hi, raw)
                raw = raw + hi_shelf * brightness * 0.4

        return raw * env * note.velocity

    # ------------------------------------------------------------------
    # Track → mono array
    # ------------------------------------------------------------------

    def render_track(self, track: Track, bpm: float, total_beats: float) -> FloatArray:
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
        for beat in track.beats:
            dur_sec = beat.duration * beat_sec

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
                mixed += self._render_note(note, n_samples, preset)
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
            rendered = self._render_note(note, n_samples, preset)
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

        # Support both new song.effects dict and legacy song._effects dict.
        # EffectsChain objects and plain callables are both accepted as values.
        effects: dict = getattr(song, "effects", {}) or getattr(song, "_effects", {})
        has_timed_tracks = (
            has_instrument_tracks or has_poly_tracks or has_sample_tracks or has_voice_tracks
        )
        total_beats = song.total_beats if has_timed_tracks else 8.0
        beat_sec = 60.0 / song.bpm
        total_samples = int(total_beats * beat_sec * self.sample_rate) + self.sample_rate

        stereo_mix = np.zeros((total_samples, 2))

        # ── Instrument tracks ──────────────────────────────────────────────
        for track in song.tracks:
            mono = self.render_track(track, song.bpm, total_beats)
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

        # Soft clip / normalize master bus
        peak = np.max(np.abs(stereo_mix))
        if peak > 0:
            stereo_mix /= peak
        stereo_mix = np.tanh(stereo_mix * 0.95)

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
