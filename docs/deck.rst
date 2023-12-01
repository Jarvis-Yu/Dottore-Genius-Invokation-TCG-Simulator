Deck
====

.. code-block:: python3

    from dgisim import Deck, FrozenDeck, MutableDeck

``__eq__`` is implemented so that two decks are equal if they have the same
data.

.. autoclass:: dgisim.deck.Deck
    :members:

Usage Example
-------------

.. code-block:: python3

    from dgisim import FrozenDeck, MutableDeck, HashableDict
    from dgisim import char
    from dgisim import card

    deck1 = FrozenDeck(
        chars = (char.Bennett, char.Klee, char.Keqing),
        cards = HashableDict({
            card.TeyvatFriedEgg: 2,
            card.TandooriRoastChicken: 2,
            card.LotusFlowerCrisp: 2,
        }),
    )

    deck2 = MutableDeck(
        chars = [char.Bennett, char.Klee, char.Keqing],
        cards = {
            card.TeyvatFriedEgg: 2,
            card.TandooriRoastChicken: 2,
            card.LotusFlowerCrisp: 2,
        },
    )
