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
#if !defined _PTWORD_H_
#define _PTWORD_H_

class CPTWord{
public:
	CPTWord() : m_ipStartPos(0) { }
	CPTWord(const CFSWString &szWord, INTPTR ipStartPos=0) : m_szWord(szWord), m_ipStartPos(ipStartPos) { }

	void RemovePunctuation();
	void RemoveHyphens();
	void Trim() { m_ipStartPos+=m_szWord.Trim(); }
	void Trim(const FSWCHAR *lpszTrim) { m_szWord.TrimRight(lpszTrim); m_ipStartPos+=m_szWord.TrimLeft(lpszTrim); }

	CFSWString m_szWord;
	INTPTR m_ipStartPos;
};

typedef CFSArray<CPTWord> CPTWordArray;

void PTWSplitBuffer(const CFSWString &szBuffer, CPTWordArray &Words);

#endif
