# -*- coding: utf-8 -*-
"""
This example demonstrates how to lemmatize a field in a MySQL database.
Requires MySQL-python module to be installed.

INSTRUCTIONS:

1. Create and populate a table named `test.`lemmatize`.

CREATE TABLE `test`.`lemmatize` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `lemmatized` text,
  PRIMARY KEY (`id`),
  FULLTEXT idx (`text`, `lemmatized`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


INSERT INTO `test`.`lemmatize` (`text`)
VALUES
('Venemaa Pihkva oblastikohus tuvastas esmaspäeval alanud protsessil Eestist röövitud kaitsepolitseiniku Eston Kohvri süüasjas rikkumisi ja saatis kaasuse tagasi prokuratuuri.
Kohus otsustas tagastada süüasja materjalid Venemaa peaprokuratuurile, et eemaldada sellest rikkumised, mis takistavad süüasja sisulist läbivaatamist, märkis Pihkva oblastikohus.
Kohvri advokaat Jevgeni Aksjonov ütles Postimehele, et Eston Kohver viiakse tagasi Moskvasse, sest vaja on teha «lisamenetlustoiminguid». Aksjonovi sõnul jätkub kohtuprotsess Pihkvas augustis.
Aksjonovi sõnul seisneb tema kaitse selles, et Kohvrile määrataks võimalikult minimaalne vanglakaristus. Miinimum olevat aga kümmekond aastat.
Ka selgus, et Kohver võib oma perega kohtuda, kuid väidetavalt pole taotlust selleks veel rahuldatud.
Kohtuprotsessi alguses lubati istungitesaali ka ajakirjanikud. Fotograafidel lubati pildistada üldplaanis kohtunikku. Eston Kohvri juhatasid kohtusaali neli maskides eriteenistuslast, keda fotograafidel pildistada ei lubatud.
Kinniste uste taga peetud istungil oli esmaspäeval süüasja arutav kohtunik Larissa Bobrova.
Pihkvas viibiva Postimehe ajakirjaniku sõnul oli Eston Kohver kohtusaalis enne istungi algust rahulik ja ei lasknud ennast väliselt häirida. Saali lubatud ajakirjanike poole vaatas ta vaid ühe korra.
Välisminister Keit Pentus-Rosimannuse sõnul tuleb Kohvri kohtumenetluse puhul meeles pidada, et see ei ole tegelik ja tõsiseltvõetav kohtuprotsess.
«Eston Kohveri röövimise järel on püütud algusest peale luua teadlikult palju segadusttekitavat müra, millega püütakse Venemaa poolt ähmastada tegelikult möödunud aasta 5. septembril juhtunut. Eesti kaitsepolitseinikult võeti jõuga vabadus Eesti Vabariigi territooriumilt FSB poolt ja teda hoitakse jätkuvalt õigusvastaselt kinni Venemaal. Tegu on tõsise rahvusvahelise õiguse rikkumisega ja see on lubamatu,» ütles välisminister.
Pentus-Rosimannus kinnitas, et Eesti jätkab aktiivselt kõikide diplomaatiliste võimaluste kasutamist, et hoida Eston Kohveri küsimuses survet nii rahvusvahelisel tasandil kui ka kahepoolses suhtluses.
Samuti on oluline, et Eesti konsul saaks jätkata Eston Kohvriga regulaarseid kohtumisi, et teda toetada ning et tal oleks usaldusväärne kanal suhtlemiseks. Viimati kohtus konsul Eston Kohvriga 29. mail, et rääkida tema kinnipidamisega seonduvast ning kinnitada talle, et Eesti ametiasutused teevad jätkuvalt kõik, et ta vabastataks ja koju pääseks.
Möödunud nädalal pikendas kohus Kohvri vahi all hoidmise tähtaega 4. augustini ja pani paika, et süüasja kohtulik uurimine algab kinniste uste taga 8. juunil. Kohvrile on esitatud süüdistus spionaažis, illegaalses piiriületuses, relva omamises ja selle salakaubaveos.
Eesti kaitsepolitsei teatas mullu 5. septembri õhtul, et sama päeva hommikul kella 9 ajal võtsid Venemaalt tulnud tundmatud isikud relva ähvardusel vabaduse teenistuskohuseid täitnud kaitsepolitsei ametnikult ja viisid ta endaga üle piiri Venemaale. Vahejuhtum leidis aset Luhamaa piiripunkti läheduses Võrumaal Meremäel.
Kaitsepolitseinik Eston Kohver viidi füüsilist jõudu kasutades ja relva ähvardusel Venemaale. Inimröövile eelnes seejuures Venemaa suunalt operatiivraadioside segamine ja suitsugranaadi kasutamine. Sestpeale on Kohvrit hoitud Moskva Lefortovo vanglas, nüüd aga toodi ta Pihkvasse.'
),
('Tallinna teletornis juhtunud õnnetuse põhjustas kahe köiellaskumise instruktori omavaheline arusaamatus. Ligi kaheksa meetri kõrguselt kukkunud soomlased on tänaseks kodus, kuid atraktsiooni edasine saatus on lahtine.
«Tänaseks on viga saanud soomlannad haiglast koju saanud,» kinnitas atraktsiooni käitava Vidrio Baltico OÜ juhatuse liige Olari Niit. «Eile käisime ühele naisele sadamas lilli viimas. Teine asub Eestis, tal oli väike peapõrutus ja ta ei soovinud kohtuda – suhelnud oleme ainult tema mehega.»
Niidu sõnul põhjustas õnnetuse kommunikatsiooni viga. «Meil on kokku lepitud teatud koht, kümme meetrit teise korruse katuse servast, kus alumine inimene teatab ülemisele, et nüüd tuleb rahulikumalt võtta. Ülemised vaatasid, et kolmkümmend meetrit on veel minna ja tekkis selline väike kruss köie sisse. See meie laskumismehhanismist läbi ei lähe ja naised jäid kinni,» selgitas Niit. «Ülemised võtsid sõlme köiest välja, aga alumine arvas, et ülemised said juba aru ka sellest, et tuleb rahulikumalt laskma hakata. Seda aga ei tehtud ja siis, kui nad selle nööri lahti lasksid, oligi mingi 8 meetrit, kust nad alla tulid. Alumine hakkas jooksma ja signaali vajutama, aga see aeg on nii lühike, et ei jõutud reageerida.»
«Kahekümne meetri kõrguselt ei lennanud keegi alla, see jutt ei vasta tõele. See päris vabalangemine ei olnud, aga asend on laskujatel selline istuv ja seal ei saa jalgu korralikult maha panna. Oleks nad saanud jalgadel maanduda, siis poleks vast peale ehmatuse midagi juhtunud,» lisas Niit.
Alpinismialaseid koolitusi korraldava Jaan Künnapi sõnul puudus meestel ilmselt piisav kogemus. «Kui ülemine mees natuke sellest asjast midagi jagab, siis ta teab, kui palju tal köit kulub, et enne lõppu inimest pidurdama hakata. See asi peaks paigas olema ilma igasuguse raadiosidemeta. Köie peale võib ka märked teha, et kus on veel 10 meetrit jäänud minna ja kus inimene juba maapinnal on,» selgitas Künnap.
Künnap leiab ka seda, et sellistel atraktsioonidel tegutsevatel inimestel peaks olema alpinismialane treenerikutse. Näiteks alpinismis on rangelt keelatud see, et kaks inimest on ühe köie otsas. «Eesti Olümpiakomitee annab välja alpinismi ja kaljuronimise treeneritunnistust. Nendel meestel, kes seal neid töid tegid, ei olnud vist mingeid pabereid,» ütles Künnap.
«Näiteks veematkadel on asi paigas ja grupp saab alati küsida, et kas instruktoril on mingi paber olemas. See nimekiri on kõigile EOK lehel kättesaadav,» lisas Künnap.
Algatatakse sisejuurdlus
Atraktsiooni edasine saatus on lahtine. «Just tulin koosolekult. Meil tuleb siia varsti üks alpinismi ekspert ja tema vaatab asjad üle. Lisaks sellele tehakse veel ka sisejuurdlus. Siis selgub, mis edasi saab,» ütles Niit.
«Minupoolne lahendus on see, et teha köiele sisse märgistus, et ülemine inimene näeks, palju köit on kulunud. Sellisel juhul ei saa seal mingeid valearusaamu olla,» lisas Niit.
Niidu sõnul on nende instruktorid käinud vastavatel koolitustel ja omavad kogemusi. Konkreetsed instruktorid on teinud inimestele üle saja laskumise ja varem ei ole probleeme esinenud. Teletorni atraktsioonil on laskutud tänaseks üle tuhande korra.
Laupäeva õhtul juhtus Tallinna teletorni atraktsioonil õnnetus, kus atraktsioonilt kukkusid alla kaks soomlast. Kiirabi toimetas haiglasse 28- ja 36-aastase naise, kellest ühel on raskemad vigastused. Tänaseks on kannatanud pääsenud kodusele ravile.
Rappelling ehk köiellaskumine on atraktsioon, mis saab alguse teletorni vaateplatvormi servalt, 175 meetri kõrguselt. See on unikaalne atraktsioon terves Euroopas.
'),
('Kreeka ei teinud ära viimast makset IMFile ning uus kokkulepe peaks saabuma päevade jooksul. Kuid Real Time Brussels\'i arvutused näitavad, et nii Kreeka valitsusel kui võlausaldajatel on kolmanda abipaketiga aega talveni.
Kreeka otsustas möödunud nädalal lükata selle kuu 1,6 miljardi euro eest makseid kokku 30. juunile. Seetõttu on oodata kokkulepet hiljemalt 18. juunil toimuval rahandusministrite kohtumisel. Ent kokkulepe võib tulla ka selle nädalavahetuse rahandusministrite kohtumiselt, vahendab Wall Street Journal.
Euroopa rahandusministrid on võtmeisikud sõltumata kokkuleppe ajast. Nemad peavad heaks kiitma uue abipaketi tingimused, määrama Kreeka edusammudest sõltuva tagasimakse graafiku ning pikendama juuniga lõppema pidanud abipaketti. Usume, et pikendus võib kesta septembrini ja ehk isegi detsembrini.
See annab nii Kreekale kui võlausaldajatele piisavalt aega, et otsustada uued abipaketi tingimused ning leppida kokku esimeses väljamakses. Tõenäoliselt on tegu osa või täieliku Euroopa Keskpanga Kreeka investeeringute kasumiga, milleks on 1,9 miljardit eurot.
Euroopa keskpank lubaks Kreeka pankadel osta valitsuse lühiajalisi võlakirju. Meie arvutused näitavad, et see võiks olla 3,5 miljardi euro eest just nagu 2012. aasta augustis, mil Kreeka oli sarnases olukorras.
See annaks Kreeka valitsusele 5,4 miljardit eurot. Ning kuna Kreeka on korduvalt öelnud, et suudab ära teha kaks esimest makset IMFile, siis on neil järel veel vähemalt 600 miljonit eurot. See tähendab, et neil on kuue miljardi eurone rahapuhver, millest on enam kui küllalt, et teha ära 1,6 miljardi eurone makse IMFile kuu lõpus. Samuti jätkub, et maksta IMFile 450 miljonit ning Euroopa Keskpangale 3,4 miljardit järgmisel kuul. See jätab riigile juuli lõpus vähemalt 550 miljonit eurot.
Järgmine suurem väljamakse, 3,2 miljardit Euroopa Keskpangale, on 20. augustil. See on hea, sest vahepeal võib paljugi juhtuda. Näiteks võib peaminister Alexis Tsipas kaotada koalitsiooni toetuse ning peab toetuma opositsioonile. See tähendab, et tulevad uued koalitsioonipartnerid või enneaegsed valimised. Me usume, et Tsipas võidaks valimised taas ning moodustab vähem radikaalse koalitsiooni, mis toetavad tema püüdlusi hoida Kreekat euroalas.
Seejärel saavad osapooled hakata rääkima kolmandast abipaketist. IMF ei tee tõenäoliselt järgmist väljamakset ilma uue paketi ja meetmeteta, mis hoiaksid Kreeka riigivõla kontrolli all. See tähendab, et enne 20. augustit tuleb see teatavaks teha. Mõned ametnikud usuvad, et IMF ei tee väljamakset enne, kui uus abipakett on ametlikult heaks kiidetud. Teised usuvad, et piisab kirjalikust lubadusest nagu see varem on olnud. 3,5 miljardit IMFilt, sellele järgnev 1,8 miljardit EFSFilt ning 180 miljonit eurot intressitulu, on Kreekal augusti lõpus taas 6,7 miljardit eurot. Ning peale augusti 3,2 miljardi eurost makset on Kreekal septembris taas 3,5 miljardit. Sellest piisab, et maksta IMFilt 1,53 miljardit septembris ning 450 miljardit oktoobris. 1. novembril on ka 150 miljoni eurone intressimakse.
Asjad lähevad taas keerukaks detsembris, kui Kreeka peab maksma IMFile 1,2 miljardit eurot. Selleks ajaks peaksid Kreeka ja euroala olema uues abipaketis kokkuleppele jõudnud, ent kui mitte, siis on kreeklastel ikka veel raha. Nad saavad enam kui miljardi euro Euroopa Keskpanga kasumist.
Stsenaarium võib suurem määral muutuda. Ent kõigepealt peab Kreeka leppima soovimatute kärbetega ning reformidega. See stsenaarium eeldab ka et Kreeka suudab oma raha hallata ka muidu peale võla ja intressimaksete.'
);

2. Run command

python lemmatize_mysql.py test test test lemmatize text lemmatized

explanation:
$ python estnltk/examples/lemmatize_mysql.py -h
usage: lemmatize_mysql.py [-h] [--host HOST] [--port PORT] [--pkey PKEY]
                          user passwd schema table src_field dest_field

Process some integers.

positional arguments:
  user         MySQL server user
  passwd       MySQL server user
  schema       The database/schema of the table
  table        The table containing the field
  src_field    The field we wish to lemmatize
  dest_field   The field to store the lemmatized str

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  MySQL server host
  --port PORT  MySQL server port
  --pkey PKEY  The primary key of the table

3. Perform MySQL query:

select * from `test`.`lemmatize`
where match(`text`, `lemmatized`) against ('röövima');

Outputs the article about Eston Kohver.

"""
from __future__ import unicode_literals, print_function, absolute_import

