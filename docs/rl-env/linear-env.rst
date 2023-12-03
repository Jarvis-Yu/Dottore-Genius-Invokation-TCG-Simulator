Linear Env
==========

.. code-block:: python3

    from dgisim import LinearEnv

``LinearEnv`` is a simple RL enviroment that can take an action and return the
reward and the resulting game state.

An example of a simple set up is.

.. code-block:: python3

    from dgisim import LinearEnv

    env = LinearEnv()
    rl_net = ...  # your RL network

    for _ in range(100):
        env.reset()
        game_state, encoded_state, reward, turn, done = env.view()

        while not done:
            action = rl_net(encoded_state)  # this is just an example, your network
                                            # doesn't have to directly generate an action
            game_state, encoded_state, reward, turn, done = env.step(action)

.. autoclass:: dgisim.env.linear_env.LinearEnv
    :members:
    :undoc-members:
