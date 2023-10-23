Status, Summon and Support
==========================

.. code-block:: python3

    from dgisim import Status, Summon, Support

``Status`` is the superclass of ``Summon`` and ``Support``.

``Status`` is used to implement all statuses in the game, character statuses,
combat statuses...

``Summon`` and ``Support``, as their names suggest, corresponds to the implementation
of summons and supports.

The way how each individual status (summon or support) is implemented can be vastly
different to each other, please check the source code for more information.

For simple usages, you only need to access the attributes of each status without
calling any methods.

.. autoclass:: dgisim.status.status.Status
    :members:

.. autoclass:: dgisim.summon.summon.Summon
    :show-inheritance:
    :members:

.. autoclass:: dgisim.support.support.Support
    :show-inheritance:
    :members:

The implementations of ``Status``, ``Summon`` and ``Support`` could be imported
from:

.. code-block:: python3

    from dgisim.status import *
    from dgisim.summon import *
    from dgisim.support import *

There are too many statuses implemented, so the details will not be elaborated here.
Please refer to the source code for more information.
