==========================================================================
  Java-based Text Analysis Tools:
    * Clause Segmenter (Osalausestaja)
    * Temporal Expressions Tagger (Ajaväljendite tuvastaja)
==========================================================================

======================================
  Clause Segmenter (Osalausestaja)
======================================

  Required files
 -----------------
  Osalau.jar
  javax.json-1.0.4.jar


  Running with Python
 ----------------------
   Executing Osalau.jar with the flag "-pyvabamorf" evokes a special standard 
  input/output processing mode, where the program reads a line from the standard 
  input (must be JSON, in UTF-8), analyzes the line, and outputs the results (in 
  a single line) to the standard output.

     java -jar Osalau.jar -pyvabamorf

   Note that the minimum JSON structure each line should have is:
     {"words": [ {"analysis": [ ... ],
                   "text": "word1"},
                  {"analysis": [ ... ],
                   "text": "word2"},
                   ...
                  {"analysis": [ ... ],
                   "text": "wordN"} ]}

   That is, an object with key "words" must be present, indicating an analyzable
  sentence.


  Interpreting the output
 --------------------------
  The clause segmenter marks clause boundaries: boundaries between regular 
 clauses, and start and end positions of embedded clauses. 
 
  In JSON input/output format, the clause boundary is indicated by adding object 
 "clauseAnnotation" to the token (at the same level as objects "text" and 
 "analysis"). The "clauseAnnotation" (which is a list of strings) can contain 
 three types of boundary markings:
    KINDEL_PIIR -- indicates that there is a clause boundary AFTER current 
                   token: one clause ends and another starts;
    KIILU_ALGUS -- marks a beginning of a new embedded clause BEFORE current 
                   token;
    KIILU_LOPP  -- marks ending of an embedded clause AFTER current token;

  Example:
    The sentence
       "Mees, keda seal kohtasime, oli tuttav ja teretas meid."

    will obtain following clause annotations:
        {"words": [ {"analysis": [ ... ],
                      "text": "Mees,"},
                     {"analysis": [ ... ],
                      "clauseAnnotation": ["KIILU_ALGUS"],
                      "text": "keda"},
                     {"analysis": [ ... ],
                      "text": "seal"},
                     {"analysis": [ ... ],
                      "clauseAnnotation": ["KIILU_LOPP"],
                      "text": "kohtasime,"},
                     {"analysis": [ ... ],
                      "text": "oli"},
                     {"analysis": [ ... ],
                      "text": "tuttav"},
                     {"analysis": [ ... ],
                      "clauseAnnotation": ["KINDEL_PIIR"],
                      "text": "ja"},
                     {"analysis": [ ... ],
                      "text": "teretas"},
                     {"analysis": [ ... ],
                      "text": "meid."} ]}

    which should be interpreted as:
          "keda" (KIILU_ALGUS) -- an embedded clause begins before "keda";
          "kohtasime," (KIILU_LOPP) -- the embedded clause ends after "kohtasime,";
          "ja" (KINDEL_PIIR)   -- one clause ends after "ja" and another begins;
          
    so, the corresponding clause structure should look like:
       "[Mees, [keda seal kohtasime,] oli tuttav ja] [teretas meid.]"
       (clauses are surrounded by brackets)
       
  Note that embedded clauses can contain other clauses and other embedded 
 clauses, and so the whole clause structure has a recursive nature.


  Source code
----------------
 https://github.com/soras/osalausestaja/


======================================
  Temporal Expressions Tagger 
  (Ajaväljendite tuvastaja)
