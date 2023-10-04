Get Started
===========

.. _installation:

Installation
------------

Please make sure your python version >= 3.10 before installation.

.. code-block:: console

    $ pip install dgisim

Use Interactive CLI
-------------------

To get you familiar with the simulator, it's nice to have a try with the
built-in CLI to play or watch a game.

.. code-block:: python3

    from dgisim import CLISession

    CLISession().run()

.. note::

    CLI has built-in command hints, so it should be intuitive to use it.

    More details can be found at :ref:`cli`.

Create a Game With Custom Deck
------------------------------

You need to start by importing relative modules.

.. code-block:: python3

    import dgisim as dg
    from dgisim.character.character import *
    import dgisim.card.card as dc

Then define a deck for player 1.

.. code-block:: python3

    deck1 = dg.MutableDeck(
        chars=[Bennett, Klee, Keqing],
        cards={
            dc.GrandExpectation: 2,
            dc.PoundingSurprise: 2,
            dc.ThunderingPenance: 2,
            dc.Vanarana: 2,
            dc.ChangingShifts: 2,
            dc.LeaveItToMe: 2,
            dc.SacrificialSword: 2,
            dc.GamblersEarrings: 2,
            dc.IHaventLostYet: 2,
            dc.LotusFlowerCrisp: 2,
            dc.NorthernSmokedChicken: 2,
            dc.ElementalResonanceFerventFlames: 2,
            dc.ElementalResonanceWovenFlames: 2,
            dc.WindAndFreedom: 2,
            dc.TeyvatFriedEgg: 2,
        }
    )

.. note::

    In the context of ``dgisim``, **player 1** is the player that goes first in the
    first round. **Player 2** is of course, the second to go.

We can create a second deck in a similar manner. Let's name it ``deck2``.

Assuming you have created ``deck2``.
(You could just code ``deck2 = deck1`` to save time)
It's now time to create the initial game state of a game.

.. code-block:: python3

    initial_game_state = dg.GameState.from_decks(
        mode=dg.mode.DefaultMode(),
        p1_deck=deck1,
        p2_deck=deck2,
    )

.. note::

    The ``initial_game_state`` is of type ``GameState``,
    which is a representation of a moment in an entire game.
    It contains all the information of the moment, and can be used to proceed
    to the next ``GameState``.

    The ``dgisim.DefaultMode()`` defines the rules about how game should be run.
    ``DefaultMode`` is the usual mode where each player has 3 characters and 30
    cards etc.

    You could also use ``dgisim.mode.AllOmniMode()`` to make the game always generate
    **omni dics** during the **roll phase**.

You can now ``print`` the current game state to check if things seem all right.

.. code-block:: python3

    print(initial_game_state)

The output below is what you should get.

.. code-block:: console

    <Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
    -----------------------------------------------------------------------------------
    <Player: *Player1>                      | <Player: Player2>                       |
    <Phase: Passive Wait Phase>             | <Phase: Passive Wait Phase>             |
    <Card/Dice Redraw Chances: 0/0>         | <Card/Dice Redraw Chances: 0/0>         |
    <Characters>                            | <Characters>                            |
      <1-Bennett>                           |   <1-Bennett>                           |
        <Aura: []>                          |     <Aura: []>                          |
        <HP: 10/10>                         |     <HP: 10/10>                         |
        <Energy: 0/2>                       |     <Energy: 0/2>                       |
        <Hiddens>                           |     <Hiddens>                           |
        <Equipments>                        |     <Equipments>                        |
        <Statuses>                          |     <Statuses>                          |
      <2-Klee>                              |   <2-Klee>                              |
        <Aura: []>                          |     <Aura: []>                          |
        <HP: 10/10>                         |     <HP: 10/10>                         |
        <Energy: 0/3>                       |     <Energy: 0/3>                       |
        <Hiddens>                           |     <Hiddens>                           |
        <Equipments>                        |     <Equipments>                        |
        <Statuses>                          |     <Statuses>                          |
      <3-Keqing>                            |   <3-Keqing>                            |
        <Aura: []>                          |     <Aura: []>                          |
        <HP: 10/10>                         |     <HP: 10/10>                         |
        <Energy: 0/3>                       |     <Energy: 0/3>                       |
        <Hiddens>                           |     <Hiddens>                           |
          <KeqingTalent(0)>                 |       <KeqingTalent(0)>                 |
        <Equipments>                        |     <Equipments>                        |
        <Statuses>                          |     <Statuses>                          |
    <Hidden Statuses>                       | <Hidden Statuses>                       |
      <PlungeAttack()>                      |   <PlungeAttack()>                      |
      <DeathThisRound()>                    |   <DeathThisRound()>                    |
    <Combat Statuses>                       | <Combat Statuses>                       |
    <Summons>                               | <Summons>                               |
    <Supports>                              | <Supports>                              |
    <Dice>                                 | <Dice>                                 |
    <Hand Cards>                            | <Hand Cards>                            |
    <Deck Cards>                            | <Deck Cards>                            |
      <GrandExpectation: 2>                 |   <GrandExpectation: 2>                 |
      <PoundingSurprise: 2>                 |   <PoundingSurprise: 2>                 |
      <ThunderingPenance: 2>                |   <ThunderingPenance: 2>                |
      <Vanarana: 2>                         |   <Vanarana: 2>                         |
      <ChangingShifts: 2>                   |   <ChangingShifts: 2>                   |
      <LeaveItToMe: 2>                      |   <LeaveItToMe: 2>                      |
      <SacrificialSword: 2>                 |   <SacrificialSword: 2>                 |
      <GamblersEarrings: 2>                 |   <GamblersEarrings: 2>                 |
      <IHaventLostYet: 2>                   |   <IHaventLostYet: 2>                   |
      <LotusFlowerCrisp: 2>                 |   <LotusFlowerCrisp: 2>                 |
      <NorthernSmokedChicken: 2>            |   <NorthernSmokedChicken: 2>            |
      <ElementalResonanceFerventFlames: 2>  |   <ElementalResonanceFerventFlames: 2>  |
      <ElementalResonanceWovenFlames: 2>    |   <ElementalResonanceWovenFlames: 2>    |
      <WindAndFreedom: 2>                   |   <WindAndFreedom: 2>                   |
      <TeyvatFriedEgg: 2>                   |   <TeyvatFriedEgg: 2>                   |
    <Publicly Used Cards>                   | <Publicly Used Cards>                   |
    <Publicly Gained Cards>                 | <Publicly Gained Cards>                 |
    -----------------------------------------------------------------------------------
    <Effects>
    ===================================================================================

