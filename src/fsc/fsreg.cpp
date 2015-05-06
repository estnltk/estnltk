#include "stdfsc.h"
#include "fstype.h"

#if defined (WIN32) && !defined (WINRT)

#include "fsreg.h"

int CFSReg::Split(const CFSString &szPath, HKEY *hRoot, CFSString *pszFolder, CFSString *pszFile)
{
	static struct _Roots{
		TCHAR *Name;
		HKEY hKey;
	}const Roots[]={
		{FSTSTR("HKEY_CLASSES_ROOT\\"), HKEY_CLASSES_ROOT},
		{FSTSTR("HKEY_CURRENT_USER\\"), HKEY_CURRENT_USER},
		{FSTSTR("HKEY_LOCAL_MACHINE\\"), HKEY_LOCAL_MACHINE},
		{FSTSTR("HKEY_USERS\\"), HKEY_USERS},
		{0, 0}
	};
	if (szPath.IsEmpty()) {
		return -1;
	}

	CFSString szFolder;
	for (INTPTR ip=0; Roots[ip].Name; ip++){
		if (szPath.StartsWith(Roots[ip].Name)) {
			*hRoot=Roots[ip].hKey;
			szFolder=szPath.Mid(FSStrLen(Roots[ip].Name));
			break;
		}
	}

	if (szFolder.IsEmpty()) {
		return -1;
	}
	INTPTR ipPos=szFolder.ReverseFind('\\');
	if (ipPos==-1) {
		*pszFolder=szFolder;
		pszFile->Empty();
	}
	else {
		*pszFolder=szFolder.Left(ipPos);
		*pszFile=szFolder.Mid(ipPos+1);
	}
	return 0;
}

HKEY CFSReg::OpenFolder(HKEY hRoot, const CFSString &szFolder)
{
	if (szFolder.IsEmpty()) {
		return hRoot;
	}
	else{
		HKEY hKey;
		if (RegOpenKeyEx(hRoot, szFolder, 0, KEY_READ, &hKey)!=ERROR_SUCCESS) {
			return 0;
		}
		return hKey;
	}
}

HKEY CFSReg::CreateFolder(HKEY hRoot, const CFSString &szFolder)
{
	if (szFolder.IsEmpty()) {
		return hRoot;
	}
	else{
		HKEY hKey;
		DWORD Disposion;
		if (RegCreateKeyEx(hRoot, szFolder, 0, 0, REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS, NULL, &hKey, &Disposion)!=ERROR_SUCCESS) {
			return 0;
		}
		return hKey;
	}
}

int CFSReg::Delete(const CFSString &szPath)
{
	HKEY hRoot; CFSString szFolder; CFSString szFile;
	if (Split(szPath, &hRoot, &szFolder, &szFile)!=0) {
		return -1;
	}

	HKEY hKey;
    long lRet=RegOpenKeyEx(hRoot, szFolder, 0, KEY_WRITE, &hKey);
    switch(lRet){
		case ERROR_SUCCESS:
		break;
		case ERROR_FILE_NOT_FOUND:
			return 0;
		default:
			return -1;
    }
    lRet=RegDeleteKey(hKey, szFile);
	if (lRet) {
		lRet=RegDeleteValue(hKey, szFile);
	}
    RegCloseKey(hKey);

    switch(lRet)
    {
		case ERROR_FILE_NOT_FOUND:
		case ERROR_SUCCESS:
			return 0;
		default:
			return -1;
    }
}

// Read -----------------------------------------

