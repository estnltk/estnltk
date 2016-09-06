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
    
    .. note:: 

        If you are familiar with the CONLL data format, you should remember that EstNLTK uses a bit different indexing system than CONLL. In the CONLL data format, word indices typically start at ``1`` and the root node has the parent index ``0``. In EstNLTK, word indices start at ``0`` and the root node has the parent index ``-1``.

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

Alternatively ( if the parser's directory is not in system's ``PATH`` ), the name of the VISLCG3 executable with full path can be provided via the input argument ``vislcg_cmd`` of the parser's class :class:`~estnltk.syntax.parsers.VISLCG3Parser`. Then the parser instance can be added as a custom parser of a :class:`~estnltk.text.Text` object via the keyword argument ``syntactic_parser``::

    from estnltk.syntax.parsers import VISLCG3Parser
    from estnltk.names import LAYER_VISLCG3
    from estnltk import Text
    from pprint import pprint
    
    # Create a new VISLCG3 parser instance, and provide 
    # the name of the VISLCG3 executable with full path 
    parser = VISLCG3Parser( vislcg_cmd='C:\\cg3\\bin\\vislcg3.exe' )
    
    # Create a new text object and override the default
    # parser with the VISLCG3 parser
    text = Text( 'Maril oli väike tall', syntactic_parser=parser )
    
    # Tag syntax: now VISLCG3Parser is used 
    text.tag_syntax()

    pprint( text[LAYER_VISLCG3] )
    
Provided that you are using a Windows machine, and VISLCG3 is installed into the directory ``C:\\cg3\\bin``, the previous example should execute successfully and should produce the following output::

    [{'end': 5, 'parser_out': [['@ADVL', 1]], 'sent_id': 0, 'start': 0},
     {'end': 9, 'parser_out': [['@FMV', -1]], 'sent_id': 0, 'start': 6},
     {'end': 15, 'parser_out': [['@AN>', 3]], 'sent_id': 0, 'start': 10},
     {'end': 20, 'parser_out': [['@SUBJ', 1]], 'sent_id': 0, 'start': 16}]

In the output: note that the root node (the node with governing word index ``-1``) has a syntactic label ``'@FMV'`` instead of ``'ROOT'``, indicating that the VISLCG3Parser was used instead of the MaltParser.

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

The class :class:`~estnltk.syntax.parsers.VISLCG3Parser` can be used to customize the settings of VISLCG3 based syntactic analysis (e.g. provide the location of the parser, and the pipeline of rules), and to get a custom output (e.g. the original output of the parser).

:class:`~estnltk.syntax.parsers.VISLCG3Parser` can be initiated with the following keyword arguments:

* ``vislcg_cmd`` -- the name of VISLCG3 executable with full path (e.g. ``'C:\\cg3\\bin\\vislcg3.exe'``);
* ``pipeline`` -- a list of rule file names that are executed by the VISLCG3Parser, in the order of execution;
* ``rules_dir`` -- a default directory from where to find rules that are executed on the pipeline (used for rule files without path);

After the :class:`~estnltk.syntax.parsers.VISLCG3Parser` has been initiated, its method  :py:meth:`~estnltk.syntax.parsers.VISLCG3Parser.parse_text` can be used to parse a :class:`~estnltk.text.Text` object. 
In addition to the Text, the method can take the following keyword arguments:

* ``return_type`` -- specifies the format of the data returned of the method. Can be one of the following: ``'text'`` (default), ``'vislcg3'``, ``'trees'``, ``'dep_graphs'``.
* ``keep_old`` -- a boolean specifying whether the initial analysis lines from the output of VISLCG3's should be preserved in the ``LAYER_VISLCG3``. If ``True``, each ``dict`` in the layer will be augmented with attribute ``'init_parser_out'`` containing the initial/old analysis lines (a list of strings); Default: ``False``
* ``mark_root`` -- a boolean specifying whether the label of the root node should be renamed to ``ROOT`` (in order to get an output comparable with MaltParser's output); Default: ``False``


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

Syntactic information stored in layers ``LAYER_CONLL`` and ``LAYER_VISLCG3`` can also be processed in the form of :class:`~estnltk.syntax.utils.Tree` objects. This datastructure provides an interface for making queries over the data, e.g. one can find all children of a tree node that satisfy a certain morphological or syntactic constraint. 

The method :py:meth:`~estnltk.text.Text.syntax_trees` can be used to build syntactic trees from a syntactic analyses layer. This method builds trees from all the sentences of the text (note: there can be more than one tree per sentence), and returns a list of :class:`~estnltk.syntax.utils.Tree` objects (see :ref:`ref-tree-object` for details) representing root nodes of these trees. 

In the following example, the input text is first syntactically parsed, and then trees are build from the results of the parsing::

    from estnltk import Text

    text = Text('Hiir hüppas ja kass kargas. Ja vana karu lõi trummi.')
    
    # Tag syntactic analysis (the prerequisite for trees)
    text.tag_syntax()
    # Get syntactic trees (root nodes) of the text
    trees = text.syntax_trees()

The resulting list of :class:`~estnltk.syntax.utils.Tree` objects can be used for making queries over the syntactic structures. In the following example, all nodes labelled ``@SUBJ``, along with the words they govern, are retrieved from the text::

    from estnltk import Text

    text = Text('Hiir hüppas ja kass kargas. Ja vana karu lõi trummi.')
    
    # Tag syntactic analysis (the prerequisite for trees)
    text.tag_syntax()
    # Get syntactic trees (root nodes) of the text
    trees = text.syntax_trees()

    # Analyse trees
    for root in trees:
        # Retrieve nodes labelled SUBJECT
        subject_nodes = root.get_children( label="@SUBJ" )
        for subj_node in subject_nodes:
            # Retrieve children of the subject node (and include the node itself):
            subject_and_children = subj_node.get_children( include_self=True, sorted=True )
            # Print SUBJ phrases (texts) and their syntactic labels
            print( [(node.text, node.labels) for node in subject_and_children] )

the example above produces the following output::

    [('Hiir', ['@SUBJ'])]
    [('kass', ['@SUBJ'])]
    [('vana', ['@AN>']), ('karu', ['@SUBJ'])]

**Specifying the layer.** By default, the method :py:meth:`~estnltk.text.Text.syntax_trees` builds trees from the layer corresponding to the current syntactic parser (a parser that can be passed to the Text object via the keyword argument ``syntactic_parser``). If no syntactic parser has been set, it builds trees from the first layer available, checking firstly for ``LAYER_CONLL`` and secondly for ``LAYER_VISLCG3``. 
If the current parser has not been specified, and there is no syntactic layer available, you should pass the name of the layer to the method via keyword argument ``layer``, in order to direct which syntactic parser should be used for analysing the text::

    from estnltk.names import LAYER_VISLCG3
    
    #  Build syntactic trees from VISLCG3's output 
    trees = text.syntax_trees(layer=LAYER_VISLCG3)

**Trees from a custom layer.** If you want to build trees from a text layer that has the same structure as layers ``LAYER_CONLL`` and ``LAYER_VISLCG3`` (see :ref:`ref-basic-usage`), but a different name, you can use the method :py:meth:`~estnltk.syntax.utils.build_trees_from_text`::

    from estnltk.syntax.utils import build_trees_from_text
    #  Build trees from a custom layer 
    trees = build_trees_from_text( text, layer = 'my_syntactic_layer' )


.. _ref-tree-object:

Tree object and queries
-----------------------

Each :class:`~estnltk.syntax.utils.Tree` object represents a node in the syntactic tree, and allows an access to its governing node (parent), to its children, and to morphological and syntactic information associated with the word token.
The object has following fields:

* ``word_id`` -- integer : index of the corresponding word in the sentence;
* ``sent_id`` -- integer : index of the sentence (that the word belongs to) in the text;
* ``labels`` -- list of syntactic function labels associated with the node (e.g. the label ``'@SUBJ'`` stands for *subject*, see `documentation`_ for details); in case of unsolved ambiguities, multiple functions can be associated with the node;
* ``parent``   -- Tree object : direct parent / head of this node (``None`` if this node is the root node);
* ``children`` -- list of Tree objects : list of all direct children of this node (``None`` if this node is a leaf node);
* ``token`` -- dict : an element from the ``'words'`` layer associated with this node. Can be used to access morphological information associated with the node, e.g. the list of morphological analyses is available from ``thisnode.token['analysis']``, and part-of-speech associated with the node can be accessed via ``thisnode.token['analysis'][0]['partofspeech']``;
* ``text`` -- string : text corresponding to the node; same as ``thisnode.token['text']``;
* ``syntax_token`` -- dict : an element from the syntactic analyses layer (``LAYER_CONLL`` or ``LAYER_VISLCG3``) associated with this node;
* ``parser_output`` -- list of strings : list of analysis lines from the initial output of the parser corresponding to the this node; (``None`` if the initial output has not been preserved (a default setting));

In addition to fields ``parent`` and ``children``, each tree node also provides methods :py:meth:`~estnltk.syntax.utils.Tree.get_root` and :py:meth:`~estnltk.syntax.utils.Tree.get_children` which can be used perform more complex queries on the tree:

* :py:meth:`~estnltk.syntax.utils.Tree.get_root` -- Moves up via the parent links of this tree until reaching the tree with no parents, and returns the parentless tree as the root. Otherwise (if this tree has no parents), returns this tree.
* :py:meth:`~estnltk.syntax.utils.Tree.get_children` -- Recursively collects and returns all subtrees of this tree (if no  arguments are given), or, alternatively, collects and returns subtrees of this tree satisfying some specific criteria (pre-specified in the keyword arguments);

If called without any keyword arguments, the method :py:meth:`~estnltk.syntax.utils.Tree.get_children` returns a list of all subtrees of this tree, including both direct children, grand-children, and ...-grand-children from unrestricted depth. Specific keyword arguments can used to expand or restrict the returned list.

The query can be limited by tree depth using the keyword argument ``depth_limit``::

    # Get all direct children of the tree
    children = tree.get_children( depth_limit=1 )
    
Note that this is the same as::

    # All direct children of the tree
    children = tree.children

They query can be restricted to retrieving only trees that have a specific syntactic function label. The keyword argument ``label`` is used for that::

    # Retrieve all nodes labelled @SUBJ
    subjects = tree.get_children( label="@SUBJ" )

If you want to allow multiple syntactic labels (e.g. ``@SUBJ`` and ``@SUBJ``), you can use ``label_regexp`` which allows to describe the syntactic function label with a regular expression::

    # Retrieve all nodes labelled @SUBJ and @OBJ
    subjects_objects = tree.get_children( label_regexp="(@SUBJ|@OBJ)" )

Constraints can be added also at the morphological level. 
The :class:`~estnltk.mw_verbs.utils.WordTemplate` object can be used to describe desirable morphological features that the returned words (tree nodes) should have::

    from estnltk.mw_verbs.utils import WordTemplate
    from estnltk.names import POSTAG, FORM
    
    # word template matching all infinite verbs
    verb_inf = WordTemplate({POSTAG:'V', FORM:'^(da|des|ma|tama|ta|maks|mas|mast|nud|tud|v|mata)$'})

In the previous example, the created template ``verb_inf`` requires that a word matching the template must be a verb (``POSTAG:'V'``), and its morphological form must match the regular expression listing all forms of the infinite verbs (``'^(da|des|ma|tama|ta|maks|mas|mast|nud|tud|v|mata)$'``). The template can be passed to the the method :py:meth:`~estnltk.syntax.utils.Tree.get_children` via the keyword argument ``word_template`` to set the morphological  constraints::

    from estnltk.mw_verbs.utils import WordTemplate
    from estnltk.names import POSTAG, FORM
    
    # word template matching all infinite verbs
    verb_inf = WordTemplate({POSTAG:'V', FORM:'^(da|des|ma|tama|ta|maks|mas|mast|nud|tud|v|mata)$'})
    
    # retrieve all infinite verbs from the children of this tree
    inf_verbs = tree.get_children( word_template=verb_inf )

If both morphological and syntactic constraints are used in a query, only nodes satisfying all the constraints are returned::

    from estnltk.mw_verbs.utils import WordTemplate
    from estnltk.names import POSTAG, FORM, ROOT
    
    # word template matching all infinite verbs
    verb_inf = WordTemplate({POSTAG:'V', FORM:'^(da|des|ma|tama|ta|maks|mas|mast|nud|tud|v|mata)$'})
    
    # retrieve all infinite verbs that function as objects
    inf_verbs = tree.get_children( word_template=verb_inf, label="@OBJ" )

Sometimes it is desirable that the tree itself is also checked for and, in case of the match, included in the list of returned trees. The keyword argument ``include_self=True`` can be used for that purpose::

    # Retrieve all nodes labelled @SUBJ, @OBJ or ROOT
    subjects_objects_roots = tree.get_children( label_regexp="(@SUBJ|ROOT|@OBJ)", include_self=True )

And finally, to ensure that all the returned trees are in the order of words in text, the keyword argument ``sorted=True`` can be used::

    # Retrieve all nodes labelled @SUBJ, ROOT, @OBJ, and sort them according to word order in text
    subj_verb_obj = tree.get_children( label_regexp="(@SUBJ|ROOT|@OBJ)", include_self=True, sorted=True )

This forces trees to be sorted ascendingly by their ``word_id`` values.

.. _ref-nltk-interface:

The NLTK interface
------------------

EstNLTK also provides an interface for converting its :class:`~estnltk.syntax.utils.Tree` objects to `NLTK`_'s corresponding datastructures: dependency graphs and trees.

.. _NLTK: http://www.nltk.org/


Dependency graphs
~~~~~~~~~~~~~~~~~~~

:class:`~estnltk.syntax.utils.Tree` object has a method :py:meth:`~estnltk.syntax.utils.Tree.as_dependencygraph` which constructs NLTK's `DependencyGraph`_ object from the tree::

    from estnltk import Text
    from pprint import pprint

    text = Text('Ja vana karu lõi trummi.')
    
    # Tag syntactic analysis (the prerequisite for trees)
    text.tag_syntax()
    
    # Get syntactic trees (root nodes) of the text
    trees = text.syntax_trees()
    
    # Convert EstNLTK's tree to dependencygraph
    dependency_graph = trees[0].as_dependencygraph()
    
    # Represent syntactic relations as PARENT-RELATION-CHILD triples
    pprint( list(dependency_graph.triples()) )

::

     [(('lõi', 'V'), '@J', ('Ja', 'J')),
      (('lõi', 'V'), '@SUBJ', ('karu', 'S')),
      (('karu', 'S'), '@AN>', ('vana', 'A')),
      (('lõi', 'V'), '@OBJ', ('trummi', 'S')),
      (('trummi', 'S'), 'xxx', ('.', 'Z'))]

.. Note: by default, the returned dependencygraph contains only syntactic information, and no morphological level information. 

.. _DependencyGraph: http://www.nltk.org/_modules/nltk/parse/dependencygraph.html

NLTK's Tree objects
~~~~~~~~~~~~~~~~~~~

The method :py:meth:`~estnltk.syntax.utils.Tree.as_nltk_tree` can be used to convert EstNLTK's :class:`~estnltk.syntax.utils.Tree` object to `NLTK's Tree`_ object::

    from estnltk import Text

    text = Text('Ja vana karu lõi trummi.')
    
    # Tag syntactic analysis (the prerequisite for trees)
    text.tag_syntax()
    
    # Get syntactic trees (root nodes) of the text
    trees = text.syntax_trees()
    
    # Convert EstNLTK's tree to NLTK's tree
    nltk_tree = trees[0].as_nltk_tree()
    
    # Output a parenthesized representation of the tree
    print( nltk_tree )

::

    (lõi Ja (karu vana) (trummi .))


.. _NLTK's Tree: http://www.nltk.org/_modules/nltk/tree.html


Importing corpus from a file
=============================

Import CG3 format file
----------------------

The method :py:meth:`~estnltk.syntax.utils.read_text_from_cg3_file` can be used to import a :class:`~estnltk.text.Text` object from a file containing VISLCG3 format syntactic annotations::

    from estnltk.syntax.utils import read_text_from_cg3_file
    
    text = read_text_from_cg3_file( 'ilu_indrikson.inforem' )

The format of the input file is expected to be the same as the format used in the `Estonian Dependency Treebank`_ (the format of *.inforem* files). 
In the example above, the :class:`~estnltk.text.Text` object is constructed from the sentences of the file, and syntactic information is attached to the object as layer ``LAYER_VISLCG3``::

    from pprint import pprint
    
    from estnltk.names import LAYER_VISLCG3
    from estnltk.syntax.utils import read_text_from_cg3_file

    # re-construct text from file
    text = read_text_from_cg3_file( 'ilu_indrikson.inforem' )
    
    # Print the first sentence of the text
    print( text.sentence_texts[0] )

    # Represent syntactic relations as PARENT-RELATION-CHILD triples
    trees = text.syntax_trees(layer=LAYER_VISLCG3)
    pprint( list(trees[0].as_dependencygraph().triples()) )
    
Provided that you have the file ``'ilu_indrikson.inforem'`` ( from `Estonian Dependency Treebank`_ ) available at the same directory as the script above, the script should produce the following output::

    Sõna  "  Lufthansa  "  ei  kõlanud  Indriksoni  kodus  ammu  erakordselt  .
    [(('kõlanud', None), '@SUBJ', ('Sõna', None)),
     (('Sõna', None), 'xxx', ('"', None)),
     (('Sõna', None), '@<NN', ('Lufthansa', None)),
     (('Lufthansa', None), 'xxx', ('"', None)),
     (('kõlanud', None), '@NEG', ('ei', None)),
     (('kõlanud', None), '@ADVL', ('kodus', None)),
     (('kodus', None), '@NN>', ('Indriksoni', None)),
     (('kõlanud', None), '@ADVL', ('ammu', None)),
     (('kõlanud', None), '@ADVL', ('erakordselt', None)),
     (('erakordselt', None), 'xxx', ('.', None))]


.. _Estonian Dependency Treebank: https://github.com/EstSyntax/EDT

.. note:: **Quirks of the import method**

    1) The import method assumes that the input file is in ``UTF-8`` encoding;
    
    2) The import method converts word indices in the syntactic annotation to EstNLTK's format: word indices will start at ``0``, and the root node will have the parent index ``-1``;
    
    3) Be aware that the import method *does not* import *morphological annotations*. As there is no guarantee that morphological annotations in the file are compatible with EstNLTK's format of morphological analysis (e.g. annotations from `Estonian Dependency Treebank`_ are not), these annotations will be skipped and the resulting Text object has no layer of morphological analyses. If you want to make queries involving morphological constraints, you should first add the layer via method :py:func:`~estnltk.text.Text.tag_analysis`.
    
    4) When reconstructing the text, the method :py:meth:`~estnltk.syntax.utils.read_text_from_cg3_file` tries to preserve the original tokenization used in the file. In order to distinguish multiword tokens (e.g. ``'Rio de Jainero'`` as a single word) from ordinary tokens, the method re-constructs the text in a way that words are separated by double space (``'  '``), and a single space (``' '``) is reserved for marking the space in a multiword. In order to preserve sentence boundaries, sentence endings are marked with newlines (``'\n'``).
    

.. note:: **Fixing the input**

    1) By default, words that have parent index referring to theirselves (self-links) are fixed: they will be linked to a previous word in the sentence; if there is no previous word, then to the next word in the sentence; and if the word is the only word in the sentence, the link will obtain the value ``-1``;
    
    2) When importing the corpus from a manually annotated file (for instance, from `Estonian Dependency Treebank`_), it could be useful to apply several post-correction steps in order to ensure validity of the data. This can be done by passing keyword argument settings ``clean_up=True``, ``fix_sent_tags=True`` and ``fix_out_of_sent=True`` to the method :py:meth:`~estnltk.syntax.utils.read_text_from_cg3_file`:
    
        * ``clean_up=True`` -- switches on the clean-up method, which contains routines for handling ``fix_sent_tags=True`` and ``fix_out_of_sent=True``;
        
        * ``fix_sent_tags=True`` -- removes analyses mistakenly added to sentence tags (``<s>`` and ``</s>``);
        
        * ``fix_out_of_sent=True`` -- fixes syntactic links pointing out-of-the-sentence; employs a similar logic as is used for fixing self-links;


Import CONLL format file
------------------------

The method :py:meth:`~estnltk.syntax.utils.read_text_from_conll_file` can be used to import a :class:`~estnltk.text.Text` object from a file containing syntactic annotations in the CONLL format::

    from estnltk.syntax.utils import read_text_from_conll_file
    
    text = read_text_from_conll_file( 'et-ud-dev.conllu' )

The format of the input file is expected to be either `CONLL-X`_ or `CONLL-U`_. The method imports information about the sentence boundaries, the word tokenization (the field ``FORM``), and dependency syntactic information (from fields ``HEAD`` and ``DEPREL``), and reconstructs a :class:`~estnltk.text.Text` object based on that information. The resulting :class:`~estnltk.text.Text` object has the layer ``LAYER_CONLL`` containing the syntactic information::

    from pprint import pprint
    
    from estnltk.names import LAYER_CONLL
    from estnltk.syntax.utils import read_text_from_conll_file

    # re-construct text from file
    text = read_text_from_conll_file( 'et-ud-dev.conllu' )
    
    # Print the first sentence of the text
    print( text.sentence_texts[0] )

    # Represent syntactic relations as PARENT-RELATION-CHILD triples
    trees = text.syntax_trees(layer=LAYER_CONLL)
    pprint( list(trees[0].as_dependencygraph().triples()) )

Provided that you have the file ``'et-ud-dev.conllu'`` ( from `The Estonian UD treebank`_ ) available at the same directory as the script above, the script should produce the following output::

    Ta  oli  tulnud  jala  juba  üle  viie  kilomeetri  ,  sest  siia  ,  selle  lossi  juurde  ,  ei  viinud  ühtegi  autoteed  .
    [(('tulnud', None), 'nsubj', ('Ta', None)),
     (('tulnud', None), 'aux', ('oli', None)),
     (('tulnud', None), 'advmod', ('jala', None)),
     (('tulnud', None), 'advmod', ('juba', None)),
     (('tulnud', None), 'nmod', ('kilomeetri', None)),
     (('kilomeetri', None), 'case', ('üle', None)),
     (('kilomeetri', None), 'nummod', ('viie', None)),
     (('tulnud', None), 'dep', ('viinud', None)),
     (('viinud', None), 'punct', (',', None)),
     (('viinud', None), 'mark', ('sest', None)),
     (('viinud', None), 'advmod', ('siia', None)),
     (('siia', None), 'nmod', ('lossi', None)),
     (('lossi', None), 'det', ('selle', None)),
     (('lossi', None), 'case', ('juurde', None)),
     (('juurde', None), 'punct', (',', None)),
     (('viinud', None), 'punct', (',', None)),
     (('viinud', None), 'neg', ('ei', None)),
     (('viinud', None), 'nsubj', ('autoteed', None)),
     (('autoteed', None), 'nummod', ('ühtegi', None)),
     (('tulnud', None), 'punct', ('.', None))]


.. _CONLL-X: http://ilk.uvt.nl/conll/#dataformat
.. _CONLL-U: http://universaldependencies.org/format.html
.. _The Estonian UD treebank: https://github.com/UniversalDependencies/UD_Estonian


.. note:: **Quirks of the import method**

    1) The import method assumes that the input file is in ``UTF-8`` encoding;
    
    2) The import method converts word indices in the syntactic annotation to EstNLTK's format: word indices will start at ``0``, and the root node will have the parent index ``-1``;
    
    3) Be aware that the import method *does not* import *morphological annotations*. As there is no guarantee that morphological annotations in the file are compatible with EstNLTK's format of morphological analysis (e.g. annotations from `The Estonian UD treebank`_ are not), these annotations will be skipped and the resulting Text object has no layer of morphological analyses. If you want to make queries involving morphological constraints, you should first add the layer via method :py:func:`~estnltk.text.Text.tag_analysis`.
    
    4) When reconstructing the text, the method :py:meth:`~estnltk.syntax.utils.read_text_from_conll_file` tries to preserve the original tokenization used in the file. In order to distinguish multiword tokens (e.g. ``'Rio de Jainero'`` as a single word) from ordinary tokens, the method re-constructs the text in a way that words are separated by double space (``'  '``), and a single space (``' '``) is reserved for marking the space in a multiword. In order to preserve sentence boundaries, sentence endings are marked with newlines (``'\n'``).