Run an Existing Game
--------------------

Given you have created a game state following `Create A Game With Custom Deck`_.
Or if you don't bother to custom one, you can get a random one by running.

.. code-block:: python3

    import dgisim as dg

    game_state = dg.GameState.from_default()

The easiest way to *run* the game is to use the ``GameStateMachine``.

.. code-block:: python3

    from dgisim.agents import RandomAgent

    game_state_machine = dg.GameStateMachine(
        game_state=game_state,
        agent1=RandomAgent(),
        agent2=RandomAgent(),
    )

.. note::

    ``RandomAgent`` is an automatic player that makes random decisions on every
    single move.

``GameStateMachine`` provides a number of methods to run a game.
What we could do here is to call ``.run()`` to run until the end of the game.

.. code-block:: python3

    game_state_machine.run()

    last_game_state = game_state_machine.get_game_state()

``.run()`` prints the results of the game, and you could ``print(last_game_state)``
to see how the game looks like by the end.

There are other ways to fine control over the game progress,
more details are **WIP**.

Customize a Player Agent
------------------------

Simplying having a running game is not enough, it is always fun to create
agents to play the game better and better.

In ``dgisim``, customizing the logics of an antomated player is simple.
You need to inherit from the class ``PlayerAgent`` and override method
``choose_action()``.

