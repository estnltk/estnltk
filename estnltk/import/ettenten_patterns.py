# coding: utf-8

import re

PATTERNS = []

SUURTAHED = "A-ZÕÄÖÜ"
VAIKETAHED = "a-zõäöü"

PATT_2 = re.compile(r'''
    (\d+)\s(\.\.\.)\s(\d+)
''', re.X)
PATT_2_REPLACE = r'\1<+/>\2<+/>\3'

# '20 000' --> '20<+/>000'
# 40 000-45 000 --> 40<+/>000-45<+/>000
# 17± 5 cm
PATT_3 = re.compile(r'''
    ((\s|\s?[-–+]|<\+/>)\d+±?)\s((?![0-9]+:)\d+(,\d+)?(\s|<\+/>|\.)(?!aasta))
''', re.X)
PATT_3_REPLACE = r'\1<+/>\3'

# 12632 ±<+/>541<
PATT_3_4 = re.compile(r'''
    (\d+)\s?(±)\s?((<+/>)?\d+)
''', re.X)
PATT_3_4_REPLACE = r'\1<+/>\2<+/>\3'

PATT_3_1 = re.compile(r'''
    (\d+<\+/>\d+)\s
    (\d+(<\+/>\d+(<\+/>\d+)?)?)
''', re.X)
PATT_3_1_REPLACE = r'\1<+/>\2'

# –60 000<+/>m³
PATT_3_3 = re.compile(r'''
    ([-–][0-9]+)\s([0-9]+<\+/>)
''', re.X)
PATT_3_3_REPLACE = r'\1<+/>\2'

# "20 %ga " --> "20%ga"
PATT_4 = re.compile(r'''
    (\d+)\s        # numbrid, millele järgneb tühik
    (              # grupi 2 algus
        %          # protsendimärk
        [^\s]*     # 0 või rohkem mittetühikut
        \s         # tühik
    )              # grupi 2 lõpp
''', re.X)
PATT_4_REPLACE = r'\1\2'

# 0,20 -protsendilise --> 0,20-protsendilise
PATT_4_2 = re.compile(r'''
    (\d)\s(-protsendi[^\s]+\s)
''', re.X)
PATT_4_2_REPLACE = r'\1\2'

PATT_4_3 = re.compile(r'''
    (\s\d+)\s([,.])\s(\d+-?\s(km|(senti|kilo)?meetr|kuu|aastane|seku|milj|minut|tun|peal|tuha|korda|protsen|võrra|ruutmeet|(Rootsi\s)?kroon|(Saksa\s)?marga|dollar|eur|koormus|naela|meetri|kilo|meremiili|tihu|megavatti|liitri|gramm|protsenti))
''', re.X)
PATT_4_3_REPLACE = r'\1\2\3'

#  1 , 5 : 0 , 5 --> 1,5<+/>:<+/>0,5
PATT_4_4 = re.compile(r'''
    (\d+)\s,\s(\d+<\+[^:]+:<\+/>\d+)\s,\s(\d+)
''', re.X)
PATT_4_4_REPLACE = r'\1,\2,\3'

# AS -le --> AS-le
# koera" -ga --> koera"-ga
# 4000 -le --> 4000-le
# 1,75 -ni --> "1,75-ni
# (?!ta|on|ja)
PATT_5 = re.compile(r'''
    (\s[%s]{2}|\s[\]§0-9)])  # lühend (nt AS) või jutumärk, kaldkriips, § või arv
    \s ?                          # tühik kahe grupi vahel
    ([-–][a-z]{1,3}([0-9])?\s)   # kuni kolmetäheline käändelõpp
''' % SUURTAHED, re.X)
PATT_5_REPLACE = r'\1\2'

# 15. 04. 2005 --> 15.04.2005
PATT_33 = re.compile(r'''
    (\d+)\s?    # arv
    \.\s?     # eraldaja ümber on tühikud
    (\d+)\s?    # arv
    \.\s?     # eraldaja ümber on tühikud
    (\d+\s?)    # arv
''', re.X)
PATT_33_REPLACE = r'\1.\2.\3'


# Simon &amp; Schusteri --> Simon<+/>&amp;<+/>Schusteri
PATT_11 = re.compile(r'''
    (\s[A-ZÕÜÖÄ][A-ZÕÜÖÄa-zõüöä]*)   # mistahes mittetühik
    \s         # kuni tühik
    (&amp;)\s  # ampersand ja kogu järgnev tühikuni
    ([A-ZÕÜÖÄ])
''', re.X)
PATT_11_REPLACE = r'\1<+/>\2<+/>\3'


