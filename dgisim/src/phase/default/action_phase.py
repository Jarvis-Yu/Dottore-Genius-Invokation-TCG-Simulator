from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .. import phase as ph

from ...action.action import *
from ...action.action_generator import ActionGenerator
from ...action.enums import ActionType
from ...character.enums import CharacterSkill
from ...effect.effect import *
from ...effect.enums import TriggeringSignal, Zone
from ...effect.structs import StaticTarget
from ...element import Element
from ...event import *
from ...helper.quality_of_life import just
from ...state.enums import Pid, Act

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...state.game_state import GameState

__all__ = [
    "ActionPhase",
]


class ActionPhase(ph.Phase):
    def _start_up_phase(self, game_state: GameState) -> GameState:
        # TODO: Handle before action statuses
        active_player_id = game_state.get_active_player_id()
        return game_state.factory().player(
            active_player_id,
            game_state.get_player(active_player_id).factory().phase(
                Act.ACTION_PHASE
            ).build()
        ).build()

    def _to_end_phase(self, game_state: GameState) -> GameState:
        active_player_id = game_state.get_active_player_id()
        return game_state.factory().phase(
            game_state.get_mode().end_phase()
        ).player(
            active_player_id,
            game_state.get_player(active_player_id).factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).build()
        ).other_player(
            active_player_id,
            game_state.get_other_player(active_player_id).factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).build()
        ).build()

    def _execute_effect(self, game_state: GameState) -> GameState:
        effect_stack, effect = game_state.get_effect_stack().pop()
        new_game_state = game_state.factory().effect_stack(effect_stack).build()
        return effect.execute(new_game_state)

    def _is_executing_effects(self, game_state: GameState) -> bool:
        effect_stack = game_state.get_effect_stack()
        return not effect_stack.is_empty() \
            and not isinstance(effect_stack.peek(), DeathSwapPhaseStartEffect)

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        if p1.is_action_phase() or p2.is_action_phase():
            assert self._is_executing_effects(game_state)
            return self._execute_effect(game_state)
        elif p1.is_passive_wait_phase() and p2.is_passive_wait_phase():
            return self._start_up_phase(game_state)
        elif p1.is_end_phase() and p2.is_end_phase():
            return self._to_end_phase(game_state)
        raise Exception("Not Reached! Unknown Game State to process")

    def _handle_end_round(
            self,
            game_state: GameState,
            pid: Pid,
            action: EndRoundAction
    ) -> GameState:
        active_player_id = game_state.get_active_player_id()
        assert active_player_id == pid
        active_player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        if other_player.get_phase() is Act.END_PHASE:
            other_player_new_phase = Act.END_PHASE
        elif other_player.get_phase() is Act.PASSIVE_WAIT_PHASE:
            other_player_new_phase = Act.ACTION_PHASE
        else:  # pragma: no cover
            print(f"ERROR pid={pid}\n {game_state}")
            raise Exception(f"Unknown Game State to process {other_player.get_phase()}")
        return game_state.factory().active_player_id(
            active_player_id.other()
        ).player(
            active_player_id,
            active_player.factory().phase(
                Act.END_PHASE
            ).build()
        ).other_player(
            active_player_id,
            other_player.factory().phase(
                other_player_new_phase
            ).build()
        ).build()

    def _handle_skill_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: SkillAction
    ) -> Optional[GameState]:
        # Check action validity
        result = game_state.skill_checker().valid_action(pid, action)
        if result is None:
            raise Exception(f"{action} from {pid} is invalid for gamestate:\n{game_state}")
        game_state = result

        player = game_state.get_player(pid)
        instruction = action.instruction
        new_effects: list[Effect] = []
        # Costs
        dices = player.get_dices()
        new_dices = dices - instruction.dices
        assert new_dices.is_legal()
        # Skill Effect
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        assert active_character.can_cast_skill()
        # note: it's important to cast skill before new_dices are putted into the game_state
        #       so that normal_attacks can correctly be marked as charged attack
        new_effects += active_character.skill(
            game_state,
            StaticTarget(pid, Zone.CHARACTERS, active_character.get_id()),
            action.skill
        )
        new_effects.append(AllStatusTriggererEffect(
            pid,
            TriggeringSignal.COMBAT_ACTION,
        ))
        new_effects.append(TurnEndEffect())
        # Afterwards
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(new_effects)
        ).player(
            pid,
            player.factory().dices(new_dices).build()
        ).build()

    def _handle_swap_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: SwapAction
    ) -> Optional[GameState]:
        # Check action validity
        result = game_state.swap_checker().valid_action(pid, action)
        if result is None:
            raise Exception(f"{action} from {pid} is invalid for gamestate:\n{game_state}")
        game_state, action_speed = result

        player = game_state.get_player(pid)
        new_effects: list[Effect] = []

        # Costs
        new_dices = player.get_dices() - action.instruction.dices
        assert new_dices.is_legal()

        # Add Effects
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        new_effects.append(SwapCharacterEffect(
            StaticTarget(pid, Zone.CHARACTERS, action.char_id)
        ))

        if action_speed is EventSpeed.COMBAT_ACTION:
            new_effects.append(
                AllStatusTriggererEffect(
                    pid=pid,
                    signal=TriggeringSignal.COMBAT_ACTION,
                )
            )
            new_effects.append(TurnEndEffect())
        elif action_speed is EventSpeed.FAST_ACTION:
            new_effects.append(
                AllStatusTriggererEffect(
                    pid=pid,
                    signal=TriggeringSignal.FAST_ACTION,
                )
            )

        return game_state.factory().effect_stack(
            game_state.get_effect_stack().push_many_fl(new_effects)
        ).player(
            pid,
            player.factory().dices(new_dices).build()
        ).build()

    def _handle_card_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: CardAction
    ) -> Optional[GameState]:
        paid_dices = action.instruction.dices
        card = action.card

        # verify action validity
        preprocessed_game_state = card.valid_instruction(game_state, pid, action.instruction)
        if preprocessed_game_state is None:
            raise Exception(f"{action.instruction} is not valid of the {card.name()} "
                            + f"in the game state:\n{game_state}")
        game_state = preprocessed_game_state

        #  setup
        player = game_state.get_player(pid)
        new_effects: list[Effect] = []

        # Costs
        dices = player.get_dices()
        new_dices = dices - paid_dices
        assert new_dices.is_legal()

        # Card
        new_effects.append(PublicRemoveCardEffect(pid, card))
        new_effects += card.effects(game_state, pid, action.instruction)
        if card.is_combat_action():
            new_effects.append(AllStatusTriggererEffect(
                pid,
                TriggeringSignal.COMBAT_ACTION,
            ))
            new_effects.append(TurnEndEffect())
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(new_effects)
        ).player(
            pid,
            player.factory().dices(new_dices).build()
        ).build()

    def _handle_elemental_tuning_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: ElementalTuningAction
    ) -> Optional[GameState]:
        player = game_state.get_player(pid)
        cards = player.get_hand_cards()
        dices = player.get_dices()
        active_character = player.get_active_character()
        assert active_character is not None
        active_character_elem = active_character.element()
        if action.card not in cards \
                or dices[action.dice_elem] == 0 \
                or action.dice_elem is active_character_elem \
                or dices[Element.OMNI] + dices[active_character_elem] == dices.num_dices():
            print(f"{action} cannot be performed in game state:\n{game_state}")
            assert False
            return None
        from ...card.card import OmniCard
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_dices(
                lambda ds: ds + {action.dice_elem: -1, active_character_elem: 1}
            ).f_hand_cards(
                lambda hcs: hcs.remove(action.card)
            ).f_publicly_used_cards(
                lambda pucs: pucs.add(OmniCard)
            ).build()
        ).build()

    def _handle_death_swap_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: DeathSwapAction
    ) -> Optional[GameState]:
        # Check action validity
        result = game_state.swap_checker().valid_action(pid, action)
        if result is None:
            raise Exception(f"{action} from {pid} is invalid for gamestate:\n{game_state}")
        game_state, _ = result

        game_state = game_state.factory().f_effect_stack(lambda es: es.pop()[0]).build()
        player = game_state.get_player(pid)
        effect_stack = game_state.get_effect_stack()
        # Add Effects
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        effect_stack = effect_stack.push_one(SwapCharacterEffect(
            StaticTarget(pid, Zone.CHARACTERS, action.char_id)
        ))
        return game_state.factory().effect_stack(
            effect_stack
        ).build()

    def _handle_game_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: GameAction
    ) -> Optional[GameState]:
        player = game_state.get_player(pid)
        if isinstance(action, SkillAction):
            return self._handle_skill_action(game_state, pid, action)
        elif isinstance(action, SwapAction):
            return self._handle_swap_action(game_state, pid, action)
        elif isinstance(action, CardAction):
            return self._handle_card_action(game_state, pid, action)
        elif isinstance(action, ElementalTuningAction):
            return self._handle_elemental_tuning_action(game_state, pid, action)
        elif isinstance(action, DeathSwapAction):
            return self._handle_death_swap_action(game_state, pid, action)
        raise Exception("Unhandld action", action)  # pragma: no cover

    def step_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: PlayerAction
    ) -> Optional[GameState]:
        # check action arrived at the right state
        if pid is not self.waiting_for(game_state):
            raise Exception(f"Unexpected action from {pid} at game state:\n{game_state}")

        # check death swap phase
        if game_state.death_swapping(pid):
            if not isinstance(action, DeathSwapAction):
                raise Exception(f"Trying to execute {action} when a death swap is expected")
            # game_state = game_state.factory().effect_stack(effect_stack.pop()[0]).build()

        if isinstance(action, GameAction):
            return self._handle_game_action(game_state, pid, action)
        elif isinstance(action, EndRoundAction):
            return self._handle_end_round(game_state, pid, action)
        raise Exception("Not Reached! Unknown Game State to process")

    def waiting_for(self, game_state: GameState) -> Optional[Pid]:
        effect_stack = game_state.get_effect_stack()
        # if no effects are to be executed or death swap phase is inserted
        if effect_stack.is_empty() or game_state.death_swapping():
            return super().waiting_for(game_state)
        else:
            return None

    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        # death swap check
        if game_state.death_swapping(pid):
            return (ActionType.SWAP_CHARACTER, )

        choices: list[ActionType] = []

        # cards
        if game_state.card_checker().playable(pid):
            choices.append(ActionType.PLAY_CARD)

        # skills
        if game_state.skill_checker().skillable(pid):
            choices.append(ActionType.CAST_SKILL)

        # swaps
        if game_state.swap_checker().swappable(pid):
            choices.append(ActionType.SWAP_CHARACTER)

        # elemental tuning
        if game_state.elem_tuning_checker().usable(pid):
            choices.append(ActionType.ELEMENTAL_TUNING)

        # unconditional end round
        choices.append(ActionType.END_ROUND)
        return tuple(choices)

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        game_state = action_generator.game_state
        pid = action_generator.pid

        if game_state.death_swapping(pid):
            assert player_choice is ActionType.SWAP_CHARACTER
            from ...action.action_generator_generator import SwapActGenGenerator
            return just(SwapActGenGenerator.action_generator(game_state, pid))

        if player_choice is ActionType.PLAY_CARD:
            assert game_state.card_checker().playable(pid)
            from ...action.action_generator_generator import CardActGenGenerator
            return just(CardActGenGenerator.action_generator(game_state, pid))
        elif player_choice is ActionType.SWAP_CHARACTER:
            assert game_state.swap_checker().swappable(pid)
            from ...action.action_generator_generator import SwapActGenGenerator
            return just(SwapActGenGenerator.action_generator(game_state, pid))
        elif player_choice is ActionType.CAST_SKILL:
            assert game_state.skill_checker().skillable(pid)
            from ...action.action_generator_generator import SkillActGenGenerator
            return just(SkillActGenGenerator.action_generator(game_state, pid))
        elif player_choice is ActionType.ELEMENTAL_TUNING:
            assert game_state.elem_tuning_checker().usable(pid)
            from ...action.action_generator_generator import ElemTuningActGenGenerator
            return just(ElemTuningActGenGenerator.action_generator(game_state, pid))
        elif player_choice is ActionType.END_ROUND:
            return ActionGenerator(game_state=game_state, pid=pid, action=EndRoundAction())
        else:  # pragma: no cover
            action_type_name = ActionType.__name__
            if isinstance(player_choice, ActionType):
                raise Exception(f"Unhandled player {action_type_name} {player_choice}")
            else:
                raise TypeError(f"Unexpected player choice {player_choice} where"
                                + f"where {action_type_name} is expected")

    def action_generator(self, game_state: GameState, pid: Pid) -> ActionGenerator | None:
        if pid is not self.waiting_for(game_state):
            return None
        return ActionGenerator(
            game_state=game_state,
            pid=pid,
            _choices_helper=self._choices_helper,
            _fill_helper=self._fill_helper,
        )
