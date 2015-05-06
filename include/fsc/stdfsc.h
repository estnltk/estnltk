#if !defined _STDFSC_H_
#define _STDFSC_H_

#if defined (_WIN32_WCE) // MS eMbedded Visual C++ 3|4
	#if !defined (WIN32CE)
		#define WIN32CE 
	#endif
	#if !defined (WIN32)
		#define WIN32
	#endif
#endif

#if defined (_WIN64) && !defined (WIN64) // MS Visual C++ 7
	#define WIN64
	#if !defined (WIN32)
		#define WIN32
	#endif
#endif

#if defined (_WIN32) && !defined (WIN32) // MS Visual C++ 6|7
	#define WIN32
#endif

#if defined (unix) && !defined (UNIX) // gcc 3.x / 2.95 for Solaris
	#define UNIX
#endif

#if defined (macintosh) && !defined (MAC) // CodeWarrior 6|8
	#define MAC
#endif

#if defined (_UNICODE) && !defined (UNICODE)
	#define UNICODE
#endif
#if defined (UNICODE) && !defined (_UNICODE)
	#define _UNICODE
#endif

#if defined (WIN32CE)
	#include <windows.h>
	#include <stdio.h>
#elif defined (WIN32)
	#include <windows.h>
	#include <stdio.h>
	#include <math.h>
	#include <process.h>
	#include <share.h>
	#if defined (WINAPI_FAMILY) 
		#if (WINAPI_FAMILY == WINAPI_FAMILY_APP)
			#define WINRT
		#endif
	#endif
#elif defined (UNIX)
	#include <stdio.h>
	#include <stdlib.h>
	#include <stdarg.h>
	#include <string.h>
	#include <ctype.h>
	#include <wchar.h>
	#include <math.h>
	#include <pthread.h>
	#include <signal.h>
	#include <dlfcn.h>
	#include <sys/time.h>
#elif defined (MAC)
	#include <stdio.h>
	#include <stdlib.h>
	#include <stdarg.h>
	#include <string.h>
	#include <ctype.h>
	#include <wchar.h>
	#include <dlfcn.h>
#else
	#error Only Win32(CE), Unix and Mac are currently supported.
#endif

#if (_MSC_VER >= 1600) || defined (__GXX_EXPERIMENTAL_CXX0X__)
	#define __FSCXX0X
#endif

#if !defined (__FSCXX0X) && defined (__has_feature)
	#if __has_feature(cxx_rvalue_references) && __has_feature(cxx_static_assert)
		#define __FSCXX0X
	#endif
#endif

#if defined (__FSCXX0X)
#include <utility>
#define FSMove(X) std::move(X)
/*template <class T> struct __FSRemoveReference { typedef T type; };
template <class T> struct __FSRemoveReference<T&> { typedef T type; };
template <class T> struct __FSRemoveReference<T&&> { typedef T type; };
template <class T> inline typename __FSRemoveReference<T>::type&& FSMove(T&& t) {
	return ((typename __FSRemoveReference<T>::type&&)t);
}

template<class T> struct __FSIdentity { typedef T type;
	const T& operator()(const T& t) const { return (t); }
};
template<class T> inline T&& FSForward(typename __FSIdentity<T>::type& t) {
	return ((T&&)t);
}*/
#else
#define FSMove(X) X
#endif

#endif // _STDFSC_H_
