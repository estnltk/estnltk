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
