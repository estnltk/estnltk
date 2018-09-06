# Converters

## CG3

## Dict

## json

## TCF

## Texta
Export Estnltk texts to Terminology EXtraction and Text Analytics ([TEXTA](https://github.com/texta-tk/texta)) Toolkit.
As TEXTA uses [Elasticsearch](https://www.elastic.co/products/elasticsearch) to store and query data, this is almost like exporting to Elasticsearch engine.

```python
from estnltk import Text
from estnltk.taggers import RobustDateNumberTagger

tagger = RobustDateNumberTagger()

texts = [Text('2018. aastal algab sügis 23. septembril kell 4:54.'),
         Text('Sügisjooksul osalejate arv võib küündida 25 000 inimeseni.')]
for text in texts:
    tagger.tag(text)

    
from estnltk.converters import TextaExporter

exporter = TextaExporter(index='collection',
                         doc_type='sentences',
                         facts_layer='dates_numbers',
                         fact_attr='grammar_symbol',
                         value_attr='value',
                         textapass='~/.textapass')

for text_id, text in enumerate(texts):
    r = exporter.export(text, meta={'text_id': text_id})
    print(r.text)
```
Output:
```
{"message": "Item(s) successfully saved."}
{"message": "Item(s) successfully saved."}

```
