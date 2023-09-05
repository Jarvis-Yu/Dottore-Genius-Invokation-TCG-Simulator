Tutorial
========

.. _installation:

Installation
------------

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

    The detailed documentation for CLI is **WIP**.

Create A Game With Custom Deck
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
    ``DefaultMode`` is the usual mode where each team has 3 characters and 30 cards etc.

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
    <Dices>                                 | <Dices>                                 |
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

Run An Existing Game
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
