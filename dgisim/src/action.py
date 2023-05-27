from __future__ import annotations
from typing_extensions import override
from dataclasses import dataclass

from dgisim.src.card.cards import Cards
from dgisim.src.dices import ActualDices
from dgisim.src.event.effect import StaticTarget
import dgisim.src.state.game_state as gs


class Actions:
    def __init__(self, systems: dict, cards, skills, others) -> None:
        self._systems = systems
        self._cards = cards
        self._skills = skills
        self._others = others

    def system_actions(self):
        pass


@dataclass(frozen=True)
class PlayerAction:
    pass


@dataclass(frozen=True)
class CardSelectAction(PlayerAction):
    selected_cards: Cards

    def num_cards(self) -> int:
        return self.selected_cards.num_cards()

    def __str__(self) -> str:
        name = self.__class__.__name__
        cards = '; '.join(str(self.selected_cards).split('\n'))
        return f"{name}[{cards}]"


@dataclass(frozen=True)
class CharacterSelectAction(PlayerAction):
    selected_character_id: int


@dataclass(frozen=True)
class EndRoundAction(PlayerAction):
    pass


@dataclass(frozen=True)
class GameAction(PlayerAction):
    def is_valid_action(self, game_state: gs.GameState) -> bool:
        raise Exception("Not overriden")


@dataclass(frozen=True)
class CardAction(GameAction):
    from dgisim.src.card.card import Card
    card: type[Card]
    instruction: Instruction

    def __str__(self) -> str:
        return f"<{self.card.__name__}, {self.instruction}>"


@dataclass(frozen=True)
class SkillAction(GameAction):
    from dgisim.src.character.character import CharacterSkill
    skill: CharacterSkill
    instruction: Instruction

    def __str__(self) -> str:
        return f"<{self.skill}, {self.instruction}>"


@dataclass(frozen=True)
class SwapAction(GameAction):
    selected_character_id: int
    instruction: Instruction


@dataclass(frozen=True)
class DeathSwapAction(GameAction):
    selected_character_id: int


class Instruction:

    def dices(self) -> ActualDices:
        return ActualDices({})


class _DicedInstruction(Instruction):

    def __init__(self, dices: ActualDices):
        self._dices = dices

    @override
    def dices(self) -> ActualDices:
        return self._dices


class DiceOnlyInstruction(_DicedInstruction):

    def __init__(self, dices: ActualDices):
        super().__init__(dices)

    def __str__(self) -> str:
        return str(self._dices.num_dices())


class CharacterTargetInstruction(_DicedInstruction):

    def __init__(self, dices: ActualDices, target: StaticTarget):
        super().__init__(dices)
        self._target = target

    def target(self) -> StaticTarget:
        return self._target
