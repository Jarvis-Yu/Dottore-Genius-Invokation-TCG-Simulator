import unittest

from src.dgisim.agents import RandomAgent
from src.dgisim.encoding.encoding_plan import encoding_plan
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.state.game_state import GameState

class TestEncoding(unittest.TestCase):
    def test_encoding(self):
        import os, sys, time
        optional_repeats = os.getenv("ENCODING_RUNS")
        optional_show_progress = os.getenv("SHOW_PROGRESS")
        repeats: int
        show_progress: bool
        try:
            repeats = int(optional_repeats) if optional_repeats is not None else 5
            show_progress = (
                int(optional_show_progress) != 0
                if optional_show_progress is not None
                else False
            )
        except:
            repeats = 5
            show_progress = False

        game_states: list[GameState] = []
        prev_progress = ""
        for i in range(repeats):
            if show_progress:
                print(end='\b' * len(prev_progress))
                prev_progress = f"[{i}/{repeats}]"
                print(end=prev_progress)
                sys.stdout.flush()
            gsm = GameStateMachine(GameState.from_default(), RandomAgent(), RandomAgent())
            gsm.run()
            game_states.extend(gsm.get_history())

        if not show_progress:
            encodings = set([
                len(game_state.encoding(encoding_plan))
                for game_state in game_states
            ])
            self.assertEqual(len(encodings), 1, encodings)
        else:
            encodings = set()
            for i, game_state in enumerate(game_states):
                encodings.add(len(game_state.encoding(encoding_plan)))
                print(end='\b' * len(prev_progress))
                prev_progress = f"[{i}/{len(game_states)}]" + f"({list(encodings)[0]})"
                print(end=prev_progress)
                sys.stdout.flush()
            print(end='\b' * len(prev_progress))
            sys.stdout.flush()
            self.assertEqual(len(encodings), 1, encodings)
