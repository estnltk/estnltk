Different rule-based taggers

Each tagger uses a ruleset made up of static and dynamic rules to add annotations to the layer.
Rulesets and rules are defined in the extraction_rules folder.

The taggers available are:
* Phrase tagger - Tags phrases on a given layer. Creates an enveloping layer.
* Regex tagger - Tags regular expression matches on the text.
* Span tagger - Tags spans on a given layer. Creates a layer for which the input layer is the parent layer.
* Substring tagger - Tags occurrences of substrings on the text, solves possible conflicts and creates a new layer of the matches.