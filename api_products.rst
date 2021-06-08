Products
========

Interesting fields are:

* ``type`` - is the product offered by the official park organisation or an external partner. Informational
* ``unit`` - has possible values "person" or "group" and helps to display on what basis the reservations are accepted. Avaiability slots (see far below) can have maximal units per reservation parameter be set (for example, 15 people or 2 groups can attend some event).
* ``available_to_agents`` (boolean) - can another organisation place reservations? Set to False if you want to (temporary) stop accepting new reservations. The product remains visible in the list, but no slots are returned. Existing reservations are not affected by changing this flag.
* ``available_to_public`` (boolean) - the same logic, but has no meaning while we don't offer the API to public. In the future we may have public information about product availability (calendar) and things like that. Personal data of agents placing reservations will not be shared.
* ``spaces_required`` - contains list (possibly empty) of spaces which are booked for each reservation for this product; having the space busy (no more free units for the reservation period) stops the reservation placement process. See spaces list endpoint for getting their list with readable name and some details.

* ``cost_per_unit`` - deprecated informational field, AUD per single unit. Decimal of format "xxxx.xx". This is the current value. Clients must consider ``price_schedule`` if they are placing reservations for far future because price may change.
* ``price_schedule`` - deprecated dict of format 2021-02-04: 00.00, where first date is the first day (server timezone) when the new price is actual. Once this day comes the 'cost per unit' field is updated automatically and the row is removed. All rows in this dict relfect the future states, the current one is available as ``cost_per_unit``.
* ``minimum_units`` deprecated field which doesn't force validation on reservation creation step but affects Reservation.total_cost calculation (the number of units in reservations considered there can't be lower than ``minimum_units`` value for product)


Pricing
-------

Note about product pricing: historically we were using ``cost_per_unit`` but now it's migrated to the new format. Please stop sending these 3 deprecated fields fields and start sending new ones as explained below (old fields are still supported while used). Expected UI is to allow users to select one from 3 pricing types and then, based on choice, show type-specific set of fields. Also, when placing reservation, either request number of people in groups or not (and don't allow number of units more than 1 for group reservations). Old behaviour: if the pricing_info dict is empty old pricing rules are used (multiple units per reservations are allowed and so on)

Currently the pricing is purely informational and API doesn't force any payments made for reservations, but it may change soon.

