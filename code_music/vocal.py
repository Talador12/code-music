"""Vocal synthesis and TTS integration for code-music.

Provides VocalTrack for adding sung/spoken vocals to songs, with pluggable
TTS backends. All backends are optional - install only what you need.

Architecture:
    VocalTrack holds a list of VocalEvents (text + timing + style).
    At render time, each event is sent to the configured TTSBackend,
    which returns audio. The audio is placed at the correct beat position
    and mixed into the song.

Backends:
    - SystemTTS: macOS `say` / Linux `espeak` (free, low quality)
    - BarkTTS: suno/bark model (free, GPU recommended, pip install bark)
    - CoquiTTS: coqui-ai TTS (free, pip install TTS)
    - ElevenLabsTTS: cloud API (paid, high quality, pip install elevenlabs)
    - FormantVocal: built-in formant synthesis (no words, just vowel textures)

None of these are required dependencies. The library works without any
TTS backend installed. VocalTrack gracefully falls back to formant
synthesis or silence when no backend is available.

Example::

    from code_music import Song, VocalTrack

    song = Song(title="Demo", bpm=120)
    vt = song.add_vocal_track(VocalTrack(name="vocals"))

    # Add vocal events with text and timing
    vt.say("hello world", at_beat=0, duration_beats=2)
    vt.say("this is code music", at_beat=4, duration_beats=4)

    # Configure a backend (optional - defaults to formant fallback)
    vt.set_backend("system")  # or "bark", "coqui", "elevenlabs"
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np

# ---------------------------------------------------------------------------
# Vocal event: one chunk of text at a specific beat position
# ---------------------------------------------------------------------------


@dataclass
class VocalEvent:
    """A single vocal event: text placed at a beat position.

    Attributes:
        text:           Words to speak/sing.
        at_beat:        Beat position in the song.
        duration_beats: How many beats this vocal spans.
        style:          Style hint for the backend (e.g. "whisper", "shout", "sing").
        pitch_shift:    Semitones to shift the rendered vocal (+/- 12 = octave).
        speed:          Playback speed multiplier (0.5 = half speed, 2.0 = double).
    """

    text: str = ""
    at_beat: float = 0.0
    duration_beats: float = 2.0
    style: str = "normal"
    pitch_shift: float = 0.0
    speed: float = 1.0


# ---------------------------------------------------------------------------
# TTS Backend protocol
# ---------------------------------------------------------------------------


class TTSBackend(Protocol):
    """Protocol for TTS backends. Implement synthesize() to add a new one."""

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        """Render text to mono audio.

        Args:
            text:        Text to speak/sing.
            sample_rate: Target sample rate.
            style:       Style hint.

        Returns:
            Mono float64 audio array.
        """
        ...

    @property
    def name(self) -> str:
        """Backend display name."""
        ...

    @property
    def available(self) -> bool:
        """Whether the backend's dependencies are installed."""
        ...


# ---------------------------------------------------------------------------
# Built-in backends
# ---------------------------------------------------------------------------


class FormantVocal:
    """Fallback: formant synthesis (no words, vowel textures).

    Always available. Renders the text length as a sustained vowel tone.
    Useful as a placeholder or for ethereal vocal textures.
    """

    name = "formant"
    available = True

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        from .sound_design import SoundDesigner

        # Map style to vowel
        vowel_map = {
            "normal": "ah",
            "whisper": "eh",
            "shout": "ah",
            "sing": "oh",
            "ethereal": "oo",
        }
        vowel = vowel_map.get(style, "ah")
        breathiness = 0.7 if style == "whisper" else 0.2

        sd = (
            SoundDesigner("vocal_fallback")
            .formant(vowel, breathiness=breathiness, vibrato_depth=0.02, volume=0.8)
            .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3)
        )

        # Duration based on text length (rough: 0.15s per character)
        duration = max(0.3, len(text) * 0.15)
        return sd.render(220.0, duration, sample_rate)