# ( Finck , 1979 ; Kuldkepp , 1994) --> <ignore> ( Finck , 1979 ; Kuldkepp , 1994) </ignore> OTSI RELEVANTSEM
# ( vt tabel 2 )" --> <ignore> ( vt tabel 2 ) </ignore>
# <ignore> ( nr 5/ 13.1.2012 ) </ignore>
_reference_year = r'''
    \s?\d+,?\s?[a-zõüöäA-ZÕÜÖÄ%'"\]!]*  # arv (aasta)
    (/\d+)?[-']?\s               # valikuline kaldkriipsuga aastaarv
    (                       # valikulise grupi 2 algus
        :\s                 # koolon
        \d+                 # arvud, nt lk nr
        ([-–]\d+[\.,]+)\s     # kuni-märk ja arvud, nt lk 5-6
    )?                      # grupi 2 lõpp
    -?\w*\s?\.?\s?                     # lõpus tühik
'''
PATT_12 = re.compile(r'''
    (\([^)]+\))?
    (\(              # viide algab suluga
        (            # viite sees võivad olla
            [^()]  # sümbolid, mis pole sulud
        )+    # rekursiivselt analoogiline struktuur
        {end}        # viide lõpeb aastaarvuga
    \))              # viide lõpeb suluga
'''.format(end=_reference_year), re.X)
PATT_12_REPLACE = r'<ignore> \2 </ignore>'


PATT_BRACS = re.compile(r'''
    (<ignore>\s)?
    (\(\s
        (
            ([A-ZÕÜÖÄa-zõüöä0-9,-<>[]/]{1,3}|\+)\s?
        )*
    \s\))
    (\s</ignore>)?
''', re.X)
PATT_BRACS_REPLACE = r'<ignore> \2 </ignore>'

PATT_REMOVE_NESTED_IGNORES = re.compile(r'''
    (<ignore>[^>]+?)
        <ignore>\s([^>]+?)\s</ignore>
    ([^>]+?</ignore>)
''', re.X)
PATT_REMOVE_NESTED_IGNORES_SUB = r'\1\2\3'

# 8 - 16% --> "82,0<+/>-<+/>16%
PATT_37 = re.compile(r'''
    ([0-9]+)\s
    ([–-])\s?
    ((?![0-9]+:)[0-9]+%?)
''', re.X)
PATT_37_REPLACE = r'\1<+/>\2<+/>\3'

# 1884. a." --> "1884.a.
# 1884 . a" --> "1884.a
PATT_15 = re.compile(r'''
    ([0-9][0-9][0-9][0-9])\s?(\.)\s  # aastaarv, mille järel on punkt ja tühik
    (a\.?\s)                         # täht a (millele võib järgneda punkt) ja tühik
''', re.X)
PATT_15_REPLACE = r'\1\2\3'

# 2004 a. --> 2004a.
PATT_27 = re.compile(r'''
    ([0-9][0-9][0-9][0-9])\s?  # number, mille järel on punkt ja tühik
    (a\.?\s)                   # täht a (millele võib järgneda punkt) ja tühik
''', re.X)
PATT_27_REPLACE = r'\1\2'

# ajal. </s> --> ajal . </s>
# jne. </s> --> jne . </s>
# 50. </s> --> 50 . </s>
# 1995.a. </s> --> 1995.a . </s>
# Eesti konsulaat Tamperes avati 2000.aastal. </s>
_PATT_16_1 = re.compile(r'''
    ((\s|<\+/>|\.|/)[a-zõüöäA-ZÕÜÖÄ0-9'",\-:;]+)\.  # sõna, millele järgneb punkt
    ((\s|<\+/>)</s>)        # lauselõpp
''', re.X)
_PATT_16_2 = re.compile(r'''
    (<\+/>)(</s>)
''', re.X)
_PATT_16_3 = re.compile(r'''
    (\s|\.)(a)(\.\s</s>)
''', re.X)


def PATT_16(s):
    while _PATT_16_1.search(s):
        s = _PATT_16_1.sub(r'\1 .\3', s, count=1)
    while _PATT_16_2.search(s):
        s = _PATT_16_2.sub(r'\1 \2', s, count=1)
    while _PATT_16_3.search(s):
        s = _PATT_16_3.sub(r'\1\2 \3', s, count=1)
    return s


PATT_20_1 = re.compile(r'''
    ((?!P\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
    \s?\.\s?                 # tühikute vahel järgneda punkt
    ((?!S\.)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
    \s?\.\s?       # tühikute vahel järgneda punkt
    ((\.[A-ZÕÜÖÄ]\.)?[A-ZÕÜÖÄ][a-zõüöä]+)   # perekonnanimi
''', re.X)
PATT_20_1_REPLACE = r'\1.\2.<+/>\3'

# N.<+/>Liiduga
# Initsiaalid
PATT_20_2 = re.compile(r'''
    (\s(?!Hr|Pr|Dr|Mrs?|Sm|Nn|Lp|Nt|Jr)[A-ZÕÜÖÄ][a-zõüöä]?)   # initsiaalid, millele võib
    \s?\.\s                 # tühikute vahel järgneda punkt
    ((?!Ja|Ei)[A-ZÕÜÖÄ][a-zõüöä]+)   # perekonnanimi
''', re.X)
PATT_20_2_REPLACE = r'\1.<+/>\2'

