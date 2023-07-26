
import unittest

from dgisim.tests.test_characters.common_imports import *


class TestAratakiItto(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                AratakiItto.from_default(2)
            ).build()
            ).f_hand_cards(
                lambda hcs: hcs.add(AratakiIchiban)
        ).dices(
            ActualDices({Element.OMNI: 100})  # even number
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(
            Act.END_PHASE
        ).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is AratakiItto

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().elem_auras())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(SuperlativeSuperstrengthStatus).usages,
            1
        )
        self.assertIn(UshiSummon, p1.get_summons())
        ushi = p1.get_summons().just_find(UshiSummon)
        assert isinstance(ushi, UshiSummon)
        self.assertEqual(ushi.usages, 1)
        self.assertEqual(ushi.status_gaining_usages, 1)
        self.assertEqual(ushi.status_gaining_available, False)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.get_max_energy()
                    ).build()
                ).build()
            ).build()
        ).build()
        base_game = oppo_aura_elem(base_game, Element.HYDRO)

        # test burst base damage
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm = GameStateMachine(base_game, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(RagingOniKing).usages,
            2
        )

    def test_superlative_superstrength_status(self):
        for i in range(1, 4):
            with self.subTest(usages=i):
                game_state = self.BASE_GAME.factory().f_player1(
                    lambda p1: p1.factory().f_characters(
                        lambda cs: cs.factory().f_active_character(
                            lambda ac: ac.factory().f_character_statuses(
                                lambda csts: csts.update_status(
                                    SuperlativeSuperstrengthStatus(usages=i))
                            ).build()
                        ).build()
                    ).build()
                ).build()
                assert game_state.get_player1().get_dices().is_even()
                a1, a2 = PuppetAgent(), PuppetAgent()
                gsm = GameStateMachine(game_state, a1, a2)

                a1.inject_action(SkillAction(
                    skill=CharacterSkill.NORMAL_ATTACK,
                    instruction=DiceOnlyInstruction(dices=ActualDices({
                        Element.OMNI: case_val(i < 2, 3, 2)
                    })),
                ))

                gsm.player_step()  # charged attack
                gsm.auto_step()

                p1ac = gsm.get_game_state().get_player1().just_get_active_character()
                p2ac = gsm.get_game_state().get_player2().just_get_active_character()
                self.assertEqual(p2ac.get_hp(), 7)
                if i == 1:
                    self.assertNotIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
                else:
                    self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
                    self.assertEqual(
                        p1ac.get_character_statuses().just_find(
                            SuperlativeSuperstrengthStatus
                        ).usages,
                        i - 1,
                    )

    def test_ushi_summon_triggered_by_action_phase_dmg(self):
        base_game = AddSummonEffect(
            target_pid=Pid.P1, summon=UshiSummon
        ).execute(self.BASE_GAME).factory().active_player_id(
            Pid.P2,
        ).f_player1(
            lambda p1: p1.factory().phase(Act.END_PHASE).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.ACTION_PHASE).build()
        ).build()

        # first character damage triggers ushi
        game_state = base_game.action_step(Pid.P2, SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        game_state = auto_step(just(game_state))

        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(
                SuperlativeSuperstrengthStatus
            ).usages,
            1,
        )
        self.assertIn(UshiSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(UshiSummon).usages, 0)

        # second character damage doesn't trigger ushi
        game_state = game_state.action_step(Pid.P2, SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        game_state = auto_step(just(game_state))

        p1 = game_state.get_player1()
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(
                SuperlativeSuperstrengthStatus
            ).usages,
            1,
        )
        self.assertIn(UshiSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(UshiSummon).usages, 0)

    def test_ushi_summon_triggered_by_end_phase_summon(self):
        base_game = self.BASE_GAME.factory().f_phase(
            lambda mode: mode.end_phase()
        ).active_player_id(
            Pid.P2,
        ).f_player1(
            lambda p1: p1.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).f_summons(
                lambda sms: sms.update_summon(UshiSummon())
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).f_summons(
                lambda sms: sms.update_summon(BurningFlameSummon())
            ).build()
        ).build()

        game_state = auto_step(base_game)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(
                SuperlativeSuperstrengthStatus
            ).usages,
            1,
        )
        self.assertNotIn(UshiSummon, p1.get_summons())

    def test_ushi_summon_not_triggered_if_dmg_kill_active_char(self):
        """ This is a test for existing bug in the official game """
        base_game = AddSummonEffect(
            target_pid=Pid.P1, summon=UshiSummon
        ).execute(self.BASE_GAME).factory().active_player_id(
            Pid.P2,
        ).f_player1(
            lambda p1: p1.factory().phase(
                Act.END_PHASE
            ).f_characters(
                # need someone other than Itto to die
                lambda cs: cs.factory().active_character_id(1).build()
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(
                Act.ACTION_PHASE
            ).f_characters(
                # 1 is Rhodeia, I need some one who deals 2 damage for normal attack
                lambda cs: cs.factory().active_character_id(2).build()
            ).build()
        ).build()
        base_game = kill_character(base_game, character_id=1, pid=Pid.P1, hp=1)

        # first character damage triggers ushi
        game_state = base_game.action_step(Pid.P2, SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        game_state = auto_step(just(game_state))
        game_state = game_state.action_step(Pid.P1, DeathSwapAction(char_id=2))
        game_state = auto_step(just(game_state))

        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        self.assertNotIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertIn(UshiSummon, p1.get_summons())
        ushi = p1.get_summons().just_find(UshiSummon)
        assert isinstance(ushi, UshiSummon)
        self.assertEqual(ushi.status_gaining_usages, 1)
        self.assertEqual(ushi.status_gaining_available, False)

    def test_raging_oni_king_status(self):
        game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_character_statuses(
                        lambda csts: csts.update_status(RagingOniKing())
                    ).build()
                ).build()
            ).build()
        ).build()
        assert game_state.get_player1().get_dices().is_even()

        # first normal attack
        game_state = oppo_aura_elem(game_state, Element.CRYO)
        game_state = just(game_state.action_step(
            Pid.P1,
            SkillAction(
                skill=CharacterSkill.NORMAL_ATTACK,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
            )
        ))
        game_state = auto_step(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertIn(CrystallizeStatus, game_state.get_player1().get_combat_statuses())
        self.assertIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(SuperlativeSuperstrengthStatus).usages,
            1
        )
        self.assertIn(RagingOniKing, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(RagingOniKing).usages,
            2
        )

        # second normal attack, none charged
        game_state = just(game_state.action_step(
            Pid.P1,
            SkillAction(
                skill=CharacterSkill.NORMAL_ATTACK,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
            )
        ))
        game_state = auto_step(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 1)
        self.assertIn(RagingOniKing, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(RagingOniKing).usages,
            2
        )

        # going to next phase reduces the usages (duration)
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_phase(game_state.get_mode().end_phase())
        gsm.step_until_phase(game_state.get_mode().action_phase())

        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertIn(RagingOniKing, p1ac.get_character_statuses())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(RagingOniKing).usages,
            1
        )

        gsm.step_until_phase(game_state.get_mode().end_phase())
        gsm.step_until_phase(game_state.get_mode().action_phase())

        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertNotIn(RagingOniKing, p1ac.get_character_statuses())

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(  # even dices; first normal attack
                card=AratakiIchiban,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            SkillAction(  # odd dices
                skill=CharacterSkill.ELEMENTAL_SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            SkillAction(  # even dices; second normal attach (charged)
                skill=CharacterSkill.NORMAL_ATTACK,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_next_phase()
        game_state = gsm.get_game_state()
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 3)
        self.assertNotIn(SuperlativeSuperstrengthStatus, p1ac.get_character_statuses())
        self.assertIn(AratakiIchibanStatus, p1ac.get_equipment_statuses())
        talent = p1ac.get_equipment_statuses().just_find(AratakiIchibanStatus)
        self.assertTrue(talent.activated())
        self.assertEqual(talent.usages, 1)

        # getting to next phase resets talent equipement statics
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_phase(game_state.get_mode().action_phase())
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertIn(AratakiIchibanStatus, p1ac.get_equipment_statuses())
        talent = p1ac.get_equipment_statuses().just_find(AratakiIchibanStatus)
        self.assertFalse(talent.activated())
        self.assertEqual(talent.usages, 0)
