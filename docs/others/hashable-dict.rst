Hashable Dict
=============

.. code-block:: python3

    from dgisim import HashableDict

.. autoclass:: dgisim.helper.hashable_dict.HashableDict
    :show-inheritance:
    :members:

Examples of some operations

.. code-block:: python3

    from dgisim import HashableDict

    dict1 = HashableDict((('a', 0), ('b', 1)))
    dict2 = HashableDict({'c': 0, 'b': 1})

    assert dict1 == dict2
    assert hash(dict1) == hash(dict2)
    assert dict1 + dict2 == HashableDict({'b': 2})
    assert dict1 - dict2 == HashableDict(())
