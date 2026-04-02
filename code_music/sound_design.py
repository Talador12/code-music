"""Custom sound design — build instruments from raw oscillators, noise, filters, envelopes.

No WAV files, no external libraries beyond numpy. Design a sound once,
register it, and use it at any pitch in any song.

Example::

    from code_music.sound_design import SoundDesigner

    supersaw = (
        SoundDesigner("supersaw")
        .add_osc("sawtooth", detune_cents=0, volume=0.3)
        .add_osc("sawtooth", detune_cents=7, volume=0.25)
        .add_osc("sawtooth", detune_cents=-7, volume=0.25)
        .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.5)
        .filter("lowpass", cutoff=4000, resonance=0.3)
    )

    song.register_instrument("supersaw", supersaw)
    lead = song.add_track(Track(instrument="supersaw"))
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


# ---------------------------------------------------------------------------
# Oscillators — pure numpy, zero deps
# ---------------------------------------------------------------------------


def _osc_sine(freq: float, n: int, sr: int) -> FloatArray:
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t)


def _osc_sawtooth(freq: float, n: int, sr: int, harmonics: int = 16) -> FloatArray:
    t = np.arange(n) / sr
    out = np.zeros(n)
    for k in range(1, harmonics + 1):
        out += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * freq * t) / k
    return out * (2.0 / np.pi)


def _osc_square(freq: float, n: int, sr: int, harmonics: int = 16) -> FloatArray:
    t = np.arange(n) / sr
    out = np.zeros(n)
    for k in range(1, harmonics * 2, 2):
        out += np.sin(2 * np.pi * k * freq * t) / k
    return out * (4.0 / np.pi)


def _osc_triangle(freq: float, n: int, sr: int, harmonics: int = 12) -> FloatArray:
    t = np.arange(n) / sr
    out = np.zeros(n)
    for k in range(harmonics):
        n_harm = 2 * k + 1
        out += ((-1) ** k) * np.sin(2 * np.pi * n_harm * freq * t) / (n_harm**2)
    return out * (8.0 / (np.pi**2))


def _osc_noise_white(n: int, seed: int | None = None) -> FloatArray:
    rng = np.random.default_rng(seed)
    return rng.standard_normal(n)


def _osc_noise_pink(n: int, seed: int | None = None) -> FloatArray:
    """Pink noise via Voss-McCartney algorithm."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    # Simple 1/f approximation: cumulative filter
    b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004709510])
    a = np.array([1.0, -2.494956002, 2.017265875, -0.522189400])
    from scipy.signal import lfilter

    pink = lfilter(b, a, white)
    return pink / (np.max(np.abs(pink)) + 1e-10)


def _osc_noise_brown(n: int, seed: int | None = None) -> FloatArray:
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    brown = np.cumsum(white)
    return brown / (np.max(np.abs(brown)) + 1e-10)


_OSC_FUNCS = {
    "sine": _osc_sine,
    "sawtooth": _osc_sawtooth,
    "square": _osc_square,
    "triangle": _osc_triangle,
}

_NOISE_FUNCS = {
    "white": _osc_noise_white,
    "pink": _osc_noise_pink,
    "brown": _osc_noise_brown,
}


# ---------------------------------------------------------------------------
# Biquad filter — no scipy needed for basic LP/HP/BP
# ---------------------------------------------------------------------------


def _biquad_coeffs(
    filter_type: str, cutoff: float, sr: int, q: float = 0.707
) -> tuple[FloatArray, FloatArray]:
    """Compute biquad filter coefficients (b, a)."""
    w0 = 2 * np.pi * min(cutoff, sr / 2 - 1) / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)

    if filter_type == "lowpass":
        b0 = (1 - cos_w0) / 2
        b1 = 1 - cos_w0
        b2 = b0
    elif filter_type == "highpass":
        b0 = (1 + cos_w0) / 2
        b1 = -(1 + cos_w0)
        b2 = b0
    elif filter_type == "bandpass":
        b0 = alpha
        b1 = 0.0
        b2 = -alpha
    else:
        raise ValueError(f"Unknown filter type: {filter_type!r}")

    a0 = 1 + alpha
    a1 = -2 * cos_w0
    a2 = 1 - alpha

    return (
        np.array([b0 / a0, b1 / a0, b2 / a0]),
        np.array([1.0, a1 / a0, a2 / a0]),
    )