# 294 ha-lt --> 294<+/>ha-lt
# 1 ha ..> 1<+/>ha
# 1,0 mM --> 1,0<+/>mM
# 740 kHz-ni
# umbes 2 kg tomateid 1 kg paprikaid 1 kg sibula
PATT_21 = re.compile(r'''
    ((<\+/>)?\d+([,–.]|<\+/>)?\d*\^?-?|½)\s
    (?!j[au]|[oO]n|ca\s|\d{4}|a|e\.|[Ee][id]|[tTMm]a|[mn]e|[ksg]a\s|Nr\s|lk.|vs\s|pr\.|jm\.\s|jt\.?|jj\.|in|Ja\s|Et\s|öö\s|kl\s|st\s|ni\s)
    (([a-zõüöäμ]{1,2}[0-9.\-]?%?³?²?|[a-zõüöä][A-ZÕÜÖÄ]{1,2}[a-zõüöä]?|[A-ZÕÜÖÄ][a-zõüöä]|[°º0o]C|C°|min|μM|spl|MHz|EEK|eur|eek|sec|\$|€|fps|kcal|m\^2)(\s|\s?-[a-zõüöä]{1,2}\s|/))
''', re.X)
PATT_21_REPLACE = r'\1<+/>\4'

PATT_21_1 = re.compile(r'''
    ((\s|<\+/>)(\d+,)?\d{1,3}\.?)\s(a\.?\s)
''', re.X)
PATT_21_1_REPLACE = r'\1<+/>\4'

# 1998. - 2000 --> "1998.<+/>-<+/>2000
# 1.- 4. --> 1.<+/>-<+/>4.
# Kell 14.00 – 16.30
PATT_26 = re.compile(r'''
    (\d+[.%]?)\s?
    ([-–*])\s
    ((?![0-9]+:)\d+[.%]?)
''', re.X)
PATT_26_REPLACE = r'\1<+/>\2<+/>\3'

PATT_26_1 = re.compile(r'''
    (\d+)\s?(\.?)
    ([-–])\s
    ((?![0-9]+:)\d+)\s?(\.?)
''', re.X)
PATT_26_1_REPLACE = r'\1\2<+/>\3<+/>\4\5'

PATT_34 = re.compile(r'''
    (?<!<s>\s)(\(\s)
    ([A-ZÕÜÖÄ]+|%)
    (\s\))(?!\s</s>)
''', re.X)
PATT_34_REPLACE = r'<ignore> \1\2\3 </ignore>'

# <ignore> ( 2 . </s> <s> 8) </ignore> --> <ignore> (2 . 8) </ignore>
PATT_43 = re.compile(r'''
    (?P<algus>\s<ignore>\s\()
    (?P<a>[^<]+)
    </s>\s<s>\s
    (?P<b>[^<]+)?
    (</s>\s<s>\s)?
    (?P<c>[^<]+)?
    (</s>\s<s>\s)?
    (?P<d>[^<]+)?
    (</s>\s<s>\s)?
    (?P<e>[^<]+)?
    (</s>\s<s>\s)?
    (?P<f>[^<]+)?
    (</s>\s<s>\s)?
    (?P<g>[^<]+)?
    (</s>\s<s>\s)?
    (?P<h>[^)]+)
    (?P<lopp>\)\s</ignore>)
''', re.X)
PATT_43_REPLACE = r'\g<algus>\g<a>\g<b>\g<c>\g<d>\g<e>\g<f>\g<g>\g<h>\g<lopp>'

PATT_47 = re.compile(r'''
    ([0-9])\s(\.\.\.|…)   # kolmele punktile
    \s(-?[0-9])           # mille järgi tulevad numbrid, nt aastaarv
    \s(,)\s([0-9])
''', re.X)
PATT_47_REPLACE = r'\1\2\3\4\5'

# 0 : 4 --> 0<+/>:<+/>4
PATT_48 = re.compile(r'''
    ((\s|>)\d+)\s:\s?(\d+)
''', re.X)
PATT_48_REPLACE = r'\1<+/>:<+/>\3'

# <ignore> (FRA) </ignore> <ignore> (13) </ignore> --> <ignore> (FRA) (13) </ignore>
PATT_49 = re.compile(r'''
    (?P<a>\s</ignore>\s)
    (?P<b><ignore>)
''', re.X)
PATT_49_REPLACE = r''

# <ignore> (17) </ignore> , <ignore> (20) </ignore> isa --> <ignore> (17) , (20) </ignore> isa
PATT_50 = re.compile(r'''
    (?P<a>\s</ignore>\s,\s)
    (?P<b><ignore>)
''', re.X)
PATT_50_REPLACE = r','

