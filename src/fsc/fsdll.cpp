#include "stdfsc.h"
#include "fstype.h"

#include "fsdll.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CFSDll::CFSDll()
{
	m_hDll=0;
#if defined (MAC)
	m_hDll2=0;
#endif
}

CFSDll::CFSDll(const CFSFileName &FileName)
{
	m_hDll=0;
#if defined (MAC)
	m_hDll2=0;
#endif
	LoadLibrary(FileName);
}

CFSDll::~CFSDll()
{
	IGNORE_FSEXCEPTION( FreeLibrary(); )
}

void CFSDll::LoadLibrary(const CFSFileName &FileName)
{
	FreeLibrary();
#if defined (WINRT)
	m_hDll=::LoadPackagedLibrary(FileName, 0);
#elif defined (WIN32)
	m_hDll=::LoadLibrary(FileName);
#elif defined (UNIX)
	m_hDll=dlopen(FileName, RTLD_LAZY);
#elif defined (MAC)
	m_hDll=dlopen(FileName, RTLD_LAZY);
	if (!m_hDll) {
		CFStringRef fsrFileName=CFStringCreateWithCString (kCFAllocatorDefault, FileName, kCFStringEncodingUTF8);
		if (fsrFileName) {
			CFURLRef urlFileName=CFURLCreateWithFileSystemPath(kCFAllocatorDefault, fsrFileName, kCFURLPOSIXPathStyle, false);
			if (urlFileName) {
				m_hDll2=CFBundleCreate(kCFAllocatorDefault, urlFileName);
				if (m_hDll2) {
					if (!CFBundleLoadExecutable(m_hDll2)) {
						CFRelease(m_hDll2);
						m_hDll2=0;
					}
				}
				CFRelease(urlFileName);
			}
			CFRelease(fsrFileName);
		}
		if (!m_hDll2) {
			throw CFSFileException(CFSFileException::OPEN);
		}
		return;
	}
#endif
	if (!m_hDll) {
		throw CFSFileException(CFSFileException::OPEN);
	}
}

void CFSDll::FreeLibrary()
{
#if defined (WIN32)
	if (m_hDll && ::FreeLibrary(m_hDll)==0) {
		throw CFSFileException(CFSFileException::CLOSE);
	}
#elif defined (UNIX)
	if (m_hDll && dlclose(m_hDll)!=0) {
		throw CFSFileException(CFSFileException::CLOSE);
	}
#elif defined (MAC)
	if (m_hDll && dlclose(m_hDll)!=0) {
		throw CFSFileException(CFSFileException::CLOSE);
	}
	if (m_hDll2) {
		CFBundleUnloadExecutable(m_hDll2);
		CFRelease(m_hDll2);
		m_hDll2=0;
	}
#endif
	m_hDll=0;
}

void *CFSDll::GetProcAddress(const CFSAString &szProcName) const
{
#if defined (WIN32CE)
	if (m_hDll) {
		return (void *)::GetProcAddress(m_hDll, FSStrAtoW(szProcName));
	}
#elif defined (WIN32)
	if (m_hDll) {
		return (void *)::GetProcAddress(m_hDll, szProcName);
	}
#elif defined (UNIX)
	if (m_hDll) {
		return dlsym(m_hDll, szProcName);
	}
#elif defined (MAC)
	if (m_hDll) {
		return dlsym(m_hDll, szProcName);
	}
	if (m_hDll2) {
		void *pFunc=NULL;
		CFStringRef fsrProcName=CFStringCreateWithCString (NULL, szProcName, kCFStringEncodingUTF8);
		if (fsrProcName) {
			pFunc=CFBundleGetFunctionPointerForName(m_hDll2, fsrProcName);
			CFRelease(fsrProcName);
		}
		return pFunc;
	}
#endif
	return 0;
}
