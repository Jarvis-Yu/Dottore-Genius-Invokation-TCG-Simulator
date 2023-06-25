import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.card.cards import *
from dgisim.src.card.card import *
from dgisim.src.status.status import *
from dgisim.src.support.support import *
from dgisim.src.agents import *


class TestCard(unittest.TestCase):
    def test_Jueyun_Guoba_card_takes_effect(self):
        """
        Pre: active character of both players are "Rhodeia of Loch"
        TODO: move to test_card.py
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({JueyunGuoba: 1})
            ).build()
        ).build()
        char1 = base_game_state.get_player1().just_get_active_character()
        p1, p2 = PuppetAgent(), PuppetAgent()

        # without JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        hp_without_guoba = gsm.get_game_state().get_player2().just_get_active_character().get_hp()

        # with JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTERS,
                    char1.get_id(),
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            hp_without_guoba - 1
        )
        self.assertFalse(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba on other character
        gsm = GameStateMachine(base_game_state, p1, p2)
        guobaed_char_id = char1.get_id() % 3 + 1  # next character
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTERS,
                    guobaed_char_id,
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .get_characters()
            .just_get_character(guobaed_char_id)
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            hp_without_guoba
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .get_characters()
            .just_get_character(guobaed_char_id)
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba but cast elemental skill
        game_state = set_active_player_id(base_game_state, GameState.Pid.P1, 2)
        gsm = GameStateMachine(game_state, p1, p2)
        p1.inject_action(CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTERS,
                    2,
                )
            )
        ))
        p1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.player_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        gsm.player_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            7,
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )

    def test_changing_shifts(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({ChangingShifts: 1})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=ChangingShifts,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(GameState.Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=ChangingShifts,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0})),
        )
        game_state = base_game.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertTrue(
            buffed_game_state.get_player1().get_combat_statuses().contains(ChangingShiftsStatus)
        )

        # test swap with dices fails
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(GameState.Pid.P1, swap_action)
        )

        # test swap with no dices
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0}))
        )
        game_state = buffed_game_state.action_step(GameState.Pid.P1, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(ChangingShiftsStatus)
        )

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(GameState.Pid.P1, EndRoundAction())
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(GameState.Pid.P2, swap_action)
        )

    def test_leave_it_to_me(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({LeaveItToMe: 1})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=LeaveItToMe,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(GameState.Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=LeaveItToMe,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0})),
        )
        game_state = base_game.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertTrue(
            buffed_game_state.get_player1().get_combat_statuses().contains(LeaveItToMeStatus)
        )

        # test swap with no dices fails
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(GameState.Pid.P1, swap_action)
        )

        # test swap with no dices
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1}))
        )
        game_state = buffed_game_state.action_step(GameState.Pid.P1, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(LeaveItToMeStatus)
        )
        self.assertEqual(game_state.get_active_player_id(), GameState.Pid.P1)

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(GameState.Pid.P1, SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        assert game_state is not None
        game_state = auto_step(game_state)
        game_state = game_state.action_step(GameState.Pid.P2, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertEqual(game_state.get_active_player_id(), GameState.Pid.P1)

    def test_northern_smoked_chicken(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({NorthernSmokedChicken: 2})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=NorthernSmokedChicken,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(GameState.Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    pid=GameState.Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertEqual(
            buffed_game_state
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .just_find(NorthernSmokedChickenStatus)
            .usages,
            1
        )
        self.assertTrue(
            buffed_game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test normal attack with 3 dices fails
        normal_attack_action = SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(GameState.Pid.P1, normal_attack_action)
        )

        # test normal attack with 2 dices pass
        normal_attack_action = SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2}))
        )
        game_state = buffed_game_state.action_step(GameState.Pid.P1, normal_attack_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(NorthernSmokedChickenStatus)
        )

        # test teammate cannot use this
        game_state = buffed_game_state.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(2).build()
            ).build()
        ).build()
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(GameState.Pid.P1, normal_attack_action)  # type: ignore
        )

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(GameState.Pid.P1, EndRoundAction())
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(GameState.Pid.P2, normal_attack_action)
        )

    def test_xudong(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({
                    Xudong: 2,
                    MondstadtHashBrown: 2,
                    SweetMadame: 2,
                })
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=Xudong,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(GameState.Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=Xudong,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.PYRO: 1, Element.GEO: 1})),
        )
        game_state = base_game.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        xudong_support = buffed_game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)

        buffed_game_state = kill_character(buffed_game_state, 1, GameState.Pid.P1, 2)
        buffed_game_state = kill_character(buffed_game_state, 2, GameState.Pid.P1, 2)
        buffed_game_state = kill_character(buffed_game_state, 3, GameState.Pid.P1, 2)

        # test play 0 cost card does not affect Xudong
        card_action = CardAction(
            card=SweetMadame,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    pid=GameState.Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = buffed_game_state.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)
        self.assertTrue(
            game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test play card does benefits from Xudong
        card_action = CardAction(
            card=MondstadtHashBrown,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    pid=GameState.Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = buffed_game_state.action_step(GameState.Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 0)
        self.assertTrue(
            game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test Xudong resets next round
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(EndRoundAction())
        a2.inject_action(EndRoundAction())
        gsm.player_step()  # P1 end
        gsm.player_step()  # P2 end
        gsm.auto_step()  # go through end phase
        game_state = gsm.get_game_state()
        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)
