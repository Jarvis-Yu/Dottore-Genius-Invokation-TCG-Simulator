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
        base_dice = base_state.player1.dice

        # test basic triggering
        game_state = base_state
        for i in range(1, 3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=TenacityOfTheMillelith,
                instruction=StaticTargetInstruction(
                    dice=ActualDice({Element.OMNI: 3}),
                    target=StaticTarget.from_char_id(Pid.P1, i),
                )
            ))
        equipped_state = game_state
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        new_dice = game_state.player1.dice
        self.assertEqual(new_dice[Element.GEO], base_dice[Element.GEO] + 1)
        self.assertEqual(new_dice[Element.CRYO], base_dice[Element.CRYO])

        # test can only trigger once
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        new_dice = game_state.player1.dice
        self.assertEqual(new_dice[Element.GEO], base_dice[Element.GEO] + 1)
        self.assertEqual(new_dice[Element.CRYO], base_dice[Element.CRYO])

        # test overload fails
        game_state = apply_elemental_aura(equipped_state, Element.PYRO, Pid.P1)
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)
        new_dice = game_state.player1.dice
        self.assertEqual(new_dice[Element.GEO], base_dice[Element.GEO])
        self.assertEqual(new_dice[Element.CRYO], base_dice[Element.CRYO])

        # test klee's burst can trigger
        game_state = skip_action_round(base_state, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = silent_fast_swap(game_state, Pid.P2, char_id=2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.ELEMENTAL_BURST)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        new_dice = game_state.player1.dice
        self.assertEqual(new_dice[Element.GEO], base_dice[Element.GEO] + 1)
        self.assertEqual(new_dice[Element.CRYO], base_dice[Element.CRYO])

        # test shield generation
        game_state = simulate_status_dmg(equipped_state, 3, Element.PHYSICAL, Pid.P1)
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.hp, 7)

        game_state = next_round(game_state)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=2)
        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 6)
        self.assertEqual(p1c2.hp, 9)