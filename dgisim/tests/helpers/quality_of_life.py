from __future__ import annotations

from dgisim.src.agents import *
from dgisim.src.dices import ActualDices
from dgisim.src.effect.effect import *
from dgisim.src.effect.enums import DynamicCharacterTarget, Zone
from dgisim.src.effect.structs import DamageType, StaticTarget
from dgisim.src.element import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.helper.quality_of_life import *
from dgisim.src.state.enums import Pid
from dgisim.src.state.game_state import GameState


def auto_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:  # pragma: no cover
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(":> ")
    return gsm.get_game_state()

def full_action_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    gsm.player_step(observe=observe)
    gsm.auto_step(observe=observe)
    return gsm.get_game_state()


def oppo_aura_elem(game_state: GameState, elem: Element, char_id: None | int = None) -> GameState:
    """
    Gives Player2's active character `elem` aura
    """
    if char_id is None:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()
    else:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    char_id,  # type: ignore
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()

def remove_aura(game_state: GameState, pid: Pid = Pid.P2, char_id: None | int = None) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                case_val(char_id is None, cs.just_get_active_character_id(), char_id),  # type: ignore
                lambda c: c.factory().elemental_aura(ElementalAura.from_default()).build()
            ).build()
        ).build()
    ).build()

def add_damage_effect(
        game_state: GameState,
        damage: int,
        elem: Element,
        pid: Pid = Pid.P2,
        char_id: None | int = None,
        damage_type: None | DamageType = None,
) -> GameState:
    """
    Adds ReferredDamageEffect to Player2's active character with `damage` and `elem` from Player1's
    active character (id=1)
    """
    return game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            ReferredDamageEffect(
                source=StaticTarget(
                    pid.other(),
                    Zone.CHARACTERS,
                    case_val(char_id is None, 1, char_id),  # type: ignore
                ),
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=elem,
                damage=damage,
                damage_type=case_val(damage_type is None, DamageType(), damage_type),  # type: ignore
            ),
            AliveMarkCheckerEffect(),
            DeathCheckCheckerEffect(),
        ))
    ).build()


def kill_character(
        game_state: GameState,
        character_id: int,
        pid: Pid = Pid.P2,
        hp: int = 0,
) -> GameState:
    """
    Sets Player2's active character's hp to `hp` (default=0)
    """
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                character_id,
                lambda c: c.factory().hp(hp).alive(hp > 0).build()
            ).build()
        ).build()
    ).build()


def set_active_player_id(game_state: GameState, pid: Pid, character_id: int) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(character_id).build()
        ).build()
    ).build()

def fill_dices_with_omni(game_state: GameState) -> GameState:
    return game_state.factory().f_player1(
        lambda p: p.factory().dices(ActualDices({Element.OMNI: BIG_INT})).build()
    ).f_player2(
        lambda p: p.factory().dices(ActualDices({Element.OMNI: BIG_INT})).build()
    ).build()
