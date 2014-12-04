// linguistic.h: interface for the CFSLinguistic class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_)
#define AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_

class CLinguisticException : public CFSException {
public:
	enum eMajor { MAINDICT, SPELLER, HYPHENATOR, THESAURUS };
	enum eMinor { UNDEFINED, OPEN, READ };

	CLinguisticException(long lMajor, long lMinor=UNDEFINED) : m_lMajor(lMajor), m_lMinor(lMinor) { }

	long m_lMajor, m_lMinor;
};

class CLinguistic  
{
public:
	DECLARE_FSNOCOPY(CLinguistic);

	CLinguistic() : m_Flags(0), m_pMorf(0) { }
	virtual ~CLinguistic() { Close(); }

	void Open(const CFSFileName &FileName);
	void Close();

	void SetFlags(MRF_FLAGS_BASE_TYPE Flags);
	void SetLevel(long lLevel);

	SPLRESULT SpellWord(const CFSWString &szWord, CFSWString *pszRealWord=0, long *pLevel=0);
	void SpellWords(const CPTWordArray &Words, CFSArray<SPLRESULT> &Results);

protected:
	MRF_FLAGS_BASE_TYPE m_Flags;

	ETMRFA *m_pMorf;
};

#endif // !defined(AFX_FSLINGUISTIC_H__CC620036_8AA0_4BF3_9072_9F585113516F__INCLUDED_)
