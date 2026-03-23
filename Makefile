# code-music Makefile
# Usage: make <target>
# Requires: Python 3.11+  |  MP3/OGG/FLAC: brew install ffmpeg
#
# Output directories (gitignored):
#   dist/wav/       lossless PCM — archive / DAW import
#   dist/flac/      lossless compressed — Spotify ingest (preferred)
#   dist/mp3/       lossy 320kbps — Spotify / sharing
#   dist/samples/   rendered sample previews (WAV)

PYTHON  ?= python3
VENV    := .venv
BIN     := $(VENV)/bin
CM      := $(BIN)/python -m code_music.cli

# Discover all song and sample scripts automatically
SONGS   := $(wildcard songs/*.py)
SAMPLES := $(wildcard samples/**/*.py)

# Derive target names from script names (strip dir + .py)
SONG_NAMES   := $(notdir $(basename $(SONGS)))
SAMPLE_NAMES := $(notdir $(basename $(SAMPLES)))

# Output paths per format
WAV_SONGS   := $(addprefix dist/wav/,   $(addsuffix .wav,  $(SONG_NAMES)))
FLAC_SONGS  := $(addprefix dist/flac/,  $(addsuffix .flac, $(SONG_NAMES)))
MP3_SONGS   := $(addprefix dist/mp3/,   $(addsuffix .mp3,  $(SONG_NAMES)))
WAV_SAMPLES := $(foreach s,$(SAMPLES),dist/samples/$(notdir $(basename $(s))).wav)

.PHONY: all install dev lint test \
        songs-wav songs-flac songs-mp3 songs-all \
        samples spotify clean help

# ── Setup ────────────────────────────────────────────────────────────────────

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e ".[dev]" -q

dev: install
	@command -v ffmpeg >/dev/null 2>&1 \
		&& echo "ffmpeg found — MP3/OGG/FLAC export enabled" \
		|| echo "WARNING: ffmpeg not found — only WAV available (brew install ffmpeg)"

# ── Quality ──────────────────────────────────────────────────────────────────

lint:
	$(BIN)/ruff check code_music tests songs samples

test:
	$(BIN)/pytest tests/ -v

# ── Render: songs ────────────────────────────────────────────────────────────

# WAV render rule for songs
dist/wav/%.wav: songs/%.py
	@mkdir -p dist/wav
	$(CM) $< -o $@

# FLAC render rule (lossless compressed — best for Spotify ingest)
dist/flac/%.flac: songs/%.py
	@mkdir -p dist/flac
	$(CM) $< --flac -o $@

# MP3 render rule (lossy 320kbps)
dist/mp3/%.mp3: songs/%.py
	@mkdir -p dist/mp3
	$(CM) $< --mp3 -o $@

songs-wav:  $(WAV_SONGS)
songs-flac: $(FLAC_SONGS)
songs-mp3:  $(MP3_SONGS)
songs-all:  songs-wav songs-flac songs-mp3

# ── Render: samples ──────────────────────────────────────────────────────────

# Pattern rule for all sample subdirs
dist/samples/%.wav: samples/bass/%.py     ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/highs/%.py    ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/synths/%.py   ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/waves/%.py    ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/chords/%.py   ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/instruments/%.py ; @mkdir -p dist/samples && $(CM) $< -o $@
dist/samples/%.wav: samples/drums/%.py    ; @mkdir -p dist/samples && $(CM) $< -o $@

# Render all samples (WAV only — they're short previews)
samples: $(WAV_SAMPLES)

# ── Spotify upload targets ────────────────────────────────────────────────────
# Spotify for Artists accepts: FLAC (preferred), MP3 320k, WAV 16-bit
# Min duration: 30s.  Recommended: FLAC 44100 Hz stereo.

spotify: songs-flac
	@echo ""
	@echo "Spotify-ready files in dist/flac/:"
	@ls -lh dist/flac/*.flac 2>/dev/null || echo "  (none yet)"
	@echo ""
	@echo "Upload at: https://artists.spotify.com"

# Convenience alias: render everything lossless+lossy
all: songs-all samples

# ── Clean ────────────────────────────────────────────────────────────────────

clean:
	rm -rf dist/ .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null; true

# ── Help ─────────────────────────────────────────────────────────────────────

help:
	@echo "code-music Makefile"
	@echo ""
	@echo "Setup:"
	@echo "  make install       create .venv and install deps"
	@echo "  make dev           install + check ffmpeg"
	@echo ""
	@echo "Quality:"
	@echo "  make lint          ruff check all Python"
	@echo "  make test          pytest tests/"
	@echo ""
	@echo "Render songs:"
	@echo "  make songs-wav     dist/wav/*.wav   (lossless PCM)"
	@echo "  make songs-flac    dist/flac/*.flac (lossless, Spotify-ready)"
	@echo "  make songs-mp3     dist/mp3/*.mp3   (lossy 320k)"
	@echo "  make songs-all     all three formats"
	@echo ""
	@echo "Render samples:"
	@echo "  make samples       dist/samples/*.wav (short previews)"
	@echo ""
	@echo "Spotify:"
	@echo "  make spotify       render FLAC + show upload instructions"
	@echo ""
	@echo "  make all           everything"
	@echo "  make clean         remove dist/ and caches"
