#include "stdfsc.h"
#include "fstype.h"

#include "fshugeinteger.h"
#include "fsmemory.h"

static const CFSString g_szFSHISymbols=FSTSTR("0123456789abcdefghijklmnopqrstuvwxyz");

CFSHugeInteger::CFSHugeInteger(const CFSString &szStr, const CFSString &szSymbols)
{
	Init();
	FromString(szStr, szSymbols);
}

CFSHugeInteger::CFSHugeInteger(const CFSString &szStr, UINT32 lBase)
{
	Init();
	if (lBase>(UINT32)g_szFSHISymbols.GetLength()) {
		return;
	}
	FromString(szStr, g_szFSHISymbols.Left(lBase));
}

int CFSHugeInteger::FromString(const CFSString &szStr, const CFSString &szSymbols)
{
	SetSize(0);
	UINT32 uiBase=(UINT32)szSymbols.GetLength();
	if (uiBase<2) {
		return -1;
	}
	if (szStr.IsEmpty()) {
		return -1;
	}
	CFSString szStrLow=szStr.ToLower();
	CFSString szSymbolsLow=szSymbols.ToLower();

	INTPTR ipIndex=0;
	bool bNegative=false;
	if (szStrLow[0]==FSTSTR('-')){
		bNegative=true;
		ipIndex++;
	}
	for (; szStrLow[ipIndex]; ipIndex++){
		INTPTR ipPos=szSymbolsLow.Find(szStrLow[ipIndex]);
		if (ipPos<0) {
			return -1;
		}
		(*this)*=uiBase;
		(*this)+=(UINT32)ipPos;
	}
	if (bNegative && m_ipSize) {
		m_iSign=-1;
	}
	return 0;
}

CFSHugeInteger::~CFSHugeInteger()
{
	if (m_pData) {
		FSFree(m_pData);
	}
}

void CFSHugeInteger::Init()
{
	m_pData=0;
	m_ipSize=0;
	m_iSign=1;
}

