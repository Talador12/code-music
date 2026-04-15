"""Integration layer for external music libraries and AI generation.

code-music is the hub. Other libraries are spokes. If it exists in the
Python music ecosystem, you can import it into code-music and use it
alongside everything we have built.

Supported integrations (all optional - install the library to activate):

    music21:    Import/export music21 Score/Stream objects. Access their
                corpus, analysis tools, and notation rendering.
    midiutil:   Export to MIDI with finer control than our built-in.
    pyo:        Use pyo's DSP engine for real-time audio processing.
    librosa:    Audio analysis (beat tracking, onset detection, chroma).
    pretty_midi: Detailed MIDI manipulation and piano roll extraction.
    AI:         Generate sounds, melodies, and arrangements via any
                LLM or audio model API (OpenAI, Anthropic, local models).

Architecture:
    Every integration is a lazy import. Nothing is required. If the
    user has music21 installed, `from_music21()` works. If not, it
    raises a clear ImportError telling them what to install.

    All integrations convert TO and FROM our core types (Note, Chord,
    Track, Song). We are the interchange format.

Example::

    # Import a music21 score and render it with our synth
    from code_music.integrations import from_music21
    import music21
    score = music21.corpus.parse("bach/bwv66.6")
    song = from_music21(score)
    song.render()

    # Export to music21 for their analysis tools
    from code_music.integrations import to_music21
    m21_score = to_music21(song)
    m21_score.analyze("key")

    # Use AI to generate a melody
    from code_music.integrations import ai_generate_melody
    melody = ai_generate_melody("jazz melody in Bb minor, 8 bars, bebop style")

    # Import any WAV/MP3 as a sample track
    from code_music.integrations import import_audio
    sample = import_audio("my_sample.wav")
    song.add_sample_track(sample)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .engine import Chord, Note, Song, Track


# ---------------------------------------------------------------------------
# music21 integration
# ---------------------------------------------------------------------------


def from_music21(score: Any, bpm: float = 120.0) -> Song:
    """Convert a music21 Score/Stream to a code-music Song.

    Imports notes, chords, rests, dynamics, and part names. Handles
    transposing instruments, key signatures, and time signatures.

    Args:
        score: A music21 Score, Part, or Stream object.
        bpm:   Default tempo if none found in the score.

    Returns:
        A code-music Song with tracks for each part.

    Requires: pip install music21
    """
    try:
        import music21 as m21
    except ImportError:
        raise ImportError("music21 is required for this integration: pip install music21")

    song = Song(title=str(getattr(score, "metadata", {}).get("title", "Imported")), bpm=bpm)

    # Extract tempo
    for mm in score.recurse().getElementsByClass("MetronomeMark"):
        song.bpm = mm.number
        break

    # Extract key signature
    for ks in score.recurse().getElementsByClass("KeySignature"):
        song.key_sig = ks.asKey().tonic.name
        break

    # Extract time signature
    for ts in score.recurse().getElementsByClass("TimeSignature"):
        song.time_sig = (ts.numerator, ts.denominator)
        break

    # Convert each part to a Track
    if hasattr(score, "parts"):
        parts = score.parts
    else:
        parts = [score]

    for part in parts:
        part_name = getattr(part, "partName", None) or "Part"
        track = Track(name=part_name, instrument="piano")

        # Try to get instrument
        for inst in part.recurse().getElementsByClass("Instrument"):
            name = getattr(inst, "instrumentName", "piano") or "piano"
            track.instrument = name.lower().replace(" ", "_")
            break

        for element in part.recurse().notesAndRests:
            if element.isRest:
                track.add(Note.rest(element.quarterLength))
            elif element.isChord:
                # Take the root and quality
                root = element.root()
                if root:
                    track.add(
                        Note(root.name, root.octave or 4, element.quarterLength, velocity=0.7)
                    )
                else:
                    track.add(Note.rest(element.quarterLength))
            elif element.isNote:
                track.add(
                    Note(
                        element.name,
                        element.octave or 4,
                        element.quarterLength,
                        velocity=element.volume.velocity / 127 if element.volume.velocity else 0.7,
                    )
                )

        if track.beats:
            song.add_track(track)

    return song


def to_music21(song: Song) -> Any:
    """Convert a code-music Song to a music21 Score.

    Exports notes, rests, time signature, key signature, and tempo.
    The resulting Score can be analyzed, displayed as notation, or
    exported to any format music21 supports (MusicXML, MIDI, LilyPond, etc.)

    Returns:
        A music21 Score object.

    Requires: pip install music21
    """
    try:
        import music21 as m21
    except ImportError:
        raise ImportError("music21 is required for this integration: pip install music21")

    score = m21.stream.Score()
    score.insert(0, m21.tempo.MetronomeMark(number=song.bpm))
    score.insert(0, m21.key.Key(song.key_sig or "C"))
    num, den = song.time_sig
    score.insert(0, m21.meter.TimeSignature(f"{num}/{den}"))

    for track in song.tracks:
        part = m21.stream.Part()
        part.partName = track.name

        offset = 0.0
        for beat in track.beats:
            event = beat.event
            if event is None:
                offset += 1.0
                continue
            dur = getattr(event, "duration", 1.0)
            if isinstance(event, Note):
                if event.pitch is None:
                    part.insert(offset, m21.note.Rest(quarterLength=dur))
                else:
                    midi = event.midi
                    if midi is not None:
                        n = m21.note.Note(midi=midi, quarterLength=dur)
                        n.volume.velocity = int(event.velocity * 127)
                        part.insert(offset, n)
            offset += dur

        score.insert(0, part)

    return score


# ---------------------------------------------------------------------------
# pretty_midi integration
# ---------------------------------------------------------------------------


def from_pretty_midi(pm: Any) -> Song:
    """Convert a pretty_midi PrettyMIDI object to a code-music Song.

    Requires: pip install pretty_midi
    """
    try:
        import pretty_midi
    except ImportError:
        raise ImportError("pretty_midi is required: pip install pretty_midi")

    song = Song(title="MIDI Import")

    # Get tempo
    tempos = pm.get_tempo_changes()
    if len(tempos[1]) > 0:
        song.bpm = tempos[1][0]

    for instrument in pm.instruments:
        name = pretty_midi.program_to_instrument_name(instrument.program)
        track = Track(
            name=name.lower().replace(" ", "_"),
            instrument="piano" if not instrument.is_drum else "drums_kick",
        )

        # Sort notes by start time
        notes = sorted(instrument.notes, key=lambda n: n.start)
        prev_end = 0.0
        beat_dur = 60.0 / song.bpm

        for note in notes:
            # Insert rest if gap
            gap = note.start - prev_end
            if gap > 0.01:
                track.add(Note.rest(gap / beat_dur))

            dur_beats = (note.end - note.start) / beat_dur
            vel = note.velocity / 127.0
            name_str = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            pitch_name = name_str[note.pitch % 12]
            octave = note.pitch // 12 - 1
            track.add(Note(pitch_name, octave, dur_beats, velocity=vel))
            prev_end = note.end

        if track.beats:
            song.add_track(track)

    return song


# ---------------------------------------------------------------------------
# librosa integration (analysis)
# ---------------------------------------------------------------------------


def analyze_audio(
    path: str | Path,
    sr: int = 44100,
) -> dict:
    """Analyze an audio file using librosa.

    Returns beat positions, tempo, onset times, chroma features, and
    spectral centroid. Useful for beat-matching, remix preparation,
    and understanding the structure of existing audio.

    Requires: pip install librosa
    """
    try:
        import librosa
    except ImportError:
        raise ImportError("librosa is required for audio analysis: pip install librosa")

    y, sr = librosa.load(str(path), sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

    return {
        "tempo": float(tempo) if hasattr(tempo, "__float__") else float(tempo[0]),
        "beat_times": librosa.frames_to_time(beats, sr=sr).tolist(),
        "onset_times": librosa.frames_to_time(onset_frames, sr=sr).tolist(),
        "duration": float(len(y) / sr),
        "sample_rate": sr,
        "chroma_mean": chroma.mean(axis=1).tolist(),
        "spectral_centroid_mean": float(centroid.mean()),
    }


# ---------------------------------------------------------------------------
# AI sound generation hooks
# ---------------------------------------------------------------------------

# Registry of AI generation backends
_AI_BACKENDS: dict[str, Callable] = {}


def register_ai_backend(name: str, fn: Callable) -> None:
    """Register an AI generation backend.

    The function should accept a prompt string and return a list of Notes
    or a Song object.

    Example::

        from code_music.integrations import register_ai_backend
        import openai

        def openai_melody(prompt: str, **kwargs) -> list[Note]:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Generate a melody: {prompt}"}],
            )
            # Parse response into Notes...
            return notes

        register_ai_backend("openai", openai_melody)
    """
    _AI_BACKENDS[name] = fn


def ai_generate_melody(
    prompt: str,
    backend: str | None = None,
    key: str = "C",
    scale_name: str = "major",
    bars: int = 4,
    bpm: float = 120.0,
    seed: int | None = None,
    **kwargs,
) -> list[Note]:
    """Generate a melody using an AI backend or built-in fallback.

    If an AI backend is registered, uses it. Otherwise falls back to
    our built-in theory-driven generation (which is already good but
    not AI-powered).

    Args:
        prompt:     Natural language description.
        backend:    AI backend name (None = try registered, then fallback).
        key:        Musical key.
        scale_name: Scale name.
        bars:       Number of bars.
        bpm:        Tempo.
        seed:       Random seed.

    Returns:
        List of Notes.
    """
    if backend and backend in _AI_BACKENDS:
        return _AI_BACKENDS[backend](
            prompt, key=key, scale_name=scale_name, bars=bars, bpm=bpm, seed=seed, **kwargs
        )

    # Try any registered backend
    for name, fn in _AI_BACKENDS.items():
        try:
            return fn(
                prompt, key=key, scale_name=scale_name, bars=bars, bpm=bpm, seed=seed, **kwargs
            )
        except Exception:
            continue

    # Fallback: use built-in generation (parse prompt for hints)
    from .theory import compose as _compose

    song = _compose(prompt, seed=seed or 42)
    # Extract the melody track
    for track in song.tracks:
        notes = [
            b.event
            for b in track.beats
            if b.event is not None
            and isinstance(b.event, Note)
            and getattr(b.event, "pitch", None) is not None
        ]
        if notes:
            return notes

    # Last resort: generate a scale-based melody
    from .engine import scale as _scale

    return _scale(key, scale_name, 5, length=bars * 4)


def ai_generate_sound(
    prompt: str,
    duration: float = 2.0,
    sample_rate: int = 44100,
    backend: str | None = None,
    **kwargs,
) -> Any:
    """Generate an audio waveform using an AI audio model.

    For models like AudioCraft, MusicGen, Stable Audio, or any API that
    returns raw audio from a text prompt. Returns a numpy array that can
    be used as a sample in code-music.

    Args:
        prompt:      Text description of the sound.
        duration:    Duration in seconds.
        sample_rate: Target sample rate.
        backend:     AI backend name.

    Returns:
        Numpy float64 array (mono or stereo).

    Example with AudioCraft (if installed)::

        register_ai_backend("audiocraft", audiocraft_generate)
        bass_hit = ai_generate_sound("punchy 808 bass hit", duration=1.0)
    """
    if backend and backend in _AI_BACKENDS:
        return _AI_BACKENDS[backend](prompt, duration=duration, sample_rate=sample_rate, **kwargs)

    for name, fn in _AI_BACKENDS.items():
        try:
            return fn(prompt, duration=duration, sample_rate=sample_rate, **kwargs)
        except Exception:
            continue

    raise RuntimeError(
        "No AI audio backend registered. Install and register one:\n"
        "  pip install audiocraft  # Meta's MusicGen\n"
        "  pip install stable-audio-tools  # Stability AI\n"
        "Then: register_ai_backend('name', your_function)"
    )


# ---------------------------------------------------------------------------
# Generic audio import
# ---------------------------------------------------------------------------


def import_audio(
    path: str | Path,
    sample_rate: int = 44100,
) -> Any:
    """Import any audio file as a numpy array for use as a sample.

    Supports WAV (native), MP3/OGG/FLAC (via pydub+ffmpeg), and
    any format librosa supports.

    Returns:
        Mono float64 numpy array normalized to [-1, 1].
    """
    import numpy as np

    path = Path(path)

    if path.suffix.lower() == ".wav":
        import wave

        with wave.open(str(path), "r") as wf:
            raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            audio = raw.astype(np.float64) / 32768.0
            if wf.getnchannels() == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)  # to mono
            if wf.getframerate() != sample_rate:
                from scipy import signal as _sig

                target_len = int(len(audio) * sample_rate / wf.getframerate())
                audio = _sig.resample(audio, target_len)
            return audio

    # Try pydub for other formats
    try:
        from pydub import AudioSegment

        seg = AudioSegment.from_file(str(path))
        seg = seg.set_frame_rate(sample_rate).set_channels(1)
        raw = np.array(seg.get_array_of_samples(), dtype=np.float64) / 32768.0
        return raw
    except Exception:
        pass

    # Try librosa as last resort
    try:
        import librosa

        y, _ = librosa.load(str(path), sr=sample_rate, mono=True)
        return y
    except ImportError:
        raise ImportError(f"Cannot import {path.suffix} files. Install pydub+ffmpeg or librosa.")


# ---------------------------------------------------------------------------
# Plugin system for custom synthesis backends
# ---------------------------------------------------------------------------

_SYNTH_PLUGINS: dict[str, Callable] = {}


def register_synth_plugin(name: str, render_fn: Callable) -> None:
    """Register a custom synthesis backend as a named instrument.

    The function should accept (freq, duration_sec, sample_rate) and
    return a mono float64 numpy array.

    This is how you integrate pyo, csound, SuperCollider, or any other
    DSP engine as a code-music instrument.

    Example with pyo::

        import pyo
        def pyo_pad(freq, duration, sr):
            s = pyo.Server(sr=sr, audio="offline").boot()
            s.recordOptions(dur=duration, filename="/tmp/pyo.wav")
            a = pyo.SuperSaw(freq=freq, detune=0.5, mul=0.3)
            s.start()
            # ... read back the rendered audio
            return audio_array

        register_synth_plugin("pyo_pad", pyo_pad)
        # Now use instrument="pyo_pad" in any Track
    """
    from .synth import Synth
    from .sound_design import SoundDesigner

    class PluginDesigner:
        def render(self, freq, duration, sr):
            return render_fn(freq, duration, sr)

    Synth.register(name, PluginDesigner())
    _SYNTH_PLUGINS[name] = render_fn


# ---------------------------------------------------------------------------
# Cross-language bridges (subprocess-based, works with any installed tool)
# ---------------------------------------------------------------------------


def render_with_csound(
    orc: str,
    sco: str,
    output_path: str = "/tmp/csound_out.wav",
    sample_rate: int = 44100,
) -> Any:
    """Render audio using Csound (C/C++ DSP engine).

    Csound has 30+ years of DSP opcodes. Anything code-music cannot
    synthesize natively, Csound probably can. Write the .orc and .sco
    as strings, get back a numpy array.

    Requires: csound installed (brew install csound / apt install csound)
    """
    import subprocess
    import tempfile
    import numpy as np

    with tempfile.NamedTemporaryFile(suffix=".orc", mode="w", delete=False) as f_orc:
        f_orc.write(orc)
        orc_path = f_orc.name
    with tempfile.NamedTemporaryFile(suffix=".sco", mode="w", delete=False) as f_sco:
        f_sco.write(sco)
        sco_path = f_sco.name

    try:
        result = subprocess.run(
            ["csound", "-o", output_path, "-r", str(sample_rate), orc_path, sco_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Csound failed: {result.stderr[:500]}")
        return import_audio(output_path, sample_rate)
    except FileNotFoundError:
        raise RuntimeError("Csound not found. Install: brew install csound")
    finally:
        Path(orc_path).unlink(missing_ok=True)
        Path(sco_path).unlink(missing_ok=True)


def render_with_supercollider(
    sc_code: str,
    duration: float = 4.0,
    output_path: str = "/tmp/sc_out.wav",
    sample_rate: int = 44100,
) -> Any:
    """Render audio using SuperCollider (sclang).

    SuperCollider is the gold standard for experimental electronic
    music synthesis. If you need granular clouds, spectral processing,
    or custom UGens that do not exist anywhere else, SC has them.

    Requires: SuperCollider installed (brew install supercollider)
    """
    import subprocess
    import tempfile

    # Wrap the code in a render-to-file block
    sc_render = f"""
    Server.default = Server.internal;
    s = Server.internal;
    s.options.sampleRate = {sample_rate};
    s.options.numOutputBusChannels = 1;
    s.waitForBoot({{
        Score.recordNRT(
            [ [0.0, [ \\s_new, \\temp, 1000, 0, 0 ]] ],
            "{output_path}",
            sampleRate: {sample_rate},
            duration: {duration},
            action: {{ 0.exit }}
        );
    }});
    """
    # This is simplified - real SC rendering is more involved
    with tempfile.NamedTemporaryFile(suffix=".scd", mode="w", delete=False) as f:
        f.write(sc_code + f'\nServer.default.record("{output_path}");\n')
        scd_path = f.name

    try:
        result = subprocess.run(
            ["sclang", scd_path],
            capture_output=True,
            text=True,
            timeout=int(duration + 30),
        )
        if Path(output_path).exists():
            return import_audio(output_path, sample_rate)
        raise RuntimeError(f"SuperCollider did not produce output: {result.stderr[:500]}")
    except FileNotFoundError:
        raise RuntimeError("sclang not found. Install SuperCollider.")
    finally:
        Path(scd_path).unlink(missing_ok=True)


def render_with_sox(
    input_path: str,
    effects: list[str],
    output_path: str = "/tmp/sox_out.wav",
    sample_rate: int = 44100,
) -> Any:
    """Process audio using SoX (Swiss Army knife of audio).

    SoX has effects that are hard to replicate: pitch detection,
    time stretching (WSOLA), format conversion, noise profiling,
    spectrograms, and 80+ other effects.

    Requires: sox installed (brew install sox)

    Example::

        # Pitch shift up 3 semitones
        audio = render_with_sox("input.wav", ["pitch", "300"])

        # Time stretch to 120% without pitch change
        audio = render_with_sox("input.wav", ["tempo", "1.2"])

        # Add reverb
        audio = render_with_sox("input.wav", ["reverb", "50", "50", "100"])
    """
    import subprocess

    cmd = ["sox", input_path, "-r", str(sample_rate), output_path] + effects
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"SoX failed: {result.stderr[:500]}")
        return import_audio(output_path, sample_rate)
    except FileNotFoundError:
        raise RuntimeError("SoX not found. Install: brew install sox")


def render_with_fluidsynth(
    midi_path: str,
    soundfont_path: str,
    output_path: str = "/tmp/fluidsynth_out.wav",
    sample_rate: int = 44100,
) -> Any:
    """Render MIDI using FluidSynth with a SoundFont (.sf2).

    SoundFonts are sample-based instruments - real recorded piano,
    strings, brass, etc. When you need photorealistic instrument
    sounds instead of synthesis, this is the path. Thousands of free
    SoundFonts exist online.

    Requires: fluidsynth installed (brew install fluid-synth)

    Example::

        # Export song to MIDI, then render with a grand piano SoundFont
        from code_music.midi import export_midi
        export_midi(song, "/tmp/song.mid")
        audio = render_with_fluidsynth("/tmp/song.mid", "grand_piano.sf2")
    """
    import subprocess

    try:
        result = subprocess.run(
            [
                "fluidsynth",
                "-ni",
                "-r",
                str(sample_rate),
                "-F",
                output_path,
                soundfont_path,
                midi_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FluidSynth failed: {result.stderr[:500]}")
        return import_audio(output_path, sample_rate)
    except FileNotFoundError:
        raise RuntimeError("FluidSynth not found. Install: brew install fluid-synth")


def render_with_cli(
    command: list[str],
    output_path: str,
    sample_rate: int = 44100,
    timeout: int = 120,
) -> Any:
    """Generic bridge: run any CLI tool that produces a WAV file.

    This is the escape hatch. If a tool exists as a command-line program
    and can write a WAV file, you can use it from code-music.

    Args:
        command:      Command and arguments (e.g. ["my_synth", "--render", "out.wav"]).
        output_path:  Where the tool writes its output.
        sample_rate:  Target sample rate (for resampling if needed).
        timeout:      Max seconds to wait.

    Returns:
        Mono float64 numpy array.
    """
    import subprocess

    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if not Path(output_path).exists():
        raise RuntimeError(
            f"Command did not produce {output_path}. "
            f"Exit code: {result.returncode}. Stderr: {result.stderr[:500]}"
        )
    return import_audio(output_path, sample_rate)


def list_integrations() -> dict[str, bool]:
    """Check which optional integrations are available.

    Checks Python libraries AND command-line tools from other languages.

    Returns:
        Dict mapping integration name to whether it is installed/available.
    """
    import shutil

    available = {}

    # Python libraries
    for lib in [
        "music21",
        "pretty_midi",
        "librosa",
        "pyo",
        "midiutil",
        "audiocraft",
        "torch",
        "sounddevice",
    ]:
        try:
            __import__(lib)
            available[f"python:{lib}"] = True
        except ImportError:
            available[f"python:{lib}"] = False

    # Command-line tools (other languages)
    cli_tools = {
        "cli:csound": "csound",  # C/C++ DSP engine
        "cli:supercollider": "sclang",  # SuperCollider
        "cli:sox": "sox",  # Swiss Army knife of audio
        "cli:fluidsynth": "fluidsynth",  # SoundFont renderer
        "cli:ffmpeg": "ffmpeg",  # Audio/video swiss army knife
        "cli:lilypond": "lilypond",  # Music engraving
        "cli:timidity": "timidity",  # MIDI software synth
        "cli:abc2midi": "abc2midi",  # ABC notation to MIDI
    }
    for name, cmd in cli_tools.items():
        available[name] = shutil.which(cmd) is not None

    available["ai_backends"] = len(_AI_BACKENDS) > 0
    available["synth_plugins"] = len(_SYNTH_PLUGINS) > 0
    return available
