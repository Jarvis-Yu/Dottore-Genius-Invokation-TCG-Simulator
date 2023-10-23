from __future__ import annotations
from dataclasses import dataclass, fields, replace
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


@dataclass(frozen=True, kw_only=True, repr=False)
class CardsSelectAction(PlayerAction):
    #: cards selected.
    selected_cards: Cards

    @classmethod
    def _empty(cls) -> Self:
        return cls(selected_cards=Cards({}))


@dataclass(frozen=True, kw_only=True, repr=False)
class DiceSelectAction(PlayerAction):
    #: dice selected.
    selected_dice: ActualDice

    @classmethod
    def _empty(cls) -> Self:
        return cls(selected_dice=ActualDice({}))


@dataclass(frozen=True, kw_only=True, repr=False)
class CharacterSelectAction(PlayerAction):
    #: selected character's id.
    char_id: int

    @classmethod
    def _empty(cls) -> Self:
        return cls(char_id=-1)


@dataclass(frozen=True, kw_only=True, repr=False)
class EndRoundAction(PlayerAction):
    pass


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


@dataclass(frozen=True, kw_only=True, repr=False)
class DiceOnlyInstruction(Instruction):
    """ An instruction that only contains dice. """
    pass


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
