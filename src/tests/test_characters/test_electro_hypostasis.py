import unittest

from src.tests.test_characters.common_imports import *


class TestAratakiItto(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                ElectroHypostasis.from_default(2).factory().f_hiddens(
                    lambda hiddens: hiddens.remove(ElectroHypostasisPassiveStatus)
                ).f_character_statuses(
                    lambda cstts: cstts.update_status(ElectroCrystalCoreStatus())
                ).build()
            ).build()
            ).f_hand_cards(
                lambda hcs: hcs.add(AbsorbingPrism)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is ElectroHypostasis

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
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 5})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        ## Normal Test ##
        # p1 skill
        gsm.player_step()
        gsm.auto_step()
        post_fst_skill_game_state = gsm.get_game_state()
        p1ac = post_fst_skill_game_state.player1.just_get_active_character()
        p2ac = post_fst_skill_game_state.player2.just_get_active_character()
        self.assertIn(RockPaperScissorsComboScissorsStatus, p1ac.character_statuses)
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.hp, 8)
        self.assertEqual(post_fst_skill_game_state.active_player_id, Pid.P2)

        # p1 second skill (prepare skill)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertNotIn(RockPaperScissorsComboScissorsStatus, p1ac.character_statuses)
        self.assertIn(RockPaperScissorsComboPaperStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.hp, 6)
        self.assertEqual(post_fst_skill_game_state.active_player_id, Pid.P2)

        # p1 third skill (prepare skill)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertNotIn(RockPaperScissorsComboScissorsStatus, p1ac.character_statuses)
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.hp, 3)
        self.assertEqual(post_fst_skill_game_state.active_player_id, Pid.P2)

        ## Frozen Test ##
        game_state = post_fst_skill_game_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_character_statuses(
                        lambda cstts: cstts.update_status(FrozenStatus())
                    ).build()
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertIn(RockPaperScissorsComboScissorsStatus, p1ac.character_statuses)
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.hp, 8)
        self.assertEqual(gsm.get_game_state().active_player_id, Pid.P1)

        ## Overload Test ##
        game_state = post_fst_skill_game_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(Element.ELECTRO)
                    ).build()
                ).build()
            ).build()
        ).f_player2(
            lambda p2: p2.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: Klee.from_default(ac.id)
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1_electro_hypo = gsm.get_game_state().player1.characters.just_get_character(2)
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertNotIn(
            RockPaperScissorsComboScissorsStatus,
            p1_electro_hypo.character_statuses
        )
        self.assertNotIn(
            RockPaperScissorsComboPaperStatus,
            p1_electro_hypo.character_statuses
        )
        self.assertEqual(p2ac.hp, 10)
        self.assertEqual(gsm.get_game_state().active_player_id, Pid.P1)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.max_energy
                    ).build()
                ).build()
            ).build()
        ).build()

        # test burst base damage
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm = GameStateMachine(base_game, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(ChainsOfWardingThunderSummon, p1.summons)
        summon = p1.summons.just_find(ChainsOfWardingThunderSummon)
        assert isinstance(summon, ChainsOfWardingThunderSummon)
        self.assertEqual(summon.usages, 2)
        self.assertEqual(summon.swap_reduce_usages, 1)

    def test_chains_of_warding_thunder_summon(self):
        base_game = AddSummonEffect(
            target_pid=Pid.P1, summon=ChainsOfWardingThunderSummon
        ).execute(self.BASE_GAME).factory().active_player_id(
            Pid.P2,
        ).f_player1(
            lambda p1: p1.factory().phase(Act.END_PHASE).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.ACTION_PHASE).build()
        ).build()

        a1: PlayerAgent; a2: PlayerAgent
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(base_game, a1, a2)
        a2.inject_actions([
            SwapAction(
                char_id=2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
            ),
            SwapAction(
                char_id=1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
            ),
        ])
        gsm.player_step()  # first swap costs more due to summon
        gsm.player_step()  # second swap costs the same cause usages run out
        p1_summons = gsm.get_game_state().player1.summons
        self.assertIn(ChainsOfWardingThunderSummon, p1_summons)
        character_summon = p1_summons.just_find(ChainsOfWardingThunderSummon)
        assert isinstance(character_summon, ChainsOfWardingThunderSummon)
        self.assertEqual(character_summon.usages, 2)
        self.assertEqual(character_summon.swap_reduce_usages, 0)

        # second round resets swap cost raise
        a1, a2 = LazyAgent(), LazyAgent()
        gsm = GameStateMachine(gsm.get_game_state(), a1, a2)
        gsm.step_until_phase(base_game.mode.action_phase())
        a1, a2 = LazyAgent(), PuppetAgent()
        gsm = GameStateMachine(fill_dice_with_omni(gsm.get_game_state()), a1, a2)
        gsm.player_step()  # p1 ends round
        a2.inject_actions([
            SwapAction(
                char_id=2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
            ),
            SwapAction(
                char_id=1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
            ),
        ])
        gsm.player_step()  # first swap costs more due to summon
        gsm.player_step()  # second swap costs the same cause usages run out
        p1_summons = gsm.get_game_state().player1.summons
        self.assertIn(ChainsOfWardingThunderSummon, p1_summons)
        character_summon = p1_summons.just_find(ChainsOfWardingThunderSummon)
        assert isinstance(character_summon, ChainsOfWardingThunderSummon)
        self.assertEqual(character_summon.usages, 1)
        self.assertEqual(character_summon.swap_reduce_usages, 0)

    def test_gaining_electro_crystal_core_status(self):
        """ Test Electro Crystal Core Status is gained at the start of the first round """
        # start with hidden status only
        game_state = GameState.from_default().factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().character(
                    ElectroHypostasis.from_default(2)
                ).build()
            ).build()
        ).build()
        electro_hypostasis = game_state.player1.characters.get_character(2)
        assert electro_hypostasis is not None
        self.assertIn(ElectroHypostasisPassiveStatus, electro_hypostasis.hidden_statuses)
        self.assertNotIn(ElectroCrystalCoreStatus, electro_hypostasis.character_statuses)

        # gain character status ver electro core status on first action phase start
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_phase(game_state.mode.action_phase())
        gsm.step_until_holds(lambda gs: gs.waiting_for() is not None)
        game_state = gsm.get_game_state()
        electro_hypostasis = game_state.player1.characters.get_character(2)
        assert electro_hypostasis is not None
        self.assertNotIn(ElectroHypostasisPassiveStatus, electro_hypostasis.hidden_statuses)
        self.assertIn(ElectroCrystalCoreStatus, electro_hypostasis.character_statuses)

    def test_triggering_electro_crystal_core_status(self):
        """ Test Electro Crystal Core Status does revive the character """
        base_game = kill_character(self.BASE_GAME, char_id=2, pid=Pid.P1, hp=1)
        base_game = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(base_game, Pid.P1),
            status=GamblersEarringsStatus,
        ).execute(base_game)
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm.player_step()  # P1 normal attack
        gsm.player_step()  # P2 normal attack; kills P1
        gsm.step_until_holds(lambda gs:
                             gs.effect_stack.is_not_empty()
                             and isinstance(gs.effect_stack.peek(), AliveMarkCheckerEffect)
                             )
        p2_dice_after_attack = gsm.get_game_state().player2.dice.num_dice()
        # checks alive check is before skill energy recharge
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertTrue(p1ac.is_alive())
        self.assertEqual(p1ac.hp, 0)
        self.assertIn(ElectroCrystalCoreStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.energy, 0)

        gsm.step_until_holds(lambda gs: gs.player1.just_get_active_character().hp > 0)

        # checks revival is before skill energy recharge
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertTrue(p1ac.is_alive())
        self.assertEqual(p1ac.hp, 3)
        self.assertNotIn(ElectroCrystalCoreStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.energy, 0)

        gsm.auto_step()
        # checks after math
        game_state = gsm.get_game_state()
        p1ac = game_state.player1.just_get_active_character()
        p2 = game_state.player2
        p2ac = p2.just_get_active_character()
        self.assertTrue(p1ac.is_alive())
        self.assertEqual(p1ac.hp, 3)
        self.assertNotIn(ElectroCrystalCoreStatus, p1ac.character_statuses)
        self.assertEqual(p2ac.energy, 1)
        # checks Gambler's Earrings not triggered
        self.assertEqual(p2.dice.num_dice(), p2_dice_after_attack)
        # check it's P1's turn again as usual
        self.assertIs(game_state.waiting_for(), Pid.P1)

    def test_talent_card(self):
        base_game = kill_character(self.BASE_GAME, char_id=2, pid=Pid.P1, hp=1)
        base_game = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_character_statuses(
                        lambda cstts: cstts.remove(ElectroCrystalCoreStatus)
                    ).build()
                ).build()
            ).build()
        ).build()

        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(CardAction(
            card=AbsorbingPrism,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 2})),
        ))
        gsm.player_step()
        gsm.auto_step()

        p1ac = gsm.get_game_state().player1.just_get_active_character()
        self.assertEqual(p1ac.hp, 4)
        self.assertIn(ElectroCrystalCoreStatus, p1ac.character_statuses)
