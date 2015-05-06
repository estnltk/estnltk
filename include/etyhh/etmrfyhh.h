#if !defined( ETMRFANA_H )
#define ETMRFYHH_H

/*
dct/data/yhh/all.cooked on sellisel kujul:
- Iga lause on omaette real.
- Punktuatsioon, sulud jms on sõnast lahku tõstetud.
- Igale sõnale, kirjavahemärgile jms järgneb tühikuga eraldatult ühestamismärgend.

Ühestaja andmefail tehakse 2 programmi abil:
- dct-t3mesta -cio kodeering treeningkorpus
- dct-t3pakitud

dct-t3mesta teeb treeningkorpuse põhjal failid:
- taglist.txt Ühestamismärgendite loend. Treeningkorpuses mittesinev ***VAHE***
  on vajalik trigrammide tabelis lause alguse/lõpuga seotud märgendijärjendite 
  tõenäosuste arvutamiseks. 
  Fail on kujul: märgendi-indeks märgend
- margcnt.txt Ühestamismärgendi esinemiste arv. 
  Fail on kujul: märgend esinemisarv
- 3grammid.txt Trigrammid. 
  Fail on kujul: märgend märgend märgend tõenäosuse-logaritm
- klassid.txt Sõnest sõltumatult mitmesusklassid. 
  Fail on kujul: 
  märgendite-arv-klassis märgend[1]=tõenäosuse-logaritm[1] ... märgend[märgendite-arv-klassis]=tõenäosuse-logaritm[märgendite-arv-klassis]
- lex.txt Sõnest sõltuvad mitmesusklassid. 
  Fail on kujul: 
  sõne [märgendite-arv-klassis] märgend[1]=tõenäosuse-logaritm[1] ... märgend[märgendite-arv-klassis]=tõenäosuse-logaritm[märgendite-arv-klassis]
Trigrammid ja sõnest sõltuvad mitmesusklassid arvutatakse sarnaselt 
Ingo Schröder'i Icopost'i tarkvarapaketile (vt Ingo Schröder. 2001. 
A Case Study in Part-of-Speech Tagging Using the ICOPOST Toolkit. 
http://acopost.sourceforge.net/schroder2002.pdf).
Loodud tekstifaile kasutab ainult programm dct-t3pakitud. 
Nende ainus mõte on selles, et võimaldavad ühestaja kasutajal paremini mõista 
ühestaja käitmist erinevates olukordades. 

dct-t3pakitud võtab jooksvast kataloogist dct-t3mesta tehtud 5 väljundfaili ja 
teeb neist ühestamismooduli poolt kasutatava leksikonifaili et3.dct.
Ühestaja saab sisendiks morfoloogiliselt analüüsitud teksti, kus punktuatsioon 
on sõnast enne analüüsi lahku tõstetud. 
Kontekstist sõltuvaid tõenäosusi (trigramme) ja treenigkorpuses esinevate 
sõnedega seotud märgendite tõenäosusi arvutatakse sarnaselt Ingo Schröder'i 
Icopost'i tarkvarapaketile (vt Ingo Schröder. 2001. 
A Case Study in Part-of-Speech Tagging Using the ICOPOST Toolkit. 
http://acopost.sourceforge.net/schroder2002.pdf). 
Nende sõnede jaoks, mida treeningkorpuses polnud, on võimalikud analüüsid 
saadud eelnevalt morfoloogilise analüüsi-oletamise moodulist ja kasutakse 
treeningkorpuse põhjal leitud sõnest sõltumatuid mitmesusklasse (vt faili klassid.txt). 

Morf ühestamise moodul võtab sisendiks treeningkorpuse põhjal tehtud andmefaili 
ja morfoloogiliselt analüüsitud teksti. Tekstis peavad olema lausepiirid 
märgendatud ja punktuatsioon sõna küljest lahku tõstetud ning samuti 
morfoloogiliselt analüüsitud.
Ühestamine toimub sarnaselt Ingo Schröder'i Icopost'i tarkvarapaketile (vt Ingo Schröder. 2001. 
A Case Study in Part-of-Speech Tagging Using the ICOPOST Toolkit. 
http://acopost.sourceforge.net/schroder2002.pdf).
*/

#include "etmrf.h"
#include "t3common.h"

#endif

