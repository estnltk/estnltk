import os.path

from estnltk.corpus_processing.parse_koondkorpus import get_div_target
from estnltk.corpus_processing.parse_koondkorpus import parse_tei_corpus_file_content


# ===========================================================
#    Loading Koondkorpus files
# ===========================================================

def _get_koondkorpus_content():
    return '''
<teiCorpus xmlns:xi="http://www.w3.org/2001/XInclude" xmlns="http://www.tei-c.org/ns/1.0"> 
<xi:include href="../../bin/koondkorpus_main_header.xml" /> 
<teiCorpus> 
<xi:include href="../bin/header_aja_postimees.xml" /> 
	<TEI> 
		<teiHeader xmlns="http://www.tei-c.org/ns/1.0" xml:lang="et" xml:id="koondkorpus_local_header" n="$Id:$"> 
			<fileDesc> 
				<titleStmt> 
					<title> Postimees Extra 1998.01.03e </title> 
  				</titleStmt> 
				<publicationStmt> 
  					<p> Vt publitseerimisandmeid failist 
						<ref target="#publicationStmt-main">koondkorpus_main_header.xml</ref> 
					</p> 
  				</publicationStmt> 
				<sourceDesc> 
					<p> Vt allkorpuse päis 
						<ref target="#header_aja_postimees">header_aja_postimees.xml</ref> 
					</p> 
				</sourceDesc> 
			</fileDesc> 
		</teiHeader>
  <text>
    <body>
      <div1 type="ajalehenumber">
        <head> Postimees Extra 1998.01.03e </head>
        <div2 type="alaosa">
          <head> Põhileht </head>
          <div3 type="rubriik">
            <head> Elu </head>
            <div4 type="alamrubriik">
              <div5 type="artikkel"><head> Olla või näida ? </head>
<p> <bibl> <author> <s> TIINA KUULER </s> </author> </bibl> </p>
<p> <s> Möödunud aasta lõpukuust jäi mind kummitama üks sündmus . </s> <s> “ Aktuaalne kaamera ” näitas lühikest lõiku sellest , et Lõuna-Aafrikast informaatikaolümpiaadilt tulid ühe kuld- ja ühe hõbemedaliga tagasi Tartu õpilased . </s> <s> Tartu maaliinide bussijaamas oli neil vastas AK võttegrupp ja pruuni baretiga matemaatikaõpetaja . </s> <s> Väidetavalt oli nende medalite näol tegemist Eesti kõigi aegade tippmargiga reaalainete olümpiaadilt . </s> </p>
<p> <s> Ja teine pilt suvalise missi minekust suvalisele piiritagusele konkursile , kus kõigi telekanalite kaamerad saadavad tütarlapse lennukisse ja , hoolimata saavutatud 56. kohast , võtavad samamoodi ka vastu . </s> <s> Ajakirjanduse vahendusel saame teada , et tal oli kaasas 16 paari kingi ja 30 kleiti , mis õmmeldi valmis kahe päevaga . </s> <s> Et mõni korraldajaist märkas meie missi ja mõni modelliagentuur vestles temaga , ehkki konkreetseid tööpakkumisi ei tehtud . </s> <s> Sellegipoolest on lootust , et Eestit pandi tähele . </s> </p>
<p> <s> Ja nii ongi . </s> </p>
<p> <s> ... </s> </p> </div5>
            </div4>
          </div3>
          <div3 type="rubriik">
            <head> Herilane </head>
            <div4 type="alamrubriik">
              <div5 type="artikkel"><head> Mida toob 1998 ? </head>
<p> <s> <hi rend="rasvane"> Maavaimulik Jaan Muhv : </hi> “ Usuinimesena ootan , et Isa , Poeg ja Püha Vaim jälle kokku tuleksid ja ühe uue maakera looksid - see praegune maakera ei kõlba ju kuhugi ! </s> <s> Uus maakera peaks olema ümmargusem . </s> <s> Samuti võiks Kolmainsus teha nii , et maainimesel oleks kergem . </s> <s> Minu koguduse liikmed peavad lehmi , lambaid , sigu ja kanu . </s> <s> Nii paljude loomade toitmiseks ja kasimiseks kulub kole palju aega ja raha , nii et kiriku remondiks ei jätku sugugi ! </s> </p>
<p> <s> See vana kirik on juba viissada aastat vana , täpselt nigu see maakeragi . </s> <s> Tahaks , et uues kirikus oleks mullikantsel , et kui ma jutlust ütlen , siis mullid masseeriksid mind samal ajal ! </s> <s> Siis kindlasti oleks vaja vaakumaknaid , et seeaeg kui ma jutlust ütlen , siis ilmarahva kisa ei segaks , kui ma räägin . </s> <s> Ja katuseluuki ja neljarattavedu on ka hädasti tarvis , sest Issanda teed on ju viletsad ! </s> </p>
<p> <s> Aga jah , minu süda valutab ikka oma armsate koguduseliikmete pärast ! </s> <s> Jumal peaks kindlasti tegema ikka ühe siukse looma , kes annaks piima nagu lehm , muneks nagu kana , hauguks nagu koer , kasvataks villa nagu lammas ja oleks söödav nigu siga ! </s> <s> No ja kui tegemiseks läheb ja see väga tüli ei tee , siis võiks juba vaadata , et ma saaks uue looma seljas ratsutada ka . ” </s> </p>
<p> <s> <hi rend="rasvane"> Autojuht Kiur Lohv : </hi> “ Mina loodan uuel aastal endale uue naise saada . </s> <s> Mul praegu üks naine on , ma sain selle päris rublaaja lõpus Leedust . </s> <s> Ta võtab ikka saja kilomeetri kohta liiga palju sööki ! </s> <s> Ja kere tahab kogu aeg remonti saada . </s> <s> Agu pulmas just üks ribi läks ! </s> <s> No Agu tegi selle ise korda , aga minek pole ka päris see enam ! </s> </p> 
<p> <s> ... </s> </p> </div5>
            </div4>
          </div3>
        </div2>
      </div1>
    </body>
  </text>
</TEI>
</teiCorpus>
</teiCorpus>
'''


