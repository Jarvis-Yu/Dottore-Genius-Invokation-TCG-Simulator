from __future__ import annotations
from typing_extensions import override

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


class PlayerAction:
    pass


class CardSelectAction(PlayerAction):
    def __init__(self, selected_cards: Cards):
        self._selected_cards = selected_cards

    def get_selected_cards(self) -> Cards:
        return self._selected_cards

    def num_cards(self) -> int:
        return self._selected_cards.num_cards()


class CharacterSelectAction(PlayerAction):
    def __init__(self, selected_character_id: int):
        self._selected_character_id = selected_character_id

    def get_selected_character_id(self) -> int:
        return self._selected_character_id


class EndRoundAction(PlayerAction):
    pass


class GameAction(PlayerAction):
    def is_valid_action(self, game_state: gs.GameState) -> bool:
        raise Exception("Not overriden")


class CardAction(GameAction):
    from dgisim.src.card.card import Card

    def __init__(self, card: type[Card], instruction: Instruction) -> None:
        self._card = card
        self._instruction = instruction

    def card(self) -> type[Card]:
        return self._card

    def instruction(self) -> Instruction:
        return self._instruction

    def __str__(self) -> str:
        return f"<{self._card().__class__.__name__}, {self._instruction}>"


class SkillAction(GameAction):
    from dgisim.src.character.character import CharacterSkill

    def __init__(self, skill: CharacterSkill, instruction: Instruction) -> None:
        self._skill = skill
        self._instruction = instruction

    def skill(self) -> CharacterSkill:
        return self._skill

    def instruction(self) -> Instruction:
        return self._instruction

    def __str__(self) -> str:
        return f"<{self._skill}, {self._instruction}>"


class SwapAction(GameAction):

    def __init__(self, selected_character_id: int, instruction: Instruction):
        self._selected_character_id = selected_character_id
        self._instruction = instruction

    def seleted_character_id(self) -> int:
        return self._selected_character_id

    def instruction(self) -> Instruction:
        return self._instruction


class DeathSwapAction(GameAction):

    def __init__(self, selected_character_id: int):
        self._selected_character_id = selected_character_id

    def seleted_character_id(self) -> int:
        return self._selected_character_id


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