int CFSReg::Read(const CFSString &szPath, CFSData *pData, DWORD *pdwDataType)
{
	HKEY hRoot; CFSString szFolder; CFSString szFile;
	if (Split(szPath, &hRoot, &szFolder, &szFile)!=0) {
		return -1;
	}
	HKEY hKey;
	if ((hKey=OpenFolder(hRoot, szFolder))==0) {
		return -1;
	}
	DWORD dwDataLen=0;
	if (RegQueryValueEx(hKey, szFile, 0, pdwDataType, NULL, &dwDataLen)!=ERROR_SUCCESS) {
		RegCloseKey(hKey);
		return -1;
	}
	pData->SetSize(dwDataLen);
	if (RegQueryValueEx(hKey, szFile, 0, pdwDataType, (BYTE *)pData->GetData(), &dwDataLen)!=ERROR_SUCCESS) {
		RegCloseKey(hKey);
		return -1;
	}
	RegCloseKey(hKey);
	if (dwDataLen!=(DWORD)pData->GetSize()) {
		return -1;
	}
	return 0;
}

int CFSReg::ReadString(const CFSString &szPath, CFSString *pszData)
{
	CFSData Data;
	DWORD dwDataType;
	if (Read(szPath, &Data, &dwDataType)!=0) {
		return -1;
	}
	if (dwDataType!=REG_SZ) {
		return -1;
	}
	*pszData=(TCHAR *)Data.GetData();
	return 0;
}

int CFSReg::ReadNumber(const CFSString &szPath, UINT32 *plData){
	CFSData Data;
	DWORD dwDataType;
	if (Read(szPath, &Data, &dwDataType)!=0) {
		return -1;
	}
	if (dwDataType!=REG_DWORD) {
		return -1;
	}
	*plData=*(UINT32 *)Data.GetData();
	return 0;
}

int CFSReg::ReadData(const CFSString &szPath, CFSData *pData)
{
	DWORD dwDataType;
	if (Read(szPath, pData, &dwDataType)!=0) {
		return -1;
	}
	if (dwDataType!=REG_BINARY) {
		return -1;
	}
	return 0;
}

// Write ----------------------------------------

int CFSReg::Write(const CFSString &szPath, const BYTE *pData, INTPTR ipDataLen, DWORD dwDataType)
{
	if (ipDataLen<0) { // || (((UINTPTR)ipDataLen)>>(sizeof(DWORD)<<3))) {
		return -1;
	}
	HKEY hRoot; CFSString szFolder; CFSString szFile;
	if (Split(szPath, &hRoot, &szFolder, &szFile)!=0) {
		return -1;
	}
	HKEY hKey;
	if ((hKey=CreateFolder(hRoot, szFolder))==0) {
		return -1;
	}
	long lRes=RegSetValueEx(hKey, szFile, 0, dwDataType, pData, (DWORD)ipDataLen);
	RegCloseKey(hKey);
	return (lRes!=ERROR_SUCCESS);
}

int CFSReg::WriteString(const CFSString &szPath, const CFSString &szData)
{
	return Write(szPath, (const BYTE *)(const TCHAR *)szData, sizeof(TCHAR)*(szData.GetLength()+1), REG_SZ);
}

int CFSReg::WriteNumber(const CFSString &szPath, UINT32 lData)
{
	return Write(szPath, (BYTE *)&lData, sizeof(UINT32), REG_DWORD);
}

int CFSReg::WriteData(const CFSString &szPath, const CFSData &Data)
{
	return WriteData(szPath, Data.GetData(), Data.GetSize());
}

int CFSReg::WriteData(const CFSString &szPath, const void *pData, INTPTR ipSize)
{
	return Write(szPath, (BYTE *)pData, ipSize, REG_BINARY);
}

// INI ------------------------------------------

#if !defined (WIN32CE)

int CFSReg::IniRead(const CFSString &szFileName, const CFSString &szSectionName, const CFSString &szVarName, CFSString *pszData)
{
	long lDataLen=1024;
	int iRes=(GetPrivateProfileString(szSectionName, szVarName, FSTSTR(""), pszData->GetBuffer(lDataLen), lDataLen, szFileName)==0);
	pszData->ReleaseBuffer();
	return iRes;
}

int CFSReg::IniWrite(const CFSString &szFileName, const CFSString &szSectionName, const CFSString &szVarName, const CFSString &szData)
{
	return (WritePrivateProfileString(szSectionName, szVarName, szData, szFileName)==0);
}

#endif

#endif // WIN32
