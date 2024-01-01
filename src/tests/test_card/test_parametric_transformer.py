import unittest

from .common_imports import *


class TestParametricTransformer(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, ParametricTransformer).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Xingqiu, char_id=1)
        base_state = replace_character(base_state, Pid.P2, Mona, char_id=1)
        base_state = grant_all_thick_shield(base_state)

        def transformer_support(game_state: GameState) -> ParametricTransformerSupport:
            support = game_state.player1.supports.just_find(
                ParametricTransformerSupport, sid=1,
            )
            assert isinstance(support, ParametricTransformerSupport)
            return support
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=ParametricTransformer,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 1, Element.GEO: 1})),
        ))

        # test skill with elemental damgae triggers
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
        transformer = transformer_support(game_state)
        self.assertEqual(transformer.usages, 1)

        # test skill without elemental damgae doesn't trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        transformer = transformer_support(game_state)
        self.assertEqual(transformer.usages, 1)

        # test skill with elemental damgae triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        transformer = transformer_support(game_state)
        self.assertEqual(transformer.usages, 2)

        # test skill wihtout elemental damage but has elemental follow-up from status triggers
        pre_dice = game_state.player1.dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        post_dice = game_state.player1.dice
        self.assertNotIn(ParametricTransformerSupport, game_state.player1.supports)
        self.assertEqual(
            post_dice.num_dice() - post_dice[Element.OMNI],
            pre_dice.num_dice() - pre_dice[Element.OMNI] + 3,
        )

        # test oppo can trigger
        game_state = next_round_with_great_omni(base_state)
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)
        transformer = transformer_support(game_state)
        self.assertEqual(transformer.usages, 1)