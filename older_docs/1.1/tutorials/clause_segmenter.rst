================
Clause segmenter
================
A simple sentence, also called an independent clause, typically contains a finite verb, and expresses a complete thought.
However, natural language sentences can also be long and complex, consisting of two or more clauses joined together.
The clause structure can be made even more complex by embedded clauses, which divide their parent clauses into two halves.

Basic usage
------------

Clause segmenter makes it possible to extract clauses from a complex sentence and treat them independently. Before the tool can be applied, the input text must be tokenized (split into sentences and words) and morphologically analyzed and disambiguated (the program also works on morphologically ambiguous text, but the quality of the analysis is expected to be lower than on morphologically disambiguated text).

Example::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()

    text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''

    segmented = segmenter(analyzer(tokenizer(text)))

The segmenter annotates clause boundaries between words, and start and end locations of embedded clauses. 
Based on the annotation, each word in the sentence is associated with a clause index. 
Following is an example on how to access both the initial clause annotations, and also clause indexes of the words::

    # Clause indices and annotations
    pprint(list(zip(segmented.words, segmented.clause_indices, segmented.clause_annotations)))

    [('Word(Mees)', 0, None),
     ('Word(,)', 1, 'embedded_clause_start'),
     ('Word(keda)', 1, None),
     ('Word(seal)', 1, None),
     ('Word(kohtasime)', 1, None),
     ('Word(,)', 1, 'embedded_clause_end'),
     ('Word(oli)', 0, None),
     ('Word(tuttav)', 0, None),
     ('Word(ja)', 0, 'clause_boundary'),
     ('Word(teretas)', 2, None),
     ('Word(meid.)', 2, None)]

There is also a  :class:`estnltk.corpus.Clause` type, that can be queried from the corpus::

    # The clauses themselves
    pprint(segmented.clauses)
    
    ['Clause(Mees oli tuttav ja [clause_index=0])',
     'Clause(, keda seal kohtasime , [clause_index=1])',
     'Clause(teretas meid. [clause_index=2])']

Here is also an example of how to group words by clauses::

    # Words grouped by clauses
    for clause in segmented.clauses:
        pprint(clause.words)
        
    ['Word(Mees)', 'Word(oli)', 'Word(tuttav)', 'Word(ja)']
    ['Word(,)', 'Word(keda)', 'Word(seal)', 'Word(kohtasime)', 'Word(,)']
    ['Word(teretas)', 'Word(meid.)']

The 'ignore_missing_commas' mode
----------------------------------

Because commas are important clause delimiters in Estonian, the quality of the clause segmentation may suffer due to accidentially missing commas in the input text. To address this issue, the clause segmenter can be initialized in a mode in which the program tries to be less sensitive to missing commas while detecting clause boundaries.

Example::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter( ignore_missing_commas=True )

    text = 'Keegi teine ka siin ju kirjutas et ütles et saab ise asjadele järgi minna aga vastust seepeale ei tulnudki.'

    segmented = segmenter(analyzer(tokenizer(text)))
    
    pprint(segmented.clauses)

will produce following output::

    ['Clause(Keegi teine ka siin ju kirjutas [clause_index=0])',
     'Clause(et ütles [clause_index=1])',
     'Clause(et saab ise asjadele järgi minna [clause_index=2])',
     'Clause(aga vastust seepeale ei tulnudki. [clause_index=3])']


Note that this mode is experimental and compared to the default mode, it may introduce additional incorrect clause boundaries, although it also improves clause boundary detection in texts with (a lot of) missing commas.
