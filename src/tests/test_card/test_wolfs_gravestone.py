import unittest

from .common_imports import *

class TestWolfsGravestone(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, WolfsGravestone).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Noelle, char_id=1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip Wolf's Gravestone
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=WolfsGravestone,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        # test dmg as expected
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.PHYSICAL)
        game_state_7 = game_state
        game_state_6 = simulate_status_dmg(game_state, 1, pid=Pid.P2)

        # test threshold & boost
        game_state = step_skill(game_state_7, Pid.P1, CharacterSkill.SKILL2)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.GEO)

        game_state = step_skill(game_state_6, Pid.P1, CharacterSkill.SKILL2)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.GEO)

        # test burst's boost (as usual)
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 7)
        self.assertIs(last_dmg.element, Element.GEO)