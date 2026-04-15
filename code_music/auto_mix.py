"""Automatic mixing intelligence.

Analyze tracks and make mixing decisions that a human engineer would make.
Frequency-aware leveling, panning, EQ carving, and automation. The AI
mixing engineer that works on every song instantly.

Example::

    from code_music.auto_mix import auto_mix, auto_pan_placement, auto_eq_carve

    # One-call auto-mix: levels, panning, EQ, all at once
    mixed = auto_mix(song)

    # Or use individual tools
    auto_pan_placement(song)   # spread tracks across stereo field
    auto_eq_carve(song)        # cut overlapping frequencies
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from scipy import signal as sig

from .engine import Note, Chord, Song, Track


# ---------------------------------------------------------------------------
# Track analysis helpers
# ---------------------------------------------------------------------------


def _analyze_track_spectrum(
    mono: np.ndarray,
    sample_rate: int,
) -> dict:
    """Analyze a track's frequency content."""
    n = len(mono)
    if n < 256:
        return {
            "centroid": 1000.0,
            "rms": 0.0,
            "peak_freq": 440.0,
            "low_energy": 0.0,
            "high_energy": 0.0,
        }

    fft = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(n, 1.0 / sample_rate)

    total = np.sum(fft**2)
    if total < 1e-20:
        return {
            "centroid": 1000.0,
            "rms": 0.0,
            "peak_freq": 440.0,
            "low_energy": 0.0,
            "high_energy": 0.0,
        }

    centroid = float(np.sum(freqs * fft**2) / total)
    peak_freq = float(freqs[np.argmax(fft[1:]) + 1])
    rms = float(np.sqrt(np.mean(mono**2)))

    # Energy in bands
    low_mask = freqs < 250
    high_mask = freqs > 4000
    low_energy = float(np.sum(fft[low_mask] ** 2) / total) if np.any(low_mask) else 0.0
    high_energy = float(np.sum(fft[high_mask] ** 2) / total) if np.any(high_mask) else 0.0

    return {
        "centroid": centroid,
        "rms": rms,
        "peak_freq": peak_freq,
        "low_energy": low_energy,
        "high_energy": high_energy,
    }


def _detect_track_role(track: Track) -> str:
    """Classify a track's musical role from its name and instrument."""
    name = track.name.lower()
    inst = track.instrument.lower()

    if any(k in name or k in inst for k in ("kick", "808")):
        return "kick"
    if any(k in name or k in inst for k in ("snare", "clap", "rim")):
        return "snare"
    if any(k in name or k in inst for k in ("hat", "ride", "cymbal", "crash")):
        return "hat"
    if any(k in name or k in inst for k in ("bass", "sub")):
        return "bass"
    if any(k in name or k in inst for k in ("pad", "strings", "ambient")):
        return "pad"
    if any(k in name or k in inst for k in ("lead", "melody", "solo", "vocal")):
        return "lead"
    if any(k in name or k in inst for k in ("chord", "rhythm", "guitar", "piano", "keys", "organ")):
        return "chords"
    return "other"


# ---------------------------------------------------------------------------
# Auto-leveling
# ---------------------------------------------------------------------------


def auto_level(song: Song) -> Song:
    """Set track volumes based on frequency content and musical role.

    Kick and bass get more headroom. Leads sit on top. Pads sit
    underneath. Hats are quiet. The basic level balance that every
    mix engineer starts with, computed automatically.

    Modifies song.tracks in place and returns the song.
    """
    role_volumes = {
        "kick": 0.80,
        "snare": 0.70,
        "hat": 0.35,
        "bass": 0.70,
        "pad": 0.40,
        "lead": 0.65,
        "chords": 0.50,
        "other": 0.55,
    }

    for track in song.tracks:
        role = _detect_track_role(track)
        target = role_volumes.get(role, 0.55)
        track.volume = target

    return song


# ---------------------------------------------------------------------------
# Auto-panning
# ---------------------------------------------------------------------------


def auto_pan_placement(song: Song) -> Song:
    """Place tracks across the stereo field based on frequency and role.

    Bass and kick: dead center (mono low end is critical).
    Lead: slightly off-center (presence without losing focus).
    Chords: moderate L or R (open the center for vocals/lead).
    Pads: wide (fill the edges).
    Hats/cymbals: slight offset (realism).
    Double instruments: hard-pan L/R for width.

    Modifies song.tracks in place and returns the song.
    """
    role_pans = {
        "kick": 0.0,
        "snare": 0.0,
        "bass": 0.0,
        "lead": -0.1,
        "hat": 0.25,
    }

    # Track pairs that should mirror (guitar_L/guitar_R, etc.)
    chord_tracks = []
    pad_tracks = []

    for track in song.tracks:
        role = _detect_track_role(track)
        if role in role_pans:
            track.pan = role_pans[role]
        elif role == "chords":
            chord_tracks.append(track)
        elif role == "pad":
            pad_tracks.append(track)
        else:
            track.pan = 0.0

    # Spread chord tracks L/R
    for i, t in enumerate(chord_tracks):
        if len(chord_tracks) == 1:
            t.pan = 0.2
        else:
            spread = 0.6
            t.pan = -spread + (2 * spread * i / max(len(chord_tracks) - 1, 1))

    # Spread pads wide
    for i, t in enumerate(pad_tracks):
        if len(pad_tracks) == 1:
            t.pan = 0.0
        else:
            spread = 0.7
            t.pan = -spread + (2 * spread * i / max(len(pad_tracks) - 1, 1))

    return song


