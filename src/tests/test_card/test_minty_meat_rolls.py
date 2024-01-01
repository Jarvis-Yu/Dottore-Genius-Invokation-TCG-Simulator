import unittest

from src.tests.test_card.common_imports import *


class TestMintyMeatRolls(unittest.TestCase):
    def test_card_normal_usage(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({MintyMeatRolls: 2})
            ).build()
        ).build()

        card_action = CardAction(
            card=MintyMeatRolls,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 1}),
                target=StaticTarget(
                    pid=Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertEqual(
            buffed_game_state
            .player1
            .just_get_active_character()
            .character_statuses
            .just_find(MintyMeatRollsStatus)
            .usages,
            3
        )
        self.assertTrue(
            buffed_game_state.player1.just_get_active_character().character_statuses
            .contains(SatiatedStatus)
        )

        # test normal attack with 3 dice fails
        normal_attack_action = SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(Pid.P1, normal_attack_action)
        )

        # test normal attack with 2 dice pass
        normal_attack_action = SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2}))
        )
        game_state = buffed_game_state.action_step(Pid.P1, normal_attack_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(
            p1ac
            .character_statuses
            .just_find(MintyMeatRollsStatus)
            .usages,
            2
        )

        # test 3 normal attacks consumes the status
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(buffed_game_state, a1, a2)
        a1.inject_actions([
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2}))
            )
        ] * 3)
        a2.inject_action(EndRoundAction())
        gsm.player_step()  # P1 normal attack
        gsm.player_step()  # P2 end round
        gsm.player_step()  # P1 normal attack
        gsm.player_step()  # P1 normal attack
        gsm.auto_step()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        self.assertFalse(
            p1ac
            .character_statuses
            .contains(MintyMeatRollsStatus)
        )

        # test shield disappears after round ends
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(buffed_game_state, a1, a2)
        a1.inject_action(EndRoundAction()) # skip action phase
        a2.inject_action(EndRoundAction())
        a1.inject_action(DiceSelectAction(selected_dice=ActualDice({}))) # skip roll phase
        a2.inject_action(DiceSelectAction(selected_dice=ActualDice({})))
        gsm.step_until_next_phase()
        gsm.step_until_phase(buffed_game_state.mode.action_phase())
        game_state = gsm.get_game_state()
        p1ac = game_state.player1.just_get_active_character()
        self.assertFalse(p1ac.character_statuses.contains(MintyMeatRollsStatus))