======================================

  Required files
 -----------------
  Ajavt.jar
  javax.json-1.0.4.jar
  joda-time-1.6.jar
  reeglid.xml


  Running with Python
 ----------------------
   Executing Ajavt.jar with the flag "-pyvabamorf" evokes a special standard 
  input/output processing mode, where the program reads a line from the standard 
  input (must be JSON, in UTF-8), analyzes the line, and outputs the results (in 
  a single line) to the standard output.

     java -jar Ajavt.jar -pyvabamorf -r FULL/PATH/TO/reeglid.xml

   Flag "-r" followed by the full path to the file "reeglid.xml" should be used to
  specify the location of the rules file.

   Note that the minimum JSON structure each input line should have is:
     {"words": [ {"analysis": [ ... ],
                   "text": "word1"},
                  {"analysis": [ ... ],
                   "text": "word2"},
                   ...
                  {"analysis": [ ... ],
                   "text": "wordN"} ]}

   That is, an object with key "words" must be present, indicating an analyzable
  sentence.
   Optionally, an ISO format document creation time ("dct") can also be specified 
  in the input as a key-value pair:
        { "dct": "yyyy-mm-ddThh:MM",
           "words": [ {"analysis": [ ... ],
                      "text": "word1"},
                     {"analysis": [ ... ],
                      "text": "word2"},
                      ...
                     {"analysis": [ ... ],
                      "text": "wordN"} ]}

   (If left unspecified, execution time of the program is taken as a document
    creation time by default);

  Interpreting the output
 --------------------------
  Temporal Expressions Tagger identifies temporal expression phrases in text and
 normalizes these expressions in a format similar to TimeML's TIMEX3.
 
  In JSON input/output format, the presence of identified temporal expression(s) 
 is indicated by adding object "timexes" to the token (at the same level as objects 
 "text" and "analysis"). The "timexes" is a list of objects and each object has
 (at minimum) a following structure:
        {
          "tid":   string,
        }
  where "tid" is an unique identifier of the temporal expression (in form that can 
  be described by a regular expression "t[0-9]+" ).
   (Note that in "-pyvabamorf" processing mode, this uniqueness only holds within 
    a single input line, which is expected to be a single document);
   If the token is at the beginning of a multiword temporal expression phrase, or
  the temporal expression is a single-word expression, additional attribute/value
  pairs will be specified in each timex object:
        "text" : string  
            // full extent phrase of the temporal expression
        "type" : string  
            // one of the following: "DATE", "TIME", "DURATION", "SET"
        "value": string
            // calendrical value (largely follows TimeML TIMEX3 value format)
        "temporalFunction": string
            // whether the "value" was found by heuristics/calculations (thus can 
            // be wrong): "true", "false"
   Depending on the (semantics of the) temporal expression, there can also be other 
  attribute/value pairs:
         "mod" : string
            // largely follows TimeML TIMEX3 mod format, with two additional values
            // used to mark first/second half of the date/time (e.g. "in the first 
            // half of the month"):  FIRST_HALF, SECOND_HALF;
         "anchorTimeID"
            // points to the temporal expression (by identifier) that this expression 
            // has been anchored to while calculating or determining the value;
            // "t0" -- means that the expression is anchored to document creation 
            // time;
         "beginPoint"
            // in case of DURATION: points to the temporal expression (by identifier)
            // that serves as a beginning point of this duration;
            // "?" -- indicates problems on finding the beginning point;
         "endPoint"
            // in case of DURATION: points to the temporal expression (by identifier)
            // that serves as an ending point of this duration;
            // "?" -- indicates problems on finding the ending point;
         "quant"
            // Quantifier; Used only in some SET expressions, e.g. quant="EVERY"
         "freq" 
            // Used in some SET expressions, marks frequency of repetition, e.g.
            // "three days in each month" will be have freq="3D"


  Example:
    The sentence
      "Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle."
      (created at 2014-10-06)
    
    will obtain following temporal expression annotations:
       {
            "words":[  { "analysis":[ ... ],
                         "text":"Potsataja"
                       },
                       { "analysis":[ ... ],
                         "text":"ütles"
                       },
                       { "analysis":[ ... ],
                         "text":"eile,",
                         "timexes":[ { "tid":"t1",
                                       "text":"eile,",
                                       "type":"DATE",
                                       "temporalFunction":"true",
                                       "value":"2014-10-05" } ]
                       },
                       { "analysis":[ ... ],
                         "text":"et"
                       },
                       { "analysis":[ ... ],
                         "text":"vaatavad"
                       },
                       {
                         "analysis":[ ... ],
                         "text":"nüüd",
                         "timexes":[ { "tid":"t2",
                                       "text":"nüüd",
                                       "type":"DATE",
                                       "temporalFunction":"true",
                                       "value":"PRESENT_REF",
                                       "anchorTimeID":"t0"  } ]
                       },
                       { "analysis":[ ... ],
                         "text":"Genaga"
                       },
                       { "analysis":[ ... ],
                         "text":"viie",
                         "timexes":[ { "tid":"t3",
                                       "text":"viie aasta",
                                       "type":"DURATION",
                                       "temporalFunction":"false",
                                       "value":"P5Y" } ]
                       },
                       { "analysis":[ ... ],
                         "text":"aasta",
                         "timexes":[ { "tid":"t3",
                                       "text":"viie aasta" } ]
                       },
                       { "analysis":[ ... ],
                         "text":"plaanid"
                       },
                       { "analysis":[ ... ],
                         "text":"uuesti"
                       },
                       { "analysis":[ ... ],
                         "text":"üle"
                       }
                    ]
        }

    which should be interpreted as:
       "eile," -- is a single-word temporal expression, which is from type "DATE",
                  and which refers to the date "2014-10-05";
       "nüüd" --  is a single-word temporal expression, which is from type "DATE",
                  and which has an uncertain calendaric value, but it refers to the 
                  present time (PRESENT_REF), contemporary to the document creation
                  time (t0, which is 2014-10-06);
       "viie", "aasta" -- forms a multiword temporal expression phrase ("viie aasta"), 
                          referring to a period ("DURATION") of length 5 years;


   Note that there can also be timexes with no "text" value, i.e. timexes that form an 
  implicit duration (A), or mark implicit beginning or ending points (B):

    (A) e.g. "2001-2005" -- the period covering explicit timepoints "2001-" and "2005" 
                            is annotated as a timex (DURATION) with no textual content;

    (B) e.g. "following three years" -- beginning and ending timepoints of the explicit 
                                        duration expression ("three years") are marked 
                                        as timexes with no textual content;

   The program does not always resolve the ambiguities of possible multiple readings of 
  temporal expressions, e.g. "aastas 2000 tundi" can be interpreted as "aastas 2000" 
  (in year 2000) or as "2000 tundi" (2000 hours). In case of ambiguities, "timexes" also 
  lists multiple timex objects.


  For more details on temporal expression annotation, see TimeML TIMEX3 specification:
    http://www.timeml.org/site/publications/timeMLdocs/timeml_1.2.1.html#timex3

