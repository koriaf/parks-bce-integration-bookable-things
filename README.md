# Parks/BCE integration

...for bookable things. https://parks-australia-bookable-things.readthedocs.io/

The purpose of this repository is so that TMA and GoSource can collaborate to develop an integration between [Book Canberra Excursions](https://www.bookcanberraexcursions.com.au/) and the Parks Australia systems used by ANBG staff (Australian National Botanic Gardens).

The technichal integration between BCE will probably be at either the [trade portal](https://trade.parksaustralia.gov.au/) or [booking](https://book.parksaustralia.gov.au/) site. These things have lower environments...


## Interesting Links

Note, our FRAPI endpoint might be interesting, it's an example of how we do APIs. It's probably not the API you need :)

Production environments:

* [Public](https://book.parksaustralia.gov.au/)
* [Trade portal](https://trade.parksaustralia.gov.au/)
* [API Spec Browser (FRAPI)](https://apidocs-ecommerce.parksaustralia.gov.au/)

Staging/Testing environments (deployed on command, dress rehearsal for Prod):

* [Public](https://staging.ecommerce.np.cp1.parksaustralia.gov.au/passes/)
* [Trade portal](https://staging.ecommerce.np.cp1.parksaustralia.gov.au/)

Integration (CI/CD, deployed when PRs are merged in our system):

* [Public](https://integration.ecommerce.np.cp1.parksaustralia.gov.au/passes/)
* [Trade portal](https://integration.ecommerce.np.cp1.parksaustralia.gov.au/)
* [FRAPI Endpoint](https://integration.ecommerce.np.cp1.parksaustralia.gov.au/api/frapi/v0/)
