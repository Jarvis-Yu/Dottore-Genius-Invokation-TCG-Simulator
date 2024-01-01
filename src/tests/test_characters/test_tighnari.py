import unittest

from src.tests.test_characters.common_imports import *


class TestTighnari(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Tighnari.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(KeenSight)
        ).dice(
            ActualDice({Element.OMNI: 100})  # even number
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(
            Act.END_PHASE
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Tighnari

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
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertTrue(p2ac.elemental_aura.contains(Element.DENDRO))
        self.assertFalse(gsm.get_game_state().player1.dice.is_even())

        # first normal attack
        game_state = remove_aura(gsm.get_game_state())
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertFalse(p2ac.elemental_aura.contains(Element.DENDRO))
        self.assertTrue(p1.dice.is_even())
        self.assertEqual(
            p1ac.character_statuses.just_find(VijnanaSuffusionStatus).usages,
            2
        )
        self.assertTrue(ClusterbloomArrowSummon not in p1.summons)

        # second normal attack (charged)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)
        self.assertTrue(p2ac.elemental_aura.contains(Element.DENDRO))
        self.assertFalse(p1.dice.is_even())
        self.assertEqual(
            p1ac.character_statuses.just_find(VijnanaSuffusionStatus).usages,
            1
        )
        self.assertEqual(
            p1.summons.just_find(ClusterbloomArrowSummon).usages,
            1,
        )

        # third normal attack
        game_state = gsm.get_game_state().factory().f_player1(  # reset dice to even
            lambda p1: p1.factory().dice(ActualDice({Element.OMNI: 100})).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertTrue(p2ac.elemental_aura.contains(Element.DENDRO))
        self.assertFalse(p1.dice.is_even())
        self.assertTrue(VijnanaSuffusionStatus not in p1ac.character_statuses)
        self.assertEqual(
            p1.summons.just_find(ClusterbloomArrowSummon).usages,
            2,
        )

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

        # burst
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
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertTrue(p2c1.elemental_aura.contains(Element.DENDRO))
        self.assertFalse(p2c2.elemental_aura.elem_auras())
        self.assertFalse(p2c3.elemental_aura.elem_auras())
        self.assertEqual(
            gsm.get_game_state().player1.just_get_active_character().energy,
            0
        )

    def test_summon(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(
                    ClusterbloomArrowSummon()
                ).update_summon(
                    ClusterbloomArrowSummon()
                )
            ).build()
        ).build()
        p1_summons = base_game.player1.summons
        self.assertEqual(p1_summons.just_find(ClusterbloomArrowSummon).usages, 2)

        a1.inject_action(EndRoundAction())
        gsm = GameStateMachine(base_game, a1, a2)

        # after first end round
        gsm.player_step()  # P1 END
        gsm.auto_step()
        a1.inject_action(DiceSelectAction(selected_dice=ActualDice({})))  # skip roll phase
        a2.inject_action(DiceSelectAction(selected_dice=ActualDice({})))
        gsm.step_until_phase(base_game.mode.action_phase())

        game_state = gsm.get_game_state()
        p1_summons = game_state.player1.summons
        p2_ac = game_state.player2.just_get_active_character()
        self.assertEqual(p1_summons.just_find(ClusterbloomArrowSummon).usages, 1)
        self.assertEqual(p2_ac.hp, 9)
        self.assertTrue(p2_ac.elemental_aura.contains(Element.DENDRO))

        # after second end round
        a1.inject_action(EndRoundAction())  # skip action phase
        a2.inject_action(EndRoundAction())
        gsm.step_until_next_phase() # to End Phase
        gsm.auto_step()
        a1.inject_action(DiceSelectAction(selected_dice=ActualDice({})))  # skip roll phase
        a2.inject_action(DiceSelectAction(selected_dice=ActualDice({})))
        gsm.step_until_phase(base_game.mode.action_phase())

        game_state = gsm.get_game_state()
        p1_summons = game_state.player1.summons
        p2_ac = game_state.player2.just_get_active_character()
        self.assertTrue(ClusterbloomArrowSummon not in p1_summons)
        self.assertEqual(p2_ac.hp, 8)
        self.assertTrue(p2_ac.elemental_aura.contains(Element.DENDRO))

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME

        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(
                card=KeenSight,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_next_phase()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertTrue(p2ac.elemental_aura.contains(Element.DENDRO))
