import unittest
import random

from src.dgisim.mode import DefaultMode
from src.dgisim.state.game_state import GameState
from src.dgisim.state.player_state import PlayerState


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

    def test_deck_extraction(self):
        game_state = GameState.from_default()
        deck1, deck2 = game_state.get_decks()
        self.assertEqual(len(deck1.chars), 3)
        self.assertEqual(len(deck2.chars), 3)
        self.assertEqual(sum(deck1.cards.values()), 30)
        self.assertEqual(sum(deck2.cards.values()), 30)
