"""09 — Generative music: let the engine compose for you.

Run:  code-music examples/09_generative.py --play
"""

from code_music import generate_song

# Generate a complete multi-track song from a genre template.
# Available genres: lo_fi, jazz, ambient, edm, rock, classical, funk, hip_hop
# Seed makes it reproducible — same seed = same song every time.

song = generate_song(
    genre="jazz",  # try: lo_fi, ambient, edm, rock, funk, hip_hop, classical
    bars=16,  # how many bars
    seed=42,  # change this number for a different song
    sample_rate=22050,
)

# That's it — a full song with chords, melody, bass, and drums.
# The generate_song() function uses:
#   - suggest_progression() for chord progressions
#   - generate_melody() for procedural melodies
#   - Genre-specific drum and bass patterns

# Try from the CLI without even writing a file:
#   code-music --random
#   code-music --random jazz
#   code-music --random ambient
