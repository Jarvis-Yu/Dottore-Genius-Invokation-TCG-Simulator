Player Action and Instruction
=============================

.. code-block:: python3

    from dgisim import PlayerAction, Instruction

* ``PlayerAction`` is any action that can be taken by a player in the game.
* ``Instruction`` is the additional information added in player actions to
  specify how an action should be performed.

.. automodule:: dgisim.action.action
    :members:
    :show-inheritance:
    :exclude-members: PlayerAction, Instruction

    .. autoclass:: PlayerAction
        :members:

    .. autoclass:: Instruction
        :members:

All classes above are frozen dataclass that is key_word only. This means in order
to initialize any of these, you need to specify all key words:

.. code-block:: python3

    from dgisim import ActualDice, CardAction, Element, Pid, StaticTarget, StaticTargetInstruction
    from dgisim.card import SendOff
    from dgisim.summon import OceanicMimicFrogSummon

    # just an example of using SendOff on OceanicMimicFrog (summon)
    card_action = CardAction(
        card=SendOff,
        instruction=StaticTargetInstruction(
            dice=ActualDice({Element.ELECTRO: 1, Element.ANEMO: 1}),
            target=StaticTarget.from_summon(Pid.P2, OceanicMimicFrogSummon),
        ),
    )
