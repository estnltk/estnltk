=================================
Working with Estonian Koondkorpus
=================================

This tutorial describes how to work with `Eesti Koondkorpus`_ and import the files in TEI format
to JSON format used by Estnltk.
After this conversion, you can check (:ref:`database_tutorial`) to see how you could import all these documents
to a fast searchable text database.
First, dowload all the XML TEI format files to your computer, into a folder ``corpora/koond``.
Check the subcategories of the site to find the download links.

.. _Eesti Koondkorpus: http://www.cl.ut.ee/korpused/segakorpus/

On my computer, I have the following list of files::

    ls -1 corpora/koond/

    Agraarteadus.zip
    Arvutitehnika.zip
    Doktoritood.zip
    EestiArst.zip
    Ekspress.zip
    foorum_uudisgrupp_kommentaar.zip
    Horisont.zip
    Ilukirjandus.zip
    Kroonika.zip
    LaaneElu.zip
    Luup.zip
    Maaleht.zip
    Paevaleht.zip
    Postimees.zip
    Riigikogu.zip
    Seadused.zip
    SLOleht.tar.gz
    Teadusartiklid.zip
    Valgamaalane.zip

Next, we go into this directory and unzip all the files.::

    cd corpora/koond/
    unzip "*.zip"

As a result, we have a bunch of folders with structure similar below::

    ├── Kroonika
    │   ├── bin
    │   │   ├── koondkorpus_main_header.xml
    │   │   └── tei_corpus.rng
    │   └── Kroon
    │       ├── bin
    │       │   └── header_aja_kroonika.xml
    │       └── kroonika
    │           ├── kroonika_2000
    │           │   ├── aja_kr_2000_12_08.xml
    │           │   ├── aja_kr_2000_12_15.xml
    │           │   ├── aja_kr_2000_12_22.xml
    │           │   └── aja_kr_2000_12_29.xml
    │           ├── kroonika_2001
    │           │   ├── aja_kr_2001_01_05.xml
    │           │   ├── aja_kr_2001_01_12.xml
    │           │   ├── aja_kr_2001_01_19.xml
    │           │   ├── aja_kr_2001_01_22.xml

Folders ``bin`` contain headers and corpus descriptions and can go hiearchially down the way.
If we are only interested in the actual articles themselves, we should ignore all files that contain ``bin`` in their
path and only use files that end with ``.xml``.

.. highlight:: python

Anyway, here is a script that tries its best at doing some basic conversion::

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals, print_function, absolute_import

    import os
    import os.path
    import argparse
    import logging

    from estnltk.teicorpus import parse_tei_corpus
    from estnltk.corpus import write_document

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('koondkonverter')


    def get_target(fnm):
        if 'drtood' in fnm:
            return 'dissertatsioon'
        if 'ilukirjandus' in fnm:
            return 'tervikteos'
        if 'seadused' in fnm:
            return 'seadus'
        if 'EestiArst' in fnm:
            return 'ajakirjanumber'
        if 'foorum' in fnm:
            return 'teema'
        if 'kommentaarid' in fnm:
            return 'kommentaarid'
        if 'uudisgrupid' in fnm:
            return 'uudisgrupi_salvestus'
        if 'jututoad' in fnm:
            return 'jututoavestlus'
        if 'stenogrammid' in fnm:
            return 'stenogramm'
        return 'artikkel'


    def process(start_dir, out_dir):
        for dirpath, dirnames, filenames in os.walk(start_dir):
            if len(dirnames) > 0 or len(filenames) == 0 or 'bin' in dirpath:
                continue
            for fnm in filenames:
                full_fnm = os.path.join(dirpath, fnm)
                out_prefix = os.path.join(out_dir, fnm)
                target = get_target(full_fnm)
                if os.path.exists(out_prefix + '_0.txt'):
                    logger.info('Skipping file {0}, because it seems to be already processed'.format(full_fnm))
                    continue
                logger.info('Processing file {0} with target {1}'.format(full_fnm, target))
                docs = parse_tei_corpus(full_fnm, target=target)
                for doc_id, doc in enumerate(docs):
                    out_fnm = '{0}_{1}.txt'.format(out_prefix, doc_id)
                    logger.info('Writing document {0}'.format(out_fnm))
                    write_document(doc, out_fnm)


    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="Convert a bunch of TEI XML files to Estnltk JSON files")
        parser.add_argument('startdir', type=str, help='The path of the downloaded and extracted koondkorpus files')
        parser.add_argument('outdir', type=str, help='The directory to store output results')
        args = parser.parse_args()

        process(args.startdir, args.outdir)

Create an output directory ``corpora/converted`` for the results and run the scripts with appropriate parameters::

    python3 -m estnltk.examples.convert_koondkorpus corpora/koond corpora/converted

The results can be downloaded from here: http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip .