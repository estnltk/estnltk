# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..morf import analyze
from multiprocessing import Pool
import unittest
import six
import os


class MultithreadingTest(unittest.TestCase):
    
    def test_multi(self):
        if os.name == 'nt' and six.PY2: # do not run the test. avoid this Python bug http://bugs.python.org/issue10845
            return
        self.assertListEqual(self.compute_multi(), self.compute_single())
    
    def compute_single(self):
        return [analyze(text) for text in self.indata()]
        
    def compute_multi(self):
        pool = Pool(3)
        return pool.map(analyze, self.indata())
    
    def indata(self):
        return [
            '«Olen saatnud klubile paberi, et homseni (tänaseni – toim) on neil aega ära maksta kõik võlgnevused, mida on 4,5 kuu palga jagu. Lisaks peaksid nad mind taas kaasama esindusmeeskonna tegemistesse,» rääkis Pareiko Volgale esitatud nõudmistest ning avaldas, mis juhtub, kui neid ei täideta: «Siis katkestan teisipäeval omalt poolt meeskonnaga lepingu ning tulen kolmapäeval Tallinna. Kogu juhtum läheb seejärel edasi UEFAsse.»',
            '«Arvan, et nad ei hakka maksma ning seega on minu jaoks asjad tegelikult selged. Meeskonnas tahetakse, et eraldi treenivad mehed lahkuksid, ja praegu on asjad niimoodi ka minemas,» selgitas 37-aastane väravavaht. «Minu eest ajab asju üks Bulgaariast pärit advokaat. Tema teeb kõik tööd ära ning minu ülesanne on panna vajalikesse kohtadesse allkiri.»',
            'Pareiko on ka varasemalt avaldanud, et mõlemale osapoolele on selge, et tema vanuses jalgpallurit on raske müüa ning mänguaja leidmiseks on vajalik praegune kontraht lõpetada ja leida talvel uus tööandja. Volgaga ühepoolselt lepingu lõpetamise korral ongi vaja asjad ka UEFAga korda ajada, et Eesti koondislane saaks seejärel liituda mõne teise klubiga. Samas on vaja dokumente sellegi jaoks, et oma välja teenitud töötasu ikkagi kätte saada.',
            'Pareiko jaoks on juba plaan paigas, mis saab edasi, kui ta sel nädalal Volga meeskonna juurest lahkub. Kuna 12. novembril on Eesti koondisel kavas maavõistlusmäng Norraga ja 15. novembril EM-valikmatš San Marinoga, on väravavaht leidnud võimaluse enda vormis hoidmiseks.',
            '«27. oktoobril on plaanis minna kümneks päevaks Poola, seal on mul kokkulepe tuttava väravavahtide treeneriga. Saaksin seal harjutada ja vormi hoida. Seejärel vaataksin, kas oleks võimalik veel Levadia trennidega liituda,» tutvustas Pareiko edasisi plaane.',
            'Venemaa esiliigas hoiab veel mullu kõrgliigas mänginud Volga praegu 15. vooru järel 21 punktiga 11. positsiooni. Eile viigistati 1:1 Pareiko kunagise tööandja Tomski Tomiga. Tomsk hoiab parasjagu 29 silmaga 2. kohta ehk on praeguse seisuga püüdmas taas pääset kõrgemasse seltskonda.',
            '23-aastane India jalgpallur Peter Biaksangzuala suri pühapäeva hommikul haiglas vigastuse tagajärjel, mille ta sai viis päeva varem väravat tähistades.',
            'Biaksangzuala vigastas teisipäeval seljaaju, kui üritas väravat tähistada Miroslav Klose moodi kahekordse saltoga.',
            'Biaksangzuala klubi Bethelem Venghtlang kaotas mängu Chanmari Westile 2:3, hukkunud pallur lõi värava 62. minutil.',
            '"Ta üritas teha sakslasele Klosele omast saltoga trikki, kuid see läks kahjuks valesti," ütles üks juhtunut pealt näinud allikas reporteritele.',
            'Brasiilia karastusjookide tootja Guaraná poolt USA-s läbi viidud kampaania võitjal oli valida, kas 10 000 dollarit auhinnaraha või eksklusiivne kokkusaamine Brasiilia vutitähe Neymariga.',
            'Kampaania võitjaks osutunud 16-aastane jalgpalliga tegelev El Paso koolitüdruk Rhiannon Conelley valis kohtumise Neymariga. "Minek Hispaaniasse ja kohtumine iidoliga, see kõlab uskumatult," rääkis õnnelik Conelley kohalikule ajalehele El Paso Times. "Soovin Neymariga nii väga kohtuda ja see on mulle palju tähtsam kui 10 000 dollarit. Paljud võivad mitte nõustuda, kuid mul on õnneks võimalus ise otsustada." Ka tüdruku vanemad olid ebameeldivalt üllatunud, et kopsakas rahaline preemia jääb välja võtmata.',
            'Ajakirjanik uuris õnnelikult tüdrukult, mida ta kohtumisel Neymariga vutitähelt kindlasti küsiks. "Küsin, kas ta ei tahaks minuga abielluda," vastas Conelley naljatledes. "Loodan teda mitte hirmutada, ma ei taha, et turvamehed mind ruumist välja viskaksid," lisas tüdruk õhinal.',
            'Kampaanias osalemiseks tuli saata foto, mis oleks seotud nii jalgpalli kui Guaraná karastusjookidega. Pildid pandi firma kodulehele üles ja inimesed andsid neile hääli. Conelley pilt osutus populaarseimaks kogudes üle 4000 hääle.']