PATT_51 = re.compile(r'''
    ([0-9a-zõüöäA-ZÕÜÖÄ])(</ignore>)
''', re.X)
PATT_51_REPLACE = r'\1 \2'

# <ignore> .* </ignore> ja <ignore> .* </ignore> --> <ignore> .* ja .* </ignore>
PATT_52 = re.compile(r'''
    (?P<a>\s</ignore>\sja\s)
    (?P<b><ignore>)
''', re.X)
PATT_52_REPLACE = r' ja'

# ( Venemaa ) --> <ignore> ( Venemaa ) </ignore>
# ( Jaapan , Subaru ) --> <ignore> ( Jaapan , Subaru ) </ignore>
PATT_55 = re.compile(r'''
    ([a-zõüöäA-ZÕÜÖÄ0-9]+\s)(\(\s[A-ZÕÜÖÄ][a-zõüöä]+(-[A-ZÕÜÖÄ][a-zõüöä]+)?\s?(,\s[A-ZÕÜÖÄ][a-zõüöä]+\s)?\)\s)
''', re.X)
PATT_55_REPLACE = r'\1<ignore> \2</ignore> '

# ( WTA 210. ) --> <ignore> ( WTA 210. ) </ignore>
# Kreekaga ( 57. ) --> Kreekaga <ignore> ( 57. ) </ignore>
PATT_62 = re.compile(r'''
    ([^>])(\s\(\s(\d+\s?\.(\s[a-zõüöä]+)?|[A-ZÕÜÖÄ]+\s\d+\s?\.)\s\))
''', re.X)
PATT_62_REPLACE = r'\1 <ignore>\2 </ignore>'

# valemilaadsed asjad, nt 3 x 15
PATT_65 = re.compile(r'''
    ([0-9]+)\s
    (x|×)\s
    ([0-9]+)
''', re.X)
PATT_65_REPLACE = r'\1<+/>\2<+/>\3'

PATT_57 = re.compile(r'''
    (\))
    \s\s
    (\+?\d)
''', re.X)
PATT_57_REPLACE = r'\1 \2'

# <+/> 24
PATT_37_1 = re.compile(r'''
    (<\+/>)\s(\d)
''', re.X)
PATT_37_1_REPLACE = r'\1\2'

PATT_37_2 = re.compile(r'''
    (\d{4})<\+/>(\d+\.)
''', re.X)
PATT_37_2_REPLACE = r'\1 \2'

# <ignore> ( SK Reval Sport spordihoone Aia t . </s> <s> <ignore> 20 ) </ignore> </ignore> ;
PATT_91 = re.compile(r'''
    (<ignore>\s\(\s([A-ZÕÜÖÄa-zõüöä]+\s)+\.\s)</s>\s<s>\s<ignore>\s(\d+\s\)\s)</ignore>\s(</ignore>)
''', re.X)
PATT_91_REPLACE = r'\1\3\4'

# SISEMISTE IGNOREIDE EEMALDUS
# <ignore> ( viimasel päeval võitis Goran Ivanisevic <ignore> ( Horvaatia ) </ignore>
#  Thomas Musteri 6<+/>:<+/>7,7<+/>:<+/>5,6<+/>:<+/>7,6<+/>:<+/>2,7<+/>:<+/>5 ) </ignore>
PATT_90 = re.compile(r'''
    (<ignore>((?!<ignore>).)+)<ignore>\s(((?!</ignore>).)+)\s</ignore>(((?!</ignore>).)+</ignore>)
''', re.X)
PATT_90_REPLACE = r'\1\3\5'

# avaldised, nt 2 + 3 = 5 --> 2<+/>+<+/>3<+/>=<+/>5
PATT_68 = re.compile(r'''
    ([0-9])\s([+=≈])\s([+–-]?[0-9])
''', re.X)
PATT_68_REPLACE = r'\1<+/>\2<+/>\3'

# avaldised, nt ' x 12' --> x<+/>12
# 1000 x 109/l
PATT_69 = re.compile(r'''
    ([\s>][xX*])\s([0-9])
''', re.X)
PATT_69_REPLACE = r'\1<+/>\2'

# avaldised, nt n = 122 --> n<+/>=<+/>122
PATT_70 = re.compile(r'''
    (\s[a-zõüöäA-ZÕÜÖÄ])\s([=≈])\s(-?[0-9])
''', re.X)
PATT_70_REPLACE = r'\1<+/>\2<+/>\3'

#  I 26 --> I<+/>26; E 961 --> E<+/>961
PATT_71 = re.compile(r'''
    (\s[A-ZÕÜÖÄ])\s([0-9]+\s)
''', re.X)
PATT_71_REPLACE = r'\1<+/>\2'

