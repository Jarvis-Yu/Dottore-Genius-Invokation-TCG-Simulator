import unittest

from src.tests.test_characters.common_imports import *


class TestLayla(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Layla,
        char_id=2,
        card=LightsRemit,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.PYRO: 1, Element.GEO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 0)
        self.assertIn(CurtainOfSlumberStatus, game_state.player1.combat_statuses)
        curtain = game_state.player1.combat_statuses.just_find(CurtainOfSlumberStatus)
        self.assertEqual(curtain.usages, 2)
        self.assertIn(ShootingStarStatus, game_state.player1.combat_statuses)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 1)

    def test_elemental_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(CelestialDreamsphereSummon, game_state.player1.summons)
        celestial_summon = game_state.player1.summons.just_find(CelestialDreamsphereSummon)
        self.assertEqual(celestial_summon.usages, 2)

    def test_curtain_of_slumber_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = AddCombatStatusEffect(Pid.P1, CurtainOfSlumberStatus).execute(game_state)

        # 1 physical damage blocked
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, pid=Pid.P1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 0)
        self.assertIn(CurtainOfSlumberStatus, game_state.player1.combat_statuses)
        curtain = game_state.player1.combat_statuses.just_find(CurtainOfSlumberStatus)
        self.assertEqual(curtain.usages, 1)
        
        # next 2 physical damage -1
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, pid=Pid.P1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertNotIn(CurtainOfSlumberStatus, game_state.player1.combat_statuses)

    def test_shooting_star_status(self):
        game_state = grant_all_infinite_revival(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = AddCombatStatusEffect(Pid.P1, ShootingStarStatus).execute(game_state)

        # self skill +1 usages
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 1)

        # opponent skill has no effect
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 1)

        # self (Layla) skill2 +3 usages, but reached 4, so triggers DMG
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 0)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)

        # double check Layla skill +3 usages
        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 3)

        # check teammate skill can also trigger
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 0)

        # check exceeded usages are kept
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 2)

    def test_celestial_dreamsphere_summon(self):
        game_state = AddSummonEffect(Pid.P1, CelestialDreamsphereSummon).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        
        # it deals damage as normal without adding ShootingStarStatus when it's not present
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(CelestialDreamsphereSummon, game_state.player1.summons)
        celestial_dreamsphere = game_state.player1.summons.just_find(CelestialDreamsphereSummon)
        self.assertEqual(celestial_dreamsphere.usages, 1)
        self.assertNotIn(ShootingStarStatus, game_state.player1.combat_statuses)

        # it adds 1 usage for ShootingStarStatus when it is present
        game_state = AddCombatStatusEffect(Pid.P1, ShootingStarStatus).execute(game_state)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 0)
        game_state = next_round(game_state)
        self.assertNotIn(CelestialDreamsphereSummon, game_state.player1.summons)
        self.assertIn(ShootingStarStatus, game_state.player1.combat_statuses)
        shooting_star = game_state.player1.combat_statuses.just_find(ShootingStarStatus)
        self.assertEqual(shooting_star.usages, 1)

    def test_talent_card(self):
        game_state = end_round(self.BASE_GAME, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LightsRemit,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3})),
        ))
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({Paimon: 3}))

        # increase usages to 4, and find ShootingStar draws a card
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(game_state.player1.hand_cards, Cards({Paimon: 1}))