CFSHugeInteger &CFSHugeInteger::operator =(const CFSHugeInteger &HInt)
{
	m_iSign=HInt.m_iSign;
	SetSize(HInt.m_ipSize);
	memcpy(m_pData, HInt.m_pData, m_ipSize*sizeof(UINT32));
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator =(INT32 lVal)
{
	if (lVal>=0){
		return operator =((UINT32)lVal);
	}
	else{
		operator =((UINT32)-lVal);
		m_iSign=-1;
		return *this;
	}
}

CFSHugeInteger &CFSHugeInteger::operator =(UINT32 lVal)
{
	m_iSign=1;
	SetSize(1);
	m_pData[0]=lVal;
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator =(INT64 lVal)
{
	if (lVal>=0){
		return operator =((UINT64)lVal);
	}
	else{
		operator =((UINT64)-lVal);
		m_iSign=-1;
		return *this;
	}
}

CFSHugeInteger &CFSHugeInteger::operator =(UINT64 lVal)
{
	m_iSign=1;
	SetSize(2);
	m_pData[0]=(UINT32)(lVal);
	m_pData[1]=(UINT32)(lVal>>32);
	UpdateSize();
	return *this;
}

CFSHugeInteger::operator INT32() const
{
	return ((INT32)(operator UINT32()&0x7fffffff))*m_iSign;
}

CFSHugeInteger::operator UINT32() const
{
	if (m_ipSize<1) {
		return 0;
	}
	return m_pData[0];
}

CFSHugeInteger::operator INT64() const
{
	return ((INT64)(operator UINT64()&LL(0x7fffffffffffffff)))*m_iSign;
}

CFSHugeInteger::operator UINT64() const
{
	if (m_ipSize<1) {
		return 0;
	}
	if (m_ipSize<2) {
		return m_pData[0];
	}
	return ((UINT64)m_pData[0]) | (((UINT64)m_pData[1])<<32);
}

CFSString CFSHugeInteger::GetString(const CFSString &szSymbols) const
{
	UINT32 lBase=(UINT32)szSymbols.GetLength();
	if (lBase<2) {
		return FSTSTR("");
	}
	if (!m_ipSize) {
		return CFSString(szSymbols[0]);
	}
	CFSHugeInteger HInt=*this;
	CFSString szResult;
	while (HInt.m_ipSize){
		CFSHugeInteger HIDiv, HIMod;
		HInt.Divide(lBase, HIDiv, HIMod);
		szResult+=szSymbols[(UINT32)HIMod];
		HInt=HIDiv; 
	}
	if (m_iSign==-1) {
		szResult+='-';
	}
	szResult.MakeReverse();
	return szResult;
}

CFSString CFSHugeInteger::GetString(UINT32 lBase) const
{
	if (lBase>(UINT32)g_szFSHISymbols.GetLength()) {
		return FSTSTR("");
	}
	return GetString(g_szFSHISymbols.Left(lBase));
}

int CFSHugeInteger::Compare(const CFSHugeInteger &HInt) const
{
	if (m_iSign!=HInt.m_iSign) {
		return m_iSign;
	}

	if (m_ipSize<HInt.m_ipSize) {
		return -m_iSign;
	}
	if (m_ipSize>HInt.m_ipSize) {
		return m_iSign;
	}

	for (INTPTR ip=m_ipSize-1; ip>=0; ip--) {
		if (m_pData[ip]<HInt.m_pData[ip]) {
			return -m_iSign;
		}
		if (m_pData[ip]>HInt.m_pData[ip]) {
			return m_iSign;
		}
	}

	return 0;
}

CFSHugeInteger &CFSHugeInteger::operator |=(const CFSHugeInteger &HInt)
{
	m_iSign|=HInt.m_iSign;
	SetSize(FSMAX(m_ipSize, HInt.m_ipSize));
	for (INTPTR ip=0; ip<HInt.m_ipSize; ip++){
		m_pData[ip]|=HInt.m_pData[ip];
	}
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator &=(const CFSHugeInteger &HInt)
{
	m_iSign&=HInt.m_iSign;
	SetSize(FSMIN(m_ipSize, HInt.m_ipSize));
	for (INTPTR ip=FSMIN(m_ipSize, HInt.m_ipSize)-1; ip>=0; ip--) {
		m_pData[ip]&=HInt.m_pData[ip];
	}
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator ^=(const CFSHugeInteger &HInt)
{
	m_iSign=(m_iSign==HInt.m_iSign ? 1 : -1);
	SetSize(FSMAX(m_ipSize, HInt.m_ipSize));
	for (INTPTR ip=0; ip<HInt.m_ipSize; ip++){
		m_pData[ip]^=HInt.m_pData[ip];
	}
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator <<=(UINTPTR uipVal)
{
	if (!uipVal) {
		return *this;
	}
	INTPTR ipByteShift=uipVal>>5;			// /32
	BYTE cBitShift=(BYTE)(uipVal&0x1f);	// 5 lower bits
	if (!cBitShift){
		INTPTR ipOldSize=m_ipSize;
		SetSize(m_ipSize+ipByteShift);
		memmove(m_pData+ipByteShift, m_pData, ipOldSize*sizeof(UINT32));
		memset(m_pData, 0, sizeof(UINT32)*ipByteShift);
	}
	else{
		CFSHugeInteger HITemp; HITemp.SetSize(m_ipSize+1);
		ShlBuf(HITemp.m_pData, m_pData, m_ipSize, cBitShift);
		HITemp.UpdateSize();
		SetSize(HITemp.m_ipSize+ipByteShift);
		memcpy(m_pData+ipByteShift, HITemp.m_pData, HITemp.m_ipSize*sizeof(UINT32));
		memset(m_pData, 0, sizeof(UINT32)*ipByteShift);
	}
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator >>=(UINTPTR uipVal)
{
	if (!uipVal) {
		return *this;
	}
	INTPTR ipByteShift=uipVal>>5;			// /32
	BYTE cBitShift=(BYTE)(uipVal&0x1f);	// 5 lower bits
	if (ipByteShift>=m_ipSize){
		SetSize(0);
		return *this;
	}
	INTPTR ipSize=m_ipSize-ipByteShift;
	if (!cBitShift){
		memmove(m_pData, m_pData+ipByteShift, sizeof(UINT32)*ipSize);
	}
	else{
		CFSHugeInteger HITemp; HITemp.SetSize(m_ipSize);
		ShrBuf(HITemp.m_pData, m_pData, m_ipSize, cBitShift);
		memcpy(m_pData, HITemp.m_pData+ipByteShift, sizeof(UINT32)*ipSize);
	}
	SetSize(ipSize);
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator +=(const CFSHugeInteger &HInt)
{
	if (HInt.m_ipSize==0) {
		return *this;
	}
	if (m_iSign!=HInt.m_iSign){
		CFSHugeInteger HInt2=HInt;
		HInt2.m_iSign=-HInt2.m_iSign;
		return operator -=(HInt2);
	}
	SetSize(FSMAX(m_ipSize, HInt.m_ipSize)+1);
	AddBuf(m_pData, HInt.m_pData, HInt.m_ipSize);
	UpdateSize();
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator -=(const CFSHugeInteger &HInt)
{
	if (HInt.m_ipSize==0) {
		return *this;
	}
	if (m_iSign!=HInt.m_iSign){
		CFSHugeInteger HInt2=HInt;
		HInt2.m_iSign=-HInt2.m_iSign;
		return operator +=(HInt2);
	}
	if (Compare(HInt)!=m_iSign){
		CFSHugeInteger HITemp=HInt;
		SubBuf(HITemp.m_pData, m_pData, m_ipSize);
		HITemp.m_iSign=-HITemp.m_iSign;
		HITemp.UpdateSize();
		*this=HITemp;
	}
	else{
		SubBuf(m_pData, HInt.m_pData, HInt.m_ipSize);
		UpdateSize();
	}
	return *this;
}

CFSHugeInteger &CFSHugeInteger::operator *=(const CFSHugeInteger &HInt)
{
	if (m_ipSize<=0) {
		return *this;
	}
	if (HInt.m_ipSize<=0) {
		SetSize(0);
		return *this;
	}
	CFSHugeInteger HIResult;
	for (INTPTR ip=0; ip<HInt.m_ipSize; ip++){
		CFSHugeInteger HITemp; HITemp.SetSize(m_ipSize+1);
		MulBuf(HITemp.m_pData, m_pData, m_ipSize, HInt.m_pData[ip]);
		HITemp.UpdateSize();
		HIResult.SetSize(FSMAX(HIResult.m_ipSize, ip+HITemp.m_ipSize)+1);
		AddBuf(HIResult.m_pData+ip, HITemp.m_pData, HITemp.m_ipSize);
		HIResult.UpdateSize();
	}
	HIResult.m_iSign=m_iSign*HInt.m_iSign;
	return *this=HIResult;
}

CFSHugeInteger &CFSHugeInteger::operator /=(const CFSHugeInteger &HInt)
{
	CFSHugeInteger HDiv, HMod;
	Divide(HInt, HDiv, HMod);
	return (*this)=HDiv;
}

CFSHugeInteger &CFSHugeInteger::operator %=(const CFSHugeInteger &HInt)
{
	CFSHugeInteger HDiv, HMod;
	Divide(HInt, HDiv, HMod);
	return (*this)=HMod;
}

CFSHugeInteger CFSHugeInteger::Power(ULONG lPower) const
{
	if (lPower==0) {
		return (UINT32)1;
	}
	if (lPower==1) {
		return (*this);
	}

	CFSHugeInteger HIResult=Power(lPower/2);
	HIResult*=HIResult;
	if (lPower&1) {
		HIResult*=(*this);
	}
	return HIResult;
}

CFSHugeInteger CFSHugeInteger::Abs() const
{
	CFSHugeInteger HIResult=(*this);
	HIResult.m_iSign=1;
	return HIResult;
}

CFSHugeInteger CFSHugeInteger::Sqrt() const
{
	if (m_iSign<0) {
		return CFSHugeInteger();
	}

	CFSHugeInteger HIVal=*this, HITemp, HITemp2, HIRes;
	for (UINTPTR ipShift=m_ipSize*16-1; ipShift!=(UINTPTR)-1; ipShift--) {
		//HITemp=(HIRes<<(ipShift+1))+(CFSHugeInteger(1)<<(ipShift*2));
		HITemp=HIRes;
		HITemp<<=ipShift+1;

		INTPTR ipElem=ipShift*2/32;
		UINT32 uiBit=1<<((ipShift*2)&0x1f);
		HITemp.SetSize(FSMAX(HITemp.m_ipSize+1, ipElem+1));
		HITemp.AddBuf(HITemp.m_pData+ipElem, &uiBit, 1);
		HITemp.UpdateSize();

		if (HIVal>=HITemp) {
			//HIRes+=CFSHugeInteger(1)<<ipShift;
			ipElem=ipShift/32;
			if (HIRes.m_ipSize<ipElem+1) {
				HIRes.SetSize(ipElem+1);
			}
			HIRes.m_pData[ipElem]|=1<<(ipShift&0x1f);
			HIRes.UpdateSize();

			HIVal-=HITemp;
		}
	}
	return HIRes;
}

void CFSHugeInteger::Divide(const CFSHugeInteger &HIDivider, CFSHugeInteger &HIDiv, CFSHugeInteger &HIMod) const
{
	HIDiv=CFSHugeInteger(); HIMod=CFSHugeInteger();

	RT_ASSERT(HIDivider.m_ipSize>0);
	CFSHugeInteger HIAbsDividend=Abs();
	CFSHugeInteger HIAbsDivider=HIDivider.Abs();
	CFSHugeInteger HITakeDown;

	if (HIAbsDividend<HIAbsDivider) {
		HIDiv=CFSHugeInteger();
		HIMod=*this;
		return;
	}

	if (HIAbsDivider.m_ipSize<=1){
		UINT32 uiMod=0;
		HIDiv.SetSize(m_ipSize);
		DivBuf(HIDiv.m_pData, &uiMod, HIAbsDividend.m_pData, m_ipSize, (UINT32)HIAbsDivider);
		HIDiv.UpdateSize();
		if (HIDiv.m_ipSize) {
			HIDiv.m_iSign=m_iSign*HIDivider.m_iSign;
		}
		HIMod=uiMod;
		HIMod.UpdateSize();
		if (HIMod.m_ipSize) {
			HIMod.m_iSign=m_iSign;
		}
		return;
	}
	
	
	INTPTR ipCursor=HIAbsDividend.m_ipSize-HIAbsDivider.m_ipSize;
	HIDiv.SetSize(ipCursor+1);
	HITakeDown.SetSize(HIAbsDivider.m_ipSize);
	memcpy(HITakeDown.m_pData, HIAbsDividend.m_pData+ipCursor, HITakeDown.m_ipSize*4);
	HITakeDown.UpdateSize();

	for (;;) {
		UINT32 uiEstimate;
		if (HITakeDown<HIAbsDivider) {
			uiEstimate=0;
		}
		else if (HITakeDown.m_ipSize<=2){
			uiEstimate=(UINT32)((UINT64)HITakeDown / (UINT64)HIAbsDivider);
			HITakeDown=(UINT64)HITakeDown % (UINT64)HIAbsDivider;
		}
		else {
			UINT32 uiTest=HITakeDown.m_pData[HITakeDown.m_ipSize-1];
			UINTPTR uipShift=(HITakeDown.m_ipSize-3)*32;
			for (; uiTest; uiTest>>=1) {
				uipShift++;
			}
			UINT64 uiEstimate2=(UINT64)(HITakeDown>>uipShift) / (UINT64)(HIAbsDivider>>uipShift);
			uiEstimate=(uiEstimate2>0xffffffff ? 0xffffffff : (UINT32)uiEstimate2);

			CFSHugeInteger HIProduct=HIAbsDivider*CFSHugeInteger(uiEstimate);
			while (HIProduct>HITakeDown) {
				HIProduct-=HIAbsDivider;
				uiEstimate--;
			}
			HITakeDown-=HIProduct;
		}
		HIDiv.m_pData[ipCursor]=uiEstimate;

		if (ipCursor==0) {
			HIDiv.UpdateSize();
			if (HIDiv.m_ipSize) {
				HIDiv.m_iSign=m_iSign*HIDivider.m_iSign;
			}
			HIMod=HITakeDown;
			if (HIMod.m_ipSize) {
				HIMod.m_iSign=m_iSign;
			}
			return;
		}
		else {
			ipCursor--;
			HITakeDown<<=32;
			if (HIAbsDividend.m_pData[ipCursor]) {
				if (HITakeDown.m_ipSize<1) {
					HITakeDown.SetSize(1);
				}
				HITakeDown.m_pData[0]=HIAbsDividend.m_pData[ipCursor];
			}
		}
	}
}

void CFSHugeInteger::SetSize(INTPTR ipSize)
{
	if (!ipSize){
		if (m_pData) {
			FSFree(m_pData);
		}
		Init();
	}
	else{
		m_pData=(UINT32 *)FSReAlloc(m_pData, ipSize*sizeof(UINT32));
		if (ipSize>m_ipSize) {
			memset(m_pData+m_ipSize, 0, (ipSize-m_ipSize)*sizeof(UINT32));
		}
		m_ipSize=ipSize;
	}
}

void CFSHugeInteger::UpdateSize()
{
	while (m_ipSize>0) {
		if (m_pData[m_ipSize-1]!=0) {
			break;
		}
		SetSize(m_ipSize-1);
	}
}

void CFSHugeInteger::ShlBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, BYTE cShift) const
{
	if (ipCount<=0) {
		return;
	}

	pTarget[0]=0;
	for (INTPTR ip=0; ip<ipCount; ip++){
		pTarget[ip]|=pSource[ip]<<cShift;
		pTarget[ip+1]=pSource[ip]>>(32-cShift);
	}
}

void CFSHugeInteger::ShrBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, BYTE cShift) const
{
	if (ipCount<=0) {
		return;
	}

	pTarget[0]=pSource[0]>>cShift;
	for (INTPTR ip=1; ip<ipCount; ip++){
		pTarget[ip-1]|=pSource[ip]<<(32-cShift);
		pTarget[ip]=pSource[ip]>>cShift;
	}
}

void CFSHugeInteger::AddBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount) const
{
	if (ipCount<=0) {
		return;
	}

	UINT32 uiTemp;
	bool bCarry=false;
	INTPTR ip;
	for (ip=0; ip<ipCount; ip++) {
		if (bCarry) {
			uiTemp=pTarget[ip]+pSource[ip]+1;
			bCarry=(uiTemp<=pTarget[ip]);
		}
		else {
			uiTemp=pTarget[ip]+pSource[ip];
			bCarry=(uiTemp<pTarget[ip]);
		}
		pTarget[ip]=uiTemp;
	}
	for (; bCarry; ip++) {
		pTarget[ip]++;
		bCarry=(pTarget[ip]==0);
	}
}

void CFSHugeInteger::SubBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount) const
{
	if (ipCount<=0) {
		return;
	}

	UINT32 uiTemp;
	bool bCarry=false;
	INTPTR ip;
	for (ip=0; ip<ipCount; ip++) {
		if (bCarry) {
			uiTemp=pTarget[ip]-pSource[ip]-1;
			bCarry=(uiTemp>=pTarget[ip]);
		}
		else {
			uiTemp=pTarget[ip]-pSource[ip];
			bCarry=(uiTemp>pTarget[ip]);
		}
		pTarget[ip]=uiTemp;
	}
	for (; bCarry; ip++) {
		pTarget[ip]--;
		bCarry=(pTarget[ip]==(UINT32)-1);
	}
}

void CFSHugeInteger::MulBuf(UINT32 *pTarget, const UINT32 *pSource, INTPTR ipCount, UINT32 uiMultiplier) const
{
	if (ipCount<=0) {
		return;
	}

	pTarget[0]=0;
	for (INTPTR ip=0; ip<ipCount; ip++){
		UINT64 uiTemp=(UINT64)pSource[ip]*uiMultiplier+pTarget[ip];
		pTarget[ip]=(UINT32)uiTemp;
		pTarget[ip+1]=(UINT32)(uiTemp>>32);
	}
}

void CFSHugeInteger::DivBuf(UINT32 *pTarget, UINT32 *pModulo, const UINT32 *pSource, INTPTR ipCount, UINT32 uiDivider) const
{
	if (ipCount<=0) {
		*pModulo=0;
		return;
	}

	UINT64 uiTemp=0;
	for (INTPTR ip=ipCount-1; ip>=0; ip--) {
		uiTemp|=pSource[ip];
		pTarget[ip]=(UINT32)(uiTemp/uiDivider);
		uiTemp=(uiTemp%uiDivider)<<32;
	}
	*pModulo=(UINT32)(uiTemp>>32);
}

CFSStream &operator<<(CFSStream &Stream, const CFSHugeInteger &HInt)
{
	Stream << HInt.m_iSign << (UINTPTR)HInt.m_ipSize;
	for (INTPTR ip=0; ip<HInt.m_ipSize; ip++) {
		Stream.WriteUInt(HInt.m_pData[ip], 4);
	}
	return Stream;
}

CFSStream &operator>>(CFSStream &Stream, CFSHugeInteger &HInt)
{
	UINTPTR uipSize;
	Stream >> HInt.m_iSign >> uipSize;
	if ((INTPTR)uipSize<0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	HInt.SetSize(uipSize);
	for (INTPTR ip=0; ip<HInt.m_ipSize; ip++) {
		Stream.ReadUInt(&HInt.m_pData[ip], 4);
	}
	return Stream;
}

