===================================
Temporal expression (TIMEX) tagging
===================================

Temporal expressions tagger identifies temporal expressions (timexes) in text and normalizes these expressions, providing corresponding calendrical dates and times. 
The program outputs an annotation in a format similar to TimeML's TIMEX3 (more detailed description can be found in `annotation guidelines`_, which are currently only in Estonian).

.. _annotation guidelines: https://github.com/soras/EstTimeMLCorpus/blob/master/docs-et/ajav2ljendite_m2rgendamine_06.pdf?raw=true

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

By default, the tagger processes all the sentences independently, which is relatively memory efficient way of processing.
However, this way of processing also has some limitations. 
Firstly, timex identifiers (timex_ids) are unique only within a sentence, and not within a document, as it is expected in TimeML. 
And secondly, some anaphoric temporal expressions (expressions that are referring to other temporal expressions) may be inaccurately normalized, as normalization may require considering a wider context than a single sentence. 
To overcome these limitations, argument `process_as_whole` can be used to process the input text as a whole (opposed to sentence-by-sentence processing)::

    text = ''''3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.'''
    tagged = tagger(analyzer(tokenizer(text)), process_as_whole = True)

    pprint(tagged.timexes)
    
    ['Timex(3. detsembril 2014, DATE, 2014-12-03, [timex_id=t1])',
     'Timex(kaks päeva varem, DATE, 2014-12-01, [timex_id=t2])']

Note that this way of processing can be rather demanding in terms of memory, especially when analyzing large documents.

The default string representation of the timex contains four fields: the temporal expression phrase, type (DATE, TIME, DURATION or SET), TimeML-based value and timex_id. 
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
