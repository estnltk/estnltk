Additional resources required for converting Vabamorf's annotations to UD (Universal Dependencies)  annotations. 

* .tab files -- dictionaries for converting Vabamorf's lemma & postag to UD postag and features. 
Original source: [https://github.com/EstSyntax/EstUD/tree/master/cgmorf2conllu/POS_LEMMA_RULES](https://github.com/EstSyntax/EstUD/tree/master/cgmorf2conllu/POS_LEMMA_RULES). Original format of the rules has been changed and rules have been extended;

* duplicate_tab_file_entries.py -- detects and displays duplicate entries in *.tab files: lemmas with more than one possible UD conversion rule; (for debugging and dictionary development);

* adj_without_verb_feats.txt -- list of adjective lemmas (one lemma per line) which should not receive verb participle features during the UD conversion;

