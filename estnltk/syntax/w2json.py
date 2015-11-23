#!/usr/bin/python

import sys, json

def convert():
    pars = {"paragraphs": []}
    sens = {"sentences": []}
    sentence = {"words": []}
    l = sys.stdin.readline()    
    rows = 1
    try:
        while l:
            line = l.strip()
            if len(line) > 0:
                word = {"text": line}
                sentence["words"].append(word)
                if line == "</s>":
                    sens["sentences"].append(sentence) 
                    sentence = {"words": []}
            l = sys.stdin.readline()
            rows = rows + 1
    except IndexError:
        sys.stderr.write("Could not read line: \n")
        sys.stderr.write(" %s" % line)
        sys.stderr.write(" %d \n" % rows)
        sys.exit(1)
    pars["paragraphs"].append(sens) 
    print json.dumps(pars, ensure_ascii = False, indent=4)


def usage():
    sys.stderr.write("""
    Usage: python w2json.py\n""")

if __name__ == "__main__":

    if len(sys.argv)!=1:
        usage()
        sys.exit(1)
    convert()

