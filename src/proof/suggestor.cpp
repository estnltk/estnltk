// Suggestor.cpp: implementation of the CSuggestor class.
//
//////////////////////////////////////////////////////////////////////

#include "fsc.h"
#include "pttype.h"
#include "suggestor.h"

static const CFSWString szInsertLettersBeg=L"KPSTVLMRAHNEJIO\x00dc" L"DFUB\x00d5" L"G";
static const CFSWString szInsertLetters=L"AEISTLUNKMODRVGHJP\x00c4\x00d5" L"B\x00dc\x00d6";
static const CFSWString szEstAlphas=L"ABCDEFGHIJKLMNOPQRSTUVWXYZ\x00d5\x00c4\x00d6\x00dc\x0160\x017d";

/*static CFSWString szQuotLeft=  FSWSTR("\x2018\x2019\x201a\x2039\x0027");
static CFSWString szQuotRight= FSWSTR("\x2018\x2019\x203a\x0027");
static CFSWString szDQuotLeft= FSWSTR("\x201c\x201d\x201e\x00ab\x0022");
static CFSWString szDQuotRight=FSWSTR("\x201c\x201d\x00bb\x0022");
static CFSWString szAllQuot=szQuotLeft+szQuotRight+szDQuotLeft+szDQuotRight;*/