``pricing_info`` - new field with pricing, must be dict with required fields ``type`` (string ``person|group-simple|group-complex`` and ``multiplyPerSlot`` (bool true|false). There are other fields here but they depend on the type.

* person:
  * product unit must be "person"
  * pricing_info dict contains pricePerPerson decimal value (required but can be 0)
  * ``reservation price = pricing_info.pricePerPerson * units`` and `` * number_of_slots`` if multiplyPerSlot is True. Reservations placed for products with that pricing type can have multiple units.

* group-simple
  * product unit must be "group"
  * pricing_info dict contains pricePerGroup decimal value (required but can be 0)
  * price calculation is the same as "person" but using ``pricePerGroup`` field
  * units per reservation value can only be 1 (reservations for 2 units at the same time are not accepted). It's done so you can provide peopleComing, peopleComingBonus values for each group separately without complicating the API; if you have 2 groups just place 2 reservations.
  * reservations may have peopleComing and peopleComingBonus fields but they are informational
  * product pricing info can have maxPersonsInGroup and maxBonusPersonsInGroup (optional, default null), if positive integer set then don't allow reservations to be placed if peopleComing or peopleComingBonus is bigger than max

* group-complex:
  * product unit must be "group", reservations are placed per single group
  * pricing_info has next extra fields:
    * baseCostPerGroup (decimal, required, can be 0)
    * pricePerPerson (decimal, required, can be 0)
    * pricePerBonusPerson (decimal, required, can be 0)
    * minPersonsInGroup (integer, can be 0 if no limit). This field doesn't stop reservation from being placed in case if fewer persons arriving, but the group will always be billed at least for this number.
    * minBonusPersonsInGroup (integer, can be 0 if no limit, the same rules apply)
    * maxPersonsInGroup (integer, 0 if no limit applied). Doesn't allow to place a reservation for number of people in group more than this.
    * maxBonusPersonsInGroup (integer, 0 if no limit applied). Also stops the reservation from placing if more people reported.
  * reservation fields peopleComing and peopleComingBonus are expected to be sent (minimal values from product pricing are always used if 0/empty)
  * price is equal to baseCostPerGroup (can be 0)
  * plus pricePerPerson * number of persons, where number of persons is either minPersonsInGroup or peopleComing (whatever is bigger) (can be 0)
  * plus pricePerBonusPerson * number of bonus persons, where number of bonus persons is either minBonusPersonsInGroup or peopleComingBonus (whatever is bigger) (can be 0)
  * final price can be multiplied by number of slots if needed


``pricing_info_schedule`` is a list of pairs like ["YYYY-MM-DD", {new-pricing-info}] - once given date arrives the new pricing info replaces current one. Reservations may be re-saved and change their price after that event. Reservations placed in the future consider this field when calculating their price. Please note that if you change price schedule and some already existing reservations are affected it can surprise users.

**Example of price calculation:**

Pricing info:

.. code-block:: json

    {
        "type": "group-complex",
        "multiplyPerSlot": True,
        "baseCostPerGroup": "0.00",
        "pricePerPerson": "10.00",
        "pricePerBonusPerson": "1.00",
        "minPersonsInGroup": 5,
        "minBonusPersonsInGroup": 0,
        "maxPersonsInGroup": 20,
        "maxBonusPersonsInGroup": 1,
    }

Reservation:

.. code-block:: json

    {"units": 1, "extra_data": {"peopleComing": 10, "peopleComingBonus": 1}}

Reservation is placed for 2 slots. Final price: 101.00 * 2 ((10 * 10 + 1 * 1) * 2) = 202.00

Products list
-------------
..for the current organisation

.. code-block:: gherkin

   As a booking agent (like BCE)
   I need to get a list of products visible to me
   so that I can map Spaces to Product Things
   and so that I know what resources to check the availability of

.. code-block:: gherkin

   As a delivering organisation
   I need to get a list of products I created
   so I can manage them:
   * manage slots
   * manage reservations
   * manage products itself


.. uml::

   actor "Delivery Org\nUser" as parks_staff
   box "Booking Agent" #lightblue
      participant "Agent\nSystem" as BCE
   end box
   parks_staff -> BCE: configure products\nfrom the Parks system\nin the agent's system
   box "Parks System" #lightgreen
      boundary "<<API>>\n/parks/{park-slug}/products\n?team={org-slug}" as get_list_products
      database "product\nthings" as product_things
   end box
   BCE -> get_list_products: GET
   get_list_products -> product_things: query_list(\n  park=park-slug,\n  org=team-slug\n)

   get_list_products -> BCE: json data
   BCE -> parks_staff: show options from Parks system
   parks_staff -> BCE: map to products\n(e.g. "spaces")\nin the Agent system

.. http:get:: /products/?org_id=(org_id)&org_slug=(string)&park_slug=(park_slug)&is_archived=true/false/all

  Returns a list of products with pagination and short information about them.

  Optional GET parameters to filter:

    * **park_slug** is an URL-compatible string that identifies the park, e.g. "anbg"
      for the Australian National Botanic Gardens or "kakadu" or "booderee" or "uluru".

    * **org_id** is a short number identifying the organisation to display only
      products provided by the choosen one. It will be useful mostly for
      the "Management" scenario, given any organisation using API is aware of this
      value for itself. See the organisations list endpoint to get variants to filter on or
      configuration endpoint to retrieve ID and name of the current org.

    * **org_name** - full organisation name (urlencoded). Exact case insensitive match.

    * **is_archived** (``false`` by default) - can be used to access archived products
      (if you set it to ``all`` or ``true``). Only active (=false) are returned by default.

  In case of wrong filters parameter (park doesn't exist, org doesn't exist)
  empty results set will be returned (except the is_archived parameter where the value
  is strictly validated to be one of ``all``, ``true`` or ``false``).

  Response example::

    {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 2,
          "type": "park",
          "park": "kakadu",
          "delivery_org": "Bowali",
          "name": "Naidoc Week",
          "short_description": "",
          "image": "http://localhost:8000/media/products_images/ObQOeL8uJqY.jpg",
          "contact": "",
          "unit": "person",
          "cost_per_unit": "6.00", -- deprecated
          "price_schedule": { -- deprecated
            "2025-01-01": "7",
            "2030-01-01": "8.00",
          },
          "pricing_info": {
            "type": "person",
            "multiplyPerSlot": false,
            "pricePerPerson": "40.00",
          },
          "pricing_info_schedule": [],
          "is_archived": false,
          "spaces_required": [
            {
              "space_id": "some-uuid-of-the-space",
              "index": 1,
              "index_percentage": 100,
              "minutes": null,
              "start_from_minutes": 0
            }
          ]
        },
        {
          "id": 1,
          "type": "park",
          "park": "kakadu",
          "delivery_org": "Bowali",
          "name": "Taste of Kakadu\tFestival Opening Night",
          "short_description": "",
          "image": null,
          "contact": "",
          "unit": "person",
          "cost_per_unit": "21.00", -- deprecated
          "minimum_units":null, -- deprecated
          "minimum_minutes":null, -- deprecated
          "maximum_minutes":null, -- deprecated
          "price_schedule": {}, -- deprecated
          "pricing_info": {
            "type": "person",
            "multiplyPerSlot": false,
            "pricePerPerson": "40.00",
          },
          "pricing_info_schedule": [],
          "is_archived": false,
          "spaces_required": [
            {
              "space_id": "some-uuid-of-the-space",
              "index": 1,
              "index_percentage": 100,
              "minutes": null,
              "start_from_minutes": 0
            }
          ]
        }
      ]
    }


