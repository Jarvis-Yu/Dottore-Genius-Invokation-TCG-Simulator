import unittest

from .common_imports import *


class TestTenacityOfTheMillelith(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, TenacityOfTheMillelith).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Noelle, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, char_id=2)
        base_state = replace_character(base_state, Pid.P2, Keqing, char_id=1)
        base_state = replace_character(base_state, Pid.P2, Klee, char_id=2)
        base_state = grant_all_infinite_revival(base_state)
        base_dices = base_state.get_player1().get_dices()

        # test basic triggering
        game_state = base_state
        for i in range(1, 3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=TenacityOfTheMillelith,
                instruction=StaticTargetInstruction(
                    dices=ActualDices({Element.OMNI: 3}),
                    target=StaticTarget.from_char_id(Pid.P1, i),
                )
            ))
        equipped_state = game_state
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], base_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], base_dices[Element.CRYO])

        # test can only trigger once
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], base_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], base_dices[Element.CRYO])

        # test overload fails
        game_state = apply_elemental_aura(equipped_state, Element.PYRO, Pid.P1)
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], base_dices[Element.GEO])
        self.assertEqual(new_dices[Element.CRYO], base_dices[Element.CRYO])

        # test klee's burst can trigger
        game_state = skip_action_round(base_state, Pid.P1)
        game_state = fill_energy_for_all(game_state)
        game_state = silent_fast_swap(game_state, Pid.P2, char_id=2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.ELEMENTAL_BURST)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.OMNI: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        new_dices = game_state.get_player1().get_dices()
        self.assertEqual(new_dices[Element.GEO], base_dices[Element.GEO] + 1)
        self.assertEqual(new_dices[Element.CRYO], base_dices[Element.CRYO])