import MySQLdb
import MySQLdb.cursors
import argparse
from estnltk.text import Text


def get_mysql_conn(args):
    kwargs = {
        'port': args.port,
        'host': args.host,
        'user': args.user,
        'passwd': args.passwd,
        'db': args.schema,
        'charset': 'utf8',
        'use_unicode': True
    }
    return MySQLdb.connect(**kwargs)


def lemmatize(text):
    return ' '.join(Text(text).lemmas).lower()

READ_SQL = 'select `{pkey}`, `{src_field}` from `{schema}`.`{table}` where `{dest_field}` is null;'
UPDATE_SQL = 'update `{schema}`.`{table}` set `{dest_field}`=%s where `{pkey}`=%s'


def process(args):
    read_conn = get_mysql_conn(args)
    write_conn = get_mysql_conn(args)

    read_sql = READ_SQL.format(**vars(args))
    update_sql = UPDATE_SQL.format(**vars(args))

    read_cur = MySQLdb.cursors.SSCursor(read_conn)
    read_cur.execute(read_sql)
    for row in read_cur:
        pkey, text = row
        lemmatized = lemmatize(text)
        write_cur = write_conn.cursor()
        write_cur.execute(update_sql, (lemmatized, pkey))
        write_conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='MySQL server host')
    parser.add_argument('--port', type=int, default=3306, help='MySQL server port')
    parser.add_argument('user', type=str, help='MySQL server user')
    parser.add_argument('passwd', type=str, help='MySQL server user')
    parser.add_argument('schema', type=str, help='The database/schema of the table')
    parser.add_argument('table', type=str, help='The table containing the field')
    parser.add_argument('--pkey', type=str, default='id', help='The primary key of the table')
    parser.add_argument('src_field', type=str, help='The field we wish to lemmatize')
    parser.add_argument('dest_field', type=str, help='The field to store the lemmatized str')

    args = parser.parse_args()
    process(args)
