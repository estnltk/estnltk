#!/usr/bin/perl -w

open(TABLE,"< tmorftrtabel.txt")
  or die "$!\n";
while(<TABLE>){
  if (/^[^¤]+/) {
   chomp;
   @r = split(/@/);
   push(@tabel,[@r]);
  }
}
close(TABLE);

#for ($i=0;$i<$#tabel;$i++){
#  print $tabel[$i][1],"\n";
#}

$lipp=0;

while(<>){
  chomp;
  if (/^[^ ]+/) {
    print;
    print "\n";
    next;
  }
  $tolgendus=$_;	

	$tolgendus=~s/…([\+0]*) \/\/_Y_ \/\//…$1 \/\/_Z_ Ell \/\//; 
	$tolgendus=~s/…([\+0]*) \/\/_Z_ \/\//…$1 \/\/_Z_ Ell \/\//; 
	$tolgendus=~s/\.\.\.([\+0]*) \/\/_Z_ \/\//\.\.\.$1 \/\/_Z_ Ell \/\//; 
	$tolgendus=~s/\.\.([\+0]*) \/\/_Z_ \/\//\.\.$1 \/\/_Z_ Els \/\//; 
	$tolgendus=~s/\.([\+0]*) \/\/_Z_ \/\//\.$1 \/\/_Z_ Fst \/\//; 
	$tolgendus=~s/,([\+0]*) \/\/_Z_ \/\//,$1 \/\/_Z_ Com \/\//; 
	$tolgendus=~s/:([\+0]*) \/\/_Z_ \/\//:$1 \/\/_Z_ Col \/\//; 
	$tolgendus=~s/;([\+0]*) \/\/_Z_ \/\//;$1 \/\/_Z_ Scl \/\//; 
	$tolgendus=~s/\?([\+0]*) \/\/_Z_ \/\//\?$1 \/\/_Z_ Int \/\//; 
	$tolgendus=~s/\!([\+0]*) \/\/_Z_ \/\//\!$1 \/\/_Z_ Exc \/\//; 
	$tolgendus=~s/--([\+0]*) \/\/_Z_ \/\//--$1 \/\/_Z_ Dsd \/\//; 
	$tolgendus=~s/-([\+0]*) \/\/_Z_ \/\//-$1 \/\/_Z_ Dsh \/\//; 
	$tolgendus=~s/\(([\+0]*) \/\/_Z_ \/\//\($1 \/\/_Z_ Opr \/\//; 
	$tolgendus=~s/\)([\+0]*) \/\/_Z_ \/\//\)$1 \/\/_Z_ Cpr \/\//; 
	$tolgendus=~s/"([\+0]*) \/\/_Z_ \/\//"$1 \/\/_Z_ Quo \/\//; 
	$tolgendus=~s/«([\+0]*) \/\/_Z_ \/\//«$1 \/\/_Z_ Oqu \/\//; 
	$tolgendus=~s/»([\+0]*) \/\/_Z_ \/\//»$1 \/\/_Z_ Cqu \/\//; 
	$tolgendus=~s/“([\+0]*) \/\/_Z_ \/\//“$1 \/\/_Z_ Oqu \/\//; #E2 80 9C
	$tolgendus=~s/”([\+0]*) \/\/_Z_ \/\//”$1 \/\/_Z_ Cqu \/\//; #E2 80 9D
	$tolgendus=~s/<([\+0]*) \/\/_Z_ \/\//<$1 \/\/_Z_ Grt \/\//; 
	$tolgendus=~s/>([\+0]*) \/\/_Z_ \/\//>$1 \/\/_Z_ Sml \/\//; 
	$tolgendus=~s/\[([\+0]*) \/\/_Z_ \/\//\[$1 \/\/_Z_ Osq \/\//; 
	$tolgendus=~s/\]([\+0]*) \/\/_Z_ \/\//\]$1 \/\/_Z_ Csq \/\//; 
	$tolgendus=~s/\/([\+0]*) \/\/_Z_ \/\//\/$1 \/\/_Z_ Sla \/\//; 
	$tolgendus=~s/\=([\+0]*) \/\/_Z_ \/\//\=\+0 \/\/_V_ b, \/\//; 
	$tolgendus=~s/\+([\+0]*) \/\/_Z_ \/\//\+$1 \/\/_Z_ crd \/\//; 

    if ($tolgendus =~ /_Z_/) { print $tolgendus,"\n"; next; }		


    #if ($tolgendus =~ /(.*)\s+\/\/(_._) (.*)\/\/(.*)/){
    if ($tolgendus =~ /(.*)\s+\/\/(_._) (.*)\/\//){
        $root=$1 ;
	$pos=$2 ;
        @inf=split(/,/,$3);
	#$eki=$4 ;
	#print $1 ,"X" ,$2 ,"X", $3 ,"X" ,$4 ,"X";
	#print ">",@inf,"<";
        foreach $m (@inf){
	#print "\n=",$m;
          $m =~ s/\s+/ /g;
          $m =~ s/^\s+//g;
          next if ($m=~/^\s*$/); 
          $morf=$pos." ".$m;

          $morf=~s/(.*)\s+$/$1/g;  

$j=0;$lipp=0;
      	  foreach $rida (@tabel){
            if ($morf eq $rida->[1]) {
                $m2=$morf;

		$morf=~ s/$rida->[1]$/$rida->[3]/;
        	$morf=~ s/$rida->[1] \?$/$rida->[3]/;
		# oli: $morf=~ s/$rida->[1]$/$rida->[3]/;
		# ei teisendanud ?-ga lõppevaid ridu, nt "_N_ ?" 
                $morf=~s/ \?/ \#?/;  
                $morf=~s/ \?/ \#?/;  
#print "1";
                print $root." //".$morf." //\n";
                $morf=$m2; #last;
		$lipp++;

            }
            $j++;
          }
          if ($lipp==0) { print $root." //".$morf." //\n"; $lipp=0;}
        }
        if ($3=~/^\s*$/) {
          $morf=$pos;  
      	  foreach $rida (@tabel){
            if ($morf =~ /$rida->[1]/){
                $m2=$morf;
		# oli: $morf=~ s/$rida->[1]$/$rida->[3]/;
       		$morf=~ s/$rida->[1]/$rida->[3]/;
                $morf=~s/ \?/ \#?/;  
                $morf=~s/ \?/ \#?/;  
#print "$root"; print "$morf"; print "2";
                print $root." //".$morf." //\n";
                $morf=$m2;             }
          }
        }
#	$tolgendus="    ".$root." //".$morf." //";
    }
    else { print $tolgendus,"\n";		}
#{print $tolgendus,"\n";		}
}
