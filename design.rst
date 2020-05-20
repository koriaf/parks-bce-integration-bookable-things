Logical Model
=============

This is the logical model,
from the perspective of the Parks System.

(blue classes already exist, green ones are new)

.. uml::

   class BookableThing #lightgreen
   class Park #lightblue {
     e.g. ANBG
   }
   Park o-- BookableThing

   class DeliveryOrg #lightblue {
     e.g. ANBG Education Officers
     like existing CTO
   }
   DeliveryOrg o-- BookableThing
   
   class Booking #lightgreen {
     status
     start_time
     end_time
   }
   BookableThing o-- Booking
   class Availability #lightgreen {
     start_time
     end_time
   }
   BookableThing o-- Availability
   class Agent #lightblue {
     e.g. BCE
     like existing RSA
   }
   Agent o-- Booking
   class Customer #lightblue {
     e.g. Hogwarts
     like existing party
   }
   Customer o-- Booking


Bookable Thing
   The thing which is booked... Deliberately generic.

Park
   Parks Australia is a coalition of separate organisations called Parks...

Delivery Org
   Somebody is responsible for delivering the Bookable Thing.
   In the current project, this is a small team within Parks Australia
   (the education officers for ANBG)
   however in theory it could also be a commercial tour operator.
   The Parks Staff who confirm or deny pending bookings are in this org.
   They are also the BCE systen users that manage bookings directly in BCE
   and configure bookable education experiences in BCE.

Availability
   This is a slice of time when
   a particular the Bookable Thing
   may be booked.
   The Delivery Org members create these
   (using some kind of calendar interface).
   when they plan to have the bookable thing available.
   They are negated by bookings.

Agent
   In the current project, the only Agent is BCE.
   Agents make tentative Bookings,
   which may be confirmed or denied by the Delivery Org.

Customer
   The party on who's behalf the booking is made.
   i.e. the School (or teacher).

Booking
   An apointment to use the Bookable Thing.
   Made by an Agent
   on behalf of a Customer.


booking statechart
------------------

Note that the booking has a **status** attribute.
This will have one of the following 6 values:

.. uml::

   state pending #lightblue
   [*] --> pending
   note "new pending bookings\ncan be created\nin the Parks System\nby Agents (like BCE)" as N1
   N1 --> pending
   pending --> denied
   state denied #lightgreen
   pending --> accepted
   state cancelled #yellow
   pending --> cancelled
   accepted --> cancelled
   state completed #orange
   state accepted #lightgreen
   accepted --> completed
   note "pending bookings can be cancelled\nby the Agent who made them,\nbut accepted bookings can only\nbe cancelled by the DeliveryOrg\nassociated with the Bookable Thing" as N2
   N2 --> cancelled
   denied --> [*]
   completed --> [*]
   cancelled --> [*]
   note "accepted bookings can be completed\nby the Agent who made them, or by\nthe responsible Delivery Org.\nWhen completed, the Agent may\nprovide aditional information about\nthe booking (post-facto)" as N3
   N3 --> completed
   note "only the Delivery Org\ncan accept a booking" as N4
   N4 --> accepted
   note "only the Delivery Org\ncan deny a booking" as N5
   N5 --> denied
   state "pending\ncancellation\nrequested" as pcr #lightblue
   pcr --> cancelled
   accepted --> pcr
   note "if the booking is pending,\nthe Agent may request cancellation.\nHowever, it may be too late for\nthe Delivery Org to Cancel.\nIn this situation, the delivery org\nmay chose to cancell or accept a\nbookings with cancellaton requested" as N6
   N6 -up-> pcr

**light green**: Only the Delivery Org can do this.

**light blue**: Agents can do this.

**orange**: Agents or Delivery Orgs can do this.

**yellow**: Agents or Delivery orgs can do this, with conditions.


note about organisations
------------------------

In the existing Parks Australia system, we have users who belong to organisations.

Some organisations are part of a park, other organisations are independent (i.e. commercial partners of the parks). We call these independent organisations CTOs (Commercial Tour Operators) or RSAs (Retail Sales Agents). In practice, CTOs and RSAs are typically associated with one part, but some of the larger ones operate across multiple parks.

.. uml::

   abstract class "generic\norganisation" as org {
     org_id
   }
   class "Park\nTeam" as pt extends org {
     org_id
     park_id
   }
   abstract class "Trade\nPartner" as trade extends org {
     org_id
   }
   class "CTO" as cto extends trade {
     org_id
   }
   class "RSA" as rsa extends trade {
     org_id
   }

   class "Park" as park {
     park_id
   }
   pt --* park

   class "Commercial\nPermit" as cp {
     park_id
     cto_org_id
   }
   park *-- cp
   cto *-- cp

CTOs have a **Commercial Permit** to operate tours in the park.
Logically, Commercial Tours are bookable things too.
So we actually have two kinds of bookable things,
**Park Bookables** (where the park team is the delivery org)
and **Partner Bookables** (where the CTO is the delivery org).

.. uml::

   class "CTO" as cto <<org>> {
      org_id
   }
   class "Park\nTeam" as pt <<org>> {
      org_id
      park_id
   }
   class "Park" as park {
      park_id
   }
   pt --* park
   class "Commercial\nPermit" as cp {
      park_id
      cto_org_id
      valid_from
      valid_until
      status
   }
   park *-- cp
   cto *-- cp

   abstract class "Bookable\nThing" as bt {
      bookable_thing_id
   }
   class "Park\nBookable" as park_bt extends bt {
      bookable_thing_id
      park_org_id
   }
   class "Partner\nBookable" as partner_bt extends bt {
      bookable_thing_id
      cto_org_id
   }
   pt <-- park_bt
   cto <-- partner_bt

Note how the Commercial Permit has a validity period.
This means we can limit the CTO from creating availabilities
outside the validity period of their Commercial Permit(s).


.. uml::

   class "CTO" as cto <<org>> {
      org_id
   }
   class "Park\nTeam" as pt <<org>> {
      org_id
      park_id
   }
   class "Park" as park {
      park_id
   }
   pt --* park
   class "Commercial\nPermit" as cp {
      park_id
      cto_org_id
      valid_from
      valid_until
      status
   }
   park *-- cp
   cto *-- cp

   class "Park\nBookable" as park_bt {
      bookable_thing_id
      park_org_id
   }
   class "Partner\nBookable" as partner_bt {
      bookable_thing_id
      cto_org_id
   }
   pt <-- park_bt
   cto <-- partner_bt

   abstract class "Availability" as availability {
      bookable_thing_id
      from_datetime
      to_datetime
      status()
   }
   note "status() reflects bookings\n(availability may be negated)" as N0
   N0 .. availability
   class "Park\nBookable\nAvailability" as park_availability extends availability {
      bookable_thing_id
      from_datetime
      to_datetime
      status()
   }
   
   class "Partner\nBookable\nAvailability" as partner_availability extends availability {
      bookable_thing_id
      from_datetime
      to_datetime
      status()
   }
   park_bt <-- park_availability
   partner_bt <-- partner_availability

   note "check constraint:\npartner bookable availabilities can\nonly be created for times when\na valid Commercial Permit exists." as N1
   partner_availability .. N1
   cp .. N1
   note "when permit status changes,\nthen the derived status()\nof the partner availability\nmay change too.\ne.g. if a permit status is revoked,\ntheir tours may be unbookable,\nexisting bookings may become\ncancellations pending, etc." as N2
   partner_availability .. N2
   cp .. N2
   
