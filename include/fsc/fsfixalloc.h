#if !defined _FSFIXALLOC_H_
#define _FSFIXALLOC_H_

#include "fsthread.h"
#include "fsmemory.h"

/**
* Fast memory allocator for const-sized memory blocks.
* fastest, thread-UNSAFE, no garbage.
* @sa CFSFixAlloc, CFSThreadBasedFixAlloc.
*/
class CFSLockFreeFixAlloc{
public:
	DECLARE_FSNOCOPY(CFSLockFreeFixAlloc);
/**
* Creates memory pool.
* @param ipBlockSize Memory block size in bytes.
* @param lMaxCache Maximum number of blocks to keep in pool.
*/
	CFSLockFreeFixAlloc(INTPTR ipBlockSize, long lMaxCache);
	virtual ~CFSLockFreeFixAlloc();

/**
* Retrieves free memory block.
* @return Address of the block.
*/
	void *Alloc();

/**
* Puts memory block back to pool.
* @param pBlock Address of the block to be released.
*/
	void Free(void *pBlock);

protected:
	struct CFSFixAllocHandle{
		CFSFixAllocHandle *m_pNext;
	}*m_pFreeHandle;
	INTPTR m_ipBlockSize;
	long m_lCacheSpace;
};

/**
* Fast memory allocator for const-sized memory blocks.
* slow, one pool, thread-safe, no garbage.
* @sa CFSLockFreeFixAlloc, CFSThreadBasedFixAlloc.
*/
class CFSFixAlloc : public CFSLockFreeFixAlloc {
public:
/**
* Creates memory pool.
* @param ipBlockSize Memory block size in bytes.
* @param lMaxCache Maximum number of blocks to keep in pool.
*/
	CFSFixAlloc(INTPTR ipBlockSize, long lMaxCache) : CFSLockFreeFixAlloc(ipBlockSize, lMaxCache) { }

/**
* Retrieves free memory block.
* @return Address of the block.
*/
	void *Alloc(){
		if (!m_pFreeHandle) {
			return FSAlloc(m_ipBlockSize);
		}
		CFSAutoLock AutoLock(&m_Mutex);
		return CFSLockFreeFixAlloc::Alloc();
	}

/**
* Puts memory block back to pool.
* @param pBlock Address of the block to be released.
*/
	void Free(void *pBlock){
		if (m_lCacheSpace<=0) { 
			FSFree(pBlock); 
			return; 
		}
		CFSAutoLock AutoLock(&m_Mutex);
		CFSLockFreeFixAlloc::Free(pBlock);
	}

protected:
	CFSQMutex m_Mutex;
};

/**
* Fast memory allocator for const-sized memory blocks.
* fast, multi-pool, thread-safe, garbage danger.
* @sa CFSLockFreeFixAlloc, CFSFixAlloc.
*/
class CFSThreadBasedFixAlloc
{
public:
	DECLARE_FSNOCOPY(CFSThreadBasedFixAlloc);

/**
* Creates memory pool.
* @param ipBlockSize Memory block size in bytes.
* @param lMaxCache Maximum number of blocks to keep in pool for every thread.
*/
	CFSThreadBasedFixAlloc(INTPTR ipBlockSize, long lMaxCache);
	virtual ~CFSThreadBasedFixAlloc();

/**
* Retrieves free memory block.
* @return Address of the block.
*/
	void *Alloc() { 
		return GetFixAlloc()->Alloc(); 
	}

/**
* Puts memory block back to pool.
* @param pBlock Address of the block to be released.
*/
	void Free(void *pBlock) { 
		GetFixAlloc()->Free(pBlock); 
	}

protected:
	CFSLockFreeFixAlloc *GetFixAlloc();

	class CFixAllocChain{
	public:
		CFixAllocChain(INTPTR ipBlockSize, long lMaxCache)
		: m_Alloc(ipBlockSize, lMaxCache) { 
			m_pNext=0; 
			m_lThreadID=FSGetCurrentThreadID(); 
		}
		~CFixAllocChain() { 
			if (m_pNext) {
				delete m_pNext; 
			}
		}

		CFixAllocChain *m_pNext;
		FSTHREADID m_lThreadID;
		CFSLockFreeFixAlloc m_Alloc;
	}*m_pFixAllocChain;

	INTPTR m_ipBlockSize;
	long m_lCacheSpace;
	CFSQMutex m_Mutex;
};

/**
* Helper macro to declare any class to use fix-alloc pool.
*/
#if defined (_DEBUG)
	#define DECLARE_FSFIXALLOC(Class, Allocator, MaxCache)
#else
	#define DECLARE_FSFIXALLOC(Class, Allocator, MaxCache) \
	public: \
		void *operator new(size_t) { return __GetFSFixAlloc().Alloc(); } \
		void operator delete(void *p) { __GetFSFixAlloc().Free(p); } \
	protected: \
		static Allocator &__GetFSFixAlloc() { static Allocator Alloc(sizeof(Class), MaxCache); return Alloc; }
#endif // _DEBUG

#endif // _FSFIXALLOC_H_
