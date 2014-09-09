# -*- coding: utf-8 -*-

import codecs

# list of available encodings in Python
encodings = [
    'ascii',
    'big5',
    'big5hkscs',
    'cp037',
    'cp424',
    'cp437',
    'cp500',
    'cp720',
    'cp737',
    'cp775',
    'cp850',
    'cp852',
    'cp855',
    'cp856',
    'cp857',
    'cp858',
    'cp860',
    'cp861',
    'cp862',
    'cp863',
    'cp864',
    'cp865',
    'cp866',
    'cp869',
    'cp874',
    'cp875',
    'cp932',
    'cp949',
    'cp950',
    'cp1006',
    'cp1026',
    'cp1140',
    'cp1250',
    'cp1251',
    'cp1252',
    'cp1253',
    'cp1254',
    'cp1255',
    'cp1256',
    'cp1257',
    'cp1258',
    'euc_jp',
    'euc_jis_2004',
    'euc_jisx0213',
    'euc_kr',
    'gb2312',
    'gbk',
    'gb18030',
    'hz',
    'iso2022_jp',
    'iso2022_jp_1',
    'iso2022_jp_2',
    'iso2022_jp_2004',
    'iso2022_jp_3',
    'iso2022_jp_ext',
    'iso2022_kr',
    'latin_1',
    'iso8859_2',
    'iso8859_3',
    'iso8859_4',
    'iso8859_5',
    'iso8859_6',
    'iso8859_7',
    'iso8859_8',
    'iso8859_9',
    'iso8859_10',
    'iso8859_13',
    'iso8859_14',
    'iso8859_15',
    'iso8859_16',
    'johab',
    'koi8_r',
    'koi8_u',
    'mac_cyrillic',
    'mac_greek',
    'mac_iceland',
    'mac_latin2',
    'mac_roman',
    'mac_turkish',
    'ptcp154',
    'shift_jis',
    'shift_jis_2004',
    'shift_jisx0213',
    'utf_8',
    'utf_32',
    'utf_32_be',
    'utf_32_le',
    'utf_16',
    'utf_16_be',
    'utf_16_le',
    'utf_7',
    'utf_8_sig']


class EncodingDetector(object):
    '''Class that works similarily to `chardet` library in Python, but
    uses a predefined alphabet to estimate the confidence.
    '''
    
    def __init__(self, alphabet=u',.!?: abcdefghijklmnopqrstuvwöäõüxyz'):
        '''Initialize encoding detector.
        
        Parameters
        ----------
        alphabet: unicode
            String containing all acceptable unicode characters.
            Default is u',.!?: abcdefghijklmnopqrstuvwöäõüxyz'
        '''
        self._alphabet = frozenset(alphabet)

    def _confidence(self, text):
        k = 0
        for c in text:
            if c in self._alphabet:
                k += 1
        return float(k) / len(text)
        
    def detect(self, text):
        '''Detect the encodings of given text.
        
        Parameters
        ----------
        text: bytes
            The text to be decoded.
        
        Returns
        -------
        list of (dict)
            List of encodings and their confidences stored as a dictionary 
            {'encoding': ENCODING, 'confidence': CONFIDENCE}.
            The list is sorted by the highest confidence.
        '''
        
        confidences = []
        for e in encodings:
            text_decoded = text.decode(e, errors='replace').lower()
            if len(text_decoded) > 0:
                c = self._confidence(text_decoded)
                if c > 0:
                    confidences.append((c, e))
        confidences.sort(reverse=True)
        return [{'confidence': c, 'encoding': e} for c, e in confidences]

    def decode(self, text, errors='strict'):
        '''Decode a given encoded text.
        
        Parameters
        ----------
        text: bytes
            The text to be decoded.
        errors: str
            Determines what to with unencoded bytes. Accepted values are 'strict', 'replace', 'ignore'.

        Raises
        ------
        ValueError
            In case no encoding could be detected for given text.

        Returns
        -------
        str:
            Decoded text.
        '''

        encodings = self.detect(text)
        if len(encodings) == 0:
            raise ValueError('No Possible encodings detected for text {0}.'.format(repr(text)))
        return text.decode(encodings[0]['encoding'], errors=errors)

