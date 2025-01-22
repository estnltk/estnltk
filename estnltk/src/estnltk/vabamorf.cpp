/*
Copyright 2015 University of Tartu and Author(s): Timo Petmanson

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
#include "vabamorf.h"
#include "silp.h"


//////////////////////////////////////////////////////////////////////
// DATA STRUCTURES
//////////////////////////////////////////////////////////////////////

Analysis::Analysis(const char* root, const char* ending, const char* clitic, const char* partofspeech, const char* form)
    : root(root), ending(ending), clitic(clitic), partofspeech(partofspeech), form(form) {
}

Analysis::Analysis(std::string const& root, std::string const& ending, std::string const& clitic, std::string const& partofspeech, std::string const& form)
    : root(root), ending(ending), clitic(clitic), partofspeech(partofspeech), form(form) {
}

Analysis::Analysis(const Analysis& analysis)
    : root(analysis.root), ending(analysis.ending), clitic(analysis.clitic), partofspeech(analysis.partofspeech), form(analysis.form) {
}

SpellingResults::SpellingResults(std::string const& word, const bool spelling, const StringVector& suggestions)
    : word(word), spelling(spelling), suggestions(suggestions) {
}

Syllable::Syllable(std::string const& syllable, const int quantity, const int accent)
    : syllable(syllable), quantity(quantity), accent(accent) {
}

//////////////////////////////////////////////////////////////////////
// COMMON FUNCTIONS
//////////////////////////////////////////////////////////////////////

// convert StringVector input to CFSArray input required by vabamorf base library.
CFSArray<CFSVar> convertInput(StringVector const& sentence) {
    CFSArray<CFSVar> data(sentence.size());
    for (size_t i=0 ; i<sentence.size() ; ++i) {
        CFSVar wordData;
        wordData.Cast(CFSVar::VAR_MAP);
        wordData["text"] = sentence[i].c_str();
        data.AddItem(wordData);
    }
    return data;
}

// apply morphoanalysis settings to CLinguistics instance.
void applyMorfSettings(CLinguistic& linguistic, const bool guess, const bool phonetic, const bool propername, 
    const bool stem = false  // TV-2024.02.03 selliselt backward compatible.
    ) {
    linguistic.m_bStem = stem; // TV-2024.02.03 
    linguistic.m_bProperName=propername;
    linguistic.m_bGuess=(guess || linguistic.m_bProperName);
    if (linguistic.m_bGuess) {
        linguistic.m_bAbbrevations = false;
    }
    linguistic.m_bPhonetic = phonetic;
}

//////////////////////////////////////////////////////////////////////
// ANALYZER
//////////////////////////////////////////////////////////////////////

Vabamorf::Vabamorf(std::string const lexPath, std::string const disambLexPath) {
    linguistic.Open(lexPath.c_str());
    disambiguator.Open(disambLexPath.c_str());
}


// add morphological analysis to CFSArray containing the sentence
void addAnalysis(CLinguistic& linguistic, CDisambiguator& disambiguator, CFSArray<CFSVar>& words, const bool disambiguate) {
    //CFSVar &words=Data["words"];
    CFSArray<CPTWord> PTWords;
    for (INTPTR ip=0; ip<words.GetSize(); ip++) {
        PTWords.AddItem(words[ip]["text"].GetWString());
    }
    // perform analysis and optional disambiguation
    CFSArray<CMorphInfos> MorphResults=linguistic.AnalyzeSentence(PTWords);
    if (disambiguate) {
        MorphResults=disambiguator.Disambiguate(MorphResults);
    }
    // collect the analysis results
    ASSERT(PTWords.GetSize()==MorphResults.GetSize());
    for (INTPTR ip=0; ip<words.GetSize(); ip++) {
        const CFSArray<CMorphInfo> &Analysis=MorphResults[ip].m_MorphInfo;
        CFSVar VarAnalysis;
        VarAnalysis.Cast(CFSVar::VAR_ARRAY);
        for (INTPTR ipRes=0; ipRes<Analysis.GetSize(); ipRes++) {
            const CMorphInfo &Analysis1=Analysis[ipRes];
            CFSVar VarAnalysis1;
            VarAnalysis1["root"]=Analysis1.m_szRoot;
            VarAnalysis1["ending"]=Analysis1.m_szEnding;
            VarAnalysis1["clitic"]=Analysis1.m_szClitic;
            VarAnalysis1["partofspeech"]=CFSWString(Analysis1.m_cPOS);
            VarAnalysis1["form"]=Analysis1.m_szForm;
            VarAnalysis[ipRes]=VarAnalysis1;
        }
        words[ip]["analysis"]=VarAnalysis;
    }
}

// convert vabamorf base library output to WordAnalysis instances, which as easier to wrap.
std::vector<WordAnalysis> convertOutput(CFSArray<CFSVar>& words) {
    std::vector<WordAnalysis> results;
    results.reserve(words.GetSize());
    for (int widx=0 ; widx < words.GetSize() ; ++widx) {
        CFSVar word = words[widx];
        CFSVar analysis = word["analysis"];
        AnalysisVector vec;
        for (int aidx=0 ; aidx < analysis.GetSize() ; ++aidx) {
            CFSVar a = analysis[aidx];
            vec.push_back(Analysis(a["root"].GetAString(),
                                   a["ending"].GetAString(),
                                   a["clitic"].GetAString(),
                                   a["partofspeech"].GetAString(),
                                   a["form"].GetAString()));
        }
        results.push_back(WordAnalysis(std::string(word["text"].GetAString()), vec));
    }
    return results;
}

std::vector<WordAnalysis> Vabamorf::analyze(
    StringVector const& sentence,
    const bool disambiguate,
    const bool guess,
    const bool phonetic,
    const bool propername,
    const bool stem // TV-2024.02.03
    ) {

    applyMorfSettings(linguistic, guess, phonetic, propername,
                                                    stem);  // TV-2024.02.03
    CFSArray<CFSVar> words = convertInput(sentence);
    addAnalysis(linguistic, disambiguator, words, disambiguate);
    return convertOutput(words);
}

//////////////////////////////////////////////////////////////////////
// DISAMBIGUATOR
//////////////////////////////////////////////////////////////////////

CFSWString asWStr(std::string const& s) {
    CFSVar var(s.c_str());
    CFSWString ws = var.GetWString();
    return ws;
}

CMorphInfos convertWordAnalysis(const WordAnalysis& wordAnalysis) {
    AnalysisVector const& analysisVec = wordAnalysis.second;
    CMorphInfos infos;
    infos.m_szWord = asWStr(wordAnalysis.first);
    const int n = analysisVec.size();
    for (int i=0 ; i<n ; ++i) {
        Analysis const& analysis = analysisVec[i];
        CMorphInfo info;
        info.m_szRoot = asWStr(analysis.root);
        info.m_szEnding = asWStr(analysis.ending);
        info.m_szClitic = asWStr(analysis.clitic);
        if (analysis.partofspeech.size() > 0) {
            info.m_cPOS = analysis.partofspeech[0];
        }
        info.m_szForm = asWStr(analysis.form);
        infos.m_MorphInfo.AddItem(info);
    }
    return infos;
}

CFSArray<CMorphInfos> convertDisambInput(std::vector<WordAnalysis> const& words) {
    CFSArray<CMorphInfos> infosarray;
    const int n = words.size();
    for (int i=0 ; i<n ; ++i) {
        WordAnalysis const& word = words[i];
        infosarray.AddItem(convertWordAnalysis(word));
    }
    return infosarray;
}

std::string asString(CFSWString const& ws) {
    CFSVar var(ws);
    return std::string(var.GetAString());
}

WordAnalysis convertMorphInfos(CMorphInfos const& infos) {
    AnalysisVector vec;
    const int n = infos.m_MorphInfo.GetSize();
    vec.reserve(n);
    for (int i=0 ; i<n ; ++i) {
        CMorphInfo const& info = infos.m_MorphInfo[i];
        char pos = info.m_cPOS;
        std::string posString;
        posString.push_back(pos);
        Analysis analysis(
            asString(info.m_szRoot),
            asString(info.m_szEnding),
            asString(info.m_szClitic),
            posString,
            asString(info.m_szForm));
        vec.push_back(analysis);
    }
    return WordAnalysis(asString(infos.m_szWord), vec);
}

std::vector<WordAnalysis> convertDisambOutput(CFSArray<CMorphInfos> const& morphInfos) {
    std::vector<WordAnalysis> output;
    const int n = morphInfos.GetSize();
    output.reserve(n);
    for (int i=0 ; i<n ; ++i) {
        CMorphInfos const& infos = morphInfos[i];
        output.push_back(convertMorphInfos(infos));
    }
    return output;
}


std::vector<WordAnalysis> Vabamorf::disambiguate(std::vector<WordAnalysis> &sentence) {
    CFSArray<CMorphInfos> infos = convertDisambInput(sentence);
    infos = disambiguator.Disambiguate(infos);
    std::vector<WordAnalysis> output = convertDisambOutput(infos);
    assert(output.size() == sentence.size());
    return output;
}

//////////////////////////////////////////////////////////////////////
// SPELLCHCKER
//////////////////////////////////////////////////////////////////////

// spellcheck the words and add suggestions
void addSuggestions(CLinguistic& linguistic, CFSArray<CFSVar>& words, const bool suggest) {
    for (INTPTR ip=0; ip<words.GetSize(); ip++) {
        CFSVar &Word=words[ip];
        CPTWord PTWord=Word["text"].GetWString();
        PTWord.RemoveHyphens();
        PTWord.RemovePunctuation();
        PTWord.Trim();
        if (PTWord.m_szWord.IsEmpty() || linguistic.SpellWord(PTWord.m_szWord)==SPL_NOERROR) {
            Word["spelling"]=true;
        } else {
            Word["spelling"]=false;
            if (suggest) {
                CFSWStringArray Suggestions=linguistic.Suggest(PTWord.m_szWord);
                CFSVar VarSuggestions;
                VarSuggestions.Cast(CFSVar::VAR_ARRAY);
                for (INTPTR ipRes=0; ipRes<Suggestions.GetSize(); ipRes++) {
                    VarSuggestions[ipRes]=Suggestions[ipRes];
                }
                Word["suggestions"]=VarSuggestions;
            }
        }
    }
}

// convert output to wrapper format
std::vector<SpellingResults> convertSpellingOutput(CFSArray<CFSVar>& words) {
    std::vector<SpellingResults> results;
    results.reserve(words.GetSize());
    for (int widx=0 ; widx < words.GetSize() ; ++widx) {
        CFSVar word = words[widx];
        std::string text = std::string(word["text"].GetAString());
        CFSVar suggestions = word["suggestions"];
        StringVector suggestStrings;
        suggestStrings.reserve(suggestions.GetSize());
        for (int sidx=0 ; sidx < suggestions.GetSize() ; ++sidx) {
            CFSVar suggestion = suggestions[sidx];
            suggestStrings.push_back(std::string(suggestion.GetAString()));
        }
        results.push_back(SpellingResults(text, word["spelling"].GetInt(), suggestStrings));
    }
    return results;
}


std::vector<SpellingResults>
Vabamorf::spellcheck(StringVector const& sentence, const bool suggest) {
    CFSArray<CFSVar> words = convertInput(sentence);
    addSuggestions(linguistic, words, suggest);
    return convertSpellingOutput(words);
}


//////////////////////////////////////////////////////////////////////
// SYNTHESIZER
//////////////////////////////////////////////////////////////////////

// synthesize words based on lemma, pos and form
void synthesizeWord(CLinguistic& linguistic, CFSVar &Data) {
    const CFSVar &Word=Data;

    CMorphInfo Input;
    Input.m_szRoot=Word["lemma"].GetWString();
    Input.m_cPOS=Word["partofspeech"].GetWString()[0];
    if (!Input.m_cPOS) {
        Input.m_cPOS='*';
    }
    Input.m_szForm=Word["form"].GetWString();
    CFSWString szHint=Word["hint"].GetWString();

    CFSArray<CMorphInfo> Result=linguistic.Synthesize(Input, szHint);
    if (Result.GetSize()) {
        CFSVar Text;
        Text.Cast(CFSVar::VAR_ARRAY);
        for (INTPTR ipRes=0; ipRes<Result.GetSize(); ipRes++) {
            Text[ipRes]=Result[ipRes].m_szRoot+Result[ipRes].m_szEnding+Result[ipRes].m_szClitic;
        }
        Data["text"]=Text;
    }
}

StringVector convertStringVectorOutput(CFSVar& data) {
    CFSVar text = data["text"];
    StringVector words;
    words.reserve(text.GetSize());
    for (int idx=0 ; idx<text.GetSize() ; ++idx) {
        words.push_back(std::string(text[idx].GetAString()));
    }
    return words;
}

StringVector Vabamorf::synthesize(
        const std::string lemma,
        const std::string form,
        const std::string partofspeech,
        const std::string hint,
        const bool guess,
        const bool phonetic) {
    // setup data
    CFSVar data;
    data["lemma"] = lemma.c_str();
    data["form"] = form.c_str();
    if (partofspeech.size() > 0) {
        data["partofspeech"] = partofspeech.c_str();
    }
    if (hint.size() > 0) {
        data["hint"] = hint.c_str();
    }

    applyMorfSettings(linguistic, guess, phonetic, false);
    synthesizeWord(linguistic, data);
    return convertStringVectorOutput(data);
}


//////////////////////////////////////////////////////////////////////
// SYLLABIFICATION
//////////////////////////////////////////////////////////////////////

Syllables syllabify(std::string word) {
    // syllabify the word
    SILP silp;
    FSXSTRING fsxWord(asWStr(word));
    size_t n = silp.silbita(&fsxWord);
    silp.silbivalted();

    // create the wrapper data structure
    Syllables syllables;
    syllables.reserve(n);

    // copy results
    for (int idx=0 ; idx<n ; ++idx) {
        const SILBISTR *silbistr = silp.silbid[idx];
        syllables.push_back(Syllable(asString(silbistr->silp), silbistr->valde, silbistr->rohk));
    }
    return syllables;
}


SentenceSyllables syllabifySentence(const StringVector& sentence) {
    SentenceSyllables ss;
    ss.reserve(sentence.size());
    for (int idx=0 ; idx<sentence.size() ; ++idx) {
        ss.push_back(syllabify(sentence[idx]));
    }
    return ss;
}

// 
// Patch discussed in here: https://github.com/estnltk/estnltk/issues/97
// Credit for the patch goes to: https://github.com/cslarsen
// See also AleksTk's fix: https://github.com/AleksTk/estnltk-1.4-light/blob/master/src/estnltk/vabamorf.cpp
//
#if defined (UNIX)
static void __init_so() {
    FSCInit();
}

static void __init_so() __attribute__((constructor));


static void __exit_so() {
    FSCTerminate();
}

static void __exit_so() __attribute__((destructor));
#endif