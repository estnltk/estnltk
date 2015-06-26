# -*- coding: utf-8 -*-
__author__ = 'Andres'
import re
text = """* [http://www.armenia.ee Armenia.EE Armeenia portaal Eestis] (''vene ja eesti keeles'')
* [http://www.armeniapedia.org Armeniapedia – Armeenia wiki]
*fghfghghfgh [http://www.armenica.org Armenica.org]
[[Pilt:Armenian Qarhunj01.jpg|pisi|
Esiaegne [[megaliit]]ide kompleks [[Zoratsh Kharer]] [[Sjunikhi maakond|Sjunikhi maakonnas]]]]
Ürgasustuse jälgi on leitud mitmes [[Armeenia mägismaa]] piirkonnas: [[Arzni]]st, [[Nurnus]]ist ja mujalt on leitud peatuspaiku kivist tööriistadega. [[Hrazdani jõgi|Hrazdani jõe]] kuristikust, [[Lusakert]]ist ja mujalt on leitud koobaseluasemeid. Kõige vanemad leitud kivist tööriistad on 800 000 aastat vanad.

* [http://www.president.am/eng/ Armeenia president]
* [http://www.gov.am/ Armeenia valitsus]
* [http://www.haias.net/armenien.html virtuaal-Armeenia]
* [http://www.haylife.ru/ Armeenia kultuuri sait, eeskätt Venemaa armeenlaste kultuurist (vene keeles)]
* [http://www.armeniainfo.am/ Armeenia turismiportaal]"""

urlBegin = "http://et.wikipedia.org/wiki/"
wgUrlProtocols = [
     'bitcoin:', 'ftp://', 'ftps://', 'geo:', 'git://', 'gopher://', 'http://',
     'https://', 'irc://', 'ircs://', 'magnet:', 'mailto:', 'mms://', 'news:',
     'nntp://', 'redis://', 'sftp://', 'sip:', 'sips:', 'sms:', 'ssh://',
     'svn://', 'tel:', 'telnet://', 'urn:', 'worldwind://', 'xmpp:', '//'
]
EXT_LINK_URL_CLASS = r'[^][<>"\x00-\x20\x7F\s]'
ExtLinkBracketedRegex = re.compile('\[(((?i)' + '|'.join(wgUrlProtocols) + ')' +
                                   EXT_LINK_URL_CLASS + r'+)\s*([^\]\x00-\x08\x0a-\x1F]*?)\]', re.S | re.U)


def addExternalLinks(sectionObj):
    text = sectionObj['text']
    if ExtLinkBracketedRegex.finditer(text):
        s = ''
        cur = 0
        extLinks = []
        for m in ExtLinkBracketedRegex.finditer(text):
            s += text[cur:m.start()]
            cur = m.end()

            url = m.group(1)
            label = m.group(3)

            s += label
            #s.append((url, label))
            obj = {}
            obj['start'] = len(s)-len(label)
            obj['end']= len(s)
            obj['url']= url
            obj['label']= label
            obj['text'] = str(s) + text[cur:]
            extLinks.append(obj)
        sectionObj['external links'] = extLinks
    return sectionObj

#TODO: test
if __name__ == '__main__':
    print(addExternalLinks(text))