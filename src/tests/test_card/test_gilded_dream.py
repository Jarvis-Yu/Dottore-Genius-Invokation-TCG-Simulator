import unittest

from .common_imports import *

class TestGildedDreams(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            GildedDreams: 5,
        }))
        base_state = replace_character(base_state, Pid.P1, Venti, 1)
        base_state = replace_character(base_state, Pid.P1, Ningguang, 2)
        base_state = replace_character(base_state, Pid.P1, Nahida, 3)
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state

        # test Gilded Dreams generates dice as expected
        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GildedDreams,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 3}),
            ),
        ))
        dice_after = game_state.player1.dice
        dice_diff = dice_after - dice_before
        self.assertEqual(dice_diff[Element.ANEMO], 2)

        # test less dice generated for team with < 3 elements
        game_state = replace_character(game_state, Pid.P1, Venti, 3)
        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GildedDreams,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 3}),
            ),
        ))
        dice_after = game_state.player1.dice
        dice_diff = dice_after - dice_before
        self.assertEqual(dice_diff[Element.ANEMO], 1)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GildedDreams,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.PYRO: 3}),
            ),
        ))

        # test opponent's reaction triggers self active's Gilded Dreams
        cards_before = game_state.player1.hand_cards

        game_state = simulate_status_dmg(game_state, 1, Element.PYRO)
        g1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(GildedDreamsStatus)
        g2 = game_state.player1.characters.just_get_character(
            2
        ).character_statuses.just_find(GildedDreamsStatus)
        self.assertEqual(g1.usages, 2)
        self.assertEqual(g2.usages, 2)

        game_state = simulate_status_dmg(game_state, 1, Element.HYDRO)
        g1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(GildedDreamsStatus)
        g2 = game_state.player1.characters.just_get_character(
            2
        ).character_statuses.just_find(GildedDreamsStatus)
        self.assertEqual(g1.usages, 1)
        self.assertEqual(g2.usages, 2)

        cards_after = game_state.player1.hand_cards
        self.assertEqual(cards_after.num_cards(), cards_before.num_cards() + 1)

        # test Gilded Dreams usages resets every round
        game_state = next_round(game_state)
        g1 = game_state.player1.characters.just_get_character(
            1
        ).character_statuses.just_find(GildedDreamsStatus)
        self.assertEqual(g1.usages, 2)
