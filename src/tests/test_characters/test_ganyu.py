import unittest

from src.tests.test_characters.common_imports import *


class TestGanyu(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Ganyu,
        char_id=2,
        card=UndividedHeart,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Ganyu

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill1 deals 1 cryo damage and creates ice lotus status
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertIn(IceLotusStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(IceLotusStatus).usages, 2)

    def test_elemental_skill2(self):
        # test elemental skill2 deals 2 cryo damage and 2 piercing to off fields
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL3,
            dice=ActualDice({Element.CRYO: 5}),
        )
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 8)
        self.assertEqual(p2c3.hp, 8)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

        # test skill2 is treated as normal attack
        game_state = PublicAddCardEffect(Pid.P1, JueyunGuoba).execute(game_state)
        game_state = AddCombatStatusEffect(Pid.P1, RainbowBladeworkStatus).execute(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=JueyunGuoba,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget.from_player_active(game_state, Pid.P1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 3)  # skill 2 + guoba 1 + rainbow 1 + frozen 1

    def test_elemental_burst(self):
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertIn(SacredCryoPearlSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SacredCryoPearlSummon).usages, 2)

    def test_ice_lotus_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, IceLotusStatus).execute(self.BASE_GAME)
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, pid=Pid.P1)
        p1 = game_state.player1
        p1ac = p1.just_get_active_character()
        self.assertEqual(p1ac.hp, 9)
        self.assertIn(IceLotusStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(IceLotusStatus).usages, 1)

        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, pid=Pid.P1)
        p1 = game_state.player1
        p1ac = p1.just_get_active_character()
        self.assertEqual(p1ac.hp, 8)
        self.assertNotIn(IceLotusStatus, p1.combat_statuses)

    def test_sacred_cryo_pearl_summon(self):
        game_state = AddSummonEffect(Pid.P1, SacredCryoPearlSummon).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 9)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertIn(SacredCryoPearlSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SacredCryoPearlSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 8)
        self.assertEqual(p2c3.hp, 8)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertNotIn(SacredCryoPearlSummon, p1.summons)

    def test_talent_card(self):
        # test early equip
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=UndividedHeart,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 5}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 8)
        self.assertEqual(p2c3.hp, 8)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 5)
        self.assertEqual(p2c3.hp, 5)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

        game_state = next_round(game_state)
        game_state = fill_dice_with_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 4)
        self.assertEqual(p2c2.hp, 2)
        self.assertEqual(p2c3.hp, 2)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

        # test late equip
        game_state = step_skill(self.BASE_GAME, Pid.P1, CharacterSkill.SKILL3)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 8)
        self.assertEqual(p2c3.hp, 8)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=UndividedHeart,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 5}))
        ))
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 5)
        self.assertEqual(p2c3.hp, 5)
        self.assertIn(Element.CRYO, p2c1.elemental_aura)
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
