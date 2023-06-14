from dgisim.src.state.game_state import GameState
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.element.element import *
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.helper.quality_of_life import *
from dgisim.src.agents import *

def auto_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:  # pragma: no cover
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(">>> ")
    return gsm.get_game_state()

def oppo_aura_elem(game_state: GameState, elem: Element, char_id: Optional[int] = None) -> GameState:
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
                    char_id,
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()


def add_damage_effect(
        game_state: GameState,
        damage: int,
        elem: Element,
        char_id: Optional[int] = None,
) -> GameState:
    """
    Adds ReferredDamageEffect to Player2's active character with `damage` and `elem` from Player1's
    active character (id=1)
    """
    return game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            ReferredDamageEffect(
                source=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTER,
                    case_val(char_id is None, 1, char_id),  # type: ignore
                ),
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=elem,
                damage=damage,
                damage_type=DamageType(),
            ),
            DeathCheckCheckerEffect(),
        ))
    ).build()


def kill_character(game_state: GameState, character_id: int, hp: int = 0) -> GameState:
    """
    Sets Player2's active character's hp to `hp` (default=0)
    """
    return game_state.factory().f_player2(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                character_id,
                lambda c: c.factory().hp(hp).build()
            ).build()
        ).build()
    ).build()