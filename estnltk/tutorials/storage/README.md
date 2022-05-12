# Postgres Tutorials

For running the code in the tutorials, you'll need to setup [a Postgres database](https://www.postgresql.org/) and install `psycopg2`:

``` 
pip install psycopg2-binary
``` 

Tutorials:

* [storing_text_objects_in_postgres](storing_text_objects_in_postgres.ipynb) demonstrates how to store and query text objects in the Postgres database.

* [extracting_and_storing_addresses](extracting_and_storing_addresses.ipynb) demonstrates how to extract addresses from text using `AddressGrammarTagger` and store results in the Postgres database.
