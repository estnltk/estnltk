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
#if !defined(AFX_DISAMBIGUATOR_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_)
#define AFX_DISAMBIGUATOR_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_

#include "morphinfo.h"

class CDisambiguatorException : public CFSException {
public:
	enum eMajor { MAINDICT };
	enum eMinor { UNDEFINED, OPEN };

	CDisambiguatorException(long lMajor, long lMinor=UNDEFINED) : m_lMajor(lMajor), m_lMinor(lMinor) { }

	CFSString GetText() const;

	long m_lMajor, m_lMinor;
};

class CDisambiguator {
public:
	CDisambiguator() : m_pDisambiguator(0) {}
	virtual ~CDisambiguator() { Close(); }

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
* Disambiguates morphological analysis of a sentence
* @param[in] Analysis Morphological analysis of full sentense.
* @return Disambiguated analysis.
*/
	CFSArray<CMorphInfos> Disambiguate(const CFSArray<CMorphInfos> &Analysis);

protected:
	ET3 *m_pDisambiguator;
	MRF2YH2MRF m_TagConverter;
};

#endif
