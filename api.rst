API
===

TODO: document the API used by BCE
to create and manage bookings
in the ANBG systems.


get list of bookable things
---------------------------
..for this team, for this park (ANBG)

.. uml::

   actor "parks staff\nANBG Team" as parks_staff
   box "BCE System" #lightblue
      participant BCE
   end box
   parks_staff -> BCE: configure ANBG\nbookable things
   box "Parks System" #lightgreen
      boundary "<<API>>\n/parks/ANBG/bookables\n?team=ANBG_team" as get_list_bookables
      database "bookable\nthings" as bookable_things
   end box
   BCE -> get_list_bookables: GET
   get_list_bookables -> bookable_things: query(\n  park=ANBG,\n  org=ANBG_team\n)

   get_list_bookables -> BCE: json data
   BCE -> parks_staff: show options...
   parks_staff -> BCE: do stuff, etc.


Notes:

* not shown: the GET call is made with an API key.
* if the park doesn't exist, 404
* if the team doesn't exist, empty list returned
* if the team exists but has no bookable things, empty list returned
* TODO: what is the data structure of the returned list?

