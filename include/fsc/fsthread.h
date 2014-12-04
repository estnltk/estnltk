#if !defined _THREAD_H_
#define _THREAD_H_

#include "fsutil.h"
#include "fsexception.h"

#if defined (SOLARIS)
	#include <atomic.h>
	#define INTATOMIC int
#elif defined (UNIX)
//#if defined (__GCC_HAVE_SYNC_COMPARE_AND_SWAP_4)
#if defined (__GNUC__) && ((__GNUC__*100 + __GNUC_MINOR__) >= 402)
	#define INTATOMIC INT32
#else
	#include <bits/atomicity.h>
	#define INTATOMIC _Atomic_word
	namespace __gnu_cxx{ }
#endif
#elif defined (MAC)
	// <libkern/OSAtomic.h> MAC 10.4 (BSD?) 
	#define INTATOMIC SInt32
#else
	#define INTATOMIC long
#endif

INTATOMIC __FSAtomicAddSlow(INTATOMIC *pVar, INTATOMIC iAdd);

/**
* Atomically adds value to a specified variable. No other thread can access the variable while operation takes place.
* @param[in, out] pVar A pointer to variable that is to have iAdd added to it.
* @param[in] iAdd Value to be added to the pVar.
* @return Sum of two variables.
* @sa FSAtomicInc, FSAtomicDec.
*/
inline INTATOMIC FSAtomicAdd(INTATOMIC *pVar, INTATOMIC iAdd){
#if defined (WIN32) // NB! Requires Win98/NT4 or newer
	return InterlockedExchangeAdd(pVar, iAdd)+iAdd;
#elif defined (SOLARIS)
	return atomic_add_int_nv((uint_t *)pVar, iAdd);
#elif defined (UNIX)
//#if defined (__GCC_HAVE_SYNC_COMPARE_AND_SWAP_4)
#if defined (__GNUC__) && ((__GNUC__*100 + __GNUC_MINOR__) >= 402)
	return __sync_fetch_and_add(pVar, iAdd)+iAdd;
#else
	using namespace __gnu_cxx;	// gcc 3.4 has moved the function under namespace
	return __exchange_and_add(pVar, iAdd)+iAdd;
#endif
#elif defined (MAC)
	// OSAtomicAdd32Barrier
	return AddAtomic(iAdd, pVar)+iAdd;
#else
	return __FSAtomicAddSlow(pVar, iAdd); // Slow add with Mutex lock
#endif
}

/**
* Atomically increments a specified variable. No other thread can access the variable while incremented.
* @param[in, out] pVar a pointer to variable that will be incremented.
* @retval 0 Result of increment is exactly 0.
* @retval <0 Result of increment is negative.
* @retval >0 Result of increment is positive.
* @sa FSAtomicDec, FSAtomicAdd.
*/
inline INTATOMIC FSAtomicInc(INTATOMIC *pVar){
#if defined (WIN32)
	return InterlockedIncrement(pVar);
#else
	return FSAtomicAdd(pVar, 1);
#endif
}

/**
* Atomically decrements a specified variable. No other thread can access the variable while decremented.
* @param[in, out] pVar a pointer to variable that will be decremented.
* @retval 0 Result of decrement is exactly 0.
* @retval <0 Result of decrement is negative.
* @retval >0 Result of decrement is positive.
* @sa FSAtomicInc, FSAtomicAdd.
*/
inline INTATOMIC FSAtomicDec(INTATOMIC *pVar){
#if defined (WIN32)
	return InterlockedDecrement(pVar);
#else
	return FSAtomicAdd(pVar, -1);
#endif
}

/**
* Basic interface for synchronization objects.
* @sa CFSMutex, CFSQMutex, CFSAutoLock
*/
class IFSMutex{
public:
/**
* Locks mutex
* @param[in] lTimeout Max time in milliseconds to wait for lock.
* -1 means infinite wait.
* Some implementations may ignore the parameter.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	virtual int Lock(ULONG lTimeout) = 0;

/**
* Unlocks mutex.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	virtual int Unlock() = 0;
};

/**
* Typical sync object, supports reentrance.
* @sa IFSMutex, CFSQMutex, CFSAutoLock.
*/
class CFSMutex : public IFSMutex{
public:
	DECLARE_FSNOCOPY(CFSMutex);
	
