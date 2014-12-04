#include "vabamorf.h"

Analysis::Analysis(const char* root, const char* ending, const char* clitic, const char* partofspeech, const char* form)
    : root(root), ending(ending), clitic(clitic), partofspeech(partofspeech), form(form) {
}

Analysis::Analysis(const Analysis& analysis)
    : root(analysis.root), ending(analysis.ending), clitic(analysis.clitic), partofspeech(analysis.partofspeech), form(analysis.form) {
}

Analyzer::Analyzer(std::string const lexPath) {
    morf.Start(lexPath.c_str(), MF_DFLT_MORFA);
    enableHeuristics(true);
}

void Analyzer::enableHeuristics(bool heuristics) {
    MRF_FLAGS_BASE_TYPE flags=MF_DFLT_MORFA;
    if (heuristics) {
        flags|=MF_OLETA;
    }
    // always add phonetic markup
    // we will trim it in python module, when necessary
    flags|=MF_KR6NKSA;
    morf.SetFlags(flags);
    morf.SetMaxTasand();
    morf.Clr();
}

void Analyzer::process(CFSArray<CFSVar>& words) {
    for (int i=0 ; i<words.GetSize() ; ++i) {
        morf.Set1(words[i]["text"].GetWString());
        morf.Tag<int>((int)i, PRMS_TAGSINT);
    }

    LYLI Lyli;
    CFSVar Analysis;
    Analysis.Cast(CFSVar::VAR_ARRAY);
    INTPTR ipLastPos=-1;
    INTPTR ipDeleted=0;

    while (morf.Flush(Lyli)) {
        if (Lyli.lipp & PRMS_TAGSINT){
            INTPTR ipPos=-ipDeleted+Lyli.ptr.arv;
            if (ipLastPos==-1) {
                words[ipPos]["analysis"]=Analysis;
                ipLastPos=ipPos;
            } else {
                words[ipLastPos]["text"]=words[ipLastPos]["text"].GetAString()+" "+words[ipPos]["text"].GetAString();
                words.RemoveItem(ipPos);
                ipDeleted++;
            }
        } else if (Lyli.lipp & PRMS_MRF) {
            Analysis.Cleanup();
            Analysis.Cast(CFSVar::VAR_ARRAY);
            ipLastPos=-1;
            Lyli.ptr.pMrfAnal->StrctKomadLahku();
            for (INTPTR ipTul=0; ipTul<Lyli.ptr.pMrfAnal->idxLast; ipTul++){
                MRFTUL Tul=*(*Lyli.ptr.pMrfAnal)[(int)ipTul];
                CFSVar Analysis1;
                Analysis1["root"]=Tul.tyvi;
                Analysis1["ending"]=Tul.lopp;
                Analysis1["clitic"]=Tul.kigi;
                Analysis1["partofspeech"]=Tul.sl;
                CFSWString szForm=Tul.vormid; szForm.TrimRight(L", ");
                Analysis1["form"]=szForm;
                Analysis[ipTul]=Analysis1;
            }
        }
    }
}

void Analyzer::compileResults(CFSArray<CFSVar>& words, std::vector<WordAnalysis>& results) {
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
}

CFSArray<CFSVar> cfsvarFromStringVector(StringVector const& sentence) {
    CFSArray<CFSVar> data(sentence.size());
    for (size_t i=0 ; i<sentence.size() ; ++i) {
        CFSVar wordData;
        wordData.Cast(CFSVar::VAR_MAP);
        wordData["text"] = sentence[i].c_str();
        data.AddItem(wordData);
    }
    return data;
}

std::vector<WordAnalysis> Analyzer::analyze(StringVector const& sentence, bool useHeuristics) {
    enableHeuristics(useHeuristics);

    CFSArray<CFSVar> words = cfsvarFromStringVector(sentence);
    process(words);

    std::vector<WordAnalysis> results;
    results.reserve(sentence.size());
    compileResults(words, results);

    return results;
}



Synthesizer::Synthesizer(std::string const lexPath) {
    morf.Start(lexPath.c_str(), MF_DFLT_MORFA);
}

void Synthesizer::updateSettings(bool guess, bool phon) {
    MRF_FLAGS_BASE_TYPE flags=MF_DFLT_MORFA;
    if (guess) {
        flags|=MF_OLETA;
    }
    if (phon) {
        flags|=MF_KR6NKSA;
    }
    morf.SetFlags(flags);
    morf.Clr();
}

std::vector<std::string>
Synthesizer::synthesize(std::string lemma,
                        std::string partofspeech,
                        std::string form,
                        std::string hint,
                        bool guess,
                        bool phon)
{
    updateSettings(guess, phon);
        
    CFSVar word;
    word.Cast(CFSVar::VAR_MAP);
    word["lemma"] = lemma.c_str();
    word["partofspeech"] = partofspeech.c_str();
    word["form"] = form.c_str();
    word["hint"] = hint.c_str();

    MRFTUL Input;
    Input.tyvi=word["lemma"].GetWString();
    Input.sl=word["partofspeech"].GetWString();
    if (Input.sl.IsEmpty()) Input.sl=FSWSTR("*");
    Input.vormid=word["form"].GetWString();
    CFSWString szHint=word["hint"].GetWString();

    morf.Clr();
    MRFTULEMUSED Result;
    if (morf.Synt(Result, Input, szHint) && Result.on_tulem()) {
        CFSVar Text;
        Text.Cast(CFSVar::VAR_ARRAY);
        for (INTPTR ipRes=0; Result[ipRes]; ipRes++){
            Text[ipRes]=Result[ipRes]->tyvi+Result[ipRes]->lopp+Result[ipRes]->kigi;
        }
        word["text"]=Text;
        CFSVar text = word["text"];
        std::vector<std::string> result;
        result.reserve(text.GetSize());
        for (int i=0 ; i<text.GetSize() ; ++i) {
            result.push_back(std::string(text[i].GetAString()));
        }
        return result;
    }
    return std::vector<std::string>();
}
