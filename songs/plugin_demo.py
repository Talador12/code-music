"""Plugin Demo - showcase the plugin registry system."""

from code_music import Note, Song, SoundDesigner, Track, register_instrument, scale


# Register a custom instrument via the plugin system
@register_instrument("retro_lead")
def retro_lead():
    return (
        SoundDesigner("retro_lead")
        .add_osc("square", volume=0.5)
        .add_osc("square", detune_cents=15, volume=0.3)
        .envelope(attack=0.01, decay=0.1, sustain=0.5, release=0.2)
        .filter("lowpass", cutoff=2500, resonance=0.7)
    )


song = Song(title="Plugin Demo", bpm=130, sample_rate=44100)

# Use the plugin-registered instrument
sd = retro_lead()
song.register_instrument("retro_lead", sd)

lead = song.add_track(Track(name="lead", instrument="retro_lead", volume=0.5, pan=0.1))
lead.extend(scale("C", "pentatonic", octave=5, length=16))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["C", "C", "G", "G", "A", "A", "F", "F"]:
    bass.add(Note(root, 2, 2.0, velocity=65))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(16):
    kick.add(Note("C", 4, 1.0, velocity=80))
