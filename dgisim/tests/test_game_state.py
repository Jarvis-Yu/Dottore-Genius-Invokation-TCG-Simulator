import unittest
import random

from dgisim.src.mode import DefaultMode
from dgisim.src.state.game_state import GameState
from dgisim.src.state.player_state import PlayerState


class TestGameState(unittest.TestCase):

    def test_eq_and_hash(self):
        game_state = GameState.from_default()
        other_state = game_state.factory().build()
        self.assertEqual(game_state, other_state)
        self.assertEqual(hash(game_state), hash(other_state))

        random.seed(100)
        game_state1 = GameState.from_players(
            mode=DefaultMode(),
            player1=PlayerState.example_player(DefaultMode()),
            player2=PlayerState.example_player(DefaultMode()),
        )
        random.seed(100)
        game_state2 = GameState.from_players(
            mode=DefaultMode(),
            player1=PlayerState.example_player(DefaultMode()),
            player2=PlayerState.example_player(DefaultMode()),
        )
        random.seed()
        self.assertEqual(game_state1, game_state2)
        self.assertEqual(hash(game_state1), hash(game_state2))
        self.assertNotEqual(game_state1, "game_state1")
