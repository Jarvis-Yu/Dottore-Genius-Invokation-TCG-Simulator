import unittest

from dgisim.src.card.card import FoodCard
from dgisim.src.dices import AbstractDices
from dgisim.src.element import Element
from dgisim.src.support.support import XudongSupport
from dgisim.tests.helpers.game_state_templates import *

class CardAny3(FoodCard):
    _DICE_COST = AbstractDices({Element.ANY: 3})

class CardAny1(FoodCard):
    _DICE_COST = AbstractDices({Element.ANY: 1})

class CardOmni3(FoodCard):
    _DICE_COST = AbstractDices({Element.OMNI: 3})

class CardOmni1(FoodCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

class TestXudong(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p1: p1.factory().f_supports(
            lambda sups: sups.update_support(XudongSupport(sid=1))
        ).build()
    ).build()

    def test_preprocess(self):
        self.assertEqual(
            CardAny1.just_preprocessed_dice_cost(self.BASE_GAME, Pid.P1)[Element.ANY],
            0
        )
        self.assertEqual(
            CardAny3.just_preprocessed_dice_cost(self.BASE_GAME, Pid.P1)[Element.ANY],
            1
        )
        self.assertEqual(
            CardOmni1.just_preprocessed_dice_cost(self.BASE_GAME, Pid.P1)[Element.OMNI],
            0
        )
        self.assertEqual(
            CardOmni3.just_preprocessed_dice_cost(self.BASE_GAME, Pid.P1)[Element.OMNI],
            1
        )
