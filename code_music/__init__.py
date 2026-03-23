"""code-music: write code blocks, export audio."""

from .effects import (
    bandpass,
    chorus,
    compress,
    delay,
    distortion,
    highpass,
    lfo_filter,
    lowpass,
    pan,
    reverb,
    sidechain,
    tremolo,
    vibrato,
)
from .engine import CHORD_SHAPES, INTERVALS, SCALES, Beat, Chord, Note, Song, Track, scale
from .export import export_flac, export_mp3, export_ogg, export_wav
from .synth import Synth
from .voice import VoiceClip, VoiceTrack, detect_backends, list_voices
from .voice import generate as generate_voice

__all__ = [
    # engine
    "Note",
    "Chord",
    "Beat",
    "Track",
    "Song",
    "scale",
    "SCALES",
    "CHORD_SHAPES",
    "INTERVALS",
    # synth
    "Synth",
    # export
    "export_wav",
    "export_mp3",
    "export_ogg",
    "export_flac",
    # effects
    "reverb",
    "delay",
    "chorus",
    "distortion",
    "lowpass",
    "highpass",
    "bandpass",
    "compress",
    "pan",
    "sidechain",
    "tremolo",
    "vibrato",
    "lfo_filter",
    # voice
    "VoiceClip",
    "VoiceTrack",
    "generate_voice",
    "detect_backends",
    "list_voices",
]
