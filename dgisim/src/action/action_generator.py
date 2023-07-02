from __future__ import annotations
from dataclasses import dataclass, replace, fields
from typing import Callable, TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    import dgisim.src.action.action as act
    import dgisim.src.card.card as cd
    import dgisim.src.card.cards as cds
    import dgisim.src.state.game_state as gs
    from dgisim.src.state.enums import PID
    from dgisim.src.dices import ActualDices, AbstractDices


@dataclass(frozen=True, kw_only=True)
class ActionGenerator:
    game_state: gs.GameState
    pid: PID
    action: act.PlayerAction
    instruction: None | act.Instruction = None
    _choices_helper: Callable[[Self], tuple[cd.Choosable, ...] | AbstractDices | cds.Cards]
    _fill_helper: Callable[[Self, cd.Choosable | ActualDices | cds.Cards], Self]

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

    def generate_action(self) -> act.PlayerAction:
        assert self.filled()
        action = self.action
        if self.instruction is not None:
            action = replace(action, instruction=self.instruction)
        return action

    def choices(self) -> tuple[cd.Choosable, ...] | AbstractDices | cds.Cards:
        assert not self.filled()
        return self._choices_helper(self)

    def dices_available(self) -> ActualDices:
        return self.game_state.get_player(self.pid).get_dices()

    def choose(self, choice: cd.Choosable | ActualDices | cds.Cards) -> ActionGenerator:
        return self._fill_helper(self, choice)

    def __str__(self) -> str:
        field_pairs = [f"<{field.name}, {getattr(self, field.name)}>" for field in fields(self)]
        content = '\n'.join(field_pairs)
        return self.__class__.__name__ + '\n' + content
