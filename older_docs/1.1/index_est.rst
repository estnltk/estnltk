.. estnltk documentation master file, created by
   sphinx-quickstart on Fri Nov 28 13:32:28 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================================================================================
Estnltk --- Avatud lähtekoodiga teegid eestikeelsete vabatektside lihtsamaks töötlemiseks
==============================================================================================

Estnltk on kogumik Python 2.7/Python 3.4 teeke, mis pakuvad eestikeelsete vabatekstide töötlemiseks vajalikke baasoperatsioone.
Projekt on rahastatud `Eesti Keeletehnoloogia Riikliku Programmi`_ alamprojekti `EKT57`_ vahenditest.
Kuigi eesti keele töötlemiseks on juba loodud üksjagu keeletehnoloogilisi tööriistu, pole seniste tööriistade omavaheline liidestamine, olgu siis rakenduste loomise või uurimustöö eesmärgil, olnud eriti lihtne.
Tüüpiliselt on olnud tarvis teha lisatööd rakendusespetsiifiliste liideste loomisel.

.. _Eesti Keeletehnoloogia Riikliku Programmi: https://www.keeletehnoloogia.ee/
.. _EKT57: https://www.keeletehnoloogia.ee/et/ekt-projektid/estnltk-pythoni-teegid-eestikeelsete-vabatektside-lihtsamaks-tootlemiseks

Teiseks probleemiks on tööriistade hajutatus: paljud tööriistad on veebis laiali ning neid on keeruline üles leida.
Kuigi leiduvad keeletehnoloogia materjale ja tulemusi tutvustavad veebilehed `keeleveeb.ee`_ and `EKT`_, `EKKTT`_, on tudengitel ning valdkonnaga mitte kursis olevatel asjahuvilistel keeruline nende põhjal keeletehnoloogilise arendustööga algust teha.

.. _keeleveeb.ee: http://www.keeleveeb.ee/
.. _EKT: https://www.keeletehnoloogia.ee/et/EKT2011-2017-programm-uuendet.pdf/view
.. _EKKTT: https://www.keeletehnoloogia.ee/et

.. TODO: kontrollida üle see lehekülgede loend

Käesoleva projekti eesmärgiks ongi siduda olemasolevad avatud lähtekoodiga tööriistad kokku üheks keeletehnoloogiliste tööriistade kogumikuks, et pakkuda tuge järgmistele keeletöötluse baasoperatsioonidele:

* Teksti tükeldamine sõnadeks ja lauseteks
* Morfoloogiline analüüs ja süntees
* Sõnade lemmatiseerimine
* Osalausestamine
* Ajaväljendite tuvastamine
* Nimeüksuste tuvastamine
* Verbiahelate tuvastamine
* Eesti Wordnet'i liidestamine

Eeltoodud nimekiri ei sisalda kindlasti kõiki olemasolevaid tööriistu, ent peaks olema siiski piisavalt suur, et katta vabatekstide töötlemise baasjuhud.
Loodame tulevikus seda nimekirja ka täiendada uute tööriistadega.

Kasutusjuhised
=========

.. toctree::
    :maxdepth: 2
    
    installation.rst

    tutorials/textdiagnostics_est.rst
    tutorials/tokenization_est.rst
    tutorials/morf_analysis_est.rst
    tutorials/clause_segmenter_est.rst
    tutorials/ner_est.rst
    tutorials/timex_est.rst
    tutorials/verbchain_est.rst


API kirjeldus
=============

.. toctree::
   :maxdepth: 2

   estnltk.rst
   modules.rst
   estnltk.textclassifier.rst
   estnltk.estner.rst
   

Indeksid ja tabelid
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
