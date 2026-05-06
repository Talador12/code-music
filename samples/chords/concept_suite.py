"""Concept suite: render an album idea into several hook sketches."""

from code_music.theory import generate_concept_suite

suite = generate_concept_suite("Rasputin", tracks=4, seed=77)

# Exporters expect a top-level ``song`` variable. Pick the first sketch for
# quick preview; scripts can import ``suite`` when they want the whole batch.
song = suite[0]
