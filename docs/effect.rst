Effect
======

.. code-block:: python3

    from dgisim import Effect

``Effect`` acts as an abstract class that could be extended to carry pending
effects waiting to be executed in a game state.

.. autoclass:: dgisim.effect.effect.Effect
    :members:

The actual implementations of the effects could be imported from:

.. code-block:: python3

    from dgisim.effect import *

There are too many effects, so the documentation is not going to elaborate here.
Please refer to the source code for more information.
