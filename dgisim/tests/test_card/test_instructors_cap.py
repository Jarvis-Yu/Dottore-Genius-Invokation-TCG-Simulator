
import unittest

from .common_imports import *


class TestInstructorsCap(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, InstructorsCap).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Noelle, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, char_id=2)
        base_state = grant_all_thick_shield(base_state)

        # equip cap for char 1 and 2
        game_state = base_state
        for i in range(1, 3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=InstructorsCap,
                instruction=StaticTargetInstruction(
                    dices=ActualDices({Element.PYRO: 1, Element.HYDRO: 1}),
                    target=StaticTarget.from_char_id(Pid.P1, i),
                )
            ))

        # test no reaction doesn't generate dices
        old_dices = game_state.get_player1().get_dices()
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        # here we assume step_skill() consumes OMNI dices
        self.assertEqual(new_dices[Element.GEO], old_dices[Element.GEO])
        self.assertEqual(new_dices[Element.CRYO], old_dices[Element.CRYO])

        # test with reaction triggers
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        old_dices = new_dices
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], old_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], old_dices[Element.CRYO])

        # test triggers 3 times maximum
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        old_dices = new_dices
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], old_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], old_dices[Element.CRYO])

        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        old_dices = new_dices
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], old_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], old_dices[Element.CRYO])

        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        old_dices = new_dices
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], old_dices[Element.GEO] + 0)
        self.assertEqual(new_dices[Element.CRYO], old_dices[Element.CRYO])
        artifact = game_state.get_player1().just_get_active_character(
        ).get_equipment_statuses().find(InstructorsCapStatus)
        self.assertIsNotNone(artifact)
        assert isinstance(artifact, InstructorsCapStatus)
        self.assertEqual(artifact.usages, 0)

        # test usages restore the next round
        game_state = next_round(game_state)
        artifact = game_state.get_player1().just_get_active_character(
        ).get_equipment_statuses().find(InstructorsCapStatus)
        self.assertIsNotNone(artifact)
        assert isinstance(artifact, InstructorsCapStatus)
        self.assertEqual(artifact.usages, 3)