Product creation
----------------

.. http:post:: /products/

.. code-block:: gherkin

   As a delivering organisation
   I want to create a "Product Thing"
   so agent organisation can book my time

The current organisation becomes ``delivery_org``. ``customer`` field is mostly ignored in this version.
All fields not listed here are readonly or optional.
Success is 201, error is 4xx (subject to change and specific codes will be used)

Minimal request example::

    {
        "name": "First Product",
        "unit": "person",
        "park": "kakadu"
    }

Full request example::

    {
        "name": "First Product",
        "unit": "person",
        "park": "kakadu",
        "short_description": "night walk",
        "cost_per_unit": "55.00", -- deprecated
        "price_schedule": {the same format as the product list}, -- deprecated
        "pricing_info": {..},
        "pricing_info_schedule": [..],
        "image": "full image url goes here - see notes",
        "spaces_required": [the same format as the product list],
        "time_setup": 0,
        "time_packup": 0,
    }

Success response: the same as the Products list endpoint but without pagination.

Note about the image: it's a text field where you should pass the exact absolute url
what has been returned to you by the image upload endpoint. No other urls will be accepted for security reasons. The field is optional.

The field ``spaces_required`` is optional and once provided will make the system place
space reservations along with the product reservation. Please note that once provided
the busy space will block the reservation creation.

``time_setup`` and ``time_packup`` is used to add buffer times at the beginning/end of each reservation, meaning that no other
activities may be performed for that product for this number of units. So, for example, if you have these values set then
adjacent slots will be automatically blocked (booked indirectly) to display the fact that somebody is doing something
on the spot. If interval between the slots is bigger than setup+packup time then no limits are applied and no indirectly
booked slots are created.

Error response example::

    {"code":"FRS-400","title":"ValidationError","detail":{"name":["This field is required."],"unit":["This field is required."]}}

    {"detail":"JSON parse error - Expecting property name enclosed in double quotes: line 6 column 5 (char 141)"}

    {
      "code": "FRS-400",
      "title": "ValidationError",
      "detail": {
        "non_field_errors": [
          "The fields park, name must make a unique set."
        ]
      }
    }

    {
      "code": "FRS-400",
      "title": "ValidationError",
      "detail": {
        "park": [
          "This park is unknown to this org"
        ]
      }
    }


Product details
---------------

.. http:get:: /products/(product_id)/

  Returns the same response format as the "products list" endpoint
  but for the single object.


Product update
--------------

.. http:patch:: /products/(product_id)/

  Payload: set of non-readonly fields (like "short_description"); see products list endpoint for details

  Returns the same response format as the GET method in case of success (code 200) or
  error message if any happened (code 4xx).

  Please use actual product version before updating and use patch on minimal set of fields
  to avoid overwritting data changed on server (for example cost per unit changed due to the schedule)


Product delete
--------------

.. http:delete:: /products/(product_id)/

  Payload: none.

  Returns: empty response with 204 code or 4xx error message.

  In case of no reservations created the product and all its slots are deleted.
  In case of at least one reservation (including not confirmed) present the product
  is marked as "is_archived" and will not be shown in the products list by default,
  but it's possible to display archived as well. Archived products can't accept any more reservations.


Product image upload
--------------------

This is multipart/form request where you send an image (jpeg or png) file as ``file`` parameter and the next response is returned::

    {
        "url": "https://domain/url/"
    }

After uploaded you can reference the image using the url or put it into the "image"
field on product creation/update.

Please note that images not assigned to products will be removed after 7 days.

Please pass full url including protocol and domain name to the product update/create endpoints. Links to domains/services other than our own are not allowed for security
reasons.

Please keep your files reasonable small (a typical photo from a mobile phone which is 5MB+ big is not a good choice).

The request is authenticated as usual while the image file is available without any auth
after uploaded.

This image may be used for space as well.
