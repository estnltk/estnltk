#if !defined _FSTYPE_H_
#define _FSTYPE_H_

#include <stddef.h>

#if !defined (CHAR)
	#define CHAR char
#endif
#if !defined (UCHAR)
	#define UCHAR unsigned char
#endif
#if !defined (SHORT)
	#define SHORT short
#endif
#if !defined (USHORT)
	#define USHORT unsigned short
#endif
#if !defined (INT)
	#define INT int
#endif
#if !defined (UINT)
	#define UINT unsigned int
#endif
#if !defined (LONG)
	#define LONG long
#endif
#if !defined (ULONG)
	#define ULONG unsigned long
#endif
#if !defined (LONGLONG)
	#if defined (WIN32)
		#define LONGLONG __int64
	#elif defined (UNIX) || defined (MAC)
		#define LONGLONG long long
	#endif
#endif
#if !defined (ULONGLONG)
	#if defined (WIN32)
		#define ULONGLONG unsigned __int64
	#elif defined (UNIX) || defined (MAC)
		#define ULONGLONG unsigned long long
	#endif
#endif

#if !defined (BYTE)
	#define BYTE unsigned char
#endif

#if !defined (WCHAR)
	#define WCHAR wchar_t
#endif
#if !defined (LCHAR)
	#define LCHAR UINT32
#endif
#if !defined (TCHAR)
	#if defined (UNICODE)
		#define TCHAR WCHAR
	#else
		#define TCHAR char
	#endif
#endif
#if !defined (FSTSTR)
	#if defined (UNICODE)
		#define FSTSTR(X) L##X
	#else
		#define FSTSTR(X) X
	#endif
#endif

#if !defined (INT8)
	#define INT8 signed char
#endif
#if !defined (UINT8)
	#define UINT8 unsigned char
#endif
#if !defined (INT16)
	#define INT16 signed short
#endif
#if !defined (UINT16)
	#define UINT16 unsigned short
#endif
#if !defined (INT32)
	#define INT32 signed int
#endif
#if !defined (UINT32)
	#define UINT32 unsigned int
#endif
#if !defined (INT64)
	#define INT64 LONGLONG
#endif
#if !defined (UINT64)
	#define UINT64 ULONGLONG
#endif

#if !defined (INTPTR)
	#define INTPTR ptrdiff_t
#endif
#if !defined (UINTPTR)
	#define UINTPTR size_t
#endif

#if defined (WIN32)
	#define LL(X) X##i64
#else
	#define LL(X) X##LL
#endif

#define FSWCHAR WCHAR
#define FSTCHAR TCHAR
#define FSWSTR(X) L##X

#endif // _FSTYPE_H_
