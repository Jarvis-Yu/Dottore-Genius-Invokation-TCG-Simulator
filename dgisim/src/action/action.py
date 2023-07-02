from __future__ import annotations
from typing import Any, ClassVar
from typing_extensions import override, Self
from dataclasses import dataclass, fields, replace

from dgisim.src.card.cards import Cards
from dgisim.src.card.card import Card
from dgisim.src.dices import ActualDices
from dgisim.src.effect.effect import StaticTarget
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.element.element import Element
import dgisim.src.state.game_state as gs
from dgisim.src.state.enums import PID
import dgisim.src.effect.effect as eft


@dataclass(frozen=True)
class PlayerAction:
    @classmethod
    def _empty(cls) -> Self:
        """
        This is just for action generator
        """
        return cls()

    @classmethod
    def _all_none(cls) -> Self:
        """
        This is just for action generator
        """
        self = cls._empty()
        for field in fields(self):
            object.__setattr__(self, field.name, None)
        return self

    def _set_attr(self, name: str, val: Any) -> Self:
        """
        This is just for action generator
        """
        other = replace(self)
        object.__setattr__(other, name, val)
        return other

    def _filled(self, exceptions: set[str] = set()) -> bool:
        """
        This is just for action generator
        """
        return all(
            self.__getattribute__(field.name) is not None
            for field in fields(self)
            if field.name not in exceptions
        )

    def legal(self) -> bool:
        field_type_val = (
            (field.type, field.__getattribute__(field.name))
            for field in fields(self)
        )
        return all(
            isinstance(val, field_type)
            for field_type, val in field_type_val
        )

    def __str__(self) -> str:
        cls_fields = fields(self)
        paired_fields = (
            f"{field.name}={str(self.__getattribute__(field.name))}" for field in cls_fields)
        return f"{self.__class__.__name__}:({', '.join(paired_fields)})"


@dataclass(frozen=True, kw_only=True)
class CardSelectAction(PlayerAction):
    selected_cards: Cards

    def num_cards(self) -> int:
        return self.selected_cards.num_cards()

    @classmethod
    def _empty(cls) -> Self:
        return cls(selected_cards=Cards({}))

    def __str__(self) -> str:
        name = self.__class__.__name__
        cards = '; '.join(str(self.selected_cards).split('\n'))
        return f"{name}[{cards}]"


@dataclass(frozen=True, kw_only=True)
class CharacterSelectAction(PlayerAction):
    char_id: int

    @classmethod
    def _empty(cls) -> Self:
        return cls(char_id=-1)


@dataclass(frozen=True, kw_only=True)
class EndRoundAction(PlayerAction):
    pass


@dataclass(frozen=True, kw_only=True)
class GameAction(PlayerAction):
    def is_valid_action(self, game_state: gs.GameState) -> bool:
        raise Exception("Not overriden")


@dataclass(frozen=True, kw_only=True)
class ElementalTuningAction(GameAction):
    card: type[Card]
    dice_elem: Element

    @classmethod
    def _empty(cls) -> Self:
        from dgisim.src.card.card import Card
        return cls(card=Card, dice_elem=Element.ANY)


@dataclass(frozen=True, kw_only=True)
class CardAction(GameAction):
    from dgisim.src.card.card import Card
    card: type[Card]
    instruction: Instruction

    @classmethod
    def _empty(cls) -> Self:
        from dgisim.src.card.card import Card
        return cls(card=Card, instruction=Instruction._empty())

    def __str__(self) -> str:
        return f"<{self.card.__name__}, {self.instruction}>"


@dataclass(frozen=True, kw_only=True)
class SkillAction(GameAction):
    skill: CharacterSkill
    instruction: DiceOnlyInstruction

    @classmethod
    def _empty(cls) -> Self:
        from dgisim.src.card.card import Card
        return cls(skill=CharacterSkill.NORMAL_ATTACK, instruction=DiceOnlyInstruction._empty())

    def __str__(self) -> str:
        return f"<{self.skill}, {self.instruction}>"


@dataclass(frozen=True, kw_only=True)
class SwapAction(GameAction):
    char_id: int
    instruction: Instruction

    @classmethod
    def _empty(cls) -> Self:
        from dgisim.src.card.card import Card
        return cls(char_id=-1, instruction=Instruction._empty())


@dataclass(frozen=True, kw_only=True)
class DeathSwapAction(GameAction):
    char_id: int

    @classmethod
    def _empty(cls) -> Self:
        from dgisim.src.card.card import Card
        return cls(char_id=-1)


@dataclass(frozen=True, kw_only=True)
class Instruction:
    dices: ActualDices

    @classmethod
    def _empty(cls) -> Self:
        return cls(dices=ActualDices({}))

    @classmethod
    def _all_none(cls) -> Self:
        """
        This is just for action generator
        """
        self = cls._empty()
        for field in fields(self):
            object.__setattr__(self, field.name, None)
        return self

    def _set_attr(self, name: str, val: Any) -> Self:
        """
        This is just for action generator
        """
        other = replace(self)
        object.__setattr__(other, name, val)
        return other

    def _filled(self, exceptions: set[str] = set()) -> bool:
        """
        This is just for action generator
        """
        return all(
            self.__getattribute__(field.name) is not None
            for field in fields(self)
            if field.name not in exceptions
        )

    def legal(self) -> bool:
        field_type_val = (
            (field.type, field.__getattribute__(field.name))
            for field in fields(self)
        )
        return all(
            isinstance(val, field_type)
            for field_type, val in field_type_val
        )

    def __str__(self) -> str:
        cls_fields = fields(self)
        paired_fields = (
            f"{field.name}={str(self.__getattribute__(field.name))}"
            for field in cls_fields
        )
        return f"{self.__class__.__name__}:({', '.join(paired_fields)})"


@dataclass(frozen=True, kw_only=True)
class DiceOnlyInstruction(Instruction):
    pass


@dataclass(frozen=True, kw_only=True)
class StaticTargetInstruction(Instruction):
    target: StaticTarget

    @classmethod
    def _empty(cls) -> Self:
        return cls(
            dices=ActualDices({}),
            target=StaticTarget(
                pid=PID.P1,
                zone=eft.Zone.CHARACTERS,
                id=-1,
            ),
        )


@dataclass(frozen=True, kw_only=True)
class SourceTargetInstruction(Instruction):
    source: StaticTarget
    target: StaticTarget

    @classmethod
    def _empty(cls) -> Self:
        target = StaticTarget(
            pid=PID.P1,
            zone=eft.Zone.CHARACTERS,
            id=-1,
        )
        return cls(
            dices=ActualDices({}),
            source=target,
            target=target,
        )
