#if !defined _FSSTRING2_H_
#define _FSSTRING2_H_

#include "fsstring.h"
#include "fslist.h"

typedef CFSArray<CFSAString> CFSAStringArray;
typedef CFSArray<CFSWString> CFSWStringArray;
typedef CFSArray<CFSString> CFSStringArray;

/**
* Codepages supported by FSC.
*/
enum eFSCP { FSCP_UTF8=-3, FSCP_HTML=-2, FSCP_ACP=-1, FSCP_SYSTEM=0, FSCP_WESTERN=1252, FSCP_BALTIC=1257 };

/**
* Codepage that is used in different ANSI string functions. Default value FSCP_SYSTEM.
*/
extern long g_lFSCodePage;

/**
* Converts Wide string to Ansi string.
* @param[in] WString Wide string to convert.
* @param[in] CodePage Code page to use for conversion.
* @param[out] pbError Optional pointer to variable that receives error status indication.
* @return Converted string.
* @sa eFSCP
*/
CFSAString FSStrWtoA(const CFSWString &WString, long CodePage=FSCP_ACP, bool *pbError=0);

/**
* Converts Ansi string to Wide string.
* @param[in] AString Ansi string to convert.
* @param[in] CodePage Code page to use for conversion.
* @param[out] pbError Optional pointer to variable that receives error status indication.
* @return Converted string.
* @sa eFSCP
*/
CFSWString FSStrAtoW(const CFSAString &AString, long CodePage=FSCP_ACP, bool *pbError=0);

#if defined (UNICODE)
inline CFSString FSStrAtoT(const CFSAString &AString, long CodePage=FSCP_ACP, bool *pbError=0) {
	return FSStrAtoW(AString, CodePage, pbError);
}
inline CFSAString FSStrTtoA(const CFSString &String, long CodePage=FSCP_ACP, bool *pbError=0) {
	return FSStrWtoA(String, CodePage, pbError);
}
inline CFSString FSStrWtoT(const CFSWString &WString, long CodePage=FSCP_ACP, bool *pbError=0) {
	FSUNUSED(CodePage);
	if (pbError) *pbError=false;
	return WString;
}
inline CFSWString FSStrTtoW(const CFSString &String, long CodePage=FSCP_ACP, bool *pbError=0) {
	FSUNUSED(CodePage);
	if (pbError) *pbError=false;
	return String;
}
#else
inline CFSString FSStrAtoT(const CFSAString &AString, long CodePage=FSCP_ACP, bool *pbError=0) {
	FSUNUSED(CodePage);
	if (pbError) *pbError=false;
	return AString;
}
inline CFSAString FSStrTtoA(const CFSString &String, long CodePage=FSCP_ACP, bool *pbError=0) {
	FSUNUSED(CodePage);
	if (pbError) *pbError=false;
	return String;
}
inline CFSString FSStrWtoT(const CFSWString &WString, long CodePage=FSCP_ACP, bool *pbError=0) {
	return FSStrWtoA(WString, CodePage, pbError);
}
inline CFSWString FSStrTtoW(const CFSString &String, long CodePage=FSCP_ACP, bool *pbError=0) {
	return FSStrAtoW(String, CodePage, pbError);
}
#endif	
	
/**
* Converts 0-terminated C-string to length-header Pascal-string.
* @param[out] pszPStr Result string is Pascal format.
* @param[in] pszCStr Source C-string.
* @param[in] nMaxLength Max size of Pascal string, typically sizeof(pszPStr).
*/
void FSStrCtoP(unsigned char *pszPStr, const char *pszCStr, unsigned char nMaxLength=255);

/**
* Converts length-header Pascal-string to 0-terminated C-string.
* @param[in] pszPStr Pointer to Pascal-style string.
* @return Converted string
*/
CFSAString FSStrPtoC(const unsigned char *pszPStr);

/**
* Checks whether character is UTF16 first surrogate.
* @param[in] Char Character to test.
* @retval true Is first surrogate.
* @retval false Otherwise.
*/
inline bool FSIsW21(WCHAR Char)
{ 
	return (Char>=0xd800 && Char<=0xdbff);
}

