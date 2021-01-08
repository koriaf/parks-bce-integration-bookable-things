API documentation
=================

This shows how the API is used
by booking Agents (such as BCE)
to create and manage bookings
in the Parks Australia systems,
and by the delivery organisations
to manage products and available slots.

The API and the development process is flexible, so if something doesn't fit your case
too much please talk to us about it.

.. uml:: api_overview.uml

.. admonition:: N.B.

   These API's reqire an access key.
   Access keys are managed via the trade portal UI.
   See the **Security** page for details.


Side notes
----------

Please note that all URLs described here use empty API prefix. The real one will be something like this::

  https://integration.ecommerce.np.cp1.parksaustralia.gov.au/api/booking/v0/

so for example endpoint ``/reservations/`` becomes::

  https://integration.ecommerce.np.cp1.parksaustralia.gov.au/api/booking/v0/reservations/

Also, when doing request user is probably aware of some organisation ID (short number) and having some access credentials (either API token or browser session).

We suport pagination, objects are usually paginated by 50.

Current policy allows reservation creator to update number of people/groups after
the reservation is confirmed; if this behaviour is a problem for your organisation
then please contact us.

Base workflow

  * Delivery organisation creates a product
  * Delivery organisation adds slots (start-end datetime pair and some extra parameters) for the product
  * Agent organisation browses products and sees slots available
  * Agent organisation places reservations
  * Delivery org either confirms or denies reservations

Terms
-----

**Delivery organisation** - the organisation created the product and offering the service
described in it. This organisation can see all incoming reservations and information
about agents who book it.

**Agent** - organisation placing reservation for the product. The idea is that delivery org
creates products to offer their services, and agent organisations create reservations so
agent's clients can visit it.

**Product** - description of event which happens from time to time and has extra
information like delivery organisation, name, description and so on

**Space** - physical place which can be booked for one or more product. Examples of spaces
are campgrounds, wedding lawns, buildings and so on.

**Slot** - start and end datetime pair linked to specific product; can be booked.

**Reservation** - the fact of some slot booked by some organisation

**SpaceReservation** - the fact of some space booked for given time; usually linked to
product reservation and is created just after it

**Reservation note** - some text used to help delivery org and agent (booking) or to communicate


Rules
-----

Some constraints help us to keep the system in logical and strict state.
They can be hard (logically correct) or soft (just here to keep things simpler but can be avoided)

Soft:

* You can't update buffer times of product with active future reservations when these buffer times are in action (this will require freeing some slots or auto-booking other ones and the logic of that is not discussed/determined yet)
* You can't change slot start/end time once reservations are placed for it (because it means that customer experience changes, and they should be at least aware of that - logic of such notifications/approvals is not determined yet)
* you can't change product reservation status from the final one (declined/cancelled) to active - to keep things simple

Hard:

* product with reservations can't be deleted, only deactivated (thus stopping new reservatiosn from appearing)
* slots with reservations can't be deleted (but can have their units number decreased so no new reservations are placed for them)


Reservation workflow
--------------------

Once placed, the reservation goes from one status to another, triggering some actions
(like notification email sent) when moving to/from specific statuses.

This workflow is still to determine but generally next rules may be applied:

* Once the status changes to/from X we send email to customer/agent/deliveryorg
* Once the status in X it can be changed only to Y
* Object may change its status to X by agent/deliveryorg/both action

Space
-----

* There is contention for spaces, so:
  * spaces need to be shared between multiple orgs, and
  * spaces need to be shared between multiple products
  * spaces also need to have their availability managed (similar to products)
* any organisation can create space and make it available to other organisations of the same parks, but usually park will be doing that
  * current API version doesn't support space creation by organisations, it is the staff action
* space has ``is_public`` parameter
  * if True then any organisation of the given park can see it and place reservations
  * if False then only org creator + orgs from the ``visible_to_orgs`` list can operate with it.
* Spaces have a maximum capacity (for people or groups)
* There are several ways in which spaces can be booked:
  * directly: by a product that requires the space
  * via staff: some period are just blocked for that space, either soft or hard, to create technical reservation:
    * soft - this technical resevation can be overwriten by a direct reservation from some product
    * hard - space can't be used during this period for some maintenance reason
