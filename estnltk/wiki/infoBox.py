# -*- coding: utf-8 -*-
__author__ = 'Andres'



import re
import json
import pprint
from wikiextra import balancedSlicer as bSB

linkBegin = "http://et.wikipedia.org/wiki/"

infob = """iygyugyugyugyugyugyugyuyg{{See artikkel| on Altamira koopast Hispaanias; samanimeliste kohtade kohta vaata lehekülge [[Altamira (täpsustus)]]}}
{{UNESCO
|Nimi       = Altamira
|Pilt       = [[Pilt:Techo de Altamira (replica)-Museo Arqueológico Nacional.jpg|300px|Koopamaalid]]
|Pildiinfo  = Altamira koopamaalid
|Asukoht    = {{PisiLipp|Hispaania}}
|Tüüp       = Kultuurimälestis
|Kriteerium = I, III
|ID         = 310
|Regioon    = Euroopa ja Põhja-Ameerika
|Laiuskoord  = 43/22/39/N
|Pikkuskoord = 4/7/9/W
|Aasta      = 1985
|Istung     =
|Laiendatud = 2008
|Ohus       =
}}
}}yuguibguihuihiuih"""

def infoBoxParser(text):
    t = ''
    infobStartRegEx = re.compile(r"(?!\<ref>)\{\{[^\}]+?\n ?\|.+?=" , re.DOTALL)
    infob = [x for x in re.finditer(infobStartRegEx, text)]
    if infob:
        for i in infob:
            start = i.start()
            infobContent, end = bSB(text[start:], openDelim='{', closeDelim='}')
            print('Infobox:', text[start:end])
            t = text[:start]+text[end:]
            if infobContent:
                infobContent = infobContent.replace('[', '').replace(']', '').splitlines()  #.replace('|', '').split('\n'))
                infobDict = {}
                for line in infobContent:
                    line = line.strip('|  ').strip(' ')
                    line = line.split('=')
                    if len(line) == 2:
                        if line[0] and line[1]:
                            l = line[1].strip('[').strip(']').strip()
                            if '|' in l:
                                l = l.split('|')[1]
                            infobDict[line[0].strip()]= l

        return t, infobDict

    return None

