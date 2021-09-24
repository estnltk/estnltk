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
#include "fsc.h"
#include "ptword.h"

void CPTWord::RemovePunctuation()
{
	static const CFSWString szPunctuationStart(
		FSWSTR(".,:;?!*+/=\\")
		FSWSTR("({[<\x00AB-")
		FSWSTR("\x2018\x2019\x201a\x2039\x0027") // Single quotes L
		FSWSTR("\x201c\x201d\x201e\x00ab\x0022") // Double quotes L
	);
	static const CFSWString szPunctuationEnd(
		FSWSTR(".,:;?!*+/=\\\x2026")
		FSWSTR(")}]>\x00BB")
		FSWSTR("\x2018\x2019\x203a\x0027") // Single quotes R
		FSWSTR("\x201c\x201d\x00bb\x0022") // Double quotes R
	);

	m_szWord.TrimRight(szPunctuationEnd);
	m_ipStartPos+=m_szWord.TrimLeft(szPunctuationStart);
}

void CPTWord::RemoveHyphens()
{
	m_szWord.Remove(FSWSTR('\x001F')); // Old soft hyph???
	m_szWord.Remove(FSWSTR('\x00AD')); // Soft hyphen
}

void PTWSplitBuffer(const CFSWString &szBuffer, CPTWordArray &Words)
{
	Words.Cleanup();
	INTPTR ipStartPos=0;
	INTPTR ipPos;
	for (ipPos=0; ipPos<szBuffer.GetLength(); ipPos++) {
		if (FSIsSpace(szBuffer[ipPos])) {
			if (ipPos>ipStartPos) {
				Words.AddItem(CPTWord(szBuffer.Mid(ipStartPos, ipPos-ipStartPos), ipStartPos));
			}
			ipStartPos=ipPos+1;
		}
	}
	if (ipPos>ipStartPos) {
		Words.AddItem(CPTWord(szBuffer.Mid(ipStartPos, ipPos-ipStartPos), ipStartPos));
	}
}
