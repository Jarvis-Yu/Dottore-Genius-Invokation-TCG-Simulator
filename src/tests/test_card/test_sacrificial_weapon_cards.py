"""
Tests the sacrificial weapon cards which's statuses directly use the template of
_SacrificialWeaponStatus

Cards covered are: SacrificialBow, SacrificalFragments, SacrificalGreatsword, SacrificialSword
"""
import unittest

from .common_imports import *


class TestSacrificialWeaponEquipmentCard(unittest.TestCase):
    def test_sacrifical_weapons(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_hand_cards(
                lambda hcs: hcs.add(SacrificialBow).add(SacrificialSword)
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()

        self.assertFalse(SacrificialBow.loosely_usable(base_game, Pid.P1))
        self.assertTrue(SacrificialSword.loosely_usable(base_game, Pid.P1))

        game_state = set_active_player_id(base_game, Pid.P1, 3)
        game_state = just(game_state.action_step(Pid.P1, CardAction(
            card=SacrificialSword,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 3}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 3),
            ),
        )))
        game_state = auto_step(game_state)
        p1ac = game_state.player1.just_get_active_character()
        self.assertIn(SacrificialSwordStatus, p1ac.character_statuses)

        dice_before = game_state.player1.dice

        # Normal attacks doesn't give dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO])

        # Burst attacks doesn't give dice
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO])

        # First Elemental Skill attacks gives dice
        game_state = kill_character(game_state, character_id=1, hp=10)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO] + 1)

        # Second Elemental Skill attacks doesn't give dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO] + 1)

        # Proceed to next round
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_next_phase()
        gsm.step_until_phase(game_state.mode.action_phase)

        game_state = auto_step(gsm.get_game_state())
        game_state = auto_step(just(game_state.action_step(Pid.P2, EndRoundAction())))
        game_state = kill_character(game_state, character_id=1, hp=10)
        game_state = fill_dice_with_omni(game_state)
        dice_before = game_state.player1.dice

        # First Elemental Skill attacks gives dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO] + 1)

        # Second Elemental Skill attacks doesn't give dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertEqual(p1.dice[Element.ELECTRO], dice_before[Element.ELECTRO] + 1)