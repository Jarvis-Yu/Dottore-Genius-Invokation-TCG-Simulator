import unittest

from dgisim.tests.test_characters.common_imports import *


class TestNingguang(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Ningguang,
        char_id=2,
        card=StrategicReserve,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Ningguang

    def test_normal_attack(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.GEO)

    def test_elemental_skill1(self):
        # test elemental skill generate status
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.GEO: 3}),
        )
        p1 = game_state.get_player1()
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.GEO)
        self.assertIn(JadeScreenStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(JadeScreenStatus).usages, 2)

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)

        # test burst without jade screen
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 6)
        self.assertIs(dmg.element, Element.GEO)

        # test burst with jade screen
        game_state = AddCombatStatusEffect(Pid.P1, JadeScreenStatus).execute(game_state)
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 8)
        self.assertIs(dmg.element, Element.GEO)

    def test_jade_screen_status(self):
        for dmg_amount in range(1, 4):
            with self.subTest(dmg_amount=dmg_amount):
                game_state = AddCombatStatusEffect(Pid.P1, JadeScreenStatus).execute(self.BASE_GAME)
                game_state = add_dmg_listener(game_state, Pid.P1)
                game_state = simulate_status_dmg(game_state, dmg_amount, Element.PHYSICAL, Pid.P1)
                dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
                should_trigger = dmg_amount >= 2
                self.assertEqual(dmg.damage, dmg_amount - (1 if should_trigger else 0))
                jade_screen_status = game_state.get_player1().get_combat_statuses().just_find(
                    JadeScreenStatus
                )
                self.assertEqual(jade_screen_status.usages, 1 if should_trigger else 2)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=StrategicReserve,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 4}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.GEO)

        # test has geo damage boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.GEO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.GEO)

        # not activated when Ningguang is off-field
        game_state = replace_character(game_state, Pid.P1, Noelle, 3)
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.GEO)

        # not activated when there's no JadeScreen
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = RemoveCombatStatusEffect(Pid.P1, JadeScreenStatus).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.GEO)

        # can boost summon
        game_state = AddCombatStatusEffect(Pid.P1, JadeScreenStatus).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, SolarIsotomaSummon).execute(game_state)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.GEO)
