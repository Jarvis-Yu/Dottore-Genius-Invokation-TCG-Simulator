from __future__ import annotations

from dgisim.src.card.cards import Cards
from dgisim.src.character.characters import Characters
from dgisim.src.dices import ActualDices
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
    def __init__(self, selected_character_id: Characters.CharId):
        self._selected_character_id = selected_character_id

    def get_selected_character_id(self) -> Characters.CharId:
        return self._selected_character_id


class EndRoundAction(PlayerAction):
    pass


class GameAction(PlayerAction):
    def is_valid_action(self, game_state: gs.GameState) -> bool:
        raise Exception("Not overriden")


class CardAction(GameAction):
    from dgisim.src.card.card import Card

    def __init__(self, card: type[Card], instruction: Instruction) -> None:
        pass


class SkillAction(GameAction):
    from dgisim.src.character.character import CharacterSkill

    def __init__(self, skill: CharacterSkill, instruction: Instruction) -> None:
        self._skill = skill
        self._instruction = instruction

    def __str__(self) -> str:
        return f"<{self._skill}, {self._instruction}>"


class SwapAction(GameAction):
    def __init__(self, selected_character_id: Characters.CharId, instruction: Instruction):
        self._selected_character_id = selected_character_id
        self._instruction = instruction

    def get_selected_character_id(self) -> Characters.CharId:
        return self._selected_character_id


class Instruction:
    pass


class DiceOnlyInstruction(Instruction):
    def __init__(self, dices: ActualDices) -> None:
        self._dices = dices

    def dices(self) -> ActualDices:
        return self._dices

    def __str__(self) -> str:
        return str(self._dices.num_dices())
