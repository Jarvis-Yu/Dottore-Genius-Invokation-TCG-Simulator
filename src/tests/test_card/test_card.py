import unittest
from typing import cast

from src.dgisim.card.card import _DiceOnlyChoiceProvider, _CharTargetChoiceProvider
from src.dgisim.support.supports import Supports
from .common_imports import *


class CardA(_DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: BIG_INT << 32})


class CardB(_DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.ANY: 1})


class CardC(SupportCard):
    _DICE_COST = AbstractDice({})


class TestCard(unittest.TestCase):
    def test_dice_only_choice_provider(self):
        game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_hand_cards(
                lambda hcs: hcs + cast(dict[type[Card], int], {CardA: 1, CardB: 1})
            ).build()
        ).build()
        self.assertIsNone(CardA.action_generator(
            game_state,
            Pid.P1,
        ))
        self.assertIsNotNone(CardB.action_generator(
            game_state,
            Pid.P1,
        ))

    def test_support_card(self):
        full_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_hand_cards(
                lambda hcs: hcs + cast(dict[type[Card], int], {CardC: 1, Xudong: 1})
            ).supports(
                Supports((Support(sid=1), Support(sid=2), Support(sid=3), Support(sid=4)), max_num=4)
            ).build()
        ).build()
        action_generator = CardC.action_generator(full_game, Pid.P1)
        assert action_generator is not None
        choices = action_generator.choices()
        for id in range(1, 5):
            self.assertIn(StaticTarget(Pid.P1, Zone.SUPPORTS, id), choices)

        self.assertIsNone(
            CardC.valid_instruction(full_game, Pid.P1, DiceOnlyInstruction(dice=ActualDice({})))
        )
        self.assertIsNone(
            CardC.valid_instruction(
                full_game,
                Pid.P1, StaticTargetInstruction(
                    dice=ActualDice({}),
                    target=StaticTarget(Pid.P1, Zone.SUPPORTS, 5)
                )
            )
        )
        action_generator = just(Xudong.action_generator(full_game, Pid.P1))
        action_generator = just(action_generator.choose(StaticTarget(Pid.P1, Zone.SUPPORTS, 3)))
        action_generator = just(action_generator.choose(ActualDice({Element.OMNI: 2})))
        assert action_generator.filled()
        action = action_generator.generate_action()
        game_state = full_game.action_step(Pid.P1, action)
        assert game_state is not None
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.auto_step()
        supports = gsm.get_game_state().player1.supports.get_supports()
        self.assertEqual(
            (1, 2, 4, 3),
            tuple(support.sid for support in supports)
        )

        not_full_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_hand_cards(
                lambda hcs: hcs + cast(dict[type[Card], int], {CardC: 1})
            ).supports(
                Supports((Support(sid=1), Support(sid=2)), max_num=4)
            ).build()
        ).build()

        action_generator = CardC.action_generator(not_full_game, Pid.P1)
        assert action_generator is not None

        self.assertIsNone(
            CardC.valid_instruction(
                not_full_game,
                Pid.P1, StaticTargetInstruction(
                    dice=ActualDice({}),
                    target=StaticTarget(Pid.P1, Zone.SUPPORTS, 5)
                )
            )
        )
