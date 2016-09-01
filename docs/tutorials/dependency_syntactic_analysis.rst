===============================
 Dependency syntactic analysis
===============================

EstNLTK provides wrappers for two syntactic analysers: `MaltParser`_ and `VISLCG3 based syntactic analyser of Estonian`_. 
MaltParser based syntactic analysis is distributed with EstNLTK and can be applied by default. VISLCG3 based syntactic analysis has a requirement that VISLCG3 must be installed into the system first (see :ref:`ref-vislcg-install` for further instructions).

.. _MaltParser: http://www.maltparser.org/
.. _VISLCG3 based syntactic analyser of Estonian: https://github.com/EstSyntax/EstCG 

Both analysers are using a common syntactic analysis tagset, which is introduced in the `documentation`_.

.. _documentation: https://korpused.keeleressursid.ee/syntaks/dokumendid/syntaksiliides_en.pdf

.. _ref-basic-usage:

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

    * the first item is the **syntactic function label** (e.g. ``'@SUBJ'`` stands for *subject* and ``'@OBJ'`` for *object*, see `documentation`_ for details), and 
    * the second item (the integer) is the index of its **governing word** in the sentence. 

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

Installation & configuration
----------------------------

In order to use VISLCG3 based syntactic analysis, the VISLCG3 parser must be installed into the system. The information about the parser is distributed in the `Constraint Grammar's Google Group`_, and this is also the place to look for the most compact guide about getting & installing `the latest version of the parser`_.

.. _Constraint Grammar's Google Group: http://groups.google.com/group/constraint-grammar
.. _the latest version of the parser: https://groups.google.com/d/msg/constraint-grammar/hXsbzyyhIVI/nHXRnOomf9wJ

By default, EstNLTK expects that the directory containing VISLCG3 parser's executable (``vislcg3`` in UNIX, ``vislcg3.exe`` in Windows) is accessible from system's environment variable ``PATH``. If this requirement is satisfied, the EstNLTK should always be able to execute the parser.

Alternatively ( if the parser's directory is not in system's ``PATH`` ), the full path to the VISLCG3 executable can be provided via the input argument ``vislcg_cmd`` of the parser's class :class:`~estnltk.syntax.parsers.VISLCG3Parser`. Then the parser instance can be added as a custom parser of a :class:`~estnltk.text.Text` object via the input argument ``syntactic_parser``::

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

:class:`~estnltk.text.Text` object provides the method :py:meth:`~estnltk.text.Text.tag_syntax_vislcg3`, which changes the default parser to a new instance of :class:`~estnltk.syntax.parsers.VISLCG3Parser`, and parses the text. The results of the parsing are stored in the layer ``LAYER_VISLCG3``::

    from estnltk.names import LAYER_VISLCG3
    from estnltk import Text
    from pprint import pprint
    
    text = Text( 'Valge jänes jooksis metsas' )
    
    # Tag text with VISLCG3 parser
    text.tag_syntax_vislcg3()

    pprint( text[LAYER_VISLCG3] )

This example should produce the following output::

    [{'end': 5, 'parser_out': [['@AN>', 1]], 'sent_id': 0, 'start': 0},
     {'end': 11, 'parser_out': [['@SUBJ', 2]], 'sent_id': 0, 'start': 6},
     {'end': 19, 'parser_out': [['@FMV', -1]], 'sent_id': 0, 'start': 12},
     {'end': 26, 'parser_out': [['@ADVL', 2]], 'sent_id': 0, 'start': 20}]

For each word in the text, the layer ``LAYER_VISLCG3`` contains a ``dict`` storing the syntactic analysis of the word (see :ref:`ref-basic-usage` for details).
The method :py:meth:`~estnltk.text.Text.syntax_trees` can be used to build queryable syntactic trees from  ``LAYER_VISLCG3``, see :ref:`ref-tree-structure` for details.

.. note::

    The method :py:meth:`~estnltk.text.Text.tag_syntax_vislcg3` can only be used if the VISLCG3's directory is in system's environment variable ``PATH``.
    For an alternative way of providing the parser with the location of the VISLCG3's directory, see :ref:`ref-vislcg-install`.

VISLCG3Parser class
-------------------

The class :class:`~estnltk.syntax.parsers.VISLCG3Parser` can be used to customize the settings of VISLCG3 based syntactic analysis (e.g. provide the location of the parser, and the pipeline of rules), to parse the text with the custom settings, and to get a custom output (e.g. the original output of the parser).

:class:`~estnltk.syntax.parsers.VISLCG3Parser` can be initiated with the following keyword arguments:

* ``vislcg_cmd`` -- a full path to the VISLCG3 installation directory;
* ``pipeline`` -- a list of rule file names that are executed by the VISLCG3Parser, in the order of execution;
* ``rules_dir`` -- a default directory from where to find rules that are executed on the pipeline (used for rule files without path);

After the :class:`~estnltk.syntax.parsers.VISLCG3Parser` has been initiated, its method  :py:meth:`~estnltk.syntax.parsers.VISLCG3Parser.parse_text` can be used to parse a :class:`~estnltk.text.Text` object. 
In addition to the Text, the method can take the following keyword arguments:

* ``return_type`` -- specifies the format of the data returned of the method. Can be one of the following: ``'text'`` (default), ``'vislcg3'``, ``'trees'``, ``'dep_graphs'``.
* ``keep_old`` -- a boolean specifying whether the initial analysis lines from the output of VISLCG3's should be preserved in the ``LAYER_VISLCG3``. If ``True``, each ``dict`` in the layer will be augmented with attribute ``'init_parser_out'`` containing the initial/old analysis lines (a list of strings);

