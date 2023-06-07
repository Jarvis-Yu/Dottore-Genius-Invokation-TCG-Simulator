import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import auto_step
from dgisim.src.state.game_state import GameState
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.agents import *
from dgisim.src.element.element import Reaction, ElementalAura
from dgisim.src.effect.effect import *
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.status.status import *
from dgisim.src.action import *


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
                damage=damage,
            ),
        ))
    ).build()


def _kill_character(game_state: GameState, character_id: int, hp: int = 0) -> GameState:
    return game_state.factory().f_player2(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                character_id,
                lambda c: c.factory().hp(hp).build()
            ).build()
        ).build()
    ).build()


class TestStatus(unittest.TestCase):

    ############################## Vaporize ##############################
    def testVaporize(self):
        # PYRO to HYDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )
        game_state = auto_step(game_state)
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
        game_state = auto_step(game_state)
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    ############################## Melt ##############################
    def testMelt(self):
        # PYRO to CRYO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = _add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    ############################## Overloaded ##############################
    def testOverloadedBasics(self):
        # ELECTRO to PYRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(ac.get_id(), 1)

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
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

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertTrue(chars.just_get_character(1).defeated())
        self.assertEqual(
            chars.get_active_character_id(),
            2,
        )
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertTrue(game_state.get_effect_stack().is_empty())

        # kill character 1 with no reaction causes death swap effect
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = _add_damage_effect(game_state, 10, Element.PYRO)
        game_state = _kill_character(game_state, 1, hp=2)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 2)
        self.assertEqual(ac.get_id(), 1)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertTrue(chars.just_get_character(1).defeated())
        self.assertEqual(
            chars.get_active_character_id(),
            1,
        )
        self.assertTrue(game_state.get_effect_stack().is_not_empty())

    def testOverloadOffField(self):
        # cause overloaded to an offfield character
        aura_char_id = 2
        game_state = ACTION_TEMPLATE.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    aura_char_id,
                    lambda c: c.factory().elemental_aura(
                        ElementalAura.from_default().add(Element.PYRO)
                    ).build()
                ).build()
            ).build()
        ).f_effect_stack(
            lambda es: es.push_one(
                ReferredDamageEffect(
                    source=StaticTarget(
                        pid=GameState.Pid.P1,
                        zone=Zone.CHARACTER,
                        id=1,
                    ),
                    target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                    element=Element.ELECTRO,
                    damage=1,
                )
            )
        ).build()

        # checks execution
        p2_active_id = game_state.get_player2().just_get_active_character().get_id() != aura_char_id
        p2_c2 = game_state.get_player2().get_characters().just_get_character(2)
        self.assertEqual(p2_active_id, 1)
        self.assertEqual(p2_c2.get_hp(), 10)

        game_state = auto_step(game_state)
        p2_active_id = game_state.get_player2().just_get_active_character().get_id() != aura_char_id
        self.assertEqual(p2_active_id, 1)
        p2_c2 = game_state.get_player2().get_characters().just_get_character(2)
        self.assertEqual(p2_c2.get_hp(), 7)

    ############################## ElectroCharged ##############################
    def testElectroCharged(self):
        # HYDRO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

        # ELECTRO to HYDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

    ############################## SuperConduct ##############################
    def testSuperConduct(self):
        # CRYO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.CRYO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

        # ELECTRO to CRYO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(chars.just_get_character(1).get_hp(), 8)
        self.assertEqual(chars.just_get_character(2).get_hp(), 9)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
        self.assertFalse(chars.just_get_active_character().get_elemental_aura().elem_auras())

    ############################## Swirl ##############################
    def testSwirl(self):
        elems = [
            Element.PYRO,
            Element.HYDRO,
            Element.ELECTRO,
            Element.CRYO,
        ]
        for aura_elem in elems:
            game_state = _oppo_aura_elem(ACTION_TEMPLATE, aura_elem)
            game_state = _add_damage_effect(game_state, 1, Element.ANEMO)

            game_state = auto_step(game_state)
            chars = game_state.get_player2().get_characters()
            self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
            self.assertEqual(chars.just_get_character(1).get_hp(), 9)
            self.assertTrue(chars.just_get_character(2).get_elemental_aura().has(aura_elem))
            self.assertEqual(chars.just_get_character(2).get_hp(), 9)
            self.assertTrue(chars.just_get_character(3).get_elemental_aura().has(aura_elem))
            self.assertEqual(chars.just_get_character(3).get_hp(), 9)

        aura_elem = Element.DENDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, aura_elem)
        game_state = _add_damage_effect(game_state, 1, Element.ANEMO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertTrue(chars.just_get_character(1).get_elemental_aura().has(aura_elem))
        self.assertEqual(chars.just_get_character(1).get_hp(), 9)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 10)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 10)

    @staticmethod
    def swirlElem1ToElem2(elem1: Element, elem2: Element) -> GameState:
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, elem1)
        game_state = _add_damage_effect(game_state, 1, Element.ANEMO)
        game_state = game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().elemental_aura(
                        ElementalAura.from_default().add(elem2)
                    ).build()
                ).f_character(
                    3,
                    lambda c: c.factory().elemental_aura(
                        ElementalAura.from_default().add(elem2)
                    ).build()
                ).build()
            ).build()
        ).build()
        return game_state

    def testSwirledReaction(self):
        # Superconduct
        game_state = self.swirlElem1ToElem2(Element.ELECTRO, Element.CRYO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(1).get_hp(), 7)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 7)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 7)

        # Overloaded
        game_state = self.swirlElem1ToElem2(Element.ELECTRO, Element.PYRO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertEqual(just(chars.get_active_character_id()), 1)
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(1).get_hp(), 9)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 7)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 7)

        # Melt
        game_state = self.swirlElem1ToElem2(Element.CRYO, Element.PYRO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(1).get_hp(), 9)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 7)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 7)

    ############################## Frozen ##############################
    def testFrozen(self):
        # HYDRO to CRYO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertTrue(ac.get_character_statuses().contains(FrozenStatus))

        # CRYO to HYDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.CRYO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        frozen_game_state = auto_step(game_state)
        ac = frozen_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertTrue(ac.get_character_statuses().contains(FrozenStatus))

        # defrost after round end
        p1, p2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(frozen_game_state, p1, p2)
        p1.inject_action(EndRoundAction())
        p2.inject_action(EndRoundAction())
        gsm.step_until_phase(frozen_game_state.get_mode().end_phase())
        gsm.step_until_next_phase()
        ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertFalse(ac.get_character_statuses().contains(FrozenStatus))

        # boost physical damage
        game_state = _add_damage_effect(frozen_game_state, 1, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_character_statuses().contains(FrozenStatus))

        # boost physical damage
        game_state = _add_damage_effect(frozen_game_state, 1, Element.PYRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_character_statuses().contains(FrozenStatus))
