# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys, json

def convert():
    sens = json.loads(sys.stdin.read().replace("\\n", "\n").replace('"\\\\""', '"\\""'), encoding = 'utf-8')["paragraphs"][0]["sentences"] 
    for sentence in sens:
        print ("<s>\n")
        for word in sentence["words"]:
            if word["text"] == "<s>" or word["text"] == "</s>":
                continue
            print (word["text"]).encode('utf-8')
            for al in word["analysis"]:
                if al["ending"] == "":
                    print ("    "+al["root"].replace("\\", "\\\\")+"+0 //_"+al["partofspeech"]+'_ '+al["form"]+" //").encode('utf-8')
                else:
                    print ("    "+al["root"].replace("\\", "\\\\")+'+'+al["ending"]+" //_"+al["partofspeech"]+'_ '+al["form"]+" //").encode('utf-8')
        print ("</s>\n")

def usage():
    sys.stderr.write("""
    Usage: python json2mrf.py\n""")

if __name__ == "__main__":

    if len(sys.argv)!=1:
        usage()
        sys.exit(1)
    convert()

