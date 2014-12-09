==================
Basics of Estnltk
==================

As they say, it is best to learn by example.
In this section, we cover all basic use cases of the library.
We recommend that the user would read the tutorial and try out the examples themselves to become comfortable with the library.
The source code for the examples can also be found in `estnltk/examples` directory of the package.


Paragraph, sentence and word tokenization
=========================================

The first step in most text processing tasks is to tokenize the input into smaller pieces, typically paragraphs, sentences and words.
In lexical analysis, tokenization is the process of breaking a stream of text up into words, phrases, symbols, or other meaningful elements called tokens.
The list of tokens becomes input for further processing such as parsing or text mining.
Tokenization is useful both in linguistics (where it is a form of text segmentation), and in computer science, where it forms part of lexical analysis.


Estnltk provides the :class:`estnltk.tokenize.Tokenizer` class that does this.
In the next example, we define some text, then import and initialize a :class:`estnltk.tokenize.Tokenizer` instance and use to create a :class:`estnltk.corpus.Document` instance::

    # Let's define a sample document
    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # tokenize it using default tokenizer
    from estnltk import Tokenizer
    tokenizer = Tokenizer()
    document = tokenizer.tokenize(text)

    # tokenized results
    print (document.word_texts)
    print (document.sentence_texts)
    print (document.paragraph_texts)
    print (document.text)

    
This will print out the tokenized words::

    ['Keeletehnoloogia', 'on', 'arvutilingvistika', 'praktiline', 'pool.', 'Keeletehnoloogid', 
    'kasutavad', 'arvutilingvistikas', 'välja', 'töötatud', 'teooriaid', ',', 'et', 'luua', 
    'rakendusi', '(', 'nt', 'arvutiprogramme', ')', ',', 'mis', 'võimaldavad', 'inimkeelt', 
    'arvuti', 'abil', 'töödelda', 'ja', 'mõista.', 'Tänapäeval', 'on', 'keeletehnoloogia', 
    'tuntumateks', 'valdkondadeks', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteemid', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees.']
    
and tokenized sentences::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.', 
     'Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, 
        et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt 
        arvuti abil töödelda ja mõista. ', 
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and tokenized paragraphs::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid 
        kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua 
        rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti 
        abil töödelda ja mõista.',
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and also the original full text can be accessed using ``text`` property of :class:`estnltk.corpus.Document`.
In case you get an error during tokenization, something like::

    LookupError: 
    **********************************************************************
      Resource u'tokenizers/punkt/estonian.pickle' not found.  Please
      use the NLTK Downloader to obtain the resource:  >>>
      nltk.download()

Then you have forgot post-installation step of downloading NLTK tokenizers. This can be done by invoking command::

    python -m nltk.downloader punkt

Token spans -- start and end positions
--------------------------------------

In addition to tokenization, it is often necessary to know where the tokens reside in the original document.
For example, you might want to inspect the context of a particular word.
For this purpose, estnltk provide ``word_spans``, ``sentence_spans`` and ``paragraph_spans`` methods.
Following the previous example, we can group together words and their start and end positions 
in the document using the following::

    zip(document.word_texts, document.word_spans)
    
This will create a list of tuples, where the first element is the tokenized word and the second element is a tuple
containing the start and end positions::

    [('Keeletehnoloogia', (0, 16)),
     ('on', (17, 19)),
     ('arvutilingvistika', (20, 37)),
     ('praktiline', (38, 48)),
     ('pool.', (49, 54)),
     ...
     ('kõneanalüüs', (340, 351)),
     ('ja', (352, 354)),
     ('kõnesüntees.', (355, 367))]

For other possible options, please check :class:`estnltk.corpus.Corpus`, :class:`estnltk.corpus.Document`, :class:`estnltk.corpus.Paragraph`, :class:`estnltk.corpus.Sentence` and :class:`estnltk.corpus.Word` classes.


Morphological analysis
======================

In linguistics, morphology is the identification, analysis, and description of the structure of a given language's morphemes and other linguistic units,
such as root words, lemmas, affixes/endings, parts of speech.

