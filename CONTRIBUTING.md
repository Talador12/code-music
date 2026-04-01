# Contributing to code-music

## Setup

```bash
git clone https://github.com/Talador12/code-music
cd code-music
make dev    # creates .venv, installs deps
make check  # lint + test (run before every PR)
```

## Writing a song

1. `code-music --new songs/my_song.py` to scaffold
2. Edit the file — change chords, melody, instruments, effects
3. `code-music songs/my_song.py --play` to hear it
4. `make check` to verify lint + tests pass
5. Open a PR

### Song conventions

- One `song` variable per file
- Use `EffectsChain` (not `_effects` lambdas)
- Use `song.effects` (not `song._effects`)
- Seed any `random` usage: `rng = random.Random(42)`
- Keep the docstring: title, style, key, BPM

### Available instruments

```bash
code-music --list-instruments
```

## Running tests

```bash
make test           # full pytest suite
make check          # lint + test
```

## Code style

- Ruff for linting (`ruff check`)
- 100-char line limit for code, relaxed for song data files
- Imports sorted by ruff (isort rules)

## PR checklist

- [ ] `make check` passes
- [ ] New songs render without error
- [ ] No hardcoded counts in docs (say "full set" not "135 songs")
- [ ] No secrets or API keys committed
