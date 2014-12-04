#include "stdfsc.h"
#include "fstype.h"

#include "fslist.h"

/////////////////////////////////////////////////////////////////////
// CFSBitSet
void CFSBitSet::Reserve(INTPTR ipSize)
{
	ASSERT(ipSize>=0);
	m_Array.Reserve((ipSize+31)/32);
}

void CFSBitSet::SetSize(INTPTR ipSize, bool bReserveMore)
{
	ASSERT(ipSize>=0);
	m_ipSize=ipSize;
	m_Array.SetSize((m_ipSize+31)/32, bReserveMore);
	int iBit=(int)(m_ipSize%32);
	if (iBit) {
		m_Array[m_Array.GetSize()-1]=(m_Array[m_Array.GetSize()-1]<<(32-iBit))>>(32-iBit);
	}
}

INTPTR CFSBitSet::GetSetCount(bool bBit) const
{
	INTPTR ipCount=0;
	for (INTPTR ip=0; ip<m_Array.GetSize(); ip++){
		UINT32 ui=m_Array[ip];
		ui=ui-((ui>>1)&0x55555555);
		ui=(ui&0x33333333)+((ui>>2)&0x33333333);
		ipCount+=(((ui+(ui>>4))&0xF0F0F0F)*0x1010101)>>24;
	}
	return (bBit ? ipCount : GetSize()-ipCount);
}

bool CFSBitSet::operator [](INTPTR ipIndex) const
{
	ASSERT(ipIndex>=0 && ipIndex<m_ipSize);
	return (m_Array[ipIndex/32]&(1<<(ipIndex%32)))!=0;
}

void CFSBitSet::Set(INTPTR ipIndex, bool bBit)
{
	ASSERT(ipIndex>=0 && ipIndex<m_ipSize);
	if (bBit) {
		m_Array[ipIndex/32]|=(1<<(ipIndex%32));
	}
	else {
		m_Array[ipIndex/32]&=~(1<<(ipIndex%32));
	}
}

bool CFSBitSet::operator ==(const CFSBitSet &BitSet) const
{
	if (GetSize()!=BitSet.GetSize()) {
		return false;
	}
	for (INTPTR ip=0; ip<m_Array.GetSize(); ip++) {
		if (m_Array[ip]!=BitSet.m_Array[ip]) {
			return false;
		}
	}
	return true;
}

CFSBitSet &CFSBitSet::operator |=(const CFSBitSet &BitSet)
{
	if (BitSet.GetSize()>GetSize()) {
		SetSize(BitSet.GetSize());
	}
	for (INTPTR ip=0; ip<BitSet.m_Array.GetSize(); ip++) {
		m_Array[ip]|=BitSet.m_Array[ip];
	}
	return *this;
}

CFSBitSet &CFSBitSet::operator &=(const CFSBitSet &BitSet)
{
	if (BitSet.GetSize()<GetSize()) {
		SetSize(BitSet.GetSize());
	}
	for (INTPTR ip=0; ip<m_Array.GetSize(); ip++) {
		m_Array[ip]&=BitSet.m_Array[ip];
	}
	return *this;
}

CFSStream &operator<<(CFSStream &Stream, const CFSBitSet &BitSet)
{
	Stream << (UINTPTR)BitSet.m_ipSize;
	for (INTPTR ip=0; ip<BitSet.m_Array.GetSize(); ip++) {
		Stream << BitSet.m_Array[ip];
	}
	return Stream;
}

