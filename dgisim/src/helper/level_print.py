from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Union

__all__ = [
    "GamePrinter",
    "INDENT",
    "StrDrawer",
    "level_print",
]

_INDENTATION = "| "
INDENT = len(_INDENTATION)


def level_print(strs: Dict[str, str], indent: int = 0) -> str:
    indentation = _INDENTATION * (indent // INDENT)
    str_builder = []
    for key, val in strs.items():
        if val and val[-1] == '\n':
            str_builder.append(indentation + '<' + key + ">:\n")
            str_builder.append(val)
        else:
            str_builder.append(indentation + '<' + key + ">: ")
            str_builder.append(val + '\n')
    return ''.join(str_builder)


def level_print_single(s: str, indent: int = 0) -> str:
    """
    format prints one line of string
    """
    indentation = _INDENTATION * (indent // INDENT)
    return indentation + s + '\n'


class StrDrawer:
    @dataclass(frozen=True)
    class _Insertion:
        x: int
        y: int
        s: str

    def __init__(self, lim_x: int = 0, lim_y: int = 0) -> None:
        self._lim_x = lim_x
        self._lim_y = lim_y
        self._insertions: list[StrDrawer._Insertion] = []

    def lim_x(self) -> int:
        return self._lim_x

    def lim_y(self) -> int:
        return self._lim_y

    def insert_at(self, x: int, y: int, s: str) -> tuple[int, int]:
        assert '\n' not in s
        self._insertions.append(StrDrawer._Insertion(x, y, s))
        if x > self._lim_x:
            self._lim_x = x
        y_end = y + len(s)
        if y_end > self._lim_y:
            self._lim_y = y_end
        return (x, y_end)

    def insert_at_nextline(self, y: int, s: str) -> tuple[int, int]:
        return self.insert_at(self.lim_x() + 1, y, s)

    def insert_board_at(self, x: int, y: int, other: StrDrawer) -> tuple[int, int]:
        max_x, max_y = 0, 0
        for insertion in other._insertions:
            nx, ny = self.insert_at(
                insertion.x + x,
                insertion.y + y,
                insertion.s,
            )
            max_x = max(max_x, nx)
            max_y = max(max_y, ny)
        return (max_x, max_y)

    def insert_board_at_nextline(self, y: int, other: StrDrawer) -> tuple[int, int]:
        return self.insert_board_at(self._lim_x + 1, y, other)

    def clear(self) -> None:
        self._insertions = []

    def draw(self) -> str:
        board = [[' ' for j in range(self._lim_y + 1)] for i in range(self._lim_x + 1)]
        for insertion in self._insertions:
            for i, c in enumerate(insertion.s):
                board[insertion.x][insertion.y + i] = c
        return '\n'.join(''.join(cs).rstrip() for cs in board)


class GamePrinter:

    @staticmethod
    def _pair(d: dict, key: str) -> str:
        return "<" + key + ": " + str(d[key]) + ">"

    @staticmethod
    def _insert_lines(board: StrDrawer, y: int, d: dict, keys: list[str]) -> None:
        for key in keys:
            board.insert_at_nextline(y, GamePrinter._pair(d, key))

    @staticmethod
    def _insert_character(name: str, character: dict) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<{name}{'[x]' if not character['Alive'] else ''}>")
        GamePrinter._insert_lines(board, 2, character, [
            # "id",
            "Aura",
        ])
        board.insert_at_nextline(2, f"<HP: {character['HP']}/{character['Max HP']}>")
        board.insert_at_nextline(2, f"<Energy: {character['Energy']}/{character['Max Energy']}>")
        board.insert_board_at_nextline(
            2,
            GamePrinter._insert_str_list("Hiddens", character["Hiddens"])
        )
        board.insert_board_at_nextline(
            2,
            GamePrinter._insert_str_list("Equipments", character["Equipments"])
        )
        board.insert_board_at_nextline(
            2,
            GamePrinter._insert_str_list("Statuses", character["Statuses"])
        )
        return board

    @staticmethod
    def _insert_characters(characters: dict) -> StrDrawer:
        board = StrDrawer()
        # board.insert_at(0, 0, GamePrinter._pair(characters, "Active Character"))
        board.insert_at(0, 0, "<Characters>")
        character_boards = []
        for name, character in characters["Characters"].items():
            character_boards.append(GamePrinter._insert_character(
                ('*' if name == characters["Active Character"] else '') + name,
                character,
            ))
        for c_board in character_boards:
            board.insert_board_at_nextline(2, c_board)
        return board

    @staticmethod
    def _insert_str_list(name: str, str_list: list) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<{name}>")
        for s in str_list:
            board.insert_at_nextline(2, f"<{s}>")
        return board

    @staticmethod
    def _insert_str_str_dict(name: str, d: dict) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<{name}>")
        for key in d:
            board.insert_at_nextline(2, GamePrinter._pair(d, key))
        return board

    @staticmethod
    def _insert_player(name: str, player: dict) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<Player: {name}>")
        board.insert_at_nextline(0, GamePrinter._pair(player, "Phase"))
        board.insert_at_nextline(0, GamePrinter._pair(player, "Card/Dice Redraw Chances"))
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_characters(player["Characters"]),
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_list("Hidden Statuses", player["Hidden Statuses"])
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_list("Combat Statuses", player["Combat Statuses"])
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Summons", player["Summons"])
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Supports", player["Supports"])
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Dice", player["Dice"]),
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Hand Cards", player["Hand Cards"]),
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Deck Cards", player["Deck Cards"]),
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict("Publicly Used Cards", player["Publicly Used Cards"]),
        )
        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_str_str_dict(
                "Publicly Gained Cards", player["Publicly Gained Cards"]),
        )
        return board

    @staticmethod
    def _insert_effect(name: str, effect: Union[dict, str]) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<{name}>")
        if type(effect) is str:
            if effect != "{}":
                board.insert_at_nextline(2, f"<{effect}>")
        else:
            assert type(effect) is dict
            for field, content in effect.items():
                content = ''.join(c for c in str(content) if c != '\n')
                board.insert_at_nextline(2, f"<{field}: {content}>")
        return board

    @staticmethod
    def _insert_effects(name: str, effects: dict) -> StrDrawer:
        board = StrDrawer()
        board.insert_at(0, 0, f"<{name}>")
        es = []
        for effect in effects:
            es.append(GamePrinter._insert_effect(effect, effects[effect]))
        for effect_board in es:
            board.insert_board_at_nextline(2, effect_board)
        return board

    @staticmethod
    def dict_game_printer(game_state: dict) -> str:
        board = StrDrawer()
        x, y = 0, -2
        x, y = board.insert_at(x, y + 2, GamePrinter._pair(game_state, "Mode"))
        x, y = board.insert_at(x, y + 2, GamePrinter._pair(game_state, "Phase"))
        x, y = board.insert_at(x, y + 2, GamePrinter._pair(game_state, "Round"))
        # x, y = board.insert_at(x, y + 2, GamePrinter._pair(game_state, "Active Player"))

        p1_active = '1' in game_state["Active Player"]
        p1_board = GamePrinter._insert_player(
            f"{'*' if p1_active else ''}Player1",
            game_state["Player1"]
        )
        p2_board = GamePrinter._insert_player(
            f"{'*' if not p1_active else ''}Player2",
            game_state["Player2"]
        )
        player_row_start = 2
        board.insert_board_at(player_row_start, 0, p1_board)
        px, py = board.insert_board_at(player_row_start, p1_board.lim_y() + 4, p2_board)
        for i in range(player_row_start, board.lim_x() + 1):
            board.insert_at(i, p1_board.lim_y() + 2, '|')
            board.insert_at(i, py + 2, '|')
        board.insert_at_nextline(0, "-" * (board.lim_y()))
        board.insert_at(1, 0, "-" * (board.lim_y()))

        board.insert_board_at_nextline(
            0,
            GamePrinter._insert_effects("Effects", game_state["Effects"]),
        )
        board.insert_at_nextline(0, "=" * board.lim_y())
        return board.draw()
