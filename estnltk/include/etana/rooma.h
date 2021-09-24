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
#if !defined( _ROMANNR_H_ )
#define _ROMANNR_H_

class CRomanNr{

public:
	bool IsRomanNr(const char *lpszText);
	bool IsRomanNr(const FSWCHAR *lpszText);

protected:
	void Reset(int iRomanIdx);
	bool IsAnyRuleOk(int iRomanIdx);
	bool CheckRule(int iRomanIdx);

	bool m_bUsed[9];
	int m_iRulePos;
	int m_iLastIdx, m_iMinIdx;
	static struct Rule{
        unsigned char m_Mask[5]; // *NUX ei tunne vaikimisi BYTE t��pi
	}m_Rules[9];
};

#endif
/* versioon enne 6, juunit 2002 HJK
int IsRoman(char *Rom);
*/


