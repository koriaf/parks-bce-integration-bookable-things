Slots
=====

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
----------

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
-----------

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

  Succesfull response contains full slot information in the same format as the slots list returns.

  Tip: if you send a list of dicts instead of single dict - multiple slots will be created.
  Error handlng strategy is "all or none", so single error means that no slot will be created by this request.


Slot Detail
-----------

.. http:get:: /products/(product_id)/slots/(slot_id)/


Slot Delete
-----------

.. http:delete:: /products/(product_id)/slots/(slot_id)/

  Slots with active reservations can't be deleted by that endpoint.


Slots bulk disable/delete
--------------------------

.. http:post:: /products/(product_id)/slots/delete/

  * Slots that are either available or pending could be deleted
  * Slots with confirmed reservations are not deleted but their units number is decreased so they can't accept any new ones

  Request example::

    {
      "slots": [1, 2, 3, 4]
    }

  Response example::

    {
      "1": "deleted",
      "2": "disabled",
      "3": "deleted",
      "4": "not-found"
    }

  Note keys are converted to string for compatibility with possible non-int IDs

  If requested slot can't be found then no error is raised but response reflects that fact (for cases when someone deleted single slot while someone else was clicking the button)
