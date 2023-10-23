Static Target
=============

.. code-block:: python3

    from dgisim import StaticTarget

``StaticTarget`` is widely used to locate a certain thing in the game state.
It stores 3 values: ``pid``, ``zone`` and ``id``.

* ``pid`` tells which player to look for.
* ``zone`` tells which zone is the focus (character, summon, support).
* ``id`` is either the character id, summon type or support id (sid).

.. autoclass:: dgisim.effect.structs.StaticTarget
    :members:

    .. autoattribute:: pid
    .. autoattribute:: zone
    .. autoattribute:: id
