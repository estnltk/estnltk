==========================================================================
  Java-based Text Analysis Tools:
    * Clause Segmenter (Osalausestaja)
    * Temporal Expressions Tagger (Ajaväljendite tuvastaja)
==========================================================================

======================================
  Clause Segmenter (Osalausestaja)
======================================
 Status: WIP, needs testing and comparing against old version of the program;

  Usage
 --------
  See the example of sentence level analysis in script "usage_example1.py"
 
  Input
 --------
  The clause segmenter requires that the input text has been split into 
 sentences and tokens, and tokens are morphologically analyzed and disambiguated.
  The input should be in vabamorf JSON format ( https://github.com/Filosoft/vabamorf ), 
 i.e. analyzed with the "etana" tool.
  Important! There should be no phonetic markup symbols in the word root analyses;
 
  Output
 --------
  The clause segmenter marks clause boundaries: boundaries of regular clauses, and
 start and end positions of embedded clauses. 
 
  The clause boundary is indicated by adding object 'clauseAnnotation' to the token
 (at the same level as objects 'text' and 'analysis'). The 'clauseAnnotation' (a list 
 of strings) can contain three types of boundary markings:
    KINDEL_PIIR -- indicates that there is a clause boundary AFTER current token:
                   one clause ends and another starts;
    KIILU_ALGUS -- marks a beginning of a new embedded clause BEFORE current token;
    KIILU_LOPP  -- marks ending of an embedded clause AFTER current token;

  Example:
    The sentence
       "Mees, keda seal kohtasime, oli tuttav ja teretas meid."
    will obtain following clause annotations:
       "keda"       -- KIILU_ALGUS ( == <KIIL> )
       "kohtasime," -- KIILU_LOPP  ( == </KIIL> )
       "ja"         -- KINDEL_PIIR
    so the annotated sentence should look like:
       "Mees, <KIIL> keda seal kohtasime, </KIIL> oli tuttav ja <KINDEL_PIIR/> teretas meid."
    and the corresponding clause tree should look like:
       "[Mees, [keda seal kohtasime,] oli tuttav ja] [teretas meid.]"
   
     Note that embedded clauses can contain other clauses and embedded clauses, and so the 
    whole clause structure can be recursive.
    
  References
 ------------
  *) Kaalep, Heiki-Jaan; Muischnek, Kadri (2012). Osalausete tuvastamine eestikeelses tekstis kui 
     iseseisev ülesanne. Helle Metslang, Margit Langemets, Maria-Maren Sepper (Toim.). Eesti 
     Rakenduslingvistika Ühingu aastaraamat (55 - 68). Tallinn: Eesti Rakenduslingvistika Ühing;
  *) Kaalep, Heiki-Jaan; Muischnek, Kadri (2012). Robust clause boundary identification for corpus 
     annotation. Nicoletta Calzolari, Khalid Choukri, Thierry Declerck, Mehmet Uğur Doğan, Bente 
     Maegaard, Joseph Mar (Toim.). Proceedings of the Eight International Conference on Language 
     Resources and Evaluation (LREC'12) (1632 - 1636). Istanbul, Turkey: ELRA;

======================================
  Temporal Expressions Tagger 
  (Ajaväljendite tuvastaja)
======================================
 Status: WIP - detailed information, rules file and Python interface will be added later;
