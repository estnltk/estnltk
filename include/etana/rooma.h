
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


