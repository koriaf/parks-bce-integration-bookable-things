Products
========

Interesting fields are:

* ``type`` - is the product offered by the official park organisation or an external partner. Informational
* ``unit`` - has possible values "person" or "group" and helps to display on what basis the reservations are accepted. Avaiability slots (see far below) can have maximal units per reservation parameter be set (for example, 15 people or 2 groups can attend some event).
* ``cost_per_unit`` - informational field, AUD per single unit. Decimal of format "xxxx.xx". This is the current value. Clients must consider ``price_schedule`` if they are placing reservations for far future because price may change.
* ``price_schedule`` - dict of format 2021-02-04: 00.00, where first date is the first day (server timezone) when the new price is actual. Once this day comes the 'cost per unit' field is updated automatically and the row is removed. All rows in this dict relfect the future states, the current one is available as ``cost_per_init``.
* ``available_to_agents`` (boolean) - can another organisation place reservations? Set to False if you want to (temporary) stop accepting new reservations. The product remains visible in the list, but no slots are returned. Existing reservations are not affected by changing this flag.
* ``available_to_public`` (boolean) - the same logic, but has no meaning while we don't offer the API to public. In the future we may have public information about product availability (calendar) and things like that. Personal data of agents placing reservations will not be shared.
* ``spaces_required`` - contains list (possibly empty) of spaces which are booked for each reservation for this product; having the space busy (no more free units for the reservation period) stops the reservation placement process. See spaces list endpoint for getting their list with readable name and some details.

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
          "cost_per_unit": "6.00",
          "price_schedule": {
            "2025-01-01": "7",
            "2030-01-01": "8.00",
          }
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
          "cost_per_unit": "21.00",
          "price_schedule": {},
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
        "cost_per_unit": "55.00",
        "image": "(full image url goes here - see notes",
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

  Returns the same response format as the previous endpoint
  but for the single object.


Product update
--------------

.. http:patch:: /products/(product_id)/

  Payload: set of non-readonly fields (like "short_description")

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
