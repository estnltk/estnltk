
# Elative Consctruction checker

This (re)tagger detects instances like "lendurist abikaasa" and assigns 4 types of matches.  

"rabasin kapist kleiti" - "kapist" is in locative case and is a location, instances like this are correct   
"rabasin siidist kleiti" - "siidist" is also in locative case but is not a location, 
            therefore "siidist" should be detected by this tagger and potential correction should be "kleiti"  

The phrase consist of two target words. For all the matches, it is irrelevant how many adjectives are between two target words.  

The target "pairs" are in the elative construction list that will be given to the tagger as a dictionary. The dictionary keys are the first target words and each has a list of potential second target words. For example {"lendurist":["abikaasa", "isa"], "treenerist": ["isa", "ema", ..], ...}



### move_next

This match type applies when the syntax tree is correct and both of the target words are direct children of the same node.

![example of move_next](https://github.com/estnltk/estnltk/tree/devel_1.7/estnltk_neural/estnltk_neural/taggers/morphosyntax/elative_construction/next.png)

In this case, the tagger finds "treenerist isa" and since both words are direct descendants (next to eachother) of the same node then match_type is "move_next".

This case would apply also if the tree is correct and the sentence had "treenerist väga vana isa".


### move_further

This match type applies when the syntax tree may or may not be correct and one target word has additional word between the target and the first common parent node.

![example of move_further](https://github.com/estnltk/estnltk/tree/devel_1.7/estnltk_neural/estnltk_neural/taggers/morphosyntax/elative_construction/further.png)

In this case, the tagger finds "isikust ettevõtjaid". The first common parent node is "kohustama". But there is additional word between "ettevõtja" and "kohustama".
This is considered a longer path to the second target word and therefore match_type is "move_further".


### linear_match 

This category is given when two target words are next to eachother (regardless of adjectives) but the syntax tree is incorrect or would suggest another target.

![example of linear_match](https://github.com/estnltk/estnltk/tree/devel_1.7/estnltk_neural/estnltk_neural/taggers/morphosyntax/elative_construction/linear.png)

The target words are "treenerist" and "isa". However, the tree is incorrect and since "ema" is alo a potential match for "treenerist" then according to the syntax tree
 the match would be "treenerist ema". That is incorrect since those target words are separated by non-adjectives. To avoid such false matches, a linear match pushes the pair that is closest in the sentence - "treenerist isa".

In many cases, linear matches overlap with move_next or move_further matches. In such cases the next/further match is preferred as a category to distinguish the cases where the syntax tree is faulty and a linear match had to be used.



## potential_match 

It applies when the first target word exists in the sentence but the second target word is not in the dictionary. 

![example of potential_match](https://github.com/estnltk/estnltk/tree/devel_1.7/estnltk_neural/estnltk_neural/taggers/morphosyntax/elative_construction/potential.png)

If "treenerist" exists as a first target word but second target word from the dictionary is not found, then the first noun will be offered as potential second target.

This is experimental and would need a validator (wordnet, gpt, etc). It might be useful in expanding the target dictionary.



