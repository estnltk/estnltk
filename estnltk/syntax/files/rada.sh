#!/bin/sh
RADA=./
RADAMRF=/home/timo/projects/vabamorf/apps/cmdline/project/unix
RADADCT=/home/timo/projects/vabamorf/dct/binary

cat $1 | $RADA/rlausestaja.pl | python $RADA/w2json.py  | $RADAMRF/etana analyze -lex $RADADCT/et.dct -guess | python $RADA/json2mrf.py | $RADA/rtolkija.pl | $RADA/tpron.pl | $RADA/tcopyremover.pl |awk -f $RADA/TTRELLID.AWK | $RADA/tagger09 $RADA/abileksikon06utf.lx stdin stdout | $RADA/tcopyremover.pl | $RADA/tkms2cg3.pl  | $RADA/vislcg3 -o -g $RADA/clo_ub.rle | $RADA/vislcg3 -o -g $RADA/morfyhe_ub.rle | $RADA/vislcg3 -o -g $RADA/PhVerbs_ub.rle  | $RADA/vislcg3 -o -g $RADA/pindsyn_ub.rle  | $RADA/vislcg3 -o -g $RADA/strukt_ub.rle  > $1.cg3


