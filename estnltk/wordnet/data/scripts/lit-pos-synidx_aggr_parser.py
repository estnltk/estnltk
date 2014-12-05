import re
from sys import argv,exit


if len(argv) < 3:
	print "Usage: python lit-pos-synidx_parser.py ordered_lit-pos-synidx_dir output_dir"

with open("%s/lit-pos-synidx.txt"%argv[1],'r') as fin, open("%s/lit-pos-synidx2.txt"%argv[2],'w') as fout:
	posses = set()

	prev_split_line = [""]*3
	prev_literal_synsets = []
	for line in fin:
		split_line = line.strip().split(':')
		posses.update([split_line[1]])
		if split_line[:2] == prev_split_line[:2]:
			prev_literal_synsets.append(split_line[2])
		else:
			fout.write("%s:%s:%s\n"%(prev_split_line[0],prev_split_line[1],' '.join(prev_literal_synsets)))
			prev_split_line = split_line
			prev_literal_synsets = [split_line[2]]
	fout.write("%s:%s:%s\n"%(prev_split_line[0],prev_split_line[1],' '.join(prev_literal_synsets)))

print posses
