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

    def run(self) -> None:
        print("==================================================")
        print("Welcome to the Dottore Genius Invokation TCG Simulator CLI ver.")
        print("This is currently just a basic version for debugging only.")
        print("==================================================")
        print("a - to forward to an autostep")
        print("n - to forward to next step")
        # print("ba - to previous autostep")
        # print("bn - to previous step")
        print("end - to end this session")
        print("- enter nothing to repeat last step")
        print("Note: any invalid commands are ignored")
        print("==================================================")
        last_cmd = ""
        self._print_latest_game_state()
        while last_cmd != "end":
            new_cmd = input("\n>>> ")
            if new_cmd == "":
                new_cmd = last_cmd

            if new_cmd == "a":
                self._game_session.auto_step()
                self._print_latest_game_state()
                self._game_session.one_step()
                self._print_latest_action()
            elif new_cmd == "n":
                if last_cmd != "a":
                    self._game_session.one_step()
                self._print_latest_game_state()

            if new_cmd != "":
                last_cmd = new_cmd
            # LATEST_TODO

    def _print_latest_game_state(self) -> None:
        game_state = self._game_session.get_game_state()
        game_state_dict = game_state.dict_str() 
        assert type(game_state_dict) is dict
        output = GamePrinter.dict_game_printer(game_state_dict)
        print(output)

    def _print_latest_action(self) -> None:
        action = self._game_session.get_last_action()
        assert action is not None
        print("**** Player Action:", action)

if __name__ == "__main__":
    cli_session = CLISession()
    cli_session.run()