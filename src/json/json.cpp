#include "json.h"

///////////////////////////////////////////////////////////
// Reader

bool CJSONReader::GetChar(bool bSkipWhitespace)
{
	while (m_Stream.ReadBuf(&m_cCh, 1, false)==1) {
		if (!bSkipWhitespace || !FSIsSpace(m_cCh)) return true;
	}
	m_cCh=0;
	return false;
}

CFSAString CJSONReader::ReadString()
{
	char cQuote=m_cCh;
	CFSAString szStr;
	while (GetChar()) {
		if (m_cCh=='\\') {
			szStr+=m_cCh;
			if (GetChar()) szStr+=m_cCh;
			else break;
		} else if (m_cCh==cQuote) {
			GetChar(true);
			return szStr;
		} else {
			szStr+=m_cCh;
		}
	}
	throw CJSONException(FSTSTR("Missing end of string"));
}

CFSAString CJSONReader::ReadText()
{
	CFSAString szStr;
	for (;;) {
		if (FSIsLetter(m_cCh) || FSIsNumber(m_cCh)) {
			szStr+=m_cCh;
		} else if (m_cCh=='\\') {
			szStr+=m_cCh;
			if (GetChar()) szStr+=m_cCh;
		} else {
			if (FSIsSpace(m_cCh)) GetChar(true);
			break;
		}
		GetChar();
	}
	return szStr;
}

CFSVar CJSONReader::ReadNumber()
{
	CFSAString szStr=m_cCh;
	while (GetChar()) {
		if ((m_cCh>='0' && m_cCh<='9') || m_cCh=='.') {
			szStr+=m_cCh;
		} else {
			if (FSIsSpace(m_cCh)) GetChar(true);
			break;
		}
	}
	if (szStr.Find('.')>=0) {
		return 	strtod(szStr, 0);
	} else{
		return (INTPTR)strtol(szStr, 0, 10);
	}
}

CFSVar CJSONReader::ReadConst()
{
	CFSAString szStr=ReadText();
	if (szStr=="true") return CFSVar(true);
	if (szStr=="false") return CFSVar(true);
	if (szStr=="null") return CFSVar();
	throw CJSONException(CFSString(FSTSTR("Unknown constant '")) + FSStrAtoT(szStr, FSCP_UTF8) + FSTSTR("'"));
}

CFSVar CJSONReader::ReadVal(const CFSAString &szKeyPath)
{
	OnValReadStart(szKeyPath);
	CFSVar Data;

	if (m_cCh=='[') {
		Data.Cast(CFSVar::VAR_ARRAY);
		GetChar(true);
		INTPTR ipPos=0;
		for (;;) {
			if (m_cCh==0) {
				throw CJSONException(FSTSTR("Unexpetcted EOF"));
			} else if (m_cCh==']') {
				GetChar(true);
				break;
			} else if (ipPos>0) {
				if (m_cCh==',') {
					GetChar(true);
				} else {
					throw CJSONException(FSTSTR("Missing ',' in array"));
				}
			}

			CFSAString szKey;
			szKey.Format("%zd", ipPos);
			CFSVar Data1=ReadVal(szKeyPath+"/"+szKey);
			if (m_iCollectData>0) {
				Data[ipPos]=Data1;
			}
			ipPos++;
		}
	} else if (m_cCh=='{') {
		Data.Cast(CFSVar::VAR_MAP);
		GetChar(true);
		INTPTR ipPos=0;
		for (;;) {
			if (m_cCh==0) {
				throw CJSONException(FSTSTR("Unexpetcted EOF"));
			} else if (m_cCh=='}') {
				GetChar(true);
				break;
			} else if (ipPos>0) {
				if (m_cCh==',') {
					GetChar(true);
				} else {
					throw CJSONException(FSTSTR("Missing ',' in map"));
				}
			}

			CFSAString szKey;
			if (m_cCh=='\"' || m_cCh=='\'') {
				szKey=ReadString();
			} else if (FSIsLetter(m_cCh)) {
				szKey=ReadText();
			} else {
				throw CJSONException(FSTSTR("Expected key"));
			}
			if (m_cCh==':') {
				GetChar(true);
			} else {
				throw CJSONException(FSTSTR("Expected ':'"));
			}
			CFSVar Data1=ReadVal(szKeyPath+"/"+szKey);
			if (m_iCollectData>0) {
				Data[szKey]=Data1;
			}
			ipPos++;
		}
	} else if (m_cCh=='\"' || m_cCh=='\'') {
		Data=ReadString();
	} else if ((m_cCh>='0' && m_cCh<='9') || FSStrChr("-+.", m_cCh)) {
		Data=ReadNumber();
	} else if (FSIsLetter(m_cCh)) {
		Data=ReadConst();
	} else if (!m_cCh) {
	} else {
		throw CJSONException(FSTSTR("Unknown value type"));
	}

	OnValReadEnd(szKeyPath, Data);
	return Data;
}

