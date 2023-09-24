.. _cli:

CLI (Command Line Interface)
============================

``dgisim`` has a built-in CLI for developers to manually play and test the game.

CLI Session Basics
------------------------------

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
To choose a new mode or start a new game, you need to run ``rst`` when prompt
is ``:>``.