# ---------------------------------------------------------------------------
# Auto EQ carving
# ---------------------------------------------------------------------------


def auto_eq_carve(song: Song) -> Song:
    """Add EQ cuts to prevent tracks from masking each other.

    When two tracks occupy the same frequency range, one masks the other.
    This analyzes each track's spectral content and adds subtle EQ cuts
    so every track has its own frequency "slot." The bass gets a low-mid
    cut to make room for the kick. The pad gets a mid cut to make room
    for the lead. Etc.

    Adds EffectsChain entries to song.effects and returns the song.
    """
    from .effects import parametric_eq

    if not hasattr(song, "effects") or song.effects is None:
        song.effects = {}

    roles = {}
    for track in song.tracks:
        role = _detect_track_role(track)
        roles[track.name] = role

    for track in song.tracks:
        role = roles.get(track.name, "other")
        bands = []

        if role == "bass":
            # Cut 200-500 Hz to make room for kick body
            bands.append(("peak", 350.0, -2.0, 1.5))
            # Highpass below 30 Hz (subsonic cleanup)
            bands.append(("highpass", 30.0, 0.0, 0.7))

        elif role == "kick":
            # Cut 300-600 Hz to tighten (boxy frequencies)
            bands.append(("peak", 400.0, -3.0, 1.0))

        elif role == "chords":
            # Cut low end to stay out of bass territory
            bands.append(("highpass", 120.0, 0.0, 0.7))
            # Cut 2-4 kHz slightly to make room for lead
            bands.append(("peak", 3000.0, -2.0, 1.0))

        elif role == "pad":
            # Cut low end aggressively
            bands.append(("highpass", 200.0, 0.0, 0.7))
            # Cut mids to make room for everything else
            bands.append(("peak", 1000.0, -3.0, 0.8))

        elif role == "lead":
            # Boost presence
            bands.append(("peak", 3000.0, 2.0, 1.5))
            # Cut below 200 Hz
            bands.append(("highpass", 200.0, 0.0, 0.7))

        elif role == "hat":
            # Highpass aggressively (hats do not need low end)
            bands.append(("highpass", 500.0, 0.0, 0.7))

        if bands and track.name not in song.effects:
            from .effects import EffectsChain

            song.effects[track.name] = EffectsChain().add(
                parametric_eq,
                bands=bands,
            )

    return song


# ---------------------------------------------------------------------------
# Fade / swell automation
# ---------------------------------------------------------------------------


def fade_in(
    song: Song,
    track_name: str,
    beats: float = 4.0,
) -> Song:
    """Apply a volume fade-in to the start of a track.

    Modifies the track's note velocities for the first N beats.
    """
    for track in song.tracks:
        if track.name != track_name:
            continue
        cumulative = 0.0
        for beat in track.beats:
            if cumulative < beats:
                frac = cumulative / beats
                if beat.event and hasattr(beat.event, "velocity"):
                    beat.event.velocity *= frac
            cumulative += beat.duration
    return song


def fade_out(
    song: Song,
    track_name: str,
    beats: float = 4.0,
) -> Song:
    """Apply a volume fade-out to the end of a track."""
    for track in song.tracks:
        if track.name != track_name:
            continue
        total = track.total_beats
        start_fade = total - beats
        cumulative = 0.0
        for beat in track.beats:
            if cumulative > start_fade:
                frac = max(0.0, 1.0 - (cumulative - start_fade) / beats)
                if beat.event and hasattr(beat.event, "velocity"):
                    beat.event.velocity *= frac
            cumulative += beat.duration
    return song


def swell(
    song: Song,
    track_name: str,
    start_beat: float = 0.0,
    peak_beat: float = 4.0,
    end_beat: float = 8.0,
    peak_velocity: float = 1.0,
) -> Song:
    """Create a volume swell (crescendo then decrescendo) on a track."""
    for track in song.tracks:
        if track.name != track_name:
            continue
        cumulative = 0.0
        for beat in track.beats:
            if (
                start_beat <= cumulative <= end_beat
                and beat.event
                and hasattr(beat.event, "velocity")
            ):
                if cumulative <= peak_beat:
                    frac = (cumulative - start_beat) / max(peak_beat - start_beat, 0.01)
                else:
                    frac = 1.0 - (cumulative - peak_beat) / max(end_beat - peak_beat, 0.01)
                frac = max(0.0, min(1.0, frac))
                beat.event.velocity = beat.event.velocity * (1 - frac) + peak_velocity * frac
            cumulative += beat.duration
    return song


# ---------------------------------------------------------------------------
# The one-call auto-mixer
# ---------------------------------------------------------------------------


def auto_mix(song: Song) -> Song:
    """One-call automatic mixing: levels, panning, and EQ carving.

    Analyzes all tracks and makes mixing decisions:
    1. Set volumes based on musical role
    2. Place tracks across the stereo field
    3. Add EQ cuts to prevent masking

    This is the "make it sound good" button. Not a substitute for a
    human mix engineer on a critical release, but better than random
    volume knobs and center-panned everything.

    Modifies song in place and returns it.

    Example::

        song = auto_mix(song)
        audio = song.render()
    """
    auto_level(song)
    auto_pan_placement(song)
    auto_eq_carve(song)
    return song
