# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest
from estnltk.textdiagnostics import *

est_text = 'Segan suhkrut malbelt tassis, kus nii armsalt aurab tee.'
rus_text = 'Дождь, звонкой пеленой наполнил небо майский дождь.'


class DiagnosticsTest(unittest.TestCase):
    
    def test_estonian(self):
        td_et = TextDiagnostics()
        td_ru = TextDiagnostics(RUSSIAN)
        self.assertTrue(td_et.is_valid(est_text))
        self.assertFalse(td_ru.is_valid(est_text))
        
    def test_russian(self):
        td_et = TextDiagnostics()
        td_ru = TextDiagnostics(RUSSIAN)
        self.assertFalse(td_et.is_valid(rus_text))
        self.assertTrue(td_ru.is_valid(rus_text))


if __name__ == '__main__':
    unittest.main()
