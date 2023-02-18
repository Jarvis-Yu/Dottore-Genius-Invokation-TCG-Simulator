import unittest

from dgisim.src.state.game import GameState


class TestGameState(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(GameState.from_default(), GameState.from_default())


if __name__ == "__main__":
    unittest.main()
