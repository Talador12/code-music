# Strudel + Algorave integration plan

## Why this exists

[Switch Angel](https://www.youtube.com/@Switch-Angel) makes high-energy trance with [Strudel](https://strudel.cc), the JavaScript live-coding language for music (Strudel is the official browser port of [TidalCycles](https://tidalcycles.org)). Her tag set is `#livecode #algorave #strudelnotstrudel`. From her [Night Friends](https://www.youtube.com/watch?v=BWLFus_LaCs) video description:

> I created an ascii track sequencer in Strudel for this song that I am excited to show, which I am using here while tweaking params!

That single sentence captures the gap between code-music and the Strudel ecosystem. code-music is an excellent **offline** music engine (write a script, render to FLAC, upload to Spotify) but the algorave aesthetic is **live**: code is the instrument, parameters are tweaked while a pattern executes, and the visual representation of the pattern (her ASCII tracker) is part of the performance.

This plan brings the best of Strudel into code-music without breaking the offline-render simplicity that already works.

## What Strudel actually is

Three things, layered:

1. **Mini-notation** - a string grammar for rhythm + pitch. `"c3 [eb3 g3] ~ bb3*2"`. Ten or so operators in total.
2. **Pattern functions** - methods chained off a Pattern that transform it in time (`fast, slow, rev, every, struct, mask, chunk, ply, swing, euclid, ...`). About 80 of them.
3. **Audio engine** - a WebAudio synth + sample player that renders patterns in real time.

Patterns in Strudel are not flat event lists, they are **functions of time** over `[0, 1)` cycles. That is the deep idea worth porting. Everything else is grammar and ergonomics.

## Feature gap analysis

### Mini-notation grammar (Strudel vs code-music today)

| Operator | Strudel meaning | code-music status |
|---|---|---|
| `a b c` | sequence, equal subdivisions of a cycle | implemented |
| `~` or `-` | rest | `~` only |
| `[a b]` | nested subdivision (compresses into one outer slot) | flattened, not time-divided |
| `<a b c>` | one event per cycle, cycles through | missing |
| `a*N` | repeat N times (speed up) | implemented |
| `a/N` | slow down N times | missing |
| `a@N` | temporal weight (elongation) | missing |
| `a!N` | repeat without speeding up | missing |
| `a?` or `a?p` | random drop with probability `p` (default 0.5) | implemented (default only) |
| `a\|b\|c` | random pick one | missing |
| `a,b,c` | parallel/polyphony (chord) | missing as inline operator |
| `a(N,M)` | euclidean rhythm, N pulses over M steps | missing in mini-notation (have `euclid()` function) |
| `a(N,M,O)` | euclidean with rotation `O` | missing |

### Pattern transforms (Strudel vs code-music)

Implemented today: `reverse, rotate, every, degrade, fast, slow, choose, cat, polymeter, to_notes`.

Worth adding, in priority order:

**Tier A - high musical value, low effort:**
- `rev` (alias for reverse, matches Strudel name)
- `palindrome` (forward then backward each cycle)
- `ply(n)` (repeat each event n times in place)
- `clip(factor)` / `legato` (multiply note duration without changing onset)
- `swing(subdivision)` and `swingBy(amount, subdivision)` (groove)
- `early(cycles)` / `late(cycles)` (nudge timing)
- `iter(n)` / `iterBack(n)` (rotate by 1 each cycle)
- `chunk(n, fn)` (apply fn to one chunk at a time, rotating)
- `mask(binary_pattern)` (silence where mask is 0)
- `struct(rhythm_pattern)` (apply a rhythm structure to a pitch pattern)
- `euclid(n, m, rotation=0)` (already in engine.py as a free function, alias on Pattern)

**Tier B - higher value, requires the time-function abstraction below:**
- `arp(indices)` (arpeggiate stacked notes by index)
- `pick(table)` / `pickF(table)` (lookup tables of patterns or functions)
- `inhabit(table)` (squeezed pick)
- `compress(start, end)` (fit cycle into a sub-timespan)
- `zoom(start, end)` (play a portion of the pattern)
- `linger(fraction)` (repeat first fraction)
- `when(binary_pattern, fn)` (conditional transform)
- `inside(n, fn)` / `outside(n, fn)` (apply transform inside/outside a cycle)

**Tier C - real architectural change:**
- Per-event control parameters as separate patterns: `gain`, `pan`, `cutoff`, `room`, `delay`, ... that can themselves be patterns and combine via `set` / `add` / `mul` operators.
- Continuous patterns: `sine`, `saw`, `tri`, `square` as LFOs that any control parameter can sample.
- `stack(*patterns)` proper time-aligned parallel layering (not just polymeter).

### Concepts not yet present at all

1. **Cycle-time abstraction**. Strudel's Pattern is `(start, end) -> [Hap]` where `Hap` is `(timespan, value)`. code-music's Pattern is `list[str | None]`. Porting the time-function model unlocks Tier B and C cleanly. Without it, transforms like `compress`, `zoom`, `early`, `late`, `chunk` become awkward edge cases.

2. **Control parameter patterns**. In Strudel, `s("bd*4").gain("1 0.5 0.8 0.3").pan(sine)` lets every parameter be its own time-function, multiplexed at render time. code-music currently sets velocity per Note up front; a parametric layer would be a natural extension and is what makes algorave performances feel *modulated*.

3. **Live execution loop**. None of code-music runs in real time today. This is the biggest gap and the most interesting one. Already on the roadmap (`docs/for_developers.md` Tier 4: "Live Coding REPL").

## Switch Angel's ASCII tracker

The "ascii track sequencer in Strudel" she mentions is not open-sourced (we checked). Based on her descriptions and the long tradition of music trackers (FastTracker II, Renoise, Sunvox, Buzz), the format is almost certainly a **multi-line text grid where rows are time steps and columns are voices**:

```
     KICK SNARE HAT  BASS LEAD
00 | C2   ...   C5   F1   ...
01 | ...  ...   C5   ...  ...
02 | ...  D2    C5   ...  C5
03 | ...  ...   C5   ...  ...
04 | C2   ...   C5   F1   ...
05 | ...  ...   ...  ...  D5
06 | ...  D2    C5   ...  ...
07 | ...  ...   C5   ...  Eb5
```

This is a well-defined notation. Each column becomes a Pattern; the grid as a whole becomes a Song or a `MultiPattern`. We can ship it as `code_music.ascii_tracker` independently of any Strudel work. It is also a great vehicle for live coding once that lands.

## Phased plan

Each phase is shippable on its own and lands as a single PR.

### Phase 1 - Mini-notation parity (no architecture change)

**Goal:** Anything that compiles in Strudel mini-notation also compiles in code-music's Pattern parser, with semantics that match for the static (non-time-varying) cases.

**Scope:**
- Extend `_parse_mini` and `_tokenize` to handle `<...>`, `/N`, `@N`, `!N`, `|`, `?p`, and `(N,M[,O])`.
- Honour `[...]` as a true subdivision (returns nested events with fractional durations) instead of flattening.
- Add `-` as rest synonym.
- Update `Pattern.events` to optionally return `(value, duration_fraction)` tuples for nested subdivisions, while keeping the simple `list[str|None]` form for back-compat.
- Tests: round-trip every Strudel mini-notation example from `https://strudel.cc/learn/mini-notation/` through our parser.

**Out of scope:** time-function abstraction, real-time playback, control parameter patterns.

**PR title:** `feat(pattern): mini-notation parity with Strudel`
**Estimated tests:** ~40 new
**Estimated lines:** ~500 in `pattern.py` + tests

### Phase 2 - ASCII tracker (`code_music.ascii_tracker`) - SHIPPED

Switch Angel's signature notation, in Python, with no Strudel dependency.

**Shipped:**
- `code_music/ascii_tracker.py` (~290 lines) with `AsciiTracker.from_string`, `to_patterns`, `to_song`, and `to_string` round-trip.
- Cell formats supported: rests (`~`, `-`, `...`), single notes (`C2`, `Bb4`, `F#3`), chords (`C2,E2,G2`), velocity suffixes both MIDI-scale (`C2:80`) and fractional (`C2:0.6`).
- Optional leading `NN |` step-index column. `#` line comments. Blank lines ignored.
- Two demo songs: `songs/tracker_trance.py` (16-step trance grid in the Switch Angel style at 138 BPM) and `songs/tracker_chord_progression.py` (I-vi-IV-V chord grid at 84 BPM).
- 35 unit tests in `tests/test_ascii_tracker.py` covering parsing, rendering, error cases, round-trip, and edge cases.
- Tracker smoke render added to CI.

**Slide notation (`C2~D2`) and modulation lanes deferred** to a future PR - the v1 cell parser does not accept them. Calling `_parse_cell("C2~D2")` raises `ValueError` deliberately so the gap is visible.

### Phase 3 - Tier A transforms

**Goal:** Add the high-value Strudel transforms that work on the current event-list Pattern.

**Scope:**
- Implement `rev` (alias), `palindrome`, `ply`, `clip`/`legato`, `swing`, `swingBy`, `early`, `late`, `iter`, `iterBack`, `chunk`, `mask`, `struct`, `euclid` (Pattern method), `linger`.
- Each gets a docstring with the Strudel equivalent for cross-reference.
- Each gets a test with at least one input/output assertion.

**Estimated tests:** ~60 new
**Estimated lines:** ~400 in `pattern.py` + tests

### Phase 4 - Time-function Pattern abstraction

**Goal:** Port the actual Strudel data model.

**Scope:**
- New class `code_music.pattern2.Pattern` (kept separate from existing flat Pattern during migration) that represents a pattern as `query(timespan) -> list[Hap]`.
- `Hap` is a dataclass: `timespan: TimeSpan, value: T, whole: TimeSpan | None`.
- Implement the core combinators on top: `fast, slow, rev, every, cat, stack, app, sequence, polymeter, polyrhythm`.
- Compile mini-notation (already extended in Phase 1) into this representation directly instead of into a flat list.
- Provide `Pattern2.query(0, 1) -> list[Hap]` adaptor that produces equivalent flat events for back-compat.
- Tests: cycle equivalence between Phase 1's flat parser and Phase 4's time-function parser for the entire Strudel example set.

**Why this is its own phase:** it touches every consumer. Doing it in one PR keeps the diff reviewable. After Phase 4, all later transforms become natural method definitions on `Pattern2`.

**Estimated tests:** ~80 new
**Estimated lines:** ~1500 + tests

### Phase 5 - Tier B + C transforms and parametric controls

**Goal:** The expressive power of Strudel: per-parameter patterns that combine.

**Scope:**
- Implement `arp, pick, pickF, inhabit, compress, zoom, when, inside, outside, segment` on `Pattern2`.
- Add `code_music.controls`: `Pattern2[float]` for `gain, pan, cutoff, resonance, room, delay, ...`.
- Continuous source patterns: `sine, saw, tri, square` as LFOs producing `Pattern2[float]`.
- Combinators: `set, add, mul, div` on numeric Patterns.
- `Track.from_pattern(p, controls={"gain": gain_pat, "cutoff": cutoff_pat})` plumbs the controls through the existing `EffectsChain` at render time.

**Estimated tests:** ~100 new
**Estimated lines:** ~1500 + tests

### Phase 6 - Live coding REPL (`code-music repl`)

**Goal:** Already on the roadmap (Tier 4 in `docs/for_developers.md`). Strudel parity makes this finally worth the cost.

**Scope:**
- New CLI subcommand `code-music repl`.
- Interactive prompt: edit a pattern variable, press `eval`, audio crossfades to the new pattern at the next cycle boundary.
- Use `sounddevice` for ring-buffer playback (already an optional install: `pip install code-music[play]`).
- Save / load REPL sessions as `.cm` files.
- Display the currently-playing pattern visually in the terminal (rich highlight on the active step), so the user gets the Strudel visual feedback experience without a browser.

**This is the killer feature.** The user writes Python in their terminal, sees the pattern grid update in real time, and audio reflects edits within one cycle. Same instinct as Switch Angel's Strudel performances, but in the offline-friendly Python ecosystem.

**Estimated tests:** ~30 new (mostly RingBuffer + reload-debouncing)
**Estimated lines:** ~1200 + tests

### Phase 7 - Bidirectional Strudel bridge

**Goal:** Studio-stage interop with the actual Strudel ecosystem.

**Scope:**
- `Song.to_strudel() -> str` (one-way export). Walks tracks, emits `note(...)`, `s(...)`, `gain(...)`, `pan(...)`, `room(...)`, `delay(...)` calls. The result pastes into a Strudel REPL and plays.
- `Song.to_midi(path)` and `Song.from_midi(path)` if not already there. MIDI is the lingua franca for Strudel `<-> code-music` round-trip when the transpiler is not bidirectional.
- Round-trip test: render `Song -> .strudel -> evaluate via Strudel CLI in CI -> .wav` and compare against direct `Song -> .wav`.
- Add a `samples/strudel/` directory with three demo songs: a kick pattern, a bassline, and a chord progression, each shown as both Python and as the generated Strudel string in a side-by-side `.md` file.

**Estimated tests:** ~25 new (transpiler unit tests; the CLI round-trip is integration, runs in a separate workflow)
**Estimated lines:** ~600 + tests

## Non-goals

- **Replacing the existing synth chain with Strudel's WebAudio engine.** The 27-stage pipeline + 171 instrument presets are good and tested. Strudel's synth is fine but not better.
- **Browser-only rendering.** code-music's offline FLAC pipeline is the differentiator. Live mode is additive.
- **Implementing every single Strudel function.** There are ~80 transforms. Tier A + B covers ~30 of them and accounts for most of what shows up in actual Strudel patterns.

## What ships first

**Phase 2 has shipped. Phase 1 is the recommended next PR.**

1. ~~Ship Phase 2 first~~ DONE - tracker module + 35 tests + 2 demo songs + CI smoke render.
2. Ship Phase 1 next - extend the existing Pattern grammar with the missing Strudel mini-notation operators (`<>`, `/N`, `@N`, `!N`, `|`, `(N,M[,O])`, true subdivisions, `-` rest synonym).
3. Then Phase 3 (Tier A transforms) - cheap, satisfying.
4. Then Phase 4 (time-function abstraction) - the real architectural lift.
5. Phases 5/6/7 follow naturally once the abstraction is in place.

## Open questions

- **Sample timing semantics.** Strudel cycles are unitless; code-music renders at fixed BPM. The mapping is straightforward (one cycle = one bar by default), but `cpm()` and tempo-modulated patterns need a decision. Default proposal: a Pattern is one bar at the Song's BPM unless `pattern.cpm(N)` overrides.
- **Note vs sample distinction.** Strudel separates `note("c3")` (synth pitch) from `s("bd")` (named sample). code-music has `instrument="..."` per Track. We can keep that, but mini-notation strings should accept both note names (`c3`, `bb4`) and sample names (`bd`, `sd`, `hh`) and dispatch at render time.
- **Naming.** Use Strudel's names (`fast, slow, rev, ply, struct`) directly even when code-music has older equivalents? Recommendation: yes, with the older names kept as aliases. Reduces translation friction for anyone coming from Tidal/Strudel.

## References

- Strudel docs: https://strudel.cc/learn/
- Strudel mini-notation: https://strudel.cc/learn/mini-notation/
- Strudel time modifiers: https://strudel.cc/learn/time-modifiers/
- Strudel synths: https://strudel.cc/learn/synths/
- Strudel source (MIT): https://github.com/tidalcycles/strudel
- TidalCycles (the original): https://tidalcycles.org/
- Switch Angel: https://www.youtube.com/@Switch-Angel and https://linktr.ee/switchangel
- Toplap (live coding community): https://toplap.org/
