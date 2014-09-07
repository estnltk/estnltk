# TODO fix parsing

import re, codecs
from sys import argv
from pyvabamorf import analyze_sentence

syn_idx_regexp = re.compile("0\s+@(\d+)@\s+WORD_MEANING")
pos_regexp = re.compile("\s+1\s+PART_OF_SPEECH\s+\"(\w+)\"")
literal_regexp = re.compile("\s+2\s+LITERAL\s\"(.+)\"")
sense_regexp = re.compile("\s+3\s+SENSE\s+(\d+)")

with codecs.open('%s'%argv[1],'r',encoding='utf-8') as fin, codecs.open("../synset_to_lemma.txt",'w',encoding='utf-8') as fout:
	for line in fin:
		result = syn_idx_regexp.match(line)
		if result:
			syn_idx = result.group(1)
			continue

		result = pos_regexp.match(line)
		if result:
			pos = result.group(1)
			continue

		result = literal_regexp.match(line)
		if result:
			literal = result.group(1)
			continue

		result = sense_regexp.match(line)
		if result:
			sense = result.group(1)
			lemma_product = analyze_sentence([literal])[0]
			for candidate in lemma_product['analysis']:
				form = candidate['form']
				lemma = candidate['lemma']
				cand_pos = candidate['partofspeech']
				
				fout.write("%s@%s:%s:%02d@%s:%s:%s\n"%(syn_idx,pos,literal,int(sense),lemma,form,cand_pos))
