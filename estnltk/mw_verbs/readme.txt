==================================
     Verb chain detector
==================================

=========================
  Usage example
=========================
    See the file '../usage_example_verb_chains1.py' for an example of how to use the 
   verb chain detector module.

=========================
  What do expect from 
  the output: examples
  from Tasak corpus
=========================
    In following, the verb chain examples extracted from The Balanced Corpus of Estonian
   (http://www.cl.ut.ee/korpused/grammatikakorpus/index.php?lang=et) are listed.
    
    Verb chains are grouped by the general patterns, more specifically, by the first words
   of the general patterns, and are sorted by the relative frequency. Additionally, one 
   example sentence is listed for each verb chain.
    Note that only chains with 'clear contexts' are listed, and chains with verbChain['otherVerbs']==True,
   are left out, because these chains are likely incomplete.
    
    ===========================
     olema-verb, POS polarity
    ===========================
       ole                             | 14.51%    Probleeme on palju ja raha <on> alati vähe .
       ole+verb                        | 4.55%     <Oleme> <jätkanud> Eesti Arstide Päevade traditsiooni .
       ole+nom/adv+verb                | 0.54%     Raamatukogu <on> <kavas> <liita> mõne teise teadusraamatukoguga .
       ole+ole                         | 0.34%     Ka Rootsi ühiskonna pöördumine Balti-sõbralikuks <on> <olnud> tähtsaks teguriks .
       ole+verb+verb                   | 0.31%     Esimesed kogemused näitavad , et see <on> <võimaldanud> oluliselt <vähendada> haigekassa kulutusi ravimite kompenseerimiseks .
       ole+verb+ole                    | 0.01%     Ta <oleks> <tahtnud> <olla> väikene palavikus laps , kelle eest ema hoolitseb .
       ole+verb+verb+&+verb            | 0.01%     Konjakid <olid> <aidanud> mul rahulikult <uinuda> <ja> ennast korralikult välja <magada> .
       ole+nom/adv+ole                 | <0.01%    Sellepärast <on> mul <õigus> ka natuke pahane <olla> .
       ole+verb+nom/adv+verb           | <0.01%    Poliitilise eliidi võõrandumine lihtvalijatest <on> <andnud> <alust> <kõnelda> mõnikord isegi " poliitilisest klassist " 346.
       ole+ole+nom/adv+verb            | <0.01%    Pärsia teekonda <oleks> <olnud> <vaja> <jätkata> ümber Aafrika ja sellega saadi hakkama alles 16. sajandil .
       ole+ole+verb                    | <0.01%    Kui juhtkond <oleks> <olnud> asjasse <segatud> , siis saaginuks ta oksa , mille peal ise istus .
       ole+verb+nom/adv+verb+&+verb    | <0.01%    Firma AltaVista <on> <saanud> <õiguse> <jälgida> kõiki olulisi võrguraadiojaamu <ning> <analüüsida> häälenäidiseid ja linke kõigile Interneti-lehtedele .
       ole+ole+ole                     | <0.01%    Ma teadsin küll , et see pusa <oleks> <olnud> <olemata> , kui ma poleks läbi mütsi oma pead süganud .
       ole+verb+verb+nom/adv+verb      | <0.01%    " Kas on võimalik , et kõrgused tekitasid teis hirmu seepärast , et teil <oleks> <võinud> <tekkida> <tahtmine> alla <hüpata> ? "
       ole+verb+nom/adv+ole            | <0.01%    Digitaalülikooli Konsortsium <on> <seadnud> <eesmärgiks> <olla> juhtiv keskus elektrooniliste õpikeskkondade arendamise ja rakendamise vallas Hollandi kõrghariduses .
       ole+verb+ole+nom/adv+verb       | <0.01%    See oli minu pidu ja minul <oleks> <pidanud> <olema> <õigus> ise endale külalisi <kutsuda> . "
       ole+ole+nom/adv+ole             | <0.01%    Side isaga nähtub ka napist stiilist – paljud patsiendid , kel <on> <olnud> <võimalus> isaga pikemalt tuttav <olla> , omandavad alateadlikult mingi osa temast .
    
    ================================
     non-olema verbs, POS polarity
    ================================
       verb                            | 47.09%    Üks tont <hulgub> mööda maailma S-L .
       verb+verb                       | 8.50%     E. Raudam <suutis> oma üksikutel välissõitudel <luua> viljakad kontaktid kolleegidega välismaal .
       verb+ole                        | 0.90%     Tsüsti ümber <võib> <olla> sekundaarne põletik .
       verb+verb+&+verb                | 0.33%     Isegi sellises olukorras <suutsid> poliitikud veel <keerutada> <ja> uskumatuid avaldusi <teha> .
       verb+nom/adv+verb               | 0.07%     Koos keeluga <anti> <luba> <avada> Balti rüütelkondadel kiires korras kohalik protestantlik ülikool kogu Vene riigi , eelkõige Eesti- , Liivi- ja Kuramaa rüütelkondade jaoks .
       verb+ole+nom/adv+verb           | 0.01%     Klassifikatsiooniskeemi alusel <peab> <olema> <võimalik> <hinnata> kvaliteeti nii üldistatud kui detailsel tasemel .
       verb+verb+nom/adv+verb          | <0.01%    <Tuleb> neile ainult <aega> <anda> selle mõttega <harjuda> .
       verb+nom/adv+verb+&+verb        | <0.01%    <Andkem> ka peaarhitektile <aega> atra <seada> <ja> veel täiendavaid lõikeid silme eest läbi <lasta> .
       verb+nom/adv+ole                | <0.01%    See <annab> sulle <vabaduse> <olla> kes iganes .
       verb+verb+verb                  | <0.01%    Jälle <sai> <magama> <mindud> , nii et meiki maha ei võtnud .
       verb+verb+ole                   | <0.01%    Ja kuidas Põiklik polnud siis teps vaadanud küsijale jõmmis pilgul otsa ega öelnud patentselt " Minister — mis <võiks> teil <teada> <olla> " — , vaid oli vaadanud hämmelduses lauale ja vastanud , nagu öeldakse , värahtavate ripsmete varjust : " Ametnik — "
       verb+nom/adv+verb+nom/adv+verb  | <0.01%    Abilinnapea <tegi> juba eelmise aasta lõpus <ettepaneku> <leida> linnaeelarvest <võimalusi> kainestusmaja <luua> .
    
    ================================
     ei/pole/ega/ära, NEG polarity
    ================================
       ei+verb                         | 4.72%     Ta <ei> <rõhutanud> kunagi oma autoriteeti või ülemuse positsiooni .
       ei+verb+verb                    | 1.70%     ( Kindlas kõneviisis ma seda lauset veel <kirjutada> <ei> <söanda> . )
       ei+ole                          | 0.96%     Kui ikterus puudub ja tegemist on idiopaatilise pankreatiidi kerge vormiga , <ei> <ole> ERKP tingimata vajalik .
       ei+ole+verb                     | 0.22%     MRT-uuringul ilmnes , et tuumor <ei> <ole> <kahjustanud> luu kasvuplaati .
       ei+verb+ole                     | 0.15%     Efektiivsus ja tasakaal võivad , kuid <ei> <pruugi> <olla> vastuolus .
       ei+ole+nom/adv+verb             | 0.06%     Vaimse stressi seost võimalike meditsiiniliste hilistagajärgedega <ei> <ole> <lihtne> <uurida> .
       ei+verb+verb+&+verb             | 0.03%     Õpilased <ei> <torma> neile etteantavat õppetükki <omandama> <ja> sellesse pimesi <uskuma> .
       ei+ole+verb+verb                | 0.02%     Ent Killu <ei> <oleks> <soovinud> <võtta> vanaema ees vastutust poisi käekäigu pärast , ning Simmo sõprade ja nende näkkidega tal klappi ei olnud tekkinud .
       ei+ole+ole                      | 0.02%     Samas <ei> <olnud> teadlikku keskkonnakaitset sel ajal loomulikult <olemas> .
       ei+verb+nom/adv+verb            | 0.01%     Ta <ei> <pea> <vajalikuks> isegi laulude sõnu <lugeda> .
       ei+ole+verb+ole                 | <0.01%    Ent Himmleri arvates nad <ei> <oleks> <pidanud> seda <olema> .
       ei+verb+ole+nom/adv+verb        | <0.01%    Küll aga <ei> <pruugi> igaühel <olla> <võimalust> uut garderoobi <soetada> .
       ei+ole+nom/adv+ole              | <0.01%    Ja <ei> <ole> <lihtne> <olla> jumala isa .
       ei+ole+verb+nom/adv+verb        | <0.01%    Ja ta ise <ei> <ole> ab-so-luut-selt <pidanud> <vajalikuks> mulle aru <anda> . . . !
       ei+verb+verb+nom/adv+verb       | <0.01%    <Ei> <sobi> ju minul <teha> <ettepanekut> uuesti kokku <saada> .
       ei+ole+ole+nom/adv+verb         | <0.01%    Pestitsiide <ei> <ole> <olnud> <vaja> <kasutada> .
       ei+ole+verb+verb+&+verb         | <0.01%    Äriühingu likvideerija <ei> <oleks> <tohtinud> töölepingut ühepoolselt <muuta> <ega> <lõpetada> .
       ei+verb+nom/adv+verb+&+verb     | <0.01%    Kuid see <ei> <anna> <õigust> kaalu <kallutada> <ja> kaussi kummuli <ajada> .
       ei+ole+verb+nom/adv+ole         | <0.01%    Enam ammu <ei> <olnud> ma <leidnud> <põhjust> ööd naise pärast üleval <olla> .
       ei+verb+verb+ole                | <0.01%    /---/ on seoses selle kohtuotsusega avaldanud arvamust , et kuna väljaspool kohtulikku arutamist toimuvatel eelläbirääkimistel <ei> <saa> <olla> konkreetsed teemad ( näiteks võimalik karistusmäär ) <keelatud> , siis ei ole välistatud , et /---/
       ei+verb+verb+verb               | <0.01%    <Ei> <saa> siis emale <süüa> <antud> , ” pahandab Aide rikka poja peale ja laseb Pillel pensionist kahe kuu lehetellimise raha maha võtta .
       ei+verb+nom/adv+ole             | <0.01%    Tihti <ei> <anna> ema lihtsalt <võimalust> isale <olla> isa .
       
       pole                            | 1.28%     Une hulga või kvaliteediga <pole> rahul 8-18% uuritutest .
       pole+verb                       | 0.41%     Kokkuvõttena leiab ta , et postmodernismi mõiste <pole> kirjanduskriitikas väga laialt <levinud> .
       pole+nom/adv+verb               | 0.12%     Vaevusteta naistel <pole> abi <vaja> <otsida> .
       pole+ole                        | 0.06%     Endine orduametnik Renner märkis samas peksukaristust ja nimetas , et kui seda <poleks> <olnud> , siis oleksid talupojad sakslased hukanud .
       pole+verb+verb                  | 0.03%     On olnud olukordi , kus vastutavat töötlejat <pole> <õnnestunud> isegi välja <selgitada> .
       pole+nom/adv+ole                | <0.01%    " Ma kardan , et tal <polnud> <aega> õnnelik <olla> . "
       pole+verb+ole                   | <0.01%    Seega <poleks> <saanud> juttugi <olla> mingite Rüütli sõlmitud kokkulepete edasiarendamisest .
       pole+ole+nom/adv+verb           | <0.01%    Tööasjadega on olnud väga kiire , <pole> <olnud> <aega> <mõelda> , mis minust edasi saab .
       pole+verb+verb+&+verb           | <0.01%    Komöödia muutus tragöödiaks , mida ma <polnud> <osanud> ette <näha> <ega> ära <hoida> .
       pole+ole+verb                   | <0.01%    Vald on hoonet pakkunud äriettevõtetele , kuid ka need <pole> <olnud> sellest <huvitatud> .
       pole+verb+nom/adv+verb          | <0.01%    Mees <polnud> <jätnud> mulle <võimalust> kuhugi sõna vahele <poetada> .
       pole+ole+ole                    | <0.01%    /---/ aga kunagi pole olnud sellist aega , et Hiinat ja hiina kultuuri <poleks> <olnud> <olemas> , /---/
       
       ega+verb                        | 0.14%     Ettepanekud põhjustasid rahva vastupanu <ega> <leidnud> rakendamist .
       ega+verb+verb                   | 0.05%     Ei taha <ega> <püüa> <vaielda> tõlgenduste ja tõlgendajatega .
       ega+ole                         | 0.03%     " Küllap ma siis oleksin ka kuulnud , <ega> see mingi tumm-mäng <ole> . "
       ega+ole+verb                    | 0.01%     <Ega> targad mehed muidu neid sõnu <oleks> <rääkinud> .
       ega+verb+ole                    | <0.01%    Ikka oled skeptiline <ega> <suuda> <olla> uskmatu ja tühi .
       ega+ole+verb+verb               | <0.01%    " Igaüks ajab oma rida <ega> <ole> <püüdnudki> milleski kokku <leppida> . "
       ega+ole+ole                     | <0.01%    <Ega> temast <ole> tõesti kusagil suurt juttu <olnud> .
       ega+verb+verb+&+verb            | <0.01%    " Hoidku küll ! " ehmus Neena <ega> <mõistnud> midagi <teha> <või> <öelda> .
       ega+verb+nom/adv+verb           | <0.01%    Too istus endiselt maas <ega> <teinud> <katsetki> <tõusta> .
       ega+ole+nom/adv+verb            | <0.01%    Ka loomalaut jäi pooltühjaks , <ega> emalgi <olnud> <kerge> lehmadest <loobuda> .
       ega+ole+verb+nom/adv+verb       | <0.01%    Viimanegi on lootnud oma oraatorlikele võimetele <ega> <ole> <pidanud> <vajalikuks> midagi kirja <panna> .
       ega+ole+verb+verb+&+verb        | <0.01%    " Anna andeks , aga ma olen siiski teadlane , mitte kohvikutante , <ega> <ole> <harjunud> <koguma> <või> <levitama> kuuldusi . "
       
       ära+verb                        | 0.12%     <Ärme> <kiirustame> , jõuame ka hiljem liituda .
       ära+verb+verb                   | 0.01%     Juba Kant kirjutas : <ärge> <laske> omale pähe <astuda> .
       ära+ole                         | <0.01%    Eeva polnud rahul ja hakkas Aadamat sakutama : " <Ära> <ole> nii vedel !
       ära+verb+verb+&+verb            | <0.01%    <Ärge> kunagi <püüdke> <halvustada> <või> <kritiseerida> kauba kvaliteeti .
       ära+ole+verb                    | <0.01%    <Ära> <ole> nii <hirmunud> .
       ära+verb+ole                    | <0.01%    <Ära> <püüa> <olla> kohtumõistja , sinu enda üle mõistetakse kohut . "

