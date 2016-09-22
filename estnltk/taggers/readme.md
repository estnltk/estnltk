
# AdjectivePhraseTagger

A class that tags simple adjective phrases in the **Text** object.

## Usage


```python
from adjective_phrase_tagger.adj_phrase_tagger import AdjectivePhraseTagger
from estnltk import Text
```

Create **Text** object, **AdjectivePhraseTagger** object and tag adjective phrases as a new layer of the **Text** object.


```python
tagger = AdjectivePhraseTagger(return_layer=True) # return_layer=True returns only the adjective phrase layer
sent = Text("Peaaegu 8-aastane koer oli väga energiline ja mänguhimuline.")
tagger.tag(sent)
```




    [{'adverb_class': 'doubt',
      'end': 17,
      'intersects_with_verb': False,
      'lemmas': ['peaaegu', '8aastane'],
      'measurement_adj': True,
      'start': 0,
      'text': 'Peaaegu 8-aastane',
      'type': 'adjective'},
     {'adverb_class': 'strong_intensifier',
      'end': 59,
      'intersects_with_verb': False,
      'lemmas': ['väga', 'energiline', 'ja', 'mänguhimuline'],
      'measurement_adj': False,
      'start': 27,
      'text': 'väga energiline ja mänguhimuline',
      'type': 'adjective'}]



### Attributes that are given with the adjective phrases:

**type** is the type of the phrase: 
* **adjective**: adjective is in its 'normal' (aka positive) form
* **comparative**: contains a comparative adjective
* **participle**: contains an adjective derived from a verb

**measurement_adj** means that the adjective in the phrase either contains a number or some other type of measurement

**intersects_with_verb** signifies whether the found adjective phrase intersects with a verb phrase in the text; this happens mostly in the case of participles as in the following sentence:


```python
tagger.tag(Text("Ta oli väga üllatunud."))
```




    [{'adverb_class': 'strong_intensifier',
      'end': 21,
      'intersects_with_verb': True,
      'lemmas': ['väga', 'üllatunud'],
      'measurement_adj': False,
      'start': 7,
      'text': 'väga üllatunud',
      'type': 'participle'}]



**adverb_class** marks the intensity of the adverb in the phrase. Currently there are 6 classes:
* diminisher
* doubt
* affirmation
* strong_intensifier
* surprise
* excess

All the adverbs are not divided into classes, therefore some do have _unknow_ as class.

### Example

Adjective phrases can be used for sentiment analysis - determining the polarity of the text. While this is often done using only adjectives, the phrases consisting of an adverb and an adjective can give more precise results because adverbs in these kinds of phrases are usually some sort of intensifiers. For this purpose, the most frequent adverbs are already divided into classes based on their intensifying properties (see above).

#### Tagging adjective phrases in hinnavaatlus.ee user reviews to use them as a feature in text classification (e.g. http://estnltk.github.io/estnltk/1.4/tutorials/textclassifier.html)


```python
import csv

with open('data/hinnavaatlus.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    
    for idx, row in enumerate(reader):
        e = tagger.tag(Text(row[1]))

        print(row[1])
        for i in e:
            if len(i) > 0:  
                print(i['lemmas'])
        print("-----------------------------")
        if idx > 5:
            break

```

    Kommentaar
    -----------------------------
    Väike, aga tubli firma!
    ['väike']
    ['tubli']
    -----------------------------
    väga hea firma
    ['väga', 'hea']
    -----------------------------
    Viimasel ajal pole midagi halba öelda, aga samas ei konkureeri nad kuidagi Genneti, Ordiga ei hindadelt ega teeninduselt. Toorikute ja tindi ostmiseks samas hea koht ja kuna müüjaid on rohkem valima hakatud, siis võiks 2 ikka ära panna - tuleks 3 kui hinadele ei pandaks kirvest ja toodete saadavus oleks parem.
    ['viimane']
    ['halb']
    ['hea']
    ['hakatud']
    ['parem']
    -----------------------------
    Fotode kvaliteet väga pro ja "jjk" seal töötamise ajal leiti ikka paljudele asjadele väga meeldivad lahendused. Samas hilisem läpaka ost sujus ka väga meeldivalt - sain esialgse rahas ostusoovi vormistada ümber järelmaksule...äärmiselt asjalik teenindus.
    ['hilisem']
    ['esialgne']
    ['äärmiselt', 'asjalik']
    ['väga', 'meeldiv']
    -----------------------------
    Ainult positiivsed kogemused
    ['positiivne']
    -----------------------------
    Viimane kord, kui käisin suutis leti taga askeldav ~60 aastane mees tegutseda nii aeglaselt, et minu seal veedetud 10min jooksul pani juba vähemalt 6-7 klienti putku. Garantiiga ka kurvad kogemused, neid poleks, saaks isegi kahe vast. Vihaseks ajab lihtsalt vahest nende teenindus!
    ['viimane']
    ['askeldav']
    ['aastane']
    ['veedetud']
    ['kurb']
    ['vihane']
    -----------------------------



```python

```