/**
* Checks whether character is UTF16 second surrogate.
* @param[in] Char Character to test.
* @retval true Is second surrogate.
* @retval false Otherwise.
*/
inline bool FSIsW22(WCHAR Char)
{
	return (Char>=0xdc00 && Char<=0xdfff);
}

/**
* Converts UTF16 surrogate pair to UCS4 character.
* @param[in] Char1 First UTF16 surrogate.
* @param[in] Char2 Second UTF16 surrogate.
* @param[out] pChar Pointer to UCS4 character, that will receive the result.
* @retval 0 Conversion successful.
* @retval !=0 Otherwise.
*/
inline int FSW2toL(WCHAR Char1, WCHAR Char2, LCHAR *pChar)
{
	if (!FSIsW21(Char1) || !FSIsW22(Char2)) {
		return -1;
	}
	*pChar=(0x10000 + (((LCHAR)Char1&0x3ff)<<10)) | (Char2&0x3ff);
	return 0;
}

/**
* Converts above-UCS2 UCS4 character to UTF16 surrogate pair.
* @param[in] Char UCS4 character to convert.
* @param[out] pChar1 Pointer to first UTF16 surrogate that will receive the result.
* @param[out] pChar2 Pointer to second UTF16 surrogate that will receive the result.
* @retval 0 Conversion successful.
* @retval !=0 Otherwise.
*/
inline int FSLtoW2(LCHAR Char, WCHAR *pChar1, WCHAR *pChar2)
{
	if (Char<0x10000 || Char>0x10ffff) {
		return -1;
	}
	*pChar1=(WCHAR)(0xd800+((Char-0x10000)>>10));
	*pChar2=(WCHAR)(0xdc00+((Char-0x10000)&0x3ff));
	return 0;
}

/**
* Appends UCS4 character to wide string. On UTF16 systems, character is converted to UTF16 surrogates, if necessary.
* @param[in, out] szStr String that will get appended.
* @param[in] lChar Character to append.
* @return Number of physical characters that were appended after possible conversion.
*/
INTPTR FSStrAppendFSLCHAR(CFSWString &szStr, LCHAR lChar);

/**
* Extracts UCS4 character from Wide string.
* @param[out] pChar Pointer to variable that will receive the char.
* @param[in] szStr String to extract character from.
* @param[in] ipPos Position in string to extract character from.
* @return A number of physical characters used to combine UCS4 char.
*/
INTPTR FSStrGetFSLCHAR(LCHAR *pChar, const CFSWString &szStr, INTPTR ipPos);

/**
* On UCS4 systems replaces all surrogate pairs in the string with their corresponding UCS4 values.
* @param[in, out] szStr String to convert.
* @retval 0 Operation successful.
* @retval !=0 Otherwise.
*/
int FSStrCombineW2(CFSWString &szStr);

/**
* Simple string capitalization class.
*/
template <class STRING>
class CFSStrCap{
public:
/**
* Capitalization modes.
*/
	enum eCap { CAP_LOWER, CAP_INITIAL, CAP_UPPER, CAP_MIXED };
	CFSStrCap() {
		m_lCapMode=CAP_LOWER;
	}
/**
* Initializes class and extracts capitalization information from word.
* @param[in] szWord Word to extract capitalization info from.
*/
	CFSStrCap(const STRING &szWord) {
		SetCap(szWord);
	}

/**
* Set capitalization mode.
* @param lCapMode New capitalization mode to use.
*/
	void SetCapMode(long lCapMode) {
		m_lCapMode=lCapMode;
	}

/**
* Query active capitalization mode.
* @return Active capitalization mode.
*/
	long GetCapMode() const {
		return m_lCapMode;
	}
	
/**
* Extact cap information from word.
* @param[in] szWord Word to extract capitalization info from.
*/
	void SetCap(const STRING &szWord) {
		STRING szWord1, szWord2;
		szWord1=szWord.ToLower();
		if (szWord1==szWord) {
			m_lCapMode=CAP_LOWER;
			return;
		}
		szWord2=szWord; szWord2[0]=FSToLower(szWord2[0]);
		if (szWord1==szWord2) {
			m_lCapMode=CAP_INITIAL;
			return;
		}
		szWord1.MakeUpper();
		if (szWord1==szWord) {
			m_lCapMode=CAP_UPPER;
			return;
		}
		m_lCapMode=CAP_MIXED;
	}

/**
* Capitalize word according to current capitalization mode.
* @param[in] szWord Word to capitalize.
* @return Capitalized word.
*/
	STRING GetCap(STRING szWord) const {
		switch (m_lCapMode){
			case CAP_INITIAL:
				szWord[0]=FSToUpper(szWord[0]);
			break;
			case CAP_UPPER:
				szWord.MakeUpper();
			break;
		}
		return szWord;
	}

protected:
	long m_lCapMode;
};

