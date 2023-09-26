.. _cli:

CLI (Command Line Interface)
============================

``dgisim`` has a built-in CLI for developers to manually play and test the game.

CLI Session Basics
------------------

All you need to do to run the CLI is to import and use directly.

.. code-block:: python3

    from dgisim import CLISession

    session = CLISession()
    session.run()

Running the program will print the follwing and wait for your input.

.. code-block:: console

    ==================================================
    Welcome to the Dottore Genius Invokation TCG Simulator CLI ver.
    ==================================================
    Commands:
    a    - to forward to an autostep
    n    - to forward to next step
    ba   - to previous autostep
    bn   - to previous step
    h    - to get help
    q    - to quit this session
         - enter nothing to repeat last step
    rst  - to reset game session (and choose next game mode)

    Note: any invalid commands are ignored

    Definitions:
    - autostep - jumps to the next game-state where player interaction is required
    - step - jumps to the next game-state
    ==================================================
    Please choose the cli mode:
    Choices are:
    @0: PVP  |||  @1: PVE  |||  @2: EVE
    Please choose id (0-2)
    ::> 

Starting with a warm welcome message, all supported commands are immediately shown
to you.

The CLI takes two types of commands under two cases.

Normally, the prompt looks like ``:>`` waiting to take your commands.
(commands here are ``a``, ``n``...)

When in the middle of a decision making, the prompt looks like ``::>``.
In this case, you must finish the entire decision in order to continue.
As to what to input here, you need to follow the instruction right above the ``::>``.

For example, in this case.

.. code-block:: console

    Please choose the cli mode:
    Choices are:
    @0: PVP  |||  @1: PVE  |||  @2: EVE
    Please choose id (0-2)
    ::> 

As shown above, you need to type in a numebr in range 0 to 2,
each representing the choice of *PVP*, *PVE* and *EVE*.

.. note::

    **P** is player controlled by you.

    **E** is a random computer agent that makes random choices.

    Currently CLI doesn't support customzing decks yet,
    so for any game, random decks are applied to each player.

After you choose your game mode, the game starts immediately and becomes the
focused game of the session.
(A CLI session can only have one focused game)
To choose a new mode or start a new game, you need to run ``rst`` when prompt
is ``:>``.

Run the Game
------------

