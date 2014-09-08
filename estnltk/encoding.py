# -*- coding: utf-8 -*-



class textDiagnostics:

    

    def __init__(self):

        self.allowed_alphabet = ' aeilsntuor.kdmv0p12g\,h-bjäüõ:5346978cöf/)( x%y*+;?z>=<w"#!~q\'˛µ`_|–´ˇ°…[]’¤^½•&×éō²@“óų„±”€³¬šč{ŗ— 37·łęą®æ}§ß©¹«‘Øāį‚$ćķ\n\t\ržš‰'.decode('utf8')



    def containsForbiddenChar(self,s):

        for letter in list(s):

            letter = letter.lower()

            if letter not in self.allowed_alphabet:

                return True

        return False



    def forbiddenCharLocation(self,s):

        for i,letter in enumerate(list(s)):

            letter = letter.lower()

            if letter not in self.allowed_alphabet:

                yield i



    def forbiddenChars(self,s):

        for letter in list(s):

            letter = letter.lower()

            if letter not in self.allowed_alphabet:

                yield letter





### EXAMPLE ###

import os



td = textDiagnostics()



path = '/media/cdata-container/archives/epikriisid_2012/statsionaarsed_epikriisid_20130417/'

for item in os.listdir(path):

    blob = open(path+item).read().decode('utf8')

    if td.containsForbiddenChar(blob) == True:

        chars = list(td.forbiddenChars(blob))

        print item+'\t'+str(len(chars))

