# -*- coding: utf-8 -*-

import re
import json

linkBegin = "http://et.wikipedia.org/wiki/"

infob = """{{Riik
|  riiginimi = Afganistani Islamivabariik
|  omastav = Afganistani
|  omakeelne_nimi_1 = puštu |  د افغانستان اسلامي جمهوریت|de Afghānistān Islāmī Jumhūrīyat
|  omakeelne_nimi_2 = dari | جمهورئ اسلامی افغانستان |Jomhūrī-ye Eslāmī-ye Afghānestān
|  mis_lipp =
|  mis_vapp =
|  vapi_laius = 100px
|  asendikaart = Afghanistan in its region.svg
|  deviis =
|  riigikeel =
|  ametlik_keel = [[puštu keel|puštu]], [[dari keel|dari]]
|  pealinn = [[Kabul]]
|  riigipea_ametinimi = President
|  riigipea_nimi = [[Ashraf Ghani]]
|  valitsusjuhi_ametinimi = Tegevjuht
|  valitsusjuhi_nimi = [[‘Abdullāh ‘Abdullāh]]
|  pindala = 647500
|  rahvaarv =
|  iseseisvus = [[19. august]] [[1919]]
|  valuuta = [[Afganistani afgaani|afgaani]] (AFN)
|  ajavöönd = [[maailmaaeg]] +4:30
|  hümn = [[Sououd-e-Melli]]
|  usk = islam
|  üladomeen = [[.af]]
|  telefonikood = 93
|  riigikord =
|  SKT =
|  SKT_elaniku_kohta =
|  rok-i_kood = AFG
|  märkused =
}}"""

#tühjad väljad jäävad sisse
#kujul {'text': '', 'title': 'mis_lipp'}

def infoboxParser(infob):
    typeRegEx = re.compile(r"\{\{[A-Za-zÄÖÕÜäöõü]+\n([^}])+\}\}")
    contentRegEx = re.compile(r"\n\W+(.+)")
    ibType = re.search(typeRegEx, infob)
    ibContent = re.findall(contentRegEx, infob)
    #print(ibType.group(1)) #IB Tüüp. Riik, Provints, Taksonitabel jne
    #print(ibContent)
    ibDict = [{"type": ibType.group(1)}]
    for i in ibContent:
        try:
            title, text = i.split("=")[0].strip(), i.split("=")[1].strip()
            ibDict.append({"title":title,"text":text})
        except:
            pass

    return ibDict

def wikiLinkParser(line):
    """returns dict obj"""
    linkBegin = "http://et.wikipedia.org/wiki/"
    if "|" not in line:
        linkRegEx = re.compile(r"\[\[([^\]]+)\]")
        matchObj = re.match(linkRegEx, line)
        link, text = linkBegin + matchObj.group(1), matchObj.group(1)
        return {"link":link, "text":text}
    else:
        linkRegEx = re.compile(r"\[\[([^\|]+)\|([^\]]+)")
        matchObj = re.match(linkRegEx, line)
        link, text = linkBegin + matchObj.group(1), matchObj.group(2)
        return {"link":link, "text":text}

def islink(line):
    matchjObj = re.match(r"\[\[([^\]]+\]\])", line)
    return True if matchjObj else False

#hackish TEST

print(infoboxParser(infob))
print(json.dumps(infoboxParser(infob)))

infoblinelist = infob.splitlines()
for i in infoblinelist:
    #i = i.lstrip("| ")
    i = i.split("= ")
    print(i)
    if len(i)>1:
        print(i[1])
        if islink(i[1]):
            print(wikiLinkParser(i[1]))