#pprint.pprint(infobDict)
if __name__ == '__main__':
    ar = """"{{ToimetaAeg|kuu=september|aasta=2006}}
{{Lisaviiteid|kuupäev=veebruar 2015}}
{{Infokast president
| nimi=Arnold Rüütel
| pildi nimi=Estlands president Arnold Ruutel.jpg
| pildi suurus=300px
| amet=3. [[Eesti Vabariigi President]]
| ametiajaalgus=2001
| ametiajalõpp=2006
| predecessor=[[Lennart Meri]]
| järgmine=[[Toomas Hendrik Ilves]]
| sünnikuupäev=[[10. mai]] [[1928]]
| sünnikoht=[[Saaremaa]]l
| surmakuupäev=
| surmakoht=
| partei=
|}}
'''Arnold Rüütel''' (sündinud [[10. mai]]l [[1928]] [[Laimjala vald (Pöide kihelkond)|Laimjala vallas]] [[Pahavalla|Pahavalla külas]]) on [[Eesti]] poliitik ja põllumajandusteadlane, [[Eesti Vabariigi president]] aastatel [[2001]]–[[2006]].

Arnold Rüütel kuulub [[1999]]. aastal valitud [[20. sajandi sada suurkuju|20. sajandi saja suurkuju]] hulka ja ta on valitud [[aasta inimene|aasta inimeseks]] ([[2001]]).

==Elulugu==
Arnold Rüütel on sündinud [[10. mai]]l [[1928]] [[Laimjala vald (Pöide kihelkond)|Laimjala vallas]] [[Saaremaa]]l [[Õigeusk|õigeusuliste]] eestlaste Feodor ja Juuli Rüütli perekonnas.

1946–1949 õppis ta [[Jäneda põllumajandustehnikum]]is, kus kirjutas 17. oktoobril 1946 avalduse [[Komsomol|Üleliidulise Leninliku Kommunistliku Noorsooühingu]] liikmeks astumiseks. Pärast põllumajandustehnikumi lõpetamist töötas ta Saaremaa TSN Täitevkomitee põllumajandusosakonna vanemagronoomina. Hiljem oli Arnold Rüütel [[Tartu Põllumajanduse Mehhaniseerimise Kooli]] õpetaja.

Seejärel sai temast [[Eesti Loomakasvatuse ja Veterinaaria Teadusliku Uurimise Instituut|Eesti Loomakasvatuse ja Veterinaaria Teadusliku Uurimise Instituudi]] katsebaasi peazootehnik ja seejärel direktor. [[Tartu näidissovhoos]]i direktori ametis olles lõpetas Rüütel töö kõrvalt 1964. aastal [[Eesti Maaülikool|Eesti Põllumajanduse Akadeemia]] [[agronoomia]] erialal.
[[File: Karl XXII istutatud tamm Vana-Antsa pargis.jpg|pisi|left|Rüütel 1978. aastal Vana-Antsla pargis tamme kõrval. Esireas [[Johannes Käbin]] (EKP Keskkomitee 1. sekretär), Elmo Saar (Antsla ST direktor) ja Rüütel (tollal EKP Keskkomitee sekretär). Tagareas alates tammest: Endel Saia (EKP Võru Rajoonikomitee 1. sekretär), Aare Lang (Antsla ST  partorg ja õpetaja).]]
Aastal 1969 valiti Arnold Rüütel [[Eesti Põllumajanduse Akadeemia]] rektoriks, kellena ta lisaks teadusjuhi igapäevaste kohustuste täitmisele tegeles aktiivselt ka teadustööga.

Töö kõrvalt on Arnold Rüütel tuntud ka avaliku elu tegelasena, olles aastaid olnud loodushoidu ja -kasvatust propageeriva [[Eesti Looduskaitse Selts]]i esimees ning hariduselu edendava [[Forseliuse Selts]]i esimees. Arnold Rüütel asutas ühiskondlikel alustel tegutseva [[Rahvusliku Arengu ja Koostöö Instituut|Rahvusliku Arengu ja Koostöö Instituudi]], mis on oma eesmärgiks seadnud Eesti peamiste arengufaktorite uurimise.

Arnold Rüütel on ka ülemaailmse [[Roheline Rist|Rohelise Risti]] Eesti rahvusliku organisatsiooni president. See organisatsioon on eelkõige hea seisnud selle eest, et puhastada Eesti territoorium Nõukogude armee jäetud reostusest ja selle tagajärgedest ning hoida Eesti järeltulevatele põlvedele puhta ning loodussõbralikuna. Arnold Rüütel on olnud ka liikumise [[Hoia Eesti Merd]] esimees. See ühendus on oma hoole alla võtnud Eesti enam kui 3,5 tuhande kilomeetri pikkuse rannajoone korrastamise ning pühendunud väikesadamate taastamisele ja rajamisele.

==Haridus==
*[[1949]] [[Jäneda]] Põllumajandustehnikum
*[[1964]] lõpetas töö kõrvalt [[Eesti Põllumajanduse Akadeemia]] [[agronoomia]] erialal
*[[1972]] põllumajandusteaduste kandidaat
*[[1991]] kaitses [[Venemaa]]l põllumajandusdoktori kraadi

==Ametikohad==
[[Pilt:Arnold Rüütel Vasknarva piirivalvekordonis.jpg|pisi|Arnold Rüütel 2004. aastal Vasknarva piirivalvekordonis.]]
*[[1949]]–[[1950]] Saaremaa Töörahva Saadikute Nõukogu Täitevkomitee põllumajandusosakonna vanemagronoom
*[[1950]]–[[1955]] armeeteenistus;
*[[1955]]–[[1957]] [[Tartu]] Põllumajanduse Mehhaniseerimise Kooli õpetaja
*[[1957]]–[[1963]] [[Eesti Loomakasvatuse ja Veterinaaria Teadusliku Uurimise Instituut|Eesti Loomakasvatuse ja Veterinaaria Teadusliku Uurimise Instituudi]] katsebaasi peazootehnik
*[[1963]]–[[1969]] [[Tartu Näidissovhoos]]i direktor
*[[1969]]–[[1977]] [[Eesti Põllumajanduse Akadeemia]] rektor
*[[1969]] – [[Eesti NSV|Eesti Nõukogude Sotsialistliku Vabariigi]] [[Eesti NSV Ülemnõukogu|Ülemnõukogu]] Presiidiumi aseesimees
*[[1977]]–[[1979]] [[EKP Keskkomitee sekretär]] põllumajanduse alal
*[[1977]] – [[Eestimaa Kommunistlik Partei|Eestimaa Kommunistliku Partei]] [[EKP Keskkomitee|Keskkomitee]] sekretär põllumajanduse alal ja EKP Keskkomitee büroo liige
*[[1979]]–[[1983]] [[Eesti NSV Ministrite Nõukogu]] esimehe esimene asetäitja
*[[1983]]–[[1990]] [[Eesti NSV Ülemnõukogu Presiidiumi esimees]]
*[[1990]] – oktoober [[1992]] Eesti NSV Ülemnõukogu (ja pärast selle ümbernimetamist Eesti Vabariigi Ülemnõukogu) esimees
*[[1991]]–[[1992]] Põhiseadusliku Assamblee liige
*[[1993]]–[[2001]] Rahvusliku Arengu ja Koostöö Instituudi direktor
*[[1994]]–[[1999]] Eesti Maarahva Erakonna esimees
*[[1999]]–[[2000]] Eestimaa Rahvaliidu esimees
*[[2000]]–[[2001]] Eestimaa Rahvaliidu auesimees
*[[1995]]–[[2001]] [[Riigikogu]] liige
*[[1995]]–[[1997]] Riigikogu aseesimees
*[[1995]]–[[1999]] koalitsiooninõukogu esimees
*[[1995]]–[[1999]] Riigikogu Balti Assamblee Eesti delegatsiooni juht
*[[1995]]–[[1999]] Balti Assamblee Presiidiumi liige ja vaheaegadega esimees
*[[8. oktoober]] [[2001]] – [[9. oktoober]] 2006 Eesti Vabariigi president

==Poliitiline tegevus==
[[Pilt:Est UN.jpg|pisi|Arnold Rüütel esinemas ÜRO Peaassambleel.]]
[[Pilt:George W. Bush John Paul II funeral.jpg|pisi|Arnold Rüütel [[Johannes Paulus II]] matustel.]]
*[[1964]]. aastal astus [[NLKP|Nõukogude Liidu Kommunistlikku Parteisse]].
*[[1966]]–[[1971]] oli ta EKP Keskkomitee liikmekandidaat;
*[[1971]]. aastast EKP Keskkomitee liige;
*[[1977]]. aastast EKP Keskkomitee sekretär.
*[[1983]]. aastal valiti ta Eesti NSV Ülemnõukogu Presiidiumi esimeheks. Ta oli Eesti NSV Ülemnõukogu VII ja VIII koosseisu saadik ning Ülemnõukogu Presiidiumi esimees.
*[[1988]]. aasta kevadeni oli Arnold Rüütel nii poliitilises tegevuses kui ka avalikes sõnavõttudes täielikult lojaalne Nõukogude Liidu keskvõimudele.
*[[20. veebruar]]il [[1988]] üle kantud televisioonikõnes kritiseeris ta [[Balti küsimus]]e ülestõstmist [[USA]] poliitikute poolt ning väitis, et &quot;mingit tagasiteed kodanliku Eesti Vabariigi juurde ei ole ega saagi olla&quot;.
*Hiljem samal aastal oli tal oma osa Eesti NSV [[suveräänsusdeklaratsioon]]i ettevalmistamisel ja vastuvõtmisel ([[16. november]] 1988) ning ta kogus mujal maailmas tuntust selle deklaratsiooni kaitsjana konfliktis Nõukogude Liidu keskvõimudega.
*[[1990]]. aasta märtsis sai Arnold Rüütel uue, varasematest oluliselt vabamate valimiste tulemusena moodustunud Eesti NSV Ülemnõukogu koosseisu liikmeks ning seejärel valis Ülemnõukogu oma esimesel istungil ta oma esimeheks. Rüütli kaastegevusel võttis Ülemnõukogu vastu otsuse &quot;[[Eesti riiklikust staatusest]]&quot;, milles deklareeriti NSV Liidu riigivõimu ebaseaduslikkust Eestis selle kehtestamise momendist alates ja kuulutati välja [[üleminekuperiood Eesti Vabariigi taastamiseks]].
*Arnold Rüütel oli Eesti Vabariigi Ülemnõukogu viimane esimees, kuni selle volituste lõppemiseni ja vastvalitud Riigikogu ametisse astumiseni oktoobris [[1992]].
*[[12. mai]]l [[1990]] loodi Arnold Rüütli algatusel [[Tallinn]]as [[Balti Riikide Nõukogu]], mis iseseisvusvõitluse seisukohalt etendas olulist osa Balti riikide ühisrinde loomisel.
*[[20. august]]il 1991 võttis Eesti Vabariigi Ülemnõukogu vastu &quot;[[Otsus Eesti riiklikust iseseisvusest|Otsuse Eesti riiklikust iseseisvusest]]&quot;
*[[17. september|17. septembril]] [[1991]] võeti Eesti Vabariik vastu [[ÜRO]] täieõiguslikuks liikmeks. Eestis veretult kulgenud pingeline võitlus iseseisvuse eest oli kandnud vilja. Arnold Rüütel oli nendel aastatel Eesti riigijuht ja etendas olulist osa rahva ja poliitiliste jõudude koondamisel ühise eesmärgi nimel.
*[[1991]]. aastal esines Arnold Rüütel Eesti riigijuhina [[ÜRO Peaassamblee]]l. [[1992]] tegi ta ettekande [[Rio de Janeiro]]s ÜRO keskkonnakonverentsil.
*1991–1992 oli Arnold Rüütel Eesti Vabariigi uut põhiseadust koostanud [[Põhiseaduslik Assamblee|Põhiseadusliku Assamblee]] liige.
*[[1992]] kandideeris ta Eesti Vabariigi presidendi ametikohale, kogudes esimeses voorus 43% valijate häältest.
*[[1995]]. aastal valiti ta rekordarvu häältega Riigikogu liikmeks, seejärel Riigikogu aseesimeheks.
*[[1994]]–[[2000]] oli Arnold Rüütel Eesti ühe suurema liikmeskonnaga partei, paremtsentristliku [[Maarahva Erakond|Maarahva Erakonna]] esimees. [[1999]]. aastast kannab partei nimetust [[Eestimaa Rahvaliit]].
*[[1995]] valiti Arnold Rüütel Riigikogu [[Balti Assamblee]] delegatsiooni juhiks ja Balti Assamblee Presiidiumi esimeheks vaheaegadega kuni aastani 1999.
*[[21. september|21. septembril]] [[2001]] valiti Arnold Rüütel [[valijameeste kogu]] poolt Eesti Vabariigi presidendiks.
*Vabariigi Presidendi ametisse pühitsemise tseremoonia toimus Toompea lossis [[8. oktoober|8. oktoobril]] [[2001]].
*[[14. august]]il [[2006]] esines Arnold Rüütel [[Eesti Keskerakond|Eesti Keskerakonna]] erakorralise volikogu ees ning vastas küsimustele. Ta andis nõusoleku kandideerida valijameeste kogus teiseks ametiajaks Eesti Vabariigi presidendiks. Volikogu valis 94 häälega erakonna presidendikandidaadiks Arnold Rüütli. [[Ene Ergma]] sai kolm ja [[Toomas Hendrik Ilves]] kaks häält.
*[[23. september|23. septembril]] [[2006]] valimiskogus Eesti Vabariigi presidendiks kandideerinud Arnold Rüütel kogus 162 häält Toomas Hendrik Ilvese 174 hääle vastu ega osutunud seega valituks.
*[[9. oktoober|9. oktoobril]] [[2006]] andis ta oma volitused presidendina üle [[Toomas Hendrik Ilves]]ele.
*[[28. märts]]il [[2007]] kiitis [[Eestimaa Rahvaliit|Eestimaa Rahvaliidu]] juhatus heaks tema avalduse taasliituda erakonnaga ja nimetas ta ühtlasi erakonna auesimeheks. Seda ametit pidas ta ka aastatel 2000–2001. Auesimeheks jäi Rüütel ka pärast Rahvaliidu liitumist [[Eesti Rahvuslik Liikumine|Eesti Rahvusliku Liikumisega]], mille käigus kujunes parteist [[Eesti Konservatiivne Rahvaerakond]]&lt;ref&gt;[http://uudised.err.ee/v/eesti/a072ff38-b9d5-4828-80d2-1a0f02c77328 &quot;EKRE auesimees Rüütel: Madisoni ümber tekitati probleem kunstlikult&quot;] ERR, 04.03,2015&lt;/ref&gt;.

==Ühiskondlik tegevus==
[[Image:Allkirjad.jpg|pisi|Arnold Rüütel&lt;br&gt;&lt;small&gt;Foto: Presidendi Kantselei arhiiv/[http://www.president.ee/img/pilt_albumis.php?gid=69578&amp;width=500&amp;q=90]&lt;/small&gt;]]
[[Pilt:Kirjutab.jpg|pisi|Arnold Rüütel 2005. aastal]]
*[[1981]]–[[1988]] [[Eesti Looduskaitse Selts]]i esimees; [[1989]] Eesti Looduskaitse Seltsi auliige
*[[1989]]–[[2002]] [[B.G. Forseliuse Selts]]i esimees; [[2002]] B.G. Forseliuse Seltsi auesimees
*[[1993]] asutas [[Rahvusliku Arengu ja Koostöö Instituut|Rahvusliku Arengu ja Koostöö Instituudi]]
*[[1993]]–[[2001]] ülemaailmse [[Roheline Rist|Rohelise Risti]] Eesti rahvusliku organisatsiooni president
*[[1993]]–[[2001]] liikumise [[Hoia Eesti Merd]] esimees; [[2002]] &quot;Hoia Eesti Merd&quot; liikumise auesimees
* [[1994]] [[20. Augusti Klubi]] liige
* [[1999]] MTÜ [[Konstantin Pätsi Muuseum]] liige
* [[2002]] Akadeemilise Põllumajanduse Seltsi auliige
* [[2002]] Raoul Wallenbergi Sihtasutuse auliige
* [[2002]] [[Tallinna Botaanikaaia Sõprade Selts]]i liige

==Teadustegevus==
[[Eesti Põllumajandusakadeemia]] [[rektor]]ina töötades tegeles Rüütel intensiivselt [[teadustöö]]ga. Ta on uurinud piimakarja [[suurfarm]]ide tehnoloogiat ja ökonoomikat.

Riigijuhtimisega paralleelselt jätkas Arnold Rüütel teadustööd, kaitstes [[1991]]. aastal põllumajandusdoktori kraadi. Ta on [[USA]] [[Bentley College]]'i audoktor, Eesti Põllumajandusülikooli [[emeriitprofessor]], [[Helsingi Ülikool]]i audoktor, [[Ukraina Põllumajandusteaduste Akadeemia]] välisliige, [[Napoli II ülikool]]i audoktor, Kasahstani L. N. Gumiljovi nimelise Euraasia Riikliku Ülikooli audoktor ja [[Ungari Püha Istvani Ülikool]]i audoktor.

Tema sulest on Eestis ja välismaal ilmunud üle saja teadusliku töö.

[[1991]]. aastal esines Arnold Rüütel Eesti riigijuhina [[ÜRO Peaassamblee]]l. 1992 tegi ta ettekande [[Rio de Janeiro]]s [[ÜRO]] keskkonnakonverentsil. See konverents pani kogu maailmas aluse loodushoiu uuele etapile.

==Tunnustused==
[[Pilt:Ilves ja Rüütel.jpg|pisi|[[Toomas Hendrik Ilves]] ja Arnold Rüütel 2011. aastal.]]
* [[1976]] [[Eesti NSV teeneline põllumajandustöötaja]]
* [[Bentley College]]'i (USA) audoktor – 1991
* Eesti Põllumajandusülikooli [[audoktor]] – 1991
* Eesti Põllumajandusülikooli [[emeriitprofessor]] – 1993
* [[Akadeemilise Põllumajanduse Selts]]i auliige – 2002
* [[Helsingi Ülikool]]i (Soome) audoktor – 2002
* [[Ukraina Rahvuslik Põllumajandusülikool|Ukraina Rahvusliku Põllumajandusülikooli]] audoktor – 2002
* Ülemaailmse [[Rotary]] liikumise teenetemärk – 2002
* Rahvusvahelise Sõjaväespordi Komitee ordeni Suurpael 2002
* [[Andres Bello]] mälestusmedal nr 1 – 2002
* [[Napoli II ülikool]]i audoktor – 2002
* [[Ukraina Põllumajandusteaduste Akadeemia]] välisliige, akadeemik – 2002
* [[Kaitseliidu Valgeristi I järgu teenetemärk]] – 2003
* [[Ungari Püha Istváni Ülikool]]i audoktor – 2004
* [[Kasahstan]]i L. N. Gumiljovi nimelise Euraasia Riikliku Ülikooli audoktor – 2004
* Jerevani Riikliku Ülikooli audoktor – 2004
* Ülemaailmse Rotary liikumise aumärk – 2005
* [[Läti]] Põllumajandusülikooli audoktor – 2005
* [[Jõgevamaa Vapimärk]] – 2006
* [[Aasta eurooplane]] – 2007

==Teenetemärgid==
===Eesti Vabariik===
* [[Maarjamaa Risti teenetemärk|Maarjamaa Risti ketiklassi teenetemärk]] 2001
* [[Riigivapi teenetemärk|Riigivapi ketiklassi teenetemärk]] 2008

===Välisriigid===
* [[Soome]] [[Soome Valge Roosi Rüütelkond|Valge Roosi Rüütelkonna]] Suurrist ketiga 2001
* [[Poola]] Vabariigi [[Valge Kotka orden]]i Suurrist 2002
* [[Norra]] Kuningriigi Püha Olafi ordeni Suurrist 2002
* [[Ungari]] Vabariigi Teeneteordeni Suurrist 2002
* [[Luksemburg]]i [[Adolph de Nassau]] ordeni Suurrist 2003
* [[Portugal]]i Prints [[Dom Henrique]]'i ordeni suurkett 2003
* [[Malta]] Vabariigi Teeneteordeni suurkett 2003
* [[Rumeenia]] Rahvuslik Teeneteorden ketiga 2003
* [[Bulgaaria]] [[Stara planina orden|Stara Planina Suurorden]] 2003
* [[Vene]] [[Vene Õigeusu Kirik|Õigeusu Kirik]]u Püha Sergi Radonezski orden 2003
* [[Küpros]]e Vabariigi Makarios III ordeni suurkett 2004
* [[Itaalia]] Vabariigi Teeneteordeni Suure Risti kett 2004
* [[Island]]i Vabariigi Hauka orden 2004
* [[Leedu]] Vabariigi Vytautas Suure ordeni kett 2004
* [[Slovakkia]] Vabariigi Valge Topeltristi esimese klassi orden 2005
* [[Läti]] [[Kolme Tähe orden]]i Komandöri Suurrist 2005

===NSV Liit===
* [[1964]] orden „[[Austuse märk]]”
* [[1971]] [[Lenini orden]]
* [[1981]] [[Rahvaste Sõpruse orden]]

== Isiklikku ==
[[Pilt:Vabariigi President Arnold Rüütel ja proua Ingrid Rüütel.jpg|pisi|Ingrid ja Arnold Rüütel 10. mail 2003, presidendi 75. sünnipäeval]]
[[Pilt:Arnold and Ingrid Rüütel - Laulupidu 2009.jpg|thumb|Ingrid ja Arnold Rüütel 2009. aasta [[XXV üldlaulupidu|üldlaulupeol]]]]
Arnold Rüütel abiellus Ingrid Ruusiga [[1959]]. aastal. Proua [[Ingrid Rüütel]] on [[humanitaarteaduste doktor]] ning rahvusvaheliselt tuntud [[folklorist]] ja [[Baltica (folklooriassotsiatsioon)|folklooriassotsiatsiooni Baltica]] president. Peres on tütred Maris ([[1958]]) ja Anneli ([[1965]]) ning kuus lapselast.

== Tsitaate ==
* &quot;Eesti areng on kreenis keskuste poole, nüüd tuleks seda tasakaalustada.&quot; (Arnold Rüütli kõne Riigikogus presidendiks vannutamisel, esmaspäeval 8. oktoobril 2001.)&lt;ref&gt;[http://www.riigikogu.ee/?op=steno&amp;stcommand=stenogramm&amp;date=1002546000&amp;pkpkaupa=1&amp;paevakord=2000008110 IX RIIGIKOGU STENOGRAMM. VI ISTUNGJÄRK] 8. oktoober 2001&lt;/ref&gt;

* &quot;Oleme jõudnud ajastusse, mil inimesed lendavad suurtel kiirustel ja hulgakaupa.&quot;&lt;ref&gt;[http://www.delfi.ee/news/paevauudised/arvamus/eesti-poliitikute-paremaid-motteapse-likviidsuse-likvideerimisest-meeltesegaduseni?id=65942604 &quot;Eesti poliitikute paremaid mõtteapse likviidsuse likvideerimisest meeltesegaduseni&quot;] Delfi, 9. aprill 2013&lt;/ref&gt;

==Vaata ka==
*[[Arnold Rüütli publikatsioonide loend]]
*[[Kadriorgia]]
*[[1992. aasta Eesti presidendivalimised]]
*[[1996. aasta Eesti presidendivalimised]]
*[[Eesti Vabariigi President Arnold Rüütel]]

== Viited ==
{{viited}}

== Välislingid ==
{{commonskat|Arnold Rüütel}}
{{vikitsitaat}}
*[http://vana.www.postimees.ee/index.html?op=lugu&amp;rubriik=49&amp;id=33287&amp;number=307 &quot;Arnold Rüütel sai Eesti uueks presidendiks&quot;] Postimees, 21. september 2001
*Argo Ideon: [http://vana.www.postimees.ee/index.html?op=lugu&amp;rubriik=49&amp;id=33348&amp;number=308 &quot;Rüütel: sõna «kommunism» on minu puhul ülearune&quot;] Postimees, 22. september 2001
*[http://vana.www.postimees.ee/index.html?op=lugu&amp;rubriik=49&amp;id=33349&amp;number=308 &quot;Erakonnad lubavad Rüütli omaks võtta&quot;] Postimees, 22. september 2001
*[http://vana.www.postimees.ee/index.html?op=lugu&amp;rubriik=49&amp;id=35101&amp;number=322 &quot;Uus ja vana president&quot;] Postimees, 9. oktoober 2001
*Illar Mõttus: [http://www.president.ee/et/ametitegevus/intervjuud.php?gid=10919 &quot;President toetub teadlastele&quot;] Virumaa Teataja, 9. oktoober 2001
*Urmas Klaas: [http://www.president.ee/et/ametitegevus/intervjuud.php?gid=11988 &quot;Rüütel: võõrandumisest päästab poliitikute häbitunde taastamine&quot;] Postimees, 16. november 2001
*[http://paber.ekspress.ee/viewdoc/0AA4550302D98A33C2256FAC002F9F34 &quot;Kuidas Arnold Rüütli pilt ENEst välja jäi&quot;] Eesti Ekspress, 21. veebruar 2005
* Allar Viivik: [http://www.sloleht.ee/index.aspx?r=2&amp;d=16.11.02&amp;id=131272 &quot;Suveräänsusdeklaratsioon sündis presidendi korteris&quot;]
* {{EestiPostmark|1595}}
*[http://eestileht.kolhoos.ee/stories/storyReader$884 &quot;Uus raamat: Tagasiteel tulevikku. August ´91&quot;]
* [http://vpb.nlib.ee/Ryytel/ Arnold Rüütli bibliograafia Eesti Rahvusraamatukogu Vabariigi Presidendi bibliograafia andmebaasis]
* [http://vp2001-2006.president.ee/et/president/ Arnold Rüütel Eesti Vabariigi Presidendi kodulehel]
* [[Mait Raun]]: [http://iseseisvus.kongress.ee/index1304.html?a=page&amp;page=perioodika&amp;subpage=3f618228d4f7b6594f7dc &quot;Arnold Rüütli neli nägu&quot;]
* [[Alo Lõhmus]]: [http://www.delfi.ee/news/paevauudised/eesti/ruutel-kasutas-kgb-desintegraatori-kallale.d?id=13728096 &quot;Rüütel käsutas KGB Desintegraatori kallale&quot;], 29. august 2006
* [[Aarne Ruben]]: [http://archive.is/R28t8 &quot;Kui asju juhtis raudteemees&quot;] [[Maaleht]], 14.september 2006
* Peeter Järvelaid. Presidendi institutsioon Eesti kultuuris. – Pärnu Postimees, 2014, 30. aprill, lk. 19.

{{algus}}
{{eelnev-järgnev | eelnev=[[Lennart Meri]] | nimi=[[Eesti president]] | aeg=[[2001]]–[[2006]] | järgnev=[[Toomas Hendrik Ilves]]}}
{{eelnev-järgnev|eelnev=[[Johannes Käbin]]|nimi=[[Eesti NSV Ülemnõukogu Presiidiumi esimees]]|aeg=[[1983]]–[[1990]]|järgnev=Institutsioon asendus &lt;br/&gt;[[Eesti Vabariigi Ülemnõukogu]]ga}}
{{eelnev-järgnev|eelnev=Institutsioon loodi &lt;br/&gt;Eesti NSV Ülemnõukogu Presiidiumist|nimi=[[Eesti Vabariigi Ülemnõukogu esimees]]|aeg=[[1990]]–[[1992]]|järgnev=Institutsioon lakkas olemast}}
{{lõpp}}

{{Eestipresident}}

{{JÄRJESTA:Rüütel, Arnold}}
[[Kategooria:Eesti presidendid]]
[[Kategooria:Eesti kommunistid]]
[[Kategooria:Eesti Vabariigi Ülemnõukogu liikmed]]
[[Kategooria:VIII Riigikogu liikmed]]
[[Kategooria:IX Riigikogu liikmed]]
[[Kategooria:Eesti põllumajandusteadlased]]
[[Kategooria:Eesti Maaülikooli rektorid]]
[[Kategooria:Eesti Maaülikooli audoktorid]]
[[Kategooria:Helsingi Ülikooli audoktorid]]
[[Kategooria:Kaitseliidu Vanematekogu liikmed]]
[[Kategooria:Kaitseliidu Tallinna maleva liikmed]]
[[Kategooria:Riigivapi ketiklassi teenetemärgi kavalerid]]
[[Kategooria:Maarjamaa Risti ketiklassi teenetemärgi kavalerid]]
[[Kategooria:Kolme Tähe ordeni kavalerid]]
[[Kategooria:Eesti Maaülikooli vilistlased]]
[[Kategooria:Rahvaliidu poliitikud]]
[[Kategooria:Eesti Konservatiivse Rahvaerakonna poliitikud]]
[[Kategooria:Tartu aukodanikud]]
[[Kategooria:Sündinud 1928]]"""

    print(infoBoxParser(ar))