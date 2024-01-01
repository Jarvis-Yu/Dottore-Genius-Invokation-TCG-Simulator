import unittest

from src.tests.test_characters.common_imports import *


class TestJean(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Jean,
        char_id=2,
        card=LandsOfDandelion,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Jean

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill deals 3 anemo damage and force forward swap
        game_state = apply_elemental_aura(self.BASE_GAME, Element.PYRO, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ANEMO: 3}),
        )
        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 7)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertFalse(p2c1.elemental_aura.has_aura())
        self.assertIn(Element.PYRO, p2c2.elemental_aura)
        self.assertIn(Element.PYRO, p2c3.elemental_aura)
        self.assertEqual(p2cs.get_active_character_id(), 2)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and generates status
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = simulate_status_dmg(game_state, 4, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 3, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 2, pid=Pid.P1, char_id=3)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ANEMO: 4}),
        )
        p1 = game_state.player1
        p1cs = p1.characters
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertEqual(p1cs.just_get_character(1).hp, 8)
        self.assertEqual(p1cs.just_get_character(2).hp, 9)
        self.assertEqual(p1cs.just_get_character(3).hp, 10)
        self.assertIn(DandelionFieldSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(DandelionFieldSummon).usages, 2)

    def test_dandelion_field_summon(self):
        game_state = AddSummonEffect(Pid.P1, DandelionFieldSummon).execute(self.BASE_GAME)
        game_state = apply_elemental_aura(game_state, Element.ELECTRO, Pid.P2)
        game_state = simulate_status_dmg(game_state, 3, pid=Pid.P1)
        game_state = next_round(game_state)
        p1 = game_state.player1
        p1ac = p1.just_get_active_character()
        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 9)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertFalse(p2c1.elemental_aura.has_aura())
        self.assertIn(Element.ELECTRO, p2c2.elemental_aura)
        self.assertIn(Element.ELECTRO, p2c3.elemental_aura)
        self.assertEqual(p1ac.hp, 8)
        self.assertIn(DandelionFieldSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(DandelionFieldSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.player1
        self.assertNotIn(DandelionFieldSummon, p1.summons)

    def test_talent_card(self):
        base_state = fill_energy_for_all(self.BASE_GAME)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=LandsOfDandelion,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 4}))
        ))
        base_state = skip_action_round_until(base_state, Pid.P1)

        # test non-anemo damage doesn't get boost
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)

        # test summon doesn't get ANEMO boost
        game_state = next_round(base_state)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)

        # test jean elemental skill (anemo damage) does get ANEMO boost
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = step_swap(game_state, Pid.P2, 1)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)

        # test teammate gets boost
        game_state = replace_character(base_state, Pid.P1, Venti, 3)
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)

        # test teammate gets no boost if Jean dies
        game_state = replace_character(base_state, Pid.P1, Venti, 3)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1)
        game_state = step_action(game_state, Pid.P1, DeathSwapAction(char_id=3))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