# emailid, nt ingrid . </s> <s> vinn [ -at- ] keskkonnaamet.ee
# väljund: ingrid.vinn[-at-]keskkonnaamet.ee
PATT_email_1 = re.compile(r'''
    (\s[^\s]+)\s(\.)\s</s>\s<s>\s([^\s]+)\s\[\s(-at-)\s\]\s([^\s]+)
''', re.X)
PATT_email_1_REPLACE = r'\1\2\3[\4]\5'

# Kristiina . Abel </s> <s> [ -at- ] fin.ee
PATT_email_2 = re.compile(r'''
    (\s[^\s]+)\s(\.)\s([^\s]+)\s</s>\s<s>\s\[\s(-at-)\s\]\s([^\s]+)
''', re.X)
PATT_email_2_REPLACE = r'\1\2\3[\4]\5'

# piret.eensoo [ -at- ] keskkonnaamet.ee
PATT_email_3 = re.compile(r'''
    (\s[^\s]+)\s\[\s(-at-)\s\]\s([^\s]+)
''', re.X)
PATT_email_3_REPLACE = r'\1[\2]\3'

# 5<+/>36-st
PATT_46 = re.compile(r'''
    ([0-9])
    <\+/>
    ([0-9]+-?st)
''', re.X)
PATT_46_REPLACE = r'\1 \2'

# sealh. </s> <s>
# sh. </s> <s>
PATT_72 = re.compile(r'''
    (\s(sealh|sh|lüh))\s?(\.)(\s</s>\s<s>)
''', re.X)
PATT_72_REPLACE = r'\1\3'

PATT_72_1 = re.compile(r'''
    (\sst)\s(\.)(\s</s>\s<s>)
''', re.X)
PATT_72_1_REPLACE = r'\1\2'

# s. </s> <s> o.
# s. </s> <s> t.
PATT_73 = re.compile(r'''
    (\ss)\s?(\.)\s</s>\s<s>\s([ot]\.\s)
''', re.X)
PATT_73_REPLACE = r'\1\2\3'

# Uus t(n). </s> <s> [0-9]
PATT_74 = re.compile(r'''
    (\stn?)\s?(\.\s)</s>\s<s>\s([0-9])
''', re.X)
PATT_74_REPLACE = r'\1\2\3'

# Koost \. </s> <s>
# <s> Nt . </s> <s> sisendada
PATT_75 = re.compile(r'''
    (\s(Koost|Nt))\s(\.)\s(</s>\s<s>)
''', re.X)
PATT_75_REPLACE = r'\1\3'

# toim\. </s> <s>
# Tlk\. </s> <s>
PATT_76 = re.compile(r'''
    (\s(toim|[tT]lk))\s?(\.)\s</s>\s<s>
''', re.X)
PATT_76_REPLACE = r'\1\3'

PATT_86 = re.compile(r'''
    (\sMrs?)\s?(\.)(\s</s>\s<s>)
''', re.X)
PATT_86_REPLACE = r'\1\2'

# ülaindeksid: </s> <s> [0-9]\+ </s> </p>'
PATT_77 = re.compile(r'''
    (</s>\s<s>)(\s[0-9]+\s)(</s>\s</p>)
''', re.X)
PATT_77_REPLACE = r'\1 <ignore>\2</ignore> \3'

# lause ja lõigu sisu: number, nt <p heading="0"> <s> 8 . </s> </p>
PATT_82 = re.compile(r'''
    (<p[^>]+>\s)(<s>\s[0-9]+\s\.\s</s>)(\s</p>)
''', re.X)
PATT_82_REPLACE = r'\1<ignore> \2 <ignore>\3'

# kokkukleepunud ignore, lausestaja viga
PATT_78 = re.compile(r'''
    (\s[^\s]+)(</?ignore)
''', re.X)
PATT_78_REPLACE = r'\1 \2'

PATT_78_1 = re.compile(r'''
    (ignore>)([^\s]+\s)
''', re.X)
PATT_78_1_REPLACE = r'\1 \2'

# VIITED või ÜLAINDEKSID, nt [ 4 ]
PATT_80 = re.compile(r'''
    (\[\s[0-9]+\s\])
''', re.X)
PATT_80_REPLACE = r'<ignore> \1 </ignore>'

# KUUPÄEVAD (arv ja kuu kokku kleepunud)
# nt 1.jaanuar, 15.okt
PATT_81 = re.compile(r'''
    ([0-9]+\.)((jaan|veebr|märts|april|mai|juun|juul|aug|sept|okt|nov|dets)[^\s-]+)
''', re.X)
PATT_81_REPLACE = r'\1 \2'

