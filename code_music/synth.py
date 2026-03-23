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
        # (wave_func, harmonics, attack, decay, sustain, release)
        "sine": {"wave": "sine", "harmonics": 1, "A": 0.01, "D": 0.1, "S": 0.9, "R": 0.3},
        "square": {"wave": "square", "harmonics": 8, "A": 0.01, "D": 0.05, "S": 0.8, "R": 0.2},
        "sawtooth": {"wave": "sawtooth", "harmonics": 12, "A": 0.02, "D": 0.1, "S": 0.7, "R": 0.4},
        "triangle": {"wave": "triangle", "harmonics": 6, "A": 0.02, "D": 0.08, "S": 0.85, "R": 0.3},
        "piano": {"wave": "sine", "harmonics": 5, "A": 0.005, "D": 0.3, "S": 0.4, "R": 0.8},
        "organ": {"wave": "sine", "harmonics": 4, "A": 0.01, "D": 0.0, "S": 1.0, "R": 0.1},
        "bass": {"wave": "sawtooth", "harmonics": 6, "A": 0.02, "D": 0.2, "S": 0.6, "R": 0.3},
        "pad": {"wave": "sine", "harmonics": 3, "A": 0.3, "D": 0.0, "S": 1.0, "R": 0.8},
        "pluck": {"wave": "sawtooth", "harmonics": 8, "A": 0.001, "D": 0.4, "S": 0.1, "R": 0.5},
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
    }

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    # ------------------------------------------------------------------
    # Waveform generators
    # ------------------------------------------------------------------

    def _wave(self, wave: str, freq: float, n_samples: int) -> FloatArray:
        """Generate one-cycle-aligned waveform using additive synthesis."""
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        harmonics = self.PRESETS.get(wave, {}).get("harmonics", 1)
        # Dispatch
        if wave == "sine":
            return np.sin(2 * np.pi * freq * t)
        elif wave == "square":
            sig = np.zeros(n_samples)
            for k in range(1, harmonics + 1, 2):
                sig += (1 / k) * np.sin(2 * np.pi * freq * k * t)
            return sig * (4 / np.pi)
        elif wave == "sawtooth":
            sig = np.zeros(n_samples)
            for k in range(1, harmonics + 1):
                sig += ((-1) ** (k + 1) / k) * np.sin(2 * np.pi * freq * k * t)
            return sig * (2 / np.pi)
        elif wave == "triangle":
            sig = np.zeros(n_samples)
            for k in range(0, harmonics):
                n = 2 * k + 1
                sig += ((-1) ** k / n**2) * np.sin(2 * np.pi * freq * n * t)
            return sig * (8 / (np.pi**2))
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

        # Pitch-drop for kick drum feel
        if preset.get("wave") == "sine" and preset.get("A", 0.01) < 0.005:
            t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
            freq_env = freq * np.exp(-30 * t)
            raw = np.sin(2 * np.pi * np.cumsum(freq_env) / self.sample_rate)
        else:
            raw = self._wave(preset["wave"], freq, n_samples)

        # Add noise layer for snare
        if "snare" in str(preset):
            noise = np.random.normal(0, 0.4, n_samples)
            raw = raw * 0.6 + noise * 0.4

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
        total_samples = (
            int(total_beats * beat_sec * self.sample_rate) + self.sample_rate
        )  # +1s tail
        buf = np.zeros(total_samples)

        cursor = 0
        for beat in track.beats:
            dur_sec = beat.duration * beat_sec
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

            end = min(cursor + n_samples, total_samples)
            buf[cursor:end] += mixed[: end - cursor] * track.volume
            cursor += n_samples

        return buf

    # ------------------------------------------------------------------
    # Song → stereo array
    # ------------------------------------------------------------------

    def render_song(self, song: Song) -> FloatArray:
        """Render all tracks to a stereo float64 array, shape (N, 2)."""
        if not song.tracks:
            return np.zeros((self.sample_rate, 2))  # 1s silence

        total_beats = song.total_beats
        beat_sec = 60.0 / song.bpm
        total_samples = int(total_beats * beat_sec * self.sample_rate) + self.sample_rate

        mono = np.zeros(total_samples)
        for track in song.tracks:
            rendered = self.render_track(track, song.bpm, total_beats)
            n = min(len(rendered), total_samples)
            mono[:n] += rendered[:n]

        # Soft clip / normalize
        peak = np.max(np.abs(mono))
        if peak > 0:
            mono /= peak
        mono = np.tanh(mono * 0.95)  # gentle saturation

        # Mono → stereo
        stereo = np.column_stack([mono, mono])
        return stereo.astype(np.float64)
