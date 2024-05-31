Encoding Plan
=============

.. code-block:: python3

    from dgisim import EncodingPlan

``EncodingPlan`` is a class defining how to encode a game.

.. autoclass:: dgisim.encoding.encoding_plan.EncodingPlan
    :members:

    .. automethod:: __init__

``EncodingPlanFast`` is a subclass of ``EncodingPlan`` whose ``encode`` would always return None.

.. autoclass:: dgisim.encoding.encoding_plan.EncodingPlanFast
    .. automethod:: encode