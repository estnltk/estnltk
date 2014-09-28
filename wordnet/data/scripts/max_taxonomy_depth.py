import sys, os

_MY_DIR = os.path.dirname(__file__)

sys.path.insert(1,os.path.join(_MY_DIR,'..','..'))

import wn

FILE_ = os.path.join(_MY_DIR,'..','max_tax_depths.cnf')

max_depths = {}

for pos in 'bavn':
	all_synsets = wn.all_synsets(pos)
	n = len(all_synsets)

	max_depth = -1

	for i in range(n):
		depth = all_synsets[i]._min_depth()
		max_depth = depth if depth > max_depth else max_depth
	max_depths[pos] = max_depth

with open(FILE_,'w') as fout:
	for pos in max_depths:
		fout.write("%s:%d\n"%(pos,max_depths[pos]))
