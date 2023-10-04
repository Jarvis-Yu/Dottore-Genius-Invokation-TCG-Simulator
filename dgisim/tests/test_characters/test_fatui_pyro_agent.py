import unittest

from dgisim.tests.test_characters.common_imports import *


class TestFatuiPyroAgent(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        FatuiPyroAgent,
        char_id=2,
        card=PaidInFull,
    )
    BASE_NO_STEALTH = RemoveCharacterStatusEffect(
        target=StaticTarget.from_char_id(Pid.P1, 2),
        status=StealthStatus,
    ).execute(BASE_GAME)
    assert type(BASE_GAME.get_player1().just_get_active_character()) is FatuiPyroAgent

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_NO_STEALTH,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        game_state = step_skill(
            self.BASE_NO_STEALTH,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 2)

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_NO_STEALTH)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.PYRO: 3}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())

    def test_passive(self):
        p1ac = self.BASE_GAME.get_player1().just_get_active_character()
        self.assertIn(StealthStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 2)

    def test_stealth_status(self):
        # boost normal attack
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 1)

        # boost elemental skill 1
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 2)

        # boost elemental burst
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.PYRO: 3}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 1)

        # takes damage
        game_state = add_damage_effect(self.BASE_GAME, 2, Element.ANEMO, Pid.P1, char_id=2)
        game_state = auto_step(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 9)
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 1)

    def test_talent_card(self):
        # talent provides 3 usages of Stealth Status
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=PaidInFull,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 3}))
        ))
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 3)

        # removes opponent aura and test status as shield
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = add_damage_effect(game_state, 2, Element.ANEMO, Pid.P1, char_id=2)
        game_state = auto_step(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 9)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 2)

        # test normal attack gains pyro infusion
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_character_statuses().just_find(StealthStatus).usages, 1)
