# Postgres Tutorials

For running the code in the tutorials, you'll need to setup [a Postgres database](https://www.postgresql.org/) and install `psycopg2`:

``` 
pip install psycopg2-binary
``` 

Tutorials:

* [main tutorial] [storing_text_objects_in_postgres](storing_text_objects_in_postgres.ipynb) demonstrates how to store and query text objects in the Postgres database.

* [extracting_and_storing_addresses](extracting_and_storing_addresses.ipynb) demonstrates how to extract addresses from text using `AddressGrammarTagger` and store results in the database.

* [storing_text_objects_with_syntax_layer_in_postgres.ipynb](storing_text_objects_with_syntax_layer_in_postgres.ipynb) demonstrates how to store and query EstNLTK Text objects with syntax layer in the database.

* [sampling_texts_and_layers_in_postgres.ipynb](sampling_texts_and_layers_in_postgres.ipynb) demonstrates how to shuffle a text collection and how to draw samples from a text collection stored in the database.
 

