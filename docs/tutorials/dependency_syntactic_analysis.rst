===============================
 Dependency syntactic analysis
===============================

EstNLTK provides wrappers for two syntactic analysers: `MaltParser`_ and `VISLCG3 based syntactic analyser of Estonian`_. 
MaltParser based syntactic analysis is distributed with EstNLTK and can be applied by default. VISLCG3 based syntactic analysis has a requirement that VISLCG3 must be installed into the system first (see :ref:`ref-vislcg-install` for further instructions).

.. _MaltParser: http://www.maltparser.org/
.. _VISLCG3 based syntactic analyser of Estonian: https://github.com/EstSyntax/EstCG 

Both analysers are using a common syntactic analysis tagset, which is introduced in the `documentation`_.

.. _documentation: https://korpused.keeleressursid.ee/syntaks/dokumendid/syntaksiliides_en.pdf

Basic usage
=============

Calling :py:meth:`~estnltk.text.Text.tag_syntax` method of the :class:`~estnltk.text.Text` instance evokes the syntactic analysis on the text, using the default syntactic parser (MaltParser)::

    from estnltk.names import LAYER_CONLL
    from estnltk import Text
    from pprint import pprint

    text = Text('Ilus suur karvane kass nurrus punasel diivanil')
    text.tag_syntax()

    pprint( text[LAYER_CONLL] )

Results of the analysis are stored in the layer named ``LAYER_CONLL`` ( note that the name of the layer depends on the parser: in case of VISLCG3, the name would be ``LAYER_VISLCG3`` ). The example produces the following output::

    [{'end': 4, 'parser_out': [['@AN>', 3]], 'sent_id': 0, 'start': 0},
     {'end': 9, 'parser_out': [['@AN>', 3]], 'sent_id': 0, 'start': 5},
     {'end': 17, 'parser_out': [['@AN>', 3]], 'sent_id': 0, 'start': 10},
     {'end': 22, 'parser_out': [['@SUBJ', 4]], 'sent_id': 0, 'start': 18},
     {'end': 29, 'parser_out': [['ROOT', -1]], 'sent_id': 0, 'start': 23},
     {'end': 37, 'parser_out': [['@AN>', 6]], 'sent_id': 0, 'start': 30},
     {'end': 46, 'parser_out': [['@ADVL', 4]], 'sent_id': 0, 'start': 38}]

The layer contains a ``dict`` for each word in the text, indicating the location of the word (in ``start`` and ``end`` attributes, and in the sentence identifier ``sent_id``), and dependency syntactic relations associated with the word (in the attribute ``parser_out``).

    The attribute ``parser_out`` contains a list of dependency syntactic relations. 
    Each relation is a list where:

    * the first item is the *syntactic function label* (e.g. ``'@SUBJ'`` stands for *subject* and ``'@OBJ'`` for *object*, see `documentation`_ for details), and 
    * the second item (the integer) is the index of its governing word in the sentence. 

    The governing word index ``-1`` marks that the current word is the root node of the tree, and this is also supported by syntactic function label ``'ROOT'`` from MaltParser output. VISLCG3 does not use the label ``'ROOT'``, and only governing word index ``-1`` is used for marking the root in VISLCG3's output.

The tree structure described in the previous example of MaltParser's output can be illustrated with the following dependency tree:

.. image:: _static/nurruvkass_2.png
   :scale: 60%
   :alt: Purring cat example

EstNLTK also provides API for processing and making queries on trees built from syntactic analyses, see :ref:`ref-tree-structure` for further details.

VISLCG3 based syntactic analysis
=================================

.. VISLCG3 based syntactic analysis in EstNLTK is a re-implementation of the `Estonian Constraint Grammar`_ syntactic analysis pipeline. 

.. _Estonian Constraint Grammar: https://github.com/EstSyntax/EstCG 

.. _ref-vislcg-install:

Installation & usage
---------------------

In order to use VISLCG3 based syntactic analysis, the VISLCG3 parser must be installed into the system. The information about the parser is distributed in the `Constraint Grammar's Google Group`_, and this is also the place to look for the most compact guide about getting & installing `the latest version of the parser`_.

.. _Constraint Grammar's Google Group: http://groups.google.com/group/constraint-grammar
.. _the latest version of the parser: https://groups.google.com/d/msg/constraint-grammar/hXsbzyyhIVI/nHXRnOomf9wJ

By default, EstNLTK expects that the directory containing VISLCG3 parser's executable (``vislcg3`` in UNIX, ``vislcg3.exe`` in Windows) is accessible from system's environment variable ``PATH``. If this requirement is satisfied, the EstNLTK should always be able to execute the parser.

Alternatively ( if the parser's directory is not in system's ``PATH`` ), the full path to the VISLCG3 executable can be provided via the input argument ``vislcg_cmd`` of the parser's class :class:`~estnltk.syntax.vislcg3_syntax.VISLCG3Pipeline`. Then the parser instance can be added as a custom parser of a :class:`~estnltk.text.Text` object via the input argument ``syntactic_parser``::

    from estnltk.syntax.parsers import VISLCG3Parser
    from estnltk.names import LAYER_VISLCG3
    from estnltk import Text
    from pprint import pprint
    
    # Create a new VISLCG3 parser instance, and provide 
    # the exact path of the VISLCG3's installation directory
    parser = VISLCG3Parser( vislcg_cmd='C:\\Program Files\\vislcg3' )
    
    # Create a new text object and override the default
    # parser with the VISLCG3 parser
    text = Text( 'Maril oli väike tall', syntactic_parser=parser )
    
    # Tag syntax: now VISLCG3Parser is used 
    text.tag_syntax()

    pprint( text[LAYER_VISLCG3] )
    
This example should produce the following output::

    [{'end': 5, 'parser_out': [['@ADVL', 1]], 'sent_id': 0, 'start': 0},
     {'end': 9, 'parser_out': [['@FMV', -1]], 'sent_id': 0, 'start': 6},
     {'end': 15, 'parser_out': [['@AN>', 3]], 'sent_id': 0, 'start': 10},
     {'end': 20, 'parser_out': [['@SUBJ', 1]], 'sent_id': 0, 'start': 16}]

Note that the root node (the node with governing word index ``-1``) has a syntactic label ``'@FMV'`` instead of ``'ROOT'``, indicating that the VISLCG3Parser was used instead of the MaltParser.
    

Text interface
--------------

Stand-alone parser
------------------

MaltParser based syntactic analysis
====================================

Text interface
--------------

Stand-alone parser
------------------


.. _ref-tree-structure:

Tree datastructure
===================

.. a :class:`~estnltk.syntax.utils.Tree` datastructure

Dependency graphs
------------------

NLTK's Tree objects
--------------------

Input from corpus
===================

