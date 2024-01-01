import unittest

from .common_imports import *


class TestAncientCourtyard(unittest.TestCase):
    def test_cost_deduction(self):
        base_state = replace_character_make_active_add_card(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Noelle,
            2,
            card=AncientCourtyard,
        )
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=AncientCourtyard,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertIn(AncientCourtyardStatus, base_state.player1.combat_statuses)

        test_cards = (
            IGotYourBack,
            WolfsGravestone,
            WhiteIronGreatsword,
            GamblersEarrings,
        )
        expected_cost = (
            (3, 3),
            (1, 3),
            (0, 2),
            (0, 1),
        )

        def dice_only(n: int) -> DiceOnlyInstruction:
            return DiceOnlyInstruction(dice=ActualDice({Element.OMNI: n}))

        def targetted(n: int) -> StaticTargetInstruction:
            return StaticTargetInstruction(
                target=StaticTarget.from_player_active(base_state, Pid.P1),
                dice=ActualDice({Element.OMNI: n}),
            )

        instructions = (
            dice_only,
            targetted,
            targetted,
            targetted,
        )

        for card, costs, instr in zip(test_cards, expected_cost, instructions):
            with self.subTest(card=card.__name__):
                game_state = PublicAddCardEffect(Pid.P1, card=card).execute(base_state)
                game_state = PublicAddCardEffect(Pid.P1, card=card).execute(game_state)

                # if this step doesn't raise an error, then the cost is valid (the card is valid)
                game_state = step_action(game_state, Pid.P1, CardAction(
                    card=card,
                    instruction=instr(costs[0]),
                ))
                self.assertIs(
                    AncientCourtyardStatus not in game_state.player1.combat_statuses,
                    issubclass(card, WeaponEquipmentCard | ArtifactEquipmentCard) and costs[1] > 0,
                )

                # should only be effective once
                game_state = step_action(game_state, Pid.P1, CardAction(
                    card=card,
                    instruction=instr(costs[1]),
                ))

    def testDisappearance(self):
        base_state = replace_character_make_active_add_card(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Noelle,
            2,
            card=AncientCourtyard,
        )
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=AncientCourtyard,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertIn(AncientCourtyardStatus, base_state.player1.combat_statuses)

        game_state = next_round(base_state)
        self.assertNotIn(AncientCourtyardStatus, game_state.player1.combat_statuses)
