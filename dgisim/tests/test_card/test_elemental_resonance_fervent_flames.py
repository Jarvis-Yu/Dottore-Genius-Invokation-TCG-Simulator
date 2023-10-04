import unittest

from .common_imports import *


class TestElementalResonanceFerventFlames(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceFerventFlames
    ).execute(ACTION_TEMPLATE).factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().character(
                KaedeharaKazuha.from_default(1)
            ).build()
        ).build()
    ).build()

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceFerventFlames.valid_in_deck(
                MutableDeck(chars=[Klee, Keqing, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceFerventFlames.valid_in_deck(
                MutableDeck(chars=[Bennett, Klee, Keqing], cards={})
            )
        )

    def test_card_adds_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=ElementalResonanceFerventFlames,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1}))
        ))
        self.assertIn(
            ElementalResonanceFerventFlamesStatus,
            game_state.get_player1().get_combat_statuses()
        )

    def test_status_behaviour(self):
        base_state = AddCombatStatusEffect(Pid.P1, ElementalResonanceFerventFlamesStatus).execute(
            self.BASE_GAME
        )
        base_state = oppo_aura_elem(base_state, Element.ELECTRO)
        # None reaction damage doesn't trigger status
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 8)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)

        # Reaction does boost the damage that triggers the reaction
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 2)

        # Summon doesn't trigger
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(base_state)
        game_state = next_round(game_state)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 8)  # raptor 1 + electro-charged 1

        # status naturally disappears next round
        game_state = next_round(base_state)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
