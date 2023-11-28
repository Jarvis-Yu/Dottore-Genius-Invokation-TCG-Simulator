"""
This file contains different implementations of PlayerAgents.
"""
import random
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, TypeVar, cast

from .action.action import *
from .action.enums import ActionType
from .action.action_generator import *
from .action.action_generator_generator import *
from .action.types import DecidedChoiceType
from .card.card import *
from .card.cards import Cards
from .dice import AbstractDice, ActualDice
from .effect.effect import *
from .element import Element
from .phase.default.action_phase import ActionPhase
from .phase.default.card_select_phase import CardSelectPhase
from .phase.default.end_phase import EndPhase
from .phase.default.roll_phase import RollPhase
from .phase.default.starting_hand_select_phase import StartingHandSelectPhase
from .player_agent import PlayerAgent
from .state.enums import Pid
from .state.game_state import GameState


__all__ = [
    "CustomChoiceAgent",
    "LazyAgent",
    "NoneAgent",
    "PuppetAgent",
    "RandomAgent",
]


class NoneAgent(PlayerAgent):
    """
    A dummy agent that doesn't do anything.
    This means any call to `.choose_action()` results in an exception.
    """
    pass


class LazyAgent(PlayerAgent):
    """
    A player agent that only end round whenever possible.
    It can also reluctantly perform death swaps.
    """
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        mode = game_state.get_mode()
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, mode.card_select_phase):
            _, selected_cards = game_state.get_player(
                pid
            ).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardsSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, mode.starting_hand_select_phase):
            return CharacterSelectAction(char_id=1)

        elif isinstance(curr_phase, mode.roll_phase):
            return DiceSelectAction(selected_dice=ActualDice({}))

        elif isinstance(curr_phase, mode.action_phase)  \
                or isinstance(curr_phase, mode.end_phase):
            action_generator = game_state.action_generator(pid)
            assert action_generator is not None
            action_types = action_generator.choices()
            assert isinstance(action_types, tuple)
            if ActionType.END_ROUND in action_types:
                return EndRoundAction()
            assert ActionType.SWAP_CHARACTER in action_types and game_state.death_swapping()
            choices = action_types
            while True:
                action_generator = action_generator.choose(random.choice(choices))
                assert action_generator is not None
                if action_generator.filled():
                    break
                else:
                    choices = cast(tuple, action_generator.choices())
            return action_generator.generate_action()

        else:  # pragma: no cover
            raise Exception("No Action Defined")


class PuppetAgent(PlayerAgent):
    """
    A player agent that gives the game PlayerActions passed into the object by
    the user.

    This agent is mainly used for controlled testing.
    """

    def __init__(self, actions: Optional[list[PlayerAction]] = None) -> None:
        """
        :param actions: initial actions that will be executed from left to right.
        """
        if actions is None:
            self._actions = []
        else:  # pragma: no cover
            self._actions = actions

    def inject_action(self, action: PlayerAction) -> None:
        """
        Push an action to right end.
        """
        self._actions.append(action)

    def inject_front_action(self, action: PlayerAction) -> None:
        """
        Push an action to left end.
        """
        self._actions.insert(0, action)

    def inject_actions(self, actions: list[PlayerAction]) -> None:
        """
        Push actions to right end.
        """
        self._actions += actions

    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        assert self._actions, f"no action at game state:\b{history[-1]}"
        return self._actions.pop(0)

    def clear(self) -> None:
        """
        Clears all pending actions.
        """
        self._actions = []

    def __str__(self) -> str:
        return f"PuppetAgent[{', '.join(str(action) for action in self._actions)}]"


