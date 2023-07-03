from __future__ import annotations
from dataclasses import dataclass, replace, fields
from typing import Callable, TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    from ..state.game_state import GameState
    from ..state.enums import PID
    from ..dices import ActualDices

    from .action import PlayerAction, Instruction
    from .types import DecidedChoiceType, GivenChoiceType


@dataclass(frozen=True, kw_only=True)
class ActionGenerator:
    game_state: GameState
    pid: PID
    action: PlayerAction
    instruction: None | Instruction = None
    _choices_helper: Callable[[Self], GivenChoiceType]
    _fill_helper: Callable[[Self, DecidedChoiceType], Self]

    def _action_filled(self) -> bool:
        return self.action._filled(exceptions={"instruction"})

    def _instruction_filled(self) -> bool:
        return self.instruction is None \
            or self.instruction._filled()

    def _legal_action(self) -> bool:
        return self.action.legal()

    def _legal_instruction(self) -> bool:
        return self.instruction is None or self.instruction.legal()

    def filled(self) -> bool:
        return self._action_filled() and self._instruction_filled()

    def valid(self) -> bool:
        return self._legal_action() and self._legal_instruction()

    def generate_action(self) -> PlayerAction:
        assert self.filled()
        action = self.action
        if self.instruction is not None:
            action = replace(action, instruction=self.instruction)
        return action

    def choices(self) -> GivenChoiceType:
        assert not self.filled()
        return self._choices_helper(self)

    def dices_available(self) -> ActualDices:
        return self.game_state.get_player(self.pid).get_dices()

    def choose(self, choice: DecidedChoiceType) -> ActionGenerator:
        return self._fill_helper(self, choice)

    def __str__(self) -> str:
        field_pairs = [f"<{field.name}, {getattr(self, field.name)}>" for field in fields(self)]
        content = '\n'.join(field_pairs)
        return self.__class__.__name__ + '\n' + content
