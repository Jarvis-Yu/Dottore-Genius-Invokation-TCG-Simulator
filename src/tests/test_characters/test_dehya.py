import unittest

from src.tests.test_characters.common_imports import *


class TestDehya(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Dehya,
        char_id=2,
        card=StalwartAndTrue,
    )

    def test_normal_attack(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_elemental_skill1(self):
        # test elemental skill generate summon
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        p1 = game_state.player1
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 0)
        self.assertIn(FierySanctumFieldSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(FierySanctumFieldSummon).usages, 3)

        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.PYRO)

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)

        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.PYRO: 4}),
        )

        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)

        game_state = step_action(game_state, Pid.P2, EndRoundAction())

        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        dmg = dmgs[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)

    def test_fiery_sanctum_field_summon(self):
        base_state = AddSummonEffect(Pid.P1, FierySanctumFieldSummon).execute(self.BASE_GAME)

        # dmg to Dehya doesn't trigger
        game_state = simulate_status_dmg(base_state, 3, Element.PYRO, Pid.P1)
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.hp, 7)

        # dmg to Ally trigger
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = simulate_status_dmg(game_state, 3, Element.PYRO, Pid.P1)
        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 8)
        self.assertEqual(p1c2.hp, 6)

        # once per round
        game_state = simulate_status_dmg(game_state, 1, Element.PYRO, Pid.P1)
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.hp, 7)

        # check dmg by the end
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertEqual(dmg.element, Element.PYRO)

        # check hp deduction limit is 7
        game_state = simulate_status_dmg(game_state, 3, Element.PYRO, Pid.P1)
        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 5)
        self.assertEqual(p1c2.hp, 6)

    def test_stalwart_and_true_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=StalwartAndTrue,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 4}))
        ))
        self.assertIn(FierySanctumFieldSummon, game_state.player1.summons)
        game_state = simulate_status_dmg(game_state, 4, Element.PYRO, Pid.P1)
        game_state = next_round(game_state)
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.hp, 8)
