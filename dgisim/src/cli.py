"""
This file contains the CLI class.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Iterable, TypeVar

from .agents import *
from .action.action import PlayerAction
from .action.types import DecidedChoiceType
from .effect.structs import StaticTarget
from .game_state_machine import GameStateMachine
from .helper.hashable_dict import HashableDict
from .helper.level_print import GamePrinter
from .helper.quality_of_life import case_val
from .state.game_state import GameState
from .state.enums import Pid

__all__ = [
    "CLISession",
]

_T = TypeVar("_T")


class _GameMode(Enum):
    PVP = "PVP"
    PVE = "PVE"
    EVE = "EVE"


class CLISession:
    _PS1 = ":> "

    def __init__(self) -> None:
        self._mode: _GameMode = _GameMode.PVE
        self.reset_game()

    def reset_game(self) -> None:
        if self._mode is _GameMode.EVE:
            self._game_session = GameStateMachine(
                GameState.from_default(),
                RandomAgent(),
                RandomAgent(),
            )
        elif self._mode is _GameMode.PVE:
            self._game_session = GameStateMachine(
                GameState.from_default(),
                CustomChoiceAgent(
                    prompt_handler=self.prompt_handler,
                    choose_handler=self.game_action_chooser,
                    dict_choose_handler=self.dict_action_chooser,
                    any_handler=self.chooser
                ),
                RandomAgent(),
            )
        elif self._mode is _GameMode.PVP:
            self._game_session = GameStateMachine(
                GameState.from_default(),
                CustomChoiceAgent(
                    prompt_handler=self.prompt_handler,
                    choose_handler=self.game_action_chooser,
                    dict_choose_handler=self.dict_action_chooser,
                    any_handler=self.chooser
                ),
                CustomChoiceAgent(
                    prompt_handler=self.prompt_handler,
                    choose_handler=self.game_action_chooser,
                    dict_choose_handler=self.dict_action_chooser,
                    any_handler=self.chooser
                ),
            )
        self._state_idx = 0

    def _help(self) -> None:
        print("Commands:")
        print("a    - to forward to an autostep")
        print("n    - to forward to next step")
        print("ba   - to previous autostep")
        print("bn   - to previous step")
        print("h    - to get help")
        print("q    - to quit this session")
        print("     - enter nothing to repeat last step")
        print("rst  - to reset game session (and choose next game mode)")
        print()
        print("Note: any invalid commands are ignored")
        print()
        print("Definitions:")
        print("- autostep - jumps to the next game-state where player interaction is required")
        print("- step - jumps to the next game-state")

    def _equals_sep_bar(self) -> None:
        print("==================================================")

    def _welcome(self) -> None:
        print("Welcome to the Dottore Genius Invokation TCG Simulator CLI ver.")
        print("This is currently just a basic version for debugging only.")

    def _mode_prompt(self) -> None:
        print("Please choose the cli mode:")
        mode = self.chooser(mode for mode in _GameMode)
        assert isinstance(mode, _GameMode)
        self._mode = mode
        self.reset_game()

    @classmethod
    def prompt_handler(cls, info_type: str, prompt: str) -> None:
        prompt_type = case_val(
            info_type == "",
            "",
            f"[{info_type}]"
        )
        print(f"{prompt_type} -- {prompt}")

    @classmethod
    def _display_choice(cls, choice: Any) -> str:
        import inspect
        if isinstance(choice, Enum):
            return choice.name
        if inspect.isclass(choice):
            return choice.__name__
        if isinstance(choice, StaticTarget):
            return f"id={choice.id} in Player{choice.pid.value}'s {choice.zone.name}"
        return str(choice)

    @classmethod
    def chooser(cls, choices: Iterable[Any]) -> Any:
        choices_map = dict(enumerate(choices))
        choices_display = "  |||  ".join(
            f"@{i}: {cls._display_choice(choice)}"
            for i, choice in choices_map.items()
        )
        final_choice: int = -1
        id_range = (0, len(choices_map) - 1)
        while final_choice < 0 or final_choice >= len(choices_map):
            try:
                print("Choices are:")
                print(choices_display)
                print(f"Please choose id ({id_range[0]}-{id_range[1]})")
                choice = input(f":{cls._PS1}@")
                print()
                final_choice = int(choice)
            except KeyboardInterrupt:
                print()
                cls.prompt_handler("exit", "Bye...")
                exit(0)
            except:
                cls.prompt_handler("error", f"Last input is invalid!")
                final_choice = -1
                continue
        return choices_map[final_choice]

    @classmethod
    def game_action_chooser(cls, choices: Iterable[DecidedChoiceType]) -> DecidedChoiceType:
        choice = cls.chooser(choices)
        return choice

    @classmethod
    def dict_action_chooser(cls, choices: dict[_T, int], optional: bool) -> None | dict[_T, int]:
        def parse(s: str) -> dict[int, int]:
            pairs = s.split(',')
            return dict(
                (int(tokens[0]), int(tokens[1]))
                for tokens in (
                    pair.split(':')
                    for pair in pairs
                )
            )

        tuple_list = list(tuple(item) for item in choices.items())
        original_dict = HashableDict((i, val) for i, val in enumerate(choices.values()))
        dict_display = "  |||  ".join(
            f"@{i}: <{cls._display_choice(pair[0])}, {pair[1]}>"
            for i, pair in enumerate(tuple_list)
            if pair[1] > 0  # type: ignore
        )
        prompt = 'e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3'
        selected_dict: dict[int, int]
        while True:
            try:
                print("Selections are:")
                print(dict_display)
                print(prompt)
                choice = input(f":{cls._PS1}")
                print()
                choice = choice.replace(' ', '')
                if optional and choice == '':
                    return None
                selected_dict = parse(choice)
            except KeyboardInterrupt:
                print()
                cls.prompt_handler("exit", "Bye...")
                exit(0)
            except:
                cls.prompt_handler("error", f"Last input is invalid!")
                continue
            if (original_dict - selected_dict).all_val_non_negative():
                break
            cls.prompt_handler("error", f"Last input is invalid!")
            continue
        return dict(  # type: ignore
            (tuple_list[i][0], j)  # type: ignore
            for i, j in selected_dict.items()
        )

    def run(self) -> None:
        self._equals_sep_bar()
        self._welcome()
        self._equals_sep_bar()
        self._help()
        self._equals_sep_bar()
        self._mode_prompt()
        self._equals_sep_bar()
        last_cmd = ""
        self._print_latest_game_state()
        wrong_cmd_counter = 0
        while last_cmd != "q":
            new_cmd = input(f"\n{self._PS1}")
            if new_cmd == "":
                new_cmd = last_cmd

            if new_cmd == "a":
                next_idx = self._game_session.next_action_index(self._state_idx)
                if self._state_idx >= next_idx:
                    # should actually proceed
                    if self._game_session.game_end():
                        print("[i] Game has ended")
                    else:
                        self._game_session.auto_step()
                        self._print_latest_game_state()
                        self._state_idx = self._game_session.latest_index()
                        self._game_session.one_step()
                        self._print_latest_action()
                else:
                    # get history
                    self._state_idx = next_idx
                    self._print_game_state_at(self._state_idx)
            elif new_cmd == "n":
                next_idx = self._game_session.next_index(self._state_idx)
                if self._state_idx >= next_idx:
                    # should actually proceed
                    if self._game_session.game_end():
                        print("[i] Game has ended")
                    else:
                        self._game_session.one_step()
                        self._print_latest_game_state()
                        self._state_idx = self._game_session.latest_index()
                else:
                    # get history
                    self._state_idx = next_idx
                    self._print_game_state_at(self._state_idx)
            elif new_cmd == "ba":
                prev_idx = self._game_session.prev_action_index(self._state_idx)
                if self._state_idx <= prev_idx:
                    print("[i] Cannot go back anymore")
                else:
                    self._state_idx = prev_idx
                    self._print_game_state_at(self._state_idx)
            elif new_cmd == "bn":
                prev_idx = self._game_session.prev_index(self._state_idx)
                if self._state_idx <= prev_idx:
                    print("[i] Cannot go back anymore")
                else:
                    self._state_idx = prev_idx
                    self._print_game_state_at(self._state_idx)
            elif new_cmd == "h":
                self._help()
            elif new_cmd == "q":
                pass
            elif new_cmd == "rst":
                self._mode_prompt()
                self._equals_sep_bar()
                self._print_latest_game_state()
            else:
                wrong_cmd_counter += 1
                if wrong_cmd_counter >= 3:
                    self._help()
                    wrong_cmd_counter = 0
                continue

            wrong_cmd_counter = 0
            if new_cmd != "":
                last_cmd = new_cmd

    def _print_latest_game_state(self) -> None:
        self._print_game_state(self._game_session.get_game_state())

    def _print_game_state_at(self, index: int) -> None:
        game_state = self._game_session.get_game_state_at(index)
        self._print_game_state(game_state)
        action = self._game_session.action_at(index)
        if action is not None:
            self._print_action(action, game_state)
        print(f"#### [{index}/{self._game_session.curr_index()}] in game history")

    def _print_game_state(self, game_state: GameState) -> None:
        game_state.waiting_for()
        game_state_dict = game_state.dict_str()
        assert type(game_state_dict) is dict
        output = GamePrinter.dict_game_printer(game_state_dict)
        print(output)

    def _print_latest_action(self) -> None:
        idx = self._game_session.get_last_action_idx()
        assert idx is not None
        game_state = self._game_session.get_game_state_at(idx)
        action = self._game_session.get_last_action()
        if action is None:
            return
        self._print_action(action, game_state)

    def _print_action(self, action: PlayerAction, game_state: GameState) -> None:
        waiting_for = game_state.get_phase().waiting_for(game_state)
        assert waiting_for is not None
        p1_active = waiting_for is Pid.P1
        print(f"#### Player{'1' if p1_active else '2'} Action:", action)


if __name__ == "__main__":
    cli_session = CLISession()
    cli_session.run()