* space has its capacity in the same units as products
  * think about it as a bus which can hold only 1 group or a large hall where 3 groups can be at the same time
  * when placing space reservation (using some product) there will be "max units available" value for that space, and you can't reserve more than present. The larger reservation period you have the more probability of space having less units (for example, some space has capacity of 10 and there are 4 groups at 11, 1 group at 12 and 3 groups at 13; which means if you want to reserve it for some large event between 11 and 13 you'll be able to do it for 6 units, and if you move your event to the evening all 10 will be available)
  * for example space can hold 4 groups, which means 4 different reservations of product with "group" as unit can be placed for that
  * capacity is either "persons" or "groups"
  * if space capacity is in persons then only per-person products can be attached, the same is working for groups
  * you can't change product unit type once the product is attached to some space (but you can detach it). the same works the other way - after selecting some space for your product you may be sure that space won't change its unit type.
* if a product x requires space y and space y isn't available at time z, then product x also isn't available at time z (even if product  x has an otherwise available time slot)
* some products require multiple spaces simultaneously (``product.spaces_required`` is a list)
  * to avoid things being too simple some products require multiple spaces at different times (e.g 3 hours product, uses space 1 for an hour, then space 2 for an hour, then space 3) - explained separately
* there is an endpoint to view reservations from the space perspective
* having a space for the product is very limiting and means that if someone else got it first then no product reservations for these dates will be placed; please consider it when attaching some space to your product.
* if you assign space to existing product old reservations stay intact and don't reserve the space retrospectively; only new reservations will
* if you un-assign space from product (or change its parameters) existing reservations will stay intact
* if existing reservation with existing space attached to it is changed:
  * space reservation is changed as well, freeing or taking some units
  * in case of increase it's validated and you may get an error if the space can't fit this number (even if product slots can)
  * if the status is changed to cancelled/denied then the space reservation is deleted, freeing the units there (and you may not be able to change status back to active because the space may already be busy)

Space-Product relationship has the next important fields:
  * ``space_id`` which is just UUID of the space available to product owner
  * ``index`` (1 by default) - integer, values like 1 2 3 and used:
    * in case there are multiple spaces attached to the same product when the action is moved between different spaces (say they start at the space A spending 1 hour there and then move to space B spending another hour and end in space C with 30 minutes excursion).
    * there are multiple simultaneous spaces and product uses each of them fully (so index is ``1`` for both cases and ``index_percentage`` is ``100`` for both)
    * there are multiple alternative spaces: for both rows the ``index`` is ``1`` and the ``index_percentage`` is ``50``, which means product doesn't care which space to use OR product willingly uses just a half of space (allowing them or somewhere else to put another reservation with percentage value set to number not exceeding space usage over 100%)
    * Please note that now we are talking just about 1 unit of the space capacity; so if space capacity is 2 then 2 products can use this space for 100% simultaneously; and if capacity is 1 then only 1 product can use it for 100%, or 2 for 40/60 or 3 for 33% each.
    * The simplest case is having only 1 product-space relationship with the index ``1``.
  * ``index_percentage`` (100 by default) - as described previously, allows products to use only part of an unit of some space (or 2 spaces), this way manifesting the fact that 2 reservations may share 2 spaces and somehow deal with it on site.
  * ``minutes`` (null by default) - specifies how many minutes of the whole reservation time the space will be used. This is mostly informational field which doesn't have any logic constraints for it (yet).
  ** ``start_from_minutes`` (0 by default) - if you want product action to be moved from spaceA to spaceB then set this value to 0 for the first space in the list, then to N for the second, and L for the third, so space owner knows that space B is free for first N minutes and space A is free after first N minutes and so on.

Product
-------

Interesting fields:

* ``type`` - is the product offered by the official park organisation or an external partner. Informational
* ``unit`` - has possible values "person" or "group" and helps to display on what basis the reservations are accepted. Avaiability slots (see far below) can have maximal units per reservation parameter be set (for example, 15 people or 2 groups can attend some event).
* ``cost_per_unit`` - informational field, AUD per single unit. Decimal of format "xxxx.xx"
* ``available_to_agents`` (boolean) - can another organisation place reservations? Set to False if you want to (temporary) stop accepting new reservations. The product remains visible in the list, but no slots are returned. Existing reservations are not affected by changing this flag.
* ``available_to_public`` (boolean) - the same logic, but has no meaning while we don't offer the API to public. In the future we may have public information about product availability (calendar) and things like that. Personal data of agents placing reservations will not be shared.
* ``spaces_required`` - contains list (possibly empty) of spaces which are booked for each reservation for this product; having the space busy (no more free units for the reservation period) stops the reservation placement process. See spaces list endpoint for getting their list with readable name and some details.


Products list
~~~~~~~~~~~~~
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

  The next GET parameters (optional) are supported:

    * **park_slug** is a URL-compatible string that identifies the park, e.g. "anbg"
      for the Australian National Botanic Gardens or "kakadu" or "booderee".

    * **org_id** is a short number identifying the organisation to display only
      products provided by the choosen one. It will be useful mostly for
      the "Management" scenarion, and any organisation using API is aware of this
      value for itself. See the organisations list endpoint to get variants to filter on.

    * **org_name** - full organisation name (urlencoded). Exact case insensitive match.

    * **is_archived** (``false`` by default) - can be used to access archived products
      (if you set it to ``all`` or ``true``). Only active are returned by default.

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
~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~

.. http:get:: /products/(product_id)/

  Returns the same response format as the previous endpoint
  but for the single object.


Product update
~~~~~~~~~~~~~~

.. http:patch:: /products/(product_id)/

  Payload: set of non-readonly fields (like "short_description")

  Returns the same response format as the GET method in case of success (code 200) or
  error message if any happened (code 4xx).


Product delete
~~~~~~~~~~~~~~

.. http:delete:: /products/(product_id)/

  Payload: none.

  Returns: empty response with 204 code or 4xx error message.

  In case of no reservations created the product and all its slots are deleted.
  In case of at least one reservation (including not confirmed) present the product
  is marked as "is_archived" and will not be shown in the products list by default,
  but it's possible to display archived as well. Archived products can't accept any more reservations.


Product image upload
~~~~~~~~~~~~~~~~~~~~

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

Slots
-----

Slot is just a start-end datetime pair with some extra data attached.
The start date is usually inclusive while the end date is exclusive.
Reservations are created against one or more slots. Slot can be reserved
directly (when you place reservation for that slot, default behaviour)
or indirectly (the slot is disabled due to buffer time). Directly reserved slot
can't change start/end time while indirectly reserved one can.

If you create slot and there is buffer time set for this product and there is reservation
which buffer time touches the slot then this slot may be reserved from the start (at least
some number of units in it).


Slots list
~~~~~~~~~~

(check availability of product)

.. code-block:: gherkin

   So that users can plan a school excursion to Canberra
   they need to check the availability
      of an individual product
      at a particular park
      (optionally, within a date range)
   using the "check availability" API

This could be done on-demand, or as a periodic task
(to populate a cache).

The Parks System MAY wrap this call in a CDN
(with a ~short TTL) so that it's safe for booking agent systems
to hit it as often as they like.

.. uml::

   box "Booking Agent System" #lightblue
      participant BCE
   end box
   box "Parks System" #lightgreen
      boundary "<<API>>\n.../availability\n?from=$date\n&to=$date" as get_availability
      database "product\nthings" as product_things
   end box
   BCE -> get_availability: GET
   get_availability -> product_things: query_availability(\n  product=id,\n  from=from_date\n  to=to_date)
   get_availability -> BCE: json data