In morphology and lexicography, a lemma (plural lemmas or lemmata) is the canonical form, dictionary form, or citation form of a set of words (headword).
In grammar, a part of speech (also a word class, a lexical class, or a lexical category) is a linguistic category of words (or more precisely lexical items),
which is generally defined by the syntactic or morphological behaviour of the lexical item in question.
Common linguistic categories include noun and verb, among others.
Word forms define additional grammatical information such as cases, plurality etc.


Estnltk contains :class:`estnltk.morf.analyze` function for performing morphological analysis::

    from estnltk import analyze
    from pprint import pprint

    pprint(analyze('Tüünete öötööde allmaaraudteejaam'))

The result will be JSON-style data::

    [{'analysis': [{'clitic': '',
                    'ending': 'te',
                    'form': 'pl g',
                    'lemma': 'tüüne',
                    'partofspeech': 'A',
                    'root': 'tüüne',
                    'root_tokens': ['tüüne']}],
      'text': 'Tüünete'},
     {'analysis': [{'clitic': '',
                    'ending': 'de',
                    'form': 'pl g',
                    'lemma': 'öötöö',
                    'partofspeech': 'S',
                    'root': 'öö_töö',
                    'root_tokens': ['öö', 'töö']}],
      'text': 'öötööde'},
     {'analysis': [{'clitic': '',
                    'ending': '0',
                    'form': 'sg n',
                    'lemma': 'allmaaraudteejaam',
                    'partofspeech': 'S',
                    'root': 'all_maa_raud_tee_jaam',
                    'root_tokens': ['all', 'maa', 'raud', 'tee', 'jaam']}],
      'text': 'allmaaraudteejaam'}]

Note that the underlying `vabamorf`_ library does not yet include disambiguation, so all possible analysis will be returned.
The tags are documented in vabamorf tagset `documentation`_.

    .. _vabamorf: https://github.com/Filosoft/vabamorf/
    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html


The morphological analysis can also be applied on pretokenized data, so it will be possible to more easily list all lemmas, pos tags etc.
To do that, one needs to use :class:`estnltk.morf.PyVabamorfAnalyzer` class::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()

    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # first tokenize and then morphologically analyze
    morf_analyzed = analyzer(tokenizer(text))

    # print some results
    print (morf_analyzed.lemmas)
    print (morf_analyzed.postags)
    
    # print more information together
    pprint (list(zip(morf_analyzed.word_texts,
                     morf_analyzed.lemmas,
                     morf_analyzed.forms,
                     morf_analyzed.postags)))


The lemmas / stemmed words::
    
    ['keeletehnoloogia', 'olema', 'arvutilingvistika', 'praktiline', 'pool', 'keeletehnoloog', 
    'kasutama', 'arvutilingvistika', 'väli', 'töötatud', 'teooria', ',', 'et', 'looma', 
    'rakendus', '(', 'nt', 'arvutiprogramm', ')', ',', 'mis', 'võimaldama', 'inimkeel', 
    'arvuti', 'abi', 'töötlema', 'ja', 'mõistma', 'tänapäev', 'olema', 'keeletehnoloogia', 
    'tuntum', 'valdkond', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteem', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees']

The pos tags::

    ['S', 'V', 'S', 'A', 'S', 'S', 'A', 'S', 'S', 'A', 'S', 'Z', 'J', 'S', 'S', 'Z', 'Y', 
    'S', 'Z', 'Z', 'P', 'A', 'S', 'S', 'K', 'V', 'J', 'V', 'S', 'V', 'S', 'C', 'S', 'S', 
    'Z', 'S', 'Z', 'S', 'Z', 'S', 'J', 'S']

