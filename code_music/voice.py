"""Voice synthesis backends: say (macOS), Bark, ElevenLabs, OpenAI TTS.

VoiceClip — the core primitive — generates a stereo float64 numpy array from
a text prompt + voice spec. The backend is selected automatically based on
what's available, or can be forced explicitly.

Usage in a song::

    from code_music.voice import VoiceClip, VoiceTrack

    vc = VoiceClip("♪ la la la ♪", voice="Cellos", backend="say")
    track = VoiceTrack(name="vox", clips=[(vc, beat_offset=4.0)])
    song.add_voice_track(track)

Available backends (checked in order if backend="auto"):
    say       macOS built-in — 184 voices, musical novelty ones, zero cost
    bark      Suno Bark — AI text-to-audio, MIT, needs transformers + torch
    elevenlabs ElevenLabs API — high quality, needs ELEVENLABS_API_KEY env var
    openai    OpenAI TTS API — natural voices, needs OPENAI_API_KEY env var
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

Backend = Literal["auto", "say", "bark", "elevenlabs", "openai"]

# macOS say voices — musical / character ones worth highlighting
SAY_MUSICAL_VOICES = [
    "Cellos",
    "Organ",
    "Bells",
    "Bubbles",
    "Zarvox",
    "Trinoids",
    "Whisper",
    "Wobble",
    "Boing",
    "Jester",
    "Junior",
    "Bahh",
    "Bad News",
    "Good News",
    "Superstar",
    "Albert",
    "Ralph",
    "Fred",
    "Kathy",
    "Samantha",
    "Daniel",
]

# Bark speaker presets (subset — full list at https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683)
BARK_VOICES = {
    "narrator": "v2/en_speaker_6",
    "male_1": "v2/en_speaker_1",
    "male_2": "v2/en_speaker_3",
    "female_1": "v2/en_speaker_9",
    "female_2": "v2/en_speaker_0",
    "old_man": "v2/en_speaker_5",
    "announcer": "v2/en_speaker_7",
    "storyteller": "v2/en_speaker_8",
}

# OpenAI TTS voices
OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# ElevenLabs default voice IDs (stable cross-account)
ELEVENLABS_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam": "pNInz6obpgDQGcFmaJgB",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "arnold": "VR6AewLTigWG4xSOukaG",
    "josh": "TxGEqnHWrfWFTfGW9XjX",
    "dorothy": "ThT5KcBeYPX3keUQqHPh",
    "thomas": "GBv7mTt0atIp3Br8iCZE",
}


# ---------------------------------------------------------------------------
# Auto-detect available backends
# ---------------------------------------------------------------------------


def detect_backends() -> list[str]:
    """Return list of available backends in preference order."""
    available = []
    # say — macOS only
    if shutil.which("say") and shutil.which("afconvert"):
        available.append("say")
    # Bark — needs transformers + torch
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401

        available.append("bark")
    except ImportError:
        pass
    # ElevenLabs
    if os.environ.get("ELEVENLABS_API_KEY"):
        available.append("elevenlabs")
    # OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        available.append("openai")
    return available


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------


@dataclass
class VoiceClip:
    """A single voice/speech/singing clip to be placed in a Song.

    Args:
        text:       Text to speak/sing. Bark supports [laughs], ♪ lyrics ♪.
        voice:      Voice name/preset (backend-specific).
                    For say: e.g. "Cellos", "Zarvox", "Samantha"
                    For bark: e.g. "narrator", "female_1", or a v2/en_speaker_N preset
                    For elevenlabs: e.g. "rachel", "adam", or a raw voice ID
                    For openai: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        backend:    "auto" | "say" | "bark" | "elevenlabs" | "openai"
        rate:       Speaking rate as % (say backend only). 100=normal, 50=slow, 200=fast.
        pitch:      Pitch shift semitones after generation (all backends, via resampling).
        volume:     0.0–1.0 gain applied to this clip.
        pan:        Stereo position -1.0 (L) to 1.0 (R).
    """

    text: str
    voice: str = "Samantha"
    backend: Backend = "auto"
    rate: int = 100  # say rate %
    pitch: float = 0.0  # semitones, applied post-generation
    volume: float = 0.8
    pan: float = 0.0


@dataclass
class VoiceTrack:
    """A sequence of (VoiceClip, beat_offset) pairs added to a Song.

    Args:
        name:        Track label (used in mix display).
        clips:       List of (VoiceClip, beat_offset_in_beats) tuples.
        sample_rate: Render sample rate — set automatically by Song.
    """

    name: str = "voice"
    clips: list[tuple[VoiceClip, float]] = field(default_factory=list)
    sample_rate: int = 44100

    def add(self, clip: VoiceClip, beat_offset: float = 0.0) -> "VoiceTrack":
        self.clips.append((clip, beat_offset))
        return self


# ---------------------------------------------------------------------------
# Lyrics helper — write lyrics as text, auto-place on beats
# ---------------------------------------------------------------------------


@dataclass
class Lyrics:
    """Lyrics with beat-aligned lines for voice synthesis.

    Write lyrics as a list of (beat_offset, text) tuples, or use
    ``from_text()`` to auto-space lines evenly across a bar range.

    Example (manual placement)::

        lyrics = Lyrics([
            (0.0,  "hello world"),
            (4.0,  "this is code music"),
            (8.0,  "every note is a function"),
            (12.0, "every song is a program"),
        ])

    Example (auto-spaced)::

        lyrics = Lyrics.from_text('''
            hello world
            this is code music
            every note is a function
            every song is a program
        ''', start_beat=0.0, beats_per_line=4.0)

    Then convert to a VoiceTrack::

        vox = lyrics.to_voice_track(voice="Samantha", backend="say")
        song.add_voice_track(vox)
    """

    lines: list[tuple[float, str]] = field(default_factory=list)

    @classmethod
    def from_text(
        cls,
        text: str,
        start_beat: float = 0.0,
        beats_per_line: float = 4.0,
    ) -> "Lyrics":
        """Create lyrics from a multi-line string, auto-spaced.

        Each non-empty line becomes one voice clip, placed ``beats_per_line``
        beats apart starting at ``start_beat``.

        Args:
            text:           Multi-line lyrics string (one line per phrase).
            start_beat:     Beat offset for the first line.
            beats_per_line: Beats between each line (default 4.0 = one bar at 4/4).
        """
        raw_lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        return cls([(start_beat + i * beats_per_line, line) for i, line in enumerate(raw_lines)])

    def to_voice_track(
        self,
        name: str = "vocals",
        voice: str = "Samantha",
        backend: Backend = "auto",
        rate: int = 100,
        volume: float = 0.8,
        pan: float = 0.0,
    ) -> VoiceTrack:
        """Convert lyrics to a VoiceTrack ready to add to a Song.

        Each line becomes a VoiceClip placed at its beat offset.

        Args:
            name:    Track name.
            voice:   Voice preset (backend-specific).
            backend: Voice backend ("auto", "say", "bark", etc.)
            rate:    Speaking rate (say backend, percentage).
            volume:  Clip volume 0.0–1.0.
            pan:     Stereo position -1.0 to 1.0.

        Returns:
            VoiceTrack ready for ``song.add_voice_track()``.
        """
        track = VoiceTrack(name=name)
        for beat, text in self.lines:
            clip = VoiceClip(
                text=text,
                voice=voice,
                backend=backend,
                rate=rate,
                volume=volume,
                pan=pan,
            )
            track.add(clip, beat_offset=beat)
        return track


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------


def _samples_from_wav_bytes(data: bytes) -> tuple[FloatArray, int]:
    """Read raw WAV bytes → (float64 stereo array, sample_rate)."""
    with wave.open(io.BytesIO(data)) as wf:
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        n_ch = wf.getnchannels()
        raw = wf.readframes(n_frames)
    dtype = np.int16
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float64) / 32768.0
    if n_ch == 1:
        samples = np.column_stack([samples, samples])
    elif n_ch == 2:
        samples = samples.reshape(-1, 2)
    return samples, sr


def _resample(samples: FloatArray, src_sr: int, dst_sr: int) -> FloatArray:
    """Resample stereo array from src_sr to dst_sr using scipy."""
    if src_sr == dst_sr:
        return samples
    from scipy import signal as sig

    n_out = int(len(samples) * dst_sr / src_sr)
    left = sig.resample(samples[:, 0], n_out)
    right = sig.resample(samples[:, 1], n_out)
    return np.column_stack([left, right]).astype(np.float64)


def _pitch_shift(samples: FloatArray, semitones: float, sr: int) -> FloatArray:
    """Crude pitch shift via resampling (no formant preservation)."""
    if semitones == 0.0:
        return samples
    ratio = 2 ** (semitones / 12.0)
    # Speed up/slow down by ratio, then resample back to original length
    from scipy import signal as sig

    n_out = int(len(samples) / ratio)
    left = sig.resample(samples[:, 0], n_out)
    right = sig.resample(samples[:, 1], n_out)
    shortened = np.column_stack([left, right]).astype(np.float64)
    # Resample back to original duration
    return _resample(shortened, sr, sr)


def _apply_pan(samples: FloatArray, pan: float) -> FloatArray:
    """Equal-power stereo pan."""
    import math

    angle = (pan + 1) / 2 * math.pi / 2
    result = samples.copy()
    result[:, 0] *= math.cos(angle)
    result[:, 1] *= math.sin(angle)
    return result


# ── say backend (macOS) ────────────────────────────────────────────────────


def _generate_say(clip: VoiceClip, target_sr: int) -> FloatArray:
    """Generate voice audio via macOS `say` → AIFF → WAV → numpy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        aiff_path = Path(tmpdir) / "voice.aiff"
        wav_path = Path(tmpdir) / "voice.wav"

        # Build say command
        cmd = [
            "say",
            "-v",
            clip.voice,
            "--rate",
            str(clip.rate),
            "-o",
            str(aiff_path),
            clip.text,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"say failed: {result.stderr.decode()}")
        if not aiff_path.exists() or aiff_path.stat().st_size < 100:
            raise RuntimeError(f"say produced no output for voice={clip.voice!r}")

        # Convert AIFF → WAV via afconvert (always available on macOS)
        subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16@44100", str(aiff_path), str(wav_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )

        samples, sr = _samples_from_wav_bytes(wav_path.read_bytes())

    samples = _resample(samples, sr, target_sr)
    return samples


