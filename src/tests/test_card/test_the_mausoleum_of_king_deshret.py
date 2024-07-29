import unittest

from .common_imports import *

SUPPORT = TheMausoleumOfKingDeshret
SUPPORT_STATUS = TheMausoleumOfKingDeshretSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

def forbidden_knowledge_count(game_state: GameState, pid: Pid = Pid.P2) -> int:
    return (
        game_state.get_player(pid).deck_cards[ForbiddenKnowledge]
        + game_state.get_player(pid).hand_cards[ForbiddenKnowledge]
    )

class TestTheMausoleumOfKingDeshret(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 2,
            Strategize: 2,
        }))
        base_state = replace_deck_cards(base_state, Pid.P2, Cards({Strategize: 30}))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({
            Strategize: 2,
            LiyueHarborWharf: 1,
            ShadowOfTheSandKing: 1,
        }))

        """ Precondition """
        with self.subTest("Precondition"):
            game_state = base_state
            game_state = end_round(game_state, Pid.P1)
            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            self.assertEqual(game_state.player2.hand_cards.num_cards(), 3 + 2)
            game_state = play_char_target_card(game_state, Pid.P2, ShadowOfTheSandKing, 1)
            self.assertEqual(game_state.player2.hand_cards.num_cards(), 5)
            game_state = play_support_card(game_state, Pid.P2, LiyueHarborWharf)
            game_state = next_round(game_state)
            self.assertEqual(
                game_state.player2.hand_cards.num_cards(),
                4 + game_state.mode.cards_per_round() + 2,
            )

        """ check it is triggered when 4 cards are drawn (by the opponenet) """
        with self.subTest("Oppo 4-Card Trigger"):
            game_state = base_state
            game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=1)
            self.assertIn(SUPPORT_STATUS, game_state.player1.supports)
            self.assertEqual(p1_support_status(game_state).usages, 0)

            # self card-draw doesn't not trigger the support
            game_state = play_dice_only_card(game_state, Pid.P1, Strategize)
            self.assertEqual(p1_support_status(game_state).usages, 0)
            game_state = end_round(game_state, Pid.P1)

            # oppo draws 2 + 2 cards, support adds 2 FK and adds combat status
            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            self.assertEqual(p1_support_status(game_state).usages, 2)
            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)

            self.assertEqual(game_state.player2.deck_cards.num_cards(), 28)
            self.assertEqual(game_state.player2.deck_cards[ForbiddenKnowledge], 2)
            self.assertIn(TheMausoleumOfKingDeshretStatus, game_state.player2.combat_statuses)

            # check action-round draw triggers
            game_state = play_char_target_card(game_state, Pid.P2, ShadowOfTheSandKing, 1)
            self.assertEqual(game_state.player2.deck_cards.num_cards(), 28)
            self.assertEqual(forbidden_knowledge_count(game_state, Pid.P2), 3)

            # check end-round support and game draws count (and status last one round only)
            game_state = play_support_card(game_state, Pid.P2, LiyueHarborWharf)
            game_state = next_round_with_great_omni(game_state)
            self.assertNotIn(TheMausoleumOfKingDeshretStatus, game_state.player2.combat_statuses)
            self.assertEqual(game_state.player2.deck_cards.num_cards(), 28)
            self.assertEqual(forbidden_knowledge_count(game_state, Pid.P2), 7)

            game_state = end_round(game_state, Pid.P1)
            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            self.assertEqual(game_state.player2.deck_cards.num_cards(), 26)
            self.assertEqual(forbidden_knowledge_count(game_state, Pid.P2), 7)

        """ check 2 + 1 + 2 draw adds the last FK from 2 = (1 + 1) """
        with self.subTest("Oppo 2+1+2 Trigger"):
            game_state = base_state
            game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=1)
            game_state = end_round(game_state, Pid.P1)

            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            game_state = play_char_target_card(game_state, Pid.P2, ShadowOfTheSandKing, 1)
            game_state = play_dice_only_card(game_state, Pid.P2, Strategize)
            self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
            self.assertEqual(game_state.player2.deck_cards.num_cards(), 28)
            self.assertEqual(forbidden_knowledge_count(game_state, Pid.P2), 3)

    def test_forbidden_knowledge(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ForbiddenKnowledge: 5}))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({Paimon: 30}))
        base_state = add_dmg_listener(base_state, Pid.P1)

        """ Check Forbidden Knowledge cannot be tuned """
        with self.subTest("FK not tunable"):
            game_state = base_state
            game_state = replace_character(game_state, Pid.P1, Ningguang)
            assert game_state.player1.dice[Element.PYRO] > 0
            self.assertRaises(
                Exception,
                lambda: game_state.action_step(Pid.P1, ElementalTuningAction(
                    card=ForbiddenKnowledge,
                    dice_elem=Element.PYRO,
                )),
            )

        """ Check Forbidden Knowledge deals 1 piercing damage and draws a card """
        with self.subTest("FK effects"):
            game_state = base_state
            game_state = play_dice_only_card(game_state, Pid.P1, ForbiddenKnowledge, cost=0)
            assert_last_dmg(
                self, game_state, Pid.P1,
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                amount=1,
                elem=Element.PIERCING,
                card=True,
            )
            self.assertEqual(game_state.player1.deck_cards.num_cards(), 29)
            self.assertEqual(game_state.player1.hand_cards[Paimon], 1)

            # check only one can be played per round
            self.assertIn(ForbiddenKnowledgeStatus, game_state.player1.combat_statuses)
            self.assertRaises(
                Exception,
                lambda: game_state.action_step(Pid.P1, CardAction(
                    card=ForbiddenKnowledge,
                    instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
                )),
            )

            # check can be played the next round
            game_state = next_round_with_great_omni(game_state)
            game_state = end_round(game_state, Pid.P2)
            game_state = play_dice_only_card(game_state, Pid.P1, ForbiddenKnowledge, cost=0)
