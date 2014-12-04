#if !defined _FSBLOCKALLOC_H_
#define _FSBLOCKALLOC_H_

#include "fsmemory.h"

struct __FSNewPtr { };

inline void *operator new(size_t, __FSNewPtr *pMem) {
	return (void *)pMem;
}
inline void *operator new[](size_t, __FSNewPtr *pMem) {
	return (void *)pMem;
}
inline void operator delete(void *, __FSNewPtr *) { }

template <class ITEM>
class CFSBlockAlloc
{
public:
	static ITEM *Alloc(INTPTR ipSize) {
		return (ITEM *)FSAlloc(ipSize*sizeof(ITEM));
	}
	static void Init(ITEM *pDest, INTPTR ipCount) {
		for (INTPTR ip=0; ip<ipCount; ip++) {
			new ((__FSNewPtr *)(pDest+ip)) ITEM();
		}
	}
	static void Terminate(ITEM *pDest, INTPTR ipCount) {
		for (INTPTR ip=0; ip<ipCount; ip++) {
			pDest[ip].~ITEM();
		}
	}
	static void Free(ITEM *pBlock, INTPTR ipDestructFirst=0, INTPTR ipDestructCount=0) {
		Terminate(pBlock+ipDestructFirst, ipDestructCount);
		FSFree(pBlock);
	}
	static void AssignCopy(ITEM *pDest, const ITEM *pSource, INTPTR ipCount) {
		for (INTPTR ip=0; ip<ipCount; ip++) {
			new ((__FSNewPtr *)(pDest+ip)) ITEM(pSource[ip]);
		}
	}
	static void AssignMove(ITEM *pDest, ITEM *pSource, INTPTR ipCount) {
		for (INTPTR ip=0; ip<ipCount; ip++) {
			new ((__FSNewPtr *)(pDest+ip)) ITEM(FSMove(pSource[ip]));
		}
	}
	static void Copy(ITEM *pDest, const ITEM *pSource, INTPTR ipCount) {
		if ((UINTPTR)(pDest-pSource)<(UINTPTR)ipCount){
			for (INTPTR ip=ipCount-1; ip>=0; ip--) {
				pDest[ip]=pSource[ip];
			}
		}
		else{
			for (INTPTR ip=0; ip<ipCount; ip++) {
				pDest[ip]=pSource[ip];
			}
		}
	}
	static void Move(ITEM *pDest, ITEM *pSource, INTPTR ipCount) {
		if ((UINTPTR)(pDest-pSource)<(UINTPTR)ipCount){
			for (INTPTR ip=ipCount-1; ip>=0; ip--) {
				pDest[ip]=FSMove(pSource[ip]);
			}
		}
		else{
			for (INTPTR ip=0; ip<ipCount; ip++) {
				pDest[ip]=FSMove(pSource[ip]);
			}
		}
	}
};

#endif
