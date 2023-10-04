import unittest

from .common_imports import *


class TestSumeruCity(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SumeruCity: 1,
            ThunderingPenance: 1,
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice({
            Element.OMNI: 8,
            Element.ANEMO: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Keqing, char_id=1)
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SumeruCity,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 2})),
        ))

        # not triggered when dice > cards
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 8)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDice({
            Element.OMNI: 3,
        }))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 2)

        # not triggered when dice > cards
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 5)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, ActualDice({
            Element.OMNI: 3,
        }))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 2)

        state_2_2 = game_state  # state with 2 cards and 2 OMNI dice

        # triggered when dice == cards, normal attack
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, ActualDice({
            Element.OMNI: 2,
        }))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 2)

        # triggered when dice == cards, use skill that consumes card
        game_state = state_2_2
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDice({
            Element.OMNI: 2,
        }))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 1)

        # triggered when dice == cards, use talent card (keqing skill generated)
        game_state = state_2_2
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LightningStiletto,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget.from_player_active(game_state, Pid.P1),
            )
        ))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 1)

        # triggered when dice == cards, use talent card (keqing skill generated)
        game_state = state_2_2
        self.assertEqual(game_state.get_player1().get_dice().num_dice(), 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderingPenance,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(game_state.get_player1().get_hand_cards().num_cards(), 0)

        # check can only be triggered once
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 2}))
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({NRE: 2}))
        self.assertRaises(Exception, lambda: step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            ActualDice({Element.OMNI: 2}),
        ))

        # check can be triggered when cards > dice
        game_state = replace_hand_cards(state_2_2, Pid.P1, Cards({NRE: 2, Liben: 1}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, ActualDice({
            Element.OMNI: 2,
        }))
