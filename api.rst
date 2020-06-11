API Requirements
================

This shows how the API is used
by booking Agents (such as BCE)
to create and manage bookings
in the Parks Australia systems,
and by the delivery organisations
to manage bookable things and available slots.

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

  * Delivery organisation create bookable thing
  * Delivery organisation add slots (start-end datetime pair) for the bookable thing
  * Agent organisation browses bookable things and slots available
  * Agent organisation places reservations
  * Delivery org either confirms or denies reservations

Bookable things
---------------

An example of bookable thing is Tour, School excursion or Tasting event.

Interesting fields:

* type - is the bookable offered by the official park organisation or an external partner. Informational
* unit - has possible values "person" or "group" and helps to display on what basis the reservations are accepted. Avaiability slots (see far below) can have maximal units per reservation parameter be set (for example, 15 people or 2 groups can attend some event).
* cost_per_unit - informational field, AUD per single unit.
* available_to_agents (boolean) - is another organisation can place reservations. Set to False if you want to (temporary) stop accepting new reservations. The bookable remains visible in the list, but no slots are returned.
* available_to_public (boolean) - the same logic, but has no meaning while we don't offer the API to public.

Bookables list
~~~~~~~~~~~~~~
..for the current organisation

.. code-block:: gherkin

   As a booking agent (like BCE)
   I need to get a list of bookable things visible to me
   so that I can map Spaces to Bookable Things
   and so that I know what resources to check the availability of

.. code-block:: gherkin

   As a delivering organisation
   I need to get a list of bookable things I created
   so I can manage them:
   * manage slots
   * manage reservations
   * manage bookable things itself


.. uml::

   actor "Delivery Org\nUser" as parks_staff
   box "Booking Agent" #lightblue
      participant "Agent\nSystem" as BCE
   end box
   parks_staff -> BCE: configure bookable things\nfrom the Parks system\nin the agent's system
   box "Parks System" #lightgreen
      boundary "<<API>>\n/parks/{park-slug}/bookables\n?team={org-slug}" as get_list_bookables
      database "bookable\nthings" as bookable_things
   end box
   BCE -> get_list_bookables: GET
   get_list_bookables -> bookable_things: query_list(\n  park=park-slug,\n  org=team-slug\n)

   get_list_bookables -> BCE: json data
   BCE -> parks_staff: show options from Parks system
   parks_staff -> BCE: map to bookable things\n(e.g. "spaces")\nin the Agent system

.. http:get:: /bookables/?org_id=(org_id)&org_slug=(string)&park_slug=(park_slug)&is_archived=true/false/all

  Returns a list of bookable things. GET parameters are optional and filter
  the output.

  The "park_slug" is a URL-compatible string
  that identifies the park, e.g. "anbg"
  for the Australian National Botanic Gardens or "kakadu" or "booderee".

  The "org_id" is a short number identifying the organisation to display only
  bookable things provided by the choosen one. It will be useful mostly for
  the "Management" scenarion, and any organisation using API is aware of this
  value for itself.
  org_name - full organisation name (urlencoded)

  ``is_archived`` parameter is false by default and can be used to access archived
  bookables (if you set it to all or true). They are hidden by default.

  In case of wrong filters parameter (park doesn't exist, org doesn't exist)
  empty results set will be returned (except the is_archived parameter where the value
  is strictly validated to be one of all, true or false).

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
          "image": "http://localhost:8000/media/bookables_images/ObQOeL8uJqY.jpg",
          "contact": "",
          "unit": "person",
          "cost_per_unit": "6.00",
          "is_archived": false,
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
        }
      ]
    }


Bookable creation
~~~~~~~~~~~~~~~~~

.. http:post:: /bookables/

.. code-block:: gherkin

   As a delivering organisation
   I want to create a "Bookable Thing"
   so agent organisation can book my time

  The current organisation becomes ``delivery_org``. ``customer`` field will
  be explained later. All fields not listed here are readonly or optional.
  Success is 201, error is 4xx (subject to change and specific codes will be used)

  Minimal request example::

    {
        "name": "First Bookable",
        "unit": "person",
        "park": "kakadu"
    }

  Full request example::

    {
        "name": "First Bookable '${NOW}'",
        "unit": "person",
        "park": "kakadu",
        "short_description": "night walk",
        "cost_per_unit": "55.00"
    }

  Success response: the same as the Bookables list endpoint but without pagination.


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


Bookable details
~~~~~~~~~~~~~~~~

.. http:get:: /bookables/(bookable_id)/

  Returns the same response format as the previous endpoint
  but for the single object.


Bookable update
~~~~~~~~~~~~~~~

.. http:patch:: /bookables/(bookable_id)/

  Payload: set of non-readonly fields (like "short_description")

  Returns the same response format as the GET method in case of success (code 200) or
  error message if any happened (code 4xx).


