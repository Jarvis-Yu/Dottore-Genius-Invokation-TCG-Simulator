from typing import List, Tuple, Type, Optional, Any

from dgisim.src.character.character import Character
from dgisim.src.helper.level_print import level_print, INDENT, level_print_single


class Characters:
    def __init__(self, characters: List[Character]):
        self._characters = characters
        self._team_size = len(characters)
        self._active_character: Optional[int] = None

    def get_characters(self) -> Tuple:
        return tuple(self._characters)

    def set_active_character(self, character: Type[Character]) -> bool:
        # if new active character is current active character
        if self._active_character is not None and isinstance(self._characters[self._active_character], character):
            return False
        for i, char in enumerate(self._characters):
            if isinstance(char, character):
                if char.defeated():
                    return False
                else:
                    self._active_character = i
                    return True
        return False

    def _all_unique_data(self) -> Tuple:
        return (self._characters, self._team_size, self._active_character)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Characters):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        return ''.join([char.to_string(indent) for char in self._characters])
