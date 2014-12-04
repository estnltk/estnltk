#if !defined _FSDLL_H_
#define _FSDLL_H_

#include "fsfile.h"

#if defined (WIN32)
#define FSDLL_EXPORT __declspec(dllexport)
#elif (__GNUC__ >= 4)
#define FSDLL_EXPORT __attribute__ ((visibility ("default")))
#else
#define FSDLL_EXPORT
#endif

/**
* Wrapper class for dynamic libraries (.dll/.so/.shlb).
*/
class CFSDll  
{
public:
	DECLARE_FSNOCOPY(CFSDll);
	
	CFSDll();

/**
* Initializes class and loads library. Throws exception on error.
* @param[in] FileName Name of the library.
*/
	CFSDll(const CFSFileName &FileName);

/**
* Uninitializes class and unloads dll if loaded. Ignores errors.
*/
	virtual ~CFSDll();

/**
* Loads library. Throws exception on error.
* @param[in] FileName Name of the library.
*/
	void LoadLibrary(const CFSFileName &FileName);

/**
* Unloads library. Throws exception on error.
*/
	void FreeLibrary();

/**
* Finds an address of symbol in dynamic library.
* @param[in] szProcName Name of the resource.
* @return address of the resource.
* @retval 0 Fail.
*/
	void *GetProcAddress(const CFSAString &szProcName) const;

protected:
#if defined (WIN32)
	HINSTANCE m_hDll;
#elif defined (UNIX)
	void *m_hDll;
#elif defined (MAC)
	void *m_hDll;
	CFBundleRef m_hDll2;
#endif
};

#endif // _FSDLL_H_