Assuming now you have chosen a game mode to play.
(see `CLI Session Basics`_ if you don't know how to)
The initial game state will immediately be printed.

It may look somewhat like this:

.. code-block:: console

    <Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
    ----------------------------------------------------------------------
    <Player: *Player1>                | <Player: Player2>                |
    <Phase: Passive Wait Phase>       | <Phase: Passive Wait Phase>      |
    <Card/Dice Redraw Chances: 0/0>   | <Card/Dice Redraw Chances: 0/0>  |
    <Characters>                      | <Characters>                     |
      <1-FatuiPyroAgent>              |   <1-Shenhe>                     |
        <Aura: []>                    |     <Aura: []>                   |
        <HP: 10/10>                   |     <HP: 10/10>                  |
        <Energy: 0/2>                 |     <Energy: 0/2>                |
        <Hiddens>                     |     <Hiddens>                    |
          <StealthMaster>             |     <Equipments>                 |
        <Equipments>                  |     <Statuses>                   |
        <Statuses>                    |   <2-SangonomiyaKokomi>          |
      <2-Jean>                        |     <Aura: []>                   |
        <Aura: []>                    |     <HP: 10/10>                  |
        <HP: 10/10>                   |     <Energy: 0/2>                |
        <Energy: 0/3>                 |     <Hiddens>                    |
        <Hiddens>                     |     <Equipments>                 |
        <Equipments>                  |     <Statuses>                   |
        <Statuses>                    |   <3-Venti>                      |
      <3-Keqing>                      |     <Aura: []>                   |
        <Aura: []>                    |     <HP: 10/10>                  |
        <HP: 10/10>                   |     <Energy: 0/2>                |
        <Energy: 0/3>                 |     <Hiddens>                    |
        <Hiddens>                     |     <Equipments>                 |
          <KeqingTalent(0)>           |     <Statuses>                   |
        <Equipments>                  | <Hidden Statuses>                |
        <Statuses>                    |   <ChargedAttack>                |
    <Hidden Statuses>                 |   <PlungeAttack()>               |
      <ChargedAttack>                 |   <DeathThisRound()>             |
      <PlungeAttack()>                | <Combat Statuses>                |
      <DeathThisRound()>              | <Summons>                        |
    <Combat Statuses>                 | <Supports>                       |
    <Summons>                         | <Dices>                          |
    <Supports>                        | <Hand Cards>                     |
    <Dices>                           | <Deck Cards>                     |
    <Hand Cards>                      |   <NRE: 2>                       |
    <Deck Cards>                      |   <EmbraceOfWinds: 2>            |
      <TheBestestTravelCompanion: 2>  |   <WolfsGravestone: 2>           |
      <NRE: 2>                        |   <MagicGuide: 2>                |
      <TravelersHandySword: 2>        |   <WhiteTassel: 2>               |
      <ParametricTransformer: 2>      |   <TheBell: 2>                   |
      <MushroomPizza: 2>              |   <TamakushiCasket: 2>           |
      <LandsOfDandelion: 2>           |   <KingsSquire: 2>               |
      <WhereIsTheUnseenRazor: 2>      |   <WhereIsTheUnseenRazor: 2>     |
      <TheBell: 2>                    |   <JueyunGuoba: 2>               |
      <KnightsOfFavoniusLibrary: 2>   |   <AmosBow: 2>                   |
      <AThousandFloatingDreams: 2>    |   <KnightsOfFavoniusLibrary: 2>  |
      <SacrificialBow: 2>             |   <MysticalAbandon: 2>           |
      <GamblersEarrings: 2>           |   <CalxsArts: 2>                 |
      <QuickKnit: 2>                  |   <SacrificialGreatsword: 2>     |
      <VortexVanquisher: 2>           | <Publicly Used Cards>            |
      <MintyMeatRolls: 2>             | <Publicly Gained Cards>          |
    <Publicly Used Cards>             |                                  |
    <Publicly Gained Cards>           |                                  |
    ----------------------------------------------------------------------
    <Effects>
    ======================================================================

Although this section may appear complex at first glance,
upon closer examination,
you'll find it more intuitively understandable than it may initially seem.

The top row shows the some global game information shared by both players.

The middle section (divided into the left and right part),
contains all the information of each player.
The indentation marks the scope of each piece of information.

The bottom part lists upcoming effects to be executed.
Initially it's empty.

The printed game state, is the current state of the game you are focusing on.
In this case, the future of the game is yet to be decided.
To have the game *run*, you need to input commands to tell the CLI how much
you want the game to proceed forward.

* ``n`` is the command to take only one step forward, that is the minimal change
  to the game that can be isolated.
* ``a`` is the command to proceed the game until a player input is required.
  (the player input can be from any player that is either human or computer)

Meanwhile, some commands are provided to traverse the history of the current game.
The commands are ``bn`` and ``ba`` which functions similar to ``n`` and ``a``.

.. note::

    Once again, note that commands can only work if prompt is ``:>``

.. tip::

    You can enter nothing to repeat the last **valid** command executed.

Handle Player Input
-------------------

**Player Input** manipulates the human players in the game.
Actions like choosing the starting hand cards,
casting a skill are all **Player Input**.

When the prompt of CLI is ``::>``,
it means you are expected to input the **Player Input**.

The very first **Player Input** you might need to provide at the start of the game
is selecting the initial hand cards.

What you may see is:

.. code-block:: console

    Choices are:
    @0: SELECT_CARDS  |||  @1: END_ROUND
    Please choose id (0-1)
    ::> @

* ``@0: SELECT_CARDS`` means the 0th option is select cards to replace
* ``@1: END_ROUND`` take the current hand cards and keep them

If you input ``0``, choosing ``SELECT_CARDS`` you'll see something like:

.. code-block:: console

    Selections are:
    @0: <SacrificialBow, 2>  |||  @1: <VortexVanquisher, 1>  |||  @2: <GamblersEarrings, 2>
    e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
    ::> 

In this case, you need to input some dictionary-like text to represent the cards
you are to choose and replace.

.. note::

    ``<CardName, n>`` means there are ``n`` of ``CardName(s)``.

To replace all the ``SacrificialBow`` and one of ``GamblersEarrings``, I can input:
``0:2, 2:1``

After any **Player Input** is passed to the game,
the **Player Action** is printed out.
So after the input ``0:2, 2:1``, you'll see:

.. code-block:: console

    #### Player1 Action: CardsSelectAction(selected_cards={SacrificialBow: 2, GamblersEarrings: 1})

Then, you'll be able to proceed the game with ``a``, ``n`` or other commands.

Great, now you have officially made an impact on the game.
**Player Input** of other types follow a similar pattern.
You just need to keep the following note in your mind.

.. note::
    Once your prompt is ``::>``, every input you've made is not undoable.
    You have to complete the entire **Player Input** before being able to
    execute any commands.
