""" Test detecting parts of text that should be ignored by the syntactic analyser;
"""

from estnltk.text import Text
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger

def test_ignore_content_in_parenthesis_1():
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        # Pattern: parenthesis_1to3
        # Inputs from Koondkorpus:
        { 'text': 'Eesti judokate võistlus jäi laupäeval lühikeseks , nii Joel Rothberg ( -66 kg ) kui ka Renee Villemson ( -73 kg ) võidurõõmu maitsta ei saanud .', \
          'expected_ignore_texts': ['( -66 kg )', '( -73 kg )'] }, \
        { 'text': 'Vladimir Grill ( M 66 kg ) , Joel Rothberg ( M 73 kg ) , Rasmus Toompere ( M 81 kg ) ja Sander Maripuu ( M 90 kg ).', \
          'expected_ignore_texts': ['( M 66 kg )', '( M 73 kg )', '( M 81 kg )', '( M 90 kg )'] }, \
        { 'text': 'B-grupi MM-il kaotas Eesti teisipäeval Kasahstanile 3 : 8 ( 0 : 1 , 1 : 1 , 2 : 5 ) .', \
          'expected_ignore_texts': ['( 0 : 1 , 1 : 1 , 2 : 5 )'] }, \
        { 'text': 'Meeste meistriliiga eilsed tulemused : Rivaal - Pärnu 1 : 3 ( 21 , -14 , -21 , -12 ) , Audentes - Volle 3 : 1 ( 15 , -25 , 17 , 22 ) .', \
          'expected_ignore_texts': ['( 21 , -14 , -21 , -12 )', '( 15 , -25 , 17 , 22 )'] }, \
        { 'text': 'Suursoosikutele järgnevad AC Milan ( 7 : 1 ) , Manchester United ( 8 : 1 ) , Londoni Arsenal ja Müncheni Bayern ( 9 : 1 ) ning Torino Juventus ( 10 : 1 ) .', \
          'expected_ignore_texts': ['( 7 : 1 )', '( 8 : 1 )', '( 9 : 1 )', '( 10 : 1 )'] }, \
        { 'text': 'Oli selline jada (x 1 , x 2 , ... , K , ... , x n) .', \
          'expected_ignore_texts': ['(x 1 , x 2 , ... , K , ... , x n)'] }, \
        # Inputs from etTenTen:
        { 'text': 'Nädala kolm parimat olid seekord kasutajad dieedipaevik (2,3 kg), Elfie (1,6 kg) ja RiinRiin (1,5 kg).', \
          'expected_ignore_texts': ['(2,3 kg)', '(1,6 kg)', '(1,5 kg)'] }, \
        { 'text': '5-liitrisest koolast (ehk 250 ml), saad 105 kcal, mis moodustab 5% päevasest energiavajadusest (3).', \
          'expected_ignore_texts': ['(ehk 250 ml)', '(3)'] }, \
        { 'text': 'Kõige vihmasemad kuud on juuli (68 mm) ja juuni (60 mm), kõige kuivemad on jaanuar (22 mm) ja veebruar (23 mm).', \
          'expected_ignore_texts': ['(68 mm)', '(60 mm)', '(22 mm)', '(23 mm)'] }, \
        # Pattern: parenthesis_1to4
        # Koondkorpus:
        { 'text': 'Kaks lavatudengite diplomilavastust : Komissarovi " Kolm õde " XIII lennuga ( 1988 ) ning Pedajase variant XVI lennuga ( 1994 ) .', \
          'expected_ignore_texts': ['( 1988 )', '( 1994 )'] }, \
        # etTenTen:
        { 'text': 'Kohtuministeeriumi asjadevalitseja (1918), Pariisi (1919) ja Tartu (1920) rahukonverentsidel Eesti delegatsiooni sekretär.', \
          'expected_ignore_texts': ['(1918)', '(1919)', '(1920)'] }, \
 
        # Pattern: parenthesis_title_words
        { 'text': 'Neidude 5 km klassikat võitis Lina Andersson ( Rootsi ) Pirjo Mannineni ( Soome ) ja Karin Holmbergi ( Rootsi ) ees .', \
          'expected_ignore_texts': ['( Rootsi )', '( Soome )', '( Rootsi )'] }, \
        # Pattern: parenthesis_ordinal_numbers
        { 'text': 'Naiste turniirid toimuvad Jakartas ja Budapestis ( 26. aprillini ) .', \
          'expected_ignore_texts': ['( 26. aprillini )'] }, \
        { 'text': '1930ndate algul avaldati romaani uus väljaanne ( 4. trükk ) KT XVI ande teise trüki kujul .', \
          'expected_ignore_texts': ['( 4. trükk )'] }, \
        # Pattern: brackets
        { 'text': 'Nurksulgudes tuuakse materjali viitekirje järjekorranumber kirjanduse loetelus ja leheküljed , nt [9: 5] või [9 lk 5], aga internetimaterjalil lihtsalt viitekirje, nt [7]', \
          'expected_ignore_texts': ['[9: 5]', '[9 lk 5]', '[7]'] }, \
        { 'text': 'Kohustuslik päritolumärgistus on välja töötatud vertikaalsete lähenemisviiside alusel , näiteks mee , [ 14 ] puu- ja köögiviljade , [ 15 ] kala , [ 16 ] veiseliha ja veiselihatoodete [ 17 ] ja oliiviõli [ 18 ] kohta .', \
          'expected_ignore_texts': ['[ 14 ]', '[ 15 ]', '[ 16 ]', '[ 17 ]', '[ 18 ]'] }, \
        { 'text': 'Lepitav , harmooniat taaskinnitav finaal kutsub esile katarsise [Hegel1976:548-551].', \
          'expected_ignore_texts': ['[Hegel1976:548-551]'] }, \
        # Negative: do not extract <ignore> content inside email address
        { 'text': 'saada meil meie klubi esimehele xxxtonisxxx[at]gmail.com', \
          'expected_ignore_texts': [] }, \
        
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']


