from estnltk.vabamorf.morf import generate_verb_phrases
import unittest

class TestGenerateVerbPhrases(unittest.TestCase):
    
    def test_generate_verb_phrases_smoke(self):
        # output_type = 'verb_form' (default)
        verb_phrases = generate_verb_phrases('hängima')
        self.assertListEqual( sorted(verb_phrases), \
            ['hängi', 'hängib', 'hängid', 'hängige', 'hängigem', 'hängigu', 'hängiks', 'hängiksid', 
            'hängiksime', 'hängiksin', 'hängiksite', 'hängime', 'hängin', 'hänginud', 'hänginud', 
            'hänginuks', 'hänginuksid', 'hänginuksime', 'hänginuksin', 'hänginuksite', 'hänginuvat', 
            'hängis', 'hängisid', 'hängisime', 'hängisin', 'hängisite', 'hängita', 'hängitagu', 
            'hängitaks', 'hängitakse', 'hängitavat', 'hängite', 'hängiti', 'hängitud', 'hängitud', 
            'hängituks', 'hängituvat', 'hängivad', 'hängivat'])

        # output_type = 'verb_phrase'
        verb_phrases = generate_verb_phrases('hängima', output_type='verb_phrase')
        self.assertListEqual( sorted(verb_phrases),  \
            ['ei hängi', 'ei hängiks', 'ei hänginud', 'ei hänginuks', 'ei hänginuvat', 'ei hängita', 
             'ei hängitaks', 'ei hängitavat', 'ei hängitud', 'ei hängituks', 'ei hängituvat', 'ei hängivat', 
             'ei ole hänginud', 'ei ole hängitud', 'ei oleks hänginud', 'ei oleks hängitud', 'ei olevat hänginud', 
             'ei olevat hängitud', 'ei olnud hänginud', 'ei olnud hängitud', 'ei olnuks hänginud', 'ei olnuks hängitud', 
             'ei olnuvat hänginud', 'ei olnuvat hängitud', 'hängi', 'hängib', 'hängid', 'hängige', 'hängigem', 
             'hängigu', 'hängiks', 'hängiksid', 'hängiksime', 'hängiksin', 'hängiksite', 'hängime', 'hängin', 
             'hänginuks', 'hänginuksid', 'hänginuksime', 'hänginuksin', 'hänginuksite', 'hänginuvat', 'hängis', 
             'hängisid', 'hängisime', 'hängisin', 'hängisite', 'hängitagu', 'hängitaks', 'hängitakse', 'hängitavat', 
             'hängite', 'hängiti', 'hängituks', 'hängituvat', 'hängivad', 'hängivat', 'oled hänginud', 'oleks hänginud', 
             'oleks hängitud', 'oleksid hänginud', 'oleksime hänginud', 'oleksin hänginud', 'oleksite hänginud', 
             'oleme hänginud', 'olen hänginud', 'olete hänginud', 'olevat hänginud', 'olevat hängitud', 'oli hänginud', 
             'oli hängitud', 'olid hänginud', 'olime hänginud', 'olin hänginud', 'olite hänginud', 'olnuks hänginud', 
             'olnuks hängitud', 'olnuksime hänginud', 'olnuksin hänginud', 'olnuksite hänginud', 'olnuvat hänginud', 
             'olnuvat hängitud', 'on hänginud', 'on hängitud', 'pole hänginud', 'pole hängitud', 'poleks hänginud', 
             'poleks hängitud', 'polevat hänginud', 'polevat hängitud', 'polnud hänginud', 'polnud hängitud', 
             'polnuks hänginud', 'polnuks hängitud', 'polnuvat hänginud', 'polnuvat hängitud', 'ära hängi', 
             'ärge hängige', 'ärgem hängigem', 'ärgu hängigu', 'ärgu hängitagu'] )

        # output_type = 'complete_phrase'
        verb_phrases = generate_verb_phrases('hängima', output_type='complete_phrase')
        self.assertListEqual( sorted(verb_phrases),  \
            ['ei hängi', 'ei hängiks', 'ei hänginud', 'ei hänginuks', 'ei hänginuvat', 'ei hängita', 'ei hängitaks', 
             'ei hängitavat', 'ei hängitud', 'ei hängituks', 'ei hängituvat', 'ei hängivat', 'ei ole hängitud', 
             'ei oleks hängitud', 'ei olevat hängitud', 'ei olnud hängitud', 'ei olnuks hängitud', 'ei olnuvat hängitud', 
             'hängi', 'hängib', 'hängid', 'hängige', 'hängigem', 'hängigu', 'hängiks', 'hängiksid', 'hängiksime', 
             'hängiksin', 'hängiksite', 'hängime', 'hängin', 'hänginuks', 'hänginuksid', 'hänginuksime', 'hänginuksin', 
             'hänginuksite', 'hänginuvat', 'hängis', 'hängisid', 'hängisime', 'hängisin', 'hängisite', 'hängitagu', 
             'hängitaks', 'hängitakse', 'hängitavat', 'hängite', 'hängiti', 'hängituks', 'hängituvat', 'hängivad', 
             'hängivat', 'ma ei hängi', 'ma ei hängiks', 'ma ei hänginud', 'ma ei hänginuks', 'ma ei hänginuvat', 
             'ma ei hängita', 'ma ei hängitaks', 'ma ei hängitavat', 'ma ei hängitud', 'ma ei hängituks', 'ma ei hängituvat', 
             'ma ei hängivat', 'ma ei ole hänginud', 'ma ei oleks hänginud', 'ma ei olevat hänginud', 'ma ei olnud hänginud', 
             'ma ei olnuks hänginud', 'ma ei olnuvat hänginud', 'ma oleks hänginud', 'ma oleksin hänginud', 'ma olen hänginud', 
             'ma olevat hänginud', 'ma olin hänginud', 'ma olnuks hänginud', 'ma olnuksin hänginud', 'ma olnuvat hänginud', 
             'ma pole hänginud', 'ma poleks hänginud', 'ma polevat hänginud', 'ma polnud hänginud', 'ma polnuks hänginud', 
             'ma polnuvat hänginud', 'me ei hängi', 'me ei hängiks', 'me ei hänginud', 'me ei hänginuks', 'me ei hänginuvat', 
             'me ei hängita', 'me ei hängitaks', 'me ei hängitavat', 'me ei hängitud', 'me ei hängituks', 'me ei hängituvat', 
             'me ei hängivat', 'me ei ole hänginud', 'me ei oleks hänginud', 'me ei olevat hänginud', 'me ei olnud hänginud', 
             'me ei olnuks hänginud', 'me ei olnuvat hänginud', 'me oleks hänginud', 'me oleksime hänginud', 'me oleme hänginud', 
             'me olevat hänginud', 'me olime hänginud', 'me olnuks hänginud', 'me olnuksime hänginud', 'me olnuvat hänginud', 
             'me pole hänginud', 'me poleks hänginud', 'me polevat hänginud', 'me polnud hänginud', 'me polnuks hänginud', 
             'me polnuvat hänginud', 'me ärgem hängigem', 'nad ei hängi', 'nad ei hängiks', 'nad ei hänginud', 
             'nad ei hänginuks', 'nad ei hänginuvat', 'nad ei hängita', 'nad ei hängitaks', 'nad ei hängitavat', 
             'nad ei hängitud', 'nad ei hängituks', 'nad ei hängituvat', 'nad ei hängivat', 'nad ei ole hänginud', 
             'nad ei oleks hänginud', 'nad ei olevat hänginud', 'nad ei olnud hänginud', 'nad ei olnuks hänginud', 
             'nad ei olnuvat hänginud', 'nad oleks hänginud', 'nad olevat hänginud', 'nad olid hänginud', 'nad olnuks hänginud', 
             'nad olnuvat hänginud', 'nad on hänginud', 'nad pole hänginud', 'nad poleks hänginud', 'nad polevat hänginud', 
             'nad polnud hänginud', 'nad polnuks hänginud', 'nad polnuvat hänginud', 'nad ärgu hängigu', 'oleks hängitud', 
             'olevat hängitud', 'oli hängitud', 'olnuks hängitud', 'olnuvat hängitud', 'on hängitud', 'pole hängitud', 
             'poleks hängitud', 'polevat hängitud', 'polnud hängitud', 'polnuks hängitud', 'polnuvat hängitud', 'sa ei hängi', 
             'sa ei hängiks', 'sa ei hänginud', 'sa ei hänginuks', 'sa ei hänginuvat', 'sa ei hängita', 'sa ei hängitaks', 
             'sa ei hängitavat', 'sa ei hängitud', 'sa ei hängituks', 'sa ei hängituvat', 'sa ei hängivat', 'sa ei ole hänginud', 
             'sa ei oleks hänginud', 'sa ei olevat hänginud', 'sa ei olnud hänginud', 'sa ei olnuks hänginud', 'sa ei olnuvat hänginud', 
             'sa oled hänginud', 'sa oleks hänginud', 'sa oleksid hänginud', 'sa olevat hänginud', 'sa olid hänginud', 
             'sa olnuks hänginud', 'sa olnuksite hänginud', 'sa olnuvat hänginud', 'sa pole hänginud', 'sa poleks hänginud', 
             'sa polevat hänginud', 'sa polnud hänginud', 'sa polnuks hänginud', 'sa polnuvat hänginud', 'sa ära hängi', 
             'ta ei hängi', 'ta ei hängiks', 'ta ei hänginud', 'ta ei hänginuks', 'ta ei hänginuvat', 'ta ei hängita', 
             'ta ei hängitaks', 'ta ei hängitavat', 'ta ei hängitud', 'ta ei hängituks', 'ta ei hängituvat', 'ta ei hängivat', 
             'ta ei ole hänginud', 'ta ei oleks hänginud', 'ta ei olevat hänginud', 'ta ei olnud hänginud', 'ta ei olnuks hänginud', 
             'ta ei olnuvat hänginud', 'ta oleks hänginud', 'ta olevat hänginud', 'ta oli hänginud', 'ta olnuks hänginud', 
             'ta olnuvat hänginud', 'ta on hänginud', 'ta pole hänginud', 'ta poleks hänginud', 'ta polevat hänginud', 
             'ta polnud hänginud', 'ta polnuks hänginud', 'ta polnuvat hänginud', 'ta ärgu hängigu', 'te ei hängi', 'te ei hängiks', 
             'te ei hänginud', 'te ei hänginuks', 'te ei hänginuvat', 'te ei hängita', 'te ei hängitaks', 'te ei hängitavat', 
             'te ei hängitud', 'te ei hängituks', 'te ei hängituvat', 'te ei hängivat', 'te ei ole hänginud', 'te ei oleks hänginud', 
             'te ei olevat hänginud', 'te ei olnud hänginud', 'te ei olnuks hänginud', 'te ei olnuvat hänginud', 'te oleks hänginud', 
             'te oleksite hänginud', 'te olete hänginud', 'te olevat hänginud', 'te olite hänginud', 'te olnuks hänginud', 
             'te olnuksite hänginud', 'te olnuvat hänginud', 'te pole hänginud', 'te poleks hänginud', 'te polevat hänginud', 
             'te polnud hänginud', 'te polnuks hänginud', 'te polnuvat hänginud', 'te ärge hängige', 'ärgu hängitagu'])
