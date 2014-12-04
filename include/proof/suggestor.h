// Suggestor.h: interface for the CSuggestor class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SUGGESTOR_H__A6DCC469_2927_40FE_B8E9_01D4395936ED__INCLUDED_)
#define AFX_SUGGESTOR_H__A6DCC469_2927_40FE_B8E9_01D4395936ED__INCLUDED_

class CSuggestorItem{
public:
	CSuggestorItem(const CFSWString &szWord, long lRating) : m_szWord(szWord), m_lRating(lRating) { }
	bool operator < (const CSuggestorItem &Item) const { return m_lRating<Item.m_lRating; }

	CFSWString m_szWord;
	long m_lRating;
};

class CSuggestor  
{
public:
	CSuggestor();
	virtual ~CSuggestor();

	int Suggest(const CFSWString &szWord, bool bStartSentence=false);

	INTPTR GetSize() const { return m_Items.GetSize(); }
	void GetItem(INTPTR ipPos, CFSWString &szWord, long *plRating=0) const;
	void RemoveItem(INTPTR ipPos) { m_Items.RemoveItem(ipPos); }
	
	void SetTimeOut(double fTimeOut) { m_fTimeOut=fTimeOut; }

protected:
	virtual SPLRESULT SpellWord(const CFSWString &szWord, CFSWString &szWordReal, long *pLevel) = 0;
	virtual void SetLevel(long lLevel) = 0;
	
	int CheckAndAdd(const CFSWString &szWord);
	long GetLevelGroup(long lLevel) const;
	
	void MultiReplace(const CFSWString &szWord, INTPTR ipStartPos);

	void Order();
	void RemoveDuplicates();
	void RemoveImmoderate();

	CFSArray<CSuggestorItem> m_Items;
	CFSTime m_TimeStart;
	double m_fTimeOut;
	CFSStrCap<CFSWString> m_Cap;
};

#endif // !defined(AFX_SUGGESTOR_H__A6DCC469_2927_40FE_B8E9_01D4395936ED__INCLUDED_)
