import csv
from adjective_phrase_tagger.adj_phrase_tagger import AdjectivePhraseTagger
from estnltk import *
from pprint import pprint
import codecs

tagger = AdjectivePhraseTagger(return_layer=False, layer_name = 'adjective_phrase')

#file=open("comments_phrases_from_csv_9.txt", "w")
#file.close()

#db2 = Database("ohtuleht_adjective_phrases_from_csv_j")  #171479-250200

ok_phrases = []
not_ok_phrases = []
i = 0

with codecs.open('all_comments.csv', 'r','utf-8') as csvfile, codecs.open("comments_phrases_from_csv_test.txt", "a") as fout:
    reader = csv.reader(csvfile)
    
    for row in reader:
        i += 1
        if i%100 == 0:
            print(i)
        if i > 0:
            #print(i)
            text = Text(row[1])
            #print(text)
            text['score'] = row[2]
            text['id'] = row[0]

                
            tagger.tag(text)
            if 'adjective_phrase' in text:
                if text['score'] == 'ok':
                    for phrase in text['adjective_phrase']:
                        print(phrase['lemmas'])
                        fout.write("#ok# " + str(phrase['lemmas']))
                        fout.write("\n")
                else:
                    for phrase in text['adjective_phrase']:
                        print(phrase['lemmas'])
                        fout.write("#" + text['score'].replace("\n", "+") + "# " + str(phrase['lemmas']))
                        fout.write("\n")
                 
            #db2.insert(text)
        #if i%100 == 0:
        #    print(i)
        #print(i, )
        
        







