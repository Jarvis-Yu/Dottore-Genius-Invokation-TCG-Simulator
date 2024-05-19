import unittest

from src.dgisim.mode import AllOmniMode
from src.tests.test_characters.common_imports import *

class TestKaeya(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(2).build()  # make active character Kaeya
        ).f_hand_cards(
            lambda hcs: hcs.add(ColdBloodedStrike)
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(
            Act.END_PHASE
        ).f_characters(
            lambda cs: cs.factory().active_character_id(
                3  # make opponenet active characater Keqing
            ).build()
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Kaeya
    assert type(BASE_GAME.player2.just_get_active_character()) is Keqing

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

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertTrue(p2ac.elemental_aura.contains(Element.CRYO))

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
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4})),
        ))
        gsm = GameStateMachine(base_game, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p2ac = game_state.player2.just_get_active_character()
        p1 = game_state.player1
        self.assertEqual(p2ac.hp, 9)
        self.assertTrue(p2ac.elemental_aura.contains(Element.CRYO))
        self.assertEqual(
            p1.combat_statuses.just_find(IcicleStatus).usages,
            3
        )

        # test normal swap cause usage of burst
        game_state_p1_move = game_state.factory().f_player1(
            lambda p: p.factory().f_hand_cards(
                lambda hcs: hcs.add(LightningStiletto)
            ).build()
        ).player2(
            self.BASE_GAME.player2.factory().f_combat_statuses(
                lambda cs: cs.update_status(IcicleStatus())
            ).build()
        ).build()

        a1.inject_action(SwapAction(
            char_id=1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        gsm = GameStateMachine(game_state_p1_move, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertTrue(p2ac.elemental_aura.contains(Element.CRYO))
        self.assertEqual(
            p1.combat_statuses.just_find(IcicleStatus).usages,
            2
        )

        # test Keqing card swap cause usage of Icicle prior of Keqing's skill
        a1.inject_action(CardAction(
            card=LightningStiletto,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        gsm = GameStateMachine(game_state_p1_move, a1, a2)
        gsm.player_step()
        gsm.step_until_holds(
            lambda gs: gs.player1.combat_statuses.just_find(IcicleStatus).usages == 2
        )
        game_state = gsm.get_game_state()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertTrue(p2ac.elemental_aura.contains(Element.CRYO))

        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(1).hp, 9)
        self.assertEqual(p2cs.just_get_character(2).hp, 9)
        self.assertEqual(p2cs.just_get_character(3).hp, 4)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertEqual(
            p1.combat_statuses.just_find(IcicleStatus).usages,
            2
        )

        # test self being overloaded
        game_state_p2_move = game_state_p1_move.factory().active_player_id(
            Pid.P2
        ).f_player1(
            lambda p: p.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(Element.PYRO)
                    ).build()
                ).build()
            ).build()
        ).f_player2(
            lambda p: p.factory().phase(Act.ACTION_PHASE).build()
        ).build()

        a2.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm = GameStateMachine(game_state_p2_move, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertTrue(p2ac.elemental_aura.contains(Element.CRYO))
        self.assertEqual(
            p1.combat_statuses.just_find(IcicleStatus).usages,
            2
        )

        # test chain of Icicle of 2
        game_state_p2_move_and_low = kill_character(game_state_p2_move, 3, hp=2)
        a2.inject_actions([
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            DeathSwapAction(
                char_id=2,
            ),
        ])
        gsm = GameStateMachine(game_state_p2_move_and_low, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        gsm.player_step()  # a2 death swap character because Icicle killed their active character
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1 = game_state.player1
        p2 = game_state.player2
        p2cs = game_state.player2.characters
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(3).hp, 0)
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertEqual(
            p1.combat_statuses.just_find(IcicleStatus).usages,
            2
        )
        self.assertEqual(
            p2.combat_statuses.just_find(IcicleStatus).usages,
            2
        )

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        initial_hp = 3
        base_game_state = kill_character(
            game_state=self.BASE_GAME.factory().mode(AllOmniMode()).build(),
            char_id=2,
            pid=Pid.P1,
            hp=initial_hp,
        )

        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_actions([
            CardAction(
                card=ColdBloodedStrike,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            EndRoundAction(),
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
        ])
        a2.inject_action(EndRoundAction())

        # equiping the talent card casts elemental skill and heals
        gsm.player_step()  # p1 equip talent card
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p1ac.hp, initial_hp + 2)
        self.assertEqual(p2ac.hp, 7)

        # second elemtnal skill in same round doesn't heal
        gsm.player_step()  # p1 elemental skill 1
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        self.assertEqual(p1ac.hp, initial_hp + 2)

        gsm.player_step()  # p1 end round, go to next round
        gsm.auto_step()

        gsm.player_step()  # p2 end round, let p1 play
        gsm.auto_step()

        # elemtnal skill in next round heals
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        self.assertEqual(p1ac.hp, initial_hp + 4)
