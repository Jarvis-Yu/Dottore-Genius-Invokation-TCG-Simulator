import unittest

from .common_imports import *

class TestJeht(unittest.TestCase):
    def test_behaviour(self):
        base_state = replace_hand_cards(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Cards({
                Jeht: 2,
                ChangTheNinth: 8,
            }),
        )
        base_state = grant_all_infinite_revival(base_state)

        # check non-removel support does not trigger Jeht
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Jeht,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        for _ in range(3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=ChangTheNinth,
                instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
            ))
        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 0)

        # removel support triggers Jeht
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_support(Pid.P1, 4),
                dice=ActualDice.from_empty(),
            ),
        ))
        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 1)

        for _ in range(3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=ChangTheNinth,
                instruction=StaticTargetInstruction(
                    target=StaticTarget.from_support(Pid.P1, 4),
                    dice=ActualDice.from_empty(),
                ),
            ))

        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 4)

        # elemental burst cannot trigger Jeht when usages < 5
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 4)

        # play Jeht when some supports are removed
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Jeht,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_support(Pid.P1, 2),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        jeht2 = game_state.player1.supports.find_by_sid(2)
        assert isinstance(jeht2, JehtSupport)
        self.assertEqual(jeht2.usages, 5)

        # elemental burst can trigger Jeht when usages >= 5
        game_state = replace_character(game_state, Pid.P1, Keqing, 1)
        game_state = recharge_energy_for_all(game_state)
        dice_before = game_state.player1.dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, ActualDice({
            Element.ELECTRO: 4,
        }))
        dice_after = game_state.player1.dice
        self.assertEqual(dice_after[Element.OMNI], dice_before[Element.OMNI] + 7)
        self.assertNotIn(JehtSupport, game_state.player1.supports)

        # check usages cannot be greater than 6
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Jeht: 1, ChangTheNinth: 5}))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Jeht,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_support(Pid.P1, 4),
                dice=ActualDice.from_empty(),
            ),
        ))
        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 6)
