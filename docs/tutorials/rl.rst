.. _rl-tutorial:

RL-related Tutorial
===================

This page contains a general tutorial on how to use ``dgisim`` for RL.

.. note::

    Linear game simulation environment is provided,
    but if you want to apply Monte-Carlo Tree Search or other non-linear methods,
    you need to implement your own game simulation environment (for now).

    |GameState| is perfectly suitable for efficient MCTS, please
    refer to documentations on |GameState| for more details.

Linear Game Environment
-----------------------

Currently |LinearEnv| is provided for RL environment for linear simulation process.

A simple example of using |LinearEnv| is as follows:

.. code-block:: python3

    from dgisim import LinearEnv

    env = LinearEnv()
    rl_net = ...  # your RL network

    for _ in range(100):
        env.reset()
        game_state, encoded_state, reward, turn, done = env.view()

        while not done:
            action = rl_net(encoded_state)  # this is just an example, your network
                                            # doesn't have to directly generate an action
            game_state, encoded_state, reward, turn, done = env.step(action)

The default behaviour of |LinearEnv| is to generate a random game state at the
beginning of each episode.
You may also reset the environment with two specific decks for each player by
calling ``.reset_with_decks(deck1, deck2)``.

.. note::

    ``.reset()`` follows the last way of resetting the environment.
    If you want to reset the environment with random deck after calling
    ``.reset_with_decks()``, you should call ``.reset_random()``.

.. note::

    If you want to get the decks used by the players in the current episode,
    you need to call ``.extract_decks()`` on the initial game state right after
    resetting. (As the game progress, some information on the decks are lost,
    thus you may not get the complete decks by calling ``.extract_decks()`` on
    later game states.)

    .. code-block:: python3

        env.reset()
        initial_game_state = env.full_view()
        deck1, deck2 = initial_game_state.extract_decks()

``LinearEnv.step()`` takes either a list of int as the encoded player action
that might be an output of a NN, or a |PlayerAction| object.
If the action failed to be decoded or is invalid in other ways, the same
game state will be returned with a customizable penalty (default to -0.1).

The ``reward`` is:

* If Game Ends:
    * ``1`` if player 1 wins
    * ``0`` if draw
    * ``-1`` if player 2 wins
* If Invalid Action:
    * ``-0.1`` if player 1 makes an invalid action
    * ``0.1`` if player 2 makes an invalid action
* Otherwise:
    * ``0``

All the return values above can be customized by passing values to |LinearEnv|
when initializing.

Game Encoding Details
---------------------

A |GameState| object is encoded as a 1D vector of length 2682.

The encoding for a |GameState| object is ordered as follows:

* ``4`` ints for basic game information (game mode, game phase, round number, active player id)
* ``839`` ints for player 1 information (deck, hand, characters, statuses, summons, supports...)
* ``839`` ints for player 2 information
* ``1000`` ints for all pending effects to be executed (useful when facing death swap)

The encoding for a |PlayerState| object is ordered as follows:

* ``4`` ints for basic information (player phase, right for consecutive action...)
* ``22`` ints for dice
* ``40`` ints for hand cards (designed for 40 cards max for future expansion)
* ``40`` ints for deck cards
* ``40`` ints for publicly used cards (cards used that your opponent can see)
* ``40`` ints for publicly gained cards (cards gained that your opponent can see)
* ``43`` ints for initial deck (containing 3 characters and 30 cards)
* ``414`` ints for characters
* ``70`` ints for hidden statuses (whether plunge attack is available...)
* ``70`` ints for combat statuses (designed for 10 statuses max)
* ``28`` ints for summons
* ``28`` ints for supports

The encoding for a ``Character`` object is ordered as follows:

* ``9`` ints for basic information (character type, character element, weapon type...)
* ``10`` ints for elemental application / aura
* ``28`` ints for hidden statuses (empty for most characters, but a few need this)
* ``91`` ints for character statuses

The 1000 ints for pending effects can encoding a maximum of 40 effects, which
is enough for most cases.
(only 1 game state out of over 1,000,000 game states in hundreds of random plays
can reach 23 pending effects)

Custom Encoding
---------------

If you want ot use your own way of encoding, you may instantialize your own
|EncodingPlan| object and pass it to |LinearEnv| when initializing.

Please refer to the documentations on |EncodingPlan| for more details.

.. |EncodingPlan| replace:: :py:mod:`EncodingPlan <dgisim.encoding.encoding_plan.EncodingPlan>`
.. |GameState| replace:: :py:mod:`GameState <dgisim.state.game_state.GameState>`
.. |LinearEnv| replace:: :py:mod:`LinearEnv <dgisim.env.linear_env.LinearEnv>`
.. |PlayerAction| replace:: :py:mod:`PlayerAction <dgisim.action.action.PlayerAction>`
.. |PlayerState| replace:: :py:mod:`PlayerState <dgisim.state.player_state.PlayerState>`