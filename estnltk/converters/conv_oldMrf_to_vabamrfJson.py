# -*- coding: utf-8 -*-
#
#     Abifunktsioonid koondkorpuse T3MESTA morf märgenduse konverteerimiseks
#     kujule, mis on sarnane vabamorfi JSON kujuga;
#
#     Sisend:  kataloog, kus asuvad morf m2rgendusega failid (*.mrf failid);
#     Valjund: iga sisendkataloogi .mrf faili sisu konverteeritakse JSON kujule,
#              ning kirjutatakse .json-alpha faili, iga lause JSON eraldi real;
# 

import json, re, sys, os, os.path

# =================================================================
#   Morf analüüside konverteerimine vabamorfi JSON ~formaati
# =================================================================

def getJSONanalysis(root, pos, form):
    result = { "clitic":"", "ending":"", "form":form, "partofspeech":pos, "root":""}
    # {
    #   "clitic": "string",
    #   "ending": "string",
    #   "form": "string",
    #   "partofspeech": "string",
    #   "root": "string"
    # },
    breakpoint = -1
    for i in range(len(root)-1, -1, -1):
        if root[i] == '+':
            breakpoint = i
            break
    if breakpoint == -1:
        result["root"]   = root
        result["ending"] = "0"
        if not re.match("^\W+$", root):
            try:
                print( " No breakpoint found from: ", root, pos, form )
            except UnicodeEncodeError:
                print( " No breakpoint found from: ", (root+" "+pos+" "+form).encode('utf8').decode(sys.stdout.encoding) )
    else:
        result["root"]   = root[0:breakpoint]
        result["ending"] = root[breakpoint+1:]
    return result


def convertTokenToJSON( token ):
    parts = token.split('    ')
    text = parts[0]
    tokenJSON = { 'text' : text, 'analysis' : [] }
    for part in parts[1:]:
        root = (re.sub('^(.+)//_[A-Z]_[^/]*//\s*$', '\\1', part)).strip()
        pos  = (re.sub('^(.+)//_([A-Z])_[^/]*//\s*$', '\\2', part)).strip()
        form = ((re.sub('.+//_[A-Z]_([^/]*)//', '\\1', part)).strip()).rstrip(',')
        tokenJSON['analysis'].append( getJSONanalysis(root, pos, form) )
    return tokenJSON


def getSentenceInJSONformat( sentenceMrf ):
    results = { 'words': [] }
    for token in sentenceMrf:
        if re.match('\S+\s{4}\S*', token):
            results['words'].append( convertTokenToJSON(token) )
    return json.dumps(results, ensure_ascii=False)+"\n"


def cleanFromAnnotations(sentence):
    text = ""
    for token in sentence:
        if not re.match("\s*<[^>]+>\s*$", token):
            m1 = re.match("(\S+)\s{4}.*", token)
            if (m1):
                text += m1.group(1)+" "
    return text

# =================================================================
#   Yhe faili konverteerimine
# =================================================================

def convertMrfToJSON(inFileName, outFileName):
    articleContent = []
    wordsInArticle = 0
    curIgnoreContent = None
    in_f  = open(inFileName, mode='r', encoding='utf-8')
    for line in in_f:
        line = line.rstrip()
        if re.match("\s*<ignoreeri>\s*$", line):
            curIgnoreContent = ""
        elif re.match("\s*</ignoreeri>\s*$", line):
            curIgnoreContent = None
        elif curIgnoreContent != None:
            curIgnoreContent = curIgnoreContent + " " + line
        elif curIgnoreContent == None:
            if re.match("\s*<s>\s*$", line):
                # Uus lause
                articleContent.append([])
            elif not re.match("\s*<[^>]+>\s*$", line):
                # Uus s6na
                wordsInArticle += 1
                articleContent[-1].append( line )
    in_f.close()
    if (len(articleContent) > 0):
        out_f = open(outFileName, mode='w', encoding='utf-8')
        for sentence in articleContent:
            out_f.write( getSentenceInJSONformat( sentence ) )
            #print(cleanFromAnnotations(sentence))
        out_f.write( '\n' )
        out_f.close()

    

outputSuffix = ".json-alpha"
inputSuffix  = ".mrf"

if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
    inputDir  = None
    outputDir = None
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if os.path.isdir(arg):
            if not inputDir:
                inputDir  = arg
            elif not outputDir:
                outputDir = arg

    if not outputDir:
        outputDir = inputDir

    for fileName in os.listdir(inputDir):
        filePath = os.path.join(inputDir, fileName)
        if (filePath.endswith(inputSuffix)):
            outFilePath = os.path.join(outputDir, fileName)
            outFilePath = re.sub("\.([^.]+)$", ".\\1"+outputSuffix, outFilePath)
            print (fileName)
            convertMrfToJSON(filePath, outFilePath)

else:
    print(" Please give argument(s):  <t3mesta-inputdir>  <outputdir>(optional)")
    print(" Example:\n     python  "+sys.argv[0]+"  aja_EPL_1999")

