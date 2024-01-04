import unittest

from src.tests.test_characters.common_imports import *


class TestShenhe(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Shenhe.from_default(2)
            ).character(
                Kaeya.from_default(3)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(MysticalAbandon)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Shenhe

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 3}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.OMNI: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 2)

    def test_elemental_burst(self):
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.OMNI: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.summons.just_find(TalismanSpiritSummon).usages, 2)

    def test_icy_quill_status(self):
        base_state = AddCombatStatusEffect(Pid.P1, IcyQuillStatus).execute(self.BASE_GAME)
        base_state = AddCombatStatusEffect(Pid.P1, IcicleStatus).execute(base_state)
        base_state = UpdateCombatStatusEffect(
            Pid.P1, ChonghuasFrostFieldStatus(usages=2)
        ).execute(base_state)
        base_state = AddSummonEffect(Pid.P1, ShadowswordGallopingFrostSummon).execute(base_state)

        # test cryo-infused normal attack gets boost
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 1)

        # Kaeya's burst (not from character)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, char_id=3)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 5)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 1)

        from dataclasses import dataclass
        from typing import ClassVar
        from src.dgisim.status.status import _InfusionStatus

        @dataclass(frozen=True, kw_only=True)
        class AnemoInfusion(CharacterStatus, _InfusionStatus):
            usages: int = 1000
            ELEMENT: ClassVar[Element] = Element.ANEMO

        game_state = AddCharacterStatusEffect(
            StaticTarget(Pid.P1, Zone.CHARACTERS, 3), AnemoInfusion
        ).execute(game_state)

        # test character swirl benefits from IcyQuillStatus
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        self.assertEqual(p2cs.just_get_character(1).hp, 3)
        self.assertEqual(p2cs.just_get_character(2).hp, 8)
        self.assertEqual(p2cs.just_get_character(3).hp, 9)
        self.assertNotIn(IcyQuillStatus, p1.combat_statuses)

        # test that IcyQuillStatus doesn't boost cryo summon
        game_state = AddCombatStatusEffect(Pid.P1, IcyQuillStatus).execute(game_state)
        game_state = next_round(game_state)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)

    def test_talisman_spirit_summon(self):
        base_state = AddSummonEffect(Pid.P1, TalismanSpiritSummon).execute(self.BASE_GAME)
        base_state = AddCombatStatusEffect(Pid.P1, IcicleStatus).execute(base_state)

        # test normal attack gets boost
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertFalse(p2ac.elemental_aura.has_aura())

        # test Kaeya's burst gets buffed
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, char_id=1)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)

        # test summons get buffed
        game_state = next_round(game_state)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 2)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertIn(TalismanSpiritSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(TalismanSpiritSummon).usages, 1)

    def test_talent_card(self):
        base_state = UpdateCombatStatusEffect(
            Pid.P1, ChonghuasFrostFieldStatus(usages=2)
        ).execute(self.BASE_GAME)
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=MysticalAbandon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, char_id=3)  # to Kaeya

        # elemental skill consumes status as normal
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)  # initial Shenhe skill already
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 1)

        # first normal attack is a free boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 1)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 1)

        # second normal attack is not free
        game_state = heal_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertNotIn(IcyQuillStatus, p1.combat_statuses)

        game_state = next_round(game_state)
        game_state = fill_dice_with_omni(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = OverrideCombatStatusEffect(Pid.P1, IcyQuillStatus(usages=1)).execute(game_state)
        # first normal attack is a free boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertEqual(p1.combat_statuses.just_find(IcyQuillStatus).usages, 1)

        # second normal attack is not free
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 1)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertNotIn(IcyQuillStatus, p1.combat_statuses)
