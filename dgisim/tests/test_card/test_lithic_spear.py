import unittest

from .common_imports import *

class TestLithicSpear(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, LithicSpear).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Shenhe, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Albedo, char_id=2)
        base_state = replace_character(base_state, Pid.P1, YaeMiko, char_id=3)
        base_state = add_dmg_listener(base_state, Pid.P1)
        liyue_1 = base_state

        # equip The Lithic Spear with 1 Liyue Character only
        game_state = step_action(liyue_1, Pid.P1, CardAction(
            card=LithicSpear,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        p1ac_char_stts = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertIn(LithicGuardStatus, p1ac_char_stts)
        self.assertEqual(p1ac_char_stts.just_find(LithicGuardStatus).usages, 1)

        liyue_2 = replace_character(base_state, Pid.P1, Keqing, char_id=2)

        # equip The Lithic Spear with 2 Liyue Characters only
        game_state = step_action(liyue_2, Pid.P1, CardAction(
            card=LithicSpear,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        p1ac_char_stts = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertIn(LithicGuardStatus, p1ac_char_stts)
        self.assertEqual(p1ac_char_stts.just_find(LithicGuardStatus).usages, 2)

        liyue_2_equiped = game_state
        liyue_3 = replace_character(liyue_2, Pid.P1, Ganyu, char_id=3)

        # equip The Lithic Spear with 2 Liyue Characters only
        game_state = step_action(liyue_3, Pid.P1, CardAction(
            card=LithicSpear,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        p1ac_char_stts = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertIn(LithicGuardStatus, p1ac_char_stts)
        self.assertEqual(p1ac_char_stts.just_find(LithicGuardStatus).usages, 3)

        # test shield stacks capped at 3
        game_state = step_action(liyue_2_equiped, Pid.P1, CardAction(
            card=LithicSpear,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        p1ac_char_stts = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertIn(LithicGuardStatus, p1ac_char_stts)
        self.assertEqual(p1ac_char_stts.just_find(LithicGuardStatus).usages, 3)

        # test normal dmg boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.PHYSICAL)