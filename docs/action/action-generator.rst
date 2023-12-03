Action Generator
================

.. code-block:: python3

    from dgisim import ActionGenerator

``ActionGenerator`` is a class used to helper agents generate valid actions.

An example use flow typically looks like this:

.. code-block:: python3

    from dgisim import ActionGenerator, GameState, Pid

    # get some game state waiting for an action
    game_state: GameState = ...
    assert game_state.waiting_for() is Pid.P1

    # get initial action generator
    act_gen: ActionGenerator | None = game_state.action_generator(Pid.P1)
    assert act_gen is not None

    # fill in the action generator until it is full
    while not act_gen.filled():
        choices = act_gen.choices()
        choice = ...  # make a choice based on choices
        act_gen = act_gen.choose(choice)

    # As each ActionGenerator object is immutable, you can easily construct all
    # valid actions with the use of recursion or a queue.

.. autoclass:: dgisim.action.action_generator.ActionGenerator
    :members:
