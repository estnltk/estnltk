/**
 * This file defines interface used for generating Python wrapper of the
 * vabamorf library.
 *
 * It makes use of STL strings and vectors to make automatic wrapper generation
 * easier.
 */
#if !defined(VABAMORF_H)
#define VABAMORF_H

#include "etmrf.h"

#include <vector>
#include <string>
#include <cstdio>

// forward reference to functions for initializing vabamorf library
bool FSCInit();
void FSCTerminate();


/**
 * Class for storing single analysis.
 */
class Analysis {
public:
    std::string root;
    std::string ending;
    std::string clitic;
    std::string partofspeech;
    std::string form;

    Analysis() {}
    Analysis(const char* root, const char* ending, const char* clitic, const char* partofspeech, const char* form);
    Analysis(Analysis const& analysis);
};

typedef std::vector<Analysis> AnalysisVector;
typedef std::pair<std::string, AnalysisVector > WordAnalysis;
typedef std::vector<std::string> StringVector;


/**
 * Morphological analyzer.
 *
 * Simple wrapper of ETMRF class for doing morphological analysis
 * for one sequence at a time.
 */
class Analyzer {
public:
    Analyzer(std::string const lexPath);
    std::vector<WordAnalysis> analyze(StringVector const& sentence, bool useHeuristics);

private:
    void enableHeuristics(bool heuristic);
    void process(CFSArray<CFSVar>& words);
    void compileResults(CFSArray<CFSVar>& words, std::vector<WordAnalysis>& results);

    ETMRFA morf;
};


/** Morphological synthesizer.
 * 
 * Simple wrapper of ETMRFAS class for doing morphological synthesis.
 */
class Synthesizer {
public:
    Synthesizer(std::string const lexPath);
    std::vector<std::string> synthesize(
        std::string lemma,
        std::string partofspeech,
        std::string form,
        std::string hint,
        bool guess,
        bool phon);
private:
    void updateSettings(bool guess, bool phon);
    
    ETMRFAS morf;
};

#endif