class SystemTTS:
    """macOS `say` or Linux `espeak` text-to-speech.

    Low quality but free and requires no pip install. Renders to a temp WAV
    and reads it back. Available on macOS (say) and Linux (espeak/espeak-ng).
    """

    name = "system"

    @property
    def available(self) -> bool:
        import platform
        import shutil

        if platform.system() == "Darwin":
            return shutil.which("say") is not None
        return shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        import platform
        import wave

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        try:
            if platform.system() == "Darwin":
                # macOS say command
                rate_map = {"normal": "175", "whisper": "130", "shout": "220", "sing": "150"}
                rate = rate_map.get(style, "175")
                subprocess.run(
                    ["say", "-r", rate, "-o", tmp_path, "--data-format=LEI16@44100", text],
                    capture_output=True,
                    timeout=30,
                )
            else:
                # Linux espeak
                cmd = "espeak-ng" if __import__("shutil").which("espeak-ng") else "espeak"
                speed_map = {"normal": "150", "whisper": "120", "shout": "200", "sing": "130"}
                speed = speed_map.get(style, "150")
                subprocess.run(
                    [cmd, "-s", speed, "-w", tmp_path, text],
                    capture_output=True,
                    timeout=30,
                )

            # Read the WAV back
            if not Path(tmp_path).exists() or Path(tmp_path).stat().st_size < 44:
                return np.zeros(sample_rate)

            with wave.open(tmp_path, "r") as wf:
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
                wav_sr = wf.getframerate()

            # Resample if needed
            if wav_sr != sample_rate:
                target_len = int(len(audio) * sample_rate / wav_sr)
                audio = np.interp(
                    np.linspace(0, len(audio) - 1, target_len),
                    np.arange(len(audio)),
                    audio,
                )

            return audio

        except Exception:
            return np.zeros(sample_rate)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class BarkTTS:
    """Suno Bark neural TTS (pip install bark). GPU recommended.

    High quality, multiple voices, can do music/singing. Large model.
    """

    name = "bark"

    @property
    def available(self) -> bool:
        try:
            import bark  # noqa: F401

            return True
        except ImportError:
            return False

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models

            preload_models()
            audio = generate_audio(text)
            # Resample to target rate
            if SAMPLE_RATE != sample_rate:
                target_len = int(len(audio) * sample_rate / SAMPLE_RATE)
                audio = np.interp(
                    np.linspace(0, len(audio) - 1, target_len),
                    np.arange(len(audio)),
                    audio,
                ).astype(np.float64)
            return audio
        except Exception:
            return FormantVocal().synthesize(text, sample_rate, style)


