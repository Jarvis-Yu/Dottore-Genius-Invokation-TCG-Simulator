import random
import unittest

from src.tests.test_characters.common_imports import *


def p1_guoba(game_state: GameState) -> GuobaSummon:
    return game_state.player1.summons.just_find(GuobaSummon)


def p1_pyronade(game_state: GameState) -> PyronadoStatus:
    return game_state.player1.combat_statuses.just_find(PyronadoStatus)


class TestXiangling(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Xiangling,
        char_id=2,
        card=Crossfire,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.PYRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL, normal_attack=True)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.PYRO: 3}),
        )
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 0)
        self.assertIn(GuobaSummon, game_state.player1.summons)
        self.assertEqual(p1_guoba(game_state).usages, 2)

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.PYRO: 4}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.PYRO,
            num=1, elemental_burst=True,
        )
        self.assertIn(PyronadoStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_pyronade(game_state).usages, 2)

    def test_guoba_summon(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = add_summon(game_state, Pid.P1, GuobaSummon)
        assert p1_guoba(game_state).usages == 2

        game_state = next_round(game_state)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PYRO, summon=True, num=1,
            clear=True,
        )
        self.assertEqual(p1_guoba(game_state).usages, 1)

        game_state = next_round(game_state)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PYRO, summon=True, num=1,
            clear=True,
        )
        self.assertNotIn(GuobaSummon, game_state.player1.summons)

    def test_pyronado_status(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_combat_status(base_state, Pid.P1, PyronadoStatus)
        base_state = add_aura_remover(base_state, Pid.P2)
        base_state = replace_character(base_state, Pid.P1, RhodeiaOfLoch, char_id=1)
        base_state = grant_all_infinite_revival(base_state)
        assert p1_pyronade(base_state).usages == 2

        """ check all skill triggers pyronado """
        game_state = base_state
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO, status=True, num=2)
        self.assertEqual(p1_pyronade(game_state).usages, 1)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO, status=True)
        self.assertNotIn(PyronadoStatus, game_state.player1.combat_statuses)

        game_state = add_combat_status(game_state, Pid.P1, PyronadoStatus)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO, status=True)
        self.assertEqual(p1_pyronade(game_state).usages, 1)

        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO, status=True)
        self.assertNotIn(PyronadoStatus, game_state.player1.combat_statuses)

    def talent_card(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)

        """ check skill 2 deals additional dmg """
        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, Crossfire, cost=ActualDice({Element.PYRO: 3}))
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.PYRO, num=1,
            elemental_skill=True, clear=True,
        )
        self.assertIn(GuobaSummon, game_state.player1.summons)
        self.assertEqual(p1_guoba(game_state).usages, 2)

        # and again
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.PYRO, num=1,
            elemental_skill=True, clear=True,
        )
        self.assertIn(GuobaSummon, game_state.player1.summons)
        self.assertEqual(p1_guoba(game_state).usages, 2)
