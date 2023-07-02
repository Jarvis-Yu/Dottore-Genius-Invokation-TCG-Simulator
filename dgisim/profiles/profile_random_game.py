import cProfile

from dgisim.src.card.card import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.state.game_state import GameState
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.agents import RandomAgent

def _random_play(repeats: int) -> None:
    for i in range(repeats):
        state_machine = GameStateMachine(
            GameState.from_default(),
            RandomAgent(),
            RandomAgent(),
        )
        game_end_phase = state_machine.get_game_state().get_mode().game_end_phase()
        try:
            state_machine.step_until_phase(game_end_phase)
        except Exception:
            print(GamePrinter.dict_game_printer(state_machine.get_game_state().dict_str()))
            raise Exception("Test failed")


if __name__ == "__main__":
    repeats = 100
    cProfile.run("_random_play(repeats)", filename="game_play.prof")#, filename="game_profile_result")