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
        "supersaw": {"wave": "supersaw", "harmonics": 7, "A": 0.02, "D": 0.05, "S": 0.9, "R": 0.3},
        "reese_bass": {"wave": "reese", "harmonics": 6, "A": 0.03, "D": 0.1, "S": 0.8, "R": 0.4},
        "acid": {"wave": "sawtooth", "harmonics": 10, "A": 0.005, "D": 0.2, "S": 0.3, "R": 0.15},
        "hoover": {"wave": "hoover", "harmonics": 8, "A": 0.05, "D": 0.3, "S": 0.6, "R": 0.5},
        "stab": {"wave": "square", "harmonics": 6, "A": 0.005, "D": 0.08, "S": 0.0, "R": 0.1},
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

        env = self._adsr(n_samples, preset["A"], preset["D"], preset["S"], preset["R"])
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

    # ------------------------------------------------------------------
    # Song → stereo array
    # ------------------------------------------------------------------

    def render_song(self, song: Song) -> FloatArray:
        """Render all tracks to a stereo float64 array, shape (N, 2).

        If song._effects is a dict mapping track name → callable(stereo, sr),
        each named track's stereo contribution is passed through its effect
        chain before being mixed into the master bus.
        """
        import math

        if not song.tracks:
            return np.zeros((self.sample_rate, 2))  # 1s silence

        effects: dict = getattr(song, "_effects", {})
        total_beats = song.total_beats
        beat_sec = 60.0 / song.bpm
        total_samples = int(total_beats * beat_sec * self.sample_rate) + self.sample_rate

        stereo_mix = np.zeros((total_samples, 2))
        for track in song.tracks:
            mono = self.render_track(track, song.bpm, total_beats)
            n = min(len(mono), total_samples)
            # Equal-power pan: -1..1 → 0..π/2
            angle = (track.pan + 1) / 2 * math.pi / 2
            l_gain = math.cos(angle)
            r_gain = math.sin(angle)
            # Build stereo slice for this track
            track_stereo = np.zeros((total_samples, 2))
            track_stereo[:n, 0] = mono[:n] * l_gain
            track_stereo[:n, 1] = mono[:n] * r_gain
            # Apply per-track effect chain if defined
            if track.name in effects:
                try:
                    track_stereo = effects[track.name](track_stereo, self.sample_rate)
                except Exception:
                    pass  # never let an effect crash the render
            stereo_mix += track_stereo

        # Soft clip / normalize master bus
        peak = np.max(np.abs(stereo_mix))
        if peak > 0:
            stereo_mix /= peak
        stereo_mix = np.tanh(stereo_mix * 0.95)
        return stereo_mix.astype(np.float64)
