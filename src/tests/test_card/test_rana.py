import unittest

from .common_imports import *

class TestRana(unittest.TestCase):
    def test_behaviour(self):
        base_state = replace_hand_cards(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Cards({Rana: 2}),
        )

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Rana,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        game_state = grant_all_infinite_revival(game_state)

        next_char_elem = game_state.player1.characters.get_nth_next_alive_character_in_activity_order(1).ELEMENT
        prev_dice_num = game_state.player1.dice[next_char_elem]

        game_state = replace_character(game_state, Pid.P1, Albedo, 1)

        # Non elemental skill cannot trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num)

        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num)

        # Elemental skill triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num + 1)

        # Can only trigger once per round
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num + 1)

        # Can be triggered again the next round (and only self skill triggers)
        game_state = next_round_with_great_omni(game_state)
        game_state = replace_character(game_state, Pid.P2, Albedo, 1)
        prev_dice_num = game_state.player1.dice[next_char_elem]
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        curr_dice_num = game_state.player1.dice[next_char_elem]
        self.assertEqual(curr_dice_num, prev_dice_num + 1)