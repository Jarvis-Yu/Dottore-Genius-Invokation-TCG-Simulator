import unittest

from .common_imports import *

class TestAdeptusTemptation(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            AdeptusTemptation: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = replace_character(base_state, Pid.P2, Kaeya, 1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = recharge_energy_for_all(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_dmg_listener(base_state, Pid.P2)

        game_state = base_state

        # check adeptus temptation cannot be triggered by self elemental skill
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AdeptusTemptation,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                dice=ActualDice({Element.PYRO: 1, Element.DENDRO: 1}),
            )
        ))

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIn(AdeptusTemptationStatus, p1_active_char(game_state).character_statuses)

        # check adeptus temptation cannot be triggered by opponent's burst
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIn(AdeptusTemptationStatus, p1_active_char(game_state).character_statuses)

        # check adeptus temptation can be triggered by self elemental burst
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)[-3:]
        from pprint import pprint
        self.assertEqual(dmgs[0].damage, 3)
        self.assertEqual(dmgs[1].damage, 3)
        self.assertEqual(dmgs[2].damage, 7)
        self.assertNotIn(AdeptusTemptationStatus, p1_active_char(game_state).character_statuses)

        # check adeptus temptation status disappears the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AdeptusTemptation,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                dice=ActualDice({Element.PYRO: 1, Element.DENDRO: 1}),
            )
        ))
        self.assertIn(AdeptusTemptationStatus, p1_active_char(game_state).character_statuses)
        game_state = next_round(game_state)
        self.assertNotIn(AdeptusTemptationStatus, p1_active_char(game_state).character_statuses)
