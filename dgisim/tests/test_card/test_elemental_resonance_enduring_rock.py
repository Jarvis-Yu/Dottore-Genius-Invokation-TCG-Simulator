import unittest

from .common_imports import *


class TestElementalResonanceEnduringRock(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceEnduringRock
    ).execute(ACTION_TEMPLATE).factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().character(
                AratakiItto.from_default(1)
            ).character(
                Noelle.from_default(2)
            ).build()
        ).build()
    ).build()

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceEnduringRock.valid_in_deck(
                MutableDeck(chars=[AratakiItto, Nahida, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceEnduringRock.valid_in_deck(
                MutableDeck(chars=[AratakiItto, Nahida, Noelle], cards={})
            )
        )

    def test_card_adds_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=ElementalResonanceEnduringRock,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.GEO: 1}))
        ))
        self.assertIn(
            ElementalResonanceEnduringRockStatus,
            game_state.get_player1().get_combat_statuses()
        )

    def test_status_behaviour(self):
        base_state = AddCombatStatusEffect(Pid.P1, ElementalResonanceEnduringRockStatus).execute(
            self.BASE_GAME
        )
        # GEO damage without stacked shield in combat statuses doesn't trigger
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        self.assertFalse(any(
            isinstance(status, StackedShieldStatus)
            for status in p1_combat_statuses
        ))
        self.assertIn(ElementalResonanceEnduringRockStatus, p1_combat_statuses)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)

        game_state = AddCombatStatusEffect(Pid.P1, LeaveItToMeStatus).execute(game_state)
        game_state = step_swap(game_state, Pid.P1, char_id=2)
        game_state = UpdateCombatStatusEffect(Pid.P1, FullPlateStatus(usages=1)).execute(game_state)

        # PHYSICAL attack with stacked shield in combat statuses doesn't trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(FullPlateStatus).usages,
            1
        )

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)

        # GEO attack with stacked shield in combat statuses triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        self.assertEqual(p1_combat_statuses.just_find(FullPlateStatus).usages, 5)
        self.assertNotIn(ElementalResonanceEnduringRockStatus, p1_combat_statuses)

        # status disappears next round
        game_state = next_round(base_state)
        p1_combat_statuses = game_state.get_player1().get_combat_statuses()
        self.assertNotIn(ElementalResonanceEnduringRockStatus, p1_combat_statuses)
