
from dgisim.src.state.game_state import GameState
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.agents import *

def auto_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:  # pragma: no cover
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(">>> ")
    return gsm.get_game_state()