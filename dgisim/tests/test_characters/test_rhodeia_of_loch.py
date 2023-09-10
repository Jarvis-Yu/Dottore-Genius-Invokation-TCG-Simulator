
import unittest

from dgisim.tests.test_characters.common_imports import *


class TestRohdeiaOfLoch(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(1).build()  # make active character Rhodeia
        ).f_hand_cards(
            lambda hcs: hcs.add(StreamingSurge)  # TODO: replace with Rhodeia Talent Card
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(Act.END_PHASE).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is RhodeiaOfLoch

    def test_frog_summon(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(OceanicMimicFrogSummon())
            ).build()
        ).build()

        # first hit
        game_state = add_damage_effect(base_game, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 9)
        self.assertEqual(frog.usages, 1)

        # second hit
        game_state = add_damage_effect(game_state, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 8)
        self.assertEqual(frog.usages, 0)

        # third hit
        game_state = add_damage_effect(game_state, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 6)
        self.assertEqual(frog.usages, 0)

        # end round and frog attacks & disappears
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(EndRoundAction())
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        ac = game_state.get_player1().just_get_active_character()
        optional_frog = game_state.get_player2().get_summons().find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertTrue(optional_frog is None)

        # end round with frog(2) keeps frog untouched
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(EndRoundAction())
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        ac = game_state.get_player1().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 10)
        self.assertFalse(ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertTrue(frog.usages, 2)

    def test_raptor_and_squirrel_summons(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    OceanicMimicRaptorSummon()
                ).update_summon(
                    OceanicMimicSquirrelSummon()
                )
            ).build()
        ).build()
        base_game = kill_character(base_game, 1, hp=1)

        a1.inject_action(EndRoundAction())
        a2.inject_action(DeathSwapAction(char_id=2))

        gsm = GameStateMachine(base_game, a1, a2)

        # after first end round
        gsm.player_step()  # P1 END
        gsm.player_step()  # p2 death swap
        gsm.auto_step()
        a1.inject_action(DicesSelectAction(selected_dices=ActualDices({})))  # skip roll phase
        a2.inject_action(DicesSelectAction(selected_dices=ActualDices({})))
        gsm.step_until_phase(base_game.get_mode().action_phase())

        game_state = gsm.get_game_state()
        p1_summons = game_state.get_player1().get_summons()
        p2_ac = game_state.get_player2().just_get_active_character()
        p2_c1 = game_state.get_player2().get_characters().just_get_character(1)
        self.assertEqual(p1_summons.just_find(OceanicMimicRaptorSummon).usages, 2)
        self.assertEqual(p1_summons.just_find(OceanicMimicSquirrelSummon).usages, 1)
        self.assertEqual(p2_ac.get_hp(), 8)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertEqual(p2_c1.get_hp(), 0)

        # after second end round
        a1.inject_action(EndRoundAction())  # skip action phase
        a2.inject_action(EndRoundAction())
        gsm.step_until_phase(game_state.get_mode().end_phase())
        a1.inject_action(DicesSelectAction(selected_dices=ActualDices({})))  # skip roll phase
        a2.inject_action(DicesSelectAction(selected_dices=ActualDices({})))
        gsm.step_until_phase(game_state.get_mode().action_phase())

        game_state = gsm.get_game_state()
        p1_summons = game_state.get_player1().get_summons()
        p2_ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p1_summons.just_find(OceanicMimicRaptorSummon).usages, 1)
        self.assertFalse(p1_summons.contains(OceanicMimicSquirrelSummon))
        self.assertEqual(p2_ac.get_hp(), 5)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))

        # after third end round
        a1.inject_action(EndRoundAction())
        a2.inject_action(EndRoundAction())

        gsm.player_step()
        gsm.player_step()
        gsm.auto_step()

        game_state = gsm.get_game_state()
        p1_summons = game_state.get_player1().get_summons()
        p2_ac = game_state.get_player2().just_get_active_character()
        self.assertFalse(p1_summons.contains(OceanicMimicRaptorSummon))
        self.assertFalse(p1_summons.contains(OceanicMimicSquirrelSummon))
        self.assertEqual(p2_ac.get_hp(), 4)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.HYDRO))

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    OceanicMimicRaptorSummon()
                ).update_summon(
                    OceanicMimicSquirrelSummon()
                )
            ).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1_summons = game_state.get_player1().get_summons()
        self.assertEqual(p1_summons.just_find(OceanicMimicFrogSummon).usages, 2)
        self.assertEqual(p1_summons.just_find(OceanicMimicRaptorSummon).usages, 3)
        self.assertEqual(p1_summons.just_find(OceanicMimicSquirrelSummon).usages, 2)

    def test_elemental_skill2(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(OceanicMimicRaptorSummon())
            ).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 5})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1_summons = game_state.get_player1().get_summons()
        self.assertEqual(p1_summons.just_find(OceanicMimicFrogSummon).usages, 2)
        self.assertEqual(p1_summons.just_find(OceanicMimicRaptorSummon).usages, 3)
        self.assertEqual(p1_summons.just_find(OceanicMimicSquirrelSummon).usages, 2)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    OceanicMimicRaptorSummon()
                )
            ).f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(ac.get_max_energy()).build()
                ).build()
            ).build()
        ).build()

        # burst with one summon
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p2_ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2_ac.get_hp(), 6)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))

        # burst with two summons
        game_state = base_game.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    BurningFlameSummon()
                )
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p2_ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2_ac.get_hp(), 4)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    OceanicMimicRaptorSummon()
                ).update_summon(
                    BurningFlameSummon(usages=2)
                )
            ).f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(ac.get_max_energy()).build()
                ).build()
            ).build()
        ).build()

        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(
            CardAction(
                card=StreamingSurge,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 4})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p2_ac = game_state.get_player2().just_get_active_character()
        p1_summons = game_state.get_player1().get_summons()
        self.assertEqual(p2_ac.get_hp(), 4)
        self.assertTrue(p2_ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertEqual(p1_summons.just_find(OceanicMimicRaptorSummon).usages, 4)
        self.assertEqual(p1_summons.just_find(BurningFlameSummon).usages, 3)
