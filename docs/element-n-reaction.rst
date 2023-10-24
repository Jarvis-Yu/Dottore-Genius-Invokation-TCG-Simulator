Element and Reaction
====================

Element
-------

.. code-block:: python3

    from dgisim import Element

.. autoclass:: dgisim.element.Element
    :members:
    :undoc-members:

There are some const values for different groups of elements.
These values can be directly imported from ``dgisim``.

.. autoattribute:: dgisim.element.PURE_ELEMENTS

    Elements of the seven.

.. autoattribute:: dgisim.element.AURA_ELEMENTS

    Elements that are aurable (can be applied to characters).

.. autoattribute:: dgisim.element.AURA_ELEMENTS_ORDERED

    Elements ordered by reaction priority when they are already applied to a character.

Elemental Aura
--------------

.. autoclass:: dgisim.element.ElementalAura
    :members:

Reaction
--------

.. code-block:: python3

    from dgisim import Reaction, ReactionDetail

.. autoclass:: dgisim.element.Reaction
    :members:
    :undoc-members:

.. autoclass:: dgisim.element.ReactionDetail
    :members:
    :undoc-members:
