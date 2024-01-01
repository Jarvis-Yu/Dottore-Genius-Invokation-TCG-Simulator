import unittest

from .common_imports import *


class TestElementalShatteringIce(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceShatteringIce,
    ).execute(ACTION_TEMPLATE)

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceShatteringIce.valid_in_deck(
                MutableDeck(chars=[Venti, Kaeya, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceShatteringIce.valid_in_deck(
                MutableDeck(chars=[Bennett, Kaeya, Shenhe], cards={})
            )
        )

    def test_card_adds_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=ElementalResonanceShatteringIce,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 1}))
        ))
        self.assertIn(
            ElementalResonanceShatteringIceStatus,
            game_state.player1.combat_statuses
        )

    def test_status_behaviour(self):
        base_state = AddCombatStatusEffect(Pid.P1, ElementalResonanceShatteringIceStatus).execute(
            self.BASE_GAME
        )

        # Elemental skill (of Rhodeia of Loch) doesn't trigger or consume
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertIn(ElementalResonanceShatteringIceStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 10)

        game_state = step_action(game_state, Pid.P2, EndRoundAction())

        # Normal attack (of Rhodeia of Loch) triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertNotIn(ElementalResonanceShatteringIceStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 7)

        # Summon doesn't trigger
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(base_state)
        game_state = next_round(game_state)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertNotIn(ElementalResonanceShatteringIceStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 9)

        # status naturally disappears next round
        game_state = next_round(base_state)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertNotIn(ElementalResonanceShatteringIceStatus, p1_combat_statuses)