def _apply_biquad(signal: FloatArray, b: FloatArray, a: FloatArray) -> FloatArray:
    """Apply biquad filter using direct form II transposed."""
    out = np.zeros_like(signal)
    z1 = 0.0
    z2 = 0.0
    for i in range(len(signal)):
        x = signal[i]
        y = b[0] * x + z1
        z1 = b[1] * x - a[1] * y + z2
        z2 = b[2] * x - a[2] * y
        out[i] = y
    return out


# ---------------------------------------------------------------------------
# ADSR envelope
# ---------------------------------------------------------------------------


def _adsr(
    n: int, sr: int, attack: float, decay: float, sustain: float, release: float
) -> FloatArray:
    """Generate an ADSR amplitude envelope."""
    a_samples = int(attack * sr)
    d_samples = int(decay * sr)
    r_samples = int(release * sr)
    s_samples = max(0, n - a_samples - d_samples - r_samples)

    env = np.concatenate(
        [
            np.linspace(0, 1, max(1, a_samples)),  # attack
            np.linspace(1, sustain, max(1, d_samples)),  # decay
            np.full(s_samples, sustain),  # sustain
            np.linspace(sustain, 0, max(1, r_samples)),  # release
        ]
    )
    # Trim or pad to exact length
    if len(env) > n:
        env = env[:n]
    elif len(env) < n:
        env = np.concatenate([env, np.zeros(n - len(env))])
    return env


# ---------------------------------------------------------------------------
# SoundDesigner — the main class
# ---------------------------------------------------------------------------


class _OscLayer:
    __slots__ = ("wave", "detune_cents", "volume", "harmonics")

    def __init__(self, wave: str, detune_cents: float, volume: float, harmonics: int):
        self.wave = wave
        self.detune_cents = detune_cents
        self.volume = volume
        self.harmonics = harmonics


class _NoiseLayer:
    __slots__ = ("noise_type", "volume", "seed")

    def __init__(self, noise_type: str, volume: float, seed: int | None):
        self.noise_type = noise_type
        self.volume = volume
        self.seed = seed


class _FilterSpec:
    __slots__ = ("filter_type", "cutoff", "resonance")

    def __init__(self, filter_type: str, cutoff: float, resonance: float):
        self.filter_type = filter_type
        self.cutoff = cutoff
        self.resonance = resonance


class _FMLayer:
    __slots__ = ("carrier_wave", "mod_ratio", "mod_index", "volume")

    def __init__(self, carrier_wave: str, mod_ratio: float, mod_index: float, volume: float):
        self.carrier_wave = carrier_wave
        self.mod_ratio = mod_ratio
        self.mod_index = mod_index
        self.volume = volume


class _WavetableLayer:
    __slots__ = ("table", "volume", "detune_cents")

    def __init__(self, table: FloatArray, volume: float, detune_cents: float):
        self.table = table
        self.volume = volume
        self.detune_cents = detune_cents


class _LFOSpec:
    __slots__ = ("target", "rate", "depth", "wave")

    def __init__(self, target: str, rate: float, depth: float, wave: str):
        self.target = target
        self.rate = rate
        self.depth = depth
        self.wave = wave


# ---------------------------------------------------------------------------
# Wavetable helpers
# ---------------------------------------------------------------------------


