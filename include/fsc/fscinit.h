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
