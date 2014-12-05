import re
import subprocess
from sys import argv,exit


if len(argv) < 2:
	print "Usage: python lit-pos-synidx_parser.py wordnet_file"
	exit()

OUTPUT = "../sense.txt"

synset_idx_regexp = re.compile("0\s+@(\d+)@\s+WORD_MEANING") 
pos_regexp = re.compile("\s+1\s+PART_OF_SPEECH\s+\"(.+)\"")
literal_regexp = re.compile("\s+2\s+LITERAL\s+\"(.+)\"")
sense_regexp = re.compile("\s+3\s+SENSE\s+(\d+)")

with open(argv[1],'r') as fin, open(OUTPUT,'w') as fout:
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
			continue

		result = sense_regexp.match(line)
		if result != None:
			sense = "%02d" % int(result.group(1))
			fout.write("%s.%s.%s:%s\n"%(literal,pos,sense,synset_idx))

subprocess.Popen(['sort','-o',OUTPUT,OUTPUT]).wait()
