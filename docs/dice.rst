Dice
====

``Dice`` is an abstraction for dice in the game.
It has two subclasses ``ActualDice`` and ``AbstractDice``.

* ``ActualDice`` represents the dice that can be held by a player.
* ``AbstractDice`` represents the dice-cost of different actions.

Dice Class
----------

.. code-block:: python3

    from dgisim import Dice

.. autoclass:: dgisim.dice.Dice
    :members:

    .. autoattribute:: _LEGAL_ELEMS

        If you want to customize your legal elements, override this attribute
        in your subclass of ``Dice``.

    .. automethod:: __init__

In additional to the methods listed above, ``Dice`` overrides some magic methods
for better experience.

.. code-block:: python3

    from dgisim import Dice, Element

    # Note that Element.PIERCING is illegal in Dice
    dice1 = Dice({Element.PYRO: 3, Element.ANY: 2, Element.OMNI: 0, Element.PIERCING: 5})
    dice2 = Dice({Element.PYRO: 1, Element.GEO: 2})
    
    # in (__contains__)
    print(Element.ANY in dice1)       # True
    print(Element.OMNI in dice1)      # False, because there's <= 0 OMNI in dice1
    print(Element.PIERCING in dice1)  # False, because PIERCING is illegal in dice1

    # in (__iter__)
    for elem in dice1:
        # only elements with a positive number are iterated
        print(elem)  # Element

    # [] (__getitem__)
    print(dice1[Element.OMNI])      # 0
    print(dice1[Element.PIERCING])  # 5
    print(dice1[Element.HYDRO])     # 0

    # +, - (__add__, __sub__)
    print(dice1 + dice2) # {PYRO: 4, ANY: 2, OMNI: 0, PIERCING: 5, GEO: 2}
    print(dice1 - dice2) # {PYRO: 2, ANY: 2, OMNI: 0, PIERCING: 5, GEO: -2}
    print(dice1 - {Element.PYRO: 3, Element.OMNI: 1})  # {PYRO: 1, ANY: 2, OMNI: -1, PIERCING: 5}

ActualDice Class
----------------

.. code-block:: python3

    from dgisim import ActualDice

.. autoclass:: dgisim.dice.ActualDice
    :show-inheritance:
    :members:

    .. autoattribute:: _LEGAL_ELEMS

AbstractDice Class
------------------

.. code-block:: python3

    from dgisim import AbstractDice

.. autoclass:: dgisim.dice.AbstractDice
    :show-inheritance:
    :members:

    .. autoattribute:: _LEGAL_ELEMS