class CoquiTTS:
    """Coqui TTS (pip install TTS). Local neural TTS with many voices."""

    name = "coqui"

    @property
    def available(self) -> bool:
        try:
            import TTS  # noqa: F401

            return True
        except ImportError:
            return False

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        try:
            from TTS.api import TTS as CoquiAPI

            tts = CoquiAPI(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tts.tts_to_file(text=text, file_path=f.name)
                import wave

                with wave.open(f.name, "r") as wf:
                    frames = wf.readframes(wf.getnframes())
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
                    wav_sr = wf.getframerate()
                Path(f.name).unlink(missing_ok=True)

            if wav_sr != sample_rate:
                target_len = int(len(audio) * sample_rate / wav_sr)
                audio = np.interp(
                    np.linspace(0, len(audio) - 1, target_len),
                    np.arange(len(audio)),
                    audio,
                )
            return audio
        except Exception:
            return FormantVocal().synthesize(text, sample_rate, style)


class ElevenLabsTTS:
    """ElevenLabs cloud TTS (pip install elevenlabs). Paid API, highest quality.

    Set ELEVENLABS_API_KEY environment variable before use.
    """

    name = "elevenlabs"

    @property
    def available(self) -> bool:
        try:
            import os

            import elevenlabs  # noqa: F401

            return bool(os.environ.get("ELEVENLABS_API_KEY"))
        except ImportError:
            return False

    def synthesize(self, text: str, sample_rate: int, style: str = "normal") -> np.ndarray:
        try:
            import os

            from elevenlabs import generate, set_api_key

            set_api_key(os.environ["ELEVENLABS_API_KEY"])

            voice_map = {
                "normal": "Rachel",
                "whisper": "Domi",
                "shout": "Josh",
                "sing": "Bella",
            }
            voice = voice_map.get(style, "Rachel")

            audio_bytes = generate(text=text, voice=voice, model="eleven_monolingual_v1")

            # Decode MP3 bytes to numpy
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                tmp = f.name

            try:
                from pydub import AudioSegment

                seg = AudioSegment.from_mp3(tmp)
                raw = np.array(seg.get_array_of_samples(), dtype=np.float64)
                raw /= 32768.0
                if seg.channels == 2:
                    raw = raw.reshape(-1, 2).mean(axis=1)
                if seg.frame_rate != sample_rate:
                    target_len = int(len(raw) * sample_rate / seg.frame_rate)
                    raw = np.interp(
                        np.linspace(0, len(raw) - 1, target_len),
                        np.arange(len(raw)),
                        raw,
                    )
                return raw
            finally:
                Path(tmp).unlink(missing_ok=True)

        except Exception:
            return FormantVocal().synthesize(text, sample_rate, style)


# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

_BACKENDS: dict[str, TTSBackend] = {
    "formant": FormantVocal(),
    "system": SystemTTS(),
    "bark": BarkTTS(),
    "coqui": CoquiTTS(),
    "elevenlabs": ElevenLabsTTS(),
}


def list_tts_backends() -> list[dict]:
    """List all TTS backends with availability status.

    Returns:
        List of dicts with name and available keys.
    """
    return [{"name": b.name, "available": b.available} for b in _BACKENDS.values()]


def register_tts_backend(name: str, backend: TTSBackend) -> None:
    """Register a custom TTS backend.

    Args:
        name:    Backend name.
        backend: Object implementing TTSBackend protocol.
    """
    _BACKENDS[name] = backend


# ---------------------------------------------------------------------------
# VocalTrack
# ---------------------------------------------------------------------------


@dataclass
class VocalTrack:
    """A track of vocal events with TTS backend integration.

    Add text at specific beat positions, then render() produces the mixed
    audio. Falls back to formant synthesis if no TTS backend is available.

    Attributes:
        name:       Track name.
        volume:     Track volume (0.0-1.0).
        pan:        Stereo pan (-1.0 to 1.0).
        backend:    TTS backend name ('formant', 'system', 'bark', etc).
        events:     List of VocalEvents.

    Example::

        vt = VocalTrack(name="vocals")
        vt.say("hello world", at_beat=0, duration_beats=2)
        vt.say("code music", at_beat=4, duration_beats=2, style="sing")
        audio = vt.render(bpm=120, sample_rate=44100)
    """

    name: str = "vocals"
    volume: float = 0.8
    pan: float = 0.0
    backend: str = "formant"
    events: list[VocalEvent] = field(default_factory=list)

    def say(
        self,
        text: str,
        at_beat: float = 0.0,
        duration_beats: float = 2.0,
        style: str = "normal",
        pitch_shift: float = 0.0,
        speed: float = 1.0,
    ) -> "VocalTrack":
        """Add a vocal event.

        Args:
            text:           Words to speak/sing.
            at_beat:        Beat position.
            duration_beats: Duration in beats.
            style:          Style: normal, whisper, shout, sing, ethereal.
            pitch_shift:    Semitones to shift.
            speed:          Speed multiplier.
        """
        self.events.append(
            VocalEvent(
                text=text,
                at_beat=at_beat,
                duration_beats=duration_beats,
                style=style,
                pitch_shift=pitch_shift,
                speed=speed,
            )
        )
        return self

    def set_backend(self, name: str) -> "VocalTrack":
        """Set the TTS backend by name.

        Args:
            name: Backend name (formant, system, bark, coqui, elevenlabs).
        """
        if name not in _BACKENDS:
            raise ValueError(f"Unknown backend {name!r}. Available: {sorted(_BACKENDS.keys())}")
        self.backend = name
        return self

    def render(self, bpm: float, sample_rate: int) -> np.ndarray:
        """Render all vocal events to a mono audio array.

        Args:
            bpm:         Song tempo.
            sample_rate: Sample rate.

        Returns:
            Mono float64 audio.
        """
        if not self.events:
            return np.zeros(sample_rate)

        beat_dur = 60.0 / bpm

        # Calculate total length needed
        max_end = max((e.at_beat + e.duration_beats) * beat_dur for e in self.events)
        n = int(max_end * sample_rate) + sample_rate  # extra second buffer

        out = np.zeros(n, dtype=np.float64)

        # Get the backend
        be = _BACKENDS.get(self.backend)
        if be is None or not be.available:
            be = _BACKENDS["formant"]

        for event in self.events:
            # Synthesize the text
            audio = be.synthesize(event.text, sample_rate, event.style)

            # Apply speed
            if abs(event.speed - 1.0) > 0.01:
                target_len = int(len(audio) / event.speed)
                if target_len > 0:
                    audio = np.interp(
                        np.linspace(0, len(audio) - 1, target_len),
                        np.arange(len(audio)),
                        audio,
                    )

            # Apply pitch shift
            if abs(event.pitch_shift) > 0.1:
                from .effects import pitch_shift

                audio = pitch_shift(audio, sample_rate, semitones=event.pitch_shift)

            # Trim or pad to fit duration_beats
            target_samples = int(event.duration_beats * beat_dur * sample_rate)
            if len(audio) > target_samples:
                # Fade out last 10%
                fade_len = max(1, target_samples // 10)
                audio = audio[:target_samples]
                audio[-fade_len:] *= np.linspace(1, 0, fade_len)
            elif len(audio) < target_samples:
                audio = np.pad(audio, (0, target_samples - len(audio)))

            # Place at beat position
            start_sample = int(event.at_beat * beat_dur * sample_rate)
            end_sample = start_sample + len(audio)
            if end_sample <= n:
                out[start_sample:end_sample] += audio * self.volume

        return out

    def __len__(self) -> int:
        return len(self.events)

    def __repr__(self) -> str:
        return f"VocalTrack({self.name!r}, {len(self.events)} events, backend={self.backend!r})"