# 60 km / h --> 60<+/>km/h ; 2,3 h / m --> 2,3<+/>h/m; 110 m/h --> 110<+/>m/h
PATT_14 = re.compile(r'''
    (\s?\d+,?\d*)\s  # algab arvuga, mis võib olla täis- või ujukomaarv,
    ([^\s<]{1,3})\s?       # millele järgneb vähemalt ühe korra miskit
    /\s?              # ja millele omakorda järgneb kaldkriips(/)
    ([^\s]{1,3}\s)       # ja millele järgneb omakorda miskit
''', re.X)
PATT_14_REPLACE = r'\1<+/>\2/\3'

# ' [^ ]\+ \. [A-ZÕÜÖÄ][a-zõüöä]\+ <\/s> <s> [a-zõüöä]\+'
# maksma . Noh </s> <s> naised
PATT_83 = re.compile(r'''
    (\s(?![Kk]od|[Nn]n|[NnSs]t|sm|[HhPp]r|[Mm]rs?|[Dd]r|[Ll]p)[^ ]+\s\.\s)([A-ZÕÜÖÄ][a-zõüöä]+\s)(</s>\s<s>\s)
    ([a-zõüöä]+)
''', re.X)
PATT_83_REPLACE = r'\1\3\2\4'

# <s> Kui pudikeelne hr . Laar </s> <s> veel Rahumäel elas kommunaalmajas
# sm . Kõlvarti </s> <s> tegevus
PATT_84 = re.compile(r'''
    (\s([HhPp]r|sm|[NnSs]t|[Kk]od|[Mm]rs?|[dD]r|[Nn]n|[Ll]p))\s(\.)(\s[A-ZÕÜÖÄ][a-zõüöä]+)\s</s>\s<s>
''', re.X)
PATT_84_REPLACE = r'\1\3\4'

# ' \. [A-ZÕÜÖÄ][a-zõüöä]\+ , <\/s> <s>'
# nt ahjusuu . Eesruumil , </s> <s> nurgatagusel duširuumil ja
PATT_85 = re.compile(r'''
    (\s(?![Kk]od|[Nn]n|[NnSs]t|sm|[HhPp]r|[Mm]rs?|[Dd]r)[^\s]+\s\.)(\s[A-ZÕÜÖÄ][a-zõüöä]+\s,)(\s</s>\s<s>)
''', re.X)
PATT_85_REPLACE = r'\1\3\2'

# sõna ja käändelõpp (kas -i, -il, -it, -iks, -ile, -le, -lt, -l, -ga, -iga, -s, -st, -sse,
# -is, -ist, -ni, -d, -id, -ed, -u, -e, -ta, -t, -ks)
# nt  SKT -st või LinkedIn -ist
# workshop ' e
PATT_92 = re.compile(r'''
     ((\s|>)[a-zõüöäA-ZÕÜÖÄ\-.0-9%]+)\s?
     ([\-\'’])\s((i[ltk]?[se]?|l[et]?|ga|ss?e?|i?st?|ni|[ei]d|u|t|ks|ne|e)\.?\s)
''', re.X)
PATT_92_REPLACE = r'\1\3\4'

# so . </s> <s> nautida
PATT_93 = re.compile(r'''
    (\sso)\s?(\.)(\s</s>\s<s>)
''', re.X)
PATT_93_REPLACE = r'\1\2'

# Vrd . </s> <s> ka nt.
PATT_94 = re.compile(r'''
    (\s([Vv]rd))\s?(\.)\s</s>\s<s>
''', re.X)
PATT_94_REPLACE = r'\1\3'

# Jr . </s> <s> , USA tennisist
PATT_103 = re.compile(r'''
    (\sJr)\s?(\.)\s</s>\s<s>(\s,\s)
''', re.X)
PATT_103_REPLACE = r'\1\2\3'

# Lausestuse jama:
# Koidula Ameerikas <ignore> ( s . </s> 1927 ) </ignore> . </p>
# tänavate olukorraga Võru linnas ? " </s> jne. </p>
PATT_95 = re.compile(r'''
    (</s>)\s(((?!<s>|</p>).)+)(<s>|</p>)
''', re.X)
PATT_95_REPLACE = r'\2\1 \4'

# ( Ibid . , </s> <s> 1 )
PATT_96 = re.compile(r'''
    (\s[Ii]bid)\s(\.)([^<]+)</s>\s<s>\s((Lk\s?\.\s?)?\d+)
''', re.X)
PATT_96_REPLACE = r'\1\2\3\4'

# Lause koosneb vaid numbrist
PATT_97 = re.compile(r'''
    (<s>\s)(-?[0-9,%*]+)(\s</s>\s</p>)
''', re.X)
PATT_97_REPLACE = r'\1<ignore> \2 </ignore>\3'

PATT_98 = re.compile(r'''
    (<s>\s)([\s.…0-9]+)(\s</s>)
''', re.X)
PATT_98_REPLACE = r'\1<ignore> \2 </ignore>\3'

PATT_99 = re.compile(r'''
    (</s>\s<s>\s)(\)\s\.\s)
''', re.X)
PATT_99_REPLACE = r'\2\1'

