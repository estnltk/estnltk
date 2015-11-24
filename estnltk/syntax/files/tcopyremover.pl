#!/usr/bin/perl
#remove copies

while(<>){
  chomp;
  if (/^[^ ]/) { 
	print $_, "\n"; 
	$eelm1="";
	$eelm2="";
	$eelm3="";
	$eelm4="";
	$eelm5="";
	$eelm6="";
	$eelm7="";
	$eelm8="";
	$eelm9="";
	$Kpre_removed=0;
	next;
  }
  if ($_ eq $eelm1 or $_ eq $eelm2 or $_ eq $eelm3 or $_ eq $eelm4 or $_ eq $eelm5 or 
	$_ eq $eelm6 or $_ eq $eelm7 or $_ eq $eelm8 or $_ eq $eelm9) 
	{next;}
  if (/_K_ pre \/\//) { $Kpre_removed=1; next;} 
  if (/_K_ post \/\// and $Kpre_removed==0) { next;}  
  $eelm9=$eelm8;
  $eelm8=$eelm7;
  $eelm7=$eelm6;
  $eelm6=$eelm5;
  $eelm5=$eelm4;
  $eelm4=$eelm3;
  $eelm3=$eelm2;
  $eelm2=$eelm1;
  $eelm1=$_;
  print $_,"\n";
}
