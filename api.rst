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

.. http:get:: /parks/(str:park-slug)/bookables?team=(org-slug)

   Returns a list of bookable things,
   for the given delivery org (org-slug).

   The "park-slug" is a URL-compatible string
   that identifies the park, e.g. "ANBG"
   for the Australian National Botanic Gardens

   The "org-slug" is a URL-compatible string
   that identifies the organisation
   responsible for the bookable thing.
   e.g. "anbg-edu-team".

   TODO: what data structure is returned?
   Needs to include a URL to each bookable thing,
   and some text suitable for a drop-down list.
   Anything else?

   Notes:
    * not shown: the GET call is made with an API key.
    * if the park doesn't exist, 404
    * if the team doesn't exist, empty list returned
    * if the team exists but has no bookable things, empty list returned


check availability of bookable thing
------------------------------------

.. code-block:: gherkin

   So that BCE users can plan a school excursion to Canberra
   they need to check the availability
      of an individual bookable thing
      at a particular park
      (optionally, within a date range)
   using the "check availability" API

This could be done on-demand,
or as a periodic task
(to populate a cache).

The Parks System MAY
wrap this call in a CDN
(with a ~short TTL)
so that it's safe for booking agent systems
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


.. http:get:: /parks/(str:park-slug)/bookables/(int: id)?from=(date: from_date)&until=(date: to_date)

   Returns a list of available time slots
   for a bookable thing,
   within the given date range.

   If no "from" parameter given,
   then from today.

   "from" and "until" dates are inclusive,
   i.e. from today includes today's availabilities,
   and until tomorrow includes tomorrow's.

   The "from" and "until" parameters
   may be an ISO-8601 date string,
   (`YYYY-MM-DDTHH:mm:ss.sssZ`)
   however the time part will be ignored
   (chomped to `YYYY-MM-DD`).
   You can also supply a pre-chomped string,
   like `YYYY-MM-DD`.
   Actually the hyphens are optional too,
   `YYYYMMDD` will also work.
   
   If you actually want to filter by a time of day,
   you have to do it on the client side.
   This shouldn't be too bad because
   the list of available time slots
   for the given thing on a given day
   should be reasonably small.

   You can the fact we ignore the time of day
   to bust our cache (CDN).
   Maybe this will help you debug something.

   *(note to self:
   remember to memory-cache our DB queries
   to prevent explicit-microsecond DOSsing)*

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

   "from" dates in the past
   will be silently replaced with today.
   "until" dates in the past
   will be silently replaced with tomorrow.

   The "park-slug" is a URL-compatible string
   that identifies the park, e.g. "ANBG"
   for the Australian National Botanic Gardens

   TODO:
    * what data structure is returned?
    * should it be paginated? How does that work?
    * should there be a header-like structure
      summarising the results?

   Notes:
    * not shown: the GET call is made with an API key.
    * if the park doesn't exist, 404
    * if the bookable thing doesn't exist, 404
    * if the park and bookable thing both exist,
      but there are no availabilities,
      then an empty list is returned.
    * if the from date is after the until date
      you will get an error message.
    * it's perfectly fine for the from date
      to be the same as the until date.

   
create pending booking
----------------------


finalise booking
----------------


create detailed information about booking
-----------------------------------------


update detailed information about booking
-----------------------------------------
