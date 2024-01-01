import unittest

from src.tests.test_card.common_imports import *


class TestJueyunGuoba(unittest.TestCase):
    def test_Jueyun_Guoba_card_takes_effect(self):
        """
        Pre: active character of both players are "Rhodeia of Loch"
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({JueyunGuoba: 1})
            ).build()
        ).build()
        char1 = base_game_state.player1.just_get_active_character()
        p1, p2 = PuppetAgent(), PuppetAgent()

        # without JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        hp_without_guoba = gsm.get_game_state().player2.just_get_active_character().hp

        # with JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget(
                    Pid.P1,
                    Zone.CHARACTERS,
                    char1.id,
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .player1
            .just_get_active_character()
            .character_statuses
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().player2.just_get_active_character().hp,
            hp_without_guoba - 1
        )
        self.assertFalse(
            gsm
            .get_game_state()
            .player1
            .just_get_active_character()
            .character_statuses
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba on other character
        gsm = GameStateMachine(base_game_state, p1, p2)
        guobaed_char_id = char1.id % 3 + 1  # next character
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget(
                    Pid.P1,
                    Zone.CHARACTERS,
                    guobaed_char_id,
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .player1
            .characters
            .just_get_character(guobaed_char_id)
            .character_statuses
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().player2.just_get_active_character().hp,
            hp_without_guoba
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .player1
            .characters
            .just_get_character(guobaed_char_id)
            .character_statuses
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba but cast elemental skill
        game_state = set_active_player_id(base_game_state, Pid.P1, 2)
        gsm = GameStateMachine(game_state, p1, p2)
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget(
                    Pid.P1,
                    Zone.CHARACTERS,
                    2,
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.player_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        gsm.player_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().player2.just_get_active_character().hp,
            7,
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .player1
            .just_get_active_character()
            .character_statuses
            .contains(JueyunGuobaStatus)
        )