class Wavetable:
    """A single-cycle waveform stored as a numpy array.

    Example::

        wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25])
        organ = SoundDesigner("organ").add_wavetable(wt, volume=0.6)
    """

    def __init__(self, table: FloatArray) -> None:
        self.table = np.asarray(table, dtype=np.float64)
        peak = np.max(np.abs(self.table))
        if peak > 0:
            self.table /= peak

    @classmethod
    def from_harmonics(cls, amplitudes: list[float], size: int = 2048) -> "Wavetable":
        """Build a wavetable from harmonic amplitudes (additive synthesis).

        Args:
            amplitudes: Amplitude of each harmonic (1st = fundamental).
            size:       Number of samples in the single-cycle table.
        """
        t = np.linspace(0, 2 * np.pi, size, endpoint=False)
        wave = np.zeros(size)
        for k, amp in enumerate(amplitudes, 1):
            wave += amp * np.sin(k * t)
        return cls(wave)

    @classmethod
    def from_wave(cls, wave: str, size: int = 2048) -> "Wavetable":
        """Build a wavetable from a named wave shape."""
        if wave == "sine":
            t = np.linspace(0, 2 * np.pi, size, endpoint=False)
            return cls(np.sin(t))
        elif wave == "sawtooth":
            return cls(np.linspace(-1, 1, size, endpoint=False))
        elif wave == "square":
            table = np.ones(size)
            table[size // 2 :] = -1.0
            return cls(table)
        elif wave == "triangle":
            half = size // 2
            table = np.concatenate([np.linspace(-1, 1, half), np.linspace(1, -1, size - half)])
            return cls(table)
        else:
            raise ValueError(f"Unknown wave {wave!r}")

    def morph(self, other: "Wavetable", amount: float = 0.5) -> "Wavetable":
        """Interpolate between this wavetable and another.

        Args:
            other:  Target wavetable.
            amount: 0.0 = fully self, 1.0 = fully other.
        """
        size = max(len(self.table), len(other.table))
        a = np.interp(
            np.linspace(0, len(self.table) - 1, size), np.arange(len(self.table)), self.table
        )
        b = np.interp(
            np.linspace(0, len(other.table) - 1, size), np.arange(len(other.table)), other.table
        )
        return Wavetable(a * (1.0 - amount) + b * amount)

    def to_list(self) -> list[float]:
        """Serialize to a plain list (JSON-compatible)."""
        return self.table.tolist()

    @classmethod
    def from_list(cls, data: list[float]) -> "Wavetable":
        """Reconstruct from a serialized list."""
        return cls(np.array(data, dtype=np.float64))


class SoundDesigner:
    """Build custom instruments from oscillators, noise, filters, and envelopes.

    Design a sound by chaining methods, then register it as an instrument
    and use it in any song at any pitch.

    Example::

        kick808 = (
            SoundDesigner("808_kick")
            .add_osc("sine", volume=1.0)
            .envelope(attack=0.001, decay=0.5, sustain=0.0, release=0.3)
            .pitch_envelope(start_multiplier=4.0, end_multiplier=1.0, duration=0.05)
        )

        song.register_instrument("808_kick", kick808)
        tr = song.add_track(Track(instrument="808_kick"))
        tr.add(Note("C", 2, 2.0))
    """

    def __init__(self, name: str = "custom") -> None:
        self.name = name
        self._oscs: list[_OscLayer] = []
        self._noises: list[_NoiseLayer] = []
        self._fm_layers: list[_FMLayer] = []
        self._wavetable_layers: list[_WavetableLayer] = []
        self._env: tuple[float, float, float, float] = (0.01, 0.1, 0.8, 0.3)
        self._filter: _FilterSpec | None = None
        self._lfos: list[_LFOSpec] = []
        self._pitch_env: tuple[float, float, float] | None = None  # (start_mult, end_mult, dur)

    # -- Oscillator layers -------------------------------------------------

    def add_osc(
        self,
        wave: str = "sine",
        detune_cents: float = 0.0,
        volume: float = 1.0,
        harmonics: int = 16,
    ) -> "SoundDesigner":
        """Add an oscillator layer.

        Args:
            wave:         Waveform: sine, sawtooth, square, triangle.
            detune_cents: Detune from base frequency in cents (100 cents = 1 semitone).
            volume:       Layer volume (0.0–1.0).
            harmonics:    Number of harmonics for additive synthesis.
        """
        if wave not in _OSC_FUNCS:
            raise ValueError(f"Unknown wave {wave!r}. Choose: {sorted(_OSC_FUNCS)}")
        self._oscs.append(_OscLayer(wave, detune_cents, volume, harmonics))
        return self

    def noise(
        self, noise_type: str = "white", volume: float = 0.5, seed: int | None = None
    ) -> "SoundDesigner":
        """Add a noise layer.

        Args:
            noise_type: white, pink, or brown.
            volume:     Layer volume.
            seed:       Random seed for reproducibility.
        """
        if noise_type not in _NOISE_FUNCS:
            raise ValueError(f"Unknown noise {noise_type!r}. Choose: {sorted(_NOISE_FUNCS)}")
        self._noises.append(_NoiseLayer(noise_type, volume, seed))
        return self

    # -- FM synthesis ------------------------------------------------------

    def fm(
        self,
        carrier_wave: str = "sine",
        mod_ratio: float = 2.0,
        mod_index: float = 5.0,
        volume: float = 1.0,
    ) -> "SoundDesigner":
        """Add an FM synthesis layer.

        Frequency modulation: a modulator oscillator modulates the frequency
        of a carrier oscillator. Creates complex, evolving timbres — bells,
        electric pianos, metallic sounds, bass.

        Args:
            carrier_wave: Carrier waveform (sine, sawtooth, square, triangle).
            mod_ratio:    Modulator freq / carrier freq. Integer ratios = harmonic,
                          non-integer = inharmonic/metallic.
            mod_index:    Modulation depth. Higher = more harmonics.
                          0 = pure carrier. 1-3 = subtle. 5+ = aggressive.
            volume:       Layer volume (0.0-1.0).

        Example::

            # DX7-style electric piano (2:1 ratio, moderate index)
            epiano = SoundDesigner("epiano").fm("sine", mod_ratio=2.0, mod_index=3.5)

            # Bell (inharmonic ratio for metallic partials)
            bell = SoundDesigner("bell").fm("sine", mod_ratio=1.414, mod_index=8.0)
        """
        if carrier_wave not in _OSC_FUNCS:
            raise ValueError(f"Unknown wave {carrier_wave!r}. Choose: {sorted(_OSC_FUNCS)}")
        self._fm_layers.append(_FMLayer(carrier_wave, mod_ratio, mod_index, volume))
        return self

    # -- Wavetable synthesis -----------------------------------------------

    def add_wavetable(
        self,
        wavetable: "Wavetable | list[float]",
        volume: float = 1.0,
        detune_cents: float = 0.0,
    ) -> "SoundDesigner":
        """Add a wavetable oscillator layer.

        Reads a single-cycle waveform from a Wavetable object and uses it
        as the oscillator source. Design arbitrary waveforms, build them
        from harmonics, or morph between shapes.

        Args:
            wavetable:    Wavetable object or raw list of float samples.
            volume:       Layer volume (0.0-1.0).
            detune_cents: Detune from base frequency in cents.

        Example::

            wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25, 0.1])
            sd = SoundDesigner("custom_organ").add_wavetable(wt)
        """
        if isinstance(wavetable, list):
            table = np.array(wavetable, dtype=np.float64)
        elif isinstance(wavetable, Wavetable):
            table = wavetable.table.copy()
        else:
            table = np.asarray(wavetable, dtype=np.float64)
        self._wavetable_layers.append(_WavetableLayer(table, volume, detune_cents))
        return self

    # -- Envelope ----------------------------------------------------------

    def envelope(
        self,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.8,
        release: float = 0.3,
    ) -> "SoundDesigner":
        """Set the ADSR amplitude envelope (in seconds)."""
        self._env = (attack, decay, sustain, release)
        return self

    def pitch_envelope(
        self,
        start_multiplier: float = 2.0,
        end_multiplier: float = 1.0,
        duration: float = 0.05,
    ) -> "SoundDesigner":
        """Add a pitch envelope (e.g. for kick drums with pitch drop).

        Multiplies the base frequency by start_multiplier, sweeps to
        end_multiplier over *duration* seconds, then holds.
        """
        self._pitch_env = (start_multiplier, end_multiplier, duration)
        return self

    # -- Filter ------------------------------------------------------------

    def filter(
        self,
        filter_type: str = "lowpass",
        cutoff: float = 2000.0,
        resonance: float = 0.707,
    ) -> "SoundDesigner":
        """Add a filter (applied after oscillator mixing).

        Args:
            filter_type: lowpass, highpass, or bandpass.
            cutoff:      Cutoff frequency in Hz.
            resonance:   Q factor (0.5–10, higher = sharper peak).
        """
        self._filter = _FilterSpec(filter_type, cutoff, resonance)
        return self

    # -- LFO ---------------------------------------------------------------

    def lfo(
        self,
        target: str = "filter_cutoff",
        rate: float = 2.0,
        depth: float = 0.5,
        wave: str = "sine",
    ) -> "SoundDesigner":
        """Add an LFO modulation source.

        Args:
            target: What to modulate: filter_cutoff, pitch, or volume.
            rate:   LFO frequency in Hz.
            depth:  Modulation depth (0.0–1.0).
            wave:   LFO waveform (sine, triangle).
        """
        if target not in ("filter_cutoff", "pitch", "volume"):
            raise ValueError(f"Unknown LFO target {target!r}")
        self._lfos.append(_LFOSpec(target, rate, depth, wave))
        return self

    # -- Render ------------------------------------------------------------

    def render(self, freq: float, duration: float, sr: int = 44100) -> FloatArray:
        """Render the designed sound at a specific frequency and duration.

        Args:
            freq:     Fundamental frequency in Hz.
            duration: Duration in seconds.
            sr:       Sample rate.

        Returns:
            Mono float64 numpy array.
        """
        n = int(duration * sr)
        if n == 0:
            return np.zeros(0)

        t = np.arange(n) / sr

        # -- Pitch envelope (modifies freq over time) ----------------------
        if self._pitch_env:
            s_mult, e_mult, p_dur = self._pitch_env
            p_samples = min(int(p_dur * sr), n)
            freq_env = np.ones(n) * freq * e_mult
            if p_samples > 0:
                freq_env[:p_samples] = freq * np.linspace(s_mult, e_mult, p_samples)
        else:
            freq_env = None

        # -- LFO: pitch modulation -----------------------------------------
        pitch_mod = np.ones(n)
        for lfo_spec in self._lfos:
            if lfo_spec.target == "pitch":
                lfo_signal = np.sin(2 * np.pi * lfo_spec.rate * t)
                pitch_mod *= 1.0 + lfo_spec.depth * lfo_signal * 0.1  # ±10% per depth

        # -- Mix oscillator layers -----------------------------------------
        mix = np.zeros(n)
        has_sources = self._oscs or self._noises or self._fm_layers or self._wavetable_layers
        if not has_sources:
            # Default: single sine
            self._oscs.append(_OscLayer("sine", 0.0, 1.0, 1))

        for osc in self._oscs:
            detune_ratio = 2.0 ** (osc.detune_cents / 1200.0)
            if freq_env is not None:
                # Per-sample frequency with pitch envelope
                osc_freq_env = freq_env * detune_ratio * pitch_mod
                phase = np.cumsum(osc_freq_env / sr) * 2 * np.pi
                if osc.wave == "sine":
                    layer = np.sin(phase)
                elif osc.wave == "sawtooth":
                    # Phase-based sawtooth
                    layer = 2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
                elif osc.wave == "square":
                    layer = np.sign(np.sin(phase))
                elif osc.wave == "triangle":
                    layer = (
                        2.0
                        * np.abs(2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5)))
                        - 1.0
                    )
                else:
                    layer = np.sin(phase)
            else:
                osc_freq = freq * detune_ratio
                osc_func = _OSC_FUNCS[osc.wave]
                if osc.wave == "sine":
                    osc_freq_mod = osc_freq * pitch_mod
                    phase = np.cumsum(osc_freq_mod / sr) * 2 * np.pi
                    layer = np.sin(phase)
                else:
                    # For complex waveforms with pitch mod, use phase accumulator
                    osc_freq_mod = osc_freq * pitch_mod
                    phase = np.cumsum(osc_freq_mod / sr) * 2 * np.pi
                    if osc.wave == "sawtooth":
                        layer = 2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
                    elif osc.wave == "square":
                        layer = np.sign(np.sin(phase))
                    elif osc.wave == "triangle":
                        layer = (
                            2.0
                            * np.abs(
                                2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
                            )
                            - 1.0
                        )
                    else:
                        layer = osc_func(osc_freq, n, sr)

            mix += layer * osc.volume

        for nl in self._noises:
            noise_func = _NOISE_FUNCS[nl.noise_type]
            mix += noise_func(n, nl.seed) * nl.volume

        # -- FM synthesis layers -------------------------------------------
        for fm_layer in self._fm_layers:
            carrier_freq = freq * pitch_mod if freq_env is None else freq_env * pitch_mod
            mod_freq = carrier_freq * fm_layer.mod_ratio
            # Modulator signal
            mod_phase = np.cumsum(mod_freq / sr) * 2 * np.pi
            modulator = np.sin(mod_phase) * fm_layer.mod_index * carrier_freq
            # Carrier with frequency modulation
            carrier_inst_freq = carrier_freq + modulator
            carrier_phase = np.cumsum(carrier_inst_freq / sr) * 2 * np.pi
            if fm_layer.carrier_wave == "sine":
                layer = np.sin(carrier_phase)
            elif fm_layer.carrier_wave == "sawtooth":
                layer = 2.0 * (
                    carrier_phase / (2 * np.pi) - np.floor(carrier_phase / (2 * np.pi) + 0.5)
                )
            elif fm_layer.carrier_wave == "square":
                layer = np.sign(np.sin(carrier_phase))
            elif fm_layer.carrier_wave == "triangle":
                layer = (
                    2.0
                    * np.abs(
                        2.0
                        * (
                            carrier_phase / (2 * np.pi)
                            - np.floor(carrier_phase / (2 * np.pi) + 0.5)
                        )
                    )
                    - 1.0
                )
            else:
                layer = np.sin(carrier_phase)
            mix += layer * fm_layer.volume

        # -- Wavetable layers ----------------------------------------------
        for wt_layer in self._wavetable_layers:
            detune_ratio = 2.0 ** (wt_layer.detune_cents / 1200.0)
            wt_freq = (
                freq * detune_ratio * pitch_mod
                if freq_env is None
                else freq_env * detune_ratio * pitch_mod
            )
            phase = np.cumsum(wt_freq / sr)  # phase in cycles (0..N)
            table_len = len(wt_layer.table)
            # Map phase to table indices with linear interpolation
            table_pos = (phase % 1.0) * table_len
            idx0 = table_pos.astype(np.intp) % table_len
            idx1 = (idx0 + 1) % table_len
            frac = table_pos - np.floor(table_pos)
            layer = wt_layer.table[idx0] * (1.0 - frac) + wt_layer.table[idx1] * frac
            mix += layer * wt_layer.volume

        # Normalize if clipping
        peak = np.max(np.abs(mix))
        if peak > 1.0:
            mix /= peak

        # -- Filter --------------------------------------------------------
        if self._filter:
            # LFO on filter cutoff
            cutoff = self._filter.cutoff
            cutoff_mod = np.ones(n) * cutoff
            for lfo_spec in self._lfos:
                if lfo_spec.target == "filter_cutoff":
                    lfo_signal = np.sin(2 * np.pi * lfo_spec.rate * t)
                    cutoff_mod *= 1.0 + lfo_spec.depth * lfo_signal

            # If cutoff is modulated, apply filter in blocks
            if any(lfo.target == "filter_cutoff" for lfo in self._lfos):
                block = 256
                filtered = np.zeros(n)
                for start in range(0, n, block):
                    end = min(start + block, n)
                    avg_cutoff = float(np.clip(np.mean(cutoff_mod[start:end]), 20, sr / 2 - 1))
                    b, a = _biquad_coeffs(
                        self._filter.filter_type, avg_cutoff, sr, self._filter.resonance
                    )
                    filtered[start:end] = _apply_biquad(mix[start:end], b, a)
                mix = filtered
            else:
                b, a = _biquad_coeffs(self._filter.filter_type, cutoff, sr, self._filter.resonance)
                mix = _apply_biquad(mix, b, a)

        # -- ADSR envelope -------------------------------------------------
        env = _adsr(n, sr, *self._env)
        mix *= env

        # -- LFO: volume (tremolo) -----------------------------------------
        for lfo_spec in self._lfos:
            if lfo_spec.target == "volume":
                lfo_signal = np.sin(2 * np.pi * lfo_spec.rate * t)
                mix *= 1.0 + lfo_spec.depth * lfo_signal * 0.5

        return np.clip(mix, -1.0, 1.0)

    # -- Convenience -------------------------------------------------------

    def preview(self, freq: float = 440.0, duration: float = 2.0, sr: int = 22050) -> None:
        """Render at the given frequency and play immediately."""
        from .engine import Note, Song, Track
        from .playback import play as _play_fn

        song = Song(title=f"Preview: {self.name}", bpm=120, sample_rate=sr)
        song.register_instrument(self.name, self)
        tr = song.add_track(Track(instrument=self.name))
        tr.add(Note("A", 4, duration))
        _play_fn(song)

    def to_wav(self, path: str, freq: float = 440.0, duration: float = 2.0, sr: int = 44100) -> str:
        """Render and save as a WAV file."""
        import wave
        from pathlib import Path

        audio = self.render(freq, duration, sr)
        pcm = (audio * 32767).astype(np.int16)
        out = Path(path)
        with wave.open(str(out), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())
        return str(out)

    # -- Serialization -----------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the sound design to a JSON-compatible dict."""
        return {
            "name": self.name,
            "oscillators": [
                {
                    "wave": o.wave,
                    "detune_cents": o.detune_cents,
                    "volume": o.volume,
                    "harmonics": o.harmonics,
                }
                for o in self._oscs
            ],
            "noises": [
                {"type": n.noise_type, "volume": n.volume, "seed": n.seed} for n in self._noises
            ],
            "fm_layers": [
                {
                    "carrier_wave": fm.carrier_wave,
                    "mod_ratio": fm.mod_ratio,
                    "mod_index": fm.mod_index,
                    "volume": fm.volume,
                }
                for fm in self._fm_layers
            ],
            "wavetable_layers": [
                {
                    "table": wt.table.tolist(),
                    "volume": wt.volume,
                    "detune_cents": wt.detune_cents,
                }
                for wt in self._wavetable_layers
            ],
            "envelope": {
                "attack": self._env[0],
                "decay": self._env[1],
                "sustain": self._env[2],
                "release": self._env[3],
            },
            "filter": {
                "type": self._filter.filter_type,
                "cutoff": self._filter.cutoff,
                "resonance": self._filter.resonance,
            }
            if self._filter
            else None,
            "lfos": [
                {"target": lfo.target, "rate": lfo.rate, "depth": lfo.depth, "wave": lfo.wave}
                for lfo in self._lfos
            ],
            "pitch_envelope": {
                "start": self._pitch_env[0],
                "end": self._pitch_env[1],
                "duration": self._pitch_env[2],
            }
            if self._pitch_env
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SoundDesigner":
        """Reconstruct a SoundDesigner from a serialized dict."""
        sd = cls(data.get("name", "custom"))
        for o in data.get("oscillators", []):
            sd.add_osc(
                o["wave"], o.get("detune_cents", 0), o.get("volume", 1.0), o.get("harmonics", 16)
            )
        for n in data.get("noises", []):
            sd.noise(n["type"], n.get("volume", 0.5), n.get("seed"))
        for fm_data in data.get("fm_layers", []):
            sd.fm(
                fm_data.get("carrier_wave", "sine"),
                fm_data.get("mod_ratio", 2.0),
                fm_data.get("mod_index", 5.0),
                fm_data.get("volume", 1.0),
            )
        for wt_data in data.get("wavetable_layers", []):
            sd.add_wavetable(
                wt_data["table"],
                wt_data.get("volume", 1.0),
                wt_data.get("detune_cents", 0.0),
            )
        env = data.get("envelope", {})
        if env:
            sd.envelope(
                env.get("attack", 0.01),
                env.get("decay", 0.1),
                env.get("sustain", 0.8),
                env.get("release", 0.3),
            )
        f = data.get("filter")
        if f:
            sd.filter(f["type"], f.get("cutoff", 2000), f.get("resonance", 0.707))
        for lfo_data in data.get("lfos", []):
            sd.lfo(
                lfo_data["target"],
                lfo_data.get("rate", 2.0),
                lfo_data.get("depth", 0.5),
                lfo_data.get("wave", "sine"),
            )
        pe = data.get("pitch_envelope")
        if pe:
            sd.pitch_envelope(pe["start"], pe["end"], pe.get("duration", 0.05))
        return sd

    def __repr__(self) -> str:
        parts = [f"SoundDesigner({self.name!r}"]
        parts.append(f"oscs={len(self._oscs)}")
        parts.append(f"noises={len(self._noises)}")
        if self._fm_layers:
            parts.append(f"fm={len(self._fm_layers)}")
        if self._wavetable_layers:
            parts.append(f"wavetables={len(self._wavetable_layers)}")
        if self._filter:
            parts.append(f"filter={self._filter.filter_type}")
        parts.append(f"lfos={len(self._lfos)}")
        return ", ".join(parts) + ")"


# ---------------------------------------------------------------------------
# Preset Library — sounds built with SoundDesigner
# ---------------------------------------------------------------------------

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", detune_cents=0, volume=0.25)
    .add_osc("sawtooth", detune_cents=7, volume=0.2)
    .add_osc("sawtooth", detune_cents=-7, volume=0.2)
    .add_osc("sawtooth", detune_cents=15, volume=0.15)
    .add_osc("sawtooth", detune_cents=-15, volume=0.15)
    .add_osc("sawtooth", detune_cents=25, volume=0.1)
    .add_osc("sawtooth", detune_cents=-25, volume=0.1)
    .envelope(attack=0.03, decay=0.1, sustain=0.7, release=0.5)
    .filter("lowpass", cutoff=5000, resonance=0.5)
)

sub_808 = (
    SoundDesigner("sub_808")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.6, sustain=0.0, release=0.4)
    .pitch_envelope(start_multiplier=4.0, end_multiplier=1.0, duration=0.04)
    .filter("lowpass", cutoff=200, resonance=0.8)
)

metallic_hit = (
    SoundDesigner("metallic_hit")
    .add_osc("square", detune_cents=0, volume=0.4, harmonics=6)
    .add_osc("square", detune_cents=710, volume=0.3, harmonics=4)  # inharmonic
    .add_osc("square", detune_cents=1500, volume=0.2, harmonics=3)
    .noise("white", volume=0.3)
    .envelope(attack=0.001, decay=0.15, sustain=0.0, release=0.1)
    .filter("bandpass", cutoff=3000, resonance=2.0)
)

vocal_pad = (
    SoundDesigner("vocal_pad")
    .add_osc("sawtooth", detune_cents=0, volume=0.3)
    .add_osc("sawtooth", detune_cents=3, volume=0.25)
    .add_osc("sawtooth", detune_cents=-3, volume=0.25)
    .envelope(attack=0.3, decay=0.2, sustain=0.6, release=0.8)
    .filter("bandpass", cutoff=800, resonance=3.0)
    .lfo("filter_cutoff", rate=0.3, depth=0.4)
)

