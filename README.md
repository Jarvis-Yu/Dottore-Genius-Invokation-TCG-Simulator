# Dottore Genius Invokation TCG Simulator

[![PyPI Version](https://img.shields.io/pypi/v/dgisim.svg)](https://pypi.org/project/dgisim/)
![Python 3.10](https://img.shields.io/badge/python->=3.10-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/badge.svg?branch=master)](https://coveralls.io/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator?branch=master)
[![license](https://img.shields.io/github/license/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator)](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/LICENSE)

A Genshin Impact Genius Invokation TCG simulator intended to be used for AI training.

- [**Documentation**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/wiki/v0.3.dev0-Documentation)
- [**Source code**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator)
- [**Contributing**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/dev_readme.md)
- [**Game design**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/state_machine_design.md)
- [**Bug reports**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/issues)
- [**Discord server**](https://discord.gg/arammB6BEY)

This package aims to help programmers code things based on Genius Invokation
TCG with ease. e.g. AI, desktop application, website...

The simulator is modeled as a finite state machine, where all game states are immutable.
Optimizations are done to make sure immutability doesn't impact performance.

Basic rules of Genius Invokation TCG can be found on [Fandom](https://genshin-impact.fandom.com/wiki/Genius_Invokation_TCG).

## Installation

Please make sure your Python version `>= 3.10` before installing.

```
pip install dgisim
```

## Simple Start With CLI

### Run Locally

Once installed, you may start by trying the CLI to play the game first.

You might want to run a simple python program like this:

```py
from dgisim import CLISession

session = CLISession()
session.run()
```

### Run Remotely

You may try the CLI online on [Google Colab](https://colab.research.google.com/drive/1h6ckw4LQ2jMEnZAs9QQo6tHjCwWnR8KD?usp=sharing)

### CLI Simple Usages

See CLI's [README](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/cli_readme.md)
for showcase and explanations of the CLI.

## Customize Player Agents _(Important For AI Or Building App)_

A player agent controls all actions of a player in a game.

To implement a player agent, all you need to do is to inherit the abstact class
`PlayerAgent` and implement the method `choose_action()`.

A simple example is shown below, the agent implemented choose 3 random cards to
replace during _Card Select Phase_, and normal attacks until there's no dices
for it during _Action Phase_.

```py
class ExampleAgent(PlayerAgent):
    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        latest_game_state: GameState = history[-1]
        game_mode: Mode = latest_game_state.get_mode()
        curr_phase: Phase = latest_game_state.get_phase()

        if isinstance(curr_phase, game_mode.card_select_phase):
            cards_to_select_from: Cards = latest_game_state.get_player(pid).get_hand_cards()
            _, selected_cards = cards_to_select_from.pick_random_cards(num=3)
            return CardsSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, game_mode.action_phase):
            me: PlayerState = latest_game_state.get_player(pid)
            active_character: Character = me.just_get_active_character()
            dices: ActualDices = me.get_dices()
            # check if dices are enough for normal attack
            normal_attack_cost = active_character.skill_cost(CharacterSkill.NORMAL_ATTACK)
            dices_to_use = dices.basically_satisfy(normal_attack_cost)
            if dices_to_use is not None:
                # normal attack if dices can be found to pay for normal attack
                return SkillAction(
                    skill=CharacterSkill.NORMAL_ATTACK,
                    instruction=DiceOnlyInstruction(dices=dices_to_use),
                )
            return EndRoundAction()  # end round otherwise

        else:
            raise NotImplementedError(f"actions for {curr_phase} not defined yet")
```

The above example manually tests if there are dices for some action, which is
straightforward but takes time to exhaust all options.
So the `GameState` can return an `ActionGenerator` object which automatically
provides you with all valid actions to choose from.
More about `ActionGenerator` will be updated later.

You can find more examples of implementations of `PlayerAgent` in `dgisim/src/agents.py`.
The `RandomAgent` in `agents.py` is implemented based on `ActionGenerator` mentioned above
to make random but valid decision.

Once you defined your own player agent, you can test it against the `RandomAgent`.

```py
# generates a random initial game state with random decks
init_game_state = GameState.from_default()
# forms a `game`; YourCustomAgent is Player 1, RandomAgent is Player 2
game_state_machine = GameStateMachine(init_game_state, YourCustomAgent(), RandomAgent())
# runs the game and prints who wins
game_state_machine.run()
# gets full history of the game
history: tuple[GameState, ...] = game_state_machine.get_history()
# gets only history of game states that are right before a player action
act_history: tuple[GameState, ...] = game_state_machine.get_action_history()
# any GameState can be printed with nice formatting directly
print(history[-1])
```

## Features

This simulator is modeled as a finite state machine, which means any intermediate state can be
standalone and be used to proceed to other states.

The `GameState` class represents some game state in the state machine. It uses passed in
`Phase` object to determine how to transform to another state, which means the game flow is
highly customizable. (Default Mode and some Heated Battle Modes are implemented already)

Everything in the `GameState` object are immutable, so traversing game history
and exploring different branches of possibilities in the future are not error-prone.
The simulator did optimizations for immutability.
The unchanged data are shared among neighbouring game states.

`GameState` implements `__eq__` and `__hash__`, enabling you to use any game state as a key in a
dictionary, and discover game states on different 'game branches' being actually the same.

An `ActionGenerator` can be returned by any valid `GameState` to help
generate valid player actions.

## Development Milestones

Currently a full game can be played with any combination of the characters and cards implemented.

- [x] Implement all game phases (Action Phase, End Phase...)
- [ ] Implement all cards (59/200 implemented) ([details](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/progress.md))
- [ ] Implement all characters with their talent cards (16/54 implemented) ([details](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/progress.md))
- [x] Implement all reactions, death handling, revival handling etc.
- [x] Implement all game logics to support the implemented cards and characters
- [x] Implement interactive CLI for better debugging experience
- [x] Ensure 99% unittest coverage checking behaviour of characters and cards
- [x] Implement lazy player agent for minimal testing purposes
- [x] Implement random player agent for testing purposes
- [x] Implement player action validity checker
- [x] Implement player action choices provider

## Future Plans

I have the plan to implement a simple cross-platform GUI interface for the simulator.
But that will be in a separate repo.

Once this project is done, I'll be reading relative papers and develop an AI for this game.
The AI is supposed to be used for learning strategies and making decks,
but not against another player directly.
