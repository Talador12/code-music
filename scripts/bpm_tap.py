#!/usr/bin/env python3
"""BPM tap utility — tap Enter to the beat, get the tempo.

Tap along to any music. After 4+ taps it shows the running average BPM.
Resets after 3 seconds of silence. Ctrl+C to quit.

Usage:
    python scripts/bpm_tap.py
    make bpm-tap
"""

from __future__ import annotations

import sys
import time

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"
UP1 = "\033[1A"
ERASE = "\033[2K"

RESET_TIMEOUT = 3.0  # seconds of silence before resetting


def run() -> None:
    taps: list[float] = []

    sys.stdout.write(
        f"\n{BOLD}BPM Tap{RESET}  {DIM}— tap Enter to the beat, Ctrl+C to quit{RESET}\n"
        f"{DIM}Resets after {RESET_TIMEOUT:.0f}s of no taps{RESET}\n\n"
        f"  {DIM}waiting for first tap...{RESET}\n"
    )
    sys.stdout.flush()

    try:
        while True:
            input()  # blocks until Enter
            now = time.monotonic()

            # Reset if too long since last tap
            if taps and (now - taps[-1]) > RESET_TIMEOUT:
                taps.clear()

            taps.append(now)

            if len(taps) < 2:
                sys.stdout.write(f"{UP1}{ERASE}  {CYAN}tap 1{RESET}  {DIM}keep going...{RESET}\n")
                sys.stdout.flush()
                continue

            # Calculate BPM from intervals
            intervals = [taps[i] - taps[i - 1] for i in range(1, len(taps))]
            avg_interval = sum(intervals) / len(intervals)
            bpm = 60.0 / avg_interval if avg_interval > 0 else 0

            # Confidence based on consistency of intervals
            if len(intervals) >= 2:
                std = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
                consistency = max(0.0, 1.0 - std / max(avg_interval, 0.01))
            else:
                consistency = 0.0

            # Visual confidence bar
            bar_len = int(consistency * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)

            color = GREEN if consistency > 0.8 else YELLOW if consistency > 0.5 else CYAN

            sys.stdout.write(
                f"{UP1}{ERASE}"
                f"  {color}{BOLD}{bpm:6.1f} BPM{RESET}"
                f"  {DIM}[{bar}]{RESET}"
                f"  {DIM}{len(taps)} taps{RESET}\n"
            )
            sys.stdout.flush()

    except (KeyboardInterrupt, EOFError):
        if len(taps) >= 2:
            intervals = [taps[i] - taps[i - 1] for i in range(1, len(taps))]
            final_bpm = 60.0 / (sum(intervals) / len(intervals))
            sys.stdout.write(f"\n{GREEN}{BOLD}Final: {final_bpm:.1f} BPM{RESET}\n\n")
        else:
            sys.stdout.write(f"\n{DIM}Not enough taps.{RESET}\n\n")
        sys.stdout.flush()


def main() -> None:
    run()


if __name__ == "__main__":
    main()
