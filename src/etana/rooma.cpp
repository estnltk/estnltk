
#include "post-fsc.h"
#include "rooma.h"

struct CRomanNr::Rule CRomanNr::m_Rules[9]={
	{{1, 0}},
	{{1, 1, 0}},
	{{1, 1, 1, 0}},
	{{1, 2, 0}},
	{{2, 0}},
	{{2, 1, 0}},
	{{2, 1, 1, 0}},
	{{2, 1, 1, 1, 0}},
	{{1, 3, 0}},
};

void CRomanNr::Reset(int iRomanIdx)
{
	memset(m_bUsed, 0, sizeof(m_bUsed));
	m_iRulePos=0;
	m_iMinIdx=iRomanIdx;
}

bool CRomanNr::IsAnyRuleOk(int iRomanIdx)
{
	if ((iRomanIdx>>1)>=(m_iMinIdx>>1)) return false;
	for (int i=0; i<9; i++){
		if (!m_bUsed[i] && m_Rules[i].m_Mask[m_iRulePos]==0) return true;
	}
	return false;
}

bool CRomanNr::CheckRule(int iRomanIdx){
	int i;
	int iRuleCode=(iRomanIdx&1 ? 2 : 1); // 2-VLD | 1=IXCM

	if (m_iLastIdx>=0){
		if ((iRomanIdx>>1)<(m_iLastIdx>>1)){
			if (!IsAnyRuleOk(m_iLastIdx)) return false;
			Reset(m_iLastIdx);
		}
		else if ((iRomanIdx>>1)>(m_iLastIdx>>1)){
			if (iRomanIdx>m_iMinIdx) return false;
			iRomanIdx=m_iLastIdx;
			iRuleCode=3;
		}
	}
	bool bFound=0;
	for (i=0; i<9; i++){
		if (!m_bUsed[i]){
			if (m_Rules[i].m_Mask[m_iRulePos]!=iRuleCode) m_bUsed[i]=true;
			else bFound=1;
		}
	}
	if (!bFound) return false;
	m_iRulePos++;
	m_iLastIdx=iRomanIdx;
	return true;
}



bool CRomanNr::IsRomanNr(const char *lpszText)
    {
	CFSAString szText=lpszText;

	if (szText.IsEmpty()) return false;
	// Check for symbols
	const CFSAString szRomans("IVXLCDM");
	szText.MakeUpper();
	szText.TrimLeft(szRomans);
	if (!szText.IsEmpty()) return false;

	// Must have same case
	bool bCase=false;
	szText=lpszText;
	szText.MakeLower();
	if (szText==lpszText) bCase=true;
	szText.MakeUpper();
	if (szText==lpszText) bCase=true;
	if (!bCase) return false;

	// Text is upper, let's remove M-s
	while (!szText.IsEmpty() && szText[0]=='M') szText=szText.Mid(1)
        ;
	if (szText.IsEmpty()) 
        return true;

	// Check against rules
	Reset(100);
	m_iLastIdx=-1;

	for (long l=0; l<szText.GetLength(); l++)
        {
		int iRomanIdx=szRomans.Find(szText[l]);
		if (!CheckRule(iRomanIdx)) 
            return false;
	    }
	return IsAnyRuleOk(0);
    }

bool CRomanNr::IsRomanNr(const FSWCHAR *lpszText)
    {
    CFSWString szText=lpszText;
	if (szText.IsEmpty()) 
        return false;
	szText.MakeUpper();
	const CFSWString szRomans(FSWSTR("IVXLCDM"));
	szText.TrimLeft(szRomans);
	if (!szText.IsEmpty()) 
        return false;
    CFSWString wStr(lpszText);
    CFSAString aStr=FSStrWtoA(wStr);
    return IsRomanNr((const char*)aStr);
    }


/* versioon enne 6. juunit 2002 HJK
#include <ctype.h>
#include <string.h>
#include <stdio.h>
//#include <conio.h>

int ChIsUpperUP(char ch);

struct RRule{
	char used;
	char rule[5];
}RRules[]={
	{0, {1, 0}},
	{0, {1, 1, 0}},
	{0, {1, 1, 1, 0}},
	{0, {1, 2, 0}},
	{0, {2, 0}},
	{0, {2, 1, 0}},
	{0, {2, 1, 1, 0}},
	{0, {2, 1, 1, 1, 0}},
	{0, {1, 3, 0}},
};
char Rnrs[]="IVXLCDM";
int RRulePos, RMinPos, RLastPos;

void RResetUsed(int Pos)
{
	int i;
	for (i=0; i<9; i++)
		RRules[i].used=0;
	RRulePos=0;
	RMinPos=Pos;
}

int RIsAnyRuleOk(int Pos)
{
	int i;
	if ((Pos>>1)>=(RMinPos>>1)) return 0;
	for (i=0; i<9; i++)
		if ((!RRules[i].used)&&(!RRules[i].rule[RRulePos])) return 1;
	return 0;
}

int RGoOn(int Pos)
{
	int RuleCode, found, i;
	if (Pos&1) RuleCode=2;
	else RuleCode=1;
	
	if (RLastPos>=0){
		if ((Pos>>1)<(RLastPos>>1)){
			if (!RIsAnyRuleOk(RLastPos)) return 0;
			RResetUsed(RLastPos);
		}
		else if ((Pos>>1)>(RLastPos>>1)){
			if (Pos>RMinPos) return 0;
			Pos=RLastPos;
			RuleCode=3;
		}
	}

	found=0;
	for (i=0; i<9; i++){
		if (!RRules[i].used){
			if (RRules[i].rule[RRulePos]!=RuleCode){
				RRules[i].used=1;
			}
			else{
				found=1;
			}
		}
	}
	if (!found) return 0;

	RLastPos=Pos;
	RRulePos++;
	return 1;
}

int IsRoman(char *Rom)
{
	int Pos;
	char *ch;
	int up, low, i;
	RLastPos=-1;
	RResetUsed(100);
	up=1; low=0;
	for (ch=Rom; *ch; ch++){
		i=ChIsUpperUP(*ch);
		up&=i;
		low|=i;
	}
	if ((!up)&&(low)) return 0;
	while (toupper(*Rom)=='M') Rom++;
	if (!*Rom) return 1;
	while (*Rom){
		ch=strchr(Rnrs, toupper(*Rom));
		if (!ch) return 0;
		Pos=ch-Rnrs;
		if (!RGoOn(Pos)) return 0;
		Rom++;
	}
	return RIsAnyRuleOk(0);
}
*/
