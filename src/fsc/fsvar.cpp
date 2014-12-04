#include "stdfsc.h"
#include "fstype.h"

#include "fsvar.h"
#include "fsstring2.h"

CFSVar::CFSVar() {
	m_iType=VAR_EMPTY;
}

CFSVar::CFSVar(const CFSVar &Var) {
	m_iType=VAR_EMPTY;
	operator=(Var);
}

#if defined (__FSCXX0X)
CFSVar::CFSVar(CFSVar &&Var) {
	m_iType=VAR_EMPTY;
	operator=(FSMove(Var));
}
#endif

CFSVar::CFSVar(INTPTR ipInt, int iType) {
	m_iType=VAR_INT;
	m_ipInt=ipInt;
	Cast(iType);
}

CFSVar::CFSVar(double dFloat, int iType) {
	m_iType=VAR_FLOAT;
	m_dFloat=dFloat;
	Cast(iType);
}

CFSVar::CFSVar(bool bBool, int iType) {
	m_iType=VAR_BOOL;
	m_ipInt=bBool;
	Cast(iType);
}

CFSVar::CFSVar(const CFSAString &szString, int iType) {
	m_iType=VAR_STRING;
	m_szString=szString;
	Cast(iType);
}

CFSVar::CFSVar(const char *pszString, int iType) {
	m_iType=VAR_STRING;
	m_szString=pszString;
	Cast(iType);
}

CFSVar::CFSVar(const CFSWString &szString, int iType) {
	m_iType=VAR_STRING;
	m_szString=FSStrWtoA(szString, FSCP_UTF8);
	Cast(iType);
}

CFSVar::CFSVar(const wchar_t *pszString, int iType) {
	m_iType=VAR_STRING;
	m_szString=FSStrWtoA(pszString, FSCP_UTF8);
	Cast(iType);
}

CFSVar &CFSVar::operator =(const CFSVar &Var) {
	m_ipInt=Var.m_ipInt;
	m_dFloat=Var.m_dFloat;
	m_szString=Var.m_szString;
	m_Map=Var.m_Map;
	m_iType=Var.m_iType;
	return *this;
}

#if defined (__FSCXX0X)
CFSVar &CFSVar::operator =(CFSVar &&Var) {
	m_ipInt=Var.m_ipInt;
	m_dFloat=Var.m_dFloat;
	m_szString=FSMove(Var.m_szString);
	m_Map=FSMove(Var.m_Map);
	m_iType=Var.m_iType;
	return *this;
}
#endif

/*CFSVar &CFSVar::operator =(INTPTR ipInt) {
	Cleanup();
	m_iType=VAR_INT;
	m_ipInt=ipInt;
	return *this;
}

CFSVar &CFSVar::operator =(double dFloat) {
	Cleanup();
	m_iType=VAR_FLOAT;
	m_dFloat=dFloat;
	return *this;
}

CFSVar &CFSVar::operator =(bool bBool) {
	Cleanup();
	m_iType=VAR_BOOL;
	m_ipInt=bBool;
	return *this;
}

CFSVar &CFSVar::operator =(const CFSAString &szString) {
	Cleanup();
	m_iType=VAR_STRING;
	m_szString=szString;
	return *this;
}

CFSVar &CFSVar::operator =(const CFSWString &szString) {
	Cleanup();
	m_iType=VAR_STRING;
	m_szString=FSStrWtoA(szString, FSCP_UTF8);
	return *this;
}*/

void CFSVar::Cleanup() {
	m_szString.Empty();
	m_Map.Cleanup();
	m_iType=VAR_EMPTY;
}

INTPTR CFSVar::GetInt() const {
	switch (m_iType) {
		case VAR_INT:
		case VAR_BOOL:
			return m_ipInt;
		case VAR_FLOAT:
			return (INTPTR)m_dFloat;
		case VAR_STRING:
			return strtol(m_szString, 0, 10);
		break;
	}
	return 0;
}

double CFSVar::GetFloat() const {
	switch (m_iType) {
		case VAR_INT:
		case VAR_BOOL:
			return (double)m_ipInt;
		case VAR_FLOAT:
			return m_dFloat;
		case VAR_STRING:
			return strtod(m_szString, 0);
		break;
	}
	return 0.0;
}

CFSAString CFSVar::GetAString() const {
	CFSAString szResult;
	switch (m_iType) {
		case VAR_STRING:
			szResult=m_szString;
		break;
		case VAR_INT:
		case VAR_BOOL:
			szResult.Format("%zd", m_ipInt);
		break;
		case VAR_FLOAT:
			szResult.Format("%f", m_dFloat);
		break;
	}
	return szResult;
}

CFSWString CFSVar::GetWString() const {
	bool bError=false;
	CFSWString szResult=FSStrAtoW(GetAString(), FSCP_UTF8, &bError);
	ASSERT(!bError);
	return szResult;
}

CFSVar &CFSVar::operator [](INTPTR ipKey)
{
	CFSAString szKey;
	szKey.Format("%zd", ipKey);
	return operator[](szKey);
}

const CFSVar &CFSVar::operator [](INTPTR ipKey) const
{
	CFSAString szKey;
	szKey.Format("%zd", ipKey);
	return operator[](szKey);
}

CFSVar &CFSVar::operator [](const CFSAString &szKey)
{
	if (m_iType!=VAR_MAP && m_iType!=VAR_ARRAY) {
		Cast(VAR_MAP);
	}
	return m_Map[szKey];
}

static const CFSVar g_FSNullVar;
const CFSVar &CFSVar::operator [](const CFSAString &szKey) const
{
	if ((m_iType==VAR_MAP || m_iType==VAR_ARRAY) && m_Map.Exist(szKey)) {
		return m_Map[szKey];
	}
	else {
		return g_FSNullVar;
	}
}

void CFSVar::Cast(int iType) {
	if (iType==m_iType) return;
	switch (iType) {
		case VAR_EMPTY: {
			Cleanup();
		} break;
		case VAR_INT: {
			INTPTR ip=GetInt();
			Cleanup();
			m_ipInt=ip;
		} break;
		case VAR_FLOAT: {
			double d=GetFloat();
			Cleanup();
			m_dFloat=d;
		} break;
		case VAR_BOOL: {
			INTPTR ip=GetBool();
			Cleanup();
			m_ipInt=ip;
		} break;
		case VAR_STRING: {
			CFSAString szString=GetAString();
			Cleanup();
			m_szString=szString;
		} break;
		case VAR_MAP:
		case VAR_ARRAY: {
			m_szString.Empty();
		} break;
	}
	m_iType=iType;
}
