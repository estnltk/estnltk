#if !defined _FSTRACE_H_
#define _FSTRACE_H_

void __FSTrace(const TCHAR *pszFormat, ...);
void __FSTraceFileV(const TCHAR *pszFile, const TCHAR *pszFormat, va_list Args);

#if defined (_DEBUG) || defined (FSDOTRACE)
	#if !defined (TRACE)
		#if defined (TRACEFILE)
			inline void __FSTraceFile(const FSTCHAR *pszFormat, ...){
				va_list args;
				va_start(args, pszFormat);
				__FSTraceFileV(TRACEFILE, pszFormat, args);
				va_end(args);
			}
			#define TRACE ::__FSTraceFile
		#else // !TRACEFILE
			#define TRACE ::__FSTrace
		#endif // TRACEFILE
	#endif // TRACE
	#if !defined (ASSERT)
		#if defined (WIN32CE)
			#define ASSERT(exp) if (!(exp)) { TRACE(FSTSTR("Assertion failed: %s (%s:%d)\n"), #exp, __FILE__, __LINE__); DebugBreak(); }
		#else
			#include <assert.h>
			#define ASSERT(exp) assert(exp)
		#endif
	#endif
	#if !defined (VERIFY)
		#define VERIFY(exp) ASSERT(exp)
	#endif
#endif

#if !defined (STATIC_ASSERT)
	#if defined (__FSCXX0X)
		#define STATIC_ASSERT(exp) static_assert(exp, #exp)
	#else
		inline int __FSTestDiv0(int iTest) { return iTest; }
		#define STATIC_ASSERT(exp) __FSTestDiv0(1/(int)(exp))
	#endif
#endif

#if !defined (TRACE)
	#if (_MSC_VER>=1300)
		#define TRACE __noop
	#else
		#define TRACE(...)
		//#define TRACE ((void)0);
		//#define TRACE 1 ? (void)0 : ::__FSTrace
	#endif
#endif // TRACE
#if !defined (ASSERT)
	#define ASSERT(exp)
#endif // ASSERT
#if !defined (VERIFY)
	#define VERIFY(exp) ((void)(exp))
#endif

#endif // !defined (_FSTRACE_H_)
