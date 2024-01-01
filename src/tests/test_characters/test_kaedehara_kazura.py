import unittest
from typing import ClassVar

from src.tests.test_characters.common_imports import *


class TestKaedeharaKazuha(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                KaedeharaKazuha.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(PoeticsOfFuubutsu)
        ).dice(
            ActualDice({Element.OMNI: 100})  # even number
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(
            Act.END_PHASE
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is KaedeharaKazuha

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.elem_auras())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        elems = [None, Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                if elem is None:
                    game_state = base_game
                else:
                    game_state = oppo_aura_elem(base_game, elem)

                gsm = GameStateMachine(game_state, a1, a2)
                a1.inject_action(SkillAction(
                    skill=CharacterSkill.SKILL2,
                    instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                ))
                p2ac = gsm.get_game_state().player2.just_get_active_character()
                self.assertEqual(p2ac.hp, 10)

                # first skill
                gsm.player_step()
                gsm.auto_step()
                p2cs = gsm.get_game_state().player2.characters
                p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
                self.assertEqual(p2c1.hp, 7)
                self.assertFalse(p2c1.elemental_aura.has_aura())
                if elem is not None:
                    self.assertEqual(p2c2.hp, 9)
                    self.assertEqual(p2c3.hp, 9)
                    self.assertTrue(p2c2.elemental_aura.has_aura())
                    self.assertTrue(p2c3.elemental_aura.has_aura())
                p1ac = gsm.get_game_state().player1.just_get_active_character()
                self.assertEqual(p1ac.id, 3)

                # swap back and plunge attack
                a1.inject_actions([
                    SwapAction(
                        char_id=2,
                        instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
                    ),
                    SkillAction(
                        skill=CharacterSkill.SKILL1,
                        instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                    ),
                    EndRoundAction(),
                ])
                gsm.step_until_next_phase()
                p2cs = gsm.get_game_state().player2.characters
                p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
                self.assertEqual(p2c1.hp, 4)
                if elem is None:
                    self.assertFalse(p2c1.elemental_aura.has_aura())
                else:
                    self.assertIn(elem, p2c1.elemental_aura)
                if elem is not None:
                    self.assertEqual(p2c2.hp, 9)
                    self.assertEqual(p2c3.hp, 9)
                    self.assertTrue(p2c2.elemental_aura.has_aura())
                    self.assertTrue(p2c3.elemental_aura.has_aura())
                p1ac = gsm.get_game_state().player1.just_get_active_character()
                self.assertEqual(p1ac.id, 2)
                from src.dgisim.status.status import _MIDARE_RANZAN_MAP
                for status in p1ac.character_statuses:
                    self.assertNotIn(type(status), _MIDARE_RANZAN_MAP.values())

    def test_midare_ranzan_status(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda c: c.factory().f_character_statuses(
                        lambda css: css.update_status(MidareRanzanStatus(_protected=False))
                    ).build()
                ).build()
            ).build()
        ).build()
        elems = [Element.ANEMO, Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        # test if using skill when having MidareRanzan behaves correctly
        for elem in elems:
            with self.subTest(elem=elem):
                if elem is Element.ANEMO:
                    game_state = base_game_state
                else:
                    game_state = oppo_aura_elem(base_game_state, elem)
                from src.dgisim.status.status import _MIDARE_RANZAN_MAP
                new_midare_status = _MIDARE_RANZAN_MAP[elem]

                gsm = GameStateMachine(game_state, a1, a2)
                a1.clear()
                a2.clear()
                a1.inject_action(SkillAction(
                    skill=CharacterSkill.SKILL2,
                    instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                ))
                p2ac = gsm.get_game_state().player2.just_get_active_character()
                self.assertEqual(p2ac.hp, 10)

                # first skill
                gsm.player_step()
                gsm.auto_step()
                p1_kazuha = gsm.get_game_state().player1.characters.just_get_character(2)
                p1_kazuha_stts = p1_kazuha.character_statuses
                for midare in _MIDARE_RANZAN_MAP.values():
                    if midare is new_midare_status:
                        self.assertIn(midare, p1_kazuha_stts)
                    else:
                        self.assertNotIn(midare, p1_kazuha_stts)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.max_energy
                    ).build()
                ).build()
            ).build()
        ).build()

        # burst with no swirl
        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.ELEMENTAL_BURST,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2cs = gsm.get_game_state().player2.characters
        p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
        self.assertEqual(p2c1.hp, 7)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertFalse(p2c1.elemental_aura.has_aura())
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertEqual(
            gsm.get_game_state().player1.just_get_active_character().energy,
            0
        )
        p1 = gsm.get_game_state().player1
        p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
        assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
        self.assertEqual(p1_burst_summon.usages, 2)
        self.assertEqual(p1_burst_summon.curr_elem, Element.ANEMO)
        self.assertEqual(p1_burst_summon.ready_elem, None)

        # burst with swirl
        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                gsm = GameStateMachine(game_state, a1, a2)
                a1.inject_action(
                    SkillAction(
                        skill=CharacterSkill.ELEMENTAL_BURST,
                        instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                    )
                )
                gsm.player_step()
                gsm.step_until_holds(
                    lambda gs: gs.effect_stack.peek() == DeathCheckCheckerEffect()
                )
                p1 = gsm.get_game_state().player1
                p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
                self.assertEqual(p1_burst_summon.usages, 2)
                self.assertEqual(p1_burst_summon.curr_elem, Element.ANEMO)
                self.assertEqual(p1_burst_summon.ready_elem, elem)

                gsm.auto_step()
                p2cs = gsm.get_game_state().player2.characters
                p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
                self.assertEqual(p2c1.hp, 7)
                self.assertEqual(p2c2.hp, 9)
                self.assertEqual(p2c3.hp, 9)
                self.assertFalse(p2c1.elemental_aura.has_aura())
                self.assertIn(elem, p2c2.elemental_aura)
                self.assertIn(elem, p2c3.elemental_aura)
                self.assertEqual(
                    gsm.get_game_state().player1.just_get_active_character().energy,
                    0
                )
                p1 = gsm.get_game_state().player1
                p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
                self.assertEqual(p1_burst_summon.usages, 2)
                self.assertEqual(p1_burst_summon.curr_elem, elem)
                self.assertEqual(p1_burst_summon.ready_elem, None)

    def test_autumn_whirlwind_summon_update_on_character_swirl(self):
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AutumnWhirlwindSummon())
            ).build()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = just(game_state.action_step(Pid.P1, SkillAction(
                    skill=CharacterSkill.SKILL2,
                    instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                )))
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 2)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

    def test_autumn_whirlwind_summon_on_self_dmg(self):
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AutumnWhirlwindSummon())
            ).phase(
                Act.PASSIVE_WAIT_PHASE,
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_phase(
            lambda mode: mode.end_phase()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 1)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

                p2_chars = game_state.player2.characters
                p2_c1 = p2_chars.just_get_character(1)
                p2_c2 = p2_chars.just_get_character(2)
                p2_c3 = p2_chars.just_get_character(3)
                self.assertEqual(p2_c1.hp, 9)
                self.assertEqual(p2_c2.hp, 9)
                self.assertEqual(p2_c3.hp, 9)
                self.assertFalse(p2_c1.elemental_aura.has_aura())
                self.assertIn(elem, p2_c2.elemental_aura)
                self.assertIn(elem, p2_c3.elemental_aura)

    def test_autumn_whirlwind_summon_on_summon_swirl(self):
        from src.dgisim.summon.summon import _DmgPerRoundSummon

        class AnemoSummon(_DmgPerRoundSummon):
            usages: int = 2
            DMG: ClassVar[int] = 1
            ELEMENT: ClassVar[Element] = Element.ANEMO

        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AnemoSummon()).update_summon(AutumnWhirlwindSummon())
            ).phase(
                Act.PASSIVE_WAIT_PHASE,
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_phase(
            lambda mode: mode.end_phase()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 1)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

                p2_chars = game_state.player2.characters
                p2_c1 = p2_chars.just_get_character(1)
                p2_c2 = p2_chars.just_get_character(2)
                p2_c3 = p2_chars.just_get_character(3)
                self.assertEqual(p2_c1.hp, 8)
                self.assertEqual(p2_c2.hp, 9)
                self.assertEqual(p2_c3.hp, 9)
                self.assertIn(elem, p2_c1.elemental_aura)
                self.assertIn(elem, p2_c2.elemental_aura)
                self.assertIn(elem, p2_c3.elemental_aura)

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(
                card=PoeticsOfFuubutsu,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_next_phase()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        p1_kazuha = gsm.get_game_state().player1.characters.just_get_character(2)
        self.assertEqual(p2ac.hp, 7)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertEqual(p1ac.id, 3)
        self.assertIn(PoeticsOfFuubutsuStatus, p1_kazuha.character_statuses)

    def test_poetics_of_fuubutsu_status(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_character_statuses(
                        lambda eqs: eqs.update_status(PoeticsOfFuubutsuStatus())
                    ).build()
                ).build()
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        game_state = oppo_aura_elem(base_game, Element.ELECTRO)
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()

        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        p1_combat_statuses = gsm.get_game_state().player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 2)
        self.assertNotIn(PoeticsOfFuubutsuPyroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)

        game_state = gsm.get_game_state()
        game_state = add_damage_effect(
            game_state,
            1,
            Element.ELECTRO,
            char_id=3,
            damage_type=DamageType(elemental_skill=True)
        )
        game_state = auto_step(game_state)

        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 5)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 1)
        self.assertNotIn(PoeticsOfFuubutsuPyroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)

        game_state = remove_aura(game_state)
        game_state = add_damage_effect(
            game_state,
            1,
            Element.PYRO,
            char_id=3,
            damage_type=DamageType(elemental_skill=True)
        )
        game_state = auto_step(game_state)

        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)

        game_state = kill_character(game_state, 1, hp=10)
        game_state = oppo_aura_elem(game_state, Element.PYRO)

        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_actions([
            SwapAction(
                char_id=2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            ),
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
        ])
        gsm.player_step()
        gsm.player_step()
        gsm.auto_step()
        p1_combat_statuses = gsm.get_game_state().player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuPyroStatus).usages, 2)
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 1)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)
