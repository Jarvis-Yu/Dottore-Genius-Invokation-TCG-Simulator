Player Agent
============

Player Agent
------------

.. code-block:: python3

    from dgisim import PlayerAgent

.. autoclass:: dgisim.player_agent.PlayerAgent
    :show-inheritance:
    :members:

Implemented Agents
------------------

.. code-block:: python3

    from dgisim.agents import RandomAgent, LazyAgent  # ...

A number of agents are implemented in ``dgisim``.

.. automodule:: dgisim.agents

    .. autoclass:: LazyAgent
        :show-inheritance:
    
    .. autoclass:: RandomAgent
        :show-inheritance:

    .. autoclass:: PuppetAgent
        :show-inheritance:
        :exclude-members: choose_action
        :members:

        .. automethod:: __init__

    .. autoclass:: NoneAgent
        :show-inheritance:
