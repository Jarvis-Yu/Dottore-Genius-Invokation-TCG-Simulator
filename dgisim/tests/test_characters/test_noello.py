import unittest

from dgisim.tests.test_characters.common_imports import *


class TestNoelle(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Noelle.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(IGotYourBack)
        ).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Noelle

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        game_state = oppo_aura_elem(self.BASE_GAME, Element.ELECTRO)
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(FullPlateStatus, p1.get_combat_statuses())
        self.assertIn(CrystallizeStatus, p1.get_combat_statuses())
        self.assertEqual(
            p1.get_combat_statuses().just_find(FullPlateStatus).usages,
            2
        )

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = oppo_aura_elem(game_state, Element.PYRO)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            ActualDice({Element.OMNI: 4}),
        )

        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(CrystallizeStatus, p1.get_combat_statuses())
        self.assertIn(SweepingTimeStatus, p1ac.get_character_statuses())
        burst_status = p1ac.get_character_statuses().just_find(SweepingTimeStatus)
        self.assertEqual(burst_status.usages, 2)

    def test_full_plate_status(self):
        base_state = AddCombatStatusEffect(Pid.P1, FullPlateStatus).execute(self.BASE_GAME)

        from math import ceil
        for dmg_amount in range(1, 8):
            with self.subTest(dmg_amount=dmg_amount):
                game_state = add_damage_effect(base_state, dmg_amount, Element.PHYSICAL, Pid.P1)
                game_state = auto_step(game_state)

                p1 = game_state.get_player1()
                p1ac = p1.just_get_active_character()
                actual_dmg = ceil(dmg_amount / 2)
                post_shield_dmg = max(0, actual_dmg - 2)
                self.assertEqual(p1ac.get_hp(), 10 - post_shield_dmg)
                if actual_dmg >= 2:
                    self.assertNotIn(FullPlateStatus, p1.get_combat_statuses())
                else:
                    self.assertIn(FullPlateStatus, p1.get_combat_statuses())
                    self.assertEqual(
                        p1.get_combat_statuses().just_find(FullPlateStatus).usages,
                        2 - actual_dmg
                    )

    def test_sweeping_time_status(self):
        base_state = AddCharacterStatusEffect(
            StaticTarget(Pid.P1, Zone.CHARACTERS, 2), SweepingTimeStatus
        ).execute(self.BASE_GAME)

        # test cost deduction (if no exception then pass)
        game_state = step_skill(
            base_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.PYRO: 1, Element.CRYO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.DENDRO: 1, Element.ANEMO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 2)

        # test next round as well
        game_state = next_round(game_state)
        p1ac_character_statuses = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertIn(SweepingTimeStatus, p1ac_character_statuses)
        self.assertEqual(p1ac_character_statuses.just_find(SweepingTimeStatus).usages, 1)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = fill_dice_with_omni(game_state)
        game_state = kill_character(game_state, character_id=1, hp=10)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 2}),
        )
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 3}),
        )

        # disappears eventually after two rounds
        game_state = next_round(game_state)
        p1ac_character_statuses = \
            game_state.get_player1().just_get_active_character().get_character_statuses()
        self.assertNotIn(SweepingTimeStatus, p1ac_character_statuses)

    def test_talent_card(self):
        game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_characters(
                    lambda chars: tuple(
                        char.factory().hp(5).build()
                        for char in chars
                    )
                ).build()
            ).build()
        ).build()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=IGotYourBack,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        # first normal attack heals with shield on
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_cs = game_state.get_player1().get_characters()
        for char in p1_cs:
            self.assertEqual(char.get_hp(), 6)

        # second normal attack doesn't heal
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_cs = game_state.get_player1().get_characters()
        for char in p1_cs:
            self.assertEqual(char.get_hp(), 6)

        # healing is back the next round
        game_state = next_round(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = fill_dice_with_omni(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_cs = game_state.get_player1().get_characters()
        for char in p1_cs:
            self.assertEqual(char.get_hp(), 7)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_cs = game_state.get_player1().get_characters()
        for char in p1_cs:
            self.assertEqual(char.get_hp(), 7)

        # healing doesn't work without the shield
        game_state = next_round(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = fill_dice_with_omni(game_state)
        game_state = auto_step(add_damage_effect(game_state, 2, Element.ELECTRO, Pid.P1, char_id=2))
        game_state = kill_character(game_state, character_id=1, hp=10)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1_cs = game_state.get_player1().get_characters()
        for char in p1_cs:
            self.assertEqual(char.get_hp(), 7)
