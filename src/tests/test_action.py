import unittest

from src.dgisim.action.action import *
from src.package.card import *
from src.package import *

class TestActionEncoding(unittest.TestCase):
    def test_cards_select_action(self):
        action = CardsSelectAction(
            selected_cards=Cards({
                NorthernSmokedChicken: 1,
                SweetMadame: 1,
            }),
        )
        self.assertEqual(
            action,
            CardsSelectAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_dice_select_action(self):
        action = DiceSelectAction(
            selected_dice=ActualDice({Element.PYRO: 1}),
        )
        self.assertEqual(
            action,
            DiceSelectAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_character_select_action(self):
        action = CharacterSelectAction(
            char_id=1,
        )
        self.assertEqual(
            action,
            CharacterSelectAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_end_round_action(self):
        action = EndRoundAction()
        self.assertEqual(
            action,
            EndRoundAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_elemental_tuning_action(self):
        action = ElementalTuningAction(
            card=ThunderingPenance,
            dice_elem=Element.PYRO,
        )
        self.assertEqual(
            action,
            ElementalTuningAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )
    
    def test_card_action(self):
        action = CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            ),
        )
        self.assertEqual(
            action,
            CardAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_skill_action(self):
        action = SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(
                dice=ActualDice.from_all(3, Element.OMNI),
            ),
        )
        self.assertEqual(
            action,
            SkillAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_swap_action(self):
        action = SwapAction(
            char_id=2,
            instruction=DiceOnlyInstruction(
                dice=ActualDice.from_all(1, Element.GEO),
            ),
        )
        self.assertEqual(
            action,
            SwapAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )

    def test_death_swap_action(self):
        action = DeathSwapAction(
            char_id=3,
        )
        self.assertEqual(
            action,
            DeathSwapAction.decoding(action.encoding(encoding_plan), encoding_plan),
        )