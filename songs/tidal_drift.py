"""Tidal Drift — pattern transforms and granular synthesis combined."""

from code_music import EffectsChain, Note, Pattern, Song, SoundDesigner, Track, euclid, reverb

cloud = (
    SoundDesigner("cloud")
    .add_osc("triangle", volume=0.3)
    .granular(grain_size=0.05, density=15, scatter=0.6, volume=0.7, seed=99)
    .envelope(attack=0.4, decay=0.2, sustain=0.4, release=0.8)
    .filter("lowpass", cutoff=2500, resonance=0.5)
)

song = Song(title="Tidal Drift", bpm=100, sample_rate=44100)
song.register_instrument("cloud", cloud)

# Pattern-based lead with every-4th-reversed variation
lead_pat = Pattern("A4 C5 E5 G5 F5 E5 C5 D5")
evolving = lead_pat.every(4, lambda p: p.reverse())
tr_lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
tr_lead.extend(evolving.to_notes(0.5))

# Granular cloud texture
tr_cloud = song.add_track(Track(name="cloud", instrument="cloud", volume=0.3))
tr_cloud.add(Note("A", 3, 16.0))

# Degraded ghost pattern
ghost = lead_pat.degrade(0.4, seed=77)
tr_ghost = song.add_track(Track(name="ghost", instrument="pad", volume=0.25, pan=0.2))
for _ in range(4):
    tr_ghost.extend(ghost.to_notes(0.5))

# Bass: polymeter 3 vs 5
b3 = Pattern("A2 C3 E3")
b5 = Pattern("A2 B2 C3 D3 E3")
poly = Pattern.polymeter(b3, b5)
tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for _ in range(2):
    tr_bass.extend(poly.to_notes(0.5))

# Kick: euclidean
tr_kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6))
for _ in range(4):
    tr_kick.extend(euclid(3, 8, "C", 2, 0.5))

song.effects = {
    "cloud": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "ghost": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
