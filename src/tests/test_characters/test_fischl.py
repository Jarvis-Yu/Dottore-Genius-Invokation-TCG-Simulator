import unittest

from src.tests.test_characters.common_imports import *


class TestFischl(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Fischl,
        char_id=2,
        card=StellarPredator,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Fischl

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ELECTRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill deals 1 electro damage and summons Oz
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(OzSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(OzSummon).usages, 2)

    def test_elemental_burst(self):
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 8)
        self.assertEqual(p2c3.hp, 8)
        self.assertIn(Element.ELECTRO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

    def test_oz_summon(self):
        game_state = AddSummonEffect(Pid.P1, OzSummon).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(OzSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(OzSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertNotIn(OzSummon, p1.summons)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=StellarPredator,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 3}))
        ))
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(OzSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(OzSummon).usages, 2)

        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 5)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(OzSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(OzSummon).usages, 1)