class RandomAgent(PlayerAgent):
    """
    A player agent that make purely random (but of course valid) acions.
    """
    _NUM_PICKED_CARDS = 3

    def _card_select_phase(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        act_gen = game_state.action_generator(pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _starting_hand_select_phase(
            self,
            history: list[GameState],
            pid: Pid
    ) -> PlayerAction:
        game_state = history[-1]
        act_gen = game_state.action_generator(pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _roll_phase(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        act_gen = game_state.action_generator(pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
                game_state = action_generator.game_state
                if game_state.get_phase() == game_state.get_mode().roll_phase() and random.random() < 0.8:
                    choices = tuple(c for c in choices if c is not ActionType.END_ROUND)
                choice = random.choice(choices)
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, AbstractDice):
                optional_choice = action_generator.dice_available().smart_selection(
                    choices,
                    action_generator.game_state.get_player(action_generator.pid).get_characters(),
                )
                if optional_choice is None:
                    raise Exception(f"There's not enough dice for {choices} from "  # pragma: no cover
                                    + f"{action_generator.dice_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                choice = optional_choice
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, Cards):
                _, choice = choices.pick_random_cards(random.randint(0, choices.num_cards()))
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, ActualDice):
                game_state = action_generator.game_state
                wanted_elems = game_state.get_player(
                    action_generator.pid
                ).get_characters().all_elems()
                if game_state.get_phase() == game_state.get_mode().roll_phase():
                    choice = ActualDice(dict(
                        (elem, choices[elem])
                        for elem in choices.elems()
                        if not (elem is Element.OMNI or elem in wanted_elems)
                    ))
                else:
                    _, choice = choices.pick_random_dice(random.randint(0, choices.num_dice()))
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()

    def _action_phase(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        act_gen = game_state.action_generator(pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _end_phase(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        act_gen = game_state.action_generator(pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        mode = game_state.get_mode()
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, mode.card_select_phase):
            return self._card_select_phase(history, pid)
        elif isinstance(curr_phase, mode.starting_hand_select_phase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, mode.roll_phase):
            return self._roll_phase(history, pid)
        elif isinstance(curr_phase, mode.action_phase):
            return self._action_phase(history, pid)
        elif isinstance(curr_phase, mode.end_phase):
            return self._end_phase(history, pid)

        raise NotImplementedError


_T = TypeVar("_T")


class CustomChoiceAgent(RandomAgent):  # pragma: no cover
    """
    A player agent used by CLI, it requires several Callables passed in, in order
    to make a decision.
    """

    def __init__(
            self,
            prompt_handler: Callable[[str, str], None],
            choose_handler: Callable[[Iterable[DecidedChoiceType]], DecidedChoiceType],
            dict_choose_handler: Callable[[dict[_T, int], bool], None | dict[_T, int]],
            any_handler: Callable[[Iterable[Any]], Any],
    ) -> None:
        self._prompt_handler = prompt_handler
        self._choose_handler = choose_handler
        self._dict_choose_handler = dict_choose_handler
        self._any_handler = any_handler

    def _dict_class_choose_handler(
            self,
            action_generator: ActionGenerator,
            choices: ActualDice | Cards,
            default_choice: None | ActualDice | Cards = None,
    ) -> ActualDice | Cards:
        base_selection: ActualDice | Cards
        if isinstance(choices, ActualDice):
            base_selection = action_generator.dice_available()
        else:
            base_selection = action_generator.hand_cards_available()
        choice = default_choice
        while True:
            if default_choice is not None:
                self._prompt_handler("info", f"auto-choice is {repr(default_choice)}")
                self._prompt_handler("info", "Enter nothing if you agree with the auto-choice")
            manual_choice = self._dict_choose_handler(
                choices.to_dict(),  # type: ignore
                default_choice is not None,
            )
            if manual_choice is not None:
                if isinstance(choices, ActualDice):
                    selection = ActualDice(manual_choice)  # type: ignore
                elif isinstance(choices, Cards):
                    selection = Cards(manual_choice)  # type: ignore
                else:
                    raise ValueError(f"choices has type {type(choices)} which is not caught!")
                assert type(selection) == type(base_selection)
                if selection.is_legal() and (base_selection - selection).is_legal():  # type: ignore
                    try:
                        action_generator.choose(selection)
                    except:
                        self._prompt_handler("error", f"{repr(selection)} not valid")
                        continue
                    choice = selection
                    break
                else:
                    self._prompt_handler("error", f"{repr(selection)} not illegal")
            else:
                break
        assert choice is not None
        return choice

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
                choice = self._choose_handler(choices)
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, AbstractDice):
                optional_choice = action_generator.dice_available().smart_selection(
                    choices,
                    action_generator.game_state.get_player(action_generator.pid).get_characters(),
                )
                if optional_choice is None:
                    raise Exception(f"There's not enough dice for {repr(choices)} from "
                                    + f"{action_generator.dice_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                self._prompt_handler("info", f"You need to pay for {repr(choices)}")
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.dice_available(),
                    optional_choice,
                )
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, Cards):
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.hand_cards_available(),
                )
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, ActualDice):
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.dice_available(),
                )
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()