.. code-block:: python3

    import dgisim as dg

    class CustomAgent(dg.PlayerAgent):
        def choose_action(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
            ...

The method takes two parameters ``history`` and ``pid``.

* ``history`` contains all game states of the current game in chronological order.
  For simple agents that choose action solely based on the current game state,
  you can get it from ``history[-1]``.
* ``pid`` represents the player the agent is choosing action for. ``Pid.P1`` is
  player 1, and ``Pid.P2`` is player 2. You could use methods ``.is_player1()``
  and ``.is_player2()`` to check the value of ``pid``.

Let's try to build an agent that keeps normal attacking until there's no dice
for it.

There are many ways to implement such an agent, let's get started with the way
which uses ``ActionGenerator``.
It is a class to help you generate valid actions.

.. code-block:: python3

    import dgisim as dg
    import dgisim.action.action as dact
    import dgisim.agents as dagt

    class NormalAttackAgent(dg.PlayerAgent):
        def choose_action(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
            curr_game_state = history[-1]

            if isinstance(curr_game_state.get_phase(), curr_game_state.get_mode().action_phase):
                return self.handle_action_phase(history, pid)

            return dagt.RandomAgent().choose_action(history, pid)

        def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
            curr_game_state = history[-1]
            action_generator = curr_game_state.action_generator(pid)
            assert action_generator is not None

            # check if can use any skill
            choices = action_generator.choices()
            if dg.ActionType.CAST_SKILL not in choices:
                return dagt.RandomAgent().choose_action(history, pid)

            action_generator = action_generator.choose(dg.ActionType.CAST_SKILL)

            # check if normal attack is usable
            choices = action_generator.choices()
            if dg.CharacterSkill.SKILL1 not in choices:
                return dagt.RandomAgent().choose_action(history, pid)

            action_generator = action_generator.choose(dg.CharacterSkill.SKILL1)

            # choose the dice to pay for the normal attack action
            choices = action_generator.choices()
            assert isinstance(choices, dg.AbstractDice)
            cost = choices
            dice = curr_game_state.get_player(pid).get_dice()
            payment = dice.basically_satisfy(cost)
            assert payment is not None

            action_generator = action_generator.choose(payment)

            # generate the final action
            assert action_generator.filled()
            return action_generator.generate_action()

This may look a bit overwhelming, but don't worry, let's go though it step by step.

.. code-block:: python3

    def choose_action(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        curr_game_state = history[-1]

        if isinstance(curr_game_state.get_phase(), curr_game_state.get_mode().action_phase):
            return self.handle_action_phase(history, pid)

        return dagt.RandomAgent().choose_action(history, pid)

This block of code gets the latest game state first, and then see if it is in action
phase. If not, we let ``RandomAgent`` to handle situations we haven't covered yet.
If it is in action phase, then we call ``handle_action_phase()`` to get the action.

.. code-block:: python3

    def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        curr_game_state = history[-1]
        action_generator = curr_game_state.action_generator(pid)
        assert action_generator is not None
        ...

As usual, we first get the latest ``GameState``, then try to get an ``ActionGenerator``
object from it for player ``pid``.
If the return value is ``None``, then the player doesn't have any valid action
to take at the current state.
Here we assume agent is only called when the corresponding player has actions
to take.

.. code-block:: python3

    def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        ...
        # check if can use any skill
        choices = action_generator.choices()
        if dg.ActionType.CAST_SKILL not in choices:
            return dagt.RandomAgent().choose_action(history, pid)

        action_generator = action_generator.choose(dg.ActionType.CAST_SKILL)
        ...

First we get ``choices`` from the action generator, which is typically a ``tuple``.
The first tuple of choices we get in action phase is a tuple of ``ActionType``.
The ``choices`` only contains feasible actions, so if ``ActionType.CAST_SKILL``
is not in choices, then player is unable to cast skill for some reason.
(being frozen, or simply doesn't have dice for the skill)

After confirming we can cast skill, we tell the action generator about our choice,
and get a new action generator to make the next choice.

.. note::

    ``ActionGenerator`` is an immutable class containing the choices you have made
    for a particular game state and player. This makes BFS significantly faster
    and easier, as you can use previous ``ActionGenerator`` objects like parent
    nodes in a tree.

.. code-block:: python3

    def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        ...
        # check if normal attack is usable
        choices = action_generator.choices()
        if dg.CharacterSkill.SKILL1 not in choices:
            return dagt.RandomAgent().choose_action(history, pid)

        action_generator = action_generator.choose(dg.CharacterSkill.SKILL1)
        ...

The category of skills contains not only normal attack, but elemental skills and burst.
So here we double check if normal attack is available.

.. code-block:: python3

    def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        ...
        # choose the dice to pay for the normal attack action
        choices = action_generator.choices()
        assert isinstance(choices, dg.AbstractDice)
        cost = choices
        dice = curr_game_state.get_player(pid).get_dice()
        payment = dice.basically_satisfy(cost)
        assert payment is not None

        action_generator = action_generator.choose(payment)
        ...

Then we choose the dice to pay for the action, ``choices`` here is of type
``AbstractDice``, a class to represent the cost of actions.

.. note::

    ``ActionGenerator`` returns the cost post cost-reduction statuses,
    e.g. if your character had Northern Smoked Chicken, normal attack costs
    1 less ``Element.ANY`` die.

.. note::

    ``AbstractDice`` contains a private immutable dictionary representing the
    cost. For a typical normal attack, the inner dictionary may look like
    ``{Element.PYRO: 1, Element.ANY: 2}``.

Given ``ActionGenerator`` *approves* normal attack action, we know there are
enough dice to pay for the action.
Here I use ``.basically_satisfy()`` to find a way to pay for the cost.
(if ``dice`` cannot fulfill the ``cost`` then ``None`` is returned,
but we know this is not happening here)

.. code-block:: python3

    def handle_action_phase(self, history: list[dg.GameState], pid: dg.Pid) -> dg.PlayerAction:
        ...
        # generate the final action
        assert action_generator.filled()
        return action_generator.generate_action()

Finally, ``action_generator`` is provided with enough choices to generate a vaild action.
We get it by calling ``.generate_action()`` provided ``.filled()`` returns ``True``.

The code above is just one way to code an agent.
You could of course code in your own way, as long as you return a valid
``PlayerAction``.