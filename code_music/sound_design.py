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

from typing import Callable

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


class _WavetableScanSpec:
    __slots__ = ("tables", "scan_rate", "volume", "detune_cents")

    def __init__(
        self,
        tables: list[FloatArray],
        scan_rate: float,
        volume: float,
        detune_cents: float,
    ):
        self.tables = tables
        self.scan_rate = scan_rate
        self.volume = volume
        self.detune_cents = detune_cents


class _LFOSpec:
    __slots__ = ("target", "rate", "depth", "wave")

    def __init__(self, target: str, rate: float, depth: float, wave: str):
        self.target = target
        self.rate = rate
        self.depth = depth
        self.wave = wave


class _GranularSpec:
    __slots__ = ("grain_size", "density", "scatter", "volume", "seed")

    def __init__(
        self, grain_size: float, density: float, scatter: float, volume: float, seed: int | None
    ):
        self.grain_size = grain_size
        self.density = density
        self.scatter = scatter
        self.volume = volume
        self.seed = seed


class _PhysicalModelSpec:
    __slots__ = ("model_type", "params", "volume")

    def __init__(self, model_type: str, params: dict, volume: float):
        self.model_type = model_type
        self.params = params
        self.volume = volume


# ---------------------------------------------------------------------------
# Physical modeling algorithms
# ---------------------------------------------------------------------------


def _karplus_strong(
    freq: float, n: int, sr: int, decay: float = 0.996, brightness: float = 0.5
) -> FloatArray:
    """Karplus-Strong plucked string synthesis."""
    period = max(2, int(sr / freq))
    rng = np.random.default_rng(42)
    buf = rng.uniform(-1, 1, period).astype(np.float64)
    out = np.zeros(n)
    for i in range(n):
        idx = i % period
        out[i] = buf[idx]
        # Average filter with brightness control
        next_idx = (idx + 1) % period
        buf[idx] = decay * (brightness * buf[idx] + (1 - brightness) * buf[next_idx])
    return out


def _waveguide_pipe(
    freq: float, n: int, sr: int, feedback: float = 0.98, brightness: float = 0.6
) -> FloatArray:
    """Simple waveguide pipe/flute model — bidirectional delay line."""
    half_period = max(1, int(sr / freq / 2))
    rng = np.random.default_rng(99)
    # Excite with a short noise burst
    excite_len = min(int(sr * 0.005), n)
    excite = rng.standard_normal(excite_len) * 0.5
    # Two delay lines (forward and backward)
    delay_a = np.zeros(half_period)
    delay_b = np.zeros(half_period)
    out = np.zeros(n)
    for i in range(n):
        idx = i % half_period
        # Inject excitation at the start
        inp = excite[i] if i < excite_len else 0.0
        # Read from delay lines
        out_a = delay_a[idx]
        out_b = delay_b[idx]
        # Low-pass and reflect
        out[i] = out_a + out_b
        delay_a[idx] = (inp + feedback * (-out_b)) * brightness + (feedback * (-out_b)) * (
            1 - brightness
        )
        delay_b[idx] = feedback * (-out_a)
    # Normalize
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


def _modal_synth(
    freq: float, n: int, sr: int, modes: list[tuple[float, float, float]] | None = None
) -> FloatArray:
    """Modal synthesis — struck resonant body with configurable modes.

    Each mode is (freq_ratio, amplitude, decay_rate). Default modes approximate
    a struck metal bar.
    """
    if modes is None:
        modes = [(1.0, 1.0, 4.0), (2.76, 0.5, 6.0), (5.4, 0.3, 8.0), (8.93, 0.15, 12.0)]
    t = np.arange(n) / sr
    out = np.zeros(n)
    for ratio, amp, decay_rate in modes:
        mode_freq = freq * ratio
        if mode_freq >= sr / 2:
            continue
        out += amp * np.sin(2 * np.pi * mode_freq * t) * np.exp(-decay_rate * t)
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


def _bowed_string(
    freq: float, n: int, sr: int, bow_pressure: float = 0.5, brightness: float = 0.6
) -> FloatArray:
    """Bowed string model using a waveguide with continuous excitation.

    Unlike plucked strings (Karplus-Strong) which excite once and decay,
    a bowed string has sustained excitation from the bow friction. The bow
    pressure controls how hard the string is driven - low pressure gives
    a gentle sul tasto, high pressure gives a forceful marcato.

    Args:
        freq:         Fundamental frequency.
        n:            Number of samples.
        sr:           Sample rate.
        bow_pressure: Bow force 0.0-1.0. Low = gentle, high = aggressive.
        brightness:   Tone brightness 0.0-1.0. Low = muffled, high = bright.
    """
    period = max(2, int(sr / freq))
    buf = np.zeros(period, dtype=np.float64)
    out = np.zeros(n, dtype=np.float64)

    # Bow velocity oscillates slowly (simulates bow movement)
    bow_speed = 0.2  # bow speed in arbitrary units
    rng = np.random.default_rng(77)

    for i in range(n):
        idx = i % period
        string_vel = buf[idx]

        # Bow friction model: stick-slip behavior
        # When bow and string velocities are close, friction sticks (drives string)
        # When they diverge, it slips (releases)
        bow_vel = bow_speed * np.sin(2 * np.pi * 5.0 * i / sr)  # slow bow oscillation
        delta_v = bow_vel - string_vel
        # Friction curve: hyperbolic tangent approximation of stick-slip
        friction = bow_pressure * np.tanh(4.0 * delta_v)
        # Add small noise for rosin texture
        friction += rng.standard_normal() * 0.002 * bow_pressure

        # Inject friction force into delay line
        next_idx = (idx + 1) % period
        new_val = brightness * buf[idx] + (1 - brightness) * buf[next_idx]
        buf[idx] = 0.995 * new_val + friction * 0.15

        out[i] = buf[idx]

    # Normalize
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


