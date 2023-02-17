import unittest

from dgisim.src.state.game import GameState
from dgisim.src.helper.level_print import level_print, INDENT


class TestGameStateMachine(unittest.TestCase):
    _intitialState = GameState.from_default()

    def test_first_step(self):
        pid = self._intitialState.waiting_for()
        self.assertIsNone(pid)
        state1 = self._intitialState.run()
        print(level_print({
            "state0": self._intitialState.to_string(INDENT),
            "state1": state1.to_string(INDENT),
        }))
        pass


if __name__ == "__main__":
    unittest.main()
