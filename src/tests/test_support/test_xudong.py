import unittest

from src.dgisim.card.card import FoodCard
from src.dgisim.dice import AbstractDice
from src.dgisim.element import Element
from src.dgisim.support.support import XudongSupport
from src.tests.helpers.game_state_templates import *

class CardAny3(FoodCard):
    _DICE_COST = AbstractDice({Element.ANY: 3})

class CardAny1(FoodCard):
    _DICE_COST = AbstractDice({Element.ANY: 1})

class CardOmni3(FoodCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})

class CardOmni1(FoodCard):
    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
