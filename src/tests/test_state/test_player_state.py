import unittest

from src.dgisim.card.card import *
from src.dgisim.card.cards import Cards
from src.dgisim.character.character import *
from src.dgisim.character.characters import Characters
from src.dgisim.mode import DefaultMode
from src.dgisim.state.player_state import PlayerState
from src.dgisim.support.support import Support

class SupportA(Support):
    ...

class SupportB(Support):
    ...

class TestPlayerState(unittest.TestCase):
    def test_is_mine(self):
        player_state = PlayerState.example_player(DefaultMode())
        player_state = player_state.factory().f_supports(
            lambda sps: sps.update_support(SupportA(sid=3))
        ).build()
        self.assertTrue(player_state.is_mine(SupportA(sid=3)))
        self.assertFalse(player_state.is_mine(SupportA(sid=2)))
        self.assertFalse(player_state.is_mine(SupportB(sid=3)))

    def test_from_deck(self):
        player_state = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
            Cards({Starsigns: 1, MondstadtHashBrown: 6}),
        )
        self.assertTrue(player_state.characters.num_characters(), 5)
        for i in range(1, 6):
            self.assertIsNotNone(player_state.characters.get_by_id(i))
        self.assertTrue(player_state.deck_cards.num_cards(), 7)

    def test_eq_and_hash(self):
        player_state1 = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
            Cards({Starsigns: 1, MondstadtHashBrown: 6}),
        )
        player_state2 = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
            Cards({Starsigns: 1, MondstadtHashBrown: 6}),
        )
        player_state3 = player_state2.factory().card_redraw_chances(8848).build()
        assert player_state1._phase               == player_state2._phase
        assert player_state1._card_redraw_chances == player_state2._card_redraw_chances
        assert player_state1._dice_reroll_chances == player_state2._dice_reroll_chances
        assert player_state1._characters          == player_state2._characters
        assert player_state1._combat_statuses     == player_state2._combat_statuses
        assert player_state1._summons             == player_state2._summons
        assert player_state1._supports            == player_state2._supports
        assert player_state1._dice               == player_state2._dice
        assert player_state1._hand_cards          == player_state2._hand_cards
        assert player_state1._deck_cards          == player_state2._deck_cards
        self.assertEqual(player_state1, player_state2)
        self.assertEqual(hash(player_state1), hash(player_state2))
        self.assertNotEqual(player_state1, player_state3)
        self.assertNotEqual(hash(player_state1), hash(player_state3))
        self.assertNotEqual(player_state1, "player_state3")
