"""Parameter automation and modulation routing.

Automate any numeric parameter over time with keyframe curves. Route
modulation sources (LFO, envelope follower) to destinations (volume,
pan, filter cutoff) through a modulation matrix.

Example::

    from code_music.automation import Automation, ModMatrix

    # Volume fade-in over 4 beats
    auto = Automation([(0, 0.0), (4, 0.8), (12, 0.3)])

    # Modulation matrix
    mm = ModMatrix()
    mm.connect("lfo1", "pad.volume", amount=0.3, rate=2.0)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


# ---------------------------------------------------------------------------
# Automation Curve
# ---------------------------------------------------------------------------


class Automation:
    """Time-value curve for automating any numeric parameter.

    Keyframes are (beat, value) pairs. Values between keyframes are
    interpolated using the selected mode.

    Args:
        keyframes: List of (beat, value) tuples, sorted by beat.
        mode:      Interpolation: 'linear', 'exponential', or 'smoothstep'.

    Example::

        vol = Automation([(0, 0.0), (4, 0.8), (12, 0.3)])
        values = vol.sample(bpm=120, sr=44100, duration_beats=16)
    """

    def __init__(
        self,
        keyframes: list[tuple[float, float]],
        mode: str = "linear",
    ) -> None:
        if not keyframes:
            raise ValueError("Automation requires at least one keyframe")
        self.keyframes = sorted(keyframes, key=lambda k: k[0])
        if mode not in ("linear", "exponential", "smoothstep"):
            raise ValueError(f"Unknown mode {mode!r}. Choose: linear, exponential, smoothstep")
        self.mode = mode

    def value_at(self, beat: float) -> float:
        """Get the interpolated value at a specific beat position."""
        if beat <= self.keyframes[0][0]:
            return self.keyframes[0][1]
        if beat >= self.keyframes[-1][0]:
            return self.keyframes[-1][1]

        # Find surrounding keyframes
        for i in range(len(self.keyframes) - 1):
            b0, v0 = self.keyframes[i]
            b1, v1 = self.keyframes[i + 1]
            if b0 <= beat <= b1:
                t = (beat - b0) / (b1 - b0) if b1 != b0 else 0.0
                return self._interpolate(v0, v1, t)
        return self.keyframes[-1][1]

    def sample(self, bpm: float, sr: int, duration_beats: float) -> FloatArray:
        """Sample the automation curve into an array of per-sample values.

        Args:
            bpm:            Tempo in BPM.
            sr:             Sample rate.
            duration_beats: Total duration in beats.

        Returns:
            Float64 array with one value per audio sample.
        """
        duration_secs = duration_beats * 60.0 / bpm
        n = int(duration_secs * sr)
        if n <= 0:
            return np.array([], dtype=np.float64)

        beats_per_sample = bpm / (60.0 * sr)
        beats = np.arange(n) * beats_per_sample
        values = np.zeros(n)
        for i, beat in enumerate(beats):
            values[i] = self.value_at(float(beat))
        return values

    def _interpolate(self, v0: float, v1: float, t: float) -> float:
        if self.mode == "linear":
            return v0 + (v1 - v0) * t
        elif self.mode == "exponential":
            # Avoid log(0)
            eps = 1e-6
            a = max(abs(v0), eps)
            b = max(abs(v1), eps)
            sign = 1.0 if v1 >= 0 else -1.0
            return sign * a * (b / a) ** t
        elif self.mode == "smoothstep":
            t = t * t * (3 - 2 * t)  # Hermite smoothstep
            return v0 + (v1 - v0) * t
        return v0 + (v1 - v0) * t

    def __repr__(self) -> str:
        pts = len(self.keyframes)
        return f"Automation({pts} keyframes, mode={self.mode!r})"


# ---------------------------------------------------------------------------
# Envelope Follower (v143.0)
# ---------------------------------------------------------------------------


class EnvFollower:
    """Extract an amplitude envelope from an audio signal.

    Follows the loudness contour of audio using rectification + smoothing.
    The classic sidechain pump: feed a kick drum into EnvFollower, then
    invert the output to duck a pad. Works at mix level without needing
    the sidechain() effect.

    Args:
        attack_ms:  Attack time in milliseconds (how fast envelope rises).
        release_ms: Release time in milliseconds (how fast envelope falls).

    Example::

        env = EnvFollower(attack_ms=5, release_ms=100)

        # Extract envelope from kick audio
        kick_env = env.follow(kick_audio, sample_rate=44100)

        # Apply as sidechain duck to pad
        ducked_pad = env.duck(pad_audio, kick_audio, sample_rate=44100, amount=0.8)
    """

    def __init__(self, attack_ms: float = 5.0, release_ms: float = 100.0) -> None:
        self.attack_ms = attack_ms
        self.release_ms = release_ms

    def follow(self, audio: FloatArray, sample_rate: int = 44100) -> FloatArray:
        """Extract the amplitude envelope from audio.

        Args:
            audio:       Mono or stereo audio signal.
            sample_rate: Sample rate in Hz.

        Returns:
            Envelope signal (same length as audio, values 0.0-1.0).
        """
        import math

        # Convert stereo to mono for envelope detection
        if audio.ndim == 2:
            mono = np.mean(np.abs(audio), axis=1)
        else:
            mono = np.abs(audio)

        n = len(mono)
        env = np.zeros(n, dtype=np.float64)

        # Ballistics coefficients
        attack_coeff = math.exp(-1.0 / max(1, self.attack_ms * sample_rate / 1000))
        release_coeff = math.exp(-1.0 / max(1, self.release_ms * sample_rate / 1000))

        # One-pole envelope follower
        prev = 0.0
        for i in range(n):
            inp = mono[i]
            if inp > prev:
                prev = attack_coeff * prev + (1.0 - attack_coeff) * inp
            else:
                prev = release_coeff * prev + (1.0 - release_coeff) * inp
            env[i] = prev

        # Normalize to 0-1
        peak = np.max(env)
        if peak > 0:
            env /= peak

        return env

    def duck(
        self,
        target: FloatArray,
        sidechain: FloatArray,
        sample_rate: int = 44100,
        amount: float = 0.8,
        invert: bool = True,
    ) -> FloatArray:
        """Apply sidechain ducking to target using sidechain signal.

        The classic pump effect: when the sidechain signal is loud, the
        target gets quiet. When the sidechain is quiet, the target plays
        at full volume.

        Args:
            target:      Audio to duck (pad, bass, etc).
            sidechain:   Audio to follow (kick, vocal, etc).
            sample_rate: Sample rate.
            amount:      Ducking depth (0=none, 1=full silence on hit).
            invert:      If True, envelope ducks target (default sidechain behavior).
                         If False, envelope boosts target (gating).

        Returns:
            Ducked audio (same shape as target).

        Example::

            env = EnvFollower(attack_ms=5, release_ms=150)
            pumped_pad = env.duck(pad_audio, kick_audio, amount=0.8)
        """
        n = min(len(target), len(sidechain))
        env = self.follow(sidechain[:n], sample_rate)

        if invert:
            gain = 1.0 - amount * env
        else:
            gain = (1.0 - amount) + amount * env

        if target.ndim == 2:
            return target[:n] * gain[:, np.newaxis]
        return target[:n] * gain

    def gate(
        self,
        target: FloatArray,
        sidechain: FloatArray,
        sample_rate: int = 44100,
        threshold: float = 0.3,
        amount: float = 0.9,
    ) -> FloatArray:
        """Gate target audio using sidechain envelope.

        When sidechain is below threshold, target is attenuated. When
        above threshold, target plays through. Classic noise gate or
        rhythmic gating effect.

        Args:
            target:      Audio to gate.
            sidechain:   Audio to follow for gate trigger.
            sample_rate: Sample rate.
            threshold:   Gate opens above this envelope level (0-1).
            amount:      Attenuation depth when gate is closed (0=none, 1=full).

        Returns:
            Gated audio.
        """
        n = min(len(target), len(sidechain))
        env = self.follow(sidechain[:n], sample_rate)

        # Smooth gate: sigmoid around threshold
        gate_signal = 1.0 / (1.0 + np.exp(-20.0 * (env - threshold)))
        gain = (1.0 - amount) + amount * gate_signal

        if target.ndim == 2:
            return target[:n] * gain[:, np.newaxis]
        return target[:n] * gain


# ---------------------------------------------------------------------------
# Modulation Matrix
# ---------------------------------------------------------------------------


class _ModRoute:
    __slots__ = ("source", "dest", "amount", "rate")

    def __init__(self, source: str, dest: str, amount: float, rate: float):
        self.source = source
        self.dest = dest
        self.amount = amount
        self.rate = rate


class ModMatrix:
    """Modulation routing matrix - connect sources to destinations.

    Sources: 'lfo1', 'lfo2', 'random', 'envelope', 'env_follower'
    Destinations: '<track>.volume', '<track>.pan', '<track>.filter_cutoff'

    Example::

        mm = ModMatrix()
        mm.connect("lfo1", "pad.volume", amount=0.3, rate=2.0)
        mm.connect("random", "lead.pan", amount=0.2)

        # Sidechain pump via envelope follower
        mm.connect_env_follower("pad.volume", kick_audio, amount=-0.8)
    """

    def __init__(self) -> None:
        self._routes: list[_ModRoute] = []
        self._env_followers: list[dict] = []

    def connect(
        self, source: str, dest: str, amount: float = 0.5, rate: float = 1.0
    ) -> "ModMatrix":
        """Add a modulation route.

        Args:
            source: Modulation source ('lfo1', 'lfo2', 'random', 'envelope').
            dest:   Destination parameter ('<track>.<param>').
            amount: Modulation depth (-1.0 to 1.0).
            rate:   Rate in Hz (for LFO sources).
        """
        self._routes.append(_ModRoute(source, dest, amount, rate))
        return self

    def connect_env_follower(
        self,
        dest: str,
        sidechain_audio: FloatArray,
        amount: float = -0.8,
        attack_ms: float = 5.0,
        release_ms: float = 100.0,
    ) -> "ModMatrix":
        """Connect an envelope follower as a modulation source.

        Shorthand for sidechain pumping. The envelope of sidechain_audio
        modulates the destination parameter.

        Args:
            dest:            Destination parameter ('<track>.<param>').
            sidechain_audio: Audio to extract envelope from (e.g. kick).
            amount:          Modulation depth. Negative = ducking (default).
            attack_ms:       Envelope attack time.
            release_ms:      Envelope release time.
        """
        self._env_followers.append(
            {
                "dest": dest,
                "audio": sidechain_audio,
                "amount": amount,
                "attack_ms": attack_ms,
                "release_ms": release_ms,
            }
        )
        return self

    def generate_mod_signal(
        self, source: str, n: int, sr: int, rate: float = 1.0, seed: int | None = None
    ) -> FloatArray:
        """Generate a modulation signal for a given source type.

        Returns:
            Float64 array of shape (n,) with values in [-1, 1].
        """
        t = np.arange(n) / sr
        if source.startswith("lfo"):
            return np.sin(2 * np.pi * rate * t)
        elif source == "random":
            rng = np.random.default_rng(seed)
            # Smoothed random (low-pass filtered noise)
            raw = rng.standard_normal(n)
            # Simple moving average for smoothing
            kernel_size = max(1, int(sr / (rate * 10)))
            kernel = np.ones(kernel_size) / kernel_size
            smoothed = np.convolve(raw, kernel, mode="same")
            peak = np.max(np.abs(smoothed))
            return smoothed / peak if peak > 0 else smoothed
        elif source == "envelope":
            # Simple attack-release envelope
            attack = int(0.1 * sr)
            release = int(0.3 * sr)
            env = np.ones(n)
            if attack > 0:
                env[:attack] = np.linspace(0, 1, attack)
            if release > 0 and n > release:
                env[-release:] = np.linspace(1, 0, release)
            return env
        else:
            return np.zeros(n)

    def generate_env_follower_signals(self, n: int, sr: int) -> list[tuple[str, float, FloatArray]]:
        """Generate envelope follower modulation signals.

        Returns:
            List of (dest, amount, envelope_signal) tuples.
        """
        results = []
        for ef in self._env_followers:
            follower = EnvFollower(
                attack_ms=ef["attack_ms"],
                release_ms=ef["release_ms"],
            )
            audio = ef["audio"]
            # Truncate or pad sidechain audio to match target length
            if len(audio) < n:
                audio = np.pad(audio, ((0, n - len(audio)),) + ((0, 0),) * (audio.ndim - 1))
            env = follower.follow(audio[:n], sr)
            results.append((ef["dest"], ef["amount"], env))
        return results

    @property
    def routes(self) -> list[dict]:
        """List all routes as dicts."""
        return [
            {"source": r.source, "dest": r.dest, "amount": r.amount, "rate": r.rate}
            for r in self._routes
        ]

    @property
    def env_follower_count(self) -> int:
        """Number of envelope follower connections."""
        return len(self._env_followers)

    def __repr__(self) -> str:
        total = len(self._routes) + len(self._env_followers)
        return f"ModMatrix({total} routes)"

    def __len__(self) -> int:
        return len(self._routes) + len(self._env_followers)


# ---------------------------------------------------------------------------
# Song composition utilities (v12.0 Phase 1)
# ---------------------------------------------------------------------------


def song_overlay(base, other, at_beat: float = 0.0):
    """Overlay another song's tracks onto base at a specific beat offset.

    Args:
        base:    The target Song.
        other:   The Song whose tracks to add.
        at_beat: Beat position where other's tracks start.

    Returns:
        The base Song (modified in place).
    """
    from .engine import Note, Track

    for track in other.tracks:
        # Clone track with offset
        new_name = track.name
        existing_names = {t.name for t in base.tracks}
        if new_name in existing_names:
            new_name = f"{track.name}_2"

        new_track = Track(
            name=new_name,
            instrument=track.instrument,
            volume=track.volume,
            pan=track.pan,
        )

        # Add rest for offset
        if at_beat > 0:
            new_track.add(Note.rest(at_beat))

        # Copy events
        for beat in track.beats:
            new_track.beats.append(beat)

        base.add_track(new_track)

    return base


def song_append(first, second):
    """Concatenate two songs end-to-end.

    The second song's tracks are appended after the first song's tracks end.
    Uses the first song's BPM and sample rate.

    Args:
        first:  First Song.
        second: Second Song.

    Returns:
        A new Song containing both.
    """
    from .engine import Song, Track

    combined = Song(
        title=f"{first.title} + {second.title}",
        bpm=first.bpm,
        sample_rate=first.sample_rate,
    )

    # Calculate first song's total duration in beats
    first_duration = 0.0
    for track in first.tracks:
        track_dur = sum(b.event.duration if b.event else 0 for b in track.beats)
        first_duration = max(first_duration, track_dur)

    # Add first song's tracks
    for track in first.tracks:
        new_track = Track(
            name=track.name,
            instrument=track.instrument,
            volume=track.volume,
            pan=track.pan,
        )
        for beat in track.beats:
            new_track.beats.append(beat)
        combined.add_track(new_track)

    # Add second song's tracks with offset
    from .engine import Note

    for track in second.tracks:
        new_name = track.name
        existing = {t.name for t in combined.tracks}
        if new_name in existing:
            # Find matching track and append
            for ct in combined.tracks:
                if ct.name == new_name:
                    for beat in track.beats:
                        ct.beats.append(beat)
                    break
        else:
            new_track = Track(
                name=new_name,
                instrument=track.instrument,
                volume=track.volume,
                pan=track.pan,
            )
            # Pad with silence to align
            if first_duration > 0:
                new_track.add(Note.rest(first_duration))
            for beat in track.beats:
                new_track.beats.append(beat)
            combined.add_track(new_track)

    return combined


def song_extract(song, track_names: list[str]):
    """Extract specific tracks into a new Song.

    Args:
        song:        Source Song.
        track_names: List of track names to extract.

    Returns:
        A new Song containing only the specified tracks.
    """
    from .engine import Song, Track

    extracted = Song(
        title=f"{song.title} (extract)",
        bpm=song.bpm,
        sample_rate=song.sample_rate,
    )

    for track in song.tracks:
        if track.name in track_names:
            new_track = Track(
                name=track.name,
                instrument=track.instrument,
                volume=track.volume,
                pan=track.pan,
            )
            for beat in track.beats:
                new_track.beats.append(beat)
            extracted.add_track(new_track)

    # Copy relevant effects
    if hasattr(song, "effects") and song.effects:
        extracted.effects = {name: fx for name, fx in song.effects.items() if name in track_names}

    return extracted