	CFSMutex();
	virtual ~CFSMutex();
/**
* @param[in] lTimeout Platform: Mac.
*/
	int Lock(ULONG lTimeout);
	int Unlock();

protected:
#if defined (WIN32)
	CRITICAL_SECTION m_hMutex;
#elif defined (UNIX)
	pthread_mutex_t m_hMutex;
#elif defined (MAC)
	MPCriticalRegionID m_hMutex;
#endif
};

/**
* Fastest sync object, may not support reentrance.
* @sa IFSMutex, CFSMutex, CFSAutoLock
*/
#if defined (WIN32)
typedef CFSMutex CFSQMutex; // CFSMutex is very fast on WIN32
#else
class CFSQMutex : public IFSMutex{
public:
	CFSQMutex() { m_lLock=-1; }

/**
* @param[in] lTimeout Ignored.
*/
	int Lock(ULONG lTimeout){
		FSUNUSED(lTimeout);
		for (;;) {
			if (FSAtomicInc(&m_lLock)==0) {
				return 0;
			}
			FSAtomicDec(&m_lLock);
		}
	}
	int Unlock(){
		FSAtomicDec(&m_lLock);
		return 0;
	}
protected:
	INTATOMIC m_lLock;
};
#endif

/**
* Helper class that locks mutex on creation and unlocks on deletion.
*/
class CFSAutoLock{
public:
/**
* Constructor locks mutex, there is no timeout for lock.
* @param[in] pMutex Pointer to a mutex that will be locked.
*/
	CFSAutoLock(IFSMutex *pMutex);

	CFSAutoLock(const CFSAutoLock &AutoLock);
/**
* Destructor unlocks mutex.
*/
	virtual ~CFSAutoLock();

	CFSAutoLock &operator =(const CFSAutoLock &AutoLock);

protected:
	IFSMutex *m_pMutex;
};

///////////////////////////////////////////////////////////
// Thread
///////////////////////////////////////////////////////////

/**
* Implements thread functionality.
*/
class CFSThread{
public:
/**
* Thtead priority constants.
* Platforms Win, Mac.
*/
#if defined (WIN32)
	enum ePriority {
		PRIORITY_IDLE=THREAD_PRIORITY_IDLE,
		PRIORITY_LOWEST=THREAD_PRIORITY_LOWEST,
		PRIORITY_LOW=THREAD_PRIORITY_BELOW_NORMAL,
		PRIORITY_NORMAL=THREAD_PRIORITY_NORMAL,
		PRIORITY_HIGH=THREAD_PRIORITY_ABOVE_NORMAL,
		PRIORITY_HIGHEST=THREAD_PRIORITY_HIGHEST,
		PRIORITY_RELATIME=THREAD_PRIORITY_TIME_CRITICAL };
#elif defined (MAC)
	enum ePriority {
		PRIORITY_IDLE=1,
		PRIORITY_LOWEST=5,
		PRIORITY_LOW=25,
		PRIORITY_NORMAL=100,
		PRIORITY_HIGH=400,
		PRIORITY_HIGHEST=2000,
		PRIORITY_RELATIME=10000 };
#endif
	DECLARE_FSNOCOPY(CFSThread);
	
	CFSThread();
	virtual ~CFSThread();

/**
* Creates thread and launches Run function.
* @param[in] pData Custom data that is stored in m_pData and is accessible in Run function.
* @param[in] lFlags Win-only parameter, that is forwarded to ::CreateThread.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int Create(void *pData, long lFlags=0);

/**
* Sets thread priority.
* Platforms Win, Mac.
* @param[in] iPriority Thread priority. Use one of ePriority values.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int SetPriority(int iPriority);

/**
* Pauses thread.
* Platforms Win, Unix.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int Pause();

/**
* Resumes thread.
* Platforms Win, Unix.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int Resume();

/**
* Faits for thread execution end.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int WaitForEnd();

protected:
/**
* Function that will be executed in created thread's context Override this function.
* @retval 0 Reserved.
*/
	virtual int Run() = 0;

	void *m_pData;
#if defined (WIN32CE)
	static ULONG __stdcall CFSThreadFunc(void *pvThread);
	HANDLE m_hThread;
	DWORD m_lThreadID;
#elif defined (WIN32)
	static UINT __stdcall CFSThreadFunc(void *pvThread);
	HANDLE m_hThread;
	UINT m_lThreadID;
#elif defined (UNIX)
	static void *CFSThreadFunc(void *pvThread);
	pthread_t m_hThread;
#elif defined (MAC)
	static OSStatus CFSThreadFunc(void *pvThread);
	MPTaskID m_hThread;
	MPQueueID m_WaitQueue;
#endif
};

#if defined (WIN32)
	#define FSTHREADID DWORD
#elif defined (UNIX)
	#define FSTHREADID pthread_t
#elif defined (MAC)
	#define FSTHREADID MPTaskID
#endif

/**
* Returns identificator of current thread.
* @return The ID of the thread.
*/
inline FSTHREADID FSGetCurrentThreadID(){
#if defined (WIN32)
	return GetCurrentThreadId();
#elif defined (UNIX)
	return pthread_self();
#elif defined (MAC)
	return MPCurrentTaskID();
#endif
}

#endif // _THREAD_H_
