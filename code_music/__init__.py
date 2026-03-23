"""code-music: write code blocks, export audio."""

from .effects import bandpass, chorus, compress, delay, distortion, highpass, lowpass, pan, reverb
from .engine import CHORD_SHAPES, INTERVALS, SCALES, Beat, Chord, Note, Song, Track, scale
from .export import export_flac, export_mp3, export_ogg, export_wav
from .synth import Synth

__all__ = [
    "Note",
    "Chord",
    "Beat",
    "Track",
    "Song",
    "scale",
    "SCALES",
    "CHORD_SHAPES",
    "INTERVALS",
    "Synth",
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
]
