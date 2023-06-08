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
    """
    Gives Player2's active character `elem` aura
    """
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
                    1,
                ),
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=elem,
                damage=damage,
            ),
        ))
    ).build()


def _kill_character(game_state: GameState, character_id: int, hp: int = 0) -> GameState:
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


class TestStatus(unittest.TestCase):

    ############################## Vaporize ##############################
    def testVaporize(self):
        """
        Tests that dealing 1 Pyro damage to char with Hydro aura deals 3 damage, vice versa
        """
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
        """
        Tests that dealing 1 Pyro damage to char with Cryo aura deals 3 damage, vice versa
        """
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
        """
        Tests that dealing 1 Electro damage to char with Pyro aura deals 3 damage, and force switch
        to next character, vice versa
        """
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
        """
        Tests that the Overloaded's force switch skips defeated characters and loops back to the
        first character when 'next' the last character
        """
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
        """
        Tests that Overloaded kill doesn't trigger opponent's Deathswap phase
        """
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

    def testOverloadedOffField(self):
        """
        Tests that Overloaded to non-active characters doesn't trigger force switch
        """
        # cause overloaded to an off-field character
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
        """
        Tests that dealing 1 Hydro damage to char with Electro aura deals 2 damage, and 1 Piercing
        damage to off-field characters, vice versa
        """
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
        """
        Tests that dealing 1 Cryo damage to char with Electro aura deals 2 damage, and 1 Piercing
        damage to off-field characters, vice versa
        """
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
        """
        Tests that Swirl swirls all aurable elements except Dendro, damage value is also checked
        """
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
        """
        Tests that Swirl's behaviour when secondary reactions are triggered
        """
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
        """
        Tests that dealing 1 Hydro damage to char with Cryo aura deals 2 damage, and give character
        FrozenStatus, vice versa.
        Tests after the EndRound, FrozenStatus is removed.
        Tests FrozenStatus boosts Physical and Pyro damage correctly (by 2).
        """
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

    ############################## Quicken ##############################
    def testQuicken(self):
        """
        Tests that dealing 1 Electro damage to char with Dendro aura deals 2 damage, and give character
        CatalyzingFieldStatus, vice versa.
        """
        # ELECTRO to DENDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).count,  # type: ignore
            2
        )

        # DENDRO to ELECTRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = _add_damage_effect(game_state, 1, Element.DENDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).count,  # type: ignore
            2
        )

    def testCatalyzingFieldStatus(self):
        """
        Tests that CayalyzingFieldStatus boosts damage.
        Tests that CayalyzingFieldStatus can be consumed to disappering.
        Tests that usages of CayalyzingFieldStatus don't exceed 2.
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_statuses(CatalyzingFieldStatus())
            ).build()
        ).build()
        electro_game_state = _add_damage_effect(base_game_state, 1, Element.ELECTRO)
        dendro_game_state = _add_damage_effect(base_game_state, 1, Element.DENDRO)
        self.assertEqual(
            electro_game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        # deals 1 electro damage with CatalyzingFieldStatus(2)
        electro_game_state = auto_step(electro_game_state)
        ac = electro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().has(Element.ELECTRO))
        self.assertEqual(
            electro_game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).count,  # type: ignore
            1
        )

        # deals 1 dendro damage with CatalyzingFieldStatus(2)
        dendro_game_state = auto_step(dendro_game_state)
        ac = dendro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().has(Element.DENDRO))
        self.assertEqual(
            dendro_game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).count,  # type: ignore
            1
        )

        # deals 1 electro damage with CatalyzingFieldStatus(1)
        game_state = _add_damage_effect(electro_game_state, 1, Element.ELECTRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 6)
        self.assertTrue(ac.get_elemental_aura().has(Element.ELECTRO))
        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(CatalyzingFieldStatus)
        )

        # deals 1 dendro damage with CatalyzingFieldStatus(1) and electro aura
        game_state = _add_damage_effect(electro_game_state, 1, Element.DENDRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).count,  # type: ignore
            2
        )

    ############################## Bloom ##############################
    def testBloom(self):
        """
        Tests that dealing 1 Hydro damage to char with Dendro aura deals 2 damage, and give character
        CatalyzingFieldStatus, vice versa.
        """
        # HYDRO to DENDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).count,  # type: ignore
            1
        )

        # DENDRO to HYDRO
        game_state = _oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = _add_damage_effect(game_state, 1, Element.DENDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).count,  # type: ignore
            1
        )

    def testDendroCoreStatus(self):
        """
        Tests that DendroCoreStatus boosts damage.
        Tests that DendroCoreStatus can be consumed to disappering.
        Tests that usages of DendroCoreStatus don't exceed 2.
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_statuses(DendroCoreStatus())
            ).build()
        ).build()
        electro_game_state = _add_damage_effect(base_game_state, 1, Element.ELECTRO)
        pyro_game_state = _add_damage_effect(base_game_state, 1, Element.PYRO)
        self.assertEqual(
            electro_game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        # deals 1 electro damage with DendroCoreStatus(2)
        electro_game_state = auto_step(electro_game_state)
        ac = electro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertTrue(ac.get_elemental_aura().has(Element.ELECTRO))
        self.assertFalse(
            electro_game_state.get_player1().get_combat_statuses().contains(DendroCoreStatus)
        )

        # deals 1 pyro damage with DendroCoreStatus(2)
        pyro_game_state = auto_step(pyro_game_state)
        ac = pyro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertTrue(ac.get_elemental_aura().has(Element.PYRO))
        self.assertFalse(
            electro_game_state.get_player1().get_combat_statuses().contains(DendroCoreStatus)
        )

        # deals 1 electro damage with DendroCoreStatus(1)
        game_state = _oppo_aura_elem(base_game_state, elem=Element.DENDRO)
        game_state = _add_damage_effect(game_state, 1, Element.HYDRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).count,  # type: ignore
            2
        )

        # deals 1 electro damage with DendroCoreStatus(2)
        game_state = _add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertTrue(ac.get_elemental_aura().has(Element.ELECTRO))
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).count,  # type: ignore
            1
        )