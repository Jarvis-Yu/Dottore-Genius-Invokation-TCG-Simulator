import random
import unittest

from src.tests.test_characters.common_imports import *


class TestThoma(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Thoma,
        char_id=2,
        card=ASubordinatesSkills,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.PYRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.PYRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PYRO,
            num=1, elemental_skill=True,
        )
        self.assertIn(BlazingBarrierStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 1)

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.PYRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PYRO,
            num=1, elemental_burst=True,
        )
        self.assertIn(BlazingBarrierStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 1)
        self.assertIn(ScorchingOoyoroiStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 2)

    def test_blazing_barrier_status(self):
        base_state = self.BASE_STATE

        # check stack max to 3 usages
        game_state = base_state
        game_state = add_combat_status(game_state, Pid.P1, BlazingBarrierStatus)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 1)
        game_state = add_combat_status(game_state, Pid.P1, BlazingBarrierStatus)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 2)
        game_state = add_combat_status(game_state, Pid.P1, BlazingBarrierStatus)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 3)
        game_state = add_combat_status(game_state, Pid.P1, BlazingBarrierStatus)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 3)

        # check absorb dmg as expected
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=0)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
        self.assertNotIn(BlazingBarrierStatus, game_state.player1.combat_statuses)

    def test_scorching_ooyoroi_status(self):
        base_state = self.BASE_STATE
        base_state = add_combat_status(base_state, Pid.P1, ScorchingOoyoroiStatus)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = replace_character(base_state, Pid.P1, Lyney, 1)
        base_state = replace_character(base_state, Pid.P1, Ningguang, 3)
        self.assertEqual(base_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 2)

        """ check non-normal attack cannot trigger """
        game_state = base_state
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 2)

        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 2)

        """ check normal attack can trigger """
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.PYRO, status=True)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 1)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertNotIn(ScorchingOoyoroiStatus, game_state.player1.combat_statuses)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, normal_attack=True)
        assert_last_dmg(self, game_state, Pid.P1, last_index=0, amount=1, elem=Element.PYRO, status=True)
        self.assertEqual(game_state.player1.combat_statuses.just_find(BlazingBarrierStatus).usages, 2)

    def test_talent_card(self):
        base_state = self.BASE_STATE
        base_state = recharge_energy_for(base_state, Pid.P1)

        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, ASubordinatesSkills)
        self.assertIn(ScorchingOoyoroiStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ScorchingOoyoroiStatus).usages, 3)