.. http:get:: /products/(product_id)/slots/?from=(datetimeZ)&until=(datetimeZ)

   Returns a list of available time slots
   for a product,
   within the given date range.

   If no "from" parameter is given then all slots since the current one (which may
   be already started and thus not available for booking) are returned.
   Filter is performed using the slot end time.

   "from" and "until" datetimes are inclusive. They muse be provided in ISO format
   with mandatory UTC timezone (example: ``2020-05-28T17:00:00Z``)

   If no "until" parameter is given,
   then either for all of the future
   or some sensible default will be used.

   This is not entirely defined,
   the Parks system may or may not
   apply a default future date.
   Similarly, if you explicitly request
   an "until" date in the distant future
   (e.g. 500 years hence)
   we may or may not substitute a less distant date.
   This will be some years in the future,
   so it won't cause strange behavior
   unless you are making very strange queries.
   In which case it serves you right.

   "from" and "until" dates in the past will return you
   archived slots, which is useful if you are product owner
   and want to update it.

   Regarding max and reserved units: some products support multiple persons
   or groups at the same time, so if ``reserved_units`` value is less than max then it
   still can be reserved. We return fully booked slots as well for informational
   reasons - some reservations may be cancelled so worth to check later.

   Please note that this doesn't reflect space availability; so even if given slot is free
   the busy space still can stop the reservation process. See space reservations endpoint
   for details about their availability.

   Response example::

    {
      "count": 3,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 1,
          "start_time": "2020-05-28T12:00:00+10:00",
          "end_time": "2020-05-28T13:00:00+10:00",
          "max_units": 2,
          "reserved_units": 1,
          "direct_reserved_units": 1,
          "indirect_reserved_units": 0
        },
        {
          "id": 2,
          "start_time": "2020-05-28T17:00:00+10:00",
          "end_time": "2020-05-28T18:00:00+10:00",
          "max_units": 1,
          "reserved_units": 1,
          "direct_reserved_units": 1,
          "indirect_reserved_units": 0
        },
        {
          "id": 3,
          "start_time": "2020-05-30T02:50:42+10:00",
          "end_time": "2020-05-30T05:50:43+10:00",
          "max_units": 3,
          "reserved_units": 0,
          "direct_reserved_units": 0,
          "indirect_reserved_units": 0
        }
      ]
    }

   Notes:
    * if the product doesn't exist, 404
    * if there are no slots defined then the empty list is returned.
    * if the from date is after the until date
      you will get an error message.
    * it's perfectly fine for the from date
      to be the same as the until date.


Slot create
~~~~~~~~~~~

.. http:post:: /products/(product_id)/slots/

  .. code-block:: gherkin

    As a product owner
    I'd like to create a new slot and specify time for it
    so people can make reservations for it

  Minimal request example::

    {
      "start_time": "2020-01-01T15:00",
      "start_time": "2020-01-01T18:00:00"
    }

  Full request also can include "max_units" (integer) and other fields (future API versions).

  Error response examples::

    {"code":"FRS-400","title":"ValidationError","detail":{"start_time":["This field is required."],"end_time":["This field is required."]}}

  Succesfull response contains full slot information
  in the same format as the slots list returns.


Reservation
-----------

Reservation is a representation of fact that somebody will come to an event.
They are always created for given product and given slots set (one or more).
Has some status flow (from pending to completed) and it's expected
that both parties (reservation initiator and product delivery org)
update them based on the status flow.

