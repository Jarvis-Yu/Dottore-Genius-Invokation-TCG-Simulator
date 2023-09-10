import unittest

from dgisim.tests.test_characters.common_imports import *


class TestGanyu(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Ganyu,
        char_id=2,
        card=UndividedHeart,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Ganyu

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dices=ActualDices({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill1 deals 1 cryo damage and creates ice lotus status
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dices=ActualDices({Element.CRYO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.CRYO, p2ac.get_elemental_aura())
        self.assertIn(IceLotusStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(IceLotusStatus).usages, 2)

    def test_elemental_skill2(self):
        # test elemental skill2 deals 2 cryo damage and 2 piercing to off fields
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL3,
            dices=ActualDices({Element.CRYO: 5}),
        )
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 8)
        self.assertEqual(p2c2.get_hp(), 8)
        self.assertEqual(p2c3.get_hp(), 8)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

        # test skill2 is treated as normal attack
        game_state = PublicAddCardEffect(Pid.P1, JueyunGuoba).execute(game_state)
        game_state = AddCombatStatusEffect(Pid.P1, RainbowBladeworkStatus).execute(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget.from_player_active(game_state, Pid.P1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 3)  # skill 2 + guoba 1 + rainbow 1 + frozen 1

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dices=ActualDices({Element.CRYO: 3}),
        )
        p1 = game_state.get_player1()
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 8)
        self.assertEqual(p2c2.get_hp(), 9)
        self.assertEqual(p2c3.get_hp(), 9)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())
        self.assertIn(SacredCryoPearlSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(SacredCryoPearlSummon).usages, 2)

    def test_ice_lotus_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, IceLotusStatus).execute(self.BASE_GAME)
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, pid=Pid.P1)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 9)
        self.assertIn(IceLotusStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(IceLotusStatus).usages, 1)

        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, pid=Pid.P1)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 8)
        self.assertNotIn(IceLotusStatus, p1.get_combat_statuses())

    def test_sacred_cryo_pearl_summon(self):
        game_state = AddSummonEffect(Pid.P1, SacredCryoPearlSummon).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 9)
        self.assertEqual(p2c2.get_hp(), 9)
        self.assertEqual(p2c3.get_hp(), 9)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())
        self.assertIn(SacredCryoPearlSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(SacredCryoPearlSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 8)
        self.assertEqual(p2c2.get_hp(), 8)
        self.assertEqual(p2c3.get_hp(), 8)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())
        self.assertNotIn(SacredCryoPearlSummon, p1.get_summons())

    def test_talent_card(self):
        # test early equip
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=UndividedHeart,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.CRYO: 5}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 8)
        self.assertEqual(p2c2.get_hp(), 8)
        self.assertEqual(p2c3.get_hp(), 8)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 6)
        self.assertEqual(p2c2.get_hp(), 5)
        self.assertEqual(p2c3.get_hp(), 5)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

        game_state = next_round(game_state)
        game_state = fill_dices_with_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 4)
        self.assertEqual(p2c2.get_hp(), 2)
        self.assertEqual(p2c3.get_hp(), 2)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

        # test late equip
        game_state = step_skill(self.BASE_GAME, Pid.P1, CharacterSkill.SKILL3)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 8)
        self.assertEqual(p2c2.get_hp(), 8)
        self.assertEqual(p2c3.get_hp(), 8)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=UndividedHeart,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.CRYO: 5}))
        ))
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 6)
        self.assertEqual(p2c2.get_hp(), 5)
        self.assertEqual(p2c3.get_hp(), 5)
        self.assertIn(Element.CRYO, p2c1.get_elemental_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())
