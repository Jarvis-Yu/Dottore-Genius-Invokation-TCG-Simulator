import unittest

from .common_imports import *

SUPPORT = Taroumaru
SUPPORT_STATUS = TaroumaruSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestTimmie(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 2}))
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards.from_dict_ordered({
            Paimon: 13,  # = 2 + 2 + 3 + 3 + 3
        }))

        """ check playing it evenly inserts 4 Taroumaru's Savings to deck """
        game_state = base_state
        game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=ActualDice({Element.CRYO: 1, Element.GEO: 1}))
        self.assertIn(SUPPORT_STATUS, game_state.player1.supports)
        self.assertEqual(
            game_state.player1.deck_cards,
            OrderedCards((
                *([Paimon] * 2),
                TaroumarusSavings,
                *([Paimon] * 2),
                TaroumarusSavings,
                *([Paimon] * 3),
                TaroumarusSavings,
                *([Paimon] * 3),
                TaroumarusSavings,
                *([Paimon] * 3),
            ))
        )
        self.assertNotIn(TaroumaruEnragedSummon, game_state.player1.summons)

        """ check playing two Taroumaru's Savings summons TaroumaruEnragedSummon """
        game_state = replace_hand_cards(game_state, Pid.P1, cards=Cards({TaroumarusSavings: 2}))
        game_state = replace_dice(game_state, Pid.P1, ActualDice.from_empty())
        self.assertEqual(p1_support_status(game_state, 1).usages, 0)

        # check taroumaru's savings gives one OMNI die
        game_state = play_dice_only_card(game_state, Pid.P1, TaroumarusSavings, cost=0)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)

        game_state = play_dice_only_card(game_state, Pid.P1, TaroumarusSavings, cost=0)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 2}))
        self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
        self.assertIn(TaroumaruEnragedSummon, game_state.player1.summons)
        self.assertEqual(game_state.player1.summons.just_find(TaroumaruEnragedSummon).usages, 2)

        """ check Taroumaru Enraged deals 2 PHYSICAL dmg per round (2 usages) """
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        self.assertEqual(game_state.player1.summons.just_find(TaroumaruEnragedSummon).usages, 1)

        game_state = next_round(game_state)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        self.assertNotIn(TaroumaruEnragedSummon, game_state.player1.summons)
