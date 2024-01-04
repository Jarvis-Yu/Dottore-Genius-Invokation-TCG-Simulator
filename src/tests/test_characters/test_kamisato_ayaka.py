import unittest

from src.tests.test_characters.common_imports import *


class TestKamisatoAyaka(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        KamisatoAyaka,
        char_id=2,
        card=KantenSenmyouBlessing,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
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
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.CRYO)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(FrostflakeSekiNoToSummon, game_state.player1.summons)

    def test_kamisato_art_senho_status_on_start(self):
        # create random game state with Ayaka
        game_state = GameState.from_default()
        if KamisatoAyaka not in game_state.player1.characters:
            game_state = game_state.factory().f_player1(
                lambda p1: p1.factory().f_characters(
                    lambda chars: chars.factory().character(
                        KamisatoAyaka.from_default(id=1),
                    ).build()
                ).build()
            ).build()
        ayaka_id = just(game_state.player1.characters.find_first_character(KamisatoAyaka)).id
        game_state = auto_step(game_state)

        game_state = step_action(game_state, Pid.P1, CardsSelectAction(selected_cards=Cards({})))
        game_state = step_action(game_state, Pid.P2, CardsSelectAction(selected_cards=Cards({})))
        game_state = step_action(game_state, Pid.P1, CharacterSelectAction(char_id=ayaka_id))
        game_state = step_action(game_state, Pid.P2, CharacterSelectAction(char_id=1))
        self.assertIn(KamisatoAyakaCryoInfusionStatus, p1_active_char(game_state).character_statuses)

    def test_kamisato_art_senho_status_on_action_phase(self):
        game_state = silent_fast_swap(self.BASE_GAME, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P1, 2)
        self.assertIn(KamisatoAyakaCryoInfusionStatus, p1_active_char(game_state).character_statuses)

    def test_talent_card(self):
        base_state =  replace_character_make_active_add_card(
            ACTION_TEMPLATE,
            Pid.P1,
            KamisatoAyaka,
            char_id=2,
            card=KantenSenmyouBlessing,
        )
        
        # test card is not combat action and can be used to non-active character
        game_state = silent_fast_swap(base_state, Pid.P1, 1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=KantenSenmyouBlessing,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(base_state, Pid.P1),
                dice=ActualDice({Element.CRYO: 2}),
            ),
        ))
        self.assertIs(game_state.waiting_for(), Pid.P1)

        # test swap to ayaka only now has cost reduction
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 3, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=0)
        game_state = step_swap(game_state, Pid.P1, 3, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
        game_state = step_swap(game_state, Pid.P1, 3)

        # test cost reduction resets after round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 1, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=0)
        game_state = step_swap(game_state, Pid.P1, 3, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
        game_state = step_swap(game_state, Pid.P1, 1)

        # test generates infusion status correctly
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        self.assertNotIn(
            KamisatoAyakaCryoInfusionEnhancedStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )
        game_state = step_swap(game_state, Pid.P1, 2, cost=0)
        self.assertIn(
            KamisatoAyakaCryoInfusionEnhancedStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )
        game_state = step_swap(game_state, Pid.P1, 1)

        # test removes non-talent infusion status
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=KamisatoAyakaCryoInfusionStatus,
        ).execute(game_state)
        self.assertIn(
            KamisatoAyakaCryoInfusionStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )
        self.assertNotIn(
            KamisatoAyakaCryoInfusionEnhancedStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )
        game_state = step_swap(game_state, Pid.P1, 2, cost=0)
        self.assertNotIn(
            KamisatoAyakaCryoInfusionStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )
        self.assertIn(
            KamisatoAyakaCryoInfusionEnhancedStatus,
            just(game_state.player1.characters.get_character(2)).character_statuses,
        )

    def test_kamisato_ayaka_cryo_infusion_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = recharge_energy_for_all(game_state)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P1),
            status=KamisatoAyakaCryoInfusionStatus,
        ).execute(game_state)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.CRYO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.CRYO)

    def test_kamisato_ayaka_cryo_infusion_enhanced_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = recharge_energy_for_all(game_state)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P1),
            status=KamisatoAyakaCryoInfusionEnhancedStatus,
        ).execute(game_state)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.CRYO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.CRYO)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)
        self.assertIs(dmg.element, Element.CRYO)

        # double check summon doesn't get boosted
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)

    def test_frost_flake_seki_no_to_summon(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = AddSummonEffect(Pid.P1, FrostflakeSekiNoToSummon).execute(game_state)
        summon = game_state.player1.summons.just_find(FrostflakeSekiNoToSummon)
        self.assertEqual(summon.usages, 2)

        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)
        summon = game_state.player1.summons.just_find(FrostflakeSekiNoToSummon)
        self.assertEqual(summon.usages, 1)

        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertNotIn(FrostflakeSekiNoToSummon, game_state.player1.summons)
