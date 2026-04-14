"""Classical Fugue - 3-voice fugue in D minor via generate_fugue."""

from code_music.theory import generate_fugue

song = generate_fugue(voices=3, key="D", seed=1722)  # Bach's well-tempered year