In the following, some of the usage possibilities of these arguments are introduced in detail.


The initial output of the parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to see the **initial / original output** of the VISLCG3 parser, you can execute the method :py:meth:`~estnltk.syntax.parsers.VISLCG3Parser.parse_text` with the setting ``return_type='vislcg3'`` -- in this case, the method returns a list of lines (strings) from the initial output::

    from estnltk.syntax.parsers import VISLCG3Parser
    from estnltk import Text

    text = Text('Maril oli väike tall')
    parser = VISLCG3Parser()
    initial_output = parser.parse_text(text, return_type='vislcg3')
    
    print( '\n'.join( initial_output) )
    
the code above produces the following output::

    "<s>"
    
    "<Maril>"
            "mari" Ll S com sg ad @ADVL #1->2
    "<oli>"
            "ole" Li V main indic impf ps3 sg ps af @FMV #2->0
    "<väike>"
            "väike" L0 A pos sg nom @AN> #3->4
    "<tall>"
            "tall" L0 S com sg nom @SUBJ #4->2
    "</s>"
    


Note that the results of the analysis are also stored in the input Text object on the layer ``LAYER_VISLCG3``, but the layer does not preserve the original/initial output of the VISLCG3 parser.

.. and changing the ``return_type`` does not change the format of the layer.

In order to preserve the original/initial analysis in the layer ``LAYER_VISLCG3``, the method :py:meth:`~estnltk.syntax.parsers.VISLCG3Parser.parse_text` needs to be executed with the setting ``keep_old=True`` -- in this case, the initial syntactic analysis lines are also stored in the layer, providing each ``dict`` in the layer with the attribute ``'init_parser_out'``::

    from estnltk.syntax.parsers import VISLCG3Parser
    from estnltk.names import LAYER_VISLCG3
    from estnltk import Text
    from pprint import pprint

    text = Text('Maril oli väike tall')
    parser = VISLCG3Parser()
    parser.parse_text(text, keep_old=True)
    
    pprint( text[LAYER_VISLCG3] )

the code above produces the following output::

    [{'end': 5,
      'init_parser_out': ['\t"mari" Ll S com sg ad @ADVL #1->2'],
      'parser_out': [['@ADVL', 1]],
      'sent_id': 0,
      'start': 0},
     {'end': 9,
      'init_parser_out': ['\t"ole" Li V main indic impf ps3 sg ps af @FMV '
                          '#2->0'],
      'parser_out': [['@FMV', -1]],
      'sent_id': 0,
      'start': 6},
     {'end': 15,
      'init_parser_out': ['\t"väike" L0 A pos sg nom @AN> #3->4'],
      'parser_out': [['@AN>', 3]],
      'sent_id': 0,
      'start': 10},
     {'end': 20,
      'init_parser_out': ['\t"tall" L0 S com sg nom @SUBJ #4->2'],
      'parser_out': [['@SUBJ', 1]],
      'sent_id': 0,
      'start': 16}]

The attribute ``'init_parser_out'`` contains a list of analysis lines associated the word -- in case of unsolved ambiguities, there is more than one analysis line for the word.


Using a custom pipeline
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to make a custom pipeline based on the **default pipeline**, you can make a copy of the list in the variable ``estnltk.syntax.vislcg3_syntax.SYNTAX_PIPELINE_1_4``, modify some of the rule file names listed there, and then pass the new list as ``pipeline`` argument to the constructor of :class:`~estnltk.syntax.parsers.VISLCG3Parser`::

    from estnltk.syntax.vislcg3_syntax import SYNTAX_PIPELINE_1_4
    from estnltk.syntax.parsers import VISLCG3Parser
    from estnltk.names import LAYER_VISLCG3
    from estnltk import Text
    from pprint import pprint
    
    my_pipeline = SYNTAX_PIPELINE_1_4[:] # make a copy from the default pipeline
    del my_pipeline[-1]                  # remove the last rule file 
    
    text = Text('Konn hüppas kivilt kivile')
    # Initialize the parser with a custom pipeline:
    parser = VISLCG3Parser( pipeline=my_pipeline )
    # Parse the text
    initial_output = parser.parse_text(text, return_type='vislcg3')
    
    print( '\n'.join( initial_output) )
    
the code above produces the following output::

    "<s>"
    
    "<Konn>"
            "konn" L0 S com sg nom @SUBJ
    "<hüppas>"
            "hüppa" Ls V main indic impf ps3 sg ps af @FMV
    "<kivilt>"
            "kivi" Llt S com sg abl @ADVL
    "<kivile>"
            "kivi" Lle S com sg all @<NN @ADVL
    "</s>"
    

Note that because the last rule file (containing the rules for dependency relations) was removed from the pipeline, the results contain only morphological information and surface-syntactic information (syntactic function labels), but no dependency information (the information in the form *#Number->Number*).

.. note:: About the default pipeline 

    ``estnltk.syntax.vislcg3_syntax.SYNTAX_PIPELINE_1_4`` refers to the rules (\*.rle files) that are stored in EstNLTK's installation directory, at the location pointed by the variable ``estnltk.syntax.vislcg3_syntax.SYNTAX_PATH``.
    
    The original source of the rules is:  http://math.ut.ee/~tiinapl/CGParser.tar.gz 

If you want to provide your own, **alternative pipeline**, you can construct *a list of rule file names with full paths*, and pass them as ``pipeline`` argument to the constructor of :class:`~estnltk.syntax.parsers.VISLCG3Parser`.
Alternatively, you can put only file names to the ``pipeline`` argument, and use the ``rules_dir`` argument to indicate the default directory from which all rules files can be found.

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

