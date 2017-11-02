""""
Test postgres storage functionality.
Usage: python test.py --dbname=<DBNAME> --user=<USER> --password=<PASSWORD>
                      [--host=<HOST> --port=<PORT>]
"""
import argparse

from estnltk import Text
from estnltk.storage.postgres import PostgresStorage, JsonbQuery as Q
from estnltk import storage


def test(storage, table):
    text1 = Text('Ööbik laulab.')
    id1 = storage.insert(table, text1)

    text2 = Text('Mis kell on?')
    id2 = storage.insert(table, text2)

    # test select_by_id
    assert storage.select_by_key(table, id1) == text1
    assert storage.select_by_key(table, id2) == text2

    # test select_all
    res = list(storage.select(table, order_by_key=True))
    assert len(res) == 2
    id_, text = res[0]
    assert id_ == id1
    assert text == text1
    id_, text = res[1]
    assert id_ == id2
    assert text == text2

    # test select
    text1 = Text('mis kell on?').analyse('morphology')
    storage.insert(table, text1)
    text2 = Text('palju kell on?').analyse('morphology')
    storage.insert(table, text2)

    res = list(storage.select(table, query=Q('morph_analysis', lemma='mis')))
    assert len(res) == 1

    res = list(storage.select(table, query=Q('morph_analysis', lemma='kell')))
    assert len(res) == 2

    res = list(storage.select(table, query=Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')))
    assert len(res) == 2

    res = list(storage.select(table, query=Q('morph_analysis', lemma='mis') & Q('morph_analysis', lemma='palju')))
    assert len(res) == 0

    res = list(storage.select(table, query=(Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')) &
                                           Q('morph_analysis', lemma='kell')))
    assert len(res) == 2

    # test find_fingerprint
    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', [{'miss1', 'miss2'}, {'miss3'}]))
    assert len(res) == 0

    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', [{'miss1', 'miss2'}, {'palju'}]))
    assert len(res) == 1

    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', [{'mis', 'miss2'}, {'palju'}]))
    assert len(res) == 1

    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', [{'mis', 'kell'}, {'miss'}]))
    assert len(res) == 1

    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', [{'mis', 'kell'}, {'palju'}]))
    assert len(res) == 2

    res = list(storage.find_fingerprint(table, 'morph_analysis', 'lemma', []))
    assert len(res) == 4


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test postgres storage functionality.')
    parser.add_argument('--dbname', dest='dbname', required=True, help='database name')
    parser.add_argument('--user', dest='user', required=True, help='database user')
    parser.add_argument('--password', dest='password', required=True, help='database user password')
    parser.add_argument('--host', dest='host', help='database host', default='localhost')
    parser.add_argument('--port', dest='port', help='database port', type=int, default=5432)
    args = parser.parse_args()

    storage = PostgresStorage(dbname=args.dbname, user=args.user, password=args.password,
                              host=args.host, port=args.port)

    table = 'tmp'
    storage.create_table(table)
    try:
        test(storage, table)
    finally:
        storage.drop_table(table)
        storage.close()

    print("Tests done!")
