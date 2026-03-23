# code-music Makefile
# Requires: Python 3.11+  |  MP3/OGG/FLAC: brew install ffmpeg
#
# Output directories (gitignored):
#   dist/wav/       lossless PCM — DAW import, archival
#   dist/flac/      lossless compressed — Spotify preferred ingest
#   dist/mp3/       lossy 320kbps — sharing, streaming
#   dist/samples/   rendered sample previews (WAV, short)
#
# Quick start:
#   make dev                   # setup venv
#   make play-hello_world      # render + play a song immediately
#   make preview-notturno_rhodes  # render + play a sample
#   make songs-wav             # render all songs to dist/wav/
#   make spotify               # render all songs to dist/flac/ for upload

PYTHON  ?= python3
VENV    := .venv
BIN     := $(VENV)/bin
CM      := $(BIN)/python -m code_music.cli
PLAY    := afplay          # macOS built-in. Linux: aplay. Replace as needed.

# ── Discover songs automatically ──────────────────────────────────────────────
SONGS      := $(wildcard songs/*.py)
SONG_NAMES := $(notdir $(basename $(SONGS)))

# ── Discover scales ───────────────────────────────────────────────────────────
SCALES      := $(wildcard scales/*.py)
SCALE_NAMES := $(notdir $(basename $(SCALES)))

# ── Discover samples across all subdirs ───────────────────────────────────────
SAMPLE_DIRS := bass brass chords drums edm ensemble highs instruments \
               jazz keyboards mood orchestral solo strings synths \
               techniques voices waves woodwinds
SAMPLE_PYS  := $(foreach d,$(SAMPLE_DIRS),$(wildcard samples/$(d)/*.py))
SAMPLE_NAMES := $(notdir $(basename $(SAMPLE_PYS)))

# ── Output path lists ─────────────────────────────────────────────────────────
WAV_SONGS    := $(addprefix dist/wav/,    $(addsuffix .wav,  $(SONG_NAMES)))
FLAC_SONGS   := $(addprefix dist/flac/,   $(addsuffix .flac, $(SONG_NAMES)))
MP3_SONGS    := $(addprefix dist/mp3/,    $(addsuffix .mp3,  $(SONG_NAMES)))
WAV_SCALES   := $(addprefix dist/scales/, $(addsuffix .wav,  $(SCALE_NAMES)))
WAV_SAMPLES  := $(addprefix dist/samples/, $(addsuffix .wav, $(SAMPLE_NAMES)))

.PHONY: all install dev lint test \
        songs-wav songs-flac songs-mp3 songs-all \
        samples scales spotify clean help \
        $(addprefix play-, $(SONG_NAMES)) \
        $(addprefix play-scale-, $(SCALE_NAMES)) \
        $(addprefix preview-, $(SAMPLE_NAMES))

# ── Setup ─────────────────────────────────────────────────────────────────────

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e ".[dev]" -q

dev: install
	@command -v ffmpeg >/dev/null 2>&1 \
		&& echo "ffmpeg found — MP3/OGG/FLAC export enabled" \
		|| echo "WARNING: ffmpeg not found — WAV only. Run: brew install ffmpeg"

# ── Quality ───────────────────────────────────────────────────────────────────

lint:
	$(BIN)/ruff check code_music tests songs samples scales

test:
	$(BIN)/pytest tests/ -v

# ── Render: songs ─────────────────────────────────────────────────────────────

dist/wav/%.wav: songs/%.py
	@mkdir -p dist/wav
	$(CM) $< -o $@

dist/flac/%.flac: songs/%.py
	@mkdir -p dist/flac
	$(CM) $< --flac -o $@

dist/mp3/%.mp3: songs/%.py
	@mkdir -p dist/mp3
	$(CM) $< --mp3 -o $@

songs-wav:  $(WAV_SONGS)
songs-flac: $(FLAC_SONGS)
songs-mp3:  $(MP3_SONGS)
songs-all:  songs-wav songs-flac songs-mp3

# ── Notation export ───────────────────────────────────────────────────────────
# LilyPond (.ly): compile to PDF with: lilypond dist/notation/<song>.ly
# ABC (.abc): paste into https://abc.rectanglered.com to render
# MusicXML (.xml): open in MuseScore, Sibelius, Dorico, Finale, Noteflight

LY_SONGS  := $(addprefix dist/notation/lily/, $(addsuffix .ly,  $(SONG_NAMES)))
ABC_SONGS := $(addprefix dist/notation/abc/,  $(addsuffix .abc, $(SONG_NAMES)))
XML_SONGS := $(addprefix dist/notation/xml/,  $(addsuffix .xml, $(SONG_NAMES)))

dist/notation/lily/%.ly: songs/%.py
	@mkdir -p dist/notation/lily
	$(BIN)/python -c "import importlib.util,sys; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_lilypond; export_lilypond(m.song,'$@')"
	@echo "Wrote $@  (compile: lilypond $@)"

dist/notation/abc/%.abc: songs/%.py
	@mkdir -p dist/notation/abc
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_abc; export_abc(m.song,'$@')"
	@echo "Wrote $@  (preview: https://abc.rectanglered.com)"

dist/notation/xml/%.xml: songs/%.py
	@mkdir -p dist/notation/xml
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_musicxml; export_musicxml(m.song,'$@')"
	@echo "Wrote $@  (open in MuseScore, Sibelius, Dorico, Finale)"

notation-lily: $(LY_SONGS)
notation-abc:  $(ABC_SONGS)
notation-xml:  $(XML_SONGS)
notation-all:  notation-lily notation-abc notation-xml

.PHONY: notation-lily notation-abc notation-xml notation-all

# ── Render: scales ───────────────────────────────────────────────────────────

dist/scales/%.wav: scales/%.py
	@mkdir -p dist/scales
	$(CM) $< -o $@

scales: $(WAV_SCALES)

# ── Play scales ───────────────────────────────────────────────────────────────
# Usage: make play-scale-major   make play-scale-blues_minor   etc.

define PLAY_SCALE_RULE
play-scale-$(1): dist/scales/$(1).wav
	$(PLAY) dist/scales/$(1).wav
endef
$(foreach s,$(SCALE_NAMES),$(eval $(call PLAY_SCALE_RULE,$(s))))

# ── Play songs ────────────────────────────────────────────────────────────────
# Render a song to dist/wav/ then play it immediately.
# Usage: make play-<song_name>   e.g.  make play-trance_odyssey
#
define PLAY_SONG_RULE
play-$(1): dist/wav/$(1).wav
	$(PLAY) dist/wav/$(1).wav
endef
$(foreach s,$(SONG_NAMES),$(eval $(call PLAY_SONG_RULE,$(s))))

# ── Render: samples ───────────────────────────────────────────────────────────
# One pattern rule per subdir — make needs explicit paths, not globs.

define SAMPLE_RENDER_RULE
dist/samples/%.wav: samples/$(1)/%.py
	@mkdir -p dist/samples
	$(CM) $$< -o $$@
endef
$(foreach d,$(SAMPLE_DIRS),$(eval $(call SAMPLE_RENDER_RULE,$(d))))

samples: $(WAV_SAMPLES)

# ── Preview samples ───────────────────────────────────────────────────────────
# Render a sample to dist/samples/ then play it immediately.
# Usage: make preview-<sample_name>   e.g.  make preview-notturno_rhodes
#
define PREVIEW_RULE
preview-$(1): dist/samples/$(1).wav
	$(PLAY) dist/samples/$(1).wav
endef
$(foreach s,$(SAMPLE_NAMES),$(eval $(call PREVIEW_RULE,$(s))))

# ── Spotify ───────────────────────────────────────────────────────────────────

spotify: songs-flac
	@echo ""
	@echo "Spotify-ready files in dist/flac/:"
	@ls -lh dist/flac/*.flac 2>/dev/null || echo "  (none — run: make songs-flac)"
	@echo ""
	@echo "Upload at https://artists.spotify.com  (min 30s, 44100 Hz stereo)"

# ── Convenience ───────────────────────────────────────────────────────────────

all: songs-all samples scales notation-all

clean:
	rm -rf dist/ .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null; true

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "code-music"
	@echo ""
	@echo "SETUP"
	@echo "  make install            create .venv, install deps"
	@echo "  make dev                install + check ffmpeg"
	@echo ""
	@echo "PLAY (render then play immediately)"
	@echo "  make play-<song>        render song to dist/wav/ and play"
	@echo "  make play-scale-<name>  render scale to dist/scales/ and play"
	@echo "  make preview-<sample>   render sample to dist/samples/ and play"
	@echo ""
	@echo "  Songs available:"
	@$(foreach s,$(SONG_NAMES),echo "    make play-$(s)";)
	@echo ""
	@echo "  Sample categories (use tab-complete or list-samples):"
	@echo "    make list-samples"
	@echo ""
	@echo "EXPORT"
	@echo "  make songs-wav          dist/wav/*.wav   (lossless PCM)"
	@echo "  make songs-flac         dist/flac/*.flac (lossless, Spotify)"
	@echo "  make songs-mp3          dist/mp3/*.mp3   (320kbps)"
	@echo "  make songs-all          all three formats"
	@echo "  make samples            dist/samples/*.wav (all samples)"
	@echo "  make scales             dist/scales/*.wav  (all scales, all keys)"
	@echo "  make notation-lily      dist/notation/lily/*.ly   (LilyPond source)"
	@echo "  make notation-abc       dist/notation/abc/*.abc   (ABC notation)"
	@echo "  make notation-xml       dist/notation/xml/*.xml   (MusicXML)"
	@echo "  make notation-all       all three notation formats"
	@echo "  make spotify            songs-flac + upload instructions"
	@echo "  make all                everything"
	@echo ""
	@echo "QUALITY"
	@echo "  make lint               ruff check"
	@echo "  make test               pytest"
	@echo "  make clean              remove dist/ and caches"
	@echo ""

list-samples:
	@echo ""
	@$(foreach s,$(SAMPLE_NAMES),echo "  make preview-$(s)";)
	@echo ""

.PHONY: list-samples