_PHYSICAL_MODELS = {"karplus_strong", "waveguide_pipe", "modal", "bowed_string"}


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
        self._wavetable_scans: list[_WavetableScanSpec] = []
        self._formant_layers: list[dict] = []
        self._granular_layers: list[_GranularSpec] = []
        self._physical_layers: list[_PhysicalModelSpec] = []
        self._spectral_procs: list = []  # list of callables (audio, sr) -> audio
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

    def wavetable_scan(
        self,
        tables: list["Wavetable"],
        scan_rate: float = 0.5,
        volume: float = 1.0,
        detune_cents: float = 0.0,
    ) -> "SoundDesigner":
        """Add a scanning wavetable oscillator that morphs between tables.

        An LFO sweeps through a bank of wavetables over time. At any moment
        the output is an interpolation between two adjacent tables. This
        produces evolving, animated timbres - the hallmark of wavetable
        synthesis in modern synths like Serum and Vital.

        Args:
            tables:       List of Wavetable objects (the bank). Minimum 2.
            scan_rate:    LFO rate in Hz for scanning (0.1=slow, 2.0=fast).
            volume:       Layer volume (0.0-1.0).
            detune_cents: Detune from base frequency in cents.

        Returns:
            self (for chaining).

        Example::

            wt_bank = [
                Wavetable.from_wave("sine"),
                Wavetable.from_wave("sawtooth"),
                Wavetable.from_wave("square"),
            ]
            sd = SoundDesigner("scanner").wavetable_scan(wt_bank, scan_rate=0.3)
        """
        if len(tables) < 2:
            raise ValueError("wavetable_scan requires at least 2 tables")
        raw_tables = []
        for wt in tables:
            if isinstance(wt, Wavetable):
                raw_tables.append(wt.table.copy())
            else:
                raw_tables.append(np.asarray(wt, dtype=np.float64))
        self._wavetable_scans.append(
            _WavetableScanSpec(raw_tables, scan_rate, volume, detune_cents)
        )
        return self

    # -- Formant / Vocal synthesis -----------------------------------------

    def formant(
        self,
        vowel: str = "ah",
        breathiness: float = 0.3,
        vibrato_rate: float = 5.5,
        vibrato_depth: float = 0.02,
        volume: float = 1.0,
    ) -> "SoundDesigner":
        """Add a formant vocal synthesis layer.

        Simulates vowel sounds by passing a glottal pulse through resonant
        filters tuned to human vocal formant frequencies. Not speech - but
        musically useful vocal textures like choir pads, ethereal voices,
        and vocal drones.

        Vowels: 'ah' (open, like "father"), 'ee' (closed, like "see"),
        'oh' (round, like "go"), 'oo' (closed round, like "who"),
        'eh' (mid, like "bed"), 'ih' (near-close, like "sit").

        Args:
            vowel:         Vowel shape: ah, ee, oh, oo, eh, ih.
            breathiness:   Mix of noise in the source (0=pure, 1=whisper).
            vibrato_rate:  Vibrato speed in Hz (natural singing ~5-6 Hz).
            vibrato_depth: Vibrato pitch deviation (fraction, 0.02 = subtle).
            volume:        Layer volume.

        Returns:
            self (for chaining).

        Example::

            choir = SoundDesigner("choir").formant("ah", breathiness=0.2)
            voice = SoundDesigner("voice").formant("oo", vibrato_depth=0.03)
        """
        self._formant_layers.append(
            {
                "vowel": vowel,
                "breathiness": breathiness,
                "vibrato_rate": vibrato_rate,
                "vibrato_depth": vibrato_depth,
                "volume": volume,
            }
        )
        return self

    # -- Granular synthesis ------------------------------------------------

    def granular(
        self,
        grain_size: float = 0.05,
        density: float = 10.0,
        scatter: float = 0.3,
        volume: float = 1.0,
        seed: int | None = None,
    ) -> "SoundDesigner":
        """Add a granular synthesis layer.

        Splits a source (noise or the current osc mix) into tiny grains and
        scatters them in time. Creates cloud-like textures, time-stretch effects,
        and atmospheric soundscapes.

        Args:
            grain_size: Size of each grain in seconds (0.01–0.2).
            density:    Average grains per second.
            scatter:    Timing randomness (0 = even, 1 = fully random).
            volume:     Layer volume.
            seed:       Random seed for reproducible grain patterns.

        Example::

            cloud = SoundDesigner("cloud").granular(grain_size=0.08, density=15, scatter=0.5)
        """
        self._granular_layers.append(_GranularSpec(grain_size, density, scatter, volume, seed))
        return self

    # -- Physical modeling -------------------------------------------------

    def physical_model(
        self,
        model_type: str = "karplus_strong",
        volume: float = 1.0,
        **kwargs: float,
    ) -> "SoundDesigner":
        """Add a physical modeling synthesis layer.

        Simulates real-world instruments using waveguides and resonant models.

        Args:
            model_type: Model to use:
                - ``karplus_strong``: plucked string (guitar, harp, koto).
                  Params: decay (0.99–0.999), brightness (0–1).
                - ``waveguide_pipe``: blown pipe/flute.
                  Params: feedback (0.9–0.99), brightness (0–1).
                - ``modal``: struck resonant body (bell, bar, gong).
                  Params: (uses default metal bar modes).
                - ``bowed_string``: sustained bowed string (violin, cello).
                  Params: bow_pressure (0-1), brightness (0-1).
            volume:     Layer volume.
            **kwargs:   Model-specific parameters.

        Example::

            guitar = SoundDesigner("guitar").physical_model("karplus_strong", decay=0.998)
            flute = SoundDesigner("flute").physical_model("waveguide_pipe", feedback=0.97)
            gong = SoundDesigner("gong").physical_model("modal")
            violin = SoundDesigner("violin").physical_model("bowed_string", bow_pressure=0.6)
        """
        if model_type not in _PHYSICAL_MODELS:
            raise ValueError(f"Unknown model {model_type!r}. Choose: {sorted(_PHYSICAL_MODELS)}")
        self._physical_layers.append(_PhysicalModelSpec(model_type, dict(kwargs), volume))
        return self

    # -- Spectral processing -----------------------------------------------

    def spectral(self, process_fn: "Callable") -> "SoundDesigner":
        """Add a spectral processing step (FFT → manipulate → IFFT).

        The process_fn receives (audio_array, sample_rate) and must return
        a float64 array of the same length.

        Use the built-in spectral functions or write your own:
        - ``spectral_freeze(amount)`` — freeze spectral content (sustain)
        - ``spectral_shift(semitones)`` — shift spectrum up/down
        - ``spectral_smear(amount)`` — blur spectral content across bins

        Example::

            from code_music.sound_design import spectral_freeze
            sd = SoundDesigner("frozen").add_osc("sawtooth").spectral(spectral_freeze(0.8))
        """
        self._spectral_procs.append(process_fn)
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
        has_sources = (
            self._oscs
            or self._noises
            or self._fm_layers
            or self._wavetable_layers
            or self._granular_layers
            or self._physical_layers
        )
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

        # -- Wavetable scanning layers ------------------------------------
        for scan in self._wavetable_scans:
            detune_ratio = 2.0 ** (scan.detune_cents / 1200.0)
            wt_freq = (
                freq * detune_ratio * pitch_mod
                if freq_env is None
                else freq_env * detune_ratio * pitch_mod
            )
            phase = np.cumsum(wt_freq / sr)

            # LFO position determines which tables to interpolate
            num_tables = len(scan.tables)
            t_arr = np.arange(n) / sr
            # Triangle LFO: scans 0 -> num_tables-1 -> 0 -> ...
            lfo_phase = scan.scan_rate * t_arr
            # Triangle wave mapped to [0, num_tables-1]
            lfo_raw = 2.0 * np.abs(lfo_phase - np.floor(lfo_phase + 0.5))
            scan_pos = lfo_raw * (num_tables - 1)

            # For each sample, interpolate between adjacent tables
            table_idx_a = np.clip(np.floor(scan_pos).astype(np.intp), 0, num_tables - 2)
            table_idx_b = table_idx_a + 1
            table_frac = scan_pos - table_idx_a

            # Read from both tables at the oscillator phase
            layer = np.zeros(n, dtype=np.float64)
            for ti in range(num_tables):
                mask = (table_idx_a == ti) | (table_idx_b == ti)
                if not np.any(mask):
                    continue
                table = scan.tables[ti]
                table_len = len(table)
                pos_in_table = (phase[mask] % 1.0) * table_len
                i0 = pos_in_table.astype(np.intp) % table_len
                i1 = (i0 + 1) % table_len
                f = pos_in_table - np.floor(pos_in_table)
                table_val = table[i0] * (1.0 - f) + table[i1] * f

                # Weight: if this is table_a, weight is (1 - frac); if table_b, weight is frac
                is_a = table_idx_a[mask] == ti
                is_b = table_idx_b[mask] == ti
                weight = np.where(is_a, 1.0 - table_frac[mask], 0.0)
                weight = np.where(is_b, weight + table_frac[mask], weight)
                layer[mask] += table_val * weight

            mix += layer * scan.volume

        # -- Formant vocal synthesis layers --------------------------------
        # Formant frequencies for vowels (F1, F2, F3 in Hz + bandwidths)
        _FORMANTS = {
            "ah": [(730, 90), (1090, 110), (2440, 170)],
            "ee": [(270, 60), (2290, 100), (3010, 120)],
            "oh": [(570, 80), (840, 90), (2410, 150)],
            "oo": [(300, 50), (870, 80), (2240, 130)],
            "eh": [(530, 80), (1840, 100), (2480, 140)],
            "ih": [(390, 60), (1990, 100), (2550, 130)],
        }
        for fl in self._formant_layers:
            formants = _FORMANTS.get(fl["vowel"], _FORMANTS["ah"])
            breath = fl["breathiness"]
            vib_rate = fl["vibrato_rate"]
            vib_depth = fl["vibrato_depth"]

            # Glottal source: pulse train + noise for breathiness
            t_arr = np.arange(n) / sr
            vibrato = 1.0 + vib_depth * np.sin(2 * np.pi * vib_rate * t_arr)

            if freq_env is not None:
                source_freq = freq_env * pitch_mod * vibrato
            else:
                source_freq = freq * pitch_mod * vibrato

            # Glottal pulse: narrow sawtooth (models vocal fold vibration)
            phase = np.cumsum(source_freq / sr)
            glottal = 2.0 * (phase % 1.0) - 1.0
            # Shape the pulse (make it more impulse-like)
            glottal = np.tanh(glottal * 3.0)

            # Breathy noise component
            rng_vocal = np.random.default_rng(42)
            noise = rng_vocal.standard_normal(n) * breath
            source = glottal * (1.0 - breath * 0.5) + noise

            # Apply formant resonances (2nd-order IIR bandpass per formant)
            vocal = np.zeros(n, dtype=np.float64)
            for center_hz, bw_hz in formants:
                # Biquad bandpass coefficients
                w0 = 2.0 * np.pi * center_hz / sr
                alpha = (
                    np.sin(w0) * np.sinh(np.log(2) / 2 * (bw_hz / center_hz) * w0 / np.sin(w0))
                    if np.sin(w0) > 0.001
                    else 0.1
                )
                b0 = alpha
                b1 = 0.0
                b2 = -alpha
                a0 = 1.0 + alpha
                a1 = -2.0 * np.cos(w0)
                a2 = 1.0 - alpha
                # Normalize
                b0 /= a0
                b1 /= a0
                b2 /= a0
                a1 /= a0
                a2 /= a0
                # Direct form II
                filtered = np.zeros(n, dtype=np.float64)
                x1 = x2 = y1 = y2 = 0.0
                for i in range(n):
                    x0 = source[i]
                    y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
                    filtered[i] = y0
                    x2, x1 = x1, x0
                    y2, y1 = y1, y0
                vocal += filtered

            # Normalize vocal output
            peak = np.max(np.abs(vocal))
            if peak > 0:
                vocal /= peak

            mix += vocal * fl["volume"]

        # -- Granular synthesis layers -------------------------------------
        for gran in self._granular_layers:
            rng = np.random.default_rng(gran.seed)
            grain_samples = max(1, int(gran.grain_size * sr))
            num_grains = max(1, int(gran.density * duration))
            grain_out = np.zeros(n)
            # Generate a source grain from the base frequency
            grain_t = np.arange(grain_samples) / sr
            grain_src = np.sin(2 * np.pi * freq * grain_t)
            # Apply Hann window to each grain for smooth overlap
            grain_window = np.hanning(grain_samples)
            grain_src *= grain_window
            # Place grains
            for _ in range(num_grains):
                # Evenly spaced with scatter
                base_pos = rng.uniform(0, n - grain_samples) if gran.scatter > 0 else 0
                pos = int(np.clip(base_pos, 0, n - grain_samples))
                grain_out[pos : pos + grain_samples] += grain_src
            # Normalize grain output
            grain_peak = np.max(np.abs(grain_out))
            if grain_peak > 0:
                grain_out /= grain_peak
            mix += grain_out * gran.volume

        # -- Physical modeling layers --------------------------------------
        for phys in self._physical_layers:
            if phys.model_type == "karplus_strong":
                layer = _karplus_strong(
                    freq,
                    n,
                    sr,
                    decay=phys.params.get("decay", 0.996),
                    brightness=phys.params.get("brightness", 0.5),
                )
            elif phys.model_type == "waveguide_pipe":
                layer = _waveguide_pipe(
                    freq,
                    n,
                    sr,
                    feedback=phys.params.get("feedback", 0.98),
                    brightness=phys.params.get("brightness", 0.6),
                )
            elif phys.model_type == "modal":
                layer = _modal_synth(freq, n, sr)
            elif phys.model_type == "bowed_string":
                layer = _bowed_string(
                    freq,
                    n,
                    sr,
                    bow_pressure=phys.params.get("bow_pressure", 0.5),
                    brightness=phys.params.get("brightness", 0.6),
                )
            else:
                layer = np.zeros(n)
            mix += layer * phys.volume

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

        # -- Spectral processing -------------------------------------------
        for proc in self._spectral_procs:
            mix = proc(mix, sr)

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

    def analyze(self, freq: float = 440.0, duration: float = 1.0, sr: int = 22050) -> "Timbre":
        """Analyze the timbre of this sound design.

        Renders the sound and computes spectral features: centroid, bandwidth,
        flatness, rolloff, and RMS energy. Returns a ``Timbre`` object for
        comparison and morphing.

        Example::

            t = SoundDesigner("saw").add_osc("sawtooth").analyze()
            print(t)  # Timbre(centroid=2200Hz, bw=1800Hz, ...)
        """
        audio = self.render(freq, duration, sr)
        return _analyze_audio(audio, sr)

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
            "granular_layers": [
                {
                    "grain_size": g.grain_size,
                    "density": g.density,
                    "scatter": g.scatter,
                    "volume": g.volume,
                    "seed": g.seed,
                }
                for g in self._granular_layers
            ],
            "physical_layers": [
                {
                    "model_type": p.model_type,
                    "params": p.params,
                    "volume": p.volume,
                }
                for p in self._physical_layers
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
        for g_data in data.get("granular_layers", []):
            sd.granular(
                g_data.get("grain_size", 0.05),
                g_data.get("density", 10.0),
                g_data.get("scatter", 0.3),
                g_data.get("volume", 1.0),
                g_data.get("seed"),
            )
        for p_data in data.get("physical_layers", []):
            sd._physical_layers.append(
                _PhysicalModelSpec(
                    p_data["model_type"],
                    p_data.get("params", {}),
                    p_data.get("volume", 1.0),
                )
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
        if self._granular_layers:
            parts.append(f"granular={len(self._granular_layers)}")
        if self._physical_layers:
            parts.append(f"physical={len(self._physical_layers)}")
        if self._spectral_procs:
            parts.append(f"spectral={len(self._spectral_procs)}")
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

# ---------------------------------------------------------------------------
# Spectral processing functions (for use with SoundDesigner.spectral())
# ---------------------------------------------------------------------------


def spectral_freeze(amount: float = 0.8) -> "Callable":
    """Create a spectral freeze function — sustains spectral content.

    Higher amount = more frozen (static, drone-like).
    """

    def _process(audio: FloatArray, sr: int) -> FloatArray:
        hop = 512
        win = 2048
        n = len(audio)
        if n < win:
            return audio
        # STFT
        num_frames = (n - win) // hop + 1
        frames = np.zeros((num_frames, win))
        for i in range(num_frames):
            start = i * hop
            frames[i] = audio[start : start + win] * np.hanning(win)
        spectra = np.fft.rfft(frames, axis=1)
        magnitudes = np.abs(spectra)
        phases = np.angle(spectra)
        # Freeze: blend each frame's magnitude with the average
        avg_mag = np.mean(magnitudes, axis=0)
        for i in range(num_frames):
            magnitudes[i] = magnitudes[i] * (1 - amount) + avg_mag * amount
        # ISTFT
        spectra = magnitudes * np.exp(1j * phases)
        frames = np.fft.irfft(spectra, n=win, axis=1)
        out = np.zeros(n)
        for i in range(num_frames):
            start = i * hop
            end = min(start + win, n)
            out[start:end] += frames[i][: end - start]
        peak = np.max(np.abs(out))
        if peak > 0:
            out /= peak
        return out

    return _process


def spectral_shift(semitones: float = 7.0) -> "Callable":
    """Create a spectral shift function — shifts all frequencies up/down.

    Positive semitones = shift up, negative = shift down.
    """

    def _process(audio: FloatArray, sr: int) -> FloatArray:
        ratio = 2.0 ** (semitones / 12.0)
        n = len(audio)
        spectrum = np.fft.rfft(audio)
        shifted = np.zeros_like(spectrum)
        for i in range(len(spectrum)):
            new_i = int(i * ratio)
            if 0 <= new_i < len(shifted):
                shifted[new_i] += spectrum[i]
        out = np.fft.irfft(shifted, n=n)
        peak = np.max(np.abs(out))
        if peak > 0:
            out /= peak
        return out

    return _process


def spectral_smear(amount: float = 0.5) -> "Callable":
    """Create a spectral smear function — blurs spectral content across bins.

    Creates ghostly, diffuse textures.
    """

    def _process(audio: FloatArray, sr: int) -> FloatArray:
        spectrum = np.fft.rfft(audio)
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)
        # Gaussian-like blur on magnitudes
        kernel_size = max(1, int(amount * 50))
        kernel = np.ones(kernel_size) / kernel_size
        smeared = np.convolve(magnitudes, kernel, mode="same")
        out = np.fft.irfft(smeared * np.exp(1j * phases), n=len(audio))
        peak = np.max(np.abs(out))
        if peak > 0:
            out /= peak
        return out

    return _process


# ---------------------------------------------------------------------------
# Timbre analysis (v9.0)
# ---------------------------------------------------------------------------


class Timbre:
    """Spectral fingerprint of a rendered sound.

    Captures the frequency content of a SoundDesigner's output for comparison,
    distance measurement, and interpolation.

    Example::

        t1 = SoundDesigner("saw").add_osc("sawtooth").analyze()
        t2 = SoundDesigner("sine").add_osc("sine").analyze()
        print(t1.distance(t2))       # perceptual distance
        hybrid = t1.morph(t2, 0.5)   # interpolated timbre
    """

    def __init__(
        self,
        centroid: float,
        bandwidth: float,
        flatness: float,
        rolloff: float,
        rms: float,
        spectrum: FloatArray,
    ) -> None:
        self.centroid = centroid  # spectral centroid in Hz
        self.bandwidth = bandwidth  # spectral bandwidth in Hz
        self.flatness = flatness  # 0 = tonal, 1 = noisy
        self.rolloff = rolloff  # frequency below which 85% of energy lies
        self.rms = rms  # root mean square energy
        self.spectrum = spectrum  # magnitude spectrum (normalized)

    def distance(self, other: "Timbre") -> float:
        """Perceptual distance between two timbres (0 = identical)."""
        # Weighted Euclidean on normalized features
        c_diff = (self.centroid - other.centroid) / 10000.0
        b_diff = (self.bandwidth - other.bandwidth) / 5000.0
        f_diff = self.flatness - other.flatness
        r_diff = (self.rolloff - other.rolloff) / 10000.0
        e_diff = self.rms - other.rms
        return float(np.sqrt(c_diff**2 + b_diff**2 + f_diff**2 + r_diff**2 + e_diff**2))

    def morph(self, other: "Timbre", amount: float = 0.5) -> "Timbre":
        """Interpolate between two timbres."""
        a = 1.0 - amount
        b = amount
        min_len = min(len(self.spectrum), len(other.spectrum))
        return Timbre(
            centroid=self.centroid * a + other.centroid * b,
            bandwidth=self.bandwidth * a + other.bandwidth * b,
            flatness=self.flatness * a + other.flatness * b,
            rolloff=self.rolloff * a + other.rolloff * b,
            rms=self.rms * a + other.rms * b,
            spectrum=self.spectrum[:min_len] * a + other.spectrum[:min_len] * b,
        )

    def to_dict(self) -> dict:
        """Serialize timbre fingerprint."""
        return {
            "centroid": self.centroid,
            "bandwidth": self.bandwidth,
            "flatness": self.flatness,
            "rolloff": self.rolloff,
            "rms": self.rms,
        }

    def __repr__(self) -> str:
        return (
            f"Timbre(centroid={self.centroid:.0f}Hz, bw={self.bandwidth:.0f}Hz, "
            f"flat={self.flatness:.3f}, rolloff={self.rolloff:.0f}Hz, rms={self.rms:.3f})"
        )


def _analyze_audio(audio: FloatArray, sr: int) -> "Timbre":
    """Compute spectral features from a rendered audio array."""
    spectrum = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), d=1.0 / sr)

    # Normalize spectrum
    total = np.sum(spectrum)
    if total == 0:
        return Timbre(0.0, 0.0, 0.0, 0.0, 0.0, spectrum)

    norm = spectrum / total

    # Spectral centroid
    centroid = float(np.sum(freqs * norm))

    # Spectral bandwidth
    bandwidth = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * norm)))

    # Spectral flatness (geometric mean / arithmetic mean of magnitudes)
    eps = 1e-10
    log_spec = np.log(spectrum + eps)
    geo_mean = np.exp(np.mean(log_spec))
    arith_mean = np.mean(spectrum)
    flatness = float(geo_mean / (arith_mean + eps))

    # Spectral rolloff (85%)
    cumsum = np.cumsum(spectrum)
    rolloff_idx = np.searchsorted(cumsum, 0.85 * total)
    rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)])

    # RMS
    rms = float(np.sqrt(np.mean(audio**2)))

    return Timbre(centroid, bandwidth, flatness, rolloff, rms, spectrum / (np.max(spectrum) + eps))


