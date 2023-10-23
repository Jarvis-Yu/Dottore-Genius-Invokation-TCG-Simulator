Mode
====

``Mode`` is a class used to describe the game mode. It has full control to define
how a game should be run.

``Mode`` acts as an abstract class, and it has a number of subclasses as implementations.

.. toctree::
    :maxdepth: 1

    /mode/default-mode
    /mode/all-omni

.. autoclass:: dgisim.mode.Mode
    :members:

More could be customized like the maximum number of cards that can be held,
the hand card limit, ... But these may undergo big design changes, so won't be
specified in the documentation.