CFSVar CJSONReader::Read()
{
	m_iCollectData=1;
	GetChar(true);
	CFSVar Data=ReadVal("");
	if (m_cCh) throw CJSONException(FSTSTR("Partially parsed file"));
	return Data;
}

bool CJSONReader::KeyMatch(const CFSAString &szKey, const CFSAString &szPattern)
{
	INTPTR ipKey=0;
	INTPTR ipPattern=0;
	for (;; ipKey++, ipPattern++) {
		if (szPattern[ipPattern]=='%') {
			ipPattern++;
			switch (szPattern[ipPattern]) {
				case '%':
					if (szKey[ipKey]!='%') {
						return false;
					}
				break;
				case 'd':
					if (!FSIsNumber(szKey[ipKey])) {
						return false;
					}
					for (; FSIsNumber(szKey[ipKey+1]); ipKey++);
				break;
				default:
					return false;
			}
		} else if (szKey[ipKey]!=szPattern[ipPattern]) {
			return false;
		}
		if (szPattern[ipPattern]==0) {
			return true;
		}
	}
}

///////////////////////////////////////////////////////////
// Writer

void CJSONWriter::Key(const CFSAString &szStr) {
	Comma();
	m_Stream.WriteChar('\"');
	Text(szStr);
	m_Stream.WriteText("\": ");
}

void CJSONWriter::Val(const CFSVar &Var) {
	switch (Var.GetType()) {
		case CFSVar::VAR_EMPTY:
			NullVal();
		break;
		case CFSVar::VAR_INT:
			IntVal(Var.GetInt());
		break;
		case CFSVar::VAR_FLOAT:
			FloatVal(Var.GetFloat());
		break;
		case CFSVar::VAR_BOOL:
			BoolVal(Var.GetBool());
		break;
		case CFSVar::VAR_STRING:
			StringVal(Var.GetAString());
		break;
		case CFSVar::VAR_MAP:
			ObjectStart();
			for (INTPTR ip=0; ip<Var.GetSize(); ip++) {
				CFSAString szKey=Var.GetKey(ip);
				Key(szKey);
				Val(Var[szKey]);
			}
			ObjectEnd();
		break;
		case CFSVar::VAR_ARRAY:
			ArrayStart();
			for (INTPTR ip=0; ip<Var.GetSize(); ip++) {
				Val(Var[ip]);
			}
			ArrayEnd();
		break;
	}
}

void CJSONWriter::IntVal(INTPTR iInt) {
	Comma();
	CFSAString szStr;
	szStr.Format("%zd", iInt);
	Text(szStr);
	m_Comma[GetLevel()]=COMMA_VAL;
}

void CJSONWriter::FloatVal(double dFloat) {
	Comma();
	CFSAString szStr;
	szStr.Format("%f", dFloat);
	Text(szStr);
	m_Comma[GetLevel()]=COMMA_VAL;
}

void CJSONWriter::BoolVal(bool bBool) {
	Comma();
	Text(bBool ? "true" : "false");
	m_Comma[GetLevel()]=COMMA_VAL;
}

void CJSONWriter::StringVal(const CFSAString &szStr) {
	Comma();
	m_Stream.WriteChar('\"');
	Text(szStr);
	m_Stream.WriteChar('\"');
	m_Comma[GetLevel()]=COMMA_VAL;
}

void CJSONWriter::NullVal() {
	Comma();
	Text("null");
	m_Comma[GetLevel()]=COMMA_VAL;
}

void CJSONWriter::ObjectStart() {
	Comma();
	m_Comma[GetLevel()]=COMMA_VAL;
	Text("{");
	m_Comma.AddItem(COMMA_KEY);
}

void CJSONWriter::ObjectEnd() {
	RT_ASSERT(GetLevel()>0);
	m_Comma.RemoveItem(GetLevel());
	Text("\n");
	Indent();
	Text("}");
}

void CJSONWriter::ArrayStart() {
	Comma();
	m_Comma[GetLevel()]=COMMA_VAL;
	Text("[");
	m_Comma.AddItem(COMMA_KEY);
}

void CJSONWriter::ArrayEnd() {
	RT_ASSERT(GetLevel()>0);
	m_Comma.RemoveItem(GetLevel());
	Text("\n");
	Indent();
	Text("]");
}

void CJSONWriter::Text(const CFSAString &szStr) {
	for (INTPTR ip=0; ip<szStr.GetLength(); ip++) {
		if (szStr[ip]=='\"') m_Stream.WriteChar('\\');
		m_Stream.WriteChar(szStr[ip]);
	}
}

void CJSONWriter::Comma() {
	if (m_Comma[GetLevel()]) {
		if (m_Comma[GetLevel()]==COMMA_VAL) {
			m_Stream.WriteChar(',');
		}
		m_Stream.WriteChar('\n');
		Indent();
		m_Comma[GetLevel()]=COMMA_NO;
	}
}

void CJSONWriter::Indent() {
	for (INTPTR ip=0; ip<GetLevel(); ip++) {
		m_Stream.WriteChar('\t');
	}
}
