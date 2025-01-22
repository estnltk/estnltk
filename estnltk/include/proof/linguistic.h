/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
// linguistic.h: interface for the CFSLinguistic class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_)
#define AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_

#include "morphinfo.h"

class CLinguisticException : public CFSException {
public:
	enum eMajor { MAINDICT };
	enum eMinor { UNDEFINED, OPEN };

	CLinguisticException(long lMajor, long lMinor=UNDEFINED) : m_lMajor(lMajor), m_lMinor(lMinor) { }

	CFSString GetText() const;

	long m_lMajor, m_lMinor;
};

class CLinguistic
{
public:
	DECLARE_FSNOCOPY(CLinguistic);

	CLinguistic() :
		m_bStem(false), // TV-2024.02.03
		m_bAbbrevations(true), m_bRomanNumerals(true),
		m_bGuess(false), m_bPhonetic(false),
		m_bProperName(false), m_bCombineWords(false),
		m_pMorph(0) { }
	virtual ~CLinguistic() { Close(); }

/**
* Initiates linguistic. Throws exception on error.
* @param[in] FileName Path to lexicon file.
*/
	void Open(const CFSFileName &FileName);

/**
* De-initiates linguistic and frees up resources.
*/
	void Close();

/**
* Checks spelling of a single word. Throws exception on error.
* @param[in] szWord Word to check.
* @return SPL_NOERROR if Word is correct.
*/
	SPLRESULT SpellWord(const CFSWString &szWord);

/**
* Checks spelling of word sequence. Has primitive knowledge of phrases like New York.
* Throws exception on error.
* @param[in] Words Words to check.
* @return list of results per work. SPL_NOERROR if specific word is correct. Result size is equal to word list size.
*/
	CFSArray<SPLRESULT> SpellWords(const CPTWordArray &Words);

/**
* Suggests replacements for misspelled words.
* Throws exception on error.
* @param[in] szWord Word to suggest upon.
* @param[in] bStartSentence true if the word is the first in the sentence.
* @return list of suggestions ordered by likelyhood.
*/
	CFSWStringArray Suggest(const CFSWString &szWord, bool bStartSentence=false);

/**
* Morphologically analyzes a word.
* Throws exception on error.
* @param[in] szWord Word to analyze.
* @return list of morphological information.
*/
	CFSArray<CMorphInfo> Analyze(const CFSWString &szWord);

/**
* Morphologically analyzes a sentence. Has primitive knowledge of phrases like New York.
* Throws exception on error.
* @param[in] Words Words to analyze.
* @return list of morphological information per word.
*/
	CFSArray<CMorphInfos> AnalyzeSentence(const CPTWordArray &Words);

/**
* Synthesizes a word according to provided morphological information.
* Throws exception on error.
* @param[in] MorphInfo Morphological information about the word.
* @param[in] szHint Paradigm hint for a word (sg g) eg. palgi/palga
* @return list of morphologically detailed generated words. Form a real word by combining m_szRoot+m_szEnding+m_szClitic;
*/
	CFSArray<CMorphInfo> Synthesize(const CMorphInfo &MorphInfo, CFSWString szHint);

public:
/** TV-2024.02.03
* true: morf analüüsi väljundis tüvi; false: morf analüüsi väljundis lemma, vaikeväärtus
* Applies to Analyze
*/
	bool m_bStem;

/**
* Analyze abbrevations stricktly. Applies to Spell, Analyze
*/
	bool m_bAbbrevations;

/**
*  Analyze Roman numerals. Applies to Spell, Analyze
*/
	bool m_bRomanNumerals;

/**
* Guess words. Applier to Analyze, Synthesize
*/
	bool m_bGuess;

/**
* Generates phenetic transcription. Applies to Analyze, Synthesize
*/
	bool m_bPhonetic;

/**
* Executes additional name analysis, useful for disambiguator. Applies to Analyze, requires full sentense
*/
	bool m_bProperName;

/**
* Combines words that should be considered as one entity. Applies to Analyze, Spell, requires full sentense
*/
	bool m_bCombineWords;

protected:
	ETMRFAS *m_pMorph;
};

#endif // !defined(AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_)