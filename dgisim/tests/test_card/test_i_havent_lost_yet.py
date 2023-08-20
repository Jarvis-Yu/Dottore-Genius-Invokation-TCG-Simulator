import unittest

from .common_imports import *


class TestIHaventLostYet(unittest.TestCase):
    def test_i_havent_lost_yet(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().hand_cards(
                Cards({IHaventLostYet: 4})
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).hand_cards(
                Cards({IHaventLostYet: 4})
            ).f_characters(
                lambda cs: cs.factory().f_characters(
                    lambda chars: tuple(
                        char.factory().hp(1).build()
                        for char in chars
                    )
                ).build()
            ).build()
        ).build()

        game_state = base_game
        self.assertRaises(Exception, lambda: game_state.action_step(
            Pid.P1,
            CardAction(
                card=IHaventLostYet,
                instruction=DiceOnlyInstruction(dices=ActualDices({})),
            ),
        ))
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        p2_old_dices = game_state.get_player2().get_dices()
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.NORMAL_ATTACK,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            )
        )
        a2.inject_actions([
            DeathSwapAction(
                char_id=2
            ),
            CardAction(
                card=IHaventLostYet,
                instruction=DiceOnlyInstruction(dices=ActualDices({})),
            ),
        ])
        gsm.player_step()
        gsm.player_step()
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_energy(), 1)
        self.assertEqual(
            game_state.get_player2().get_dices()[Element.OMNI],
            p2_old_dices[Element.OMNI] + 1,
        )

        # test only one can be used per round
        self.assertFalse(IHaventLostYet.loosely_usable(game_state, Pid.P2))
