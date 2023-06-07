from __future__ import annotations

from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.state.game_state import GameState
from dgisim.src.agents import *
from dgisim.src.helper.level_print import GamePrinter

class CLISession:
    
    def __init__(self) -> None:
        self.reset_game()

    def reset_game(self) -> None:
        self._game_session = GameStateMachine(
            GameState.from_default(),
            HardCodedRandomAgent(),
            HardCodedRandomAgent(),
        )
        self._state_idx = 0

    def _help(self) -> None:
        print("a - to forward to an autostep")
        print("n - to forward to next step")
        print("ba - to previous autostep")
        print("bn - to previous step")
        print("h - to get help")
        print("q - to quit this session")
        print("- enter nothing to repeat last step")
        print("Note: any invalid commands are ignored")
        print("Definitions:")
        print("* autostep jumps to the next game-state where player interaction is required")
        print("* step jumps to the next game-state")

    def _equals_sep_bar(self) -> None:
        print("==================================================")

    def _welcome(self) -> None:
        print("Welcome to the Dottore Genius Invokation TCG Simulator CLI ver.")
        print("This is currently just a basic version for debugging only.")

    def run(self) -> None:
        self._equals_sep_bar()
        self._welcome()
        self._equals_sep_bar()
        self._help()
        self._equals_sep_bar()
        last_cmd = ""
        self._print_latest_game_state()
        wrong_cmd_counter = 0
        while last_cmd != "q":
            new_cmd = input("\n>>> ")
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
        self._print_game_state(self._game_session.get_game_state_at(index))

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
        p1_active = game_state.get_active_player_id().is_player1()
        action = self._game_session.get_last_action()
        assert action is not None
        print(f"**** Player{'1' if p1_active else '2'} Action:", action)

if __name__ == "__main__":
    cli_session = CLISession()
    cli_session.run()