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
   state cancelled #lightgreen
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
