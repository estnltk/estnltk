import re
from sys import argv,exit


if len(argv) < 3:
	print "Usage: python lit-pos-synidx_parser.py wordnet_file output_dir"

synset_idx_regexp = re.compile("0\s+@(\d+)@\s+WORD_MEANING") 
pos_regexp = re.compile("\s+1\s+PART_OF_SPEECH\s+\"(.+)\"")
literal_regexp = re.compile("\s+2\s+LITERAL\s+\"(.+)\"")

with open(argv[1],'r') as fin, open("%s/lit-pos-synidx_tmp.txt"%argv[2],'w') as fout:
	for line in fin:
		result = synset_idx_regexp.match(line)
		if result != None:
			synset_idx = result.group(1)
			continue

		result = pos_regexp.match(line)
		if result != None:
			pos = result.group(1)
			continue

		result = literal_regexp.match(line)
		if result != None:
			literal = result.group(1)
			fout.write("%s:%s:%s\n"%(literal,pos,synset_idx))
