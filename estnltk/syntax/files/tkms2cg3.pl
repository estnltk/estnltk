#!/usr/bin/perl -w
#konverteeri kms-kuju cg3-sisendkujule

while(<>){
  s/\#cap \#cap/cap/g;
  s/\#cap/cap/g; 
  s/\*\*CLB/CLB/g; 
  s/\#Correct!/<Correct!>/g; 
  s/\#\#\#\#//g;
  s/\#(\S+)/<$1>/g;
  s/\$([,.;!?:<]+)/$1/g;
  s/_Y_ \? _Z_/_Z_/g; 
  s/_Y_ _Z_/_Z_/g; 
  s/_Z_ \?/_Z_/g; 
  
  #sõna põhivorm
  chomp;
  if (/^\S+/){
    s/^(\S+)([ ]*)(.*)([ ]*)(.*)/"<$1$2$3$4$5>"/g;
    s/<<([^>]+)/<$1/g;
    s/([^<]+)>>/$1>/g;
    print;
    print "\n";
  } else {
  #tõlgendused
    s/\s+[-|+]*\s+(\S+)([ ]*)(.*)([ ]*)(.*)\+(\S+) \/\/_(\S)_ (.*)\/\/(.*)/    "$1$2$3$4$5" L$6 $7 $8 $9/g;
    s/\s+[-|+]*\s+(\S+)([ ]*)(.*)([ ]*)(.*) \/\/_(\S)_ (.*)\/\/(.*)/    "$1$2$3$4$5" $6 $7 $8/g;
    s/    \*\*CLB/ CLB/g; 
    s/    CLB/ CLB/g; 
    s/    +@/ +@/g; 
    s/    @/ @/g; 
  s/"<(.*)([ ]*)(.*)([ ]*)(.*)>"/"$1$2$3$4$5"/g; 
  print $_ ."\n" if (/\S/);
#  print "\n";
  }
}  
