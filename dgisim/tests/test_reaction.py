import unittest

from dgisim.src.action.action import *
from dgisim.src.agents import *
from dgisim.src.character.enums import CharacterSkill
from dgisim.src.effect.effect import *
from dgisim.src.effect.enums import DynamicCharacterTarget
from dgisim.src.effect.structs import DamageType
from dgisim.src.element import ElementalAura
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.state.enums import Pid
from dgisim.src.state.game_state import GameState
from dgisim.src.status.status import *
from dgisim.src.summon.summon import *
from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.tests.helpers.dummy_objects import *


class TestStatus(unittest.TestCase):

    ############################## Vaporize ##############################
    def test_vaporize(self):
        """
        Tests that dealing 1 Pyro damage to char with Hydro aura deals 3 damage, vice versa
        """
        # PYRO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

        # HYDRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )
        game_state = auto_step(game_state)
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    def test_vaporize_no_dmg(self):
        """
        Tests that 0 damage vaporize reaction has no effect
        """
        # PYRO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.PYRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

        # HYDRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.HYDRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    ############################## Melt ##############################
    def test_melt(self):
        """
        Tests that dealing 1 Pyro damage to char with Cryo aura deals 3 damage, vice versa
        """
        # PYRO to CRYO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

        # CRYO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.CRYO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertFalse(ac.get_elemental_aura().elem_auras())

    def test_melt_no_dmg(self):
        """
        Tests that 0 damage melt reaction has no effect
        """
        # PYRO to CRYO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.PYRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

        # CRYO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.CRYO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    ############################## Overloaded ##############################
    def test_overloaded_basics(self):
        """
        Tests that dealing 1 Electro damage to char with Pyro aura deals 3 damage, and force switch
        to next character, vice versa
        """
        # ELECTRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = add_damage_effect(game_state, 1, Element.PYRO)
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

    def test_overloaded_advanced(self):
        """
        Tests that the Overloaded's force switch skips defeated characters and loops back to the
        first character when 'next' the last character
        """
        # start from character 1, kill character 2
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = kill_character(game_state, 2)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = kill_character(game_state, 2)
        game_state = kill_character(game_state, 3)
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
        game_state = oppo_aura_elem(game_state, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
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

    def test_overloaded_death_priority(self):
        """
        Tests that Overloaded kill doesn't trigger opponent's Deathswap phase
        """
        # kill character 1 with overloaded doesn't trigger death swap
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
        game_state = kill_character(game_state, 1, hp=2)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 10, Element.PYRO)
        game_state = kill_character(game_state, 1, hp=2)
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

    def test_overloaded_off_field(self):
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
                        pid=Pid.P1,
                        zone=Zone.CHARACTERS,
                        id=1,
                    ),
                    target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                    element=Element.ELECTRO,
                    damage=1,
                    damage_type=DamageType(),
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

    def test_same_skill_overload_to_just_kill_character_causes_death_swap(self):
        """
        Test that Keqing's burst to *(10)(Pyro) (3) (?) overloads to the second character
        though just killed by the burst.

        (This one feels like a bug in the actual Genius Invokation game, but it does happen.
                                                                              ---- 1/8/2023)
        """
        base_game = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        base_game = kill_character(base_game, character_id=2, hp=1)
        base_game = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(
                    3
                ).f_active_character(
                    lambda ac: ac.factory().energy(ac.get_max_energy()).build()
                ).build()
            ).build()
        ).build()
        assert isinstance(base_game.get_player1().just_get_active_character(), Keqing)
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 4}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_id(), 2)

    def test_overload_no_dmg(self):
        """
        Test that overload with no damage still force swap to next character.
        """
        # ELECTRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.ELECTRO,
            ).execute(game_state)
        )
        p2_cs = game_state.get_player2().get_characters()
        self.assertEqual(p2_cs.just_get_character(1).get_hp(), 10)
        self.assertFalse(p2_cs.just_get_character(1).get_elemental_aura().has_aura())
        self.assertEqual(p2_cs.get_active_character_id(), 2)

        # PYRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.PYRO,
            ).execute(game_state)
        )
        p2_cs = game_state.get_player2().get_characters()
        self.assertEqual(p2_cs.just_get_character(1).get_hp(), 10)
        self.assertFalse(p2_cs.just_get_character(1).get_elemental_aura().has_aura())
        self.assertEqual(p2_cs.get_active_character_id(), 2)

    def test_overload_no_dmg_to_off_field(self):
        """
        Test that overload to off field with no damage doesn't force swap to next character.
        """
        # ELECTRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO, char_id=2)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 2),
                element=Element.ELECTRO,
            ).execute(game_state)
        )
        p2_cs = game_state.get_player2().get_characters()
        self.assertEqual(p2_cs.just_get_character(2).get_hp(), 10)
        self.assertFalse(p2_cs.just_get_character(2).get_elemental_aura().has_aura())
        self.assertEqual(p2_cs.get_active_character_id(), 1)

        # PYRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO, char_id=2)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 2),
                element=Element.PYRO,
            ).execute(game_state)
        )
        p2_cs = game_state.get_player2().get_characters()
        self.assertEqual(p2_cs.just_get_character(2).get_hp(), 10)
        self.assertFalse(p2_cs.just_get_character(2).get_elemental_aura().has_aura())
        self.assertEqual(p2_cs.get_active_character_id(), 1)

    ############################## ElectroCharged ##############################
    def test_electro_charged(self):
        """
        Tests that dealing 1 Hydro damage to char with Electro aura deals 2 damage, and 1 Piercing
        damage to off-field characters, vice versa
        """
        # HYDRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = add_damage_effect(game_state, 1, Element.HYDRO)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
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

    def test_electro_charged_no_dmg(self):
        """
        Tests that 0 damage electro charged reaction has no effect
        """
        # HYDRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.HYDRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

        # ELECTRO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.ELECTRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    ############################## SuperConduct ##############################
    def test_super_conduct(self):
        """
        Tests that dealing 1 Cryo damage to char with Electro aura deals 2 damage, and 1 Piercing
        damage to off-field characters, vice versa
        """
        # CRYO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = add_damage_effect(game_state, 1, Element.CRYO)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
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

    def test_super_conduct_no_dmg(self):
        """
        Tests that 0 damage super conduct reaction has no effect
        """
        # CRYO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.CRYO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

        # ELECTRO to CRYO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.ELECTRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    ############################## Swirl ##############################
    def test_swirl(self):
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
            game_state = oppo_aura_elem(ACTION_TEMPLATE, aura_elem)
            game_state = add_damage_effect(game_state, 1, Element.ANEMO)

            game_state = auto_step(game_state)
            chars = game_state.get_player2().get_characters()
            self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
            self.assertEqual(chars.just_get_character(1).get_hp(), 9)
            self.assertTrue(chars.just_get_character(2).get_elemental_aura().contains(aura_elem))
            self.assertEqual(chars.just_get_character(2).get_hp(), 9)
            self.assertTrue(chars.just_get_character(3).get_elemental_aura().contains(aura_elem))
            self.assertEqual(chars.just_get_character(3).get_hp(), 9)

        aura_elem = Element.DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, aura_elem)
        game_state = add_damage_effect(game_state, 1, Element.ANEMO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertTrue(chars.just_get_character(1).get_elemental_aura().contains(aura_elem))
        self.assertEqual(chars.just_get_character(1).get_hp(), 9)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 10)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 10)

    @staticmethod
    def swirl_elem1_to_elem2(elem1: Element, elem2: Element) -> GameState:
        game_state = oppo_aura_elem(ACTION_TEMPLATE, elem1)
        game_state = add_damage_effect(game_state, 1, Element.ANEMO)
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

    def test_swirled_reaction(self):
        """
        Tests that Swirl's behaviour when secondary reactions are triggered
        """
        # Superconduct
        game_state = self.swirl_elem1_to_elem2(Element.ELECTRO, Element.CRYO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(1).get_hp(), 7)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 7)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 7)

        # Overloaded
        game_state = self.swirl_elem1_to_elem2(Element.ELECTRO, Element.PYRO)

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
        game_state = self.swirl_elem1_to_elem2(Element.CRYO, Element.PYRO)

        game_state = auto_step(game_state)
        chars = game_state.get_player2().get_characters()
        self.assertFalse(chars.just_get_character(1).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(1).get_hp(), 9)
        self.assertFalse(chars.just_get_character(2).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(2).get_hp(), 7)
        self.assertFalse(chars.just_get_character(3).get_elemental_aura().elem_auras())
        self.assertEqual(chars.just_get_character(3).get_hp(), 7)

    def test_swirl_no_dmg(self):
        """
        NOTE that in the actual game, this is undefined behaviour.

        Tests that 0 damage swirl reaction has no effect
        """
        # ANEMO to all aurable elements
        aurable_elems = (Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO, Element.DENDRO)
        for elem in aurable_elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(ACTION_TEMPLATE, elem)
                game_state = auto_step(
                    ApplyElementalAuraEffect(
                        target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                        element=Element.ANEMO,
                    ).execute(game_state)
                )
                p2ac = game_state.get_player2().just_get_active_character()
                self.assertEqual(p2ac.get_hp(), 10)
                if elem is not Element.DENDRO:
                    self.assertFalse(p2ac.get_elemental_aura().has_aura())
                else:
                    self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())

    ############################## Frozen ##############################
    def test_frozen(self):
        """
        Tests that dealing 1 Hydro damage to char with Cryo aura deals 2 damage, and give character
        FrozenStatus, vice versa.
        Tests after the EndRound, FrozenStatus is removed.
        Tests FrozenStatus boosts Physical and Pyro damage correctly (by 2).
        """
        # HYDRO to CRYO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = add_damage_effect(game_state, 1, Element.HYDRO)
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
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.CRYO)
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
        game_state = add_damage_effect(frozen_game_state, 1, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_character_statuses().contains(FrozenStatus))

        # boost physical damage
        game_state = add_damage_effect(frozen_game_state, 1, Element.PYRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_character_statuses().contains(FrozenStatus))

    def test_frozen_no_dmg(self):
        """
        Tests that frozen without damage still applies frozen status
        """
        # HYDRO to CRYO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.CRYO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.HYDRO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(FrozenStatus, p2ac.get_character_statuses())

        # CRYO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.CRYO,
            ).execute(game_state)
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(FrozenStatus, p2ac.get_character_statuses())

    ############################## Quicken ##############################
    def test_quicken(self):
        """
        Tests that dealing 1 Electro damage to char with Dendro aura deals 2 damage, and give character
        CatalyzingFieldStatus, vice versa.
        """
        # ELECTRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = add_damage_effect(game_state, 1, Element.ELECTRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).usages,
            2
        )

        # DENDRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = add_damage_effect(game_state, 1, Element.DENDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).usages,
            2
        )

    def test_quicken_no_dmg(self):
        """
        Tests that quicken without damage still generates catalyzing field status to the opponent
        """
        # ELECTRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.ELECTRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(CatalyzingFieldStatus, p1.get_combat_statuses())

        # DENDRO to ELECTRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.ELECTRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.DENDRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(CatalyzingFieldStatus, p1.get_combat_statuses())

    def test_catalyzing_field_status(self):
        """
        Tests that CatalyzingFieldStatus boosts damage.
        Tests that CatalyzingFieldStatus can be consumed to disappering.
        Tests that usages of CatalyzingFieldStatus don't exceed 2.
        Tests that CatalyzingFieldStatus doesn't boost DMG to inactive character
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(CatalyzingFieldStatus())
            ).build()
        ).build()
        electro_game_state = add_damage_effect(base_game_state, 1, Element.ELECTRO)
        dendro_game_state = add_damage_effect(base_game_state, 1, Element.DENDRO)
        self.assertEqual(
            electro_game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        # deals 1 electro damage with CatalyzingFieldStatus(2)
        electro_game_state = auto_step(electro_game_state)
        ac = electro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertEqual(
            electro_game_state.get_player1().get_combat_statuses().just_find(
                CatalyzingFieldStatus
            ).usages,
            1
        )

        # deals 1 dendro damage with CatalyzingFieldStatus(2)
        dendro_game_state = auto_step(dendro_game_state)
        ac = dendro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().contains(Element.DENDRO))
        self.assertEqual(
            dendro_game_state.get_player1().get_combat_statuses().just_find(
                CatalyzingFieldStatus
            ).usages,
            1
        )

        # deals 1 electro damage with CatalyzingFieldStatus(1)
        game_state = add_damage_effect(electro_game_state, 1, Element.ELECTRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 6)
        self.assertTrue(ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(CatalyzingFieldStatus)
        )

        # deals 1 dendro damage with CatalyzingFieldStatus(1) and electro aura
        game_state = add_damage_effect(electro_game_state, 1, Element.DENDRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 5)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CatalyzingFieldStatus).usages,
            2
        )

        # deals 1 electro damage to off-field characters
        game_state = base_game_state.factory().f_effect_stack(
            lambda es: es.push_one(ReferredDamageEffect(
                source=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.ELECTRO,
                damage=1,
                damage_type=DamageType(),
            ))
        ).build()
        oc = game_state.get_player2().get_characters().just_get_character(3)
        self.assertEqual(oc.get_hp(), 10)
        game_state = auto_step(game_state)
        oc = game_state.get_player2().get_characters().just_get_character(3)
        self.assertEqual(oc.get_hp(), 9)

    ############################## Bloom ##############################
    def test_bloom(self):
        """
        Tests that dealing 1 Hydro damage to char with Dendro aura deals 2 damage, and give character
        CatalyzingFieldStatus, vice versa.
        """
        # HYDRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = add_damage_effect(game_state, 1, Element.HYDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).usages,
            1
        )

        # DENDRO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.DENDRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).usages,
            1
        )

    def test_bloom_no_dmg(self):
        """
        Tests that bloom without damage still generates dendro core status to the opponent
        """
        # HYDRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.HYDRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(DendroCoreStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(DendroCoreStatus).usages, 1)

        # DENDRO to HYDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.HYDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.DENDRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(DendroCoreStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(DendroCoreStatus).usages, 1)

    def test_dendro_core_status(self):
        """
        Tests that DendroCoreStatus boosts damage.
        Tests that DendroCoreStatus can be consumed to disappering.
        Tests that usages of DendroCoreStatus don't exceed 2.
        Tests that DendroCoreStatus doesn't boost DMG to inactive character
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(DendroCoreStatus())
            ).build()
        ).build()
        electro_game_state = add_damage_effect(base_game_state, 1, Element.ELECTRO)
        pyro_game_state = add_damage_effect(base_game_state, 1, Element.PYRO)
        self.assertEqual(
            electro_game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        # deals 1 electro damage with DendroCoreStatus(2)
        electro_game_state = auto_step(electro_game_state)
        ac = electro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertTrue(ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(
            electro_game_state.get_player1().get_combat_statuses().contains(DendroCoreStatus)
        )

        # deals 1 pyro damage with DendroCoreStatus(2)
        pyro_game_state = auto_step(pyro_game_state)
        ac = pyro_game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 7)
        self.assertTrue(ac.get_elemental_aura().contains(Element.PYRO))
        self.assertFalse(
            electro_game_state.get_player1().get_combat_statuses().contains(DendroCoreStatus)
        )

        # bloom with DendroCoreStatus(1)
        game_state = oppo_aura_elem(base_game_state, elem=Element.DENDRO)
        game_state = add_damage_effect(game_state, 1, Element.HYDRO)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(DendroCoreStatus).usages,
            1
        )

        # deals 1 electro damage to off-field characters
        game_state = base_game_state.factory().f_effect_stack(
            lambda es: es.push_one(ReferredDamageEffect(
                source=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.ELECTRO,
                damage=1,
                damage_type=DamageType(),
            ))
        ).build()
        oc = game_state.get_player2().get_characters().just_get_character(3)
        self.assertEqual(oc.get_hp(), 10)
        game_state = auto_step(game_state)
        oc = game_state.get_player2().get_characters().just_get_character(3)
        self.assertEqual(oc.get_hp(), 9)

    ############################## Crystallize ##############################
    def test_crystallize(self):
        """
        Tests that dealing 1 Geo damage to char with Pyro aura deals 2 damage, and give character
        CrystallizeStatus
        """
        # GEO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = add_damage_effect(game_state, 1, Element.GEO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CrystallizeStatus).usages,
            1
        )

        # GEO to HYDRO (with CrystallizeStatus{1})
        game_state = oppo_aura_elem(game_state, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.GEO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 6)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CrystallizeStatus).usages,
            2
        )

        # GEO to HYDRO (with CrystallizeStatus{2})
        game_state = oppo_aura_elem(game_state, Element.HYDRO)
        game_state = add_damage_effect(game_state, 1, Element.GEO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 4)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state.get_player1().get_combat_statuses().just_find(CrystallizeStatus).usages,
            2
        )

    def test_crystallize_no_dmg(self):
        """
        NOTE that in the actual game, this is undefined behaviour.

        Tests that 0 damage crystallize reaction has no effect
        """
        # GEO to all aurable elements
        aurable_elems = (Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO, Element.DENDRO)
        for elem in aurable_elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(ACTION_TEMPLATE, elem)
                game_state = auto_step(
                    ApplyElementalAuraEffect(
                        target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                        element=Element.GEO,
                    ).execute(game_state)
                )
                p1 = game_state.get_player1()
                p2ac = game_state.get_player2().just_get_active_character()
                self.assertEqual(p2ac.get_hp(), 10)
                if elem is not Element.DENDRO:
                    self.assertFalse(p2ac.get_elemental_aura().has_aura())
                    self.assertIn(CrystallizeStatus, p1.get_combat_statuses())
                    self.assertEqual(p1.get_combat_statuses().just_find(
                        CrystallizeStatus).usages,
                        1
                    )
                else:
                    self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
                    self.assertNotIn(CrystallizeStatus, p1.get_combat_statuses())

    def test_crystallize_status(self):
        """
        tests that CrystallizeStatus does take dmg for characters
        """
        base_game_state_1 = ACTION_TEMPLATE.factory().f_player2(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(CrystallizeStatus(usages=1))
            ).build()
        ).build()
        base_game_state_2 = ACTION_TEMPLATE.factory().f_player2(
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(CrystallizeStatus(usages=2))
            ).build()
        ).build()

        # 0 dmg test
        game_state = add_damage_effect(base_game_state_1, 0, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(
            game_state.get_player2().get_combat_statuses().just_find(CrystallizeStatus).usages,
            1
        )

        # 1 dmg test
        game_state = add_damage_effect(base_game_state_1, 1, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 10)
        self.assertFalse(game_state.get_player2().get_combat_statuses().contains(CrystallizeStatus))

        game_state = add_damage_effect(base_game_state_2, 1, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 10)
        self.assertEqual(
            game_state.get_player2().get_combat_statuses().just_find(CrystallizeStatus).usages,
            1
        )

        # 2 dmg test
        game_state = add_damage_effect(base_game_state_1, 2, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 9)
        self.assertFalse(game_state.get_player2().get_combat_statuses().contains(CrystallizeStatus))

        game_state = add_damage_effect(base_game_state_2, 2, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 10)
        self.assertFalse(game_state.get_player2().get_combat_statuses().contains(CrystallizeStatus))

        # 3 dmg test
        game_state = add_damage_effect(base_game_state_1, 3, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(game_state.get_player2().get_combat_statuses().contains(CrystallizeStatus))

        game_state = add_damage_effect(base_game_state_2, 3, Element.CRYO)

        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        self.assertTrue(ac.get_elemental_aura().contains(Element.CRYO))
        self.assertEqual(ac.get_hp(), 9)
        self.assertFalse(game_state.get_player2().get_combat_statuses().contains(CrystallizeStatus))

    ############################## Burning ##############################
    def test_burning(self):
        """
        Tests that dealing 1 Pyro damage to char with Dendro aura deals 2 damage, and adds Burning to
        Summons, vice versa
        """
        # PYRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = add_damage_effect(game_state, 1, Element.PYRO)
        self.assertEqual(
            game_state.get_player2().just_get_active_character().get_hp(),
            10,
        )

        game_state_1 = auto_step(game_state)
        ac = game_state_1.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state_1.get_player1().get_summons().just_find(BurningFlameSummon).usages,
            1
        )

        # DENDRO to PYRO with BurningFieldSummon(1) already
        game_state_2 = oppo_aura_elem(game_state_1, Element.PYRO)
        game_state_2 = add_damage_effect(game_state_2, 1, Element.DENDRO)

        game_state_2 = auto_step(game_state_2)
        ac = game_state_2.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 6)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state_2.get_player1().get_summons().just_find(BurningFlameSummon).usages,
            2
        )

        # DENDRO to PYRO with BurningFieldSummon(2) already, usages should stay at 2
        game_state_3 = oppo_aura_elem(game_state_2, Element.PYRO)
        game_state_3 = add_damage_effect(game_state_3, 1, Element.DENDRO)

        game_state_3 = auto_step(game_state_3)
        ac = game_state_3.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 4)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        self.assertEqual(
            game_state_3.get_player1().get_summons().just_find(BurningFlameSummon).usages,
            2
        )

    def test_burning_no_dmg(self):
        """
        Tests that burning without damage still adds Burning Flame summon to opponent
        """
        # PYRO to DENDRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.DENDRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.PYRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(BurningFlameSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BurningFlameSummon).usages, 1)

        # DENDRO to PYRO
        game_state = oppo_aura_elem(ACTION_TEMPLATE, Element.PYRO)
        game_state = auto_step(
            ApplyElementalAuraEffect(
                target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
                element=Element.DENDRO,
            ).execute(game_state)
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(BurningFlameSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BurningFlameSummon).usages, 1)

    def test_burning_flame_summon(self):
        """
        Tests that burning attacks when at end round normally
        """
        base_game_state_1 = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(BurningFlameSummon(usages=1))
            ).build()
        ).build()
        base_game_state_2 = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(BurningFlameSummon(usages=2))
            ).build()
        ).build()

        # test BurningFlameSummon(1)
        game_state = auto_step(base_game_state_1)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 9)
        self.assertTrue(ac.get_elemental_aura().contains(Element.PYRO))
        self.assertFalse(game_state.get_player1().get_summons().contains(BurningFlameSummon))

        # test BurningFlameSummon(2)
        game_state = auto_step(base_game_state_2)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 9)
        self.assertTrue(ac.get_elemental_aura().contains(Element.PYRO))
        self.assertEqual(
            game_state.get_player1().get_summons().just_find(BurningFlameSummon).usages,
            1
        )

    def test_burning_flame_summon_triggering_burning(self):
        """
        tests the behaviour when the burning attack triggers reaction Burning
        """
        base_game_state_1 = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(BurningFlameSummon(usages=1)
                                            ).update_summon(TestSummon())
            ).build()
        ).f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(Element.DENDRO)
                    ).build()
                ).build()
            ).build()
        ).build()
        base_game_state_2 = base_game_state_1.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(BurningFlameSummon(usages=2)
                                            ).update_summon(TestSummon())
            ).build()
        ).build()

        # test BurningFlameSummon(1), position shouldn't change, usages should be 1
        game_state = auto_step(base_game_state_1)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        summons = list(game_state.get_player1().get_summons())
        self.assertEqual(summons[0], BurningFlameSummon(usages=1))
        self.assertEqual(summons[1], TestSummon())

        # test BurningFlameSummon(2), position shouldn't change, usages should be 1
        game_state = auto_step(base_game_state_2)
        ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(ac.get_hp(), 8)
        self.assertFalse(ac.get_elemental_aura().elem_auras())
        summons = list(game_state.get_player1().get_summons())
        self.assertEqual(summons[0], BurningFlameSummon(usages=1))
        self.assertEqual(summons[1], TestSummon())