struct __CChangeLetters{
	const FSWCHAR m_cFrom;
	const FSWCHAR *m_lpszTo;
}const ChangeLetters[]={
{FSWSTR('\x41'), FSWSTR("\xc4\x45\x53")}, {FSWSTR('\x42'), FSWSTR("\x50\x4e\x56\x47\x48")}, {FSWSTR('\x43'), FSWSTR("\x4b\x44\x56")}, {FSWSTR('\x44'), FSWSTR("\x54\x45\x53\x52")}, {FSWSTR('\x45'), FSWSTR("\x41\x53\x44\x52")}, {FSWSTR('\x46'), FSWSTR("\x56\x54\x44\x52\x47")}, {FSWSTR('\x47'), FSWSTR("\x4b\x4a\x48\x17d\x54\x56\x42")}, {FSWSTR('\x48'), FSWSTR("\x55\x4e\x47\x4a\x42")}, {FSWSTR('\x49'), FSWSTR("\x4a\xdc\x55\x4b\x4f")}, {FSWSTR('\x4a'), FSWSTR("\x49\x47\x17d\x55\x4e\x4b\x4d\x48")}, 
{FSWSTR('\x4b'), FSWSTR("\x47\x48\x49\x4c\x4d\x4f")}, {FSWSTR('\x4c'), FSWSTR("\x4b\x4f\x50\xd6")}, {FSWSTR('\x4d'), FSWSTR("\x4e\x4b\x4a")}, {FSWSTR('\x4e'), FSWSTR("\x4d\x48\x4a\x42")}, {FSWSTR('\x4f'), FSWSTR("\xd5\xd6\x55\x49\x4c\x4b\x50")}, {FSWSTR('\x50'), FSWSTR("\x42\x4c\x4f\xdc\xd6")}, {FSWSTR('\x51'), FSWSTR("\x41")}, {FSWSTR('\x52'), FSWSTR("\x45\x54\x44")}, {FSWSTR('\x53'), FSWSTR("\x160\x5a\x41\x45\x44")}, {FSWSTR('\x54'), FSWSTR("\x44\x52\x47")}, 
{FSWSTR('\x55'), FSWSTR("\xdc\x4f\x49\x48\x4a")}, {FSWSTR('\x56'), FSWSTR("\x46\x47\x42")}, {FSWSTR('\x57'), FSWSTR("\x56\x41\x45\x53")}, {FSWSTR('\x58'), FSWSTR("\x53\x44")}, {FSWSTR('\x59'), FSWSTR("\xdc\x54\x55\x47\x48")}, {FSWSTR('\x5a'), FSWSTR("\x17d\x53\x41")}, {FSWSTR('\xc0'), FSWSTR("\xc4\x41")}, {FSWSTR('\xc1'), FSWSTR("\xc4\x41")}, {FSWSTR('\xc2'), FSWSTR("\xc4\x41")}, {FSWSTR('\xc3'), FSWSTR("\xc4\x41")}, 
{FSWSTR('\xc4'), FSWSTR("\x41\xd5\xdc\xd6")}, {FSWSTR('\xc5'), FSWSTR("\xc4\x41")}, {FSWSTR('\xc6'), FSWSTR("\xc4\x41\x45")}, {FSWSTR('\xc7'), FSWSTR("\x43")}, {FSWSTR('\xc8'), FSWSTR("\x45")}, {FSWSTR('\xc9'), FSWSTR("\x45")}, {FSWSTR('\xca'), FSWSTR("\x45")}, {FSWSTR('\xcb'), FSWSTR("\x45")}, {FSWSTR('\xcc'), FSWSTR("\x49")}, {FSWSTR('\xcd'), FSWSTR("\x49")}, 
{FSWSTR('\xce'), FSWSTR("\x49")}, {FSWSTR('\xcf'), FSWSTR("\x49")}, {FSWSTR('\xd0'), FSWSTR("\x44")}, {FSWSTR('\xd1'), FSWSTR("\x4e")}, {FSWSTR('\xd2'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\xd3'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\xd4'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\xd5'), FSWSTR("\xd6\x4f\xc4\xdc")}, {FSWSTR('\xd6'), FSWSTR("\xd5\x4f\x4c\x50\xc4\xdc")}, {FSWSTR('\xd8'), FSWSTR("\xd5\xd6\x4f")}, 
{FSWSTR('\xd9'), FSWSTR("\xdc\x55")}, {FSWSTR('\xda'), FSWSTR("\xdc\x55")}, {FSWSTR('\xdb'), FSWSTR("\xdc\x55")}, {FSWSTR('\xdc'), FSWSTR("\x55\x50\xc4\xd5\xd6")}, {FSWSTR('\xdd'), FSWSTR("\x59")}, {FSWSTR('\x100'), FSWSTR("\xc4\x41")}, {FSWSTR('\x102'), FSWSTR("\xc4\x41")}, {FSWSTR('\x104'), FSWSTR("\xc4\x41")}, {FSWSTR('\x106'), FSWSTR("\x43")}, {FSWSTR('\x108'), FSWSTR("\x43")}, 
{FSWSTR('\x10a'), FSWSTR("\x43")}, {FSWSTR('\x10c'), FSWSTR("\x43")}, {FSWSTR('\x10e'), FSWSTR("\x44")}, {FSWSTR('\x110'), FSWSTR("\x44")}, {FSWSTR('\x112'), FSWSTR("\x45")}, {FSWSTR('\x114'), FSWSTR("\x45")}, {FSWSTR('\x116'), FSWSTR("\x45")}, {FSWSTR('\x118'), FSWSTR("\x45")}, {FSWSTR('\x11a'), FSWSTR("\x45")}, {FSWSTR('\x11c'), FSWSTR("\x47")}, 
{FSWSTR('\x11e'), FSWSTR("\x47")}, {FSWSTR('\x120'), FSWSTR("\x47")}, {FSWSTR('\x122'), FSWSTR("\x47")}, {FSWSTR('\x124'), FSWSTR("\x48")}, {FSWSTR('\x126'), FSWSTR("\x48")}, {FSWSTR('\x128'), FSWSTR("\x49")}, {FSWSTR('\x12a'), FSWSTR("\x49")}, {FSWSTR('\x12c'), FSWSTR("\x49")}, {FSWSTR('\x12e'), FSWSTR("\x49")}, {FSWSTR('\x130'), FSWSTR("\x49")}, 
{FSWSTR('\x132'), FSWSTR("\x49\x4a")}, {FSWSTR('\x134'), FSWSTR("\x4a")}, {FSWSTR('\x136'), FSWSTR("\x4b")}, {FSWSTR('\x138'), FSWSTR("\x4b")}, {FSWSTR('\x139'), FSWSTR("\x4c")}, {FSWSTR('\x13b'), FSWSTR("\x4c")}, {FSWSTR('\x13d'), FSWSTR("\x4c")}, {FSWSTR('\x13f'), FSWSTR("\x4c")}, {FSWSTR('\x141'), FSWSTR("\x4c")}, {FSWSTR('\x143'), FSWSTR("\x4e")}, 
{FSWSTR('\x145'), FSWSTR("\x4e")}, {FSWSTR('\x147'), FSWSTR("\x4e")}, {FSWSTR('\x149'), FSWSTR("\x4e")}, {FSWSTR('\x14a'), FSWSTR("\x4e")}, {FSWSTR('\x14c'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x14e'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x150'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x152'), FSWSTR("\x43\x45\xd5\xd6\x4f")}, {FSWSTR('\x154'), FSWSTR("\x52")}, {FSWSTR('\x156'), FSWSTR("\x52")}, 
{FSWSTR('\x158'), FSWSTR("\x52")}, {FSWSTR('\x15a'), FSWSTR("\x160\x53")}, {FSWSTR('\x15c'), FSWSTR("\x160\x53")}, {FSWSTR('\x15e'), FSWSTR("\x160\x53")}, {FSWSTR('\x160'), FSWSTR("\x53\x17d")}, {FSWSTR('\x162'), FSWSTR("\x54")}, {FSWSTR('\x164'), FSWSTR("\x54")}, {FSWSTR('\x166'), FSWSTR("\x54")}, {FSWSTR('\x168'), FSWSTR("\xdc\x55")}, {FSWSTR('\x16a'), FSWSTR("\xdc\x55")}, 
{FSWSTR('\x16c'), FSWSTR("\xdc\x55")}, {FSWSTR('\x16e'), FSWSTR("\xdc\x55")}, {FSWSTR('\x170'), FSWSTR("\xdc\x55")}, {FSWSTR('\x172'), FSWSTR("\xdc\x55")}, {FSWSTR('\x174'), FSWSTR("\x57")}, {FSWSTR('\x176'), FSWSTR("\x59")}, {FSWSTR('\x178'), FSWSTR("\x59")}, {FSWSTR('\x179'), FSWSTR("\x17d\x5a")}, {FSWSTR('\x17b'), FSWSTR("\x17d\x5a")}, {FSWSTR('\x17d'), FSWSTR("\x5a\x160")}, 
{FSWSTR('\x192'), FSWSTR("\x46")}, {FSWSTR('\x1a0'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1af'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1cd'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1cf'), FSWSTR("\x49")}, {FSWSTR('\x1d1'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1d3'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1d5'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1d7'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1d9'), FSWSTR("\xdc\x55")}, 
{FSWSTR('\x1db'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1fa'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1fb'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1fc'), FSWSTR("\xc4\x41\x45")}, {FSWSTR('\x1fe'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x386'), FSWSTR("\xc4\x41")}, {FSWSTR('\x388'), FSWSTR("\x45")}, {FSWSTR('\x389'), FSWSTR("\x48")}, {FSWSTR('\x38a'), FSWSTR("\x49")}, {FSWSTR('\x38c'), FSWSTR("\xd5\xd6\x4f")}, 
{FSWSTR('\x38e'), FSWSTR("\x59")}, {FSWSTR('\x391'), FSWSTR("\xc4\x41")}, {FSWSTR('\x392'), FSWSTR("\x42")}, {FSWSTR('\x395'), FSWSTR("\x45")}, {FSWSTR('\x396'), FSWSTR("\x17d\x5a")}, {FSWSTR('\x397'), FSWSTR("\x48")}, {FSWSTR('\x399'), FSWSTR("\x49")}, {FSWSTR('\x39a'), FSWSTR("\x4b")}, {FSWSTR('\x39b'), FSWSTR("\xc4\x41")}, {FSWSTR('\x39c'), FSWSTR("\x4d")}, 
{FSWSTR('\x39d'), FSWSTR("\x4e")}, {FSWSTR('\x39f'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x3a1'), FSWSTR("\x50")}, {FSWSTR('\x3a4'), FSWSTR("\x54")}, {FSWSTR('\x3a5'), FSWSTR("\x59")}, {FSWSTR('\x3a7'), FSWSTR("\x58")}, {FSWSTR('\x3aa'), FSWSTR("\x49")}, {FSWSTR('\x3ab'), FSWSTR("\x59")}, {FSWSTR('\x3ba'), FSWSTR("\x4b")}, {FSWSTR('\x401'), FSWSTR("\x45")}, 
{FSWSTR('\x405'), FSWSTR("\x160\x53")}, {FSWSTR('\x406'), FSWSTR("\x49")}, {FSWSTR('\x407'), FSWSTR("\x49")}, {FSWSTR('\x408'), FSWSTR("\x4a")}, {FSWSTR('\x40a'), FSWSTR("\x48")}, {FSWSTR('\x40c'), FSWSTR("\x4b")}, {FSWSTR('\x40e'), FSWSTR("\x59")}, {FSWSTR('\x410'), FSWSTR("\xc4\x41")}, {FSWSTR('\x412'), FSWSTR("\x42")}, {FSWSTR('\x415'), FSWSTR("\x45")}, 
{FSWSTR('\x41a'), FSWSTR("\x4b")}, {FSWSTR('\x41c'), FSWSTR("\x4d")}, {FSWSTR('\x41d'), FSWSTR("\x48")}, {FSWSTR('\x41e'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x420'), FSWSTR("\x50")}, {FSWSTR('\x421'), FSWSTR("\x43")}, {FSWSTR('\x422'), FSWSTR("\x54")}, {FSWSTR('\x423'), FSWSTR("\x59")}, {FSWSTR('\x425'), FSWSTR("\x58")}, {FSWSTR('\x427'), FSWSTR("\x59")}, 
{FSWSTR('\x1e80'), FSWSTR("\x57")}, {FSWSTR('\x1e82'), FSWSTR("\x57")}, {FSWSTR('\x1e84'), FSWSTR("\x57")}, {FSWSTR('\x1ea0'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1ea2'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1ea4'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1ea6'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1ea8'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eaa'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eac'), FSWSTR("\xc4\x41")}, 
{FSWSTR('\x1eae'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eb0'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eb2'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eb4'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eb6'), FSWSTR("\xc4\x41")}, {FSWSTR('\x1eb8'), FSWSTR("\x45")}, {FSWSTR('\x1eba'), FSWSTR("\x45")}, {FSWSTR('\x1ebc'), FSWSTR("\x45")}, {FSWSTR('\x1ebe'), FSWSTR("\x45")}, {FSWSTR('\x1ec0'), FSWSTR("\x45")}, 
{FSWSTR('\x1ec2'), FSWSTR("\x45")}, {FSWSTR('\x1ec4'), FSWSTR("\x45")}, {FSWSTR('\x1ec6'), FSWSTR("\x45")}, {FSWSTR('\x1ec8'), FSWSTR("\x49")}, {FSWSTR('\x1eca'), FSWSTR("\x49")}, {FSWSTR('\x1ecc'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ece'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ed0'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ed2'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ed4'), FSWSTR("\xd5\xd6\x4f")}, 
{FSWSTR('\x1ed6'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ed8'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1eda'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1edc'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ede'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ee0'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ee2'), FSWSTR("\xd5\xd6\x4f")}, {FSWSTR('\x1ee4'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1ee6'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1ee8'), FSWSTR("\xdc\x55")}, 
{FSWSTR('\x1eea'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1eec'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1eee'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1ef0'), FSWSTR("\xdc\x55")}, {FSWSTR('\x1ef2'), FSWSTR("\x59")}, {FSWSTR('\x1ef4'), FSWSTR("\x59")}, {FSWSTR('\x1ef6'), FSWSTR("\x59")}, {FSWSTR('\x1ef8'), FSWSTR("\x59")}, 
};

struct __CChangeStrings{
	const FSWCHAR *m_lpszFrom;
	const FSWCHAR *m_lpszTo;
}const ChangeStrings[]={
	{FSWSTR("SH"),			FSWSTR("\x0160")},
	{FSWSTR("ZH"),			FSWSTR("\x017d")},
	{FSWSTR("X"),			FSWSTR("KS")},
	{FSWSTR("F"),			FSWSTR("HV")},
	{FSWSTR("HV"),			FSWSTR("F")},
	{FSWSTR("FF"),			FSWSTR("HV")},
	{FSWSTR("MB"),			FSWSTR("MM")},
	{FSWSTR("\x00c4\x00c4"),FSWSTR("EA")},
	{FSWSTR("G"),			FSWSTR("D\x017d")},
	{FSWSTR("D\x017d"),		FSWSTR("G")},
	{FSWSTR("J"),			FSWSTR("D\x017d")},
	{FSWSTR("D\x017d"),		FSWSTR("J")},
	{FSWSTR("DATA"),		FSWSTR("TADA")},
	{FSWSTR("TADA"),		FSWSTR("DATA")},
	{FSWSTR("DITE"),		FSWSTR("TIDE")},
	{FSWSTR("IKUTE"),		FSWSTR("IKE")},
};

struct __CChangeStrings
const ChangeStringsEnd[]={
	{FSWSTR("SI"),			FSWSTR("SEID")},
	{FSWSTR("SI"),			FSWSTR("SID")},
	{FSWSTR("SEID"),		FSWSTR("SI")},
	{FSWSTR("SEID"),		FSWSTR("SID")},
	{FSWSTR("SID"),			FSWSTR("SI")},
	{FSWSTR("SID"),			FSWSTR("SEID")},
	{FSWSTR("IKUID"),		FSWSTR("IKKE")},
	{FSWSTR("TEID"),		FSWSTR("TE")},
	{FSWSTR("UIM"),			FSWSTR("EM")},
};

struct __CChangeStrings
const ChangeStringsMultiple[]={
	{FSWSTR("O~"),			FSWSTR("\x00d5")},
	{FSWSTR("A\""),			FSWSTR("\x00c4")},
	{FSWSTR("O\""),			FSWSTR("\x00d6")},
	{FSWSTR("U\""),			FSWSTR("\x00dc")},
	{FSWSTR("S^"),			FSWSTR("\x0160")},
	{FSWSTR("Z^"),			FSWSTR("\x017d")},
};

static const FSWCHAR *__SuggestChangeLetters(FSWCHAR cChar)
{
	INTPTR ipStart=0;
	INTPTR ipEnd=sizeof(ChangeLetters)/sizeof(__CChangeLetters)-1;
	while (ipStart<=ipEnd){
		INTPTR ipMid=(ipStart+ipEnd)/2;
		if (cChar>ChangeLetters[ipMid].m_cFrom) ipStart=ipMid+1;
		else if (cChar<ChangeLetters[ipMid].m_cFrom) ipEnd=ipMid-1;
		else return ChangeLetters[ipMid].m_lpszTo;
	}
	return 0;
}

static bool FSIsLetterEst(FSWCHAR cChar)
{
	if (!cChar) return false;
	return (FSStrChr(FSWSTR("abcdefghijklmnopqrstuvwxyz\x00f5\x00e4\x00f6\x00fc\x0161\x017e"), FSToLower(cChar))!=0);
}

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CSuggestor::CSuggestor()
{
	m_fTimeOut=0.0f;
}

CSuggestor::~CSuggestor()
{
}

void CSuggestor::GetItem(INTPTR ipPos, CFSWString &szWord, long *plRating) const
{
	szWord=m_Items[ipPos].m_szWord;
	if (plRating) *plRating=m_Items[ipPos].m_lRating;
}

int CSuggestor::CheckAndAdd(const CFSWString &szWord)
{
	if (m_fTimeOut>0 && (CFSTime::Now()-m_TimeStart).GetSeconds()>=m_fTimeOut) return -1;
	if (szWord.IsEmpty()) return -1;
	CFSWString szTemp;
	long lLevel=100;
	if (SpellWord(szWord, szTemp, &lLevel)==SPL_NOERROR && !szTemp.IsEmpty()){
		szTemp=m_Cap.GetCap(szTemp);
		CFSWString szTemp2; long lLevel2;
		if (SpellWord(szTemp, szTemp2, &lLevel2)==SPL_NOERROR){
			SetLevel(GetLevelGroup(lLevel));
			m_Items.AddItem(CSuggestorItem(szTemp, lLevel)); return 0;
		}
	}
	return -1;
}

void CSuggestor::Order()
{
	CFSArraySorter<CFSArray<CSuggestorItem> > Sorter(&m_Items);
	Sorter.GnomeSort(0, m_Items.GetSize()-1);
}

void CSuggestor::RemoveDuplicates()
{
	for (INTPTR ip=0; ip<m_Items.GetSize()-1; ip++){
		for (INTPTR ip2=ip+1; ip2<m_Items.GetSize(); ip2++){
			if (m_Items[ip].m_szWord==m_Items[ip2].m_szWord){
				m_Items.RemoveItem(ip2);
				ip2--;
			}
		}
	}
}

void CSuggestor::RemoveImmoderate()
{
	if (m_Items.GetSize()<=0) return;
	long lMaxRating=GetLevelGroup(m_Items[0].m_lRating);
	for (INTPTR ip=0; ip<m_Items.GetSize(); ip++){
		if (GetLevelGroup(m_Items[ip].m_lRating)>lMaxRating){
			m_Items.RemoveItem(ip); ip--;
		}
	}
}

long CSuggestor::GetLevelGroup(long lLevel) const
{
	if (lLevel<=3) return 3;
	if (lLevel<=5) return 5;
	return 100;
}

void CSuggestor::MultiReplace(const CFSWString &szWord, INTPTR ipStartPos)
{
	if (ipStartPos>0) CheckAndAdd(szWord);
	INTPTR ipLength=szWord.GetLength();
	for (; ipStartPos<ipLength; ipStartPos++){
		for (INTPTR ip=0; ip<(INTPTR)(sizeof(ChangeStringsMultiple)/sizeof(__CChangeStrings)); ip++){
			if (szWord.ContainsAt(ipStartPos, ChangeStringsMultiple[ip].m_lpszFrom)){
				MultiReplace(szWord.Left(ipStartPos)+ChangeStringsMultiple[ip].m_lpszTo+szWord.Mid(ipStartPos+FSStrLen(ChangeStringsMultiple[ip].m_lpszFrom)), ipStartPos+FSStrLen(ChangeStringsMultiple[ip].m_lpszTo));
			}
		}
	}
}

int CSuggestor::Suggest(const CFSWString &szWord, bool bStartSentence){
	m_TimeStart=CFSTime::Now();
	m_Items.Cleanup();

	m_Cap.SetCap(szWord);
	if (bStartSentence && m_Cap.GetCapMode()==CFSStrCap<CFSWString>::CAP_LOWER) {
		m_Cap.SetCapMode(CFSStrCap<CFSWString>::CAP_INITIAL);
	}

	CFSWString szWordHigh=szWord.ToUpper();
	INTPTR ipWordLength=szWordHigh.GetLength();
	CFSWString szTemp;
	INTPTR i, j;
	long lLevel=100;
	SetLevel(lLevel);

	// Case problems & change list
	i=SpellWord(szWordHigh, szTemp, &lLevel);
	if ((i==SPL_NOERROR || i==SPL_CHANGEONCE) && !szTemp.IsEmpty()){
		SetLevel(GetLevelGroup(lLevel));
		m_Items.AddItem(CSuggestorItem(szTemp, lLevel));
	}
	else SetLevel(5);
	
	// Abbrevations
	// !!! Unimplemented

	// Quotes
/*	if (ipWordLength>=2 && 
		(szAllQuot.Find(szWordHigh[0])>=0 || szAllQuot.Find(szWordHigh[ipWordLength-1])>=0))
	{
		szTemp=szWordHigh;
		int iPos;
		if (szAllQuot.Find(szTemp[0])>=0){
			if (szQuotLeft.Find(szTemp[0])>=0) { }
			else if ((iPos=szQuotRight.Find(szTemp[0]))>=0) { szTemp[0]=szQuotLeft[iPos]; }
			else if (szDQuotLeft.Find(szTemp[0])>=0) { }
			else if ((iPos=szDQuotRight.Find(szTemp[0]))>=0) { szTemp[0]=szDQuotLeft[iPos]; }

			if (szAllQuot.Find(szTemp[ipWordLength-1])>=0) { szTemp[ipWordLength-1]=(szQuotRight+szDQuotRight)[(szQuotLeft+szDQuotLeft).Find(szTemp[0])];
		}
		else{
			if (szQuotRight.Find(szTemp[ipWordLength-1])>=0) { }
			else if ((iPos=szQuotLeft.Find(szTemp[ipWordLength-1]))>=0) { szTemp[ipWordLength-1]=szQuotRight[iPos]; }
			else if (szDQuotRight.Find(szTemp[ipWordLength-1])>=0) { }
			else if ((iPos=szDQuotLeft.Find(szTemp[ipWordLength-1]))>=0) { szTemp[ipWordLength-1]=szDQuotRight[iPos]; }
		}
		CheckAndAdd(szTemp);
	}*/

	// Add space
	for (i=1; i<ipWordLength-1; i++){
		static CFSWString szPunktuation=FSWSTR(".:,;!?");
		if (szPunktuation.Find(szWord[i])>=0){
			long lLevel1, lLevel2;
			CFSWString szTemp1, szTemp2;
			if (SpellWord(szWord.Left(i+1), szTemp1, &lLevel1)==SPL_NOERROR &&
				SpellWord(szWord.Mid(i+1), szTemp2, &lLevel2)==SPL_NOERROR)
			{
				m_Items.AddItem(CSuggestorItem(szWord.Left(i+1)+L' '+szWord.Mid(i+1), FSMAX(lLevel1, lLevel2)));
			}
		}
	}

	// Delete following blocks: le[nnu][nnu]jaam
	for (i=2; i<=3; i++){
		for (j=0; j<ipWordLength-i-i; j++){
			if (memcmp((const FSWCHAR *)szWordHigh+j, (const FSWCHAR *)szWordHigh+j+i, i*sizeof(FSWCHAR))==0){
				szTemp=szWordHigh.Left(j)+szWordHigh.Mid(j+i);
				CheckAndAdd(szTemp);
			}
		}
	}

	// Change following letters: abb -> aab & aab -> abb
	for (i=1; i<ipWordLength-1; i++){
		if (szWordHigh[i]==szWordHigh[i+1]){
			szTemp=szWordHigh;
			szTemp[i]=szTemp[i-1];
			if (FSIsLetterEst(szTemp[i])) CheckAndAdd(szTemp);
		}
		else if (szWordHigh[i]==szWordHigh[i-1]){
			szTemp=szWordHigh;
			szTemp[i]=szTemp[i+1];
			if (FSIsLetterEst(szTemp[i])) CheckAndAdd(szTemp);
		}
	}

	// Exchange letters: van[na]ema -> van[an]ema
	szTemp=szWordHigh;
	for (i=1; i<ipWordLength; i++){
		if (szTemp[i]!=szTemp[i-1]){
			FSWCHAR ch=szTemp[i];
			szTemp[i]=szTemp[i-1];
			szTemp[i-1]=ch;
			CheckAndAdd(szTemp);
			szTemp[i-1]=szTemp[i];
			szTemp[i]=ch;
		}
	}

	// Change blocks
	for (i=0; i<ipWordLength; i++){
		for (j=0; j<(INTPTR)(sizeof(ChangeStrings)/sizeof(__CChangeStrings)); j++){
			if (szWordHigh.ContainsAt(i, ChangeStrings[j].m_lpszFrom)){
				szTemp=szWordHigh.Left(i)+ChangeStrings[j].m_lpszTo+szWordHigh.Mid(i+FSStrLen(ChangeStrings[j].m_lpszFrom));
				CheckAndAdd(szTemp);
			}
		}
	}

	// Change end blocks
	for (i=0; i<(INTPTR)(sizeof(ChangeStringsEnd)/sizeof(__CChangeStrings)); i++){
		if (szWordHigh.EndsWith(ChangeStringsEnd[i].m_lpszFrom)){
			szTemp=szWordHigh.Left(ipWordLength-FSStrLen(ChangeStringsEnd[i].m_lpszFrom))+ChangeStringsEnd[i].m_lpszTo;
			CheckAndAdd(szTemp);
		}
	}

	// Po~o~sas
	MultiReplace(szWordHigh, 0);

	// gi/ki: Kylli[gi]le -> Kyllile[gi]
	for (i=3; i<=6; i++){
		if (i>ipWordLength) break;
		if (memcmp((const FSWCHAR *)szWordHigh+ipWordLength-i, FSWSTR("GI"), 2*sizeof(FSWCHAR))==0){
			szTemp=szWordHigh.Left(ipWordLength-i)+szWordHigh.Mid(ipWordLength-i+2)+FSWSTR("GI");
			CheckAndAdd(szTemp);
			szTemp=szWordHigh.Left(ipWordLength-i)+szWordHigh.Mid(ipWordLength-i+2)+FSWSTR("KI");
			CheckAndAdd(szTemp);
		}
	}

	// Delete letters: van[n]aema -> vanaema
	szTemp=szWordHigh.Mid(1);
	CheckAndAdd(szTemp);
	for (i=0; i<ipWordLength-1; i++){
		if (szTemp[i]!=szWordHigh[i]){
			szTemp[i]=szWordHigh[i];
			CheckAndAdd(szTemp);
		}
	}

	// Change letters from list
	for (i=0; i<ipWordLength; i++){
		const FSWCHAR *lpszTo=__SuggestChangeLetters(szWordHigh[i]);
		if (!lpszTo) continue;
		szTemp=szWordHigh;
		for (; lpszTo[0]; lpszTo++){
			szTemp[i]=lpszTo[0];
			CheckAndAdd(szTemp);
		}
	}
	
	// Insert letters to word body
	for (i=1; i<ipWordLength; i++){
		szTemp=szWordHigh.Left(i)+FSWSTR(' ')+szWordHigh.Mid(i);
		for (j=0; szInsertLetters[j]; j++){
			szTemp[i]=szInsertLetters[j];
			CheckAndAdd(szTemp);
		}
	}

	// Insert letters to the beginning
	szTemp=CFSWString(FSWSTR(" "))+szWordHigh;
	for (i=0; szInsertLettersBeg[i]; i++){
		if (szTemp[1]==szInsertLettersBeg[i]) continue;
		szTemp[0]=szInsertLettersBeg[i];
		CheckAndAdd(szTemp);
	}

	// Try apostrophe for names
	if (szWord[0]!=szWordHigh[0] && szWordHigh.Find('\'')<0){
		for (i=0; i<5; i++){
			if (i>=ipWordLength) break;
			szTemp=szWordHigh.Left(ipWordLength-i)+L'\''+szWordHigh.Mid(ipWordLength-i);
			CheckAndAdd(szTemp);
		}
	}

	Order();
	RemoveImmoderate();
	RemoveDuplicates();
	return 0;
}
