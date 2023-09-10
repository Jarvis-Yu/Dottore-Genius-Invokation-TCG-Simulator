
import unittest

from dgisim.tests.test_characters.common_imports import *


class TestMona(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Mona.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(ProphecyOfSubmersion)
        ).build()
    ).build()

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
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().get_player1()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertIn(ReflectionSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ReflectionSummon).usages, 1)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.get_max_energy()
                    ).build()
                ).build()
            ).build()
        ).build()

        # burst
        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.ELEMENTAL_BURST,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().get_player1()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertIn(IllusoryBubbleStatus, p1.get_combat_statuses())
        self.assertEqual(p1.just_get_active_character().get_energy(), 0)

    def test_passive_skill_illusory_torrent(self):
        active_is_mona_state = self.BASE_GAME
        active_not_mona = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(1).build()
            ).build()
        ).build()

        for state in (active_is_mona_state, active_not_mona):
            game_state = state
            a1, a2 = PuppetAgent(), PuppetAgent()
            gsm = GameStateMachine(game_state, a1, a2)
            if state is active_is_mona_state:
                a1.inject_action(SwapAction(
                    char_id=3,
                    instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
                ))
            elif state is active_not_mona:
                a1.inject_action(SwapAction(
                    char_id=2,
                    instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
                ))
            gsm.player_step()
            gsm.auto_step()
            game_state = gsm.get_game_state()
            mona = game_state.get_player1().get_characters().find_first_character(Mona)
            assert mona is not None
            if state is active_is_mona_state:
                self.assertEqual(game_state.get_active_player_id(), Pid.P1)
                self.assertFalse(
                    mona.get_hidden_statuses().just_find(IllusoryTorrentStatus).available
                )
            elif state is active_not_mona:
                self.assertEqual(game_state.get_active_player_id(), Pid.P2)
                self.assertTrue(
                    mona.get_hidden_statuses().just_find(IllusoryTorrentStatus).available
                )

    def test_reflection_summon(self):
        # p1 has the summon and ends the round
        base_game = AddSummonEffect(Pid.P1, ReflectionSummon).execute(self.BASE_GAME)
        base_game = auto_step(just(base_game.action_step(Pid.P1, EndRoundAction())))

        # case 1: p2 attack twice then end
        game_state = base_game
        initial_hp = game_state.get_player1().just_get_active_character().get_hp()

        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_actions([
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
            ),
            EndRoundAction(),
        ])
        gsm.player_step()
        gsm.auto_step()  # p2 normal attack
        second_hp = gsm.get_game_state().get_player1().just_get_active_character().get_hp()
        gsm.player_step()
        gsm.auto_step()  # p2 normal attack
        third_hp = gsm.get_game_state().get_player1().just_get_active_character().get_hp()
        self.assertEqual(initial_hp - second_hp + 1, second_hp - third_hp)

        gsm.player_step()
        gsm.auto_step()  # p2 end round
        p1_summons = gsm.get_game_state().get_player1().get_summons()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertNotIn(ReflectionSummon, p1_summons)
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())

        # case 2: p2 end directly
        game_state = base_game
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(EndRoundAction())
        gsm.player_step()
        gsm.auto_step()  # p2 end round
        p1_summons = gsm.get_game_state().get_player1().get_summons()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertNotIn(ReflectionSummon, p1_summons)
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())

    def test_burst_status_illusory_bubble(self):
        base_game = AddCombatStatusEffect(Pid.P1, IllusoryBubbleStatus).execute(self.BASE_GAME)

        # with reaction (Hydro x Pyro)
        game_state = oppo_aura_elem(base_game, Element. PYRO)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertNotIn(IllusoryBubbleStatus, game_state.get_player1().get_combat_statuses())

        # with reaction (Electro x Cryo)
        game_state = SwapCharacterEffect(
            StaticTarget(Pid.P1, Zone.CHARACTERS, 3)
        ).execute(base_game)
        game_state = auto_step(game_state)
        assert isinstance(game_state.get_player1().just_get_active_character(), Keqing)
        game_state = oppo_aura_elem(game_state, Element.CRYO)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2cs = game_state.get_player2().get_characters()
        self.assertEqual(p2cs.just_get_character(1).get_hp(), 2)
        self.assertEqual(p2cs.just_get_character(2).get_hp(), 9)
        self.assertEqual(p2cs.just_get_character(3).get_hp(), 9)
        self.assertNotIn(IllusoryBubbleStatus, game_state.get_player1().get_combat_statuses())

        # test summon doesn't trigger
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(base_game)
        game_state = step_action(game_state, Pid.P1, EndRoundAction())
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = auto_step(game_state)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(IllusoryBubbleStatus, game_state.get_player1().get_combat_statuses())

        # test multiplying happens before shields
        game_state = oppo_aura_elem(base_game, Element.PYRO)
        game_state = AddCombatStatusEffect(Pid.P2, CrystallizeStatus).execute(game_state)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)  # (1 + 2) * 2 - 1
        self.assertNotIn(IllusoryBubbleStatus, game_state.get_player1().get_combat_statuses())

    def test_talent_prophecy_of_submersion(self):
        base_game = AddCharacterStatusEffect(
            StaticTarget(Pid.P1, Zone.CHARACTERS, 2),
            ProphecyOfSubmersionStatus,
        ).execute(self.BASE_GAME)

        # test reaction (Hydro x Dendro)
        game_state = oppo_aura_elem(base_game, Element.DENDRO)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)  # damage = 1 + 1 + 2
        self.assertIn(
            ProphecyOfSubmersionStatus,
            game_state.get_player1().just_get_active_character().get_equipment_statuses(),
        )

        # test reaction (Hydro x Electro)
        game_state = oppo_aura_elem(base_game, Element.ELECTRO)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2ac = game_state.get_player2().just_get_active_character()
        p2cs = game_state.get_player2().get_characters()
        self.assertEqual(p2cs.just_get_character(1).get_hp(), 6)
        self.assertEqual(p2cs.just_get_character(2).get_hp(), 9)
        self.assertEqual(p2cs.just_get_character(3).get_hp(), 9)
        self.assertIn(
            ProphecyOfSubmersionStatus,
            game_state.get_player1().just_get_active_character().get_equipment_statuses(),
        )

        # test summon can also benefit from this
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(base_game)
        game_state = oppo_aura_elem(game_state, Element.PYRO)
        game_state = step_action(game_state, Pid.P1, EndRoundAction())
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = auto_step(game_state)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)  # damage = 1 + 2 + 2
        self.assertIn(
            ProphecyOfSubmersionStatus,
            game_state.get_player1().just_get_active_character().get_equipment_statuses(),
        )

        # test summon's swirled reaction can also benefit from this
        game_state = AddSummonEffect(Pid.P1, AutumnWhirlwindSummon).execute(base_game)
        game_state = oppo_aura_elem(game_state, Element.PYRO)
        game_state = oppo_aura_elem(game_state, Element.HYDRO, char_id=2)
        game_state = oppo_aura_elem(game_state, Element.HYDRO, char_id=3)
        game_state = next_round(game_state)
        p2cs = game_state.get_player2().get_characters()
        self.assertEqual(p2cs.just_get_character(1).get_hp(), 9)
        self.assertEqual(p2cs.just_get_character(2).get_hp(), 5)
        self.assertEqual(p2cs.just_get_character(3).get_hp(), 5)
        self.assertIn(
            ProphecyOfSubmersionStatus,
            game_state.get_player1().just_get_active_character().get_equipment_statuses(),
        )

        # test none hydro reaction doesn't benefit from this
        game_state = AddSummonEffect(Pid.P1, BurningFlameSummon).execute(base_game)
        game_state = oppo_aura_elem(game_state, Element.CRYO)
        game_state = step_action(game_state, Pid.P1, EndRoundAction())
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = auto_step(game_state)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)  # damage = 1 + 2
        self.assertIn(
            ProphecyOfSubmersionStatus,
            game_state.get_player1().just_get_active_character().get_equipment_statuses(),
        )

        # test not working if Mona is off field
        game_state = SwapCharacterEffect(
            StaticTarget(Pid.P1, Zone.CHARACTERS, 3)
        ).execute(base_game)
        game_state = auto_step(game_state)
        assert isinstance(game_state.get_player1().just_get_active_character(), Keqing)
        game_state = oppo_aura_elem(game_state, Element.HYDRO)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        p2cs = game_state.get_player2().get_characters()
        self.assertEqual(p2cs.just_get_character(1).get_hp(), 6)
        self.assertEqual(p2cs.just_get_character(2).get_hp(), 9)
        self.assertEqual(p2cs.just_get_character(3).get_hp(), 9)
