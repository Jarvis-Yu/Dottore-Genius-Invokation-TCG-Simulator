from __future__ import annotations
from typing_extensions import Self
from dataclasses import dataclass

import dgisim.src.state.game_state as gs
import dgisim.src.card.cards as cds
import dgisim.src.action.action as act
import dgisim.src.effect.effect as eft
from dgisim.src.dices import ActualDices, AbstractDices
from dgisim.src.character.character_skill_enum import CharacterSkill

Choosable = eft.StaticTarget | int | ActualDices | CharacterSkill

@dataclass(frozen=True, kw_only=True)
class ActionGenerator:
    game_state: gs.GameState
    pid: gs.GameState.Pid
    action: act.PlayerAction
    instruction: None | act.Instruction= None

    def _action_filled_but_instruction(self) -> bool:
        # return self.action.filled(exceptions={"instruction"})
        return False

    def _action_filled(self) -> bool:
        # return self.action.filled()
        return False

    def _instruction_filled(self) -> bool:
        # return self.instruction is None \
        #     or self.instruction.filled()
        return False

    def filled(self) -> bool:
        return self._action_filled() and self._instruction_filled()

    def generate_action(self) -> act.PlayerAction:
        assert self.filled()
        raise NotImplementedError

    def choices(self) -> tuple[Choosable] | AbstractDices | cds.Cards:
        assert not self.filled()
        if not self._action_filled_but_instruction():
            pass
        elif not self._instruction_filled():
            pass
        else:
            assert not self._action_filled()
            self._action_filled()
        return (-1, )

    def dices_available(self) -> ActualDices:
        return self.game_state.get_player(self.pid).get_dices()

    def choose(self, choice: Choosable | ActualDices | cds.Cards) -> Self:
        return self