# ── Bark backend ───────────────────────────────────────────────────────────


def _generate_bark(clip: VoiceClip, target_sr: int) -> FloatArray:
    """Generate audio via Suno Bark (transformers pipeline).

    Supports ♪ singing lyrics ♪, [laughs], [sighs], etc.
    Bark outputs at 24000 Hz — we resample to target_sr.
    """
    try:
        import torch
        from transformers import AutoProcessor, BarkModel
    except ImportError as e:
        raise ImportError("Bark requires: pip install transformers torch") from e

    # Map friendly voice names to Bark presets
    preset = BARK_VOICES.get(clip.voice, clip.voice)

    processor = AutoProcessor.from_pretrained("suno/bark-small")
    model = BarkModel.from_pretrained("suno/bark-small")
    if torch.cuda.is_available():
        model = model.cuda()

    inputs = processor(clip.text, voice_preset=preset)
    with torch.no_grad():
        audio_array = model.generate(**inputs)

    audio = audio_array.cpu().numpy().squeeze().astype(np.float64)
    bark_sr = model.generation_config.sample_rate  # 24000

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak

    # Mono → stereo
    stereo = np.column_stack([audio, audio])
    return _resample(stereo, bark_sr, target_sr)


# ── ElevenLabs backend ─────────────────────────────────────────────────────


