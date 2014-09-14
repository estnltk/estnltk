import re, os
import subprocess
from sys import argv,exit


if len(argv) < 2:
	print "Usage: python lit-pos-synidx_parser.py wordnet_file"

TMP_FILE = "../lit_pos_synidx_unordered.txt"
OUTPUT = "../lit_pos_synidx.txt"

synset_idx_regexp = re.compile("0\s+@(\d+)@\s+WORD_MEANING") 
pos_regexp = re.compile("\s+1\s+PART_OF_SPEECH\s+\"(.+)\"")
literal_regexp = re.compile("\s+2\s+LITERAL\s+\"(.+)\"")

with open(argv[1],'r') as fin, open(TMP_FILE,'w') as fout:
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

cmd = ['sort', '-o', TMP_FILE, TMP_FILE]

subprocess.Popen(cmd).wait()

with open(TMP_FILE,'r') as fin, open(OUTPUT,'w') as fout:
	prev_split_line = [""]*3
        prev_literal_synsets = []
        for line in fin:
                split_line = line.strip().split(':')
                if split_line[:2] == prev_split_line[:2]:
                        prev_literal_synsets.append(split_line[2])
                else:
                        fout.write("%s:%s:%s\n"%(prev_split_line[0],prev_split_line[1],' '.join(prev_literal_synsets)))
                        prev_split_line = split_line
                        prev_literal_synsets = [split_line[2]]
        fout.write("%s:%s:%s\n"%(prev_split_line[0],prev_split_line[1],' '.join(prev_literal_synsets)))

os.remove(TMP_FILE)
