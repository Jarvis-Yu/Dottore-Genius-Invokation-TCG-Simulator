Player State
============

.. code-block:: python3

    from dgisim import PlayerState

.. autoclass:: dgisim.state.player_state.PlayerState
    :members:
    :exclude-members: factory

    .. automethod:: __init__
    .. automethod:: factory

        The factory allows modifications to the existing a copy of the origial
        player state to produce a new one.

        You may call ``.<attribute-name>(new_val)`` to replace the current value.

        Or call ``.f_<attribute-name>(<function>)`` to make modifications based
        on the current value.

        e.g. ``player_state.factory().dice(ActualDice({})).f_hand_cards(lambda hcs: hcs.add(Paimon)).build()``
        returns a new player state with no dice but one additional **Paimon** card.

