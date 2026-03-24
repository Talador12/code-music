# code-music Makefile
# Run `make help` to see commands grouped by audience.
# Requires: Python 3.11+  |  MP3/OGG/FLAC: brew install ffmpeg

PYTHON  ?= python3
VENV    := .venv
BIN     := $(VENV)/bin
CM      := $(BIN)/python -m code_music.cli
PLAY    := afplay   # macOS. Linux: swap to `aplay`

# ── Auto-discovery ────────────────────────────────────────────────────────────
SONGS        := $(filter-out songs/_%.py, $(wildcard songs/*.py))
SONG_NAMES   := $(notdir $(basename $(SONGS)))

SCALES_PY    := $(wildcard scales/*.py)
SCALE_NAMES  := $(notdir $(basename $(SCALES_PY)))

SAMPLE_DIRS  := bass brass chords drums edm ensemble highs instruments \
                jazz keyboards mood orchestral solo strings synths \
                techniques voices waves woodwinds
SAMPLE_PYS   := $(foreach d,$(SAMPLE_DIRS),$(wildcard samples/$(d)/*.py))
SAMPLE_NAMES := $(notdir $(basename $(SAMPLE_PYS)))

# ── Output paths ──────────────────────────────────────────────────────────────
WAV_SONGS    := $(addprefix dist/wav/,         $(addsuffix .wav,  $(SONG_NAMES)))
FLAC_SONGS   := $(addprefix dist/flac/,        $(addsuffix .flac, $(SONG_NAMES)))
MP3_SONGS    := $(addprefix dist/mp3/,         $(addsuffix .mp3,  $(SONG_NAMES)))
WAV_SCALES   := $(addprefix dist/scales/,      $(addsuffix .wav,  $(SCALE_NAMES)))
WAV_SAMPLES  := $(addprefix dist/samples/,     $(addsuffix .wav,  $(SAMPLE_NAMES)))
LY_SONGS     := $(addprefix dist/notation/lily/, $(addsuffix .ly,  $(SONG_NAMES)))
ABC_SONGS    := $(addprefix dist/notation/abc/,  $(addsuffix .abc, $(SONG_NAMES)))
XML_SONGS    := $(addprefix dist/notation/xml/,  $(addsuffix .xml, $(SONG_NAMES)))

.PHONY: all install dev lint test clean help \
        songs-wav songs-flac songs-mp3 songs-all \
        samples scales spotify export-spotify \
        notation-lily notation-abc notation-xml notation-all \
        vibe vibe-chill vibe-energizing vibe-alluring vibe-powerful \
        play-scales play-scales-arp play-scales-group play-scales-arp-group \
        list-scales list-samples list-songs \
        $(addprefix play-,         $(SONG_NAMES)) \
        $(addprefix play-scale-,   $(SCALE_NAMES)) \
        $(addprefix preview-,      $(SAMPLE_NAMES))

# =============================================================================
# [SETUP]  First-time setup
# =============================================================================

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e ".[dev]" -q

dev: install
	@command -v ffmpeg >/dev/null 2>&1 \
		&& echo "ffmpeg found — MP3/OGG/FLAC export enabled" \
		|| echo "WARNING: ffmpeg not found — WAV only. Fix: brew install ffmpeg"

# =============================================================================
# [VIBE]  Just listen. No music knowledge needed.
# =============================================================================

# Play all songs grouped by mood — chill / energizing / alluring / powerful
# Spotify profile: authorize + read your listening data in one command
# Run once: set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET first
# (get them at https://developer.spotify.com/dashboard — takes 3 minutes)
spotify:
	@if [ -f .spotify_token ]; then \
		echo "Token found — reading your Spotify data..."; \
		$(BIN)/python scripts/spotify_taste.py; \
	else \
		echo "No token yet — authorizing first..."; \
		$(BIN)/python scripts/spotify_auth.py && $(BIN)/python scripts/spotify_taste.py; \
	fi

# Export all songs to Spotify-ready FLAC
export-spotify: songs-flac
	@echo ""
	@echo "Spotify-ready FLAC files in dist/flac/:"
	@ls -lh dist/flac/*.flac 2>/dev/null || echo "  (none — run: make songs-flac)"
	@echo ""
	@echo "Upload at: https://artists.spotify.com  (Music → Upload Track)"
	@echo "Minimum: 30s, 44100 Hz, stereo."

.PHONY: spotify export-spotify

vibe:
	$(BIN)/python -m scripts.play_vibe

vibe-chill:
	$(BIN)/python -m scripts.play_vibe --vibe chill

vibe-energizing:
	$(BIN)/python -m scripts.play_vibe --vibe energizing

vibe-alluring:
	$(BIN)/python -m scripts.play_vibe --vibe alluring

vibe-powerful:
	$(BIN)/python -m scripts.play_vibe --vibe powerful

# Play one specific song (renders first if needed)
define PLAY_SONG_RULE
play-$(1): dist/wav/$(1).wav
	$(PLAY) dist/wav/$(1).wav
endef
$(foreach s,$(SONG_NAMES),$(eval $(call PLAY_SONG_RULE,$(s))))

# List all songs with their vibe tag
list-songs:
	$(BIN)/python -m scripts.play_vibe --list

# =============================================================================
# [CREATE]  Make music. Start here if you're new.
# =============================================================================

# Copy the beginner template and open it
new-song:
	@read -p "Song name (no spaces, e.g. my_track): " name; \
	cp songs/_template_beginner.py songs/$$name.py; \
	echo "Created songs/$$name.py — edit it, then: make play-$$name"

# Render + play — re-renders every time you save the file (live coding)
watch:
	@test -n "$(SONG)" || (echo "Usage: make watch SONG=my_track"; exit 1)
	$(CM) songs/$(SONG).py --watch

# Render a song to WAV and play it
dist/wav/%.wav: songs/%.py
	@mkdir -p dist/wav
	$(CM) $< -o $@

# Export a single song to all formats
export-song:
	@test -n "$(SONG)" || (echo "Usage: make export-song SONG=trance_odyssey"; exit 1)
	$(CM) songs/$(SONG).py           -o dist/wav/$(SONG).wav
	$(CM) songs/$(SONG).py --flac    -o dist/flac/$(SONG).flac
	$(CM) songs/$(SONG).py --mp3     -o dist/mp3/$(SONG).mp3
	@echo ""
	@echo "Exported to dist/wav/, dist/flac/, dist/mp3/"

# Render all songs (three formats)
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

# (export-spotify is defined above, near the spotify auth targets)

# Preview an instrument sample — hear what a preset sounds like
define PREVIEW_RULE
preview-$(1): dist/samples/$(1).wav
	$(PLAY) dist/samples/$(1).wav
endef
$(foreach s,$(SAMPLE_NAMES),$(eval $(call PREVIEW_RULE,$(s))))

# Render all samples
define SAMPLE_RENDER_RULE
dist/samples/%.wav: samples/$(1)/%.py
	@mkdir -p dist/samples
	$(CM) $$< -o $$@
endef
$(foreach d,$(SAMPLE_DIRS),$(eval $(call SAMPLE_RENDER_RULE,$(d))))

samples: $(WAV_SAMPLES)

# List all available samples
list-samples:
	@echo ""
	@$(foreach s,$(SAMPLE_NAMES),echo "  make preview-$(s)";)
	@echo ""

# =============================================================================
# [EXPLORE]  Scales, arpeggios, samples — expand your musical vocabulary.
# =============================================================================

# Render all scales (32 types × 12 keys)
dist/scales/%.wav: scales/%.py
	@mkdir -p dist/scales
	$(CM) $< -o $@

scales: $(WAV_SCALES)

# Play one scale by name
define PLAY_SCALE_RULE
play-scale-$(1): dist/scales/$(1).wav
	$(PLAY) dist/scales/$(1).wav
endef
$(foreach s,$(SCALE_NAMES),$(eval $(call PLAY_SCALE_RULE,$(s))))

# Play all scales with name + in-place progress bar
play-scales: scales
	$(BIN)/python -m scripts.play_scales

# Play all scales as arpeggios (1-3-5-8 broken chord pattern)
play-scales-arp:
	$(BIN)/python -m scripts.play_scales --arp

# Play one group of scales  (GROUP=blues|world|bebop|symmetric|diatonic|...)
play-scales-group:
	@test -n "$(GROUP)" || (echo "Usage: make play-scales-group GROUP=world"; exit 1)
	$(BIN)/python -m scripts.play_scales --group $(GROUP)

# Same group, arpeggio mode
play-scales-arp-group:
	@test -n "$(GROUP)" || (echo "Usage: make play-scales-arp-group GROUP=blues"; exit 1)
	$(BIN)/python -m scripts.play_scales --group $(GROUP) --arp

# List all scales with render status
list-scales:
	$(BIN)/python -m scripts.play_scales --list

# Export sheet music for all songs
notation-lily: $(LY_SONGS)
notation-abc:  $(ABC_SONGS)
notation-xml:  $(XML_SONGS)
notation-all:  notation-lily notation-abc notation-xml

dist/notation/lily/%.ly: songs/%.py
	@mkdir -p dist/notation/lily
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_lilypond; export_lilypond(m.song,'$@')"
	@echo "  → $@  (compile: lilypond $@)"

dist/notation/abc/%.abc: songs/%.py
	@mkdir -p dist/notation/abc
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_abc; export_abc(m.song,'$@')"
	@echo "  → $@  (preview: https://abc.rectanglered.com)"

dist/notation/xml/%.xml: songs/%.py
	@mkdir -p dist/notation/xml
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_musicxml; export_musicxml(m.song,'$@')"
	@echo "  → $@  (open in MuseScore, Sibelius, Dorico, Finale)"

# =============================================================================
# [ALBUMS]  Genre albums + The Anthology
# =============================================================================

ALBUM_STEMS := ambient_cinematic anthology classical_orchestral cosmic_electro \
               country_americana drum_and_bass dubstep edm_festival edm_progressive \
               folk_acoustic funk_disco hiphop_lofi indie_alternative jazz_neosoul \
               latin metal parody pop rnb_soul rock_prog techno videogame_anime \
               world_experimental

# Render one album (WAV + FLAC + MP3 + liner notes + M3U playlist)
# Usage: make album-edm_progressive
define ALBUM_RULE
album-$(1):
	$(BIN)/python -m albums.render $(1)
endef
$(foreach a,$(ALBUM_STEMS),$(eval $(call ALBUM_RULE,$(a))))

# Render all albums
albums:
	$(BIN)/python -m albums.render --all

# List albums with render status
list-albums:
	$(BIN)/python -m albums.render --list

.PHONY: albums list-albums \
        $(addprefix album-, $(ALBUM_STEMS))

# =============================================================================
# [DEV]  Build, test, lint, export everything.
# =============================================================================

lint:
	$(BIN)/ruff check code_music tests songs samples scales scripts albums

test:
	$(BIN)/pytest tests/ -v

# Render everything to every format
all: songs-all samples scales notation-all albums

clean:
	rm -rf dist/ .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null; true

# =============================================================================
# HELP
# =============================================================================

help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║                        code-music                               ║"
	@echo "║          Code-generated music. Run make help for anything.      ║"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  First time?  →  make dev"
	@echo ""
	@echo "┌─ [VIBE] Just listen ──────────────────────────────────────────────"
	@echo "│"
	@echo "│  make vibe                  Play all songs grouped by mood"
	@echo "│  make vibe-chill            Slow, atmospheric, late night"
	@echo "│  make vibe-energizing       Driving, uplifting, forward motion"
	@echo "│  make vibe-alluring         Dark, mysterious, pulls you in"
	@echo "│  make vibe-powerful         Heavy, orchestral, impact"
	@echo "│  make list-songs            See all songs with descriptions"
	@echo "│  make spotify               Authorize + read your Spotify listening data"
	@echo "│    → writes styles/my_taste.py with your top artists, genres, playlists"
	@echo "│    → requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars"
	@echo "│    → get them at https://developer.spotify.com/dashboard (3 min setup)"
	@echo "│"
	@echo "│  make play-<song>           Play one song directly"
	@$(foreach s,$(filter-out _template_beginner,$(SONG_NAMES)),echo "│    make play-$(s)";)
	@echo "│"
	@echo "├─ [CREATE] Make music ─────────────────────────────────────────────"
	@echo "│"
	@echo "│  make new-song              Copy beginner template, ready to edit"
	@echo "│  make watch SONG=my_track   Live coding — re-renders on each save"
	@echo "│  make export-song SONG=x    Export one song to WAV + FLAC + MP3"
	@echo "│  make export-spotify        Render all songs → dist/flac/ (upload-ready)"
	@echo "│"
	@echo "│  make preview-<sample>      Hear an instrument or technique"
	@echo "│  make samples               Render all 100+ sample previews"
	@echo "│  make list-samples          List every available sample"
	@echo "│"
	@echo "│  make list-albums           List all 22 genre albums"
	@echo "│  make album-<name>          Render one album (WAV+FLAC+MP3+liner notes)"
	@echo "│"
	@echo "│  Electronic:  edm_progressive  edm_festival  cosmic_electro"
	@echo "│               techno  dubstep  drum_and_bass  ambient_cinematic"
	@echo "│  Jazz/Soul:   jazz_neosoul  rnb_soul  funk_disco"
	@echo "│  Rock:        rock_prog  indie_alternative  metal"
	@echo "│  Classical:   classical_orchestral"
	@echo "│  Other:       hiphop_lofi  folk_acoustic  latin  pop"
	@echo "│               world_experimental  country_americana"
	@echo "│  Special:     videogame_anime  anthology  parody"
	@echo "│"
	@echo "│  make albums                Render all 22 albums"
	@echo "│"
	@echo "├─ [EXPLORE] Scales, samples & sheet music ────────────────────────"
	@echo "│"
	@echo "│  make play-scales           All 32 scales, all 12 keys, with labels"
	@echo "│  make play-scales-arp       Same scales as 1-3-5-8 arpeggios"
	@echo "│  make play-scales-group GROUP=<g>   One group of scales"
	@echo "│    Groups: diatonic  minor  pentatonic  blues  symmetric"
	@echo "│            bebop  modal_jazz  world  reference"
	@echo "│  make play-scale-<name>     One scale by name"
	@echo "│  make list-scales           List all 32 scales with status"
	@echo "│"
	@echo "│  make notation-abc          Sheet music → ABC (browser preview)"
	@echo "│  make notation-lily         Sheet music → LilyPond (→ PDF)"
	@echo "│  make notation-xml          Sheet music → MusicXML (MuseScore etc)"
	@echo "│  make notation-all          All three notation formats"
	@echo "│"
	@echo "│  make play-scale-major           make play-scale-blues_minor"
	@echo "│  make play-scale-dorian          make play-scale-hungarian_minor"
	@echo "│  make play-scale-whole_tone      make play-scale-super_locrian"
	@echo "│"
	@echo "├─ [DEV] Build & test ──────────────────────────────────────────────"
	@echo "│"
	@echo "│  make dev                   Create .venv, install deps, check ffmpeg"
	@echo "│  make install               Create .venv and install deps only"
	@echo "│  make lint                  ruff check all Python"
	@echo "│  make test                  pytest (213 tests)"
	@echo "│  make songs-wav             Render all songs → dist/wav/"
	@echo "│  make songs-flac            Render all songs → dist/flac/"
	@echo "│  make songs-mp3             Render all songs → dist/mp3/"
	@echo "│  make songs-all             All three audio formats"
	@echo "│  make scales                Render all 32 scales → dist/scales/"
	@echo "│  make samples               Render all samples → dist/samples/"
	@echo "│  make all                   Everything: audio + scales + notation"
	@echo "│  make clean                 Remove dist/ and caches"
	@echo "│"
	@echo "│  Docs:  docs/for_developers.md"
	@echo "│  Tests: .venv/bin/pytest tests/ -v"
	@echo "│  CI:    .github/workflows/ci.yml"
	@echo "│"
	@echo "└───────────────────────────────────────────────────────────────────"
	@echo ""
