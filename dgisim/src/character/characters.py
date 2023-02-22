from __future__ import annotations
from typing import Tuple, Optional

from dgisim.src.character.character import Character
from dgisim.src.helper.level_print import level_print, INDENT, level_print_single


class Characters:
    CharId = int

    def __init__(self, characters: Tuple[Character], active_character: Optional[Characters.CharId]):
        self._characters = characters
        self._active_character_id = active_character

    @classmethod
    def from_default(cls, characters: Tuple[Character]) -> Characters:
        return cls(characters, None)

    def get_characters(self) -> Tuple[Character]:
        return self._characters

    def get_active_character_id(self) -> Optional[Characters.CharId]:
        return self._active_character_id

    def get_active_character(self) -> Optional[Character]:
        if self._active_character_id is None:
            return None
        return self._characters[self._active_character_id]

    def get_active_character_name(self) -> str:
        char = self.get_active_character()
        if char is None:
            return "None"
        return char.name()

    def char_id_valid(self, char_id: Characters.CharId) -> bool:
        return char_id >= 0 and char_id < len(self._characters)

    def factory(self) -> CharactersFactory:
        return CharactersFactory(self)

    def _all_unique_data(self) -> Tuple:
        return (self._characters, self._active_character_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Characters):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        return level_print({
            "Active Character": level_print_single(self.get_active_character_name(), new_indent),
            "Characters": ''.join([char.to_string(new_indent) for char in self._characters]),
        }, indent)


class CharactersFactory:

    def __init__(self, characters: Characters):
        self._characters = characters.get_characters()
        self._active_character_id = characters.get_active_character_id()

    def characters(self, chars: Tuple[Character]) -> CharactersFactory:
        self._characters = chars
        return self

    def active_character_id(self, id: Characters.CharId) -> CharactersFactory:
        self._active_character_id = id
        return self

    def build(self) -> Characters:
        return Characters(
            self._characters,
            self._active_character_id,
        )
