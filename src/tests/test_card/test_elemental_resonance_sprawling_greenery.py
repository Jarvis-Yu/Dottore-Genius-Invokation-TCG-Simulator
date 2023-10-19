import unittest

from .common_imports import *


class TestElementalResonanceSprawlingGreenery(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceSprawlingGreenery
    ).execute(ACTION_TEMPLATE).factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().character(
                Nahida.from_default(1)
            ).build()
        ).build()
    ).build()

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceSprawlingGreenery.valid_in_deck(
                MutableDeck(chars=[Nahida, Keqing, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceSprawlingGreenery.valid_in_deck(
                MutableDeck(chars=[Bennett, Nahida, Tighnari], cards={})
            )
        )

    def test_card_adds_status(self):
        def get_statuses(
                game_state: GameState
        ) -> tuple[BurningFlameSummon, CatalyzingFieldStatus, DendroCoreStatus]:
            p1 = game_state.get_player1()
            flame = p1.get_summons().just_find(BurningFlameSummon)
            assert isinstance(flame, BurningFlameSummon)
            cata = p1.get_combat_statuses().just_find(CatalyzingFieldStatus)
            assert isinstance(cata, CatalyzingFieldStatus)
            core = p1.get_combat_statuses().just_find(DendroCoreStatus)
            assert isinstance(core, DendroCoreStatus)
            return flame, cata, core

        game_state = AddCombatStatusEffect(Pid.P1, DendroCoreStatus).execute(self.BASE_GAME)
        game_state = AddCombatStatusEffect(Pid.P1, CatalyzingFieldStatus).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, BurningFlameSummon).execute(game_state)
        old_flame, old_cata, old_core = get_statuses(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceSprawlingGreenery,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 1}))
        ))
        new_flame, new_cata, new_core = get_statuses(game_state)
        self.assertIn(
            ElementalResonanceSprawlingGreeneryStatus,
            game_state.get_player1().get_combat_statuses()
        )
        self.assertEqual(new_flame.usages, old_flame.usages + 1)
        self.assertEqual(new_cata.usages, old_cata.usages + 1)
        self.assertEqual(new_core.usages, old_core.usages + 1)

    def test_status_behaviour(self):
        base_state = AddCombatStatusEffect(Pid.P1, ElementalResonanceSprawlingGreeneryStatus).execute(
            self.BASE_GAME
        )

        # Reaction does boost the damage that triggers the reaction
        game_state = oppo_aura_elem(base_state, Element.ELECTRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(ElementalResonanceSprawlingGreeneryStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 6)

        # None reaction damage doesn't trigger status
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertIn(ElementalResonanceSprawlingGreeneryStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 9)

        # Summon triggers
        game_state = oppo_aura_elem(base_state, Element.ELECTRO)
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(game_state)
        game_state = next_round(game_state)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(ElementalResonanceSprawlingGreeneryStatus, p1_combat_statuses)
        self.assertEqual(p2ac.get_hp(), 6)  # raptor 1 + electro-charged 1 + resonance 2

        # status naturally disappears next round
        game_state = next_round(base_state)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        self.assertNotIn(ElementalResonanceSprawlingGreeneryStatus, p1_combat_statuses)
