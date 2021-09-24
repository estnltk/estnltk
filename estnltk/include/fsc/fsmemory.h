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
#if !defined _FSMEMORY_H_
#define _FSMEMORY_H_

/**
* Allocates memory, acts like malloc().
* In case of insufficient memory throws exception.
* @param[in] nSize Requested size of the block.
* @return address of newly allocated memory block.
* @sa FSReAlloc, FSFree
*/
void *FSAlloc(INTPTR nSize);

/**
* Changes memory block size, acts like realloc().
* In case of insufficient memory throws exception.
* @param[in] pBuf Memory block that will be resized.
* @param[in] nSize Requested size of the block.
* @return address of newly allocated memory block.
* @sa FSAlloc, FSFree
*/
void *FSReAlloc(void *pBuf, INTPTR nSize);

/**
* Frees memory allocated by FS(Re)Alloc, acts like free().
* @param[in] pBuf Memory to be released.
* @sa FSAlloc, FSReAlloc
*/
void FSFree(void *pBuf);

#endif
