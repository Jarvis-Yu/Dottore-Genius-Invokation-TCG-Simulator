from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, fields, replace
from itertools import chain
from typing import Any, TYPE_CHECKING
from typing_extensions import Self

from ..card.cards import Cards
from ..character.enums import CharacterSkill
from ..dice import ActualDice
from ..effect.enums import Zone
from ..effect.structs import StaticTarget
from ..element import Element
from ..helper.quality_of_life import dataclass_repr
from ..state.enums import Pid

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan
    from ..state.game_state import GameState
    from ..card.card import Card

__all__ = [
    "PlayerAction",
    "CardsSelectAction",
    "DiceSelectAction",
    "CharacterSelectAction",
    "EndRoundAction",
    "GameAction",
    "ElementalTuningAction",
    "CardAction",
    "SkillAction",
    "SwapAction",
    "DeathSwapAction",
    "Instruction",
    "DiceOnlyInstruction",
    "StaticTargetInstruction",
    "SourceTargetInstruction",
]

"""
Action encoding scheme:

- 0: type of action
- 1: character id
- 2: skill id
- 3: card id
- 4: element
- 5-84: cards selected
- 85-106: dice selected
- 107-109: target 1
- 110-112: target 2
"""

@dataclass(frozen=True, repr=False)
class PlayerAction:
    @classmethod
    def _empty(cls) -> Self:  # pragma: no cover
        """
        This is just for action generator
        """
        return cls()

    @classmethod
    def _all_none(cls) -> Self:
        """
        This is just for action generator
        Sets all fields to None ready to be filled later
        """
        self = cls._empty()
        for field in fields(self):
            object.__setattr__(self, field.name, None)
        return self

    def _filled(self, exceptions: set[str] = set()) -> bool:
        """
        This is just for action generator
        """
        return all(
            self.__getattribute__(field.name) is not None
            for field in fields(self)
            if field.name not in exceptions
        )

    def __repr__(self) -> str:
        return dataclass_repr(self)

    @abstractmethod
    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        pass

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | PlayerAction:
        from ..card.card import Card

        action_type = encoding[0]
        if all(x == 0 for x in encoding):
            return EndRoundAction()
        elif action_type == 1:
            cards = Cards.decoding(encoding[5:encoding_plan.ACTION_LOCAL_SIZE], encoding_plan)
            if cards is None:
                return None
            return CardsSelectAction(selected_cards=cards)
        elif action_type == 2:
            dice = ActualDice.decoding(encoding[encoding_plan.ACTION_LOCAL_SIZE:107], encoding_plan)
            if dice is None or not dice.is_legal():
                return None
            return DiceSelectAction(selected_dice=dice)
        elif action_type == 3:
            return CharacterSelectAction(char_id=encoding[1])
        elif action_type == 4:
            card_type = encoding_plan.type_for(encoding[3])
            elem_code = encoding[4]
            if (
                    card_type is None
                    or not issubclass(card_type, Card)
                    or elem_code >= len(Element)
            ):
                return None
            return ElementalTuningAction(
                card=card_type,
                dice_elem=Element(elem_code),
            )
        elif action_type == 5:
            card_type = encoding_plan.type_for(encoding[3])
            if card_type is None or not issubclass(card_type, Card):
                return None
            instruction = Instruction.decoding(
                encoding[encoding_plan.ACTION_LOCAL_SIZE:],
                encoding_plan,
            )
            if instruction is None:
                return None
            return CardAction(
                card=card_type,
                instruction=instruction,
            )
        elif action_type == 6:
            skill_code = encoding[2]
            if skill_code >= len(CharacterSkill):
                return None
            skill = CharacterSkill(skill_code)
            instruction = Instruction.decoding(
                encoding[encoding_plan.ACTION_LOCAL_SIZE:],
                encoding_plan,
            )
            if instruction is None or not isinstance(instruction, DiceOnlyInstruction):
                return None
            return SkillAction(
                skill=skill,
                instruction=instruction,
            )
        elif action_type == 7:
            instruction = Instruction.decoding(
                encoding[encoding_plan.ACTION_LOCAL_SIZE:],
                encoding_plan,
            )
            if instruction is None or not isinstance(instruction, DiceOnlyInstruction):
                return None
            return SwapAction(
                char_id=encoding[1],
                instruction=instruction,
            )
        elif action_type == 8:
            return DeathSwapAction(char_id=encoding[1])
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True, repr=False)
class CardsSelectAction(PlayerAction):
    #: cards selected.
    selected_cards: Cards

    @classmethod
    def _empty(cls) -> Self:
        return cls(selected_cards=Cards({}))

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        cards_encoding = self.selected_cards.encoding(encoding_plan)
        return list(chain(
            [1, 0, 0, 0, 0],
            cards_encoding,
            [0] * encoding_plan.INSTRUCTION_SIZE,
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class DiceSelectAction(PlayerAction):
    #: dice selected.
    selected_dice: ActualDice

    @classmethod
    def _empty(cls) -> Self:
        return cls(selected_dice=ActualDice({}))

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        dice_encoding = self.selected_dice.encoding(encoding_plan)
        return list(chain(
            [2, 0, 0, 0, 0],
            [0] * (encoding_plan.ACTION_LOCAL_SIZE - 5),
            dice_encoding,
            [0] * (encoding_plan.INSTRUCTION_SIZE - len(dice_encoding)),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class CharacterSelectAction(PlayerAction):
    #: selected character's id.
    char_id: int

    @classmethod
    def _empty(cls) -> Self:
        return cls(char_id=-1)

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [3, self.char_id, 0, 0, 0],
            [0] * (encoding_plan.ACTION_FULL_SIZE - 5),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class EndRoundAction(PlayerAction):
    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return [0] * encoding_plan.ACTION_FULL_SIZE


@dataclass(frozen=True, kw_only=True, repr=False)
class GameAction(PlayerAction):
    """ A superclass for actions that are mainly performed in action phase. """
    pass


@dataclass(frozen=True, kw_only=True, repr=False)
class ElementalTuningAction(GameAction):
    """
    Used tune an elemental die.
    """
    #: type of card to be used for tuning.
    card: type[Card]
    #: the element of die to be tuned.
    dice_elem: Element

    @classmethod
    def _empty(cls) -> Self:
        from ..card.card import Card
        return cls(card=Card, dice_elem=Element.ANY)

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [4, 0, 0, encoding_plan.code_for(self.card), self.dice_elem.value],
            [0] * (encoding_plan.ACTION_FULL_SIZE - 5),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class CardAction(GameAction):
    """
    Used to play a card.
    """
    #: type of card to be used.
    card: type[Card]
    #: detailed instruction on how the card should be used.
    instruction: Instruction

    @classmethod
    def _empty(cls) -> Self:
        from ..card.card import Card
        return cls(card=Card, instruction=Instruction._empty())

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [5, 0, 0, encoding_plan.code_for(self.card), 0],
            [0] * (encoding_plan.ACTION_LOCAL_SIZE - 5),
            self.instruction.encoding(encoding_plan),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class SkillAction(GameAction):
    """
    Used to cast the skill of the active character.
    """
    #: type of skill to cast (by the active character).
    skill: CharacterSkill
    #: instruction on which dice to be paid for the skill.
    instruction: DiceOnlyInstruction

    @classmethod
    def _empty(cls) -> Self:
        return cls(skill=CharacterSkill.SKILL1, instruction=DiceOnlyInstruction._empty())

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [6, 0, self.skill.value, 0, 0],
            [0] * (encoding_plan.ACTION_LOCAL_SIZE - 5),
            self.instruction.encoding(encoding_plan),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class SwapAction(GameAction):
    """
    Used when normal character swap is performed.
    """
    #: target character's id.
    char_id: int
    #: instruction on which dice to be paid for the skill.
    instruction: DiceOnlyInstruction

    @classmethod
    def _empty(cls) -> Self:
        return cls(char_id=-1, instruction=DiceOnlyInstruction._empty())

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [7, self.char_id, 0, 0, 0],
            [0] * (encoding_plan.ACTION_LOCAL_SIZE - 5),
            self.instruction.encoding(encoding_plan),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class DeathSwapAction(GameAction):
    """
    Used when active character is defeated and requires swapping.
    """
    #: target character's id.
    char_id: int

    @classmethod
    def _empty(cls) -> Self:
        return cls(char_id=-1)

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        return list(chain(
            [8, self.char_id, 0, 0, 0],
            [0] * (encoding_plan.ACTION_FULL_SIZE - 5),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class Instruction:
    #: dice to be paid.
    dice: ActualDice

    @classmethod
    def _empty(cls) -> Self:
        return cls(dice=ActualDice({}))

    @classmethod
    def _all_none(cls) -> Self:
        """
        This is just for action generator
        """
        self = cls._empty()
        for field in fields(self):
            object.__setattr__(self, field.name, None)
        return self

    def _filled(self, exceptions: set[str] = set()) -> bool:
        """
        This is just for action generator
        """
        return all(
            self.__getattribute__(field.name) is not None
            for field in fields(self)
            if field.name not in exceptions
        )

    def legal(self) -> bool:  # pragma: no cover
        field_type_val = (
            (field.type, field.__getattribute__(field.name))
            for field in fields(self)
        )
        return all(
            isinstance(val, field_type)
            for field_type, val in field_type_val
        )

    def __repr__(self) -> str:
        return dataclass_repr(self)

    @abstractmethod
    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        pass

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Instruction:
        if all(x == 0 for x in encoding):
            return DiceOnlyInstruction(dice=ActualDice({}))
        elif any(code != 0 for code in encoding[-6:-3]) and any(code != 0 for code in encoding[-3:]):
            dice = ActualDice.decoding(encoding[:-6], encoding_plan)
            source = StaticTarget.decoding(encoding[-6:-3], encoding_plan)
            target = StaticTarget.decoding(encoding[-3:], encoding_plan)
            if dice is None or not dice.is_legal() or source is None or target is None:
                return None
            return SourceTargetInstruction(dice=dice, source=source, target=target)
        elif any(code != 0 for code in encoding[-6:-3]):
            dice = ActualDice.decoding(encoding[:-6], encoding_plan)
            target = StaticTarget.decoding(encoding[-6:-3], encoding_plan)
            if dice is None or not dice.is_legal() or target is None:
                return None
            return StaticTargetInstruction(dice=dice, target=target)
        else:
            dice = ActualDice.decoding(encoding[:-6], encoding_plan)
            if dice is None or not dice.is_legal():
                return None
            return DiceOnlyInstruction(dice=dice)


@dataclass(frozen=True, kw_only=True, repr=False)
class DiceOnlyInstruction(Instruction):
    """ An instruction that only contains dice. """
    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        dice_encoding = self.dice.encoding(encoding_plan)
        return list(chain(
            dice_encoding,
            [0] * (encoding_plan.INSTRUCTION_SIZE - len(dice_encoding)),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class StaticTargetInstruction(Instruction):
    """
    An instruction that can choose a single target.
    """
    #: the target selected.
    target: StaticTarget

    @classmethod
    def _empty(cls) -> Self:
        return cls(
            dice=ActualDice({}),
            target=StaticTarget(
                pid=Pid.P1,
                zone=Zone.CHARACTERS,
                id=-1,
            ),
        )

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        dice_encoding = self.dice.encoding(encoding_plan)
        target_encoding = self.target.encoding(encoding_plan)
        return list(chain(
            dice_encoding,
            target_encoding,
            [0] * (
                encoding_plan.INSTRUCTION_SIZE
                - len(dice_encoding)
                - len(target_encoding)
            ),
        ))


@dataclass(frozen=True, kw_only=True, repr=False)
class SourceTargetInstruction(Instruction):
    """
    An instruction that can choose two targets.
    """
    #: source target.
    source: StaticTarget
    #: target target.
    target: StaticTarget

    @classmethod
    def _empty(cls) -> Self:  # pragma: no cover
        target = StaticTarget(
            pid=Pid.P1,
            zone=Zone.CHARACTERS,
            id=-1,
        )
        return cls(
            dice=ActualDice({}),
            source=target,
            target=target,
        )

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        dice_encoding = self.dice.encoding(encoding_plan)
        source_encoding = self.source.encoding(encoding_plan)
        target_encoding = self.target.encoding(encoding_plan)
        return list(chain(
            dice_encoding,
            source_encoding,
            target_encoding,
        ))
