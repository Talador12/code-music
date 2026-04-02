"""Noise Floor — experimental ambient from noise generators and filters.

Brown noise drones, pink noise textures, filtered white noise percussion.
Exploring the musical side of noise through SoundDesigner.
"""

from code_music import (
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    reverb,
)

# -- Custom instruments built from noise + minimal osc ----------------------

rain = (
    SoundDesigner("rain")
    .noise("pink", volume=0.7, seed=1)
    .noise("brown", volume=0.3, seed=2)
    .envelope(attack=2.0, decay=0.5, sustain=0.4, release=2.0)
    .filter("bandpass", cutoff=3000, resonance=0.5)
    .lfo("filter_cutoff", rate=0.08, depth=0.6)
)

rumble = (
    SoundDesigner("rumble")
    .noise("brown", volume=0.9, seed=10)
    .add_osc("sine", volume=0.2)
    .envelope(attack=1.5, decay=0.5, sustain=0.5, release=2.0)
    .filter("lowpass", cutoff=120, resonance=1.2)
)

click = (
    SoundDesigner("click")
    .noise("white", volume=1.0, seed=42)
    .envelope(attack=0.001, decay=0.02, sustain=0.0, release=0.01)
    .filter("highpass", cutoff=5000, resonance=0.5)
)

hum = (
    SoundDesigner("hum")
    .add_osc("sine", volume=0.5)
    .add_osc("triangle", detune_cents=2, volume=0.3)
    .noise("brown", volume=0.1, seed=7)
    .envelope(attack=0.5, decay=0.3, sustain=0.6, release=1.0)
    .filter("lowpass", cutoff=500, resonance=0.6)
    .lfo("volume", rate=0.2, depth=0.3)
)

shimmer = (
    SoundDesigner("shimmer")
    .noise("white", volume=0.4, seed=88)
    .add_osc("sine", detune_cents=0, volume=0.3)
    .add_osc("sine", detune_cents=700, volume=0.2)  # ~fifth
    .envelope(attack=0.3, decay=0.5, sustain=0.2, release=1.0)
    .filter("bandpass", cutoff=5000, resonance=2.0)
    .lfo("filter_cutoff", rate=0.3, depth=0.4)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Noise Floor", bpm=50, sample_rate=44100)

for name, designer in [
    ("rain", rain),
    ("rumble", rumble),
    ("click", click),
    ("hum", hum),
    ("shimmer", shimmer),
]:
    song.register_instrument(name, designer)

# Low rumble bed
tr_rumble = song.add_track(Track(name="rumble", instrument="rumble", volume=0.3))
tr_rumble.add(Note("C", 1, 16.0))

# Rain texture
tr_rain = song.add_track(Track(name="rain", instrument="rain", volume=0.25, pan=0.2))
tr_rain.add(Note("A", 4, 16.0))

# Hum — slow tonal center
tr_hum = song.add_track(Track(name="hum", instrument="hum", volume=0.35, pan=-0.1))
tr_hum.add(Note("C", 3, 8.0))
tr_hum.add(Note("Eb", 3, 8.0))

# Shimmer: sparse accents
tr_shimmer = song.add_track(Track(name="shimmer", instrument="shimmer", volume=0.3, pan=0.3))
shimmer_pattern = [(2.0,), (1.5,), (3.0,), (1.0,), (2.5,), (1.5,), (2.0,), (2.5,)]
for dur_tuple in shimmer_pattern:
    tr_shimmer.add(Note("G", 6, dur_tuple[0]))

# Clicks: irregular sparse rhythm
tr_click = song.add_track(Track(name="click", instrument="click", volume=0.2))
click_pattern = [0.5, 1.5, 0.5, 1.0, 2.0, 0.5, 1.5, 0.5, 1.0, 0.5, 1.5, 2.0, 0.5, 1.0, 1.5, 0.5]
for dur in click_pattern:
    if dur > 1.0:
        tr_click.add(Note.rest(dur))
    else:
        tr_click.add(Note("C", 7, dur))

song.effects = {
    "rain": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "rumble": EffectsChain().add(reverb, room_size=0.8, wet=0.3),
    "shimmer": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "hum": EffectsChain().add(reverb, room_size=0.7, wet=0.25),
}
