import unittest

from .common_imports import *

class TestAThousandFloatingDreams(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, AThousandFloatingDreams).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Nahida, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Klee, char_id=2)
        base_state = replace_character(base_state, Pid.P1, Mona, char_id=3)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip A Thousand Floating Dreams for Nahida
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=AThousandFloatingDreams,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        
        # dmg gets boost if reaction
        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.DENDRO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.DENDRO)

        # dmg boost chances is limited to 2 per round
        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.DENDRO)

        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.DENDRO)

        # equip A Thousand Floating Dreams for another teammate
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AThousandFloatingDreams,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            )
        ))

        # check teammate's A Thousand Floating Dreams can boost my reaction
        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 4)
        self.assertIs(last_dmg.element, Element.DENDRO)

        # check A Thousand Floating Dreams' usages refresh the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())

        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 5)
        self.assertIs(last_dmg.element, Element.DENDRO)

        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 5)
        self.assertIs(last_dmg.element, Element.DENDRO)

        game_state = use_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 3)
        self.assertIs(last_dmg.element, Element.DENDRO)

class A:
    def __bool__(self) -> bool:
        print("__bool__")
        return False