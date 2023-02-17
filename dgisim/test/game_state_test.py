import unittest

from dgisim.src.state.game import GameState


class TestGameStateMachine(unittest.TestCase):
    _intitialState = GameState.from_default()

    def test_first_step(self):
        pid = self._intitialState.waiting_for()
        self.assertIsNone(pid)
        state = self._intitialState.run()
        pass


if __name__ == "__main__":
    unittest.main()
