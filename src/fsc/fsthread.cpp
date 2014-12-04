#include "stdfsc.h"
#include "fstype.h"

#include "fsthread.h"

///////////////////////////////////////////////////////////
// Mutex
///////////////////////////////////////////////////////////

CFSMutex::CFSMutex()
{
#if defined (WINRT)
	InitializeCriticalSectionEx(&m_hMutex, 0, 0);
#elif defined (WIN32)
	InitializeCriticalSection(&m_hMutex);
#elif defined (UNIX)
	pthread_mutexattr_t attr;
	pthread_mutexattr_init(&attr);
	pthread_mutex_init(&m_hMutex, &attr);
	pthread_mutexattr_destroy(&attr);
#elif defined (MAC)
	MPCreateCriticalRegion(&m_hMutex);
#endif
}

CFSMutex::~CFSMutex()
{
#if defined (WIN32)
	DeleteCriticalSection(&m_hMutex);
#elif defined (UNIX)
	pthread_mutex_destroy(&m_hMutex);
#elif defined (MAC)
	MPDeleteCriticalRegion(m_hMutex);
#endif
}

int CFSMutex::Lock(ULONG lTimeout)
{
#if defined (WIN32)
	FSUNUSED(lTimeout);
	::EnterCriticalSection(&m_hMutex);
#elif defined (UNIX)
	FSUNUSED(lTimeout);
	pthread_mutex_lock(&m_hMutex); 
#elif defined (MAC)
	MPEnterCriticalRegion(m_hMutex, (lTimeout == -1 ? kDurationForever : lTimeout));
#endif
	return 0;
}

int CFSMutex::Unlock()
{
#if defined (WIN32)
	::LeaveCriticalSection(&m_hMutex);
#elif defined (UNIX)
	pthread_mutex_unlock(&m_hMutex);
#elif defined (MAC)
	MPExitCriticalRegion(m_hMutex);
#endif
	return 0;
}

///////////////////////////////////////////////////////////
// AutoLock
///////////////////////////////////////////////////////////

CFSAutoLock::CFSAutoLock(IFSMutex *pMutex)
{
	m_pMutex=pMutex;
	if (m_pMutex) {
		m_pMutex->Lock((ULONG)-1);
	}
}

CFSAutoLock::CFSAutoLock(const CFSAutoLock &AutoLock)
{
	m_pMutex=AutoLock.m_pMutex;
	if (m_pMutex) {
		m_pMutex->Lock((ULONG)-1);
	}
}

CFSAutoLock::~CFSAutoLock()
{
	if (m_pMutex) {
		m_pMutex->Unlock();
	}
}

CFSAutoLock &CFSAutoLock::operator =(const CFSAutoLock &AutoLock)
{
	if (this!=&AutoLock) {
		if (m_pMutex) {
			m_pMutex->Unlock();
		}
		m_pMutex=AutoLock.m_pMutex;
		if (m_pMutex) {
			m_pMutex->Lock((ULONG)-1);
		}
	}
	return *this;
}

///////////////////////////////////////////////////////////
// Thread
///////////////////////////////////////////////////////////

CFSThread::CFSThread()
{
	m_pData=0;
	m_hThread=0;
#if defined (MAC)
	MPCreateQueue(&m_WaitQueue);
#endif
}

CFSThread::~CFSThread()
{
#if defined (MAC)
	MPDeleteQueue(m_WaitQueue);
#endif
}

#if defined (WIN32CE)
ULONG __stdcall CFSThread::CFSThreadFunc(void *pvThread)
#elif defined (WIN32)
UINT __stdcall CFSThread::CFSThreadFunc(void *pvThread)
#elif defined (UNIX)
void *CFSThread::CFSThreadFunc(void *pvThread)
#elif defined (MAC)
OSStatus CFSThread::CFSThreadFunc(void *pvThread)
#endif
{
	CFSThread *pThread=(CFSThread *)pvThread;
	pThread->Run();
	return 0;
}

int CFSThread::Create(void *pData, long lFlags)
{
	m_pData=pData;
#if defined (WIN32CE)
	m_hThread=CreateThread(NULL, 0, CFSThreadFunc, this, lFlags, &m_lThreadID);
	return (m_hThread==0);
#elif defined (WINRT)
	// Unimplemented
	FSUNUSED(pData);
	FSUNUSED(lFlags);
	return -1;
#elif defined (WIN32)
	m_hThread=(HANDLE)_beginthreadex(NULL, 0, CFSThreadFunc, this, lFlags, &m_lThreadID);
	return (m_hThread==0);
#elif defined (UNIX)
	FSUNUSED(lFlags);
	return pthread_create(&m_hThread, 0, CFSThreadFunc, this);
#elif defined (MAC)
	FSUNUSED(lFlags);
	return MPCreateTask(CFSThreadFunc, this, 512*1024, m_WaitQueue, 0, 0, 0,&m_hThread);
#endif
}

int CFSThread::SetPriority(int iPriority)
{
	if (!m_hThread) {
		return -1;
	}
#if defined (WINRT)
	// Unimplemented
	FSUNUSED(iPriority);
#elif defined (WIN32)
	::SetThreadPriority(m_hThread, iPriority);
#elif defined (UNIX)
	// Unimplemented
	FSUNUSED(iPriority);
#elif defined (MAC)
	MPSetTaskWeight(m_hThread, iPriority);
#endif
	return 0;
}

int CFSThread::Pause(){
	if (!m_hThread) {
		return -1;
	}
#if defined (WINRT)
	// Unimplemented
#elif defined (WIN32)
	::SuspendThread(m_hThread);
#elif defined (UNIX)
	pthread_kill(m_hThread, SIGSTOP);
#elif defined (MAC)
	// Unimplemented
#endif
	return 0;
}

int CFSThread::Resume()
{
	if (!m_hThread) {
		return -1;
	}
#if defined (WINRT)
	// Unimplemented
#elif defined (WIN32)
	::ResumeThread(m_hThread);
#elif defined (UNIX)
	pthread_kill(m_hThread, SIGCONT);
#elif defined (MAC)
	// Unimplemented
#endif
	return 0;
}

int CFSThread::WaitForEnd()
{
	if (m_hThread) {
#if defined (WIN32)
		WaitForSingleObjectEx(m_hThread, INFINITE, false);
		CloseHandle(m_hThread);
#elif defined (UNIX)
		pthread_join(m_hThread, 0);
#elif defined (MAC)
		OSStatus err;
	    MPWaitOnQueue(m_WaitQueue, NULL, NULL, (void**) &err, kDurationForever);
#endif
	}
	return 0;
}

///////////////////////////////////////////////////////////
// Atomic functions
///////////////////////////////////////////////////////////

INTATOMIC __FSAtomicAddSlow(INTATOMIC *pVar, INTATOMIC lAdd)
{
	static CFSMutex Mutex;
	CFSAutoLock AutoLock(&Mutex);
	(*pVar)+=lAdd;
	return *pVar;
}
