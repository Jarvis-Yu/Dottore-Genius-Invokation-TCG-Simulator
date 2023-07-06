import random
from typing import Any, Optional, Iterable, TYPE_CHECKING, TypeVar

from .action.action import *
from .action.action_generator import *
from .action.action_generator_generator import *
from .action.types import DecidedChoiceType
from .card.card import *
from .character.character_skill_enum import CharacterSkill
from .dices import AbstractDices, ActualDices
from .effect.effect import *
from .element.element import Element
from .phase.default.action_phase import ActionPhase
from .phase.default.card_select_phase import CardSelectPhase
from .phase.default.end_phase import EndPhase
from .phase.default.roll_phase import RollPhase
from .phase.default.starting_hand_select_phase import StartingHandSelectPhase
from .player_agent import PlayerAgent
from .state.enums import PID
from .state.game_state import GameState


class NoneAgent(PlayerAgent):
    pass


class LazyAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardsSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(char_id=1)

        elif isinstance(curr_phase, RollPhase):
            return EndRoundAction()

        elif isinstance(curr_phase, ActionPhase):
            return EndRoundAction()

        else:
            raise Exception("No Action Defined")


class PuppetAgent(PlayerAgent):
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

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        assert self._actions, f"no action at game state:\b{history[-1]}"
        return self._actions.pop(0)

    def clear(self) -> None:
        self._actions = []

    def __str__(self) -> str:
        return f"PuppetAgent[{', '.join(str(action) for action in self._actions)}]"


class RandomAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def _card_select_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        phase = game_state.get_phase()
        act_gen = phase.action_generator(game_state, pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _starting_hand_select_phase(
            self,
            history: list[GameState],
            pid: PID
    ) -> PlayerAction:
        game_state = history[-1]
        phase = game_state.get_phase()
        act_gen = phase.action_generator(game_state, pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _roll_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        phase = game_state.get_phase()
        act_gen = phase.action_generator(game_state, pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
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
                _, choice = choices.pick_random_dices(random.randint(0, choices.num_dices()))
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()

    def _action_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        phase = game_state.get_phase()
        act_gen = phase.action_generator(game_state, pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def _end_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        phase = game_state.get_phase()
        act_gen = phase.action_generator(game_state, pid)
        assert act_gen is not None
        player_action = self._random_action_generator_chooser(act_gen)
        return player_action

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            return self._card_select_phase(history, pid)
        elif isinstance(curr_phase, StartingHandSelectPhase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, RollPhase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, ActionPhase):
            return self._action_phase(history, pid)
        elif isinstance(curr_phase, EndPhase):
            return self._end_phase(history, pid)

        raise NotImplementedError

_T = TypeVar("_T")

class CustomChoiceAgent(RandomAgent):
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

    def _handle_abstract_dices(
            self,
            action_generator: ActionGenerator,
            abstract_dices: AbstractDices,
    ) -> ActionGenerator:
        optional_choice = action_generator.dices_available().basically_satisfy(abstract_dices)
        if optional_choice is None:
            raise Exception(f"There's not enough dices for {repr(abstract_dices)} from "
                            + f"{action_generator.dices_available()} at game_state:"
                            + f"{action_generator.game_state}")
        while True:
            choice = optional_choice
            self._prompt_handler("info", f"auto chosen dices are {repr(choice)}")
            self._prompt_handler("info", "If you want to choose manually, please input below")
            manual_choice = self._dict_choose_handler(
                action_generator.dices_available().as_dict(),  # type: ignore
                True,
            )
            if manual_choice is not None:
                selected_dices = ActualDices(manual_choice)  # type: ignore
                if (
                        selected_dices.is_legal()
                        and (action_generator.dices_available() - selected_dices).is_legal()
                ):
                    try:
                        action_generator.choose(selected_dices)  # type: ignore
                    except:
                        print("error", f"{repr(selected_dices)} cannot fulfill {repr(abstract_dices)}")
                        continue
                    choice = selected_dices
                    break
                else:
                    print("error", f"{manual_choice} is illegal")
            else:
                break
        return action_generator.choose(choice)

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
                choice = self._choose_handler(choices)
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, AbstractDices):
                action_generator = self._handle_abstract_dices(action_generator, choices)
            elif isinstance(choices, Cards):
                _, choice = choices.pick_random_cards(random.randint(0, choices.num_cards()))
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, ActualDices):
                _, choice = choices.pick_random_dices(random.randint(0, choices.num_dices()))
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()
