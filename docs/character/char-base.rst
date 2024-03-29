Character
=========

``Character`` class is the base of all implemented characters.

``__eq__`` and ``__hash__`` are implemented so that any two characters with the
equivalent content are equal to each other and have the same hash.

.. code-block:: python3

    from dgisim import Character

.. autoclass:: dgisim.character.character.Character
    :members:
    :exclude-members: factory

    .. automethod:: __init__
    .. automethod:: factory

        The factory allows modifications to the existing a copy of the origial
        character to produce a new one.

        You may call ``.<attribute-name>(new_val)`` to replace the current value.

        Or call ``.f_<attribute-name>(<function>)`` to make modifications based
        on the current value.

        e.g. ``character.factory().f_hp(lambda h: h - 1).alive(False).build()``
        returns a new character with 1 less hp and marked defeated.

.. Private Class Properties
.. ------------------------

.. Private class properties can be handy when you inherit the ``Character`` class
.. and define your new character class.

.. ``_ELEMENT: Element``
.. ^^^^^^^^^^^^^^^^^^^^^

.. The element of the character.

.. e.g. the element of Keqing is Electro, the element of Maguu Kenki is Anemo...

.. ``_WEAPON_TYPE: WeaponType``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The type of weapon a character uses.

.. ``_TALENT_STATUS: None | type[TalentEquipmentStatus]``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The talent status of the character.

.. e.g. the talent status of Sangonomiya Kokomi is ``TamakushiCasketStatus``;
.. the talent status of Electro Hypostasis is ``None``.

.. ``_FACTIONS: frozenset[Faction]``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The factions a character belongs to.

.. ``_SKILL1_COST: None | AbstractDice``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The dice cost of the skill 1 of the character. Value default to ``None``.

.. ``None`` here means the character doesn't have a defined skill1.

.. Skill *n* is the *nth* skill counting from left to right in the official TCG
.. game. (excluding the elemental burst)

.. ``_SKILL2_COST: None | AbstractDice``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The dice cost of the skill 2 of the character. Value default to ``None``.

.. ``_SKILL3_COST: None | AbstractDice``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The dice cost of the skill 3 of the character. Value default to ``None``.

.. ``_ELEMENTAL_BURST_COST: None | AbstractDice``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The dice cost of the elemental burst of the character. Value default to ``None``.

.. ``_SKILL1_ACTUAL_TYPE: CharacterSkillType``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The type of skill skill1 is treated as.
.. The default value is ``CharacterSkillType.NORMAL_ATTACK``

.. This property affects what statuses are triggered when a skill is cast.

.. ``_SKILL2_ACTUAL_TYPE: CharacterSkillType``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The type of skill skill2 is treated as.
.. The default value is ``CharacterSkillType.ELEMENTAL_SKILL``

.. ``_SKILL3_ACTUAL_TYPE: CharacterSkillType``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The type of skill skill3 is treated as.
.. The default value is ``CharacterSkillType.ELEMENTAL_SKILL``

.. ``_BURST_ACTUAL_TYPE: CharacterSkillType``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The type of skill elemental burst is treated as.
.. The default value is ``CharacterSkillType.ELEMENTAL_BURST``

.. Private Instance Properties
.. ---------------------------

.. Private instance properties are typically not introduced in documentations,
.. but the introduction of it can greatly help you understand how a character
.. is represented.

.. ``_id: int``
.. ^^^^^^^^^^^^

.. The unique id for a character of a player.

.. Typically, characters of different players can share the same id.
.. For each player, when its deck has *n* characters,
.. the characters get id *1 to n* from left to right.

.. ``_alive: bool``
.. ^^^^^^^^^^^^^^^^

.. The boolean value indicating if the character is actually dead or not.

.. Within the same skill, if the *next character* of the opponent is defeated first,
.. then an **overloaded** happen to the active character,
.. the *next character* who was just defeated could be swapped out to be the active
.. character, even though **overloaded** typically skips the defeated characters.

.. ``_alive`` is used to mark the *about to be actually defeated* characters enabling
.. them to be force swapped out until the effect ``AliveMarkCheckerEffect`` is executed
.. by the game.

.. ``_hp: int``
.. ^^^^^^^^^^^^

.. The current hp of the character.

.. ``_max_hp: int``
.. ^^^^^^^^^^^^^^^^

.. The maximum hp of the character.

.. ``_energy: int``
.. ^^^^^^^^^^^^^^^^

.. The current energy of the character.

.. ``_max_energy: int``
.. ^^^^^^^^^^^^^^^^^^^^

.. The maximum energy of the character.

.. ``_hiddens: Statuses``
.. ^^^^^^^^^^^^^^^^^^^^^^

.. Contains the hidden statuses of the character.

.. e.g. Mona's passive skill is considered a hidden status.

.. Hidden statuses are processed before all other statuses per character.

.. ``_equipments: EquipmentStatuses``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Contains the equipments equipped by the character.

.. e.g. weapons, artifacts, some talent cards.

.. Equipment statuses are executed after hidden statuses.

.. ``_statuses: Statuses``
.. ^^^^^^^^^^^^^^^^^^^^^^^

.. Contains the other statuses of the character.

.. e.g. Noelle's elemental burst status, satiated status, mushroom pizza status...

.. Equipment statuses are executed after equipment statuses.

.. ``_elemental_aura: ElementalAura``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Contains the aura of the character.

.. e.g. if the character is affected by Hydro, then the next Pyro damage
.. to the character is increased by 2.
