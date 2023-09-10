import unittest

from .common_imports import *

class TestAmosBow(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, AmosBow).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Fischl, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Ganyu, char_id=2)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip amos bow for Fischl and Ganyu
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=AmosBow,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AmosBow,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.GEO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            )
        ))

        # test fischl elemental skill (dice-energy cost of 3) doesn't trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.ELECTRO)

        # test fischl burst (dice-energy cost of 6) triggers
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 7)
        self.assertIs(last_dmg.element, Element.ELECTRO)

        # test second burst cannot trigger again in the same round
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 5)
        self.assertIs(last_dmg.element, Element.ELECTRO)

        # test ganyu 5-cost skill triggers right-away
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, char_id=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 5)
        self.assertIs(last_dmg.element, Element.CRYO)

        # test ganyu second 5-cost skill doesn't trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.CRYO)

        # test can trigger again next round
        game_state = next_round(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = fill_dices_with_omni(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 5)
        self.assertIs(last_dmg.element, Element.CRYO)