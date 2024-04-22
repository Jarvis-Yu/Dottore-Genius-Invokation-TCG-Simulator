import unittest

from .common_imports import *

class TestCrownOfWatatsumi(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, CrownOfWatatsumi).execute(base_state)
        base_state = grant_all_infinite_revival(base_state)
        base_state = replace_character(base_state, Pid.P1, Xingqiu, 1)
        base_state = simulate_status_dmg(base_state, 5, pid=Pid.P1)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CrownOfWatatsumi,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        self.assertIn(CrownOfWatatsumiStatus, p1_active_char(game_state).character_statuses)
        assert game_state.player1.characters.get_active_character_id() == 1

        # test healing can be accumulated correctly (according to actual amount healed)
        game_state = simulate_status_heal(game_state, 1, Pid.P1)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 1)
        self.assertEqual(crown_status.usages, 0)

        game_state = simulate_status_heal(game_state, 1, Pid.P1)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 2)
        self.assertEqual(crown_status.usages, 0)

        game_state = simulate_status_heal(game_state, 1, Pid.P1)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 0)
        self.assertEqual(crown_status.usages, 1)

        game_state = simulate_status_heal(game_state, 4, Pid.P1)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 2)
        self.assertEqual(crown_status.usages, 1)

        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1)
        game_state = simulate_status_heal(game_state, 1, Pid.P1)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 0)
        self.assertEqual(crown_status.usages, 2)

        # test dmg boost is running correctly
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        crown_status = p1_active_char(game_state).character_statuses.just_find_type(CrownOfWatatsumiStatus)
        self.assertEqual(crown_status.accumulated_healing, 0)
        self.assertEqual(crown_status.usages, 0)
