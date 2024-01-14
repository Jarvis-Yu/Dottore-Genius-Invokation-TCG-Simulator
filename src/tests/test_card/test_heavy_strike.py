import unittest

from .common_imports import *

class TestHeavyStrike(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            HeavyStrike: 3,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P2, Kaeya, 1)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_dmg_listener(base_state, Pid.P2)

        # test heavy strike cannot be used by the opponent
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=HeavyStrike,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1})),
        ))
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIn(HeavyStrikeStatus, p1_active_char(game_state).character_statuses)

        # test self charged attack gets +2 boost
        game_state = end_round(game_state, Pid.P2)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 10}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)

        # test non-charged attack gets +1 boost
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=HeavyStrike,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 9}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)

        # test status cannot survive the next round
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=HeavyStrike,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = next_round(game_state)
        self.assertNotIn(HeavyStrikeStatus, p1_active_char(game_state).character_statuses)
