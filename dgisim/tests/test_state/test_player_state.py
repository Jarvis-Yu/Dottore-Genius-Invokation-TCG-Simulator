import unittest

from dgisim.src.card.card import *
from dgisim.src.card.cards import Cards
from dgisim.src.character.character import *
from dgisim.src.character.characters import Characters
from dgisim.src.mode import DefaultMode
from dgisim.src.state.player_state import PlayerState
from dgisim.src.support.support import Support

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
        player_state = PlayerState.from_deck(
            DefaultMode(),
            Characters.from_list([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
            Cards({Starsigns: 1, MondstadtHashBrown: 6}),
        )
        self.assertTrue(player_state.get_characters().num_characters(), 5)
        for i in range(1, 6):
            self.assertIsNotNone(player_state.get_characters().get_by_id(i))
        self.assertTrue(player_state.get_deck_cards().num_cards(), 7)

    def test_eq_and_hash(self):
        player_state1 = PlayerState.from_deck(
            DefaultMode(),
            Characters.from_list([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
            Cards({Starsigns: 1, MondstadtHashBrown: 6}),
        )
        player_state2 = PlayerState.from_deck(
            DefaultMode(),
            Characters.from_list([Keqing, RhodeiaOfLoch, Tighnari, Kaeya, Keqing]),
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
        assert player_state1._dices               == player_state2._dices
        assert player_state1._hand_cards          == player_state2._hand_cards
        assert player_state1._deck_cards          == player_state2._deck_cards
        self.assertEqual(player_state1, player_state2)
        self.assertEqual(hash(player_state1), hash(player_state2))
        self.assertNotEqual(player_state1, player_state3)
        self.assertNotEqual(hash(player_state1), hash(player_state3))
        self.assertNotEqual(player_state1, "player_state3")
