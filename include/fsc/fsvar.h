#if !defined _FSVAR_H_
#define _FSVAR_H_

#include "fsstring.h"
#include "fslist.h"

/**
* Class that can represent any size and shape of data - integers, floating point, string, map, array.
* For example: Var["filosoft"]["prr"][0]=3.5; is completely legal.
*/
class CFSVar {
public:
	enum { VAR_EMPTY, VAR_INT, VAR_FLOAT, VAR_BOOL, VAR_STRING, VAR_MAP, VAR_ARRAY };

	CFSVar();
	CFSVar(const CFSVar &Var);
#if defined (__FSCXX0X)
	CFSVar(CFSVar &&Var);
#endif
	CFSVar(INTPTR ipInt, int iType=VAR_INT);
	CFSVar(double dFloat, int iType=VAR_FLOAT);
	CFSVar(bool bBool, int iType=VAR_BOOL);
	CFSVar(const CFSAString &szString, int iType=VAR_STRING);
	CFSVar(const char *pszString, int iType=VAR_STRING);
	CFSVar(const CFSWString &szString, int iType=VAR_STRING);
	CFSVar(const wchar_t *pszString, int iType=VAR_STRING);

	CFSVar &operator =(const CFSVar &Var);
#if defined (__FSCXX0X)
	CFSVar &operator =(CFSVar &&Var);
#endif
/*	CFSVar &operator =(INTPTR ipInt);
	CFSVar &operator =(double dFloat);
	CFSVar &operator =(bool bBool);
	CFSVar &operator =(const CFSAString &szString);
	CFSVar &operator =(const char *pszString) {
		return operator =(CFSAString(pszString));
	}
	CFSVar &operator =(const CFSWString &szString);
	CFSVar &operator =(const wchar_t *pszString) {
		return operator =(CFSWString(pszString));
	}*/

	void Cleanup();

	int GetType() const {
		return m_iType;
	}

	INTPTR GetInt() const;
	double GetFloat() const;
	bool GetBool() const {
		return GetInt()!=0;
	}
	CFSAString GetAString() const;
	CFSWString GetWString() const;

/**
* Function that returns the size of array or map
* @return Size of array/map
*/
	INTPTR GetSize() const {
		return m_Map.GetSize();
	}

/**
* Function returns the key of N-th physical element of array or map
* @param[in] ipIndex Index of physical element
* @return Key of the element
*/
	CFSAString GetKey(INTPTR ipIndex) const {
		return m_Map.GetItem(ipIndex).Key;
	}

/**
* Function verifies if the key exist in the map or array
* @param[in] szKey Key name
* @return true if key exists
*/
	bool KeyExist(const CFSAString &szKey) const {
		return (m_iType==VAR_MAP || m_iType==VAR_ARRAY) && m_Map.Exist(szKey);
	}

/**
* Returns reference to N-th element in array.
* @param[in] ipKey Index of the element.
* @return Value at the point. If element is missing from the array, it is created.
*/
	CFSVar &operator [](INTPTR ipKey);

/**
* Returns reference to N-th element in array.
* @param[in] ipKey Index of the element.
* @return Value at the point. If element is missing from the array, NULL-element is returned.
*/
	const CFSVar &operator [](INTPTR ipKey) const;

/**
* Returns reference to value of data pair identified by Key.
* @param[in] pszKey Key to search for.
* @return Reference to value of data pair. If data pair does not exist, it is created.
*/
	CFSVar &operator [](const CFSAString &szKey);
	CFSVar &operator [](const char *pszKey) {
		return (*this)[CFSAString(pszKey)];
	}

/**
* Returns reference to value of data pair identified by Key.
* @param[in] pszKey Key to search for.
* @return Reference to value of data pair. If data pair does not exist, NULL-element is returned.
*/
	const CFSVar &operator [](const CFSAString &szKey) const;
	const CFSVar &operator [](const char *pszKey) const {
		return (*this)[CFSAString(pszKey)];
	}

/**
* Converts variable to different type.
* @param[in] iType Variable type.
*/
	void Cast(int iType);

protected:
	INTPTR m_ipInt;
	double m_dFloat;
	CFSAString m_szString;
	CFSMap<CFSAString, CFSVar> m_Map;

	int m_iType;
};

#endif // _FSVAR_H_
