#if !defined _FSHUGEINTEGER_H_
#define _FSHUGEINTEGER_H_

#include "fsstring.h"
#include "fsstream.h"

/**
* Macro that defines any '?' operator through its '?'= relative.
*/
#define __FSHI_OPWRAPPER(OP, Param) CFSHugeInteger operator OP (Param Val) const { return (CFSHugeInteger(*this) OP##= Val); }

/**
* CFSHugeInteger provides calculation functions for unlimited size integer data type.
*/
class CFSHugeInteger
{
public:
	CFSHugeInteger()
	{
		Init();
	}
	CFSHugeInteger(const CFSHugeInteger &HInt)
	{
		Init();
		operator =(HInt);
	}
	CFSHugeInteger(INT32 lVal)
	{
		Init();
		operator =(lVal);
	}
	CFSHugeInteger(UINT32 lVal)
	{
		Init();
		operator =(lVal);
	}
	CFSHugeInteger(INT64 lVal)
	{
		Init();
		operator =(lVal);
	}
	CFSHugeInteger(UINT64 lVal)
	{
		Init();
		operator =(lVal);
	}
/**
* Creates class from string.
* @param[in] szStr Classic string representation of the integer (0...9a...z). Case insensitive.
* @param[in] lBase Base of the string coding. Typical values: 2, 8, 10, 16.
*/
	CFSHugeInteger(const CFSString &szStr, UINT32 lBase=10);
/**
* Creates class from string.
* @param[in] szStr String representation of the integer. Case insensitive.
* @param[in] szSymbols Digits that define the numeric system from symbol 0 to symbol Base-1. Case insensitive.
*/
	CFSHugeInteger(const CFSString &szStr, const CFSString &szSymbols);
	virtual ~CFSHugeInteger();

	CFSHugeInteger &operator =(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator =(INT32 lVal);
	CFSHugeInteger &operator =(UINT32 lVal);
	CFSHugeInteger &operator =(INT64 lVal);
	CFSHugeInteger &operator =(UINT64 lVal);

	operator INT32() const;
	operator UINT32() const;
	operator INT64() const;
	operator UINT64() const;
/**
* Converts huge integer to classic readable format (0..9a..z a digit).
* @param[in] lBase Base of the number representation format.
* @return Number in readable format.
*/
	CFSString GetString(UINT32 lBase=10) const;
/**
* Converts huge integer to a readable format in user-defined numeric-system.
* @param[in] szSymbols Symbols that define the numeric system from symbol 0 to Base-1.
* @return Number in readable format.
*/
	CFSString GetString(const CFSString &szSymbols) const;

/**
* Comparison operators.
*/
	bool operator ==(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)==0;
	}
	bool operator !=(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)!=0;
	}
	bool operator <(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)<0;
	}
	bool operator <=(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)<=0;
	}
	bool operator >(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)>0;
	}
	bool operator >=(const CFSHugeInteger &HInt) const
	{
		return Compare(HInt)>=0;
	}

/**
* Arithmetic operators.
*/
	CFSHugeInteger &operator |=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator &=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator ^=(const CFSHugeInteger &HInt);

	CFSHugeInteger &operator <<=(UINTPTR uipVal);
	CFSHugeInteger &operator >>=(UINTPTR uipVal);

	CFSHugeInteger &operator +=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator -=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator *=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator /=(const CFSHugeInteger &HInt);
	CFSHugeInteger &operator %=(const CFSHugeInteger &HInt);

/**
* '?=' to '?' arithmetic operator wrappers. For example, defines HI1+HI2 through +=.
*/
	__FSHI_OPWRAPPER (|, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (&, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (^, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (<<, UINTPTR);
	__FSHI_OPWRAPPER (>>, UINTPTR);
	__FSHI_OPWRAPPER (+, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (-, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (*, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (/, const CFSHugeInteger &);
	__FSHI_OPWRAPPER (%, const CFSHugeInteger &);

/**
* Calculates a power of the number.
* @param[in] lPower Exponent.
* @return this^lPower.
*/
	CFSHugeInteger Power(ULONG lPower) const;

/**
* Calculates a square root of the number.
* @return Calculated square root.
*/
	CFSHugeInteger Sqrt() const;

/**
* Calculates absolute value of the number.
* @return Calculated absolute value.
*/
	CFSHugeInteger Abs() const;

/**
* Divides the number and returns result and modulo.
* @param[in] HIDivider Divider.
* @param[out] HIDiv Result of division.
* @param[out] HIMod Modulo of division.
*/
	void Divide(const CFSHugeInteger &HIDivider, CFSHugeInteger &HIDiv, CFSHugeInteger &HIMod) const;

	friend CFSStream &operator<<(CFSStream &Stream, const CFSHugeInteger &HInt);
	friend CFSStream &operator>>(CFSStream &Stream, CFSHugeInteger &HInt);

protected:
	void Init();
	int FromString(const CFSString &szStr, const CFSString &szSymbols);

	int Compare(const CFSHugeInteger &HInt) const;
	void SetSize(INTPTR ipSize);
	void UpdateSize();

	void ShlBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, BYTE cShift) const;
	void ShrBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, BYTE cShift) const;
	void AddBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount) const;
	void SubBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount) const;
	void MulBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, UINT32 lMultiplier) const;
	void DivBuf(UINT32 *pTarget, UINT32 *pModulo, const UINT32 *pSource, INTPTR ipCount, UINT32 lDivider) const;

	UINT32 *m_pData;
	INTPTR m_ipSize;
	int m_iSign; // -1 | 1
};

#endif // _FSHUGEINTEGER_H_
