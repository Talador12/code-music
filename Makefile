################################################################################
#                              code-music                                      #
#         Code-generated music. Write Python, hear sound, export audio.        #
#         Requires: Python 3.11+  |  FLAC/MP3/OGG: brew install ffmpeg         #
################################################################################

SHELL  := /bin/bash
PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin
CM     := $(BIN)/python -m code_music.cli
PLAY   := afplay   # macOS. Linux: swap to `aplay`

################################################################################
#                               Auto-discovery                                 #
################################################################################

SONGS        := $(filter-out songs/_%.py, $(wildcard songs/*.py))
SONG_NAMES   := $(notdir $(basename $(SONGS)))

SCALES_PY    := $(filter-out scales/_%.py, $(wildcard scales/*.py))
SCALE_NAMES  := $(notdir $(basename $(SCALES_PY)))

SAMPLE_DIRS  := bass brass chords drums edm ensemble highs instruments \
                jazz keyboards mood orchestral solo strings synths \
                techniques voices waves woodwinds
SAMPLE_PYS   := $(filter-out %/_%.py,$(foreach d,$(SAMPLE_DIRS),$(wildcard samples/$(d)/*.py)))
SAMPLE_NAMES := $(notdir $(basename $(SAMPLE_PYS)))

ALBUM_STEMS  := ambient_cinematic anthology classical_orchestral cosmic_electro \
                country_americana drum_and_bass dubstep edm_festival edm_progressive \
                folk_acoustic funk_disco hiphop_lofi indie_alternative jazz_neosoul \
                latin metal parody pop rnb_soul rock_prog techno videogame_anime \
                world_experimental

################################################################################
#                               Output paths                                   #
################################################################################

WAV_SONGS    := $(addprefix dist/wav/,          $(addsuffix .wav,  $(SONG_NAMES)))
FLAC_SONGS   := $(addprefix dist/flac/,         $(addsuffix .flac, $(SONG_NAMES)))
MP3_SONGS    := $(addprefix dist/mp3/,          $(addsuffix .mp3,  $(SONG_NAMES)))
WAV_SCALES   := $(addprefix dist/scales/,       $(addsuffix .wav,  $(SCALE_NAMES)))
WAV_SAMPLES  := $(addprefix dist/samples/,      $(addsuffix .wav,  $(SAMPLE_NAMES)))
LY_SONGS     := $(addprefix dist/notation/lily/, $(addsuffix .ly,  $(SONG_NAMES)))
ABC_SONGS    := $(addprefix dist/notation/abc/,  $(addsuffix .abc, $(SONG_NAMES)))
XML_SONGS    := $(addprefix dist/notation/xml/,  $(addsuffix .xml, $(SONG_NAMES)))

################################################################################
#                                  Config                                      #
################################################################################

.DEFAULT_GOAL := help

.PHONY: help all install dev lint test clean \
        songs-wav songs-flac songs-mp3 songs-all \
        samples scales spotify export-spotify \
        notation-lily notation-abc notation-xml notation-all \
        vibe vibe-chill vibe-energizing vibe-alluring vibe-powerful \
        play-scales play-scales-arp play-scales-group play-scales-arp-group \
        list-scales list-samples list-songs list-albums new-song watch \
        albums export-song \
        $(addprefix play-,            $(SONG_NAMES)) \
        $(addprefix play-scale-,     $(SCALE_NAMES)) \
        $(addprefix preview-,        $(SAMPLE_NAMES)) \
        $(addprefix album-,          $(ALBUM_STEMS)) \
        $(addprefix play-album-,     $(ALBUM_STEMS))

################################################################################
#                               Utility                                        #
################################################################################

help: ## [Utility] Show this help
	@grep -E '^[a-zA-Z_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-28s\033[0m %s\n", $$1, $$2}'

################################################################################
#                                 Setup                                        #
################################################################################

install: ## [Setup] Create .venv and install all dependencies
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e ".[dev]" -q

dev: install ## [Setup] install + check for ffmpeg (required for MP3/FLAC/OGG)
	@command -v ffmpeg >/dev/null 2>&1 \
		&& echo "ffmpeg found — MP3/OGG/FLAC export enabled" \
		|| echo "WARNING: ffmpeg not found — WAV only. Fix: brew install ffmpeg"

################################################################################
#                           [VIBE] Just listen                                 #
################################################################################

vibe: ## [Vibe] Play all songs grouped by mood (chill / energizing / alluring / powerful)
	$(BIN)/python -m scripts.play_vibe

vibe-chill: ## [Vibe] Play chill songs — slow, atmospheric, late night
	$(BIN)/python -m scripts.play_vibe --vibe chill

vibe-energizing: ## [Vibe] Play energizing songs — driving, uplifting, forward motion
	$(BIN)/python -m scripts.play_vibe --vibe energizing

vibe-alluring: ## [Vibe] Play alluring songs — dark, mysterious, pulls you in
	$(BIN)/python -m scripts.play_vibe --vibe alluring

vibe-powerful: ## [Vibe] Play powerful songs — heavy, orchestral, impact
	$(BIN)/python -m scripts.play_vibe --vibe powerful

list-songs: ## [Vibe] List all songs with vibe descriptions
	$(BIN)/python -m scripts.play_vibe --list

spotify: ## [Vibe] Authorize Spotify + read your listening data → styles/my_taste.py
	@if [ -f .spotify_token ]; then \
		echo "Token found — reading your Spotify data..."; \
		$(BIN)/python scripts/spotify_taste.py; \
	else \
		echo "No token — authorizing first (needs SPOTIFY_CLIENT_ID + SECRET)..."; \
		$(BIN)/python scripts/spotify_auth.py && $(BIN)/python scripts/spotify_taste.py; \
	fi

# Per-song play rules (generated): make play-<song_name>
define PLAY_SONG_RULE
play-$(1): dist/wav/$(1).wav ## [Vibe] Render and play $(1)
	$(PLAY) dist/wav/$(1).wav
endef
$(foreach s,$(SONG_NAMES),$(eval $(call PLAY_SONG_RULE,$(s))))

################################################################################
#                          [CREATE] Make music                                 #
################################################################################

new-song: ## [Create] Copy a genre template. STYLE=edm|jazz|rock|ambient|hiphop (default: beginner)
	@read -p "Song name (no spaces, e.g. my_track): " name; \
	style=$${STYLE:-beginner}; \
	tmpl="songs/_template_$${style}.py"; \
	if [ ! -f "$$tmpl" ]; then \
		echo "Available styles: beginner edm jazz rock ambient hiphop"; \
		echo "Usage: make new-song STYLE=jazz"; \
		exit 1; \
	fi; \
	cp "$$tmpl" "songs/$$name.py"; \
	echo "Created songs/$$name.py from $$style template — edit it, then: make play-$$name"

watch: ## [Create] Live coding — re-renders and plays on every file save (SONG=name)
	@test -n "$(SONG)" || (echo "Usage: make watch SONG=my_track"; exit 1)
	$(CM) songs/$(SONG).py --watch

export-song: ## [Create] Export one song to WAV + FLAC + MP3 (SONG=name)
	@test -n "$(SONG)" || (echo "Usage: make export-song SONG=trance_odyssey"; exit 1)
	@mkdir -p dist/wav dist/flac dist/mp3
	$(CM) songs/$(SONG).py           -o dist/wav/$(SONG).wav
	$(CM) songs/$(SONG).py --flac    -o dist/flac/$(SONG).flac
	$(CM) songs/$(SONG).py --mp3     -o dist/mp3/$(SONG).mp3
	@echo "Exported: dist/{wav,flac,mp3}/$(SONG)"

export-spotify: songs-flac ## [Create] Render all songs to dist/flac/ for Spotify for Artists upload
	@echo ""; \
	echo "Spotify-ready files in dist/flac/:"; \
	ls -lh dist/flac/*.flac 2>/dev/null || echo "  (none)"; \
	echo ""; \
	echo "Upload at: https://artists.spotify.com  (Music → Upload Track)"; \
	echo "Min requirements: 30s, 44100 Hz, stereo. FLAC preferred."

samples: $(WAV_SAMPLES) ## [Create] Render all instrument/technique sample previews → dist/samples/

list-samples: ## [Create] List all available sample preview names
	@echo ""; $(foreach s,$(SAMPLE_NAMES),echo "  make preview-$(s)";) echo ""

gen-album: ## [Create] Generate a procedural album (GENRE=ambient SEED=42 TRACKS=5)
	$(BIN)/python scripts/gen_album.py --genre $(or $(GENRE),ambient) --seed $(or $(SEED),42) --tracks $(or $(TRACKS),5)

list-albums: ## [Create] List all genre albums with track counts and render status
	$(BIN)/python -m albums.render --list

albums: ## [Create] Render all genre albums (WAV + FLAC + MP3 + liner notes + playlist)
	$(BIN)/python -m albums.render --all

# Per-album render + play rules (generated)
# make album-<name>       → render to dist/albums/<name>/
# make play-album-<name>  → render then play all tracks back-to-back
define ALBUM_RULE
album-$(1): ## [Create] Render album: $(1)
	$(BIN)/python -m albums.render $(1)

play-album-$(1): album-$(1) ## [Vibe] Render and play album: $(1)
	@for f in dist/albums/$(1)/*.wav; do \
		echo "  ▶ $$$${f##*/}"; \
		$(PLAY) "$$$$f"; \
	done
endef
$(foreach a,$(ALBUM_STEMS),$(eval $(call ALBUM_RULE,$(a))))

# Per-sample preview rules (generated): make preview-<sample_name>
define PREVIEW_RULE
preview-$(1): dist/samples/$(1).wav ## [Create] Render and play sample: $(1)
	$(PLAY) dist/samples/$(1).wav
endef
$(foreach s,$(SAMPLE_NAMES),$(eval $(call PREVIEW_RULE,$(s))))

################################################################################
#                         [EXPLORE] Scales & theory                            #
################################################################################

play-scales: scales ## [Explore] Play the full guided scale set (all 12 keys) with name + progress bar
	$(BIN)/python -m scripts.play_scales

play-scales-arp: ## [Explore] Play all scales as 1-3-5-8 arpeggios (renders on the fly)
	$(BIN)/python -m scripts.play_scales --arp

play-scales-group: ## [Explore] Play one group of scales — GROUP=blues|world|bebop|symmetric|...
	@test -n "$(GROUP)" || (echo "Usage: make play-scales-group GROUP=world"; exit 1)
	$(BIN)/python -m scripts.play_scales --group $(GROUP)

play-scales-arp-group: ## [Explore] Play one group as arpeggios — GROUP=blues|world|bebop|...
	@test -n "$(GROUP)" || (echo "Usage: make play-scales-arp-group GROUP=blues"; exit 1)
	$(BIN)/python -m scripts.play_scales --group $(GROUP) --arp

list-scales: ## [Explore] List all scale demos with render status
	$(BIN)/python -m scripts.play_scales --list

scales: $(WAV_SCALES) ## [Explore] Render all scale demos → dist/scales/

notation-abc: $(ABC_SONGS) ## [Explore] Export all songs as ABC notation — paste into abc.rectanglered.com
notation-lily: $(LY_SONGS) ## [Explore] Export all songs as LilyPond — compile: lilypond <file>.ly → PDF
notation-xml: $(XML_SONGS) ## [Explore] Export all songs as MusicXML — open in MuseScore / Sibelius / Dorico
notation-all: notation-lily notation-abc notation-xml ## [Explore] Export all songs in all notation formats

# Per-scale play rules (generated): make play-scale-<scale_name>
define PLAY_SCALE_RULE
play-scale-$(1): dist/scales/$(1).wav ## [Explore] Play scale: $(1) (all 12 keys)
	$(PLAY) dist/scales/$(1).wav
endef
$(foreach s,$(SCALE_NAMES),$(eval $(call PLAY_SCALE_RULE,$(s))))

# Friendly alias for internal reference scale file.
play-scale-circle_of_fifths: dist/scales/circle_of_fifths.wav ## [Explore] Play reference: circle of fifths major scales
	$(PLAY) dist/scales/circle_of_fifths.wav

################################################################################
#                           [Dev] Build & test                                 #
################################################################################

lint: ## [Dev] Run ruff check on all Python files
	$(BIN)/ruff check code_music tests songs samples scales scripts albums

test: ## [Dev] Run pytest test suite
	$(BIN)/pytest tests/ -v

songs-wav: $(WAV_SONGS) ## [Dev] Render all songs → dist/wav/ (lossless PCM)
songs-flac: $(FLAC_SONGS) ## [Dev] Render all songs → dist/flac/ (lossless compressed, Spotify preferred)
songs-mp3: $(MP3_SONGS) ## [Dev] Render all songs → dist/mp3/ (lossy 320kbps)
songs-all: songs-wav songs-flac songs-mp3 ## [Dev] Render all songs in all audio formats

all: songs-all samples scales notation-all albums ## [Dev] Render everything — audio, scales, notation, albums

clean: ## [Dev] Remove dist/ and all caches
	rm -rf dist/ .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null; true

################################################################################
#                          Pattern / render rules                              #
################################################################################

dist/wav/%.wav: songs/%.py
	@mkdir -p dist/wav
	$(CM) $< -o $@

dist/flac/%.flac: songs/%.py
	@mkdir -p dist/flac
	$(CM) $< --flac -o $@

dist/mp3/%.mp3: songs/%.py
	@mkdir -p dist/mp3
	$(CM) $< --mp3 -o $@

dist/scales/%.wav: scales/%.py
	@mkdir -p dist/scales
	$(CM) $< -o $@

dist/scales/circle_of_fifths.wav: scales/_circle_of_fifths.py
	@mkdir -p dist/scales
	$(CM) $< -o $@

define SAMPLE_RENDER_RULE
dist/samples/%.wav: samples/$(1)/%.py
	@mkdir -p dist/samples
	$(CM) $$< -o $$@
endef
$(foreach d,$(SAMPLE_DIRS),$(eval $(call SAMPLE_RENDER_RULE,$(d))))

dist/notation/lily/%.ly: songs/%.py
	@mkdir -p dist/notation/lily
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_lilypond; export_lilypond(m.song,'$@')"

dist/notation/abc/%.abc: songs/%.py
	@mkdir -p dist/notation/abc
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_abc; export_abc(m.song,'$@')"

dist/notation/xml/%.xml: songs/%.py
	@mkdir -p dist/notation/xml
	$(BIN)/python -c "import importlib.util; spec=importlib.util.spec_from_file_location('s','$<'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); from code_music.notation import export_musicxml; export_musicxml(m.song,'$@')"

covers: ## [Create] Generate album cover art for all albums → dist/covers/
	@command -v python3 -c "import matplotlib" 2>/dev/null || $(BIN)/pip install matplotlib -q
	$(BIN)/python scripts/make_cover.py --all

cover-%: ## [Create] Generate cover art for one album (e.g. make cover-anthology)
	$(BIN)/python scripts/make_cover.py --album $*


midi-to-song: ## [Create] Convert a MIDI file to a code-music song script (MIDI=file.mid)
	@test -n "$(MIDI)" || (echo "Usage: make midi-to-song MIDI=file.mid OUT=songs/name.py"; exit 1)
	$(BIN)/python scripts/midi_to_song.py "$(MIDI)" $(if $(OUT),--out $(OUT),)


waveforms: ## [Create] Generate waveform PNG for all rendered songs → dist/waveforms/
	@command -v python3 -c "import matplotlib" 2>/dev/null || $(BIN)/pip install matplotlib -q
	$(BIN)/python scripts/make_waveform.py --all

waveform-%: ## [Create] Generate waveform PNG for one song (e.g. make waveform-trance_odyssey)
	$(BIN)/python scripts/make_waveform.py dist/wav/$*.wav

samplers: ## [Create] Build 2-min sampler preview for all albums → dist/samplers/
	$(BIN)/python scripts/make_sampler.py --all

sampler-%: ## [Create] Build sampler for one album (e.g. make sampler-jazz_neosoul)
	$(BIN)/python scripts/make_sampler.py --album $*


distrokid-prep: ## [Create] Prepare all albums for DistroKid upload → dist/distrokid/
	$(BIN)/python scripts/distrokid_prep.py --all

distrokid-prep-%: ## [Create] Prepare one album for DistroKid (e.g. make distrokid-prep-jazz_neosoul)
	$(BIN)/python scripts/distrokid_prep.py --album $*


fingerprint: ## [Dev] Save audio fingerprints of all rendered songs → .fingerprints.json
	$(BIN)/python scripts/fingerprint.py --snapshot

fingerprint-check: ## [Dev] Compare current renders against saved fingerprints (regression test)
	$(BIN)/python scripts/fingerprint.py --check


bpm-tap: ## [Explore] Tap Enter to the beat — shows running BPM average
	$(BIN)/python scripts/bpm_tap.py


playlist: ## [Create] Generate playlists (M3U + JSON + TXT) for all songs → dist/playlists/
	$(BIN)/python scripts/make_playlist.py

playlist-%: ## [Create] Generate playlist for one vibe (e.g. make playlist-chill)
	$(BIN)/python scripts/make_playlist.py --vibe $*


check: lint test ## [Dev] Run lint + test in one command
	@echo ""
	@echo "$(shell printf '\033[92m')All checks passed.$(shell printf '\033[0m')"


stats: ## [Dev] Show song statistics — total duration, BPM distribution, genres
	$(BIN)/python scripts/stats.py


stereo-images: ## [Dev] Generate stereo field visualization for all rendered songs
	$(BIN)/python scripts/stereo_imager.py --all

stereo-image-%: ## [Dev] Generate stereo image for one song (e.g. make stereo-image-trance_odyssey)
	$(BIN)/python scripts/stereo_imager.py dist/wav/$*.wav


pages-url: ## [Dev] Show the GitHub Pages URL
	@echo "https://talador12.github.io/code-music/"


render-one: ## [Dev] Render one song to all formats (WAV+FLAC+MP3). Usage: make render-one SONG=name
	@test -n "$(SONG)" || (echo "Usage: make render-one SONG=trance_odyssey"; exit 1)
	@mkdir -p dist/wav dist/flac dist/mp3
	$(CM) songs/$(SONG).py -o dist/wav/$(SONG).wav
	$(CM) songs/$(SONG).py --flac -o dist/flac/$(SONG).flac 2>/dev/null || echo "  (FLAC skipped — install ffmpeg)"
	$(CM) songs/$(SONG).py --mp3 -o dist/mp3/$(SONG).mp3 2>/dev/null || echo "  (MP3 skipped — install ffmpeg)"
