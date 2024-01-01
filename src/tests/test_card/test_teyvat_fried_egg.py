import unittest

from src.tests.test_card.common_imports import *


class TestTeyvatFriedEgg(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p1: p1.factory().f_hand_cards(
            lambda hcs: hcs.add(TeyvatFriedEgg).add(TeyvatFriedEgg)
        ).f_characters(
            lambda cs: cs.factory().f_active_character(
                lambda ac: Mona.from_default(ac.id)
            ).build()
        ).build()
    ).build()

    def test_basic_revival(self):
        base_game = kill_character(self.BASE_GAME, character_id=1, pid=Pid.P1, hp=1)
        game_state = base_game
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P1, DeathSwapAction(char_id=2))

        # check player 1's character 1 is defeated
        p1c1 = game_state.player1.characters.just_get_character(1)
        self.assertTrue(p1c1.is_defeated())

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TeyvatFriedEgg,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
            )
        ))

        # check player 1's character 1 is alive again
        p1c1 = game_state.player1.characters.just_get_character(1)
        self.assertTrue(p1c1.is_alive())
        self.assertEqual(p1c1.hp, 1)
        self.assertIn(ReviveOnCooldownStatus, game_state.player1.combat_statuses)

        # check cannot use twice per round
        game_state = kill_character(game_state, character_id=1, pid=Pid.P1, hp=0)
        self.assertRaises(Exception, lambda: game_state.action_step(Pid.P1, CardAction(
            card=TeyvatFriedEgg,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
            )
        )))

        # proceed to next round
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_phase(game_state.mode.action_phase())
        gsm.auto_step()
        game_state = fill_dice_with_omni(gsm.get_game_state())
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TeyvatFriedEgg,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
            )
        ))

        # check player 1's character 1 is alive again the next round
        p1c1 = game_state.player1.characters.just_get_character(1)
        self.assertTrue(p1c1.is_alive())
        self.assertEqual(p1c1.hp, 1)
        self.assertIn(ReviveOnCooldownStatus, game_state.player1.combat_statuses)

    def test_revival_resets_character_statuses(self):
        base_game = kill_character(self.BASE_GAME, character_id=1, pid=Pid.P1, hp=1)
        game_state = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_hiddens(
                        lambda hiddens: hiddens.update_status(IllusoryTorrentStatus(available=False))
                    ).build()
                ).build()
            ).build()
        ).build()
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P1, DeathSwapAction(char_id=2))

        # check player 1's character 1 is defeated
        p1c1 = game_state.player1.characters.just_get_character(1)
        self.assertTrue(p1c1.is_defeated())

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TeyvatFriedEgg,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
            )
        ))

        # check player 1's character 1 is alive again
        p1c1 = game_state.player1.characters.just_get_character(1)
        self.assertTrue(p1c1.is_alive())
        self.assertEqual(p1c1.hp, 1)
        self.assertTrue(p1c1.hidden_statuses.just_find(IllusoryTorrentStatus).available)