PATT_99_1 = re.compile(r'''
    (</s>\s<s>\s)(]\s)
''', re.X)
PATT_99_1_REPLACE = r'\2\1'

PATT_99_2 = re.compile(r'''
    </s>\s<s>\s(\)\s,\s)
''', re.X)
PATT_99_2_REPLACE = r'\1'

PATT_99_3 = re.compile(r'''
    </s>\s<s>\s(</s>\s<)
''', re.X)
PATT_99_3_REPLACE = r'\1'

# lausepiirid ('\w\+\.\.\+[A-ZÕÜÖÄ]\+[^ ]\+')
PATT_lausepiir = re.compile(r'''
    (\w+)(\.\.+)([A-ZÕÜÖÄ]+[^ ]+)
''', re.X)
PATT_lausepiir_REPLACE = r'\1 \2 </s> <s> \3'

# www. </s> <s> esindus.ee/korteriturg --> www.esindus.ee/korteriturg
# www. </s> <s> kavkazcenter.com
PATT_www = re.compile(r'''
    ([\s/]www)\s\.\s</s>\s<s>\s
    ([A-ZÕÜÖÄa-zõüöä0-9-]+)\s?\.\s</s>\s<s>\s([^ ]+)
''', re.X)
PATT_www_REPLACE = r'\1.\2.\3'

# http: // www. </s > <s> cavalierklubben
PATT_www2 = re.compile(r'''
    ([\s/]www)\s?\.\s</s>\s<s>\s
    ([a-zõüöä0-9A-ZÕÜÖÄ]+)\s?\.\s?([^ ]+)
''', re.X)
PATT_www2_REPLACE = r'\1.\2.\3'

#  http : //www.offa.org/ stats .
PATT_http = re.compile(r'''
    (http)\s?:\s?(/+)\s?([^ ]+)
''', re.X)
PATT_http_REPLACE = r'\1:\2\3'

# http://www.politsei.ee/dotAsset/225706. ... </s>
PATT_www3 = re.compile(r'''
    (www[^\s]+)\s([./])\s?((?!(\.\.+\s|"\s|\)\s|ning)?</s>)[^\s]+\s)
''', re.X)
PATT_www3_REPLACE = r'\1\2\3'

# Lausestus [^>] \.[A-ZÕÜÖÄ][a-zõüöä]\+
PATT_100 = re.compile(r'''
    ([^>]\s)(\.)([A-ZÕÜÖÄ][a-zõüöä]+)
''', re.X)
PATT_100_REPLACE = r'\1\2 </s> <s> \3'

# 1629 . </s> <s> a. vastu
PATT_101 = re.compile(r'''
    (\d+)\s\.\s</s>\s<s>\s(a\.?\s)
''', re.X)
PATT_101_REPLACE = r'\1.\2'

# hrl \. </s> <s>
PATT_102 = re.compile(r'''
    (\shrl)\s(\.)\s</s>\s<s>
''', re.X)
PATT_102_REPLACE = r'\1\2'

PATT_104 = re.compile(r'''
    (\d+)\s\.\s</s>\s<s>(\saasta)
''', re.X)
PATT_104_REPLACE = r'\1.\2'

# ( 85 . </s> <s> Antonov
# ( ) . </s> <s> Kui
PATT_60 = re.compile(r'''
    (\(\s([0-9]+-|[[a-zõüöä]+\s)?[0-9]+)\s(\.\s)</s>\s<s>\s([A-ZÕÜÖÄ]|saj|aasta)
''', re.X)
PATT_60_REPLACE = r'\1\3\4'

# <s> </s>
PATT_tyhjad_laused = re.compile(r'''
    \s<s>\s</s>(\s)
''', re.X)
PATT_tyhjad_laused_REPLACE = r'\1'

# <p> </p>\n
PATT_tyhjad_loigud = re.compile(r'''
    (<p[^>]*>\s<s>\s</s>\s</p>\n)
''', re.X)
PATT_tyhjad_loigud_REPLACE = r''

# <p> </p> </doc>
PATT_tyhjad_loigud_1 = re.compile(r'''
    <p[^>]*>\s</p>\s(</doc>)
''', re.X)
PATT_tyhjad_loigud_1_REPLACE = r'\1'

PATT_reavahetus = re.compile(r'''
    (</doc>)\n
''', re.X)
PATT_reavahetus_REPLACE = r'\1'

# ----------------------------------------------------------------------------------------------------------


