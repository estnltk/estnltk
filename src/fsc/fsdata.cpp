#include "stdfsc.h"
#include "fstype.h"

#include "fsdata.h"
#include "fstrace.h"
#include "fsmemory.h"
#include "fsutil.h"

#define __FSDATAMAXOVERHEAD (50*1024) // 50K

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CFSData::CFSData()
{
	m_pData=0;
	m_ipSize=m_ipBufferSize=0;
}

CFSData::CFSData(const CFSData &Data)
{
	m_pData=0;
	m_ipSize=m_ipBufferSize=0;
	operator =(Data);
}

#if defined (__FSCXX0X)
CFSData::CFSData(CFSData &&Data)
{
	m_pData=Data.m_pData;
	Data.m_pData=0;
	m_ipSize=Data.m_ipSize;
	Data.m_ipSize=0;
	m_ipBufferSize=Data.m_ipBufferSize;
	Data.m_ipBufferSize=0;
}
#endif

CFSData::~CFSData()
{
	Cleanup();
}

CFSData &CFSData::operator =(const CFSData &Data)
{
	if (m_pData!=Data.m_pData) {
		SetSize(Data.GetSize());
		memcpy(m_pData, Data.m_pData, Data.GetSize());
	}
    return *this;
}

#if defined (__FSCXX0X)
CFSData &CFSData::operator =(CFSData &&Data)
{
	if (m_pData!=Data.m_pData) {
		Cleanup();
		m_pData=Data.m_pData;
		Data.m_pData=0;
		m_ipSize=Data.m_ipSize;
		Data.m_ipSize=0;
		m_ipBufferSize=Data.m_ipBufferSize;
		Data.m_ipBufferSize=0;
	}
    return *this;
}
#endif

void CFSData::Reserve(INTPTR ipSize) {
	ASSERT(ipSize>=0);
	if (ipSize>m_ipBufferSize) {
		m_ipBufferSize=ipSize;
		m_pData=FSReAlloc(m_pData, m_ipBufferSize);
	}
}

void CFSData::SetSize(INTPTR ipSize, bool bReserveMore){
	ASSERT(ipSize>=0);
	m_ipSize=FSMAX(ipSize, 0);
	if (m_ipSize>m_ipBufferSize) {
		Reserve(bReserveMore ? FSMIN(m_ipSize+__FSDATAMAXOVERHEAD, (INTPTR)(1.2*m_ipSize)+20) : m_ipSize);
	}
}

void CFSData::FreeExtra(){
	if (m_ipBufferSize>m_ipSize) {
		m_ipBufferSize=m_ipSize;
		m_pData=FSReAlloc(m_pData, m_ipBufferSize);
	}
}

void CFSData::Cleanup()
{
	if (m_pData) {
		FSFree(m_pData);
	}
	m_pData=0;
	m_ipSize=m_ipBufferSize=0;
}

void CFSData::Append(const void *pData, INTPTR ipSize)
{
	ASSERT(ipSize>=0);
	ipSize=FSMAX(ipSize, 0);
	INTPTR ipOldSize=m_ipSize;
	SetSize(m_ipSize+ipSize);
	memcpy((BYTE *)m_pData+ipOldSize, pData, ipSize);
}

CFSStream &operator<<(CFSStream &Stream, const CFSData &Data)
{
	Stream << (UINTPTR)Data.m_ipSize;
	Stream.WriteBuf(Data.m_pData, Data.m_ipSize);
	return Stream;
}

CFSStream &operator>>(CFSStream &Stream, CFSData &Data)
{
	INTPTR ipSize;
	Stream >> (UINTPTR &)ipSize;
	if (ipSize<0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	Data.SetSize(ipSize, false);
	Stream.ReadBuf(Data.m_pData, Data.m_ipSize);
	return Stream;
}