CFSStream &operator>>(CFSStream &Stream, CFSBitSet &BitSet)
{
	INTPTR ipSize;
	Stream >> (UINTPTR &)ipSize;
	if (ipSize<0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	BitSet.SetSize(ipSize, false);
	for (INTPTR ip=0; ip<BitSet.m_Array.GetSize(); ip++) {
		Stream >> BitSet.m_Array[ip];
	}
	return Stream;
}

/////////////////////////////////////////////////////////////////////
// CFSSorter

void CFSSorter::SelectionSort(INTPTR ipStart, INTPTR ipEnd)
{
	for (INTPTR ip=ipStart; ip<ipEnd; ip++){
		INTPTR ipMinimal=ip;
		for (INTPTR ip2=ip+1; ip2<=ipEnd; ip2++){
			if (IsLessThan(ip2, ipMinimal)) {
				ipMinimal=ip2;
			}
		}
		if (ipMinimal!=ip) {
			Swap(ip, ipMinimal);
		}
	}
}

void CFSSorter::GnomeSort(INTPTR ipStart, INTPTR ipEnd)
{
	INTPTR ipCurr=ipStart+1;
	INTPTR ipNext=ipCurr+1;
	while (ipCurr<=ipEnd) {
		if (IsLessThan(ipCurr, ipCurr-1)) {
			Swap(ipCurr-1, ipCurr);
			ipCurr--;
			if (ipCurr<=ipStart) {
				ipCurr=ipNext;
				ipNext++;
			}
		}
		else {
			ipCurr=ipNext;
			ipNext++;
		}

	}
}

void CFSSorter::IntroSort(INTPTR ipStart, INTPTR ipEnd)
{
	int iLevel=0;
	for (INTPTR ipSize=ipEnd-ipStart+1; ipSize>0; ipSize/=2) {
		iLevel++;
	}
	IntroSort(ipStart, ipEnd, FSMAX(50, iLevel*2));
} 

void CFSSorter::IntroSort(INTPTR ipStart, INTPTR ipEnd, int iLevel)
{
	if (ipStart>=ipEnd) {
		return;
	}
	if (iLevel<=0) {
		HeapSort(ipStart, ipEnd);
		return;
	}

	INTPTR ipLow=ipStart;
	INTPTR ipMid=(ipStart+ipEnd)/2;
	INTPTR ipHigh=ipEnd;
	do {
		while (IsLessThan(ipLow, ipMid)) {
			ipLow++;
		}
		while (IsLessThan(ipMid, ipHigh)) {
			ipHigh--;
		}
		if (ipLow<=ipHigh) {
			Swap(ipLow, ipHigh);
			if (ipMid==ipLow) ipMid=ipHigh;
			else if (ipMid==ipHigh) ipMid=ipLow;
			ipLow++; ipHigh--;
		}
	} while (ipLow<=ipHigh);

	IntroSort(ipStart, ipHigh, iLevel-1);
	IntroSort(ipLow, ipEnd, iLevel-1);
}

void CFSSorter::HeapSort(INTPTR ipStart, INTPTR ipEnd)
{
	HeapBuild(ipStart, ipEnd);
	while (ipEnd>ipStart) {
		Swap(ipStart, ipEnd);
		ipEnd--;
		HeapDown(ipStart, ipEnd, 0);
	} 
}

void CFSSorter::HeapBuild(INTPTR ipStart, INTPTR ipEnd)
{
	for (INTPTR ip=(ipEnd-ipStart+1)/2-1; ip>=0; ip--) {
		HeapDown(ipStart, ipEnd, ip);
	}
}

void CFSSorter::HeapDown(INTPTR ipStart, INTPTR ipEnd, INTPTR ipIndex)
{
	INTPTR ipHeapLength=ipEnd-ipStart+1;

	INTPTR ipIndex2=ipIndex*2+1;
	while (ipIndex2<ipHeapLength) {
		if (ipIndex2+1<ipHeapLength && IsLessThan(ipStart+ipIndex2, ipStart+ipIndex2+1)) {
			ipIndex2++;
		}
		if (!IsLessThan(ipStart+ipIndex, ipStart+ipIndex2)) {
			return;
		}

		Swap(ipStart+ipIndex, ipStart+ipIndex2);
		ipIndex=ipIndex2;
		ipIndex2=ipIndex*2+1;
	}
}
