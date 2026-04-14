"""Example 17: Plugin System - register custom instruments, effects, generators.

Demonstrates:
- @register_instrument for custom SoundDesigner presets
- @register_effect for custom audio effects
- @register_generator for custom song generators
- discover_plugins() for auto-discovery
- plugin_summary() for inspection
- The built-in vintage preset pack
"""

from code_music import (
    Song,
    SoundDesigner,
    Track,
    discover_plugins,
    plugin_summary,
    register_effect,
    register_generator,
    register_instrument,
    scale,
)

# --- 1. Register a custom instrument ---
print("1. Custom instrument registration")


@register_instrument("chiptune_lead")
def chiptune_lead():
    return (
        SoundDesigner("chiptune_lead")
        .add_osc("square", volume=0.5)
        .add_osc("square", detune_cents=5, volume=0.3)
        .envelope(attack=0.005, decay=0.05, sustain=0.4, release=0.1)
        .filter("lowpass", cutoff=2000, resonance=0.6)
    )


print("   Registered: chiptune_lead")

# --- 2. Register a custom effect ---
print("\n2. Custom effect registration")

import numpy as np  # noqa: E402


@register_effect("bitcrush_8bit")
def bitcrush_8bit(samples, sample_rate, bits=4, wet=0.8):
    """Reduce bit depth for retro 8-bit sound."""
    levels = 2**bits
    crushed = np.round(samples * levels) / levels
    return wet * crushed + (1 - wet) * samples


print("   Registered: bitcrush_8bit")

# --- 3. Register a custom generator ---
print("\n3. Custom generator registration")


@register_generator("chiptune")
def chiptune_song(key="C", bpm=140, seed=None):
    song = Song(title=f"Chiptune in {key}", bpm=bpm)
    sd = chiptune_lead()
    song.register_instrument("chiptune_lead", sd)
    tr = song.add_track(Track(name="lead", instrument="chiptune_lead", volume=0.5))
    tr.extend(scale(key, "pentatonic", octave=5, length=16))
    return song


print("   Registered: chiptune generator")

# --- 4. Plugin summary ---
print("\n4. Plugin summary")
summary = plugin_summary()
print(f"   Instruments: {summary['instruments']}")
print(f"   Effects: {summary['effects']}")
print(f"   Generators: {summary['generators']}")

# --- 5. Auto-discovery ---
print("\n5. Entry-point discovery")
result = discover_plugins()
print(f"   Discovered {result['discovered_count']} plugins from installed packages")

# --- 6. Use the vintage pack ---
print("\n6. Vintage preset pack")
import code_music.packs.vintage  # noqa: F401, E402

summary2 = plugin_summary()
print(
    f"   After loading vintage pack: {len(summary2['instruments'])} instruments, {len(summary2['effects'])} effects"
)

# --- 7. Build a song with custom + vintage instruments ---
print("\n7. Building song with plugins")
from code_music.packs.vintage import vintage_epiano  # noqa: E402

song = Song(title="Plugin Showcase", bpm=130, sample_rate=22050)
song.register_instrument("chiptune_lead", chiptune_lead())
song.register_instrument("vintage_epiano", vintage_epiano)

lead = song.add_track(Track(name="chip_lead", instrument="chiptune_lead", volume=0.5))
lead.extend(scale("C", "pentatonic", octave=5, length=8))

from code_music import Chord  # noqa: E402

keys = song.add_track(Track(name="keys", instrument="vintage_epiano", volume=0.4))
for root, shape in [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")]:
    keys.add(Chord(root, shape, 4, duration=2.0))

print(f"   Song: '{song.title}', {len(song.tracks)} tracks")
