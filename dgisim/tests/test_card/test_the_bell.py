import unittest

from .common_imports import *

class TestTheBell(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, TheBell).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P1, ElementalResonanceEnduringRock).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, AratakiItto, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Albedo, char_id=2)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip The Bell
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=TheBell,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        # any skill triggers The Bell
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        self.assertIn(RebelliousShieldStatus, p1_combat_stts)
        self.assertEqual(p1_combat_stts.just_find(RebelliousShieldStatus).usages, 1)

        # any skill triggers The Bell but once per round only
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        self.assertIn(RebelliousShieldStatus, p1_combat_stts)
        self.assertEqual(p1_combat_stts.just_find(RebelliousShieldStatus).usages, 1)
        shield_1_state = game_state

        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        assert RebelliousShieldStatus not in p1_combat_stts
        # test can be used by geo resonance
        game_state = next_round_with_great_omni(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceEnduringRock,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.GEO: 1})),
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        self.assertIn(RebelliousShieldStatus, p1_combat_stts)
        self.assertEqual(p1_combat_stts.just_find(RebelliousShieldStatus).usages, 4)

        # test stack up to 2
        game_state = next_round_with_great_omni(shield_1_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        self.assertIn(RebelliousShieldStatus, p1_combat_stts)
        self.assertEqual(p1_combat_stts.just_find(RebelliousShieldStatus).usages, 2)

        game_state = next_round_with_great_omni(shield_1_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_stts = game_state.get_player1().get_combat_statuses()
        self.assertIn(RebelliousShieldStatus, p1_combat_stts)
        self.assertEqual(p1_combat_stts.just_find(RebelliousShieldStatus).usages, 2)

        # test normal dmg boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.PHYSICAL)