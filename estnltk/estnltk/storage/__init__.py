"""
Module enables to store and search `Text` objects in Postgres database.

For usage examples, see tutorial `estnltk/tutorials/storing_text_objects_in_postgres.ipynb`
"""

# DO not import PostgresStorage, avoid ModuleNotFoundError: No module named 'psycopg2'
# (people should be able to import estnltk.storage.sqlite without running into this error)
#from estnltk.storage.postgres.storage import PostgresStorage