plucked_string = (
    SoundDesigner("plucked_string")
    .noise("white", volume=0.8, seed=42)
    .add_osc("triangle", volume=0.3)
    .envelope(attack=0.001, decay=0.3, sustain=0.1, release=0.4)
    .filter("lowpass", cutoff=3000, resonance=0.5)
)

# ---------------------------------------------------------------------------
# FM Synthesis Presets
# ---------------------------------------------------------------------------

fm_electric_piano = (
    SoundDesigner("fm_electric_piano")
    .fm("sine", mod_ratio=2.0, mod_index=3.5, volume=0.8)
    .fm("sine", mod_ratio=1.0, mod_index=0.5, volume=0.2)
    .envelope(attack=0.005, decay=0.4, sustain=0.2, release=0.5)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

fm_bell = (
    SoundDesigner("fm_bell")
    .fm("sine", mod_ratio=1.414, mod_index=8.0, volume=0.7)
    .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.3)
    .envelope(attack=0.001, decay=1.0, sustain=0.0, release=0.8)
)

fm_brass = (
    SoundDesigner("fm_brass")
    .fm("sine", mod_ratio=1.0, mod_index=5.0, volume=0.6)
    .fm("sine", mod_ratio=3.0, mod_index=3.0, volume=0.3)
    .add_osc("sawtooth", volume=0.15)
    .envelope(attack=0.05, decay=0.15, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=3000, resonance=0.8)
)

