Security
========


Security model
--------------

REST API is available once some authentication mechanism is attached to the request.
The simplest case is the API key::

    Authorization: Bearer KNxNQ51vFDpu19SeSKEcqup8WzfSS5

The key provided has direct link to the organisation (but not user), and this way
all requests are assumed to be performed on the organisation's behalf.

Another way is to use browser sessions (cookies-based), when the API endpoints are requested
from the same browser when the user is logged in. In this case organisation
must be passed as a parameter (because session is related to the user, not org,
and one user may be part of multiple organisations). To do so please either::

    * provide `auth_org_id` GET parameter (even with POST requests) with org ID value
    * provide `X-parks-org-id` header with org ID value

Your organisation ID is typically known if you use the Parks portal.
If you have only single organisation then the parameter is still required.


Managing API keys
-----------------

To manage API keys please login to the trade portal, pick the organisation you need,
and and then select "Administration->Access Tokens" menu item. This action is available
only to org admins (vs guides or retail sales agents).

