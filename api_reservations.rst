Reservations
============

Reservation is a representation of fact that somebody will come to an event.
They are always created for given product and given slots set (one or more).
Has some status flow (from pending to completed) and it's expected
that both parties (reservation initiator and product delivery org)
update them based on the status flow.

Please note that the reservation IDs are string, not integer field, containing
some unique value (typically UUID but we won't guarantee it)

Reservations list
-----------------

.. http:get:: /reservations/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/created/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&
.. http:get:: /reservations/received/?from=&until=&park_slug=&product_id=&delivery_org_id=&delivery_org_name=&

    Return full list of all reservations visible to the current user.
    Filters are applied. Reservations are rendered quite deep for convenience.
    Use created/received sub-urls to look at the situation from the different
    parties point of view: agent making reservations for client and the
    amenity owner handling reservations and working to meet all the people
    coming to see it.

    Optional GET "sort" field (default is "chronological" which means "by start date smaller first") can
    contain one of the values "chronological", "product_name", "units", "agent_name", "total_cost"
    with optional "-" sign in front of it to change the direction.

    Please note that reservation object has informational readonly fields start_time
    and end_time; you can't update them and they are filled automatically from the first
    slot start time and the last slot end time respectively, reflecting the full
    time period of traveller visiting the event. The date filters work based on these
    fields (so only reservations which are active for the filtering period are returned).
    Default "from" value is today, "until" is some date in the far future.

    The ``extra_data`` field contains anything related to the business logic and subject are without much validation
    from the server side; useful for storing confirmation, completion and form data like shown on the example.
    None of these fields are required.
    Confirmation and completion data is updated either by a separate POST requests (see related endpoints)
    or directly using the reservation update endpoint.
    Users may add other keys in the future to follow their changing requirements, but should care about
    validation of that data themselves.

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
              "cost_per_unit": "6.00",
              "minimum_units":null,
              "minimum_minutes":null,
              "maximum_minutes":null
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
            "end_time": "2020-05-28T18:00:00+10:00",
            "total_cost": "7.25",
            "extra_data": {
              {
                "formData": {
                  "school": {
                    "street_address": "ABC Street",
                    "adults_attending": 1,
                    "students_attending": 1
                  },
                  "billing": {
                    "country": "AU"
                  },
                },
                "formVersionId": "a4883d73-02c3-4a70-844b-6d5475b79ce9",
                "confirmationData": {
                  "confirmedAt": "2021-02-18T09:41:56.929779+00:00"
                },
                "confirmationDataSchema": {},
                "completionData": {
                  "completedAt": "2021-02-18T17:12:35.345484+00:00"
                },
                "completionDataSchema": {}
              }
            }
          }
        ]
      }


Reservations confirmation and completion
----------------------------------------

.. http:post:: /reservations/{reservation_id}/confirmation-data/
.. http:post:: /reservations/{reservation_id}/completion-data/

These two endpoints are similar and are used to save extra data and update the reservation status.

In the current API version they are available both to delivery and agent orgs; although changing
status to "confirmed" is available only to delivery org.

Both endpoints save payloads to ``Reservation.extra_data`` field of the reservation related; you can
update that field directly using the reservation update endpoint itself.

The data is not validated against the schema yet, but it may be introduced in the future. Empty schema is fine.

Only POST requests are accepted to reflect the nature of these endpoints. Use reservation details endpoint
to retrieve the actual version of it.

**Confirmation**

Payload should contain 2 dicts: ``confirmationData`` and ``confirmationDataSchema`` of any format.

Response is either 200 with full reservation detail response or an error response.

If called by delivery org and status is "pending" then status is changed to "confirmed" automatically.

**Completion**

Payload should contain 2 dicts: ``completionData`` and ``completionDataSchema`` of any format.

Response is either 200 with full reservation detail response or an error response.

If status is "confirmed" then changed to "completed" automatically; if not then only that extra data is saved.



Reservation create
------------------

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
      },
      "extra_data": {
        "field1": "value1"
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
------------------

.. http:patch:: /reservations/{reservation_id}/

  Request::

    {"field1": "value1", ...}

  Validations are applied.

  Some common use-cases:

  * delivery org: accept reservation - update status to "accepted"
  * delivery org: deny reservation - update status to "denied" (with some note probably)
  * delivery org: finalise booking after fulfillment (status="completed")
  * agent: request reservation cancellation (status="cancellation_requested")
  * delivery_org: confirm reservation cancellation (status="cancelled")


Reservation notes (RNs)
-----------------------

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


Reservation history
-------------------

Return full list of historical versions of that reservation.
It's a typical paginated list result with each item a rendered Reservation instance with small differences:

* ``product`` and ``created_at`` fields are omitted because they are the same - get them from the actual version (note though that if product changes then it's history lost here)
* ``history_date`` field is added, containing ISO8601 datetime of that history element created (the moment of update event)

Ordered "newest first". Please note that each history item contains new version of that record, not old, so the first one (the most recent) is equal to the actual reservation.

During the transition period (while this functionality is fresh) historical records may not be present, but any reservations created after this endpoint is available will be fine.

.. http:get:: /reservations/{reservation_id}/history/
