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
/**
 * This file defines interface used for generating Python wrapper of the
 * vabamorf library. The code is based on command line programs coming with vabamorf.
 *
 * It makes use of STL strings and vectors to make automatic wrapper generation
 * easier.
 */
#if !defined(VABAMORF_H)
#define VABAMORF_H

#include "etmrf.h"
#include "proof.h"

#include <vector>
#include <string>
#include <cstdio>

// references vabamorf library initialization functions,
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
    Analysis(std::string const& root, std::string const& ending, std::string const& clitic, std::string const& partofspeech, std::string const& form);
    Analysis(Analysis const& analysis);
};

// type for storing a vector of analysis results
typedef std::vector<Analysis> AnalysisVector;

// type for storing words and analysis vector pair
typedef std::pair<std::string, AnalysisVector > WordAnalysis;

// type for a string vector.
typedef std::vector<std::string> StringVector;


/**
 * Class that represents a syllable.
 * This is basically a mockoff of SILBISTR
 */
class Syllable {
public:
    std::string syllable;
    int quantity; // välde
    int accent; // rõhk

    Syllable() {};
    Syllable(std::string const& syllable, const int quantity, const int accent);
};

// syllables of a single word
typedef std::vector<Syllable> Syllables;

// syllables of every word of a sentence
typedef std::vector<Syllables> SentenceSyllables;

/**
 * Class for storing spelling results.
 */
class SpellingResults {
public:
    std::string word;
    bool spelling;
    StringVector suggestions;

    SpellingResults() { }
    SpellingResults(std::string const& word, const bool spelling, const StringVector& suggestions);
};

// type for spelling suggestions for a sequence of words.
typedef std::vector<SpellingResults> SpellingSuggestions;

/**
 * Morphological analyzer.
 *
 * Simple wrapper of ETMRF class for doing morphological analysis
 * for one sequence at a time.
 */
class Vabamorf {
public:
    /**
     * Initialize the vabamorf..
     * @param lexPath The path to the binary version of the dictionary (et.dct)
     * @param disambLexPath The path to the disambiguator dictionary (et3.dtc)
     */
    Vabamorf(std::string const lexPath, std::string const disambLexPath);

    /**
     * Analyze a vector of words (a sentence).
     * @param sentence The words of a sentence (UTF8).
     * @param disambiguate Reduce the number of possible analysis by applying disambiguation.
     * @param guess Try to guess unknown words.
     * @param phonetic Add phonetic markup.
     * @param propername Perform addigional proper name analysis.
     */
    std::vector<WordAnalysis> analyze(
        StringVector const& sentence,
        const bool disambiguate,
        const bool guess,
        const bool phonetic,
        const bool propername);

    /**
     * Disambiguate a sentence that is already analyzed.
     * This method is a single step in a more complex
     * disambiguation method.
     * When you don't care or don't know what it means, just
     * use analyze method with disambiguate=true .
     * @param sentence The morphologically analyzed word vector,
     */
    std::vector<WordAnalysis> disambiguate(std::vector<WordAnalysis> &sentence);

    /**
     * Spellcheck words.
     * @param sentence The words of a sentence (UTF8).
     * @param suggest When true, then add suggestions to the result.
     */
    SpellingSuggestions spellcheck(
        StringVector const& sentence,
        const bool suggest);

    /**
     * Synthesize words.
     *
     * @param guess Use heuristics with unkown words.
     * @param phon Add phonetic markup.
     */
    StringVector synthesize(
        const std::string lemma,
        const std::string form,
        const std::string partofspeech,
        const std::string hint,
        const bool guess,
        const bool phon);

private:
    CLinguistic linguistic;
    CDisambiguator disambiguator;
};


// syllabification functions
Syllables syllabify(std::string word);
SentenceSyllables syllabifySentence(const StringVector& sentence);

#endif
