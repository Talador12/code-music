"""Noise sweep build: white noise filtered sweep for EDM drop tension."""


from code_music import Chord, Song, Track

# This sample demonstrates noise_sweep() applied directly to a rendered mix.
# The song has pads; post-render the noise sweep is mixed in manually.
song = Song(title="noise_build", bpm=128)
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.4))
for _ in range(4):
    pad.add(Chord("A", "min7", 3, duration=4.0, velocity=0.5))

# Note: to mix in the sweep programmatically, render manually:
# synth = Synth()
# base = synth.render_song(song)
# sweep = noise_sweep(len(base), 44100, start_cutoff=200, end_cutoff=16000, volume=0.4)
# mixed = np.clip(base + sweep, -1.0, 1.0)
