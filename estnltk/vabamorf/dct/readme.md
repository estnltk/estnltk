## Root directory for Vabamorf's lexicons

This directory contains Vabamorf's lexicons available in EstNLTK.  Each subdirectory should contain a pair of binary lexicons (`et.dct` and `et3.dct`). Subdirectory names must be ISO format dates, indicating dates in which corresponding lexicons were created or introduced into EstNLTK. By default, EstNLTK uses lexicons with the latest date.

### Directory name suffixes: `sp` vs `nosp`

* `sp` -- the standard written language lexicon. This is the default lexicon directory used by EstNLTK; 
* `nosp` -- a variant of the standard lexicon that has been augmented with  non-standard and slang words, such as _kodukas_, _mõnsa_, _mersu_, _kippelt_ . This lexicon can be useful for analysing Internet language, but as the label `nosp` (_no-spell_) indicates: you should not use this lexicon in a speller; 
