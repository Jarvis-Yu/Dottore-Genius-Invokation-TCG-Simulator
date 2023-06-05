import unittest

from dgisim.tests.game_state_templates import *
from dgisim.src.state.game_state import GameState
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.agents import *
from dgisim.src.element.element import Reaction, ElementalAura
from dgisim.src.effect.effect import *
from dgisim.src.helper.level_print import GamePrinter


def _oppo_aura_elem(game_state: GameState, elem: Element) -> GameState:
    return game_state.factory().f_player2(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_active_character(
                lambda ac: ac.factory().elemental_aura(
                    ElementalAura.from_default().add(elem)
                ).build()
            ).build()
        ).build()
    ).build()


def _add_damage_effect(game_state: GameState, damage: int, elem: Element) -> GameState:
    return game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            ReferredDamageEffect(
                source=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTER,
                    1,
                ),
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=elem,
                damage=1,
            ),
        ))
    ).build()


def _kill_character(game_state: GameState, character_id: int, hp: int=0) -> GameState:
    return game_state.factory().f_player2(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                character_id,
                lambda c: c.factory().hp(hp).build()
            ).build()
        ).build()
    ).build()


def _auto_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(">>> ")
    return gsm.get_game_state()


class TestStatus(unittest.TestCase):
    def testVaporize(self):
        # PYRO to HYDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )
        game_state = _auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

        # HYDRO to PYRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )
        game_state = _auto_step(game_state)
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    def testMelt(self):
        # PYRO to CRYO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = _add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

        # CRYO to PYRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.CRYO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    def testOverloadedBasics(self):
        # ELECTRO to PYRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 1)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(
            chars.just_get_character(1).get_hp(),
            7,
        )
        self.assertEqual(
            chars.get_active_character_id(),
            2,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())

        # PYRO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.PYRO)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 1)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(
            chars.just_get_character(1).get_hp(),
            7,
        )
        self.assertEqual(
            chars.get_active_character_id(),
            2,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())

    def testOverloadedAdvanced(self):
        # start from character 1, kill character 2
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = _kill_character(game_state, 2)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 1)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(
            chars.just_get_character(1).get_hp(),
            7,
        )
        self.assertEqual(
            chars.get_active_character_id(),
            3,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())

        # start from character 1, kill character 2, 3
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = _kill_character(game_state, 2)
        game_state = _kill_character(game_state, 3)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 1)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(
            chars.just_get_character(1).get_hp(),
            7,
        )
        self.assertEqual(
            chars.get_active_character_id(),
            1,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())

        # start from character 3
        game_state = ACTION_TEMPLATE.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(3).build()
            ).build()
        ).build()
        game_state = _oppo_aura_elem(game_state, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 3)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(
            chars.just_get_character(3).get_hp(),
            7,
        )
        self.assertEqual(
            chars.get_active_character_id(),
            1,
        )
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())

    def testOverloadedDeathPriority(self):
        # kill character 1 with overloaded doesn't trigger death swap
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = _kill_character(game_state, 1, hp=2)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 2)
        self.assertEqual(ac.get_id(), 1)

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertTrue(chars.just_get_character(1).defeated())
        self.assertEqual(
            chars.get_active_character_id(),
            2,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertTrue(game_state.get_effect_stack().is_empty())

    def testElectroCharged(self):
        # HYDRO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

        # HYDRO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

    def testSuperConduct(self):
        # CRYO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.CRYO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

        # CRYO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = _auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())
