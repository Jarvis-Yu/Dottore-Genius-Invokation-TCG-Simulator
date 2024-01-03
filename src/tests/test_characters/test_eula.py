import unittest

from src.tests.test_characters.common_imports import *


class TestEula(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Eula,
        char_id=2,
        card=WellspingOfWarLust,
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
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(GrimheartStatus, p1_active_char(game_state).character_statuses)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(LightfallSwordSummon, game_state.player1.summons)

    def test_grimheart_status(self):
        game_state = AddCharacterStatusEffect(
            StaticTarget.from_player_active(self.BASE_GAME, Pid.P1), GrimheartStatus
        ).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertNotIn(GrimheartStatus, p1_active_char(game_state).character_statuses)

    def test_lightfall_sword_summon(self):
        game_state = AddSummonEffect(Pid.P1, LightfallSwordSummon).execute(self.BASE_GAME)
        game_state = grant_all_infinite_revival(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 0)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 4)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3 + 4)
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertNotIn(LightfallSwordSummon, game_state.player1.summons)

    def test_talent_card(self):
        game_state = grant_all_infinite_revival(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = fill_energy_for_all(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=WellspingOfWarLust,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3})),
        ))
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 0)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(game_state.player1.summons.just_find(LightfallSwordSummon).usages, 5)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3 + 5)
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertNotIn(LightfallSwordSummon, game_state.player1.summons)
