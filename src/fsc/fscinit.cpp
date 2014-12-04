#include "stdfsc.h"
#include "fstype.h"

#include "fsstring.h"
#include "fsmemory.h"
#include "fsfixalloc.h"
#include "fscinit.h"

void __FSTestVariables() {
	STATIC_ASSERT(sizeof(INT8)==1);
	STATIC_ASSERT(sizeof(INT16)==2);
	STATIC_ASSERT(sizeof(INT32)==4);
	STATIC_ASSERT(sizeof(INT64)==8);
	STATIC_ASSERT(sizeof(WCHAR)>=2);
	STATIC_ASSERT((sizeof(LCHAR)==4)&&(0<(LCHAR)-1));
	STATIC_ASSERT(sizeof(INTPTR)==sizeof(void *));
}

#define __FSSTRINGALLOC(Size) \
	if (ipByteSize<=Size){ \
		pData=(CFSStringData *)(this ? m_Alloc##Size##b.Alloc() : FSAlloc(sizeof(CFSStringData)+Size)); \
		pData->m_ipBufSize=Size/ipCharSize; \
	}

#define __FSSTRINGFREE(Size) \
	if (ipByteSize==Size) m_Alloc##Size##b.Free(pData);

class CStringMemoryPool {
public:
	CStringMemoryPool() :
		m_Alloc32b(sizeof(CFSStringData)+32, 200),
		m_Alloc64b(sizeof(CFSStringData)+64, 150),
		m_Alloc128b(sizeof(CFSStringData)+128, 100),
		m_Alloc256b(sizeof(CFSStringData)+256, 50),
		m_Alloc512b(sizeof(CFSStringData)+512, 25) { }

	void *Alloc(INTPTR ipSize, INTPTR ipCharSize) {
		CFSStringData* pData=0;
#if defined (_DEBUG)
		pData=(CFSStringData *)FSAlloc(sizeof(CFSStringData)+ipSize*ipCharSize);
		pData->m_ipBufSize=ipSize;
#else
		INTPTR ipByteSize=ipSize*ipCharSize;
		__FSSTRINGALLOC(32)
		else __FSSTRINGALLOC(64)
		else __FSSTRINGALLOC(128)
		else __FSSTRINGALLOC(256)
		else __FSSTRINGALLOC(512)
		else{
			ipByteSize=(ipByteSize+1023)&(~1023);
			pData=(CFSStringData *)FSAlloc(sizeof(CFSStringData)+ipByteSize);
			pData->m_ipBufSize=ipByteSize/ipCharSize;
		}
#endif
		pData->m_iRefCount=1;
		pData->m_ipLength=0;
		return (void *)(pData+1);
	}

	void Free(void *pStr, INTPTR ipCharSize) {
		CFSStringData* pData=((CFSStringData *)pStr)-1;
#if defined (_DEBUG)
		FSUNUSED(ipCharSize);
		FSFree(pData);
#else
		INTPTR ipByteSize=pData->m_ipBufSize*ipCharSize;
		if (this) {
			__FSSTRINGFREE(32)
			else __FSSTRINGFREE(64)
			else __FSSTRINGFREE(128)
			else __FSSTRINGFREE(256)
			else __FSSTRINGFREE(512)
			else FSFree(pData);
		} else {
			FSFree(pData);
		}
#endif
	}

	CFSLockFreeFixAlloc m_Alloc32b;
	CFSLockFreeFixAlloc m_Alloc64b;
	CFSLockFreeFixAlloc m_Alloc128b;
	CFSLockFreeFixAlloc m_Alloc256b;
	CFSLockFreeFixAlloc m_Alloc512b;
};

#if defined (WINRT)
static __declspec(thread) CStringMemoryPool *g_FSStringMemoryPool=0;
#elif defined (WIN32)
static DWORD g_TlsKey=TLS_OUT_OF_INDEXES;
#elif defined (UNIX)
#define TLS_OUT_OF_INDEXES ((pthread_key_t)-1)
static pthread_key_t g_TlsKey=TLS_OUT_OF_INDEXES;

extern "C" void __FSCThreadTerminate(void *pData)
{
	if (pData) {
		CStringMemoryPool *pPool=(CStringMemoryPool *)pData;
		pthread_setspecific(g_TlsKey, 0);
		delete pPool;
	}
}
#endif

bool FSCInit() {
#if defined (WINRT)
	// Nothing to do.
#elif defined (WIN32)
	if (g_TlsKey==TLS_OUT_OF_INDEXES) {
		g_TlsKey=TlsAlloc();
	}
#elif defined (UNIX)
	if (g_TlsKey==TLS_OUT_OF_INDEXES) {
		if (pthread_key_create(&g_TlsKey, __FSCThreadTerminate)!=0) {
			g_TlsKey=TLS_OUT_OF_INDEXES;
		}
	}
#endif
	return FSCThreadInit();
}

void FSCTerminate() {
	FSCThreadTerminate();
#if defined (WINRT)
	// Nothing to do.
#elif defined (WIN32)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		TlsFree(g_TlsKey);
		g_TlsKey=TLS_OUT_OF_INDEXES;
	}
#elif defined (UNIX)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		pthread_key_delete(g_TlsKey);
		g_TlsKey=TLS_OUT_OF_INDEXES;
	}