fm_bass = (
    SoundDesigner("fm_bass")
    .fm("sine", mod_ratio=1.0, mod_index=4.0, volume=0.9)
    .envelope(attack=0.005, decay=0.3, sustain=0.4, release=0.2)
    .filter("lowpass", cutoff=500, resonance=1.0)
)

# ---------------------------------------------------------------------------
# Wavetable Presets
# ---------------------------------------------------------------------------

_wt_organ_table = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25, 0.0, 0.125, 0.0, 0.06])
wt_organ = (
    SoundDesigner("wt_organ")
    .add_wavetable(_wt_organ_table, volume=0.5)
    .add_wavetable(_wt_organ_table, volume=0.4, detune_cents=5)
    .add_wavetable(_wt_organ_table, volume=0.4, detune_cents=-5)
    .envelope(attack=0.02, decay=0.05, sustain=0.8, release=0.3)
)

_wt_bright = Wavetable.from_harmonics([1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08])
wt_bright_lead = (
    SoundDesigner("wt_bright_lead")
    .add_wavetable(_wt_bright, volume=0.6)
    .add_wavetable(_wt_bright, volume=0.3, detune_cents=8)
    .add_wavetable(_wt_bright, volume=0.3, detune_cents=-8)
    .envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.7)
    .lfo("filter_cutoff", rate=2.0, depth=0.3)
)

_wt_morph = Wavetable.from_wave("sawtooth").morph(Wavetable.from_wave("square"), 0.5)
wt_morph_pad = (
    SoundDesigner("wt_morph_pad")
    .add_wavetable(_wt_morph, volume=0.4)
    .add_wavetable(_wt_morph, volume=0.3, detune_cents=3)
    .add_wavetable(_wt_morph, volume=0.3, detune_cents=-3)
    .envelope(attack=0.4, decay=0.2, sustain=0.5, release=0.8)
    .filter("lowpass", cutoff=2000, resonance=0.5)
    .lfo("filter_cutoff", rate=0.2, depth=0.4)
)

PRESETS = {
    "supersaw": supersaw,
    "sub_808": sub_808,
    "metallic_hit": metallic_hit,
    "vocal_pad": vocal_pad,
    "plucked_string": plucked_string,
    "fm_electric_piano": fm_electric_piano,
    "fm_bell": fm_bell,
    "fm_brass": fm_brass,
    "fm_bass": fm_bass,
    "wt_organ": wt_organ,
    "wt_bright_lead": wt_bright_lead,
    "wt_morph_pad": wt_morph_pad,
}