# ---------------------------------------------------------------------------
# Granular Presets
# ---------------------------------------------------------------------------

grain_cloud = (
    SoundDesigner("grain_cloud")
    .add_osc("sine", volume=0.3)
    .granular(grain_size=0.06, density=20, scatter=0.7, volume=0.7, seed=42)
    .envelope(attack=0.5, decay=0.3, sustain=0.4, release=1.0)
    .filter("lowpass", cutoff=3000, resonance=0.4)
)

grain_shimmer = (
    SoundDesigner("grain_shimmer")
    .noise("white", volume=0.2, seed=10)
    .granular(grain_size=0.03, density=30, scatter=0.5, volume=0.8, seed=77)
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.8)
    .filter("bandpass", cutoff=4000, resonance=1.5)
)

# ---------------------------------------------------------------------------
# Physical Modeling Presets
# ---------------------------------------------------------------------------

pm_guitar = (
    SoundDesigner("pm_guitar")
    .physical_model("karplus_strong", volume=0.9, decay=0.998, brightness=0.5)
    .envelope(attack=0.001, decay=0.5, sustain=0.1, release=0.3)
)

pm_flute = (
    SoundDesigner("pm_flute")
    .physical_model("waveguide_pipe", volume=0.8, feedback=0.97, brightness=0.65)
    .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

pm_gong = (
    SoundDesigner("pm_gong")
    .physical_model("modal", volume=0.9)
    .envelope(attack=0.001, decay=1.5, sustain=0.1, release=1.0)
    .filter("lowpass", cutoff=6000, resonance=0.5)
)

pm_violin = (
    SoundDesigner("pm_violin")
    .physical_model("bowed_string", volume=0.85, bow_pressure=0.5, brightness=0.6)
    .envelope(attack=0.08, decay=0.2, sustain=0.8, release=0.4)
    .filter("lowpass", cutoff=5000, resonance=0.4)
)

# ---------------------------------------------------------------------------
# Vocal / Formant presets (v165.0)
# ---------------------------------------------------------------------------

choir_ah = (
    SoundDesigner("choir_ah")
    .formant("ah", breathiness=0.2, vibrato_rate=5.5, vibrato_depth=0.02, volume=0.7)
    .envelope(attack=0.2, decay=0.1, sustain=0.8, release=0.5)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

choir_oo = (
    SoundDesigner("choir_oo")
    .formant("oo", breathiness=0.15, vibrato_rate=5.0, vibrato_depth=0.025, volume=0.7)
    .envelope(attack=0.25, decay=0.1, sustain=0.8, release=0.6)
    .filter("lowpass", cutoff=3000, resonance=0.3)
)

ethereal_voice = (
    SoundDesigner("ethereal_voice")
    .formant("oh", breathiness=0.4, vibrato_rate=4.0, vibrato_depth=0.03, volume=0.5)
    .formant("ee", breathiness=0.5, vibrato_rate=4.5, vibrato_depth=0.02, volume=0.3)
    .envelope(attack=0.4, decay=0.2, sustain=0.7, release=0.8)
    .filter("lowpass", cutoff=3500, resonance=0.4)
)

whisper_pad = (
    SoundDesigner("whisper_pad")
    .formant("eh", breathiness=0.8, vibrato_rate=3.0, vibrato_depth=0.01, volume=0.6)
    .envelope(attack=0.5, decay=0.15, sustain=0.6, release=1.0)
    .filter("lowpass", cutoff=2500, resonance=0.5)
)

vocal_lead = (
    SoundDesigner("vocal_lead")
    .formant("ah", breathiness=0.15, vibrato_rate=6.0, vibrato_depth=0.03, volume=0.8)
    .envelope(attack=0.05, decay=0.15, sustain=0.7, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.4)
)

# ---------------------------------------------------------------------------
# Synth presets (v165.0)
# ---------------------------------------------------------------------------

acid_bass = (
    SoundDesigner("acid_bass")
    .add_osc("sawtooth", volume=0.7)
    .envelope(attack=0.005, decay=0.2, sustain=0.3, release=0.1)
    .filter("lowpass", cutoff=800, resonance=0.85)
    .lfo("filter_cutoff", rate=0.3, depth=0.6)
)

detuned_pad = (
    SoundDesigner("detuned_pad")
    .add_osc("sawtooth", volume=0.2)
    .add_osc("sawtooth", detune_cents=15, volume=0.2)
    .add_osc("sawtooth", detune_cents=-15, volume=0.2)
    .add_osc("square", detune_cents=7, volume=0.1)
    .envelope(attack=0.5, decay=0.2, sustain=0.8, release=1.0)
    .filter("lowpass", cutoff=2000, resonance=0.5)
    .lfo("filter_cutoff", rate=0.1, depth=0.4)
)

reese_bass = (
    SoundDesigner("reese_bass")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("sawtooth", detune_cents=3, volume=0.5)
    .envelope(attack=0.005, decay=0.1, sustain=0.8, release=0.15)
    .filter("lowpass", cutoff=600, resonance=0.6)
    .lfo("filter_cutoff", rate=0.2, depth=0.5)
)

hoover = (
    SoundDesigner("hoover")
    .add_osc("sawtooth", volume=0.35)
    .add_osc("sawtooth", detune_cents=20, volume=0.3)
    .add_osc("sawtooth", detune_cents=-20, volume=0.3)
    .add_osc("square", detune_cents=-1200, volume=0.2)
    .envelope(attack=0.01, decay=0.3, sustain=0.5, release=0.3)
    .filter("lowpass", cutoff=3000, resonance=0.7)
    .lfo("pitch", rate=4.0, depth=0.1)
)

pluck_synth = (
    SoundDesigner("pluck_synth")
    .add_osc("sawtooth", volume=0.6)
    .add_osc("square", detune_cents=5, volume=0.3)
    .envelope(attack=0.002, decay=0.15, sustain=0.0, release=0.1)
    .filter("lowpass", cutoff=5000, resonance=0.4)
)

ice_pad = (
    SoundDesigner("ice_pad")
    .add_osc("triangle", volume=0.3)
    .add_osc("sine", detune_cents=1200, volume=0.15)
    .add_osc("sine", detune_cents=1900, volume=0.1)
    .envelope(attack=0.8, decay=0.3, sustain=0.6, release=1.5)
    .filter("lowpass", cutoff=3000, resonance=0.3)
)

dark_drone = (
    SoundDesigner("dark_drone")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("square", detune_cents=-2400, volume=0.4)
    .envelope(attack=1.0, decay=0.5, sustain=0.9, release=2.0)
    .filter("lowpass", cutoff=500, resonance=0.7)
    .lfo("filter_cutoff", rate=0.05, depth=0.3)
)

# ---------------------------------------------------------------------------
# Orchestral / acoustic presets (v165.0)
# ---------------------------------------------------------------------------

pm_cello = (
    SoundDesigner("pm_cello")
    .physical_model("bowed_string", volume=0.85, bow_pressure=0.55, brightness=0.5)
    .envelope(attack=0.1, decay=0.2, sustain=0.8, release=0.5)
    .filter("lowpass", cutoff=3500, resonance=0.3)
)

pm_viola = (
    SoundDesigner("pm_viola")
    .physical_model("bowed_string", volume=0.8, bow_pressure=0.45, brightness=0.55)
    .envelope(attack=0.09, decay=0.15, sustain=0.8, release=0.45)
    .filter("lowpass", cutoff=4200, resonance=0.35)
)

pm_bass_guitar = (
    SoundDesigner("pm_bass_guitar")
    .physical_model("karplus_strong", volume=0.9, decay=0.995, brightness=0.3)
    .envelope(attack=0.002, decay=0.3, sustain=0.2, release=0.2)
    .filter("lowpass", cutoff=2000, resonance=0.4)
)

fm_clarinet = (
    SoundDesigner("fm_clarinet")
    .fm("square", mod_ratio=3.0, mod_index=1.5, volume=0.7)
    .envelope(attack=0.03, decay=0.1, sustain=0.7, release=0.2)
    .filter("lowpass", cutoff=3000, resonance=0.4)
)

fm_marimba = (
    SoundDesigner("fm_marimba")
    .fm("sine", mod_ratio=4.0, mod_index=2.0, volume=0.8)
    .envelope(attack=0.001, decay=0.4, sustain=0.0, release=0.3)
    .filter("lowpass", cutoff=6000, resonance=0.2)
)

pm_kalimba = (
    SoundDesigner("pm_kalimba")
    .physical_model("modal", volume=0.8)
    .envelope(attack=0.001, decay=0.6, sustain=0.05, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.5)
)

# ---------------------------------------------------------------------------
# Drum / percussion presets (v165.0)
# ---------------------------------------------------------------------------

trap_808 = (
    SoundDesigner("trap_808")
    .add_osc("sine", volume=0.9)
    .envelope(attack=0.001, decay=0.8, sustain=0.0, release=0.3)
    .filter("lowpass", cutoff=200, resonance=0.3)
    .lfo("pitch", rate=0.5, depth=0.8)
)

clap = (
    SoundDesigner("clap")
    .granular(grain_size=0.002, density=200, scatter=1.0, seed=77)
    .envelope(attack=0.001, decay=0.08, sustain=0.0, release=0.05)
    .filter("bandpass", cutoff=1500, resonance=0.8)
)

rimshot = (
    SoundDesigner("rimshot")
    .add_osc("sine", volume=0.5)
    .granular(grain_size=0.001, density=300, scatter=1.0, seed=88)
    .envelope(attack=0.001, decay=0.03, sustain=0.0, release=0.02)
    .filter("highpass", cutoff=2000, resonance=0.5)
)

# ---------------------------------------------------------------------------
# Granular expansion (v168.0)
# ---------------------------------------------------------------------------

grain_texture = (
    SoundDesigner("grain_texture")
    .granular(grain_size=0.08, density=12, scatter=0.6, seed=33)
    .envelope(attack=0.3, decay=0.2, sustain=0.7, release=0.8)
    .filter("lowpass", cutoff=3000, resonance=0.4)
)

grain_stutter = (
    SoundDesigner("grain_stutter")
    .granular(grain_size=0.01, density=60, scatter=0.3, seed=55)
    .envelope(attack=0.002, decay=0.1, sustain=0.3, release=0.1)
    .filter("bandpass", cutoff=2500, resonance=0.7)
)

grain_rain = (
    SoundDesigner("grain_rain")
    .granular(grain_size=0.015, density=40, scatter=0.9, seed=99)
    .envelope(attack=0.5, decay=0.3, sustain=0.5, release=1.0)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

# ---------------------------------------------------------------------------
# Wavetable expansion (v168.0)
# ---------------------------------------------------------------------------

wt_glass = (
    SoundDesigner("wt_glass")
    .add_wavetable(Wavetable.from_harmonics([1.0, 0.0, 0.5, 0.0, 0.25, 0.0, 0.125]), volume=0.6)
    .envelope(attack=0.001, decay=0.4, sustain=0.1, release=0.5)
    .filter("lowpass", cutoff=6000, resonance=0.4)
)

wt_vocal_formant = (
    SoundDesigner("wt_vocal_formant")
    .add_wavetable(Wavetable.from_harmonics([1.0, 0.7, 0.3, 0.8, 0.2, 0.1, 0.05]), volume=0.5)
    .add_wavetable(
        Wavetable.from_harmonics([0.5, 1.0, 0.4, 0.2, 0.6, 0.1]), detune_cents=5, volume=0.3
    )
    .envelope(attack=0.1, decay=0.15, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=3500, resonance=0.5)
)

wt_digital = (
    SoundDesigner("wt_digital")
    .add_wavetable(Wavetable.from_wave("square"), volume=0.4)
    .add_wavetable(Wavetable.from_wave("sawtooth"), detune_cents=12, volume=0.3)
    .envelope(attack=0.005, decay=0.1, sustain=0.5, release=0.2)
    .filter("lowpass", cutoff=4000, resonance=0.6)
)

# ---------------------------------------------------------------------------
# Ethnic / world instruments (v168.0)
# ---------------------------------------------------------------------------

sitar = (
    SoundDesigner("sitar")
    .physical_model("karplus_strong", volume=0.85, decay=0.996, brightness=0.8)
    .fm("sine", mod_ratio=3.0, mod_index=1.0, volume=0.15)
    .envelope(attack=0.002, decay=0.5, sustain=0.15, release=0.4)
    .filter("lowpass", cutoff=5000, resonance=0.5)
)

shamisen = (
    SoundDesigner("shamisen")
    .physical_model("karplus_strong", volume=0.9, decay=0.993, brightness=0.65)
    .envelope(attack=0.001, decay=0.3, sustain=0.05, release=0.2)
    .filter("lowpass", cutoff=4500, resonance=0.4)
)

didgeridoo = (
    SoundDesigner("didgeridoo")
    .add_osc("sawtooth", volume=0.4)
    .formant("oh", breathiness=0.3, vibrato_rate=3.0, vibrato_depth=0.01, volume=0.4)
    .envelope(attack=0.1, decay=0.2, sustain=0.85, release=0.5)
    .filter("lowpass", cutoff=800, resonance=0.7)
)

# ---------------------------------------------------------------------------
# Percussion / texture expansion (v168.0)
# ---------------------------------------------------------------------------

tabla = (
    SoundDesigner("tabla")
    .physical_model("modal", volume=0.8)
    .add_osc("sine", volume=0.3)
    .envelope(attack=0.001, decay=0.2, sustain=0.05, release=0.15)
    .filter("bandpass", cutoff=800, resonance=0.6)
)

shaker = (
    SoundDesigner("shaker")
    .granular(grain_size=0.002, density=150, scatter=0.8, seed=66)
    .envelope(attack=0.001, decay=0.04, sustain=0.0, release=0.03)
    .filter("highpass", cutoff=5000, resonance=0.3)
)

taiko = (
    SoundDesigner("taiko")
    .add_osc("sine", volume=0.7)
    .physical_model("modal", volume=0.3)
    .envelope(attack=0.002, decay=0.6, sustain=0.1, release=0.5)
    .filter("lowpass", cutoff=500, resonance=0.5)
)

# ---------------------------------------------------------------------------
# Wavetable scanning presets (v169.0)
# ---------------------------------------------------------------------------

wt_scan_evolve = (
    SoundDesigner("wt_scan_evolve")
    .wavetable_scan(
        [
            Wavetable.from_wave("sine"),
            Wavetable.from_wave("sawtooth"),
            Wavetable.from_wave("square"),
            Wavetable.from_wave("triangle"),
        ],
        scan_rate=0.3,
        volume=0.6,
    )
    .envelope(attack=0.05, decay=0.15, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.5)
)

wt_scan_pad = (
    SoundDesigner("wt_scan_pad")
    .wavetable_scan(
        [
            Wavetable.from_harmonics([1.0]),
            Wavetable.from_harmonics([1.0, 0.5, 0.25]),
            Wavetable.from_harmonics([1.0, 0.5, 0.25, 0.125, 0.0625]),
            Wavetable.from_harmonics([1.0, 0.3, 0.1, 0.3, 0.1]),
        ],
        scan_rate=0.15,
        volume=0.5,
    )
    .envelope(attack=0.4, decay=0.2, sustain=0.8, release=0.8)
    .filter("lowpass", cutoff=3000, resonance=0.4)
    .lfo("filter_cutoff", rate=0.1, depth=0.3)
)

wt_scan_lead = (
    SoundDesigner("wt_scan_lead")
    .wavetable_scan(
        [Wavetable.from_wave("sawtooth"), Wavetable.from_wave("square")],
        scan_rate=1.5,
        volume=0.6,
        detune_cents=5,
    )
    .envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.2)
    .filter("lowpass", cutoff=5000, resonance=0.6)
)

wt_scan_bass = (
    SoundDesigner("wt_scan_bass")
    .wavetable_scan(
        [
            Wavetable.from_wave("sine"),
            Wavetable.from_wave("sawtooth"),
            Wavetable.from_wave("square"),
        ],
        scan_rate=0.5,
        volume=0.7,
    )
    .envelope(attack=0.005, decay=0.15, sustain=0.7, release=0.15)
    .filter("lowpass", cutoff=1200, resonance=0.7)
)

wt_scan_texture = (
    SoundDesigner("wt_scan_texture")
    .wavetable_scan(
        [
            Wavetable.from_harmonics([1.0, 0.0, 0.5, 0.0, 0.25]),
            Wavetable.from_harmonics([0.5, 1.0, 0.3, 0.8, 0.1]),
            Wavetable.from_harmonics([0.1, 0.3, 1.0, 0.3, 0.5]),
        ],
        scan_rate=0.08,
        volume=0.5,
    )
    .envelope(attack=0.8, decay=0.3, sustain=0.6, release=1.2)
    .filter("lowpass", cutoff=2000, resonance=0.5)
)

# ---------------------------------------------------------------------------
# Spectral presets (v169.0)
# ---------------------------------------------------------------------------

spectral_frozen = (
    SoundDesigner("spectral_frozen")
    .add_osc("sawtooth", volume=0.6)
    .spectral(spectral_freeze(0.9))
    .envelope(attack=0.3, decay=0.2, sustain=0.8, release=1.0)
    .filter("lowpass", cutoff=3000, resonance=0.3)
)

spectral_shifted = (
    SoundDesigner("spectral_shifted")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("square", detune_cents=5, volume=0.3)
    .spectral(spectral_shift(5.0))
    .envelope(attack=0.02, decay=0.15, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.4)
)

spectral_smeared = (
    SoundDesigner("spectral_smeared")
    .add_osc("sawtooth", volume=0.5)
    .spectral(spectral_smear(0.7))
    .envelope(attack=0.5, decay=0.2, sustain=0.7, release=0.8)
    .filter("lowpass", cutoff=2500, resonance=0.5)
)

PRESETS = {
    # Original 18
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
    "grain_cloud": grain_cloud,
    "grain_shimmer": grain_shimmer,
    "pm_guitar": pm_guitar,
    "pm_flute": pm_flute,
    "pm_gong": pm_gong,
    "pm_violin": pm_violin,
    # Vocal (v165)
    "choir_ah": choir_ah,
    "choir_oo": choir_oo,
    "ethereal_voice": ethereal_voice,
    "whisper_pad": whisper_pad,
    "vocal_lead": vocal_lead,
    # Synth (v165)
    "acid_bass": acid_bass,
    "detuned_pad": detuned_pad,
    "reese_bass": reese_bass,
    "hoover": hoover,
    "pluck_synth": pluck_synth,
    "ice_pad": ice_pad,
    "dark_drone": dark_drone,
    # Orchestral (v165)
    "pm_cello": pm_cello,
    "pm_viola": pm_viola,
    "pm_bass_guitar": pm_bass_guitar,
    "fm_clarinet": fm_clarinet,
    "fm_marimba": fm_marimba,
    "pm_kalimba": pm_kalimba,
    # Drums (v165)
    "trap_808": trap_808,
    "clap": clap,
    "rimshot": rimshot,
    # Granular (v168)
    "grain_texture": grain_texture,
    "grain_stutter": grain_stutter,
    "grain_rain": grain_rain,
    # Wavetable (v168)
    "wt_glass": wt_glass,
    "wt_vocal_formant": wt_vocal_formant,
    "wt_digital": wt_digital,
    # Ethnic (v168)
    "sitar": sitar,
    "shamisen": shamisen,
    "didgeridoo": didgeridoo,
    # Percussion (v168)
    "tabla": tabla,
    "shaker": shaker,
    "taiko": taiko,
    # Wavetable scanning (v169)
    "wt_scan_evolve": wt_scan_evolve,
    "wt_scan_pad": wt_scan_pad,
    "wt_scan_lead": wt_scan_lead,
    "wt_scan_bass": wt_scan_bass,
    "wt_scan_texture": wt_scan_texture,
    # Spectral (v169)
    "spectral_frozen": spectral_frozen,
    "spectral_shifted": spectral_shifted,
    "spectral_smeared": spectral_smeared,
}
