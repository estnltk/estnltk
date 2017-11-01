""" Test detecting parts of text that should be ignored by the syntactic analyser;
"""

from estnltk.text import Text
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger

def test_ignore_content_in_parentheses_1():
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        # Pattern: parentheses_1to3
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
        # Pattern: parentheses_1to4
        # Koondkorpus:
        { 'text': 'Kaks lavatudengite diplomilavastust : Komissarovi " Kolm õde " XIII lennuga ( 1988 ) ning Pedajase variant XVI lennuga ( 1994 ) .', \
          'expected_ignore_texts': ['( 1988 )', '( 1994 )'] }, \
        # etTenTen:
        { 'text': 'Kohtuministeeriumi asjadevalitseja (1918), Pariisi (1919) ja Tartu (1920) rahukonverentsidel Eesti delegatsiooni sekretär.', \
          'expected_ignore_texts': ['(1918)', '(1919)', '(1920)'] }, \
 
        # Pattern: parentheses_title_words
        { 'text': 'Neidude 5 km klassikat võitis Lina Andersson ( Rootsi ) Pirjo Mannineni ( Soome ) ja Karin Holmbergi ( Rootsi ) ees .', \
          'expected_ignore_texts': ['( Rootsi )', '( Soome )', '( Rootsi )'] }, \
        # Pattern: parentheses_ordinal_numbers
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
        text.tag_layer(['words', 'sentences', 'paragraphs'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']


def test_ignore_content_in_parentheses_2():
    # Testing a reimplementation of PATT_12 ( from https://github.com/EstSyntax/preprocessing-module  )
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        # Pattern: parentheses_num_range
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
        # Pattern: parentheses_birthdeath_year
        { 'text': 'Sulgudes sünni/surmaaasta: A ( s.1978 ), B ( sünd. 1978 ) või C ( surnud 1978 ).', \
          'expected_ignore_texts': ['( s.1978 )', '( sünd. 1978 )', '( surnud 1978 )'] }, \

        # Pattern: parentheses_datetime
        { 'text': '(22.08.2010 18:11:32)\nLisasin püreestatud supile veel punased läätsed ja mõned herned.', \
          'expected_ignore_texts': ['(22.08.2010 18:11:32)'] }, \
        { 'text': 'Kommentaarid:\n(1.11.2012 20:49:53)\nVäga maitsev (kuigi veis oli vist väga vana ja jäi kohati sooniline ...)!', \
          'expected_ignore_texts': ['(1.11.2012 20:49:53)'] }, \
        { 'text': 'Postitas isakene (Postitatud Teisipäev Nov 13, 2012 0:20) Mythbusteri vennad on vahel ikka parajad lambad.', \
          'expected_ignore_texts': ['(Postitatud Teisipäev Nov 13, 2012 0:20)'] }, \
        { 'text': 'Viimati muutis seda surramurra (Laup Aug 20 2011, 12:04). Kokku muudetud 1 kord\n', \
          'expected_ignore_texts': ['(Laup Aug 20 2011, 12:04)'] }, \

        # Pattern: parentheses_ref
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
        # Pattern: parentheses_ref_quotes_num
        { 'text': 'Sulgudes ja jutumärkides viited: A ( “ Postimees ” , 12. märts ), B ("Preester , rabi ja blondiin", 2000), C ( “ Odysseuse tagasitulek kodumaale ” , 1641 ) ja D ( näiteks “ Administreeritud maastik ” , 1994 ).', \
          'expected_ignore_texts': ['( “ Postimees ” , 12. märts )', '("Preester , rabi ja blondiin", 2000)', '( “ Odysseuse tagasitulek kodumaale ” , 1641 )', '( näiteks “ Administreeritud maastik ” , 1994 )'] }, \
        { 'text': 'Sulgudes ja jutumärkides viited: A («Eesti naine peaks valima 11 aastat noorema mehe», PM 30.07.2010), B (Marju Lauristin «Ühtehoidmise meenutuspäevaks», EPL 22.08) ja C (ajakiri "Looming" nr 9, 1981).', \
          'expected_ignore_texts': ['(«Eesti naine peaks valima 11 aastat noorema mehe», PM 30.07.2010)', '(Marju Lauristin «Ühtehoidmise meenutuspäevaks», EPL 22.08)', '(ajakiri "Looming" nr 9, 1981)'] }, \
        # Pattern: parentheses_num_comma_word
        { 'text': 'Sulgudes komaga viited või mingid sporditulemused:  A ( New York , 1994 ), B ( PM , 25.05. ), C ( Šveits , +0.52 ), D ( Mitsubishi , +0.26 ) või E ( NY Islanders , 4+8 ).', \
          'expected_ignore_texts': ['( New York , 1994 )', '( PM , 25.05. )', '( Šveits , +0.52 )', '( Mitsubishi , +0.26 )', '( NY Islanders , 4+8 )'] }, \

        # Pattern: parentheses_ref_paragraph     
        { 'text': 'Kasutamise hüvitamise eeskirjad ( § 987 , 988 , 993 ) on leges speciales § 951 juurde .', \
          'expected_ignore_texts': ['( § 987 , 988 , 993 )'] }, \
        { 'text': '... alates hõljuvusest peab andma välja asja kasutamisest saadud tulud ( §-d 987 , 990 ) .', \
          'expected_ignore_texts': ['( §-d 987 , 990 )'] }, \
        { 'text': '... kõiki alkohoolseid jooke, mille müük EV territooriumil lubatud (§2, 4, 6, 7, 11, 13).', \
          'expected_ignore_texts': ['(§2, 4, 6, 7, 11, 13)'] }, \
        { 'text': 'Teooria järgi saab järglusõigust arestida ainult õiguse arestimise teel ( ZPO § 857 I , 829 ) .', \
          'expected_ignore_texts': ['( ZPO § 857 I , 829 )'] }, \
          
        # Pattern: parentheses_num
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
        { 'text': 'Samas voorus testiti veel Peugeot 1007 ( 5/3/2 ) , Renault Clio III ja 3. seeria BMW ( 5/4/1 ) , Suzuki Swifti ning Honda FR-V ( 4/3/3 ) , Fiat Stilo ( 4/4/1 ) , Citroen C1 ( 4/3/2 ) , Smart Forfouri ( 4/2/1 ) ja Dacia Logani ( 3/3/1 ) ohutust .', \
          'expected_ignore_texts': ['( 5/3/2 )', '( 5/4/1 )', '( 4/3/3 )', '( 4/4/1 )', '( 4/3/2 )', '( 4/2/1 )', '( 3/3/1 )'] }, \
        { 'text': 'TABLOO\nRASKEKAAL\nK : Timur Taimazov UKR 430,0 ( 195,0 + 235,0\n)\nH : Sergei Sõrtsov RUS 420,0 ( 195,0 + 225,0 )\n', \
          'expected_ignore_texts': ['( 195,0 + 235,0\n)', '( 195,0 + 225,0 )'] }, \
        { 'text': 'Need seminarid on toimunud Tartus 6 korda (1997–2000, 2002, 2005).', \
          'expected_ignore_texts': ['(1997–2000, 2002, 2005)'] }, \

        # Pattern:  parentheses_num_end_uncategorized
        { 'text': 'A (Rm 9:4 – 5), B (mudelid PI70 ja PI90), C (Rookopli 18), D (meie puhul 165/80), E (1920 x 1080)', \
          'expected_ignore_texts': ['(Rm 9:4 – 5)', '(mudelid PI70 ja PI90)', '(Rookopli 18)', '(meie puhul 165/80)', '(1920 x 1080)'] }, \
        # Pattern:  parentheses_num_start_uncategorized
        { 'text': 'A (23%), B (2 päeva, osavõtutasu 250 eurot), C (13 ja 4 aastased), D (300 000 000 m/sek), E (46,8 p 60-st), F (91% õpetajatest)', \
          'expected_ignore_texts': ['(23%)', '(2 päeva, osavõtutasu 250 eurot)', '(13 ja 4 aastased)', '(300 000 000 m/sek)', '(46,8 p 60-st)', '(91% õpetajatest)'] }, \
        # Pattern:  parentheses_num_mid_uncategorized
        { 'text': 'A ( Group 3G/Quam , Sonera osalus 42,8 protsenti ), B ( trollid nr. 6 , 7 ; bussid nr. 21 , 21B , 22 ja taksod ), C ( IPSE 2000 , Sonera osalus 12,55 protsenti ), D ( ligi 6 eurot kilogramm )', \
          'expected_ignore_texts': ['( Group 3G/Quam , Sonera osalus 42,8 protsenti )', '( trollid nr. 6 , 7 ; bussid nr. 21 , 21B , 22 ja taksod )', '( IPSE 2000 , Sonera osalus 12,55 protsenti )', '( ligi 6 eurot kilogramm )',] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences', 'paragraphs'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']


def test_ignore_consecutive_sentences_with_parentheses():
    # Ignore consecutive sentences that do not contain 3 consecutive lowercase words, 
    #        and that contain ignored content in parenthesis;
    syntax_ignore_tagger = SyntaxIgnoreTagger(ignore_consecutive_parenthesized_sentences = True)
    test_texts = [
        { 'text': 'Meeste slaalom : \n'+\
                  '1. Tom Stiansen ( Norra ) 1.51 , 70 ( 55,81 /55 , 89 ) ,\n'+\
                  '2. Sebastien Amiez ( Prantsusmaa ) 1.51 , 75 ( 54,71 /57 , 04 ) ,\n'+\
                  '3. Alberto Tomba ( Itaalia ) 1.52 , 14 ( 56,21 /55 , 93 ) ,\n',\
          'expected_ignore_texts': ['Tom Stiansen ( Norra ) 1.51 , 70 ( 55,81 /55 , 89 ) ,\n2.', \
                                    'Sebastien Amiez ( Prantsusmaa ) 1.51 , 75 ( 54,71 /57 , 04 ) ,\n3.', \
                                    'Alberto Tomba ( Itaalia ) 1.52 , 14 ( 56,21 /55 , 93 ) ,'] }, \
        { 'text': 'Eile õhtul sõidetud avakatsel sai Markko Märtin ( Subaru , pildil ) viienda aja .\n'+\
                  'Tulemused :\n'+\
                  '1. Tommi Mäkinen ( FIN ) Mitsubishi - 3.46 , 9\n'+\
                  '2. Marcus Grönholm ( FIN ) Peugeot +1,0\n'+\
                  '3. Harri Rovanperä ( FIN ) Peugeot +4,1\n'+\
                  '4. Carlos Sainz ( ESP ) Ford +6,0\n',\
          'expected_ignore_texts': ['Tommi Mäkinen ( FIN ) Mitsubishi - 3.46 , 9\n2.', \
                                    'Marcus Grönholm ( FIN ) Peugeot +1,0\n3.', \
                                    'Harri Rovanperä ( FIN ) Peugeot +4,1\n4.', \
                                    'Carlos Sainz ( ESP ) Ford +6,0'] }, \
        { 'text': 'New Yorgis peetavale WTA finaalturniirile pääseb maailma edetabeli 16 paremat naismängijat .\n'+\
                  'ATP edetabel :\n'+\
                  '1. Sampras 4375 ,\n'+\
                  '2. Michael Chang ( USA ) 3837 ,\n'+\
                  '3. Jevgeni Kafelnikov ( Venemaa ) 3486 ,\n'+\
                  '4. Goran Ivanishevic ( Horvaatia ) 3222 ,\n',\
          'expected_ignore_texts': ['Michael Chang ( USA ) 3837 ,\n3.', \
                                    'Jevgeni Kafelnikov ( Venemaa ) 3486 ,\n4.', \
                                    'Goran Ivanishevic ( Horvaatia ) 3222 ,'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences', 'paragraphs'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']
        
        
        
def test_ignore_sentences_starting_with_time_schedule():
    syntax_ignore_tagger = SyntaxIgnoreTagger( ignore_sentences_starting_with_time=True )
    test_texts = [
        { 'text': '12.05 - 12.35 "Õnne 13" (1. osa)\n\n'+\
                  '12.35 - 13.05 "Õnne 13" (1. osa, kordus)\n\n'+\
                  '13.05 - 13.35 "Õnne 13" (1. osa, teine kordus)\n\n',\
          'expected_ignore_texts': ['12.05 - 12.35 "Õnne 13" (1. osa)\n\n'+\
                                    '12.35 - 13.05 "Õnne 13" (1. osa, kordus)\n\n'+\
                                    '13.05 - 13.35 "Õnne 13" (1. osa, teine kordus)'] }, \
        { 'text': 'Seminari kava .\n'+\
                  '14.15 – 14.45 Eesti internetikaubanduse laienemine välisturgudele ON24 Sisustuskaubamaja näitel .\n'+\
                  '14.45 – 15.15 Tark turundus Facebookis .\n'+\
                  '11.40 – 12.15 E-kaubanduse areng Eestis viimasel kümnendil Kuidas on meie e-riigis arenenud e-kaubandus ?\n'+\
                  '16.15 – 16.30 Seminari lõpetamine .\n',\
          'expected_ignore_texts': ['14.15 – 14.45 Eesti internetikaubanduse laienemine välisturgudele ON24 Sisustuskaubamaja näitel .',\
                                    '14.45 – 15.15 Tark turundus Facebookis .',\
                                    '11.40 – 12.15 E-kaubanduse areng Eestis viimasel kümnendil Kuidas on meie e-riigis arenenud e-kaubandus ?',\
                                    '16.15 – 16.30 Seminari lõpetamine .'
                                    ] }, \
        # Negative examples: do not ignore here 
        { 'text': 'Õigepea on käes oktoobri algus ning yfukatel võimalus kohtuda vahvate eesti noortega.\n'+\
                  '01.10-05.10 toimub meie iga-aastane presentatsioonituur erinevates Eesti koolides, kus meie toredad vabatahtlikud tutvustavad välismaal õppimise võimalusi, räägivad oma kogemustest ning vastavad noorte küsimustele.\n',\
          'expected_ignore_texts': [] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences', 'paragraphs'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [span.enclosing_text for span in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']