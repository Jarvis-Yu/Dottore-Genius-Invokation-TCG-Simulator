# Dottore Genius Invokation TCG Simulator

A Genshin Impact Genius Invokation TCG simulator intended to be used for AI training (for now).

The simulator is modeled as a finite state machine, where all game states are immutable.

- [Dottore Genius Invokation TCG Simulator](#dottore-genius-invokation-tcg-simulator)
  - [Development Milestones](#development-milestones)
  - [Currently Working On](#currently-working-on)
  - [CLI (How to try the simulator)](#cli-how-to-try-the-simulator)
  - [Future Plans](#future-plans)
  - [Interested in the Project](#interested-in-the-project)
  - [QA](#qa)

## Development Milestones

The aim of my first stage is to make the games runs with characters Rhodeia of Loch, Kaeya and Keqing,
with limited action cards and all omni dices.

- [x] Set up the framework for maintaining game states
- [x] Implement game phase of Card Selection (card selection at the start of the game)
- [x] Implement game phase of Starting Hand Select Phase (select active character)
- [x] Implement game phase of Roll (Dice) Phase (roll dices between rounds)
- [x] Implement game phase of Action Phase (players beat each other)
  - [ ] Implement all cards (9/184 implemented)
  - [ ] Implement all characters (3/48 implemented)
  - [x] Implement all reactions
- [x] Implement game phase of End Phase (summons and some support card or statuses take action)
- [x] Implement game phase of Game End Phase (one player wins or draw)
- [x] Implement CLI for better debugging experience
- [x] Implement lazy player agent for minimal testing purposes
- [x] Implement random player agent for testing purposes
- [ ] Implement greedy player agent for testing purposes
- [ ] Implement player action validity checker
  - [ ] Provide dices request information (for card/skill/swap)  <- ***WIP***
  - [ ] Provide dices request information that is preprocessed by statuses
  - [ ] Check dices player chosen satisfies request
  - [ ] Check if card action is used on valid target (and card exists)
  - [ ] Check if swap action is fast or combat action, and target is valid
  - [ ] Check if burst is only casted when the player has the energy
- [ ] Implement player action choices provider

The second stage of development will be focusing on including all action cards.

The third stage is to implement real dices system.

The final stage is to include more characters and eventually all.

## Currently Working On

Implementing the combat system in the action phase.

## CLI (How to try the simulator)

There's currently a CLI available to try this project.

Here are the steps for you to follow to try the developing project.

For Windows based systems:  *(deprecated now, needs contribution)*

1. Clone the project
2. Make sure your Python version >= 3.10.11
3. Run scripts\venv.ps1
4. After venv is installed, run ./scripts/cli.ps1

For unix based systems (MacOS, Linux...):  *(up-to-date)*

1. Clone the project
2. Make sure your Python version >= 3.10.11
3. Set up the environment with `venv` or otherwise
4. If you don't know how to setup `venv`, google it or run the following commands under the project directory

```sh
source ./scripts/venv.sh
pip install -r requirements.txt
```

5. With the environment set up run the following command to run the CLI

```sh
./scripts/cli.sh
```

Note that currently when playing with the CLI, it is the hardcoded agents that are playing the game.
You are just the observer overseeing their gameplay.

## Future Plans

The fully developed project will be published to PyPI (beta versions will be available once all that
are left is adding more characters)

Once this project is done, I'll be reading relative papers and develop an AI for this game. The AI
is supposed to be used for learning strategies and making decks, but not against another player
directly.

## Interested in the Project

I suggest you start reading the code from `dgisim/tests/test_game_state_machine.py`,
which contains tests for the whole game flow.

## QA

Why are you implementing the simulator that is already under development on github?

- It entertains me to design and code.

So you don't want any teammates?

- Well, collaborators are welcomed. If you have the intention to join, please contact me.

How to contact you?

- I assume you can find my email somewhere ~~(hint: `git log`)~~
