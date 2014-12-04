#if !defined _FSEXCEPTION_H_
#define _FSEXCEPTION_H_

#include "fstrace.h"

/**
* Base exception class.
*/
class CFSException{
public:
	CFSException() { }
	virtual ~CFSException() { }
};

/**
* Memory exception class.
*/
class CFSMemoryException : public CFSException{
public:
};

/**
* Throws CFSMemoryException.
*/
void FSThrowMemoryException();

/**
* File exception class.
*/
class CFSFileException : public CFSException{
public:
	enum eError { OPEN, CLOSE, READ, WRITE, SEEK, INVALIDDATA };
/**
* @param nError Error code (eError).
*/
	CFSFileException(int nError) { 
		m_nError=nError; 
	}
	int m_nError;
};

/**
* Runtime exception class.
* Parameters strings must be static!
*/
class CFSRuntimeException : public CFSException{
public:
	CFSRuntimeException(const char *pszError, const char *pszFile, int iLine) { 
		m_pszError=pszError;
		m_pszFile=pszFile;
		m_iLine=iLine;
	}
	const char *m_pszError;
	const char *m_pszFile;
	int m_iLine;
};

inline int __FSRTAssert(const char *szText, const char *szFile, int iLine)
{
	throw CFSRuntimeException(szText, szFile, iLine);
}

#define RT_ASSERT(exp) \
	ASSERT(exp); \
	(void)( (!!(exp)) || __FSRTAssert(#exp, __FILE__, __LINE__));

/**
* Simple macro to ignore CFSExceptions.
*/
#define IGNORE_FSEXCEPTION(X) try{ X } catch (const CFSException &) { }

#endif
