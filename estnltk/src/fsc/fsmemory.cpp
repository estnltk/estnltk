/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
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
