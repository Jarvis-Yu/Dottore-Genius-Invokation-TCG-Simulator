import unittest

from .common_imports import *

class TestShadowOfTheSandKing(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ShadowOfTheSandKing: 5,
        }))

        game_state = base_state

        # test Shadow artifact draws card as expected
        cards_before = game_state.player1.hand_cards
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ShadowOfTheSandKing,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 1}),
            ),
        ))
        cards_after = game_state.player1.hand_cards
        self.assertEqual(cards_after.num_cards(), cards_before.num_cards())  # play artifact -1, draw + 1

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ShadowOfTheSandKing,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.PYRO: 1}),
            ),
        ))

        # test opponent's reaction triggers self active's Shadow artifact
        cards_before = game_state.player1.hand_cards

        game_state = simulate_status_dmg(game_state, 1, Element.PYRO)
        s1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(ShadowOfTheSandKingStatus)
        s2 = game_state.player1.characters.just_get_character(
            2
        ).character_statuses.just_find(ShadowOfTheSandKingStatus)
        self.assertEqual(s1.usages, 1)
        self.assertEqual(s2.usages, 1)

        game_state = simulate_status_dmg(game_state, 1, Element.HYDRO)
        s1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(ShadowOfTheSandKingStatus)
        s2 = game_state.player1.characters.just_get_character(
            2
        ).character_statuses.just_find(ShadowOfTheSandKingStatus)
        self.assertEqual(s1.usages, 0)
        self.assertEqual(s2.usages, 1)

        cards_after = game_state.player1.hand_cards
        self.assertEqual(cards_after.num_cards(), cards_before.num_cards() + 1)

        # test Shadow artifact usages resets every round
        game_state = next_round(game_state)
        s1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(ShadowOfTheSandKingStatus)
        self.assertEqual(s1.usages, 1)
