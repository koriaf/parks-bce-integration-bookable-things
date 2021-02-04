Spaces
======

Spaces list
-----------

.. http:get:: /spaces/

  .. code-block:: gherkin

    As a user
    I'd like to get detailed information about spaces
    Which products may be linked to
    So I'm aware of these physical aspects

Response example::

  {
      "count": 1,
      "next": None,
      "previous": None,
      "results": [
        {
          "name": "The viewing platform",
          "park": "uluru",
          "short_description": "A platform which offers beautiful view on the object",
          "created_by_org": "Entry Station",
          "created_at": "iso format datetime with timezone",
          "id": "UUID of the space",
          "image": "",
          "visible_to_orgs": "org name 1,org name 2, org name 3",
          "is_indoor": False,
          "is_public": True,
          "unit": "group",
          "max_units": 1
        }
      ]
  }

Fields::

  * ``created_by_org`` - any space has the owner, usually it's park own organisations
  * ``visible_to_orgs`` - in case of non-public spaces only set list of organisations + the owner see it
  * ``is_indoor`` is just an informational field
  * ``unit`` and ``max_units`` work the same way as in products and slots.


Space reservations list
-----------------------

.. http:get:: /spaces/{space_id}/reservations/

  .. code-block:: gherkin

    As a user
    I'd like to get the information about space reservation calendar
    To be aware when it's busy and when it's not

Filters::

  * GET parameters ``from`` and ``until`` like the reservations list endpoint

Response example::

    [
      {
        "space_reservation_id": "uuid",
        "product_reservation_id": "uuid (another)",
        "start_time": "iso datetime",
        "end_time": "iso datetime",
        "units": 3
      },
      ...
    ]