More information put together::

    [('Keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('arvutilingvistika', 'arvutilingvistika', 'sg g', 'S'),
     ('praktiline', 'praktiline', 'sg n', 'A'),
     ('pool.', 'pool', 'sg n', 'S'),
     ('Keeletehnoloogid', 'keeletehnoloog', 'pl n', 'S'),
     ('kasutavad', 'kasutama', 'pl n', 'A'),
     ('arvutilingvistikas', 'arvutilingvistika', 'sg in', 'S'),
     ('välja', 'väli', '', 'S'),
     ('töötatud', 'töötatud', 'pl n', 'A'),
     ('teooriaid', 'teooria', 'pl p', 'S'),
     (',', ',', '', 'Z'),
     ('et', 'et', '', 'J'),
     ('luua', 'looma', 'da', 'S'),
     ('rakendusi', 'rakendus', 'pl p', 'S'),
     ('(', '(', '', 'Z'),
     ('nt', 'nt', '?', 'Y'),
     ('arvutiprogramme', 'arvutiprogramm', 'pl p', 'S'),
     (')', ')', '', 'Z'),
     (',', ',', '', 'Z'),
     ('mis', 'mis', 'pl n', 'P'),
     ('võimaldavad', 'võimaldama', 'pl n', 'A'),
     ('inimkeelt', 'inimkeel', 'sg p', 'S'),
     ('arvuti', 'arvuti', 'sg g', 'S'),
     ('abil', 'abi', '', 'K'),
     ('töödelda', 'töötlema', 'da', 'V'),
     ('ja', 'ja', '', 'J'),
     ('mõista.', 'mõistma', 'da', 'V'),
     ('Tänapäeval', 'tänapäev', 'sg ad', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('tuntumateks', 'tuntum', 'pl tr', 'C'),
     ('valdkondadeks', 'valdkond', 'pl tr', 'S'),
     ('masintõlge', 'masintõlge', 'sg n', 'S'),
     (',', ',', '', 'Z'),
     ('arvutileksikoloogia', 'arvutileksikoloogia', 'sg g', 'S'),
     (',', ',', '', 'Z'),
     ('dialoogisüsteemid', 'dialoogisüsteem', 'pl n', 'S'),
     (',', ',', '', 'Z'),
     ('kõneanalüüs', 'kõneanalüüs', 'sg n', 'S'),
     ('ja', 'ja', '', 'J'),
     ('kõnesüntees.', 'kõnesüntees', 'sg n', 'S')]


Morphological synthesis
=======================

Estnltk can also do morphological synthesis using :class:`estnltk.morf.synthesize` function::

    from estnltk import synthesize

    print(synthesize('pood', form='pl p', partofspeech='S'))
    print(synthesize('palk', form='sg kom'))

That will print::

    ['poode', 'poodisid']
    ['palgaga', 'palgiga']

See `documentation`_ for possible parameters.

    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html

Clause segmenter
================
A simple sentence, also called an independent clause, typically contains a finite verb, and expresses a complete thought.
However, natural language sentences can also be long and complex, consisting of two or more clauses joined together.
The clause structure can be made even more complex by embedded clauses, which divide their parent clauses into two halves.

Clause segmenter makes it possible to extract clauses from a complex sentence and treat them independently::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()

    text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''

    segmented = segmenter(analyzer(tokenizer(text)))

Clause segmenter requires that the input text has been tokenized (split into sentences and words) and morphologically analyzed and disambiguated (the program also works on morphologically ambiguous text, but the quality of the analysis is expected to be lower than on morphologically disambiguated text).

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

Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate
and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.
First thing is to build the named entity model as it is too large to include in the package itself. Do it by invoking command::

    python -m estnltk.ner train_default_model

This will build the default model tuned for named entity recognition in news articles.
In order to use named entity tagging, you also need to perform morphological analysis first.
A quick example, how to do it::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, NerTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = NerTagger()

    text = '''Eesti Vabariik on riik Põhja-Euroopas. 
    Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.

    Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.

    2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
    2006. aastal valiti presidendiks Toomas Hendrik Ilves.
    '''

    # tag the documents
    ner_tagged = tagger(analyzer(tokenizer(text)))

    # print the words and their explicit labels in BIO notation
    pprint(list(zip(ner_tagged.word_texts, ner_tagged.labels)))
    

As a result, we see the list of words with annotated labels::

    [('Eesti', 'B-LOC'),
     ('Vabariik', 'I-LOC'),
     ('on', 'O'),
     ('riik', 'O'),
     ('Põhja-Euroopas.', 'B-LOC'),
     ('Eesti', 'B-LOC'),
     ('piirneb', 'O'),
     ('põhjas', 'O'),
     ('üle', 'O'),
     ('Soome', 'B-LOC'),
     ('lahe', 'I-LOC'),
     ('Soome', 'B-LOC'),
     ('Vabariigiga.', 'O'),
     ('Riigikogu', 'B-ORG'),
     ('on', 'O'),
     ('Eesti', 'B-LOC'),
     ('Vabariigi', 'I-LOC'),
     ('parlament.', 'O'),
     ('Riigikogule', 'B-ORG'),
     ('kuulub', 'O'),
     ('Eestis', 'B-LOC'),
     ('seadusandlik', 'O'),
     ('võim.', 'O'),
     ('2005.', 'O'),
     ('aastal', 'O'),
     ('sai', 'O'),
     ('peaministriks', 'O'),
     ('Andrus', 'B-PER'),
     ('Ansip', 'I-PER'),
     (',', 'O'),
     ('kes', 'O'),
     ('püsis', 'O'),
     ('sellel', 'O'),
     ('kohal', 'O'),
     ('2014.', 'O'),
     ('aastani.', 'O'),
     ('2006.', 'O'),
     ('aastal', 'O'),
     ('valiti', 'O'),
     ('presidendiks', 'O'),
     ('Toomas', 'B-PER'),
     ('Hendrik', 'I-PER'),
     ('Ilves.', 'I-PER')]

Named entity tags are encoded using a widely accepted BIO annotation scheme, where each label is prefixed with B or I, or the entire label is given as O.
**B-** denotes the *beginning* and **I-** *inside* of an entity, while **O** means *omitted*.
This can be used to detect entities that consist of more than a single word as can be seen in above example.

It is also possible to query directly :class:`estnltk.corpus.NamedEntity` objects from tagged corpora.
This makes it easy to see all words that are grouped into a named entity::

    pprint (ner_tagged.named_entities)
    
    ['NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(põhja-euroopa, LOC)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(soome lahe, LOC)',
     'NamedEntity(soome, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(andrus ansip, PER)',
     'NamedEntity(toomas hendrik ilves, PER)']

See :class:`estnltk.corpus.NamedEntity` documentation for information on available properties.


Temporal expression (TIMEX) tagging
===================================

Temporal expressions tagger identifies temporal expressions (timexes) in text and normalizes these expressions, providing corresponding calendrical dates and times. 
The program outputs an annotation in a format similar to TimeML's TIMEX3 (see TODO for more details). 
According to TimeML, four types of temporal expressions are distinguished:

* DATE expressions, e.g. *järgmisel kolmapäeval* (*on next Wednesday*)
* TIME expressions, e.g. *kell 18.00* (*at 18.00 o’clock*)
* DURATIONs, e.g. *viis päeva* (*five days*)
* SETs of times, e.g. *igal aastal* (*on every year*)

Temporal expressions tagger requires that the input text has been tokenized (split into sentences and words), morphologically analyzed and disambiguated (the program also works on morphologically ambiguous text, but the quality of the analysis is expected to be lower than on morphologically disambiguated text).

Example::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import TimexTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = TimexTagger()

    text = ''''Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'''
    tagged = tagger(analyzer(tokenizer(text)))

    pprint(tagged.timexes)

This prints found temporal expressions::

    [['Timex(eile, DATE, 2014-12-02, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

Note that the relative temporal expressions (such as *eile* (*yesterday*)) are normalized according to the date when the program was run (in the previous example: December 3, 2014). 
This behaviour can be changed by supplying `creation_date` argument to the tagger.
For example, let's tag the text given date June 10, 1995::

    # retag with a new creation date
    import datetime

    tagged = tagger(tagged, creation_date=datetime.datetime(1995, 6, 10))
    pprint(tagged.timexes)
    
    ['Timex(eile, DATE, 1995-06-09, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

By default, the tagger processes all the sentences independently, which is a relatively fast and not too memory demanding way of processing. 
However, this way of processing also has some limitations. 
Firstly, timex identifiers (timex_ids) are unique only within a sentence, and not within a document, as it is expected in TimeML. 
And secondly, some anaphoric temporal expressions (expressions that are referring to other temporal expressions) may be inaccurately normalized, as normalization may require considering a wider context than a single sentence. 
To overcome these limitations, argument `process_as_whole` can be used to process the input text as a whole (opposed to sentence-by-sentence processing)::

    text = ''''3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.'''
    tagged = tagger(analyzer(tokenizer(text)), process_as_whole = True)

    pprint(tagged.timexes)
    
    ['Timex(3. detsembril 2014, DATE, 2014-12-03, [timex_id=t1])',
     'Timex(kaks päeva varem, DATE, 2014-12-01, [timex_id=t2])']

Note that the default string representation of the timex only contains four fields: the temporal expression phrase, type (DATE, TIME, DURATION or SET), TimeML-based value and timex_id. 
Depending on (the semantics of) the temporal expression, there can also be additional attributes supplied in the timex object. 
For example, if the timex value has been calculated with respect to some other timex ("anchored" to other timex), the attribute `anchor_id` refers to the identifier of the corresponding timex::

    text = ''''3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.'''
    tagged = tagger(analyzer(tokenizer(text)), process_as_whole = True)

    for timex in tagged.timexes:
        print(timex, ' is anchored to timex:', timex.anchor_id )

outputs::
        
    'Timex(3. detsembril 2014, DATE, 2014-12-03, [timex_id=1])'  is anchored to timex: None
    'Timex(kaks päeva varem, DATE, 2014-12-01, [timex_id=2])'  is anchored to timex: 1

For more information about available attributes, see the documentation of :class:`estnltk.corpus.Timex`.

Temporal expressions tagger also identifies some temporal expressions that are difficult to normalize, and thus no *type/value* will assigned to those expressions. 
By default, timexes without *type/value* will be removed from the output; however, this behaviour can be changed by executing the tagger with an argument `remove_unnormalized_timexes=False`.


Verb chain detection
====================

Verb chain detector identifies multiword verb units from text. 
The current version of the program aims to detect following verb chain constructions:

* basic main verbs:

  * negated main verbs: *ei/ära/pole/ega* + verb;
  * (affirmative) single *olema* main verbs and *olema* verb chains: *olema* + verb;
  * (affirmative) single non-*olema* main verbs;

* verb chain extensions:

  * verb + verb : the chain is extended with an infinite verb if the last verb of the chain subcategorizes for it, e.g. the verb *kutsuma* is extended with *ma*-verb arguments (for example: Kevadpäike **kutsub** mind **suusatama**) and the verb *püüdma* is extended with *da*-verb arguments (Aita **ei püüdnudki** Leenat **mõista**);
  * verb + nom/adv + verb : the last verb of the chain is extended with nominal/adverb arguments which subcategorize for an infinite verb, e.g. the verb *otsima* forms a multiword unit with the nominal *võimalust* which, in turn, takes infinite *da*-verb as an argument (for example: Seepärast **otsisimegi võimalust** kusagilt mõned ilvesed **hankida**);

Verb chain detector requires that the input text has been tokenized (split into sentences and words), morphologically analyzed, morphologically disambiguated, and segmented into clauses. 
Recall that the text can be segmented into clauses with :class:`estnltk.clausesegmenter.ClauseSegmenter`.

Example::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import ClauseSegmenter
    from estnltk import VerbChainDetector
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()
    detector = VerbChainDetector()

    text = ''''Samas on selge, et senine korraldus jätkuda ei saa.'''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # print verb chain objects
    pprint(processed.verb_chains)

Property :class:`estnltk.corpus.Corpus.verb_chains` lists all found :class:`estnltk.corpus.VerbChain` objects.
The previous example prints out following found verb chains::

    ['VerbChain(on, ole, ole, POS)',
     'VerbChain(korraldus, verb, korraldu, POS)',
     'VerbChain(jätkuda ei saa., ei+verb+verb, ei_saa_jätku, NEG)']

Note that because the program was ran on morphologically ambiguous text, the word *korraldus* was mistakenly detected as a main verb (past form of the verb *korralduma*).
In general, morphological disambiguation of the input is an important requirement for verb chain detector, and the quality of the analysis suffers quite much without it.

The default string representation of the verb chain (as can be seen from the previous example) contains four attribute values: text of the verb chain, the general pattern of the verb chain, concanated lemmas of the verb chain words, and grammatical polarity of the chain.
These and other attributes can also be directly accessed in the verb chain object::

    text = ''' Ta oleks pidanud sinna minema, aga ei läinud. '''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # print attributes of each verb chain object
    for chain in processed.verb_chains:
        print('text: ', chain.text )
        print('general pattern: ', chain.pattern_tokens )
        print('roots: ', chain.roots )
        print('morph: ', chain.morph )
        print('polarity: ', chain.polarity )
        print('other verbs: ', chain.other_verbs )
        print()    

The previous example outputs::

     text:  oleks pidanud minema
     general pattern:  ['ole', 'verb', 'verb']
     roots:  ['ole', 'pida', 'mine']
     morph:  ['V_ks', 'V_nud', 'V_ma']
     polarity:  POS
     other verbs:  False

     text:  ei läinud.
     general pattern:  ['ei', 'verb']
     roots:  ['ei', 'mine']
     morph:  ['V_neg', 'V_nud']
     polarity:  NEG
     other verbs:  False

Following is a brief description of the attributes:
   
    * ``estnltk.corpus.VerbChain.pattern_tokens`` - the general pattern of the chain: for each word in the chain, lists whether it is *'ega'*, *'ei'*, *'ära'*, *'pole'*, *'ole'*, *'&'* (conjunction: ja/ning/ega/või), *'verb'* (verb different than *'ole'*) or *'nom/adv'* (nominal/adverb); 
    * ``estnltk.corpus.VerbChain.roots`` - for each word in the chain, lists its corresponding 'root' value from the morphological analysis;
    * ``estnltk.corpus.VerbChain.morph`` - for each word in the chain, lists its morphological features: part of speech tag and form (in one string, separated by '_', and multiple variants of the pos/form are separated by '/');
    * ``estnltk.corpus.VerbChain.polarity`` - grammatical polarity of the chain: *'POS'*, *'NEG'* or *'??'*. *'NEG'* simply means that the chains begins with a negation word *ei/pole/ega/ära*; *'??'* is reserved for cases where it is uncertain whether *ära* forms a negated verb chain or not;
    * ``estnltk.corpus.VerbChain.other_verbs`` - boolean, marks whether there are other verbs in the context, which can be potentially added to the verb chain; if ``True``,then it is uncertain whether the chain is complete or not;
  
.. Note that the words in the verb chain are ordered not as they appear in the text, but by the order of the grammatical relations: first words are mostly grammatical (such as auxiliary negation words *ei/ega/ära*) or otherwise abstract (e.g. modal words like *tohtima*, *võima*, aspectual words like *hakkama*), and only the last words carry most of the semantic/concrete meaning.
  

Estonian Wordnet
================

TODO: Add KOM documentation here.

Understanding JSON notation and Estnltk corpora
===============================================

Here is a detailed description of the JSON structure and how it relates to Corpus objects in Estnltk.


Reading TEI corpora (koondkorpus, tasakaalustatud korpus)
---------------------------------------------------------

Example, how to read files of koondkorpus and tasakaalustatud korpus with Estnltk.


Using Python NLTK corpus readers with Estnltk
----------------------------------------------

Guidelines for using NLTK corpus readers with Estnltk.


Text classifier tool
====================

TODO: add text classifier tool documentation here.