PATTERNS = (
    (PATT_lausepiir, PATT_lausepiir_REPLACE),
    (PATT_100, PATT_100_REPLACE),
    (PATT_99, PATT_99_REPLACE),
    (PATT_99_1, PATT_99_1_REPLACE),
    (PATT_99_2, PATT_99_2_REPLACE),
    (PATT_99_3, PATT_99_3_REPLACE),
    (PATT_83, PATT_83_REPLACE),
    (PATT_84, PATT_84_REPLACE),
    (PATT_85, PATT_85_REPLACE),
    (PATT_92, PATT_92_REPLACE),
    (PATT_93, PATT_93_REPLACE),
    (PATT_94, PATT_94_REPLACE),
    (PATT_96, PATT_96_REPLACE),
    (PATT_95, PATT_95_REPLACE),
    (PATT_101, PATT_101_REPLACE),
    (PATT_102, PATT_102_REPLACE),
    (PATT_103, PATT_103_REPLACE),
    (PATT_104, PATT_104_REPLACE),
    (PATT_12, PATT_12_REPLACE),
    (PATT_BRACS, PATT_BRACS_REPLACE),
    (PATT_REMOVE_NESTED_IGNORES, PATT_REMOVE_NESTED_IGNORES_SUB),
    (PATT_2, PATT_2_REPLACE),
    (PATT_3, PATT_3_REPLACE),
    (PATT_3_1, PATT_3_1_REPLACE),
    (PATT_3_4, PATT_3_4_REPLACE),
    (PATT_37, PATT_37_REPLACE),
    (PATT_4, PATT_4_REPLACE),
    (PATT_33, PATT_33_REPLACE),
    (PATT_11, PATT_11_REPLACE),
    (PATT_15, PATT_15_REPLACE),
    (PATT_4_3, PATT_4_3_REPLACE),
    (PATT_21, PATT_21_REPLACE),
    (PATT_21_1, PATT_21_1_REPLACE),
    (PATT_5, PATT_5_REPLACE),
    (PATT_26, PATT_26_REPLACE),
    (PATT_26_1, PATT_26_1_REPLACE),
    (PATT_27, PATT_27_REPLACE),
    (PATT_20_1, PATT_20_1_REPLACE),
    (PATT_20_2, PATT_20_2_REPLACE),
    (PATT_16, None),
    (PATT_46, PATT_46_REPLACE),
    (PATT_47, PATT_47_REPLACE),
    (PATT_48, PATT_48_REPLACE),
    (PATT_50, PATT_50_REPLACE),
    (PATT_51, PATT_51_REPLACE),
    (PATT_52, PATT_52_REPLACE),
    (PATT_37_1, PATT_37_1_REPLACE),
    (PATT_37_2, PATT_37_2_REPLACE),
    (PATT_65, PATT_65_REPLACE),
    (PATT_60, PATT_60_REPLACE),
    (PATT_62, PATT_62_REPLACE),
    (PATT_57, PATT_57_REPLACE),
    (PATT_55, PATT_55_REPLACE),
    (PATT_4_4, PATT_4_4_REPLACE),
    (PATT_91, PATT_91_REPLACE),
    (PATT_90, PATT_90_REPLACE),
    (PATT_68, PATT_68_REPLACE),
    (PATT_69, PATT_69_REPLACE),
    (PATT_70, PATT_70_REPLACE),
    (PATT_71, PATT_71_REPLACE),
    (PATT_48, PATT_48_REPLACE),
    (PATT_72, PATT_72_REPLACE),
    (PATT_72_1, PATT_72_1_REPLACE),
    (PATT_73, PATT_73_REPLACE),
    (PATT_74, PATT_74_REPLACE),
    (PATT_75, PATT_75_REPLACE),
    (PATT_86, PATT_86_REPLACE),
    (PATT_76, PATT_76_REPLACE),
    (PATT_14, PATT_14_REPLACE),
    (PATT_77, PATT_77_REPLACE),
    (PATT_80, PATT_80_REPLACE),
    (PATT_49, PATT_49_REPLACE),
    (PATT_81, PATT_81_REPLACE),
    (PATT_82, PATT_82_REPLACE),
    (PATT_3_3, PATT_3_3_REPLACE),
    (PATT_email_1, PATT_email_1_REPLACE),
    (PATT_email_2, PATT_email_2_REPLACE),
    (PATT_email_3, PATT_email_3_REPLACE),
    (PATT_78, PATT_78_REPLACE),
    (PATT_78_1, PATT_78_1_REPLACE),
    (PATT_97, PATT_97_REPLACE),
    (PATT_98, PATT_98_REPLACE),
    (PATT_www, PATT_www_REPLACE),
    (PATT_www2, PATT_www2_REPLACE),
    (PATT_http, PATT_http_REPLACE),
    (PATT_www3, PATT_www3_REPLACE),
    (PATT_tyhjad_loigud, PATT_tyhjad_loigud_REPLACE),
    (PATT_tyhjad_laused, PATT_tyhjad_laused_REPLACE),
    (PATT_tyhjad_loigud_1, PATT_tyhjad_loigud_1_REPLACE),
    (PATT_reavahetus, PATT_reavahetus_REPLACE)
)
