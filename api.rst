API Requirements
================

This shows how the API is used
by booking Agents (such as BCE)
to create and manage bookings
in the Parks Australia systems.

.. uml:: api_overview.uml

.. admonition:: N.B.

   These API's reqire an access key.
   Access keys are managed via the trade portal UI.
   See the **Security** page for details.

Please note that all URLs entered here use empty API prefix. The real one will be something like this::

  https://integration.ecommerce.np.cp1.parksaustralia.gov.au/api/bookables/v0/

so for example endpoint ``/reservations`` becomes::

  https://integration.ecommerce.np.cp1.parksaustralia.gov.au/api/bookables/v0/reservations/

Also, when doing request user is probably aware of some organisation ID (short number) and having some access credentials (either API token or browser session)

Note: we don't support pagination yet but it will be done soon, stay alert.

get list of bookable things
---------------------------
..for this team, for this park (ANBG)

.. code-block:: gherkin

   As a booking agent (like BCE)
   I need to get a list of bookable things
   so that I can map Spaces to Bookable Things
   and so that I know what resources to check the availability of

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

.. http:get:: /?org=(org_id)&park=(park_slug)

  Returns a list of bookable things. GET parameters are optional and filter
  the output.

  The "park_slug" is a URL-compatible string
  that identifies the park, e.g. "anbg"
  for the Australian National Botanic Gardens or "kakadu" or "booderee".

  The "org_id" is a short number identifying the organisation.
  In the nearest future we may also use org_slug and org_name filters.
  These will be URL-compatible strings that identifie the organisation
  responsible for the bookable thing. e.g. "anbg-edu-team".

  In case of wrong filters parameter (park doesn't exist, org doesn't exist)
  empty results set will be returned. We probably should return 404 or 400 in that
  case - a matter to discuss.

  The response has the next format::

    [
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
        "cost_per_unit": "6.00"
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
        "cost_per_unit": "21.00"
      }
    ]



Bookable thing details
----------------------

.. http:get:: /(bookable_id)/

  Returns the same response format as the previous endpoint but for the single object.


check availability of bookable thing
------------------------------------

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


.. http:get:: /(bookable_id)/slots/?from=(date: from_date)&until=(date: to_date)

   Returns a list of available time slots
   for a bookable thing,
   within the given date range.

   If no "from" parameter given then all slots since the current one (which may
   be already started and thus not available for booking)

   "from" and "until" dates are inclusive,
   i.e. from today includes today's availabilities,
   and until tomorrow includes tomorrow's.

   The "from" and "until" parameters
   may be an ISO-8601 date string,
   (`YYYY-MM-DD`). Having dates here help us to cache things,
   please do more detailed filtering by times on the client side.
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
   reasons - some reservations may be cancelled.

   Response example::

    [
      {
        "start_time": "2020-05-28T12:00:00+10:00",
        "end_time": "2020-05-28T13:00:00+10:00",
        "max_units": 1,
        "reserved_units": 1
      },
      {
        "start_time": "2020-05-28T17:00:00+10:00",
        "end_time": "2020-05-28T18:00:00+10:00",
        "max_units": 1,
        "reserved_units": 1
      }
    ]

   Notes:
    * not shown: the GET call is made with an API key.
    * if the bookable thing doesn't exist, 404
    * if there are no slots defined then the empty list is returned.
    * if the from date is after the until date
      you will get an error message.
    * it's perfectly fine for the from date
      to be the same as the until date.


Create pending reservation
--------------------------

.. http:post:: /reservations/

  The request example::

    {
      "bookable_id": 1,
      "slots": [1, 2, 3],
      "customer": {
        "name": "st. Martin's school"
      }
    }

  The "agent" field will be assigned automatically to the user's organisation.
  Response will contain the sent data + all other fields
  (some of them filled automatically, some of them empty).

  The original agent (booking creator) and the bookable delivery organisation
  will be able to update it (change status, provide more details, etc).



List reservations
-----------------

.. http:get:: /reservations/?from=&until=&park=&booking_id=&agent=&

    Return full list of all reservations visible to the current user.
    Filters are applied.


Update reservation
------------------

.. http:patch:: /reservations/{reservation_id}/

  Request::

    {"field1": "value1", ...}

  Validations are applied.




finalise booking
----------------

patch status to "completed"
