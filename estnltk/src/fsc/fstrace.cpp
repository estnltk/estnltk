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

#include "fstrace.h"

void __FSTrace(const TCHAR *pszFormat, ...)
{
	va_list args;
	va_start(args, pszFormat);

#if defined (WIN32)
	TCHAR szBuffer[1024];
	#if defined (UNICODE)
		_vsnwprintf_s(szBuffer, 1024, 1023, pszFormat, args);
	#else
		_vsnprintf_s(szBuffer, 1024, 1023, pszFormat, args);
	#endif
	szBuffer[1023]=0;
	OutputDebugString(szBuffer);
#elif defined (MAC)
	TCHAR szBuffer[257];
	vsnprintf(szBuffer+1, 253, pszFormat, args);
	strcat(szBuffer+1, ";g");
	szBuffer[0]=(UCHAR)strlen(szBuffer+1);
	DebugStr((UCHAR *)szBuffer);
#elif defined (UNIX)
	vfprintf(stderr, pszFormat, args);
#endif

	va_end(args);
}

void __FSTraceFileV(const TCHAR *pszFile, const TCHAR *pszFormat, va_list Args)
{
#if defined (UNICODE)
	FILE *f=_wfsopen(pszFile, FSWSTR("at"), _SH_DENYRW);
#elif defined (WIN32)
	FILE *f=_fsopen(pszFile, "at", _SH_DENYRW);
#else
	FILE *f=fopen(pszFile, "at");
#endif
	if (f){
#if defined (UNICODE)
		vfwprintf(f, pszFormat, Args);
#else
		vfprintf(f, pszFormat, Args);
#endif
		fclose(f);
	}
}
