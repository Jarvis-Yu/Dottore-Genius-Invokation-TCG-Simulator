import unittest

from .common_imports import *

class TestElementalArtifacts(unittest.TestCase):
    def test_basic_artifacts(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ThunderSummonersCrown: 7,  # Electro -
            WitchsScorchingHat: 1,   # Pyro -
            ThunderingPenance: 1,  # Keqing's Talent Equipment Card
        }))
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = grant_all_thick_shield(base_state)

        # 1 test any is reduced when elem cannot
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=WitchsScorchingHat,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 1, Element.CRYO: 1}),
            ),
        ))

        self.assertRaises(Exception, lambda: step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.CRYO: 1}),
        ))
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            dice=ActualDice({Element.ELECTRO: 1, Element.CRYO: 1}),
        )

        # 1.1 test discount is once per round and teammate's cannot take effect
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderSummonersCrown,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.ANEMO: 1, Element.CRYO: 1}),
            ),
        ))
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            dice=ActualDice({Element.ELECTRO: 1, Element.CRYO: 2}),
        )

        # 2 test electro dice required is reduced when skill is casted
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderSummonersCrown,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.ANEMO: 1, Element.CRYO: 1}),
            ),
        ))
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 2}),
        )

        # 2.1 test talent card is also discounted
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderSummonersCrown,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.DENDRO: 1, Element.GEO: 1}),
            ),
        ))
        game_state = step_swap(game_state, Pid.P1, 3)
        assert LightningStiletto in game_state.player1.hand_cards
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LightningStiletto,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 2})),
        ))

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderSummonersCrown,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.ELECTRO: 1, Element.HYDRO: 1}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderingPenance,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 2})),
        ))

        # 2.2 Discount refreshes after round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 2}),
        )

    def test_advanced_artifacts(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ThunderingFury: 1,  # Electro
            CrimsonWitchOfFlames: 2,   # Pyro
        }))

        # test roll phase init dice gets collapsed to elements of artifact
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderingFury,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.ANEMO: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CrimsonWitchOfFlames,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.ANEMO: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CrimsonWitchOfFlames,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice({Element.ANEMO: 2}),
            ),
        ))
        game_state = end_round(game_state, Pid.P1)
        p1_dice = game_state.player1.dice
        self.assertGreaterEqual(p1_dice[Element.ELECTRO], 2)
        self.assertGreaterEqual(p1_dice[Element.PYRO], 4)
