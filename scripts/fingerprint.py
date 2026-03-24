#!/usr/bin/env python3
"""Song fingerprinting — detect audio regression between renders.

Computes a perceptual fingerprint of each rendered WAV file using
spectral band energy. Two renders of the same song script should
produce identical fingerprints. If a code change alters the audio
output, the fingerprint changes — catching unintentional regressions.

Usage:
    python scripts/fingerprint.py --snapshot          # save current state
    python scripts/fingerprint.py --check             # compare against snapshot
    python scripts/fingerprint.py --diff              # show which songs changed
    python scripts/fingerprint.py --file dist/wav/trance_odyssey.wav  # one file
    make fingerprint                                  # snapshot
    make fingerprint-check                            # compare
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import wave
from pathlib import Path

import numpy as np

REPO = Path(__file__).parent.parent
WAV_DIR = REPO / "dist" / "wav"
SNAPSHOT_FILE = REPO / ".fingerprints.json"

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
DIM = "\033[2m"

# Number of frequency bands for the spectral fingerprint
N_BANDS = 32
# Number of time slices
N_SLICES = 64


def _read_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    """Read a WAV file to a mono float64 array + sample rate."""
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
        raw = wf.readframes(n)
    dtype = np.int16 if sw == 2 else np.int32
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    samples /= 32768.0 if sw == 2 else 2147483648.0
    if ch == 2:
        samples = samples.reshape(-1, 2).mean(axis=1)
    return samples, sr


def fingerprint_wav(path: Path) -> str:
    """Compute a perceptual fingerprint hash for a WAV file.

    Splits the audio into time slices, computes a simple spectral
    energy profile for each slice using FFT, quantises the energy
    into bands, and hashes the result. Two identical audio files
    always produce the same fingerprint. Small changes in the audio
    (different note timing, volume, effects) change the fingerprint.

    Returns:
        Hex string hash (SHA-256 of the spectral energy matrix).
    """
    samples, sr = _read_wav_mono(path)
    n = len(samples)

    if n < 1024:
        # Too short — just hash the raw samples
        return hashlib.sha256(samples.tobytes()).hexdigest()[:32]

    # Split into N_SLICES time windows
    slice_len = n // N_SLICES
    energy_matrix = np.zeros((N_SLICES, N_BANDS))

    for i in range(N_SLICES):
        start = i * slice_len
        chunk = samples[start : start + slice_len]
        if len(chunk) < 64:
            continue

        # FFT
        fft = np.abs(np.fft.rfft(chunk))
        freq_bins = len(fft)

        # Split FFT bins into N_BANDS logarithmic bands
        band_edges = np.logspace(np.log10(1), np.log10(freq_bins), N_BANDS + 1).astype(int)
        for b in range(N_BANDS):
            lo = band_edges[b]
            hi = min(band_edges[b + 1], freq_bins)
            if hi > lo:
                energy_matrix[i, b] = np.mean(fft[lo:hi])

    # Normalise
    peak = np.max(energy_matrix)
    if peak > 0:
        energy_matrix /= peak

    # Quantise to 8-bit for stable hashing (ignore tiny float differences)
    quantised = (energy_matrix * 255).astype(np.uint8)

    return hashlib.sha256(quantised.tobytes()).hexdigest()[:32]


def snapshot(wav_dir: Path = WAV_DIR) -> dict[str, str]:
    """Fingerprint all WAV files and save to .fingerprints.json."""
    wavs = sorted(wav_dir.glob("*.wav"))
    if not wavs:
        print(f"{YELLOW}No WAV files found. Run: make songs-wav{RESET}")
        return {}

    fps: dict[str, str] = {}
    for wav in wavs:
        stem = wav.stem
        fp = fingerprint_wav(wav)
        fps[stem] = fp
        print(f"  {stem:<35} {DIM}{fp}{RESET}")

    SNAPSHOT_FILE.write_text(json.dumps(fps, indent=2, sort_keys=True) + "\n")
    print(f"\n{GREEN}Snapshot saved: {SNAPSHOT_FILE.name} ({len(fps)} songs){RESET}")
    return fps


def check(wav_dir: Path = WAV_DIR) -> bool:
    """Compare current renders against the saved snapshot.

    Returns True if all fingerprints match, False if any differ.
    """
    if not SNAPSHOT_FILE.exists():
        print(f"{YELLOW}No snapshot found. Run: make fingerprint{RESET}")
        return False

    saved = json.loads(SNAPSHOT_FILE.read_text())
    wavs = sorted(wav_dir.glob("*.wav"))
    current = {wav.stem: fingerprint_wav(wav) for wav in wavs}

    changed: list[str] = []
    missing: list[str] = []
    new: list[str] = []
    matched = 0

    for stem, saved_fp in sorted(saved.items()):
        if stem not in current:
            missing.append(stem)
        elif current[stem] != saved_fp:
            changed.append(stem)
        else:
            matched += 1

    for stem in current:
        if stem not in saved:
            new.append(stem)

    # Report
    if changed:
        print(f"\n{RED}{BOLD}CHANGED ({len(changed)}):{RESET}")
        for s in changed:
            print(f"  {RED}✗{RESET} {s}")
            print(f"    was:    {DIM}{saved[s]}{RESET}")
            print(f"    now:    {DIM}{current[s]}{RESET}")

    if missing:
        print(f"\n{YELLOW}MISSING ({len(missing)}):{RESET}")
        for s in missing:
            print(f"  {YELLOW}?{RESET} {s} (in snapshot but not rendered)")

    if new:
        print(f"\n{DIM}NEW ({len(new)}):{RESET}")
        for s in new:
            print(f"  {DIM}+{RESET} {s} (not in snapshot)")

    print(f"\n{matched} matched, {len(changed)} changed, {len(missing)} missing, {len(new)} new")

    if changed:
        print(f"\n{RED}{BOLD}REGRESSION DETECTED{RESET}")
        print(
            f"Run {BOLD}make fingerprint{RESET} to update the snapshot "
            f"if these changes are intentional.\n"
        )
        return False

    print(f"\n{GREEN}{BOLD}All fingerprints match.{RESET}\n")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Song fingerprinting — detect audio regression")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--snapshot", action="store_true", help="Save fingerprints of all rendered songs"
    )
    group.add_argument(
        "--check", action="store_true", help="Compare current renders against snapshot"
    )
    group.add_argument("--diff", action="store_true", help="Same as --check (alias)")
    group.add_argument("--file", type=Path, help="Fingerprint a single WAV file")
    parser.add_argument(
        "--dir", type=Path, default=WAV_DIR, help="WAV directory (default: dist/wav/)"
    )
    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        fp = fingerprint_wav(args.file)
        print(f"{args.file.stem}: {fp}")
    elif args.snapshot:
        snapshot(args.dir)
    elif args.check or args.diff:
        ok = check(args.dir)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
