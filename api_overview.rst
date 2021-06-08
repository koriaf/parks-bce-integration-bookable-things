API Overview
============

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


Configuration endpoint
----------------------

With the correct api key or cookies returns base information about the current auth.

.. http:get:: /conf/

"role" can be "admin" or "guide" or "agent" (guide is applicable for CTO and agent for retail, these 2 kinds of users are the same from the permissions perspective)

Response example::

    {
      "current_org": {
        "id": 19,
        "name": "Entry Station",
        "type": "Parks Australia"
      },
      "current_user": {
        "user": "johnsmith@parks.gov.au",
        "role": "admin"
      },
      "parks": [
        "uluru"
      ]
    }
