import unittest

from src.dgisim.agents import RandomAgent
from src.dgisim.encoding.encoding_plan import encoding_plan
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.state.game_state import GameState

class TestEncoding(unittest.TestCase):
    def test_encoding(self):
        game_states: list[GameState] = []
        for _ in range(2):
            gsm = GameStateMachine(GameState.from_default(), RandomAgent(), RandomAgent())
            gsm.run()
            game_states.extend(gsm.get_history())
        encodings = set([
            len(game_state.encoding(encoding_plan))
            for game_state in game_states
        ])
        self.assertEqual(len(encodings), 1)
