# -*- coding: utf-8 -*-

import unittest
from estnltk.encoding import EncodingDetector

def et_text():
        return u'Tüüne öötöömiljöö sünges ja pimedas allmaaraudteejaamas koos Jääääre bändimeestega.'
    
def ru_text():
    return u'Дождь, звонкой пеленой наполнил небо майский дождь.Гром, прогремел по крышам, распугал всех кошек гром.'

def noise():
    return '\x00\x00'

def et_latin1():
    return et_text().encode('latin-1')

def et_utf8():
    return et_text().encode('utf-8')

def ru_cp1251():
    return ru_text().encode('cp1251')

def ru_utf8():
    return ru_text().encode('utf-8')
    
class EncodingTest(unittest.TestCase):

    def test_ru_decode(self):
        det = EncodingDetector(ru_text())
        self.assertEqual(det.decode(ru_cp1251()), ru_text())
        self.assertEqual(det.decode(ru_utf8()), ru_text())
        
    def test_et_decode(self):
        det = EncodingDetector(u'abeiüõäö')
        self.assertEqual(det.decode(et_latin1()), et_text())
        self.assertEqual(det.decode(et_utf8()), et_text())

    def test_noise(self):
        det = EncodingDetector()
        self.assertRaises(ValueError, det.decode, noise())
