#include "stdfsc.h"
#include "fstype.h"

#include "fsmemory.h"

void FSThrowMemoryException();

void *FSAlloc(INTPTR nSize)
{
	if (nSize<0) {
		FSThrowMemoryException();
	}
	void *pBuf=malloc(nSize);
	if (!pBuf) {
		FSThrowMemoryException();
	}
	return pBuf;
}

void *FSReAlloc(void *pBuf, INTPTR nSize)
{
	if (nSize<0) {
		FSThrowMemoryException();
	}
	void *pBuf2=realloc(pBuf, nSize);
	if (nSize && !pBuf2) {
		FSThrowMemoryException();
	}
	return pBuf2;
}

void FSFree(void *pBuf)
{
	free(pBuf);
}

#if !defined (_DEBUG) && !defined (FSNONEW) && !defined (__BOUNDSCHECKER__)

void *operator new(size_t nSize)
{
	return FSAlloc(nSize);
}

void *operator new[](size_t nSize)
{
	return FSAlloc(nSize);
}

void operator delete(void* pBuf)
{
	FSFree(pBuf);
}

#endif
