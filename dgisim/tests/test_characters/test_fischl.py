import unittest

from dgisim.tests.test_characters.common_imports import *


class TestFischl(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Fischl,
        char_id=2,
        card=StellarPredator,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Fischl

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.NORMAL_ATTACK,
            dices=ActualDices({Element.ELECTRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill deals 1 electro damage and summons Oz
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.ELEMENTAL_SKILL1,
            dices=ActualDices({Element.ELECTRO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())
        self.assertIn(OzSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(OzSummon).usages, 2)

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dices=ActualDices({Element.ELECTRO: 3}),
        )
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 6)
        self.assertEqual(p2c2.get_hp(), 8)
        self.assertEqual(p2c3.get_hp(), 8)
        self.assertIn(Element.ELECTRO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

    def test_oz_summon(self):
        game_state = AddSummonEffect(Pid.P1, OzSummon).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())
        self.assertIn(OzSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(OzSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())
        self.assertNotIn(OzSummon, p1.get_summons())

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=StellarPredator,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.ELECTRO: 3}))
        ))
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())
        self.assertIn(OzSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(OzSummon).usages, 2)

        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.NORMAL_ATTACK)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())
        self.assertIn(OzSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(OzSummon).usages, 1)
