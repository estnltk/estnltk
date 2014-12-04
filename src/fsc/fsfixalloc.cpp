#include "stdfsc.h"
#include "fstype.h"

#include "fsfixalloc.h"

///////////////////////////////////////////////////////////
// CFSLockFreeFixAlloc
///////////////////////////////////////////////////////////

CFSLockFreeFixAlloc::CFSLockFreeFixAlloc(INTPTR ipBlockSize, long lMaxCache)
{
	if (ipBlockSize<(INTPTR)sizeof(CFSFixAllocHandle)) {
		ipBlockSize=sizeof(CFSFixAllocHandle);
	}
	m_ipBlockSize=ipBlockSize;
	m_pFreeHandle=0;
	m_lCacheSpace=lMaxCache;
}

CFSLockFreeFixAlloc::~CFSLockFreeFixAlloc(){
	while (m_pFreeHandle){
		CFSFixAllocHandle *pNext=m_pFreeHandle->m_pNext;
		FSFree(m_pFreeHandle);
		m_pFreeHandle=pNext;
	}
}

void *CFSLockFreeFixAlloc::Alloc(){
	if (m_pFreeHandle){
		CFSFixAllocHandle *pBlock=m_pFreeHandle;
		m_pFreeHandle=m_pFreeHandle->m_pNext;
		m_lCacheSpace++;
		return pBlock;
	}
	return FSAlloc(m_ipBlockSize);
}

void CFSLockFreeFixAlloc::Free(void *pBlock){
	if (m_lCacheSpace<=0) {
		FSFree(pBlock);
	}
	else{
		CFSFixAllocHandle *pHandle=(CFSFixAllocHandle *)pBlock;
		pHandle->m_pNext=m_pFreeHandle;
		m_pFreeHandle=pHandle;
		m_lCacheSpace--;
	}
}

///////////////////////////////////////////////////////////
// CFSThreadBasedFixAlloc
///////////////////////////////////////////////////////////

CFSThreadBasedFixAlloc::CFSThreadBasedFixAlloc(INTPTR ipBlockSize, long lMaxCache)
{
	m_ipBlockSize=ipBlockSize;
	m_lCacheSpace=lMaxCache;
	m_pFixAllocChain=0;
}

CFSThreadBasedFixAlloc::~CFSThreadBasedFixAlloc()
{
	if (m_pFixAllocChain) {
		delete m_pFixAllocChain;
	}
}

CFSLockFreeFixAlloc *CFSThreadBasedFixAlloc::GetFixAlloc()
{
	FSTHREADID lThreadID=FSGetCurrentThreadID();
	for (CFixAllocChain *pChain=m_pFixAllocChain; pChain; pChain=pChain->m_pNext){
		if (lThreadID==pChain->m_lThreadID) {
			return &pChain->m_Alloc;
		}
	}
	CFSAutoLock AutoLock(&m_Mutex);
	CFixAllocChain *pElem=new CFixAllocChain(m_ipBlockSize, m_lCacheSpace);
	pElem->m_pNext=m_pFixAllocChain;
	m_pFixAllocChain=pElem;
	return &pElem->m_Alloc;
}
