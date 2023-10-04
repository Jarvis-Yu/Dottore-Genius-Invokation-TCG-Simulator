from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .. import phase as ph

from ...action.action import *
from ...action.action_generator import ActionGenerator
from ...action.enums import ActionType
from ...character.enums import CharacterSkill
from ...dice import ActualDice
from ...effect.effect import *
from ...effect.enums import TriggeringSignal, Zone
from ...effect.structs import StaticTarget
from ...element import Element
from ...event import *
from ...helper.quality_of_life import just
from ...state.enums import Pid, Act
from ...status.status import PersonalStatus, PrepareSkillStatus

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...effect.effect_stack import EffectStack
    from ...state.game_state import GameState

__all__ = [
    "ActionPhase",
]


class ActionPhase(ph.Phase):
    def _start_up_phase(self, game_state: GameState) -> GameState:
        active_player_id = game_state.get_active_player_id()
        appended_effects: list[Effect] = []
        if (game_state.get_round() == 0):
            appended_effects.append(
                AllStatusTriggererEffect(
                    active_player_id,
                    TriggeringSignal.GAME_START,
                )
            )
        appended_effects.append(
            AllStatusTriggererEffect(
                active_player_id,
                TriggeringSignal.ROUND_START,
            )
        )
        return game_state.factory().f_player(
            active_player_id,
            lambda p: p.factory().phase(
                Act.ACTIVE_WAIT_PHASE
            ).build()
        ).f_effect_stack(
            lambda es: es.push_many_fl(appended_effects)
        ).build()

    def _begin_action_phase(self, game_state: GameState) -> GameState:
        active_player_id = game_state.get_active_player_id()
        return game_state.factory().f_player(
            active_player_id,
            lambda p: p.factory().phase(
                Act.ACTION_PHASE
            ).build()
        ).f_effect_stack(
            lambda es: es.push_one(
                AllStatusTriggererEffect(
                    active_player_id,
                    TriggeringSignal.PRE_ACTION,
                )
            )
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

    def _handle_prepare_skill(self, game_state: GameState) -> GameState:
        pid = super().waiting_for(game_state)
        assert pid is not None
        prepare_skill_status = self._get_prepare_skill_status(game_state, pid)
        assert prepare_skill_status is not None
        status_source = StaticTarget(
            pid,
            Zone.CHARACTERS,
            game_state.get_player(pid).just_get_active_character().get_id(),
        )
        assert isinstance(prepare_skill_status, PersonalStatus), prepare_skill_status
        effects = [
            TriggerStatusEffect(
                target=status_source,
                status=type(prepare_skill_status),
                signal=TriggeringSignal.ACT_PRE_SKILL,
            ),
            AllStatusTriggererEffect(
                pid,
                TriggeringSignal.COMBAT_ACTION,
            ),
            TurnEndEffect(),
        ]
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()

    def _is_executing_effects(self, game_state: GameState) -> bool:
        effect_stack = game_state.get_effect_stack()
        return not effect_stack.is_empty() \
            and not isinstance(effect_stack.peek(), DeathSwapPhaseStartEffect)

    def _get_prepare_skill_status(self, game_state: GameState, pid: Pid) -> None | PrepareSkillStatus:
        player = game_state.get_player(pid)
        active_character = player.get_active_character()
        assert active_character is not None, game_state
        if not active_character.can_cast_skill():
            return None
        prepare_skill_status = next((
            status
            for status in active_character.get_all_statuses_ordered_flattened()
            if isinstance(status, PrepareSkillStatus)
        ), None)
        return prepare_skill_status

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        if p1.in_action_phase() or p2.in_action_phase():
            if self._is_executing_effects(game_state):
                return self._execute_effect(game_state)
            else:
                assert self.waiting_for(game_state) is None
                return self._handle_prepare_skill(game_state)
        elif p1.in_passive_wait_phase() and p2.in_passive_wait_phase():
            return self._start_up_phase(game_state)
        elif p1.in_active_wait_phase() or p2.in_active_wait_phase():
            if self._is_executing_effects(game_state):
                return self._execute_effect(game_state)
            return self._begin_action_phase(game_state)
        elif p1.in_end_phase() and p2.in_end_phase():
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
        effects: list[Effect] = [
            PlayerStatusTriggererEffect(
                pid=active_player_id,
                self_signal=TriggeringSignal.SELF_DECLARE_END_ROUND,
                other_signal=TriggeringSignal.OPPO_DECLARE_END_ROUND,
            )
        ]
        if other_player.get_phase() is Act.END_PHASE:
            other_player_new_phase = Act.END_PHASE
        elif other_player.get_phase() is Act.PASSIVE_WAIT_PHASE:
            other_player_new_phase = Act.ACTION_PHASE
            effects.append(AllStatusTriggererEffect(
                active_player_id.other(),
                TriggeringSignal.PRE_ACTION,
            ))
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
        ).f_effect_stack(
            lambda es: es.push_many_fl(effects)
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
        dice = player.get_dice()
        new_dice = dice - instruction.dice
        assert new_dice.is_legal()
        # Skill Effect
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        assert active_character.can_cast_skill()
        if dice.is_even():
            from ...status.status import ChargedAttackStatus
            new_effects.append(UpdateHiddenStatusEffect(
                target_pid=pid,
                status=ChargedAttackStatus(can_charge=True),
            ))
        new_effects.append(CastSkillEffect(
            target=StaticTarget.from_char_id(pid, active_character.get_id()),
            skill=action.skill,
        ))
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
            player.factory().dice(new_dice).build()
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
        new_dice = player.get_dice() - action.instruction.dice
        assert new_dice.is_legal()

        # Add Effects
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        new_effects.append(SwapCharacterEffect(
            StaticTarget(pid, Zone.CHARACTERS, action.char_id)
        ))

        if action_speed is EventSpeed.COMBAT_ACTION:
            new_effects.append(TurnEndEffect())

        return game_state.factory().effect_stack(
            game_state.get_effect_stack().push_many_fl(new_effects)
        ).player(
            pid,
            player.factory().dice(new_dice).build()
        ).build()

    def _handle_card_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: CardAction
    ) -> Optional[GameState]:
        paid_dice = action.instruction.dice
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
        dice = player.get_dice()
        new_dice = dice - paid_dice
        assert new_dice.is_legal()

        # Card
        new_effects.append(PublicRemoveCardEffect(pid, card))
        if card.is_combat_action() and dice.is_even():
            from ...status.status import ChargedAttackStatus
            new_effects.append(UpdateHiddenStatusEffect(
                target_pid=pid,
                status=ChargedAttackStatus(can_charge=True),
            ))
        new_effects += card.effects(game_state, pid, action.instruction)
        if card.is_combat_action():
            new_effects.append(AllStatusTriggererEffect(
                pid,
                TriggeringSignal.COMBAT_ACTION,
            ))
        new_effects.append(AllStatusTriggererEffect(
            pid,
            TriggeringSignal.POST_CARD,
        ))
        if card.is_combat_action():
            new_effects.append(TurnEndEffect())
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(new_effects)
        ).player(
            pid,
            player.factory().dice(new_dice).build()
        ).build()

    def _handle_elemental_tuning_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: ElementalTuningAction
    ) -> Optional[GameState]:
        player = game_state.get_player(pid)
        cards = player.get_hand_cards()
        dice = player.get_dice()
        active_character = player.get_active_character()
        assert active_character is not None
        active_character_elem = active_character.ELEMENT()
        if action.card not in cards \
                or dice[action.dice_elem] == 0 \
                or action.dice_elem is active_character_elem \
                or dice[Element.OMNI] + dice[active_character_elem] == dice.num_dice():
            print(f"{action} cannot be performed in game state:\n{game_state}")
            assert False
            return None
        from ...card.card import OmniCard
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_dice(
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

    def _handle_dice_select_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: DiceSelectAction
    ) -> Optional[GameState]:
        if action.selected_dice.is_empty():
            return game_state.factory().f_player(
                pid,
                lambda p: p.factory().dice_reroll_chances(0).build()
            ).f_effect_stack(
                lambda es: es.pop()[0]  # removes rolling phase effect
            ).build()

        player = game_state.get_player(pid)
        dice = player.get_dice()
        kept_dice = dice - action.selected_dice
        assert kept_dice.is_legal()
        replacement_dice = ActualDice.from_random(action.selected_dice.num_dice())
        new_dice = kept_dice + replacement_dice
        new_reroll_chances = player.get_dice_reroll_chances() - 1
        new_effect_stack: EffectStack
        if new_reroll_chances > 0:
            new_effect_stack = game_state.get_effect_stack()
        else:
            # removes rolling phase effect
            new_effect_stack = game_state.get_effect_stack().pop()[0]
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory()
            .dice_reroll_chances(new_reroll_chances)
            .dice(new_dice)
            .build()
        ).effect_stack(
            new_effect_stack
        ).build()

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

        elif self._rolling(game_state):  # pragma: no cover
            if not isinstance(action, DiceSelectAction):
                raise Exception(f"Trying to execute {action} when a dice selection is expected")

        if isinstance(action, GameAction):
            return self._handle_game_action(game_state, pid, action)
        elif isinstance(action, DiceSelectAction):
            return self._handle_dice_select_action(game_state, pid, action)
        elif isinstance(action, EndRoundAction):
            return self._handle_end_round(game_state, pid, action)
        raise Exception("Not Reached! Unknown Game State to process")

    @classmethod
    def _rolling(cls, game_state: GameState) -> bool:
        effect_stack = game_state.get_effect_stack()
        return (
            effect_stack.is_not_empty()
            and isinstance(effect_stack.peek(), RollPhaseStartEffect)
        )

    def waiting_for(self, game_state: GameState) -> Optional[Pid]:
        effect_stack = game_state.get_effect_stack()
        # if no effects are to be executed or death swap phase is inserted
        if effect_stack.is_empty():
            pid = super().waiting_for(game_state)
            if pid is None:
                return pid
            if self._get_prepare_skill_status(game_state, pid) is None:
                return pid
            return None
        elif game_state.death_swapping():
            return super().waiting_for(game_state)
        elif isinstance(effect_stack.peek(), PhaseStartEffect):
            effect = effect_stack.peek()
            if isinstance(effect, RollPhaseStartEffect):
                return super().waiting_for(game_state)
            else:
                raise NotImplementedError
        else:
            return None

    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        # death swap check
        if game_state.death_swapping(pid):
            return (ActionType.SWAP_CHARACTER, )

        # inserted roll phase
        if cls._rolling(action_generator.game_state):
            return (ActionType.SELECT_DICE, )

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

        # death swap handling
        if game_state.death_swapping(pid):
            assert player_choice is ActionType.SWAP_CHARACTER
            from ...action.action_generator_generator import SwapActGenGenerator
            return just(SwapActGenGenerator.action_generator(game_state, pid))

        # inserted roll phase
        if cls._rolling(action_generator.game_state):
            assert player_choice is ActionType.SELECT_DICE
            from ...action.action_generator_generator import DiceSelectionActGenGenerator
            return just(DiceSelectionActGenGenerator.action_generator(game_state, pid))

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
