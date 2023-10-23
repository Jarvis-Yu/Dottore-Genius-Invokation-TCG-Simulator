Deck
====

.. code-block:: python3

    from dgisim import Deck, MutableDeck, FrozenDeck

A data structure for a deck. A deck contains a sequence of characters and a
dictionary of cards.

.. autoclass:: dgisim.deck.Deck
    :members:
    :undoc-members:

.. autoclass:: dgisim.deck.MutableDeck
    :show-inheritance:
    :members:
    
    .. autoattribute:: cards
    .. autoattribute:: chars

.. autoclass:: dgisim.deck.FrozenDeck
    :show-inheritance:
    :members:
    
    .. autoattribute:: cards
    .. autoattribute:: chars
