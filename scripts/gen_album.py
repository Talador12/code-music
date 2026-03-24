"""Generative album: seed + genre + mood → full procedural album.

Generates a complete album of unique songs from a genre profile and random seed.
Every track is different — different key, different tempo variation, different
generated melody. Same seed always produces the same album.

Usage:
    python scripts/gen_album.py --genre progressive_house --seed 42
    python scripts/gen_album.py --genre ambient --seed 7 --tracks 6
    python scripts/gen_album.py --list-genres
    make gen-album GENRE=bebop_jazz SEED=99

Output:
    dist/albums/generative_<genre>_<seed>/  (WAV + liner notes + M3U)
"""

from __future__ import annotations

import argparse
import importlib
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
DIM = "\033[2m"

AVAILABLE_GENRES = [
    "progressive_house",
    "big_room_electro",
    "ambient",
    "liquid_dnb",
    "bebop_jazz",
    "cinematic_orchestral",
    "cosmic_electro_disco",
]


def load_style(genre: str) -> dict:
    """Load a style profile from styles/."""
    try:
        spec = importlib.util.spec_from_file_location(genre, REPO / "styles" / f"{genre}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.PROFILE
    except Exception as e:
        print(f"Error loading style '{genre}': {e}")
        sys.exit(1)


def make_song(profile: dict, track_num: int, rng: random.Random) -> object:
    """Build one procedural song from a genre profile."""
    from code_music import (
        Note,
        Song,
        Track,
        delay,
        generate_melody,
        reverb,
        stereo_width,
        suggest_progression,
    )

    # Vary BPM slightly around the profile's typical value
    bpm_lo, bpm_hi = profile["bpm_range"]
    bpm = rng.uniform(bpm_lo * 0.95, bpm_hi * 1.05)
    bpm = round(bpm, 1)

    # Pick key from profile's preferred keys
    key = rng.choice(profile["keys"]).replace("m", "").strip()

    # Pick chord progression variation
    # pick progression via suggest_progression below
    mood = rng.choice(["happy", "sad", "chill", "dreamy", "dark", "groovy"])
    prog = suggest_progression(
        key, mood=mood, octave=3, duration=4.0, velocity=0.6, variation=rng.randint(0, 2)
    )

    # Build song
    bars = rng.choice([8, 12, 16, 24])
    song = Song(title=f"Track {track_num:02d}", bpm=bpm)

    # Pad layer
    pad_inst = profile["instruments"].get("pad", "pad")
    pad = song.add_track(Track(name="pad", instrument=pad_inst, volume=rng.uniform(0.35, 0.55)))
    for _ in range(bars // 4):
        pad.extend(prog)

    # Bass layer
    bass_inst = profile["instruments"].get("bass", "bass")
    bass = song.add_track(Track(name="bass", instrument=bass_inst, volume=rng.uniform(0.6, 0.82)))
    for chord in prog * (bars // 4):
        root = chord.root
        oct_n = chord.octave - 1
        bass.add(
            Note(
                root,
                oct_n,
                chord.duration * rng.choice([0.5, 1.0, 1.0]),
                velocity=rng.uniform(0.65, 0.88),
            )
        )
        if rng.random() < 0.4:
            bass.add(Note.rest(chord.duration * 0.5))

    # Generated melody
    scale_mode = rng.choice(profile.get("scales", ["minor", "pentatonic"]))
    try:
        mel_notes = generate_melody(
            key,
            scale_mode=scale_mode,
            octave=5,
            bars=bars,
            density=rng.uniform(0.45, 0.72),
            seed=rng.randint(0, 9999),
        )
        lead_inst = profile["instruments"].get("lead", "piano")
        lead = song.add_track(
            Track(
                name="lead",
                instrument=lead_inst,
                volume=rng.uniform(0.5, 0.75),
                pan=rng.uniform(-0.3, 0.3),
            )
        )
        lead.extend(mel_notes)
    except Exception:
        pass

    # Drums if genre uses them
    drum_cfg = profile["instruments"].get("drums", {})
    if drum_cfg:
        kick_inst = drum_cfg.get("kick", "drums_kick")
        snare_inst = drum_cfg.get("snare", "drums_snare")
        hat_inst = drum_cfg.get("hat", "drums_hat")

        kick = song.add_track(Track(name="kick", instrument=kick_inst, volume=0.95))
        snare = song.add_track(Track(name="snare", instrument=snare_inst, volume=0.75))
        hat = song.add_track(Track(name="hat", instrument=hat_inst, volume=0.4))

        k = Note("C", 2, 1.0)
        s = Note("D", 3, 1.0)
        h = Note("F", 5, 0.5)

        for _ in range(bars):
            kick.extend([k, Note.rest(1.0), k, Note.rest(1.0)])
            snare.extend([Note.rest(1.0), s, Note.rest(1.0), s])
            hat.extend([h] * 8)

    # Simple effects
    fx_settings = profile.get("effects", {})
    effects = {}
    if "pad" in fx_settings and "reverb" in fx_settings["pad"]:
        rv = fx_settings["pad"]["reverb"]
        effects["pad"] = lambda s, sr, _rv=rv: stereo_width(
            reverb(s, sr, room_size=_rv.get("room_size", 0.6), wet=_rv.get("wet", 0.2)),
            width=fx_settings["pad"].get("stereo_width", 1.5),
        )
    if "lead" in fx_settings and "delay" in fx_settings["lead"]:
        dv = fx_settings["lead"]["delay"]
        effects["lead"] = lambda s, sr, _dv=dv: delay(
            s,
            sr,
            delay_ms=_dv.get("delay_ms", 250.0),
            feedback=_dv.get("feedback", 0.3),
            wet=_dv.get("wet", 0.2),
        )
    if effects:
        song._effects = effects

    return song


def render_album(genre: str, seed: int, n_tracks: int, fmt: str = "wav") -> Path:
    """Generate and render a full procedural album."""
    from code_music.export import export_flac, export_mp3, export_wav
    from code_music.synth import Synth

    profile = load_style(genre)
    rng = random.Random(seed)

    out_dir = REPO / "dist" / "albums" / f"generative_{genre}_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{BOLD}{CYAN}Generative Album{RESET}")
    print(f"  Genre: {profile['name']}")
    print(f"  Seed:  {seed}  |  Tracks: {n_tracks}  |  Format: {fmt}\n")

    rendered: list[Path] = []
    synth = Synth()

    for i in range(1, n_tracks + 1):
        song = make_song(profile, i, rng)
        dur = song.duration_sec
        print(
            f"  [{i:02d}/{n_tracks}] Track {i:02d} — {song.bpm:.0f} BPM, {dur:.0f}s ... ",
            end="",
            flush=True,
        )
        t0 = time.monotonic()
        samples = synth.render_song(song)
        elapsed = time.monotonic() - t0

        prefix = f"{i:02d} - Track {i:02d}"
        out = out_dir / f"{prefix}.{fmt}"
        if fmt == "flac":
            export_flac(samples, out)
        elif fmt == "mp3":
            export_mp3(samples, out)
        else:
            export_wav(samples, out)
        rendered.append(out)
        print(f"{GREEN}done{RESET} ({elapsed:.1f}s)")

    # Liner notes
    notes = [
        "=" * 56,
        f"GENERATIVE ALBUM — {profile['name'].upper()}",
        f"Seed: {seed}  |  {n_tracks} tracks",
        "=" * 56,
        "",
        profile.get("description", "A generative composition."),
        "",
        "INFLUENCES",
        *[f"  {inf}" for inf in profile.get("influences", [])],
        "",
        "TRACKS",
        *[f"  {i:02d}. Track {i:02d}" for i in range(1, n_tracks + 1)],
        "",
        "Generated with code-music",
        "https://github.com/Talador12/code-music",
        "=" * 56,
    ]
    (out_dir / "liner_notes.txt").write_text("\n".join(notes))

    # M3U
    m3u = ["#EXTM3U"] + [
        f"#EXTINF:-1,Track {i:02d}\n{i:02d} - Track {i:02d}.{fmt}" for i in range(1, n_tracks + 1)
    ]
    (out_dir / "playlist.m3u").write_text("\n".join(m3u))

    print(f"\n  {GREEN}✓ Album in {out_dir}{RESET}\n")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a procedural album from a genre profile and seed."
    )
    parser.add_argument(
        "--genre", default="ambient", choices=AVAILABLE_GENRES, help="Genre profile to use"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (same seed = same album)")
    parser.add_argument(
        "--tracks", type=int, default=5, help="Number of tracks to generate (default: 5)"
    )
    parser.add_argument(
        "--format", choices=["wav", "flac", "mp3"], default="wav", help="Output audio format"
    )
    parser.add_argument("--list-genres", action="store_true", help="List available genres")
    args = parser.parse_args()

    if args.list_genres:
        print("\nAvailable genres:")
        for g in AVAILABLE_GENRES:
            print(f"  {g}")
        print()
        return

    render_album(args.genre, args.seed, args.tracks, args.format)


if __name__ == "__main__":
    main()
