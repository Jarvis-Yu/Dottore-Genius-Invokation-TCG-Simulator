import unittest

from src.tests.test_characters.common_imports import *


class TestRaidenShogun(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        RaidenShogun,
        char_id=2,
        card=WishesUnnumbered,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ELECTRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        summon = game_state.player1.summons.find(EyeOfStormyJudgmentSummon)
        self.assertIsInstance(summon, EyeOfStormyJudgmentSummon)
        assert isinstance(summon, EyeOfStormyJudgmentSummon)
        self.assertEqual(summon.usages, 3)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = EnergyRechargeEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            recharge=2,
        ).execute(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ELECTRO: 4}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.ELECTRO)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.energy, 2)
        self.assertEqual(p1c2.energy, 0)
        self.assertEqual(p1c3.energy, 2)

    def test_summon(self):
        game_state = AddSummonEffect(Pid.P1, EyeOfStormyJudgmentSummon).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = replace_character(game_state, Pid.P1, Keqing, 1)
        game_state = replace_character(game_state, Pid.P1, Kaeya, 3)
        game_state = recharge_energy_for_all(game_state)

        # Test self burst damage gets buffed
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)

        # Test teammates burst damage gets buffed
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = apply_elemental_aura(game_state, Element.CRYO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)

    def test_passive(self):
        game_state = self.BASE_GAME
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = replace_character(game_state, Pid.P1, YaeMiko, 1)
        game_state = recharge_energy_for_all(game_state)

        # check self burst doesn't trigger passive
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)

        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)

        # check teammates burst charges passive
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)

        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)

        # check can only charge up to 3 times
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        for _ in range(4):
            game_state = recharge_energy_for_all(game_state)
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)

        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 6)

    def test_talent_card(self):
        game_state = self.BASE_GAME
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, YaeMiko, 1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        for _ in range(2):  # charge passive by 2
            game_state = recharge_energy_for_all(game_state)
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)

        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=WishesUnnumbered,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 4})),
        ))
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 7)