#endif
}

bool FSCThreadInit() {
	CStringMemoryPool *pPool=new CStringMemoryPool();
#if defined (WINRT)
	if (!g_FSStringMemoryPool) {
		g_FSStringMemoryPool=pPool;
	} else 
#elif defined (WIN32)
	if (g_TlsKey==TLS_OUT_OF_INDEXES || TlsGetValue(g_TlsKey)!=0 || !TlsSetValue(g_TlsKey, pPool))
#elif defined (UNIX)
	if (g_TlsKey==TLS_OUT_OF_INDEXES || pthread_getspecific(g_TlsKey)!=0 || pthread_setspecific(g_TlsKey, pPool)!=0)
#endif
	{
		delete pPool;
		return false;
	}
	return true;
}

void FSCThreadTerminate() {
#if defined (WINRT)
	delete g_FSStringMemoryPool;
	g_FSStringMemoryPool=0;
#elif defined (WIN32)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		CStringMemoryPool *pPool=(CStringMemoryPool *)TlsGetValue(g_TlsKey);
		if (pPool) {
			TlsSetValue(g_TlsKey, 0);
			delete pPool;
		}
	}
#elif defined (UNIX)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		__FSCThreadTerminate(pthread_getspecific(g_TlsKey));
	}
#endif
}

#if defined (WIN32)
extern HINSTANCE g_hFSInst;
BOOL WINAPI FSDllMain(HINSTANCE hInstDLL, DWORD dwReason, LPVOID lpvReserved) {
	FSUNUSED(lpvReserved);
	switch (dwReason) {
		case DLL_PROCESS_ATTACH:
			g_hFSInst=hInstDLL;
			FSCInit();
			break;
		case DLL_THREAD_ATTACH:
			FSCThreadInit();
			break;
		case DLL_THREAD_DETACH:
			FSCThreadTerminate();
			break;
		case DLL_PROCESS_DETACH:
			FSCTerminate();
			break;
	} 
	return true;
}
#endif

static inline CStringMemoryPool *GetStringMemoryPool() {
#if defined (WINRT)
	return g_FSStringMemoryPool;
#elif defined (WIN32)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		return (CStringMemoryPool *)TlsGetValue(g_TlsKey);
	} else {
		return 0;
	}
#elif defined (UNIX)
	if (g_TlsKey!=TLS_OUT_OF_INDEXES) {
		CStringMemoryPool *pPool=(CStringMemoryPool *)pthread_getspecific(g_TlsKey);
		if (!pPool) {
			FSCThreadInit();
			pPool=(CStringMemoryPool *)pthread_getspecific(g_TlsKey);
		}
		return pPool;
	} else {
		return 0;
	}
#else
	return 0;
#endif
}

void *FSStringAlloc(INTPTR ipSize, INTPTR ipCharSize){
	return GetStringMemoryPool()->Alloc(ipSize, ipCharSize);
}

void FSStringFree(void *pStr, INTPTR ipCharSize){
	GetStringMemoryPool()->Free(pStr, ipCharSize);
}
