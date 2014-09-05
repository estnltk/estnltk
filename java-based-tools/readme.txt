==========================================================================
  Java-based Text Analysis Tools:
    ** Clause Segmenter (Osalausestaja)
    ** Temporal Expressions Tagger (Ajaväljendite tuvastaja)
==========================================================================

======================================
  Clause Segmenter (Osalausestaja)
======================================
 WIP: set of rules used by the segmenter is still incomplete;

  Usage
 --------
  See the example of sentence level analysis in script "usage_example1.py"
 
  Input
 --------
  The clause segmenter requires that the input text has been split into 
 sentences, tokens and tokens are morphologically analyzed and disambiguated.
  The input should be in vabamorf JSON format ( https://github.com/Filosoft/vabamorf ), 
 like it can be obtained with the etana tool.
  Important! There should be no phonetic markup symbols in the word root analyses;
 
  Output
 --------
  The clause segmenter marks clause boundaries: endings of regular clauses, and
 start, and end positions of embedded clauses. 
 
  The clause boundary is indicated by adding object 'clauseAnnotation' to the token
 (at the same level as objects 'text' and 'analysis'). The 'clauseAnnotation' (a list 
 of strings) can contain three types of boundary markings:
    KINDEL_PIIR -- indicates that a clause ends AFTER current token;
    KIILU_ALGUS -- marks a beginning of a new embedded clause BEFORE current token;
    KIILU_LOPP  -- marks ending of an embedded clause AFTER current token;
    
   Note that positioning with respect to the token is not reflected in JSON format (e.g. 
  the position of 'clauseAnnotation' within the token does not tell whether the boundary 
  should be drawn before or after the token), so it is important to emphasize that 
  clause endings (KINDEL_PIIR, KIILU_LOPP) should always come after the token, and clause 
  start (KIILU_ALGUS) should come before the token;
   
   Embedded clauses can also contain other clauses, and other embedded clauses, thus the
  whole sentence can have a recursive clause structure.
  

======================================
  Temporal Expressions Tagger 
  (Ajaväljendite tuvastaja)
======================================
 WIP: detailed information, rules file and Python interface will be added later;
