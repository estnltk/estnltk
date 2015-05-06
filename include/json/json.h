#if !defined (_JSON_H_ak75qpwoehrfq38456fasdjfhe7_)
#define _JSON_H_ak75qpwoehrfq38456fasdjfhe7_

#include "fsc.h"

class CJSONException : public CFSTextualException {
public:
	CJSONException(const FSTCHAR *pszText) : CFSTextualException(pszText) { }
};

class CJSONReader {
public:
	CJSONReader(CFSStream &Stream) : m_Stream(Stream) { }

	CFSVar Read();

	static bool KeyMatch(const CFSAString &szKey, const CFSAString &szPattern);

protected:
	virtual void OnValReadStart(const CFSAString &/*szKey*/) { }
	virtual void OnValReadEnd(const CFSAString &/*szKey*/, CFSVar &/*Data*/) { }

	CFSVar ReadVal(const CFSAString &szKeyPath);
	CFSAString ReadKey();
	CFSAString ReadString();
	CFSAString ReadText();
	CFSVar ReadNumber();
	CFSVar ReadConst();

	bool GetChar(bool bSkipWhitespace=false);

protected:
	CFSStream &m_Stream;
	char m_cCh;
	int m_iCollectData;
};

class CJSONWriter {
public:
	CJSONWriter(CFSStream &Stream) : m_Stream(Stream) {
		m_Comma.AddItem(COMMA_NO);
	}

	void Key(const CFSAString &szStr);

	void Val(const CFSVar &Var);
	void IntVal(INTPTR iInt);
	void FloatVal(double dFloat);
	void BoolVal(bool bBool);
	void StringVal(const CFSAString &szStr);
	void NullVal();

	void ObjectStart();
	void ObjectEnd();
	void ArrayStart();
	void ArrayEnd();

	void Text(const CFSAString &szStr);

protected:
	enum { COMMA_NO, COMMA_KEY, COMMA_VAL };

	INTPTR GetLevel() {
		return m_Comma.GetSize()-1;
	}
	void Comma();
	void Indent();

protected:
	CFSIntArray m_Comma;
	CFSStream &m_Stream;
};

#endif // _JSON_H_ak75qpwoehrfq38456fasdjfhe7_