def _generate_elevenlabs(clip: VoiceClip, target_sr: int) -> FloatArray:
    """Generate via ElevenLabs REST API. Needs ELEVENLABS_API_KEY env var."""
    import json
    import urllib.request

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY env var not set")

    voice_id = ELEVENLABS_VOICES.get(clip.voice, clip.voice)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = json.dumps(
        {
            "text": clip.text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
    ).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        mp3_bytes = resp.read()

    # Decode MP3 via pydub
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError("ElevenLabs backend requires pydub: pip install pydub") from e

    seg = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
    seg = seg.set_frame_rate(target_sr).set_channels(2).set_sample_width(2)
    raw = np.frombuffer(seg.raw_data, dtype=np.int16).astype(np.float64) / 32768.0
    stereo = raw.reshape(-1, 2)
    return stereo


# ── OpenAI TTS backend ─────────────────────────────────────────────────────


def _generate_openai(clip: VoiceClip, target_sr: int) -> FloatArray:
    """Generate via OpenAI TTS API. Needs OPENAI_API_KEY env var."""
    import json
    import urllib.request

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var not set")

    voice = clip.voice if clip.voice in OPENAI_VOICES else "alloy"
    payload = json.dumps(
        {
            "model": "tts-1-hd",
            "input": clip.text,
            "voice": voice,
            "response_format": "wav",
        }
    ).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        wav_bytes = resp.read()

    samples, sr = _samples_from_wav_bytes(wav_bytes)
    return _resample(samples, sr, target_sr)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(clip: VoiceClip, sample_rate: int = 44100) -> FloatArray:
    """Generate a VoiceClip to a stereo float64 array.

    Args:
        clip:        VoiceClip spec.
        sample_rate: Target sample rate.

    Returns:
        Stereo float64 numpy array, shape (N, 2), range [-1, 1].
    """
    backend = clip.backend
    if backend == "auto":
        available = detect_backends()
        if not available:
            raise RuntimeError(
                "No voice backends available. "
                "On macOS: install Xcode CLT. "
                "Or: pip install transformers torch (Bark), "
                "or set ELEVENLABS_API_KEY / OPENAI_API_KEY."
            )
        backend = available[0]

    if backend == "say":
        samples = _generate_say(clip, sample_rate)
    elif backend == "bark":
        samples = _generate_bark(clip, sample_rate)
    elif backend == "elevenlabs":
        samples = _generate_elevenlabs(clip, sample_rate)
    elif backend == "openai":
        samples = _generate_openai(clip, sample_rate)
    else:
        raise ValueError(f"Unknown backend: {backend!r}")

    # Post-processing: pitch shift, pan, volume
    if clip.pitch != 0.0:
        samples = _pitch_shift(samples, clip.pitch, sample_rate)
    samples = _apply_pan(samples, clip.pan)
    samples *= clip.volume

    return np.clip(samples, -1.0, 1.0).astype(np.float64)


def render_voice_track(
    track: VoiceTrack,
    bpm: float,
    total_beats: float,
    sample_rate: int = 44100,
) -> FloatArray:
    """Render a VoiceTrack to a stereo array aligned to the song timeline.

    Args:
        track:       VoiceTrack with clips and beat offsets.
        bpm:         Song BPM (for beat → sample conversion).
        total_beats: Total song length in beats.
        sample_rate: Target sample rate.

    Returns:
        Stereo float64 array covering the full song duration.
    """
    beat_sec = 60.0 / bpm
    total_samples = int(total_beats * beat_sec * sample_rate) + sample_rate

    mix = np.zeros((total_samples, 2))

    for clip, beat_offset in track.clips:
        try:
            audio = generate(clip, sample_rate)
        except Exception as e:
            print(f"[voice] WARNING: clip generation failed ({e}), skipping")
            continue

        start_sample = int(beat_offset * beat_sec * sample_rate)
        end_sample = min(start_sample + len(audio), total_samples)
        clip_len = end_sample - start_sample
        if clip_len > 0:
            mix[start_sample:end_sample] += audio[:clip_len]

    return np.clip(mix, -1.0, 1.0).astype(np.float64)


def list_voices(backend: str = "say") -> list[str]:
    """Return available voices for a backend.

    Args:
        backend: "say" | "bark" | "elevenlabs" | "openai"
    """
    if backend == "say":
        result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
        voices = []
        for line in result.stdout.splitlines():
            if line.strip():
                name = line.split()[0] if "(" not in line else line.split("(")[0].strip()
                voices.append(name)
        return voices
    elif backend == "bark":
        return list(BARK_VOICES.keys())
    elif backend == "elevenlabs":
        return list(ELEVENLABS_VOICES.keys())
    elif backend == "openai":
        return OPENAI_VOICES
    return []
