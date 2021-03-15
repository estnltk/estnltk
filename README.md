EstNLTK-light -- core components of the EstNLTK v1.6 library
=====================================================================

This package contains core components of the EstNLTK v1.6 library:

  * data structures: Text, Layer, Span, EnvelopingSpan, SpanList, Annotation;
  * tagger component interfaces: Tagger, Retagger;
  * basic layer operations: flatten, merge, rebase, split layers etc.
  * functions for converting between EstNLTK's data structures and JSON/dict representations;

The package is based on the EstNLTK v1.6 commit [1a2754611f](https://github.com/estnltk/estnltk/tree/1a2754611feec84cdef597a7f74a2cc806964d60), which has been heavily stripped down. Removed components:

  * NLP tools and pipelines;
  * all the visualization components and Jupyter Notebook support (HTML representations);
  * storage components;
  * tests;

For details, see [changes.txt](changes.txt). 



