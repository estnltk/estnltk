#if !defined _FSREG_H_
#define _FSREG_H_

#include "fsstring.h"
#include "fsdata.h"

/**
* Wrapper class for Windows registry and INI files.
* Platform Win.
*/
class CFSReg{
public:
/**
* Reads variable from registry.
* @param[in] szPath Path to variable.
* @param[out] pData Pointer to a variable, that receives the data.
* @param[out] pdwDataType Data type, see RegGetValue for options.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int Read(const CFSString &szPath, CFSData *pData, DWORD *pdwDataType);

/**
* Reads string (REG_SZ) from registry.
* If data type is not REG_SZ, function fails.
* @param[in] szPath Path to variable.
* @param[out] pszData Pointer to a string, that receives the data.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int ReadString(const CFSString &szPath, CFSString *pszData);

/**
* Reads number (REG_DWORD) from registry.
* If data type is not REG_DWORD, function fails.
* @param[in] szPath Path to variable.
* @param[out] plData Pointer to a int, that receives the data.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int ReadNumber(const CFSString &szPath, UINT32 *plData);

/**
* Reads data (REG_BINARY) from registry.
* If data type is not REG_BINARY, function fails.
* @param[in] szPath Path to variable.
* @param[out] pData Pointer to a data, that receives the data.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int ReadData(const CFSString &szPath, CFSData *pData);


/**
* Writes any data to registry. See RegSetValue for additional information about parameters.
* @param[in] szPath Path to variable.
* @param[in] pData Data to write.
* @param[in] iDataLen Data size in bytes.
* @param[in] dwDataType Data type, see RegSetValue for options.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int Write(const CFSString &szPath, const BYTE *pData, INTPTR iDataLen, DWORD dwDataType);

/**
* Writes string into registry (REG_SZ).
* @param[in] szPath Path to variable.
* @param[in] szData String to write.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int WriteString(const CFSString &szPath, const CFSString &szData);

/**
* Writes integer into registry (REG_DWORD).
* @param[in] szPath Path to variable.
* @param[in] lData Integer to write.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int WriteNumber(const CFSString &szPath, UINT32 lData);

/**
* Writes data into registry (REG_BINARY).
* @param[in] szPath Path to variable.
* @param[in] Data Data to write.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int WriteData(const CFSString &szPath, const CFSData &Data);

/**
* Writes data into registry (REG_BINARY).
* @param[in] szPath Path to variable.
* @param[in] pData Data to write.
* @param[in] ipSize Data size in bytes.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int WriteData(const CFSString &szPath, const void *pData, INTPTR ipSize);

/**
* Deletes key or variable in registry. If key/var does not exist, function returns OK.
* @param[in] szPath Path to variable or key to delete. Use '\' as last character to indicate key. 
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int Delete(const CFSString &szPath);

#if !defined (WIN32CE)
/**
* Reads variable from INI files.
* @param[in] szFileName INI file name.
* @param[in] szSectionName Section name.
* @param[in] szVarName Variable name.
* @param[out] pszData Pointer to a string, that receives the data.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int IniRead(const CFSString &szFileName, const CFSString &szSectionName, const CFSString &szVarName, CFSString *pszData);
/**
* Write variable to INI files.
* @param[in] szFileName INI file name.
* @param[in] szSectionName Section name.
* @param[in] szVarName Variable name.
* @param[in] szData String to write.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	static int IniWrite(const CFSString &szFileName, const CFSString &szSectionName, const CFSString &szVarName, const CFSString &szData);
#endif

protected:
	static int Split(const CFSString &szPath, HKEY *hRoot, CFSString *pszFolder, CFSString *pszFile);
	static HKEY OpenFolder(HKEY hRoot, const CFSString &szFolder);
	static HKEY CreateFolder(HKEY hRoot, const CFSString &szFolder);
};

#endif // _FSREG_H_
