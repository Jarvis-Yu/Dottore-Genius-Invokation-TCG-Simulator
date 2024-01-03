import unittest

from src.package import *
from src.package.agents import RandomAgent
from src.package.card import *
from src.tests.helpers.quality_of_life import *

class TestLinearEnv(unittest.TestCase):
    def test_env(self):
        env = LinearEnv()
        init_game_state, init_state, _, _, _ = env.view()
        game_state, state, reward, turn, done = env.step(
            CardsSelectAction(
                selected_cards=Cards({
                    NorthernSmokedChicken: 1,
                    SweetMadame: 1,
                }),
            )
        )
        self.assertNotEqual(init_game_state, game_state)
        self.assertNotEqual(init_state, state)
        self.assertEqual(len(init_state), len(state))

        self.assertEqual(game_state, env.step(DeathSwapAction(char_id=1))[0])

    def test_through(self):
        agent = RandomAgent()
        env = LinearEnv()
        game_state, _, _, turn, done = env.view()
        rewards: list[int | float] = []
        while not done:
            action = agent.choose_action([game_state], Pid(turn))
            game_state, _, reward, turn, done = env.step(action)
            rewards.append(reward)

        self.assertTrue(all(reward == 0 for reward in rewards[:-1]))

        env.reset_random()
        game_state, _, _, turn, done = env.view()
        while not done:
            action = agent.choose_action([game_state], Pid(turn))
            from random import random
            if random() < 0.2:
                game_state, _, _, turn, done = env.step(action.encoding(encoding_plan))
            else:
                game_state, _, reward, turn, done = env.step(action)

    def test_resets(self):
        # random reset does create some random new initial game state
        env = LinearEnv()
        game_state = env.full_view()
        env.reset_random()
        new_game_state = env.full_view()
        self.assertNotEqual(game_state, new_game_state)

        deck1, deck2 = new_game_state.get_decks()
        env.reset_with_decks(deck1, deck2)
        self.assertEqual(
            env.full_view().get_decks(),
            (deck1, deck2),
        )
