import unittest

from .common_imports import *

class TestVortexVanquisher(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, VortexVanquisher).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Shenhe, char_id=1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip Vortex Vanquisher
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=VortexVanquisher,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))


        # test normal basic dmg boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.PHYSICAL)

        # test shields like Jade Screen doesn't trigger
        game_state = AddCombatStatusEffect(Pid.P1, status=JadeScreenStatus).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.PHYSICAL)

        # test shields like Noelle's Shield triggers
        game_state = AddCombatStatusEffect(Pid.P1, status=FullPlateStatus).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.PHYSICAL)

        game_state = simulate_status_dmg(game_state, 10, Element.PHYSICAL, Pid.P1)
        game_state = AddCombatStatusEffect(Pid.P1, status=CrystallizeStatus).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.PHYSICAL)