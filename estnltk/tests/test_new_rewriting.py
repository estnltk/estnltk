from estnltk.text import Text, Layer, words_sentences

conversions_new = [
                      ["…$",      "Ell"],
                      ["\.\.\.$", "Ell"],
                      ["\.\.$",   "Els"],
                      ["\.$",     "Fst"],
                      [",$",      "Com"],
                      [":$",      "Col"],
                      [";$",      "Scl"],
                      ["(\?+)$",  "Int"],
                      ["(\!+)$",  "Exc"],
                      ["(---?)$", "Dsd"],
                      ["(-)$",    "Dsh"],
                      ["\($",     "Opr"],
                      ["\)$",     "Cpr"],
                      ['\\\\"$',  "Quo"],
                      ["«$",      "Oqu"],
                      ["»$",      "Cqu"],
                      ["“$",      "Oqu"],
                      ["”$",      "Cqu"],
                      ["<$",      "Grt"],
                      [">$",      "Sml"],
                      ["\[$",     "Osq"],
                      ["\]$",     "Csq"],
                      ["/$",      "Sla"],
                      ["\+$",     "crd"]
]


text = words_sentences('Minu nimi on Uku, mis sinu nimi on? Miks me seda arutame?')
newlayer = Layer(name='layer1',
                 parent='words',
                 attributes = ['rewrite_from']
                 )
text._add_layer(newlayer)
for word in text.words:
    word.mark('layer1').rewrite_from = ')'

newlayer2 = Layer(name='layer2',
                 parent='words',
                 attributes = ['rewrite_to']
                 )

text.layer1.rewrite(to=text.layer2,
                    rules = func
                    )
