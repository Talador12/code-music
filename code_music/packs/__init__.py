"""Built-in preset packs for code-music.

Import a pack to register its instruments, effects, and generators::

    import code_music.packs.vintage    # FM pianos, analog strings, tape
    import code_music.packs.cinematic  # orchestra hits, epic brass, risers
    import code_music.packs.electronic # supersaw, wobble, plucks, lo-fi
    import code_music.packs            # imports all built-in packs
"""

from . import cinematic, electronic, vintage  # noqa: F401

__all__ = ["vintage", "cinematic", "electronic"]
