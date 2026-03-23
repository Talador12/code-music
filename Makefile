# code-music Makefile
# Usage: make <target>
# Requires: Python 3.11+, pip

PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin
PIP    := $(BIN)/pip

.PHONY: install dev lint test run-hello run-lofi run-prog clean

# Install runtime deps
install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e ".[dev]"

# Install + ffmpeg check (needed for MP3 export)
dev: install
	@command -v ffmpeg >/dev/null 2>&1 || echo "WARNING: ffmpeg not found — MP3 export disabled (brew install ffmpeg)"

lint:
	$(BIN)/ruff check code_music tests examples

test:
	$(BIN)/pytest tests/ -v

# Render example songs to output/
run-hello:
	$(BIN)/code-music examples/hello_world.py -o output/hello_world.wav

run-lofi:
	$(BIN)/code-music examples/lo_fi_loop.py -o output/lo_fi_loop.wav

run-prog:
	$(BIN)/code-music examples/prog_rock.py -o output/prog_rock.wav

# Render all examples
render-all: run-hello run-lofi run-prog

clean:
	rm -rf $(VENV) output/ .pytest_cache __pycache__ **/__pycache__ *.egg-info dist build