def test_parse_koondkorpus_xml_file_content():
    # Parse Texts from the TEI XML content
    test_xml_content   = _get_koondkorpus_content()
    test_xml_file_path = os.path.join('Postimees', 'PM', 'postimees_1998', 'aja_pm_1998_01_03e.xml')
    # Test getting target
    target = get_div_target( test_xml_file_path )
    assert target == 'artikkel'
    # Extract documents
    texts = parse_tei_corpus_file_content( test_xml_content, \
                                           test_xml_file_path, \
                                           target = [target], \
                                           record_xml_filename=True )
    # Assert loaded content
    assert len(texts) == 2
    doc1 = texts[0]
    doc1_expected_metadata = \
         {'alaosa': 'Põhileht', 'type': 'artikkel', 'rubriik': 'Elu', '_xml_file': 'aja_pm_1998_01_03e.xml', \
          'author': 'TIINA KUULER', 'ajalehenumber': 'Postimees Extra 1998.01.03e', 'title': 'Olla või näida ?', \
          'alamrubriik': ''}
    assert doc1.meta == doc1_expected_metadata
    assert len(doc1.text) == 958
    doc2 = texts[1]
    doc2_expected_metadata = \
         {'title': 'Mida toob 1998 ?', 'ajalehenumber': 'Postimees Extra 1998.01.03e', 'alamrubriik': '', \
          'type': 'artikkel', 'alaosa': 'Põhileht', 'rubriik': 'Herilane', '_xml_file': 'aja_pm_1998_01_03e.xml'}
    assert doc2.meta == doc2_expected_metadata
    assert len(doc2.text) == 1569



def test_parse_koondkorpus_xml_file_content_and_preserve_original_tokenization():
    # Parse Texts from the TEI XML content
    test_xml_content   = _get_koondkorpus_content()
    test_xml_file_path = os.path.join('Postimees', 'PM', 'postimees_1998', 'aja_pm_1998_01_03e.xml')
    target = get_div_target( test_xml_file_path )
    # Extract documents
    texts = parse_tei_corpus_file_content( test_xml_content, \
                                           test_xml_file_path, \
                                           target = [target], \
                                           record_xml_filename=True, \
                                           add_tokenization=True, \
                                           preserve_tokenization=True )
    # Assert loaded content
    assert len(texts) == 2
    doc1 = texts[0]
    assert len(doc1.paragraphs) == 5
    assert len(doc1.sentences)  == 11
    assert len(doc1.words) == 142
    assert len(doc1.words) == len(doc1.tokens)
    doc2 = texts[1]
    assert len(doc2.paragraphs) == 5
    assert len(doc2.sentences)  == 19
    assert len(doc2.tokens) == 297
    assert len(doc2.words) == len(doc2.tokens)



def test_parse_koondkorpus_xml_file_content_and_preserve_original_tokenization_with_name_prefixes():
    # Parse Texts from the TEI XML content
    test_xml_content   = _get_koondkorpus_content()
    test_xml_file_path = os.path.join('Postimees', 'PM', 'postimees_1998', 'aja_pm_1998_01_03e.xml')
    target = get_div_target( test_xml_file_path )
    
    # Extract documents
    # Add prefix 'original_tokenization_' to names of layers of original tokenization
    texts = parse_tei_corpus_file_content( test_xml_content, \
                                           test_xml_file_path, \
                                           target = [target], \
                                           record_xml_filename=True, \
                                           add_tokenization=True, \
                                           preserve_tokenization=True, \
                                           orig_tokenization_layer_name_prefix='original_tokenization_' )
    # Assert loaded content
    assert len(texts) == 2
    # Assert layer names
    for text in texts:
        for layer_name in text.layers:
            assert layer_name.startswith('original_tokenization_')
    # Assert layer access
    doc1 = texts[0]
    assert len(doc1.original_tokenization_paragraphs) == 5
    assert len(doc1.original_tokenization_sentences)  == 11
    assert len(doc1.original_tokenization_words) == 142
    assert len(doc1.original_tokenization_words) == len(doc1.original_tokenization_tokens)
    doc2 = texts[1]
    assert len(doc2.original_tokenization_paragraphs) == 5
    assert len(doc2.original_tokenization_sentences)  == 19
    assert len(doc2.original_tokenization_tokens) == 297
    assert len(doc2.original_tokenization_words) == len(doc2.original_tokenization_tokens)

