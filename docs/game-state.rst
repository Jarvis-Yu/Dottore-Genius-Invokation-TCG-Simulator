Game State
==========

``GameState`` is an immutable class used to hold all the information of a moment
of a game.

``__eq__`` and ``__hash__`` are implemented so that any two characters with the
equivalent content are equal to each other and have the same hash.

.. code-block:: python3

    from dgisim import GameState

.. autoclass:: dgisim.state.game_state.GameState
    :members:
    :exclude-members: factory

    .. automethod:: __init__
    .. automethod:: factory

        The factory allows modifications to the existing a copy of the origial
        game state to produce a new one.

        You may call ``.<attribute-name>(new_val)`` to replace the current value.

        Or call ``.f_<attribute-name>(<function>)`` to make modifications based
        on the current value.

        e.g. ``game_state.factory().f_round(lambda r: r + 1).active_player_id(Pid.P1).build()``
        returns a new game state with incremented round and active player as `Pid.P1`.
