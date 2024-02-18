import unittest

from src.tests.test_characters.common_imports import *


class TestChongyun(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Chongyun,
        char_id=2,
        card=SteadyBreathing,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(ChonghuasFrostFieldStatus, game_state.player1.combat_statuses)
        status = game_state.player1.combat_statuses.just_find(ChonghuasFrostFieldStatus)
        self.assertEqual(status.usages, 2)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 7)
        self.assertIs(dmg.element, Element.CRYO)

    def test_chonghuas_frost_field_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, ChonghuasFrostFieldStatus).execute(self.BASE_GAME)
        game_state = replace_character(game_state, Pid.P1, Bennett, char_id=1)  # check infusion
        game_state = replace_character(game_state, Pid.P1, Keqing, char_id=2)  # check infusion doens't override
        game_state = replace_character(game_state, Pid.P1, Tighnari, char_id=3)  # check infucion not on bow
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)

        # check infusion works normally
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.element, Element.CRYO)
        self.assertEqual(dmg.damage, 2)

        # check infusion infusion doesn't override prior infusion
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = remove_aura(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.element, Element.ELECTRO)

        # check infusion doesn't apply to bow
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.element, Element.PHYSICAL)

        # usages decrease per round
        status = game_state.player1.combat_statuses.just_find(ChonghuasFrostFieldStatus)
        self.assertEqual(status.usages, 2)

        game_state = next_round(game_state)
        status = game_state.player1.combat_statuses.just_find(ChonghuasFrostFieldStatus)
        self.assertEqual(status.usages, 1)

        game_state = next_round(game_state)
        self.assertNotIn(ChonghuasFrostFieldStatus, game_state.player1.combat_statuses)

    def test_talent_card(self):
        game_state = AddCombatStatusEffect(Pid.P1, ChonghuasFrostFieldStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SteadyBreathing,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3})),
        ))
        self.assertNotIn(ChonghuasFrostFieldStatus, game_state.player1.combat_statuses)
        self.assertIn(ChonghuasFrostFieldEnhancedStatus, game_state.player1.combat_statuses)
        status = game_state.player1.combat_statuses.just_find(ChonghuasFrostFieldEnhancedStatus)
        self.assertEqual(status.usages, 2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.CRYO)
        self.assertEqual(dmg.damage, 3)

    def test_chonghuas_frost_field_enhanced_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, ChonghuasFrostFieldEnhancedStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, Bennett, char_id=1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.CRYO)
        self.assertEqual(dmg.damage, 3)
