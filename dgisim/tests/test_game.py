import unittest

from dgisim.src.state.game_state import GameState


class TestGameState(unittest.TestCase):

    def test_eq(self):
        game_state = GameState.from_default()
        other_state = game_state.factory().build()
        self.assertEqual(game_state, other_state)