def test_ignore_content_in_parenthesis_2():
    # Testing a reimplementation of PATT_12 ( from https://github.com/EstSyntax/preprocessing-module  )
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        # Pattern: parenthesis_num_range
        { 'text': 'Mis kellani on teie koolis pikkpäev ? Meie koolis tuleb 12-17(1-7 klass).', \
          'expected_ignore_texts': ['(1-7 klass)'] }, \
        { 'text': 'Täna 100 aastat tagasi sündis lavastaja Leo Kalmet ( 2.03.1900 -16.09.1975 ) .', \
          'expected_ignore_texts': ['( 2.03.1900 -16.09.1975 )'] }, \
        { 'text': 'Tema atmosfäär ja arvatavasti ka sisemus koosneb peamiselt vesinikust (mahu järgi 87-90%) ja heeliumist (10-13%).', \
          'expected_ignore_texts': ['(mahu järgi 87-90%)', '(10-13%)'] }, 
        { 'text': 'Tallinna ( 21.-22. mai ) , Haapsalu ( 2.-3. juuli ) ja Liivimaa ( 30.-31. juuli ) rallidel on vähemalt see probleem lahendatud .', \
          'expected_ignore_texts': ['( 21.-22. mai )', '( 2.-3. juuli )', '( 30.-31. juuli )'] }, \
        { 'text': 'Esmakordselt on üleval legendaarse itaallasest autodisaineri Ettore Bugatti ( 1881-1947 ) ning tema isa , mööbli- ja ehtekunstnik Carlo ( 1856-1940 ) , ja noorema venna skulptor Rembrandti ( 1884-1916 ) 7. märtsini kestev retrospektiiv .', \
          'expected_ignore_texts': ['( 1881-1947 )', '( 1856-1940 )', '( 1884-1916 )'] }, \

        # Pattern: parenthesis_datetime
        { 'text': '(22.08.2010 18:11:32)\nLisasin püreestatud supile veel punased läätsed ja mõned herned.', \
          'expected_ignore_texts': ['(22.08.2010 18:11:32)'] }, \
        { 'text': 'Kommentaarid:\n(1.11.2012 20:49:53)\nVäga maitsev (kuigi veis oli vist väga vana ja jäi kohati sooniline ...)!', \
          'expected_ignore_texts': ['(1.11.2012 20:49:53)'] }, \
        { 'text': 'Postitas isakene (Postitatud Teisipäev Nov 13, 2012 0:20) Mythbusteri vennad on vahel ikka parajad lambad.', \
          'expected_ignore_texts': ['(Postitatud Teisipäev Nov 13, 2012 0:20)'] }, \
        { 'text': 'Viimati muutis seda surramurra (Laup Aug 20 2011, 12:04). Kokku muudetud 1 kord\n', \
          'expected_ignore_texts': ['(Laup Aug 20 2011, 12:04)'] }, \

        # Pattern: parenthesis_ref
        { 'text': 'Lambiviited: see ( PM 3.02.1998 ) või too ( “ Kanuu ” , 1982 ) või too ( Looming , 1999 , nr.6 )', \
          'expected_ignore_texts': ['( PM 3.02.1998 )', '( “ Kanuu ” , 1982 )', '( Looming , 1999 , nr.6 )'] }, \
        { 'text': 'Tutvustamisele tulevad Jan Kausi romaan “Koju” (Tuum 2012) ning Ülo Pikkovi romaan “Vana prints” (Varrak 2012).', \
          'expected_ignore_texts': ['(Tuum 2012)', '(Varrak 2012)'] }, \
        { 'text': 'Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt (Priit Pullerits «Džiibi kaitseks», PM 30.07.2010).', \
          'expected_ignore_texts': ['(Priit Pullerits «Džiibi kaitseks», PM 30.07.2010)'] }, \
        { 'text': 'Vähemalt ühes järgmistest allikatest: 1) Paul Ariste "Maailma keeled" (I, 1967; II, 1969; 2. trükk 1972); 2) "Eesti nõukogude entsüklopeedia" (1968-1978);', \
          'expected_ignore_texts': ['(I, 1967; II, 1969; 2. trükk 1972)', '(1968-1978)'] }, \
        { 'text': 'See otsus avaldati esimest korda Riigi Teatajas 27. detsembril 2002 (RT I 2002, 107, 637) ja teist korda 5. septembril 2003 (RT I 2003, 60).', \
          'expected_ignore_texts': ['(RT I 2002, 107, 637)', '(RT I 2003, 60)'] }, \
        { 'text': 'See otsus avaldati esimest korda Riigi Teatajas 27. detsembril 2002 (RT I 2002, 107, 637) ja teist korda 5. septembril 2003 (RT I 2003, 60).', \
          'expected_ignore_texts': ['(RT I 2002, 107, 637)', '(RT I 2003, 60)'] }, \
        { 'text': '... rahvaluuleteaduse vaatenurgast tehtud uurimused Ameerika viipenimede kohta (Carmel 1996; Supalla 1992; Rutherford 1987; Klima, Bellugi 1979), samuti tutvusin ülevaatega Uus-Meremaa (McKee, McKee 2000), Prantsusmaa ( Langue des Signes. Votre Prénom ) ja Palestiina kurtide nimemärkidest (Strauss-Samaneh 2001).', \
          'expected_ignore_texts': ['(Carmel 1996; Supalla 1992; Rutherford 1987; Klima, Bellugi 1979)', '(McKee, McKee 2000)', '(Strauss-Samaneh 2001)'] }, \

        # Pattern: parenthesis_ref_paragraph     
        { 'text': 'Kasutamise hüvitamise eeskirjad ( § 987 , 988 , 993 ) on leges speciales § 951 juurde .', \
          'expected_ignore_texts': ['( § 987 , 988 , 993 )'] }, \
        { 'text': '... alates hõljuvusest peab andma välja asja kasutamisest saadud tulud ( §-d 987 , 990 ) .', \
          'expected_ignore_texts': ['( §-d 987 , 990 )'] }, \
        { 'text': '... kõiki alkohoolseid jooke, mille müük EV territooriumil lubatud (§2, 4, 6, 7, 11, 13).', \
          'expected_ignore_texts': ['(§2, 4, 6, 7, 11, 13)'] }, \
        { 'text': 'Teooria järgi saab järglusõigust arestida ainult õiguse arestimise teel ( ZPO § 857 I , 829 ) .', \
          'expected_ignore_texts': ['( ZPO § 857 I , 829 )'] }, \
          
        # Pattern: parenthesis_num
        { 'text': 'Sõidu võitis Itaalia (6.00,18) Tsehhi (6.00,79) ja Prantsusmaa ees (6.01,38).', \
          'expected_ignore_texts': ['(6.00,18)', '(6.00,79)', '(6.01,38)'] }, \
        { 'text': 'Kõige paremini läksid korda 100 m ( 11,29 ) , 400 m ( 50,18 ) ja kaugushüpe ( 6.73 ) .', \
          'expected_ignore_texts': ['( 11,29 )', '( 50,18 )', '( 6.73 )'] }, \
        { 'text': 'Talle järgnes täna kaks sakslannat, teiseks tuli Lisa Neumüller (+4,45) ja kolmandaks Sina Frei (+5,77).', \
          'expected_ignore_texts': ['(+4,45)', '(+5,77)'] }, \
        { 'text': 'Klubi sai kuus korda Inglismaa meistriks (1976, 1977, 1979, 1980, 1982, 1983).', \
          'expected_ignore_texts': ['(1976, 1977, 1979, 1980, 1982, 1983)'] }, \
        { 'text': 'Jaapan võitis Hiina 3:2 (26, -23, 23, -23, 16) ja USA Dominikaani 3:0 (14, 21, 22).', \
          'expected_ignore_texts': ['(26, -23, 23, -23, 16)', '(14, 21, 22)'] }, \
        { 'text': '2. Sebastien Amiez ( Prantsusmaa ) 1.51 , 75 ( 54,71 /57 , 04 ) , 3. Alberto Tomba ( Itaalia ) 1.52 , 14 ( 56,21 /55 , 93 )', \
          'expected_ignore_texts': ['( Prantsusmaa )', '( 54,71 /57 , 04 )', '( Itaalia )', '( 56,21 /55 , 93 )'] }, \
        { 'text': 'Samas voorus testiti veel Peugeot 1007 ( 5/3/2 ) , Renault Clio III ja 3. seeria BMW ( 5/4/1 ) , Suzuki Swifti ning Honda FR-V ( 4/3/3 ) , Fiat Stilo ( 4/4/1 ) , Citroen C1 ( 4/3/2 ) , Smart Forfouri ( 4/2/1 ) ja Dacia Logani ( 3/3/1 ) ohutust .', \
          'expected_ignore_texts': ['( 5/3/2 )', '( 5/4/1 )', '( 4/3/3 )', '( 4/4/1 )', '( 4/3/2 )', '( 4/2/1 )', '( 3/3/1 )'] }, \
        { 'text': 'TABLOO\nRASKEKAAL\nK : Timur Taimazov UKR 430,0 ( 195,0 + 235,0\n)\nH : Sergei Sõrtsov RUS 420,0 ( 195,0 + 225,0 )\n', \
          'expected_ignore_texts': ['( 195,0 + 235,0\n)', '( 195,0 + 225,0 )'] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']
    