Bookable delete
~~~~~~~~~~~~~~~

.. http:delete:: /bookables/(bookable_id)/

  Payload: none.

  Returns: empty response with 204 code or 4xx error message.

  In case of no reservations created the bookable and all its slots are deleted.
  In case of at least one reservation (including not confirmed) present the bookable
  is marked as "is_archived" and will not be shown in the bookables list by default,
  but it's possible to display archived as well. Archived bookables can't accept any more reservations.


Slots
-----

Slot is just a start-end datetime pair with some extra data attached.
The start date is usually inclusive while the end date is exclusive.
Reservations are created against one or more slots.


Slots list
~~~~~~~~~~

(check availability of bookable thing)

Implemented: everything except filters.

.. code-block:: gherkin

   So that users can plan a school excursion to Canberra
   they need to check the availability
      of an individual bookable thing
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
      database "bookable\nthings" as bookable_things
   end box
   BCE -> get_availability: GET
   get_availability -> bookable_things: query_availability(\n  bookable=id,\n  from=from_date\n  to=to_date)
   get_availability -> BCE: json data


.. http:get:: /bookables/(bookable_id)/slots/?from=(date: from_date)&until=(date: to_date)

   Returns a list of available time slots
   for a bookable thing,
   within the given date range.

   If no "from" parameter given then all slots since the current one (which may
   be already started and thus not available for booking). Slot start time is used.

   "from" and "until" dates are inclusive,
   i.e. from today includes today's availabilities,
   and until tomorrow includes tomorrow's.

   The "from" and "until" parameters
   may be an ISO-8601 date string (`YYYY-MM-DD`).
   Having dates here help us to cache things,
   please do more detailed filtering on the client side.
   Regarding the timezone: the server timezone will be used, so for night
   events it's practical to get the previous and the next days (if you are not sure).

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
   archived slots, which is useful if you are bookable thing owner
   and want to update it.

   Regarding max and reserved units: some bookables support multiple persons
   or groups at the same time, so if ``reserved_units`` value is less than max then it
   still can be reserved. We return fully booked slots as well for informational
   reasons - some reservations may be cancelled so worth to check later.

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
          "reserved_units": 1
        },
        {
          "id": 2,
          "start_time": "2020-05-28T17:00:00+10:00",
          "end_time": "2020-05-28T18:00:00+10:00",
          "max_units": 1,
          "reserved_units": 1
        },
        {
          "id": 3,
          "start_time": "2020-05-30T02:50:42+10:00",
          "end_time": "2020-05-30T05:50:43+10:00",
          "max_units": 3,
          "reserved_units": 0
        }
      ]
    }

   Notes:
    * if the bookable thing doesn't exist, 404
    * if there are no slots defined then the empty list is returned.
    * if the from date is after the until date
      you will get an error message.
    * it's perfectly fine for the from date
      to be the same as the until date.


Slot create
~~~~~~~~~~~

.. http:post:: /bookables/(bookable_id)/slots/

  .. code-block:: gherkin

    As a bookable thing owner
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
They are always created for given bookable and given slots set (one or more).
Has some status flow (from pending to completed) and it's expected
that both parties (reservation initiator and bookable thing delivery org)
update them based on the status flow.

Please note that the reservation IDs are string, not integer field, containing
some unique value (typically UUID but we won't guarantee it)

Reservations list
~~~~~~~~~~~~~~~~~

Implemented: except filters (but the created-received should work).

.. http:get:: /reservations/?from=&until=&park_slug=&bookable_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/created/?from=&until=&park_slug=&bookable_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/received/?from=&until=&park_slug=&bookable_id=&delivery_org_id=&delivery_org_name=&

    Return full list of all reservations visible to the current user.
    Filters are applied. Reservations are rendered quite deep for convenience.
    Use created/received sub-urls to look at the situation from the different
    parties point of view: agent making reservatins for client and the
    amentity owner handling reservations and working to meet all the people
    coming to see it.

    Please note that reservation object has informational readonly fields start_time
    and end_time; you can't update them and they are filled automatically from the first
    slot start time and the last slot end time respectively, reflecting the full
    time period of traveller visiting the event. The filters work based on these
    fields (filtering only by start time date)

    Response example::

      {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": "9eefbecb-29be-441e-be13-c59870671940",
            "bookable": {
              "id": 2,
              "type": "park",
              "park": "kakadu",
              "delivery_org": "Bowali",
              "name": "Naidoc Week",
              "short_description": "",
              "image": "http://localhost:8000/media/bookables_images/ObQOeL8uJqY.jpg",
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
      "bookable_id": 1,
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
  useful for both parties to identify the coming people.

  The original agent (booking creator) and the bookable delivery organisation
  will be able to update it (change status, provide more details, etc).


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


Reservation notes
~~~~~~~~~~~~~~~~~

Endpoints to list and create notes. No note detail endpoint is provided. Note
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

