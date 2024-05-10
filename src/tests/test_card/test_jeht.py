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
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
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

        for _ in range(4):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=ChangTheNinth,
                instruction=StaticTargetInstruction(
                    target=StaticTarget.from_support(Pid.P1, 4),
                    dice=ActualDice.from_empty(),
                ),
            ))

        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 5)

        # elemental burst cannot trigger Jeht when usages < 6
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        jeht = game_state.player1.supports.find_by_sid(1)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 5)

        # play Jeht when some supports are removed
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Jeht,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_support(Pid.P1, 2),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        jeht2 = game_state.player1.supports.find_by_sid(2)
        assert isinstance(jeht2, JehtSupport)
        self.assertEqual(jeht2.usages, 6)

        # elemental burst can trigger one Jeht when usages >= 6
        game_state = replace_character(game_state, Pid.P1, Keqing, 1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, ActualDice({
            Element.ELECTRO: 4,
        }))
        self.assertIn(SandAndDreamsStatus, game_state.player1.combat_statuses)
        jeht_count = 0
        for support in game_state.player1.supports:
            jeht_count += isinstance(support, JehtSupport)
        self.assertEqual(jeht_count, 1)

        # check usages cannot be greater than 6
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Jeht: 1, ChangTheNinth: 5}))
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
        jeht = game_state.player1.supports.find_by_sid(2)
        assert isinstance(jeht, JehtSupport)
        self.assertEqual(jeht.usages, 6)

    def test_sand_and_dreams_status(self):
        game_state = ONE_ACTION_TEMPLATE
        game_state = AddCombatStatusEffect(Pid.P1, SandAndDreamsStatus).execute(game_state)
        game_state = replace_character(game_state, Pid.P1, Keqing, 1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, ActualDice({Element.ELECTRO: 1}),
        )
        self.assertNotIn(SandAndDreamsStatus, game_state.player1.combat_statuses)