/**
* Split string to sting array.
* @param[in] szStr String to split.
* @param[in] cSplitter Character that defines split-points.
* @param[out] Array Array that will contain splits of the string.
* @return Number of splits extracted from string.
*/
template <class CHARTYPE, class STRFUNCTIONS>
INTPTR FSStrSplit(const CFSBaseString<CHARTYPE, STRFUNCTIONS> &szStr, CHARTYPE cSplitter, CFSArray<CFSBaseString<CHARTYPE, STRFUNCTIONS> > &Array)
{
	Array.Cleanup();
	INTPTR ipStart=0;
	for (INTPTR ip=0; ip<szStr.GetLength(); ip++){
		if (szStr[ip]==cSplitter){
			Array.AddItem(szStr.Mid(ipStart, ip-ipStart));
			ipStart=ip+1;
		}
	}
	Array.AddItem(szStr.Mid(ipStart));
	return Array.GetSize();
}

/**
* Combines splitted string into one.
* @param[in] Array Array of strings to combine.
* @param[in] szSplitter Character/String that is used at glue-points.
* @return Combined string.
*/
template <class CHARTYPE, class STRFUNCTIONS>
CFSBaseString<CHARTYPE, STRFUNCTIONS> FSStrCombine(const CFSArray<CFSBaseString<CHARTYPE, STRFUNCTIONS> > &Array, const CFSBaseString<CHARTYPE, STRFUNCTIONS> &szSplitter)
{
	CFSBaseString<CHARTYPE, STRFUNCTIONS> szResult;
	INTPTR ipSize=0;
	for (INTPTR ip=0; ip<Array.GetSize(); ip++) {
		if (ip>0) {
			ipSize+=szSplitter.GetLength();
		}
		ipSize+=Array[ip].GetLength();
	}
	if (ipSize>0) {
		CHARTYPE *pBuffer=szResult.GetBuffer(ipSize+1);
		for (INTPTR ip=0; ip<Array.GetSize(); ip++) {
			if (ip>0) {
				memcpy(pBuffer, (const CHARTYPE *)szSplitter, szSplitter.GetLength()*sizeof(CHARTYPE));
				pBuffer+=szSplitter.GetLength();
			}
			memcpy(pBuffer, (const CHARTYPE *)Array[ip], Array[ip].GetLength()*sizeof(CHARTYPE));
			pBuffer+=Array[ip].GetLength();
		}
		szResult.ReleaseBuffer(ipSize);
	}
	return szResult;
}

CFSAString FSStrToLowerUTF8(const CFSAString &szStr);
CFSAString FSStrToUpperUTF8(const CFSAString &szStr);

/**
* Simple exception that carries textual information.
*/
class CFSTextualException : public CFSException
{
public:
	CFSTextualException(const FSTCHAR *pszFormat, ...)
	{
		va_list args;
		va_start(args, pszFormat);
		m_szText.FormatV(pszFormat, args);
		va_end(args);
	}

	CFSString GetText() const { return m_szText; }

protected:
	CFSString m_szText;
};

#endif // _FSSTRING2_H_