Please note that the reservation IDs are string, not integer field, containing
some unique value (typically UUID but we won't guarantee it)

Reservations list
~~~~~~~~~~~~~~~~~

.. http:get:: /reservations/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/created/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/received/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&

    Return full list of all reservations visible to the current user.
    Filters are applied. Reservations are rendered quite deep for convenience.
    Use created/received sub-urls to look at the situation from the different
    parties point of view: agent making reservatins for client and the
    amentity owner handling reservations and working to meet all the people
    coming to see it.

    Please note that reservation object has informational readonly fields start_time
    and end_time; you can't update them and they are filled automatically from the first
    slot start time and the last slot end time respectively, reflecting the full
    time period of traveller visiting the event. The date filters work based on these
    fields (so only reservations which are active for the filtering period are returned). Default "from" value is today, "until" is some date in the far future.

    Response example::

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": "9eefbecb-29be-441e-be13-c59870671940",
            "product": {
              "id": 2,
              "type": "park",
              "park": "kakadu",
              "delivery_org": "Bowali",
              "name": "Naidoc Week",
              "short_description": "",
              "image": "http://localhost:8000/media/products_images/ObQOeL8uJqY.jpg",
              "contact": "",
              "unit": "person",
              "cost_per_unit": "6.00"
            },
            "slots": [
              {
                "id": 1,
                "start_time": "2020-05-28T12:00:00+10:00",
                "end_time": "2020-05-28T13:00:00+10:00",
                "max_units": 2,
                "reserved_units": 1
              },
              {
                "id": 2,
                "start_time": "2020-05-28T17:00:00+10:00",
                "end_time": "2020-05-28T18:00:00+10:00",
                "max_units": 1,
                "reserved_units": 1
              }
            ],
            "agent": "Australian trade corp",
            "units": 1,
            "customer": null,
            "created_at": "2020-05-28T21:14:05+10:00",
            "status": "accepted",
            "start_time": "2020-05-28T12:00:00+10:00",
            "end_time": "2020-05-28T18:00:00+10:00"
          }
        ]
      }


Reservation create
~~~~~~~~~~~~~~~~~~

.. http:post:: /reservations/

  .. code-block:: gherkin

    As an agent
    I need to create reservation for my clients
    So the delivery organisation is aware that they will come

  The request example::

    {
      "product_id": 1,
      "slots": [1, 2, 3],
      "units": 1,
      "customer": {
        "name": "st. Martin's school"
      }
    }

  The "agent" field will be assigned automatically to the user's organisation.
  Response will contain the sent data + all other fields
  (some of them filled automatically, some of them empty).

  "Customer" field is not much defined currently but will contain some data
  useful for both parties to identify the coming people. Please come to us with
  your requirements for that field if you need something specific here.

  The original agent (booking creator) and the product delivery organisation
  will be able to update it (change status, provide more details, etc).

  When placing the reservation, for cases when some space(s) assigned, the space
  reservation will be performed as well transparently to user (if success) or
  error about space busy will be raised (if failed).


Reservation update
~~~~~~~~~~~~~~~~~~

.. http:patch:: /reservations/{reservation_id}/

  Request::

    {"field1": "value1", ...}

  Validations are applied.

  Some common use-cases:

  * delivery org: accept reservation - update status to "accepted"
  * delivery org: deny reservation - update status to "denied" (with some note probably)
  * delivery org: finaize booking after fulfillment (status="completed")
  * agent: request reservation cancellation (status="cancellation_requested")
  * delivery_org: confirm reservation cancellation (status="cancelled")


Reservation notes (RNs)
~~~~~~~~~~~~~~~~~~~~~~~

Endpoints to list and create RNs. No note detail endpoint is provided. RNs
can't be updated or deleted (contacting support is required if you have leaked
some private data there). Field ``is_public`` (false by default) is responsible for
note being visible to the other party. The only required field is "text".

.. http:get:: /reservations/{reservation_id}/notes/
.. http:post:: /reservations/{reservation_id}/notes/


List response example::

  {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 3,
        "reservation": "9eefbecb-29be-441e-be13-c59870671940",
        "author": "Bowali",
        "created_at": "2020-06-04T19:57:42.962933+10:00",
        "text": "Please note that you'll have to bring your concession document while visiting the event",
        "is_public": true
      },
      {
        "id": 2,
        "reservation": "9eefbecb-29be-441e-be13-c59870671940",
        "author": "Bowali",
        "created_at": "2020-06-04T19:57:27.535222+10:00",
        "text": "note to guide: check their IDs before making a tour",
        "is_public": false
      },
      {
        "id": 1,
        "reservation": "9eefbecb-29be-441e-be13-c59870671940",
        "author": "Bowali",
        "created_at": "2020-06-04T19:57:24.983188+10:00",
        "text": "hmm they seem to be a concession party but they didn't tell us",
        "is_public": false
      }
    ]
  }



Spaces list
~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
