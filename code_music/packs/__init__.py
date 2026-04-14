"""Built-in preset packs for code-music.

Import a pack to register its instruments, effects, and generators::

    import code_music.packs.vintage  # registers FM pianos, analog strings, tape
    import code_music.packs  # imports all built-in packs
"""

from . import vintage  # noqa: F401

__all__ = ["vintage"]
