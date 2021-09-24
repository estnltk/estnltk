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
#if !defined _FSCINIT_H_
#define _FSCINIT_H_

bool FSCInit();
void FSCTerminate();

bool FSCThreadInit();
void FSCThreadTerminate();

#if defined (WIN32)
BOOL WINAPI FSDllMain(HINSTANCE hInstDLL, DWORD dwReason, LPVOID lpvReserved);

#define FSDLL_ENTRYPOINT \
BOOL WINAPI DllMain(HINSTANCE hInstDLL, DWORD dwReason, LPVOID lpvReserved) { \
	TRACE(FSTSTR("DllMain(%d)\n"), (int)dwReason); \
	return FSDllMain(hInstDLL, dwReason, lpvReserved); \
}

#elif (__GNUC__ >= 4) || defined (__clang__)
#define FSDLL_ENTRYPOINT \
__attribute__ ((constructor)) void DllConstructor(void) { \
	TRACE(FSTSTR("DllConstructor()\n")); \
	FSCInit(); \
} \
__attribute__ ((destructor)) void DllDestructor(void) { \
	TRACE(FSTSTR("DllDestructor()\n")); \
	FSCTerminate(); \
}
#else
#define FSDLL_ENTRYPOINT
#endif

#endif // _FSCINIT_H_
