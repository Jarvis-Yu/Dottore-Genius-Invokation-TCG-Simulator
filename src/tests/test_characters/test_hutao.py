import unittest

from src.tests.test_characters.common_imports import *


class TestHuTao(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        HuTao,
        char_id=2,
        card=SanguineRouge,
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
        # test elemental skill generate status
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 2}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(ParamitaPapilioStatus, p1ac.get_character_statuses())

    def test_elemental_burst(self):
        base_state = fill_energy_for_all(self.BASE_GAME)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # > 6 hp
        game_state = simulate_status_dmg(base_state, 3, pid=Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.PYRO: 3}),
        )

        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.PYRO)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 9)

        # <= 6 hp
        game_state = simulate_status_dmg(base_state, 4, pid=Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.PYRO: 3}),
        )

        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)
        self.assertIs(dmg.element, Element.PYRO)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 9)

    def test_paramita_papilio_status(self):
        base_state = AddCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=ParamitaPapilioStatus,
        ).execute(self.BASE_GAME)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # non-charged attack cannot apply BloodBlossomStatus
        game_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 11}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(BloodBlossomStatus, p2ac.get_character_statuses())

        # charged attack applies BloodBlossomStatus
        game_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 10}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertIn(BloodBlossomStatus, p2ac.get_character_statuses())

    def test_blood_blossom_status(self):
        base_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P2),
            status=BloodBlossomStatus,
        ).execute(self.BASE_GAME)

        game_state = next_round(base_state)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(BloodBlossomStatus, p2ac.get_character_statuses())
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())

    def test_sanguine_rouge_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=SanguineRouge,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 2}))
        ))
        game_state = add_dmg_listener(game_state, Pid.P1)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(ParamitaPapilioStatus, p1ac.get_character_statuses())

        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 11}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)

        game_state = simulate_status_dmg(game_state, 4, pid=Pid.P1)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 11}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.PYRO)
