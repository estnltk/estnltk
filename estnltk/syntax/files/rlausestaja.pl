#!/usr/bin/perl -w

# arvestatakse, et reavahetus on lõigupiir ja ka lausepiir

use locale;
my $rida = "";


while (<>){
    
  chomp;
  s:\”:":g;
  s:\“:":g;
  s:«:":g;
  s:»:":g;
  $rida = $_;
  $rida=convert_umlauts($rida); 
  $rida =~ s:([^>]+)$:$1 </s> :g;      #v\n
  $rida =~ s:^([^<]): <s> $1:g;         		       	       #\nv
  $rida =~ s:([a-zõäöü]\.) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;         #v. S
  $rida =~ s:(\)\.) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;                #). S
  $rida =~ s:(\273\.) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;              #". S
  $rida =~ s:(\.\273) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;              #.". S
  $rida =~ s:([a-zõäöü]\.)[ ]*(\253[A-ZÕÄÖÜ]):$1</s> <s>$2:g;  #v. "S
  $rida =~ s:([a-zõäöü]\.) ("\“[A-ZÕÄÖÜ]):$1</s> <s>$2:g;        #v. "S
  $rida =~ s:([a-zõäöü]\.) (\253\253[A-ZÕÄÖÜ]):$1</s> <s>$2:g; #v. ""S
  if ($rida =~ m:[a-zõäöü]\. [0-9]:){                          #v. N
    if ($rida !~ m:nr\.:){
      $rida =~ s:([a-zõäöü]\.) ([0-9]):$1</s> <s>$2:g;
    }
  } 
  $rida =~ s:([0-9]%\.) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;            #N%. S
  $rida =~ s:([0-9]\.) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;             #N. S      
  $rida =~ s:([a-zõäöü][!\?]\273) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;     #v!" S
  # hüüu- ega küsimärk ei ole tsitaadis
  if ($rida !~ m:\253:){
    $rida =~ s:([a-zõäöü][!\?]) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;  #v! S
   $rida =~ s:([a-zõäöü][!\?]) ([0-9]):$1</s> <s>$2:g;       #v! N
    $rida =~ s:([a-zõäöü]\?!) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;    #v?! S
  }
  else {
    $rida =~ s:(\: \253[^\273]*[\.!\?]\273) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g;
    while($rida =~ s:(<s>[^\253]*?[a-zõäöü][!\?]) ([A-ZÕÄÖÜ]):$1</s> <s>$2:g){}
   
  }
  $rida =~ s:(<s>\253[^\<\273]*?)(</s> <s>):$1\273$2\253:g; #<">< => <""><"
  #$rida = convert_back($rida);

  # normaliseeri morfanalüsaatori jaoks jutumärgid

  $rida =~ s:([^ ])\" :$1 ":g;
  $rida =~ s:\"([^ ]):" $1:g;
   $rida =~ s:([^ ])»:$1 ”:g;
   $rida =~ s:«([^ ]):“ $1:g;
   $rida =~ s:([^ ])”:$1 ”:g;
   $rida =~ s:\“([^ ]):“ $1:g;
  $rida =~ s:([^ ])\):$1 ):g;
  $rida =~ s:\(([^ ]):( $1:g;
  $rida =~ s:>([^ ]):> $1:g;
  $rida =~ s:([^ ])<:$1 <:g;
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”][\.?!][\.!?]) :$1 $2 :g; # 3.. . teeb
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”][\.!?]) :$1 $2 :g;
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”]) :$1 $2 :g;

  $rida =~ s:([^\d])\. :$1 . :g;
  $rida =~ s:(\d+) (\d+) (\d+):$1$2$3:g;
  $rida =~ s:(\d+) (\d+):$1$2:g;

#  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”])$:$1 $2 :g;
#  $rida =~ s:(.*)$:$1 !!! :g;
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”][\.!?][\.!?].) </s> $:$1 $2 </s> :g;      #v\n
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”][\.!?].) </s> $:$1 $2 </s> :g;      #v\n
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”].) </s> $:$1 $2 </s> :g;      #v\n
  $rida =~ s:([^ ])([\.,!?;\-\:\"\)\(«»“”]) </s> $:$1 $2 </s> :g;      #v\n

  $rida =~ s: s : 's' :g;
  $rida =~ s:  : :g;
  $rida =~ s: :\n:g;
  print $rida;
 
}

sub convert_umlauts{
  my $l=$_[0];
  $l =~ s/&auml;/ä/g;
  $l =~ s/&ouml;/ö/g;
  $l =~ s/&uuml;/ü/g;
  $l =~ s/&otilde;/õ/g;
  $l =~ s/&Auml;/Ä/g;
  $l =~ s/&Ouml;/Ö/g;
  $l =~ s/&Uuml;/Ü/g;
  $l =~ s/&Otilde;/Õ/g; 
  $l =~ s/&raquo;/\273/g;
  $l =~ s/&laquo;/\253/g;
  $l =~ s/&rdquo;/\273/g;
  $l =~ s/&ldquo;/\253/g;
  return $l;
}

sub convert_back{
  my $l=$_[0];
  $l =~ s/ä/&auml;/g;
  $l =~ s/ö/&ouml;/g;
  $l =~ s/ü/&uuml;/g;
  $l =~ s/õ/&otilde;/g;
  $l =~ s/Ä/&Auml;/g;
  $l =~ s/Ö/&Ouml;/g;
  $l =~ s/Ü/&Uuml;/g;
  $l =~ s/Õ/&Otilde;/g; 
  $l =~ s/\273/&raquo;/g;
  $l =~ s/\253/&laquo;/g;
  return $l;
}
