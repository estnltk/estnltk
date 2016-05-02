========================
Terminal Prettyprinter
========================
.. highlight:: python

In addition to HTML pretty-printing capabilities, Estnltk also provides means for visualizing annotations in terminal: bracketing annotations, displaying annotations in a custom color font, and/or underlining annotations.

A straight-forward prettyprinting can be performed via the method :py:meth:`~estnltk.prettyprinter.terminalprettyprinter.tprint`, which takes three input arguments: a :py:class:`~estnltk.text.Text` object, a list of layer names, and list of dicts containing annotation options (i.e. which formattings should be applied), and provides formatted output to the terminal. Example::

        from estnltk import Text
        from estnltk.prettyprinter.terminalprettyprinter import tprint
        
        text = Text('Mees, keda me otsisime, oli juba kuhugi kadunud.').tag_verb_chains()
        
        # Print text in a manner that:
        #  1) clauses are bracketed,
        #  2) verb chains are underlined
        tprint( text, ['clauses','verb_chains'], [{'bracket':True},{'underline':True}] )

The above example produces the following output (in a Windows terminal):

.. image:: _static/terminalprettyprinter_example_1.png
   :alt: Terminal prettyprinter output 1

The list of annotation options must be same size as the list of layer names, individually specifying how each layer should be formatted. The pretty-printing function currently supports the following formatting options:

* ``underline`` (shortcut: ``u``) -- boolean indicating whether annotations of given layer should be underlined;
* ``bracket`` (shortcut: ``b``) -- boolean indicating whether annotations of given layer should be bracketed;
* ``color`` (shortcut: ``c``) -- string indicating color of the font in which the annotation is to be displayed; Supported color names: ``'red'``, ``'blue'``, ``'green'``, ``'white'``, ``'cyan'``, ``'purple'``, ``'yellow'``, ``'teal'``, ``'darkpurple'``, ``'darkblue'``, ``'olive'``, ``'darkgreen'``, ``'darkred'``, ``'grey'`` ;

        
.. note:: 

    Graphical formatting of annotations (changing color of the text, and/or underlining annotations) can only be used in a terminal that interprets *ANSI escape sequences* as text formatting commands. Not all terminals support these commands, e.g. Python's IDLE environment lacks the support. If the terminal does not support graphical formatting, the only viable terminal-based visualization option is to surround the annotations with brackets; using any other option (e.g. font coloring) will simply produce text mingled with unexecuted ANSI escape sequences.
