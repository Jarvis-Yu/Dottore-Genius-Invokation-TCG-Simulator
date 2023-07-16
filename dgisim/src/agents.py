"""
This file contains different implementations of PlayerAgents.
"""
import random
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, TypeVar

from .action.action import *
from .action.enums import ActionType
from .action.action_generator import *
from .action.action_generator_generator import *
from .action.types import DecidedChoiceType
from .card.card import *
from .card.cards import Cards
from .dices import AbstractDices, ActualDices
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
    A dummy agent.
    """
    pass


class LazyAgent(PlayerAgent):
    """
    A player agent that only end round whenever possible.
    """
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid
            ).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardsSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(char_id=1)

        elif isinstance(curr_phase, RollPhase):
            return EndRoundAction()

        elif isinstance(curr_phase, ActionPhase):
            return EndRoundAction()

        else:  # pragma: no cover
            raise Exception("No Action Defined")


class PuppetAgent(PlayerAgent):
    """
    A player agent that gives the game PlayerActions passed into the object by
    the user.

    This agent is meaningly used for controlled testing.
    """

    def __init__(self, actions: Optional[list[PlayerAction]] = None) -> None:
        if actions is None:
            self._actions = []
        else:
            self._actions = actions

    def inject_action(self, action: PlayerAction) -> None:
        self._actions.append(action)

    def inject_front_action(self, action: PlayerAction) -> None:
        self._actions.insert(0, action)

    def inject_actions(self, actions: list[PlayerAction]) -> None:
        self._actions += actions

    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        assert self._actions, f"no action at game state:\b{history[-1]}"
        return self._actions.pop(0)

    def clear(self) -> None:
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
            elif isinstance(choices, AbstractDices):
                optional_choice = action_generator.dices_available().basically_satisfy(choices)
                if optional_choice is None:
                    raise Exception(f"There's not enough dices for {choices} from "
                                    + f"{action_generator.dices_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                choice = optional_choice
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, Cards):
                _, choice = choices.pick_random_cards(random.randint(0, choices.num_cards()))
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, ActualDices):
                game_state = action_generator.game_state
                wanted_elems = game_state.get_player(
                    action_generator.pid
                ).get_characters().all_elems()
                if game_state.get_phase() == game_state.get_mode().roll_phase():
                    choice = ActualDices(dict(
                        (elem, choices[elem])
                        for elem in choices.elems()
                        if not(elem is Element.OMNI or elem in wanted_elems)
                    ))
                else:
                    _, choice = choices.pick_random_dices(random.randint(0, choices.num_dices()))
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
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            return self._card_select_phase(history, pid)
        elif isinstance(curr_phase, StartingHandSelectPhase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, RollPhase):
            return self._roll_phase(history, pid)
        elif isinstance(curr_phase, ActionPhase):
            return self._action_phase(history, pid)
        elif isinstance(curr_phase, EndPhase):
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
            choices: ActualDices | Cards,
            default_choice: None | ActualDices | Cards = None,
    ) -> ActualDices | Cards:
        base_selection: ActualDices | Cards
        if isinstance(choices, ActualDices):
            base_selection = action_generator.dices_available()
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
                if isinstance(choices, ActualDices):
                    selection = ActualDices(manual_choice)  # type: ignore
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
            elif isinstance(choices, AbstractDices):
                optional_choice = action_generator.dices_available().basically_satisfy(choices)
                if optional_choice is None:
                    raise Exception(f"There's not enough dices for {repr(choices)} from "
                                    + f"{action_generator.dices_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                self._prompt_handler("info", f"You need to pay for {repr(choices)}")
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.dices_available(),
                    optional_choice,
                )
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, Cards):
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.hand_cards_available(),
                )
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, ActualDices):
                choice = self._dict_class_choose_handler(
                    action_generator,
                    action_generator.dices_available(),
                )
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()
