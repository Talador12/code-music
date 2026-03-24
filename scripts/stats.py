#!/usr/bin/env python3
"""Song statistics — total duration, BPM distribution, genre counts, etc.

Usage:
    python scripts/stats.py
    make stats
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

REPO = Path(__file__).parent.parent

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
DIM = "\033[2m"
YELLOW = "\033[93m"


def load_songs() -> list[dict]:
    """Load all song modules and extract metadata."""
    songs_dir = REPO / "songs"
    results = []
    for f in sorted(songs_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location("_s", f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            song = mod.song
            results.append(
                {
                    "file": f.stem,
                    "title": song.title,
                    "bpm": song.bpm,
                    "duration": song.duration_sec,
                    "tracks": len(song.tracks),
                    "time_sig": song.time_sig,
                    "key_sig": getattr(song, "key_sig", "C"),
                }
            )
        except Exception as e:
            results.append({"file": f.stem, "title": f.stem, "error": str(e)})
    return results


def main() -> None:
    songs = load_songs()
    valid = [s for s in songs if "error" not in s]
    errors = [s for s in songs if "error" in s]

    total_songs = len(songs)
    total_dur = sum(s.get("duration", 0) for s in valid)
    total_min = int(total_dur // 60)
    total_sec = int(total_dur % 60)

    bpms = [s["bpm"] for s in valid]
    avg_bpm = sum(bpms) / len(bpms) if bpms else 0
    min_bpm = min(bpms) if bpms else 0
    max_bpm = max(bpms) if bpms else 0

    total_tracks = sum(s.get("tracks", 0) for s in valid)

    # BPM distribution
    bpm_buckets = Counter()
    for b in bpms:
        if b < 80:
            bpm_buckets["< 80 (slow)"] += 1
        elif b < 110:
            bpm_buckets["80–109 (mid)"] += 1
        elif b < 130:
            bpm_buckets["110–129 (house)"] += 1
        elif b < 150:
            bpm_buckets["130–149 (EDM)"] += 1
        elif b < 175:
            bpm_buckets["150–174 (fast)"] += 1
        else:
            bpm_buckets["175+ (DnB)"] += 1

    # Time signatures
    time_sigs = Counter(str(s.get("time_sig", (4, 4))) for s in valid)

    # Key signatures
    keys = Counter(s.get("key_sig", "C") for s in valid)

    # Duration distribution
    dur_buckets = Counter()
    for s in valid:
        d = s.get("duration", 0)
        if d < 30:
            dur_buckets["< 30s"] += 1
        elif d < 60:
            dur_buckets["30–59s"] += 1
        elif d < 120:
            dur_buckets["1–2 min"] += 1
        elif d < 180:
            dur_buckets["2–3 min"] += 1
        else:
            dur_buckets["3+ min"] += 1

    # Longest / shortest
    by_dur = sorted(valid, key=lambda s: s.get("duration", 0))
    shortest = by_dur[0] if by_dur else None
    longest = by_dur[-1] if by_dur else None

    # Print
    print(f"\n{BOLD}{CYAN}code-music statistics{RESET}\n")
    print(f"  Songs:          {BOLD}{total_songs}{RESET}")
    print(f"  Total duration: {BOLD}{total_min}m {total_sec}s{RESET}  ({total_dur:.0f}s)")
    print(
        f"  Total tracks:   {total_tracks}  (avg {total_tracks / max(len(valid), 1):.1f} per song)"
    )
    print(f"  BPM range:      {min_bpm:.0f} – {max_bpm:.0f}  (avg {avg_bpm:.0f})")

    if shortest and longest:
        print(f"  Shortest:       {shortest['title']} ({shortest['duration']:.0f}s)")
        print(f"  Longest:        {longest['title']} ({longest['duration']:.0f}s)")

    print(f"\n{BOLD}BPM Distribution:{RESET}")
    for bucket in [
        "< 80 (slow)",
        "80–109 (mid)",
        "110–129 (house)",
        "130–149 (EDM)",
        "150–174 (fast)",
        "175+ (DnB)",
    ]:
        count = bpm_buckets.get(bucket, 0)
        bar = "█" * count + "░" * (max(bpm_buckets.values()) - count) if count else ""
        print(f"  {bucket:<20} {bar}  {count}")

    print(f"\n{BOLD}Duration Distribution:{RESET}")
    for bucket in ["< 30s", "30–59s", "1–2 min", "2–3 min", "3+ min"]:
        count = dur_buckets.get(bucket, 0)
        bar = "█" * count
        print(f"  {bucket:<12} {bar}  {count}")

    print(f"\n{BOLD}Time Signatures:{RESET}")
    for ts, count in time_sigs.most_common():
        print(f"  {ts:<12} {count}")

    print(f"\n{BOLD}Key Signatures:{RESET}")
    for key, count in keys.most_common(10):
        print(f"  {key:<6} {count}")

    if errors:
        print(f"\n{YELLOW}Errors ({len(errors)}):{RESET}")
        for e in errors:
            print(f"  {e['file']}: {e['error']}")

    print()


if __name__ == "__main__":
    main()
