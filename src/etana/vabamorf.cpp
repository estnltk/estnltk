#include "vabamorf.h"


//////////////////////////////////////////////////////////////////////
// DATA STRUCTURES
//////////////////////////////////////////////////////////////////////

Analysis::Analysis(const char* root, const char* ending, const char* clitic, const char* partofspeech, const char* form)
    : root(root), ending(ending), clitic(clitic), partofspeech(partofspeech), form(form) {
}

Analysis::Analysis(const Analysis& analysis)
    : root(analysis.root), ending(analysis.ending), clitic(analysis.clitic), partofspeech(analysis.partofspeech), form(analysis.form) {
}

SpellingResults::SpellingResults(std::string const& word, const bool spelling, const StringVector& suggestions)
    : word(word), spelling(spelling), suggestions(suggestions) {
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
void applyMorfSettings(CLinguistic& linguistic, const bool guess, const bool phonetic, const bool propername) {
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
    CFSArray<CMorphInfos> MorphResults=linguistic.AnalyzeSentense(PTWords);
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
    const bool propername) {

    applyMorfSettings(linguistic, guess, phonetic, propername);
    CFSArray<CFSVar> words = convertInput(sentence);
    addAnalysis(linguistic, disambiguator, words, disambiguate);
    return convertOutput(words);
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
