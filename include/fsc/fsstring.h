#if !defined _FSSTRING_H_
#define _FSSTRING_H_

#include "fsthread.h"

/**
* Converts character to lowercase. Function behavior depends on g_lFSCodePage value.
* @param[in] Char Character to convert.
* @return Converted character.
*/
char FSToLower(char Char);

/**
* Converts character to lowercase.
* @param[in] Char Character to convert.
* @return Converted character.
*/
WCHAR FSToLower(WCHAR Char);
inline LCHAR FSToLower(LCHAR Char) { return FSToLower((WCHAR)Char); }

/**
* Converts character to uppercase. Function behavior depends on g_lFSCodePage value.
* @param[in] Char Character to convert.
* @return Converted character.
*/
char FSToUpper(char Char);

/**
* Converts character to uppercase.
* @param[in] Char Character to convert.
* @return Converted character.
*/
WCHAR FSToUpper(WCHAR Char);
inline LCHAR FSToUpper(LCHAR Char) { return FSToUpper((WCHAR)Char); }

/**
* Checks whether character is a number.
* @param[in] Char Character to check.
* @retval true Character is a number.
* @retval false Otherwise.
*/
template <class CHARTYPE>
bool FSIsNumber(CHARTYPE Char) {
	return (Char>='0' && Char<='9');
}

/**
* Checks whether character is a whitespace.
* @param[in] Char Character to check.
* @retval true Character is a whitespace.
* @retval false Otherwise.
*/
bool FSIsSpace(char Char);
bool FSIsSpace(wchar_t Char);
inline bool FSIsSpace(LCHAR Char) { return Char<0x10000 && FSIsSpace((WCHAR)Char); }

bool FSIsLetter(char Char);
bool FSIsLetter(wchar_t Char);
inline bool FSIsLetter(LCHAR Char) { return Char<0x10000 && FSIsLetter((WCHAR)Char); }

/**
* Calculates length of 0-terminated string. See strlen for details.
* @param[in] pszStr Pointer to string.
* @return Length of the string.
*/
inline INTPTR FSStrLen(const char *pszStr) { 
	return strlen(pszStr); 
}
inline INTPTR FSStrLen(const wchar_t *pszStr) { 
	return wcslen(pszStr); 
}
template <class CHARTYPE>
INTPTR FSStrLen(const CHARTYPE *pszStr)
{
	const CHARTYPE *pszStr2=pszStr;
	while (pszStr2[0]) {
		pszStr2++;
	}
	return pszStr2-pszStr;
}

/**
* Compares two 0-terminated strings. See strcmp for details.
* @param[in] pszStr1 Pointer to first string to compare.
* @param[in] pszStr2 Pointer to second string to compare.
* @retval 0 Strings are identical.
* @retval <0 String1 is less that String2.
* @retval >0 String1 is greater that String2.
*/
inline int FSStrCmp(const char *pszStr1, const char *pszStr2) { 
	return strcmp(pszStr1, pszStr2); 
}
inline int FSStrCmp(const wchar_t *pszStr1, const wchar_t *pszStr2) { 
	return wcscmp(pszStr1, pszStr2); 
}
template <class CHARTYPE>
int FSStrCmp(const CHARTYPE *pszStr1, const CHARTYPE *pszStr2)
{
	for (;; pszStr1++, pszStr2++) {
		if (pszStr1[0]<pszStr2[0]) {
			return -1;
		}
		if (pszStr1[0]>pszStr2[0]) {
			return 1;
		}
		if (!pszStr1[0]) {
			return 0;
		}
	}
}

/**
* Copies 0-terminated string to another buffer. See strcpy for details.
* @param[out] pszDest Buffer to copy to.
* @param[in] ipDestSize Size of pszDest in characters.
* @param[in] pszSrc String to copy.
* @return Pointer to pszDest.
*/
#if defined (WIN32)
inline void FSStrCpy(char *pszDest, INTPTR ipDestSize, const char *pszSrc) {
	RT_ASSERT(ipDestSize>0);
	strcpy_s(pszDest, ipDestSize, pszSrc);
}

inline void FSStrCpy(wchar_t *pszDest, INTPTR ipDestSize, const wchar_t *pszSrc) { 
	RT_ASSERT(ipDestSize>0);
	wcscpy_s(pszDest, ipDestSize, pszSrc);
}
#endif

template <class CHARTYPE>
void FSStrCpy(CHARTYPE *pszDest, INTPTR ipDestSize, const CHARTYPE *pszSrc)
{
	ASSERT(pszDest && pszSrc);
	for (;;) {
		RT_ASSERT(ipDestSize>0);
		*pszDest=*pszSrc;
		if (!*pszSrc) break;
		pszDest++; pszSrc++;
		ipDestSize--;
	}
}

/**
* Concatenates two 0-terminated strings. See strcat for details.
* @param[out] pszDest String to append to.
* @param[in] ipDestSize Size of pszDest in characters.
* @param[in] pszSrc String to append.
* @return Pointer to pszDest.
*/
#if defined (WIN32)
inline void FSStrCat(char *pszDest, INTPTR ipDestSize, const char *pszSrc) { 
	RT_ASSERT(ipDestSize>0);
	strcat_s(pszDest, ipDestSize, pszSrc);
}

inline void FSStrCat(wchar_t *pszDest, INTPTR ipDestSize, const wchar_t *pszSrc) { 
	RT_ASSERT(ipDestSize>0);
	wcscat_s(pszDest, ipDestSize, pszSrc);
}
#endif

template <class CHARTYPE>
void FSStrCat(CHARTYPE *pszDest, INTPTR ipDestSize, const CHARTYPE *pszSrc)
{
	ASSERT(pszDest && pszSrc);
	INTPTR ipLen=FSStrLen(pszDest);
	FSStrCpy(pszDest+ipLen, ipDestSize-ipLen, pszSrc);
}

/**
* Search for first existence of one 0-terminated string in another. See strstr for details.
* @param[in] pszStr String to search in.
* @param[in] pszSearch String to search for.
* @return Pointer to leftmost existence of pszSearch in pszStr.
* @retval 0 Not found.
*/
inline const char *FSStrStr(const char *pszStr, const char *pszSearch) { 
	return strstr(pszStr, pszSearch); 
}
inline const wchar_t *FSStrStr(const wchar_t *pszStr, const wchar_t *pszSearch) { 
	return wcsstr(pszStr, pszSearch); 
}
template <class CHARTYPE>
const CHARTYPE *FSStrStr(const CHARTYPE *pszStr, const CHARTYPE *pszSearch)
{
	INTPTR ipSearchLen=FSStrLen(pszSearch);
	for (INTPTR ip=FSStrLen(pszStr)-ipSearchLen; ip>=0; ip--){
		if (memcmp(pszStr, pszSearch, ipSearchLen*sizeof(CHARTYPE))==0) {
			return pszStr;
		}
		pszStr++;
	}
	return 0;
}

/**
* Search for first existence of a character in 0-terminated string. See strchr for details.
* @param[in] pszStr String to search in.
* @param[in] cChar Char to search for.
* @return Pointer to leftmost existence of cChar in pszStr.
* @retval 0 Not found.
*/
inline const char *FSStrChr(const char *pszStr, char cChar) { 
	return strchr(pszStr, cChar); 
}
inline const wchar_t *FSStrChr(const wchar_t *pszStr, wchar_t cChar) { 
	return wcschr(pszStr, cChar); 
}
template <class CHARTYPE>
const CHARTYPE *FSStrChr(const CHARTYPE *pszStr, CHARTYPE cChar)
{
	for (;; pszStr++) {
		if (pszStr[0]==cChar) {
			return pszStr;
		}
		if (!pszStr[0]) {
			return 0;
		}
	}
}

/**
* Search for last existence of one 0-terminated string in another.
* @param[in] pszStr String to search in.
* @param[in] pszSearch String to search for.
* @return Pointer to rightmost existence of pszSearch in pszStr.
* @retval 0 Not found.
*/
template <class CHARTYPE>
const CHARTYPE *FSStrRStr(const CHARTYPE *pszStr, const CHARTYPE *pszSearch)
{
	INTPTR ipSearchLen=FSStrLen(pszSearch);
	for (INTPTR ip=FSStrLen(pszStr)-ipSearchLen; ip>=0; ip--){
		if (memcmp(pszStr+ip, pszSearch, ipSearchLen*sizeof(CHARTYPE))==0) {
			return pszStr+ip;
		}
	}
	return 0;
}

/**
* Search for last existence of a character in 0-terminated string. See strrchr for details.
* @param[in] pszStr String to search in.
* @param[in] cChar Char to search for.
* @return Pointer to rightmost existence of cChar in pszStr.
* @retval 0 Not found.
*/
inline const char *FSStrRChr(const char *pszStr, char cChar) { 
	return strrchr(pszStr, cChar); 
}
inline const wchar_t *FSStrRChr(const wchar_t *pszStr, wchar_t cChar) { 
	return wcsrchr(pszStr, cChar); 
}
template <class CHARTYPE>
const CHARTYPE *FSStrRChr(const CHARTYPE *pszStr, CHARTYPE cChar)
{
	for (INTPTR ip=FSStrLen(pszStr); ip>=0; ip--) {
		if (pszStr[ip]==cChar) {
			return pszStr+ip;
		}
	}
	return 0;
}

/**
* Search for first existence of one of defined character in 0-terminated string. See strpbrk for details.
* @param[in] pszStr String to search in.
* @param[in] pszSearch String that contains a set of characters to search for.
* @return Pointer to leftmost existence of any character in pszSearch in pszStr.
* @retval 0 Not found.
*/
inline const char *FSStrSet(const char *pszStr, const char *pszSearch) {
	return strpbrk(pszStr, pszSearch);
}
inline const wchar_t *FSStrSet(const wchar_t *pszStr, const wchar_t *pszSearch) {
	return wcspbrk(pszStr, pszSearch);
}
template <class CHARTYPE>
const CHARTYPE *FSStrSet(const CHARTYPE *pszStr, const CHARTYPE *pszSearch)
{
	if (!pszSearch) {
		return 0;
	}
	for (; pszStr[0]; pszStr++){
		if (FSStrChr(pszSearch, pszStr[0])) {
			return pszStr;
		}
	}
	return 0;
}

/**
* Converts pointer to 0-terminated string to "safe" pointer.
* 0-pointers are replaced with empty strings, other pointers are left intact.
* @param[in] pszStr Pointer to 0-terminated string.
* @return Safe pointer.
*/
template<class CHARTYPE>
const CHARTYPE *FSSafeStr(const CHARTYPE *pszStr)
{
	static const CHARTYPE Char=0;
	return (pszStr ? pszStr : &Char);
}

/**
* Template class to extend CFSString functionality for new character types.
* Part of CFSString default declaration.
*/
template<class CHARTYPE>
class CFSStrFunctions{
public:
/**
* Converts character to lowercase.
* @param cChar Character to convert.
* @return Result of conversion.
*/
	static CHARTYPE ToLower(CHARTYPE cChar) {
		return FSToLower(cChar);
	}

/**
* Converts character to uppercase.
* @param cChar Character to convert.
* @return Result of conversion.
*/
	static CHARTYPE ToUpper(CHARTYPE cChar) {
		return FSToUpper(cChar);
	}
};

/**
* CFSString internal data holder block.
*/
struct CFSStringData{
	INTPTR m_ipBufSize;
	INTPTR m_ipLength;
	INTATOMIC m_iRefCount; // >1 Shared; <=0 Locked

	bool IsLocked() const {
		return m_iRefCount<=0;
	}
	bool IsShared() const {
		return m_iRefCount>1;
	}
};

/**
* Allocates data block for CFSString.
* @param[in] ipSize Size of buffer in characters.
* @param[in] ipCharSize Size of character.
* @return Pointer to data area of the data block (not head of data block).
* @sa FSStringFree
*/
void *FSStringAlloc(INTPTR ipSize, INTPTR ipCharSize);

/**
* Frees data block previously allocated by FSStringAlloc.
* @param[in] pszStr Pointer previously returned by FSStringAlloc.
* @param[in] ipCharSize Size of character.
* @sa FSStringAlloc
*/
void FSStringFree(void *pszStr, INTPTR ipCharSize);

/**
* Character-type independent string template class. Base for CFSString.
* It's usage is very similar to MFC CString.
*/
template <class CHARTYPE, class STRFUNCTIONS>
class CFSBaseString {
protected:
/**
* Helper class to differ read-write access.
*/
	class CFSBaseStringChar{
		friend class CFSBaseString;
	private:
		CFSBaseStringChar(CFSBaseString *pString, INTPTR iPos) {
			m_pString=pString;
			m_iPos=iPos;
		}
	public:
		operator CHARTYPE() const {
			return m_pString->GetAt(m_iPos);
		}
		CFSBaseStringChar &operator =(CHARTYPE cChar) {
			m_pString->SetAt(m_iPos, cChar);
			return *this;
		}
		CFSBaseStringChar &operator =(const CFSBaseStringChar &Char) {
			return operator =((CHARTYPE)Char);
		}
	private:
		CFSBaseString *m_pString;
		INTPTR m_iPos;
	};
public:
	CFSBaseString()
	{
		m_pszStr=GetNullString();
	}

	CFSBaseString(const CFSBaseString &szStr)
	{
		m_pszStr=GetNullString();
		operator =(szStr);
	}
#if defined (__FSCXX0X)
	CFSBaseString(CFSBaseString &&szStr)
	{
		m_pszStr=szStr.m_pszStr;
		szStr.m_pszStr=szStr.GetNullString();
	}
#endif
/**
* Creates class from 0-terminated string.
* @param[in] pszStr 0-terminated string to create from.
*/
	CFSBaseString(const CHARTYPE *pszStr)
	{
		m_pszStr=GetNullString();
		operator =(pszStr);
	}

/**
* Creates class from 0-terminated string with length limit.
* @param[in] pszStr 0-terminated string to create from.
* @param[in] ipLength Use up to ipLength characters from source.
*/
	CFSBaseString(const CHARTYPE *pszStr, INTPTR ipLength)
	{
		ASSERT(ipLength>=0);
		m_pszStr=GetNullString();
		if (pszStr && ipLength>0){
			_GetBuffer(ipLength+1, 0);
			for (INTPTR ip=0; ip<ipLength; ip++){
				if (!pszStr[ip]) {
					ipLength=ip;
					break; 
				}
				m_pszStr[ip]=pszStr[ip];
			}
			_ReleaseBuffer(ipLength);
		}
	}

/**
* Creates class from character. Optionally the character can be repeated lRepeat times.
* @param[in] cChar Character to create from.
* @param[in] ipRepeat Count of which the character will be repeated in string.
*/
	CFSBaseString(CHARTYPE cChar, INTPTR ipRepeat=1)
	{
		ASSERT(ipRepeat>=0);
		m_pszStr=GetNullString();
		if (cChar && ipRepeat>0){
			_GetBuffer(ipRepeat+1, 0);
			for (INTPTR ip=0; ip<ipRepeat; ip++) {
				m_pszStr[ip]=cChar;
			}
			_ReleaseBuffer(ipRepeat);
		}
	}

	~CFSBaseString()
	{
		Release();
	}

/**
* Returns the length of the string in characters.
* @return Length in characters.
*/
	INTPTR GetLength() const
	{
		return (GetData()->IsLocked() ? FSStrLen(m_pszStr) : GetData()->m_ipLength);
	}

/**
* Checks whether string is empty string.
* @retval true String is empty.
* @retval false Otherwise.
*/
	bool IsEmpty() const 
	{
		return m_pszStr[0]==0;
	}

/**
* Clears the string contents making it empty string.
*/
	void Empty()
	{
		if (GetData()->IsLocked()) {
			m_pszStr[0]=0;
		}
		else {
			Release();
			m_pszStr=GetNullString();
		}
	}

/**
* Preallocates string buffer.
* param[in] ipSize String buffer will be at least ipSize characters in size.
*/
	void SetSize(INTPTR ipSize)
	{
		_GetBuffer(ipSize, 1);
	}

/**
* Extracts leftmost ipLength characters from string.
* @param[in] ipLength Number of characters to extract.
* If ipLength is larger that length of the string, whole string is returned.
* @return Extracted substring.
* @sa Mid, End
*/
	CFSBaseString Left(INTPTR ipLength) const
	{
		ASSERT(ipLength>=0);
		if (ipLength<=0) {
			return CFSBaseString();
		}
		if (ipLength>=GetLength()) {
			return *this;
		}
		CFSBaseString szResult;
		szResult._GetBuffer(ipLength+1, 0);
		memcpy(szResult.m_pszStr, m_pszStr, ipLength*sizeof(CHARTYPE));
		szResult._ReleaseBuffer(ipLength);
		return szResult;
	}

/**
* Extracts substring from string.
* @param[in] ipPos Index of a character to start extraction from.
* @param[in] ipLength Number of characters to extract.
* If ipLength is larger that length of the remaining string or if ipLength==-1,
* substring from ipPos to the end is returned.
* @return Extracted substring.
* @sa Left, Mid
*/
	CFSBaseString Mid(INTPTR ipPos, INTPTR ipLength=-1) const
	{
		ASSERT(ipPos>=0);
		ASSERT(ipLength>=-1);
		if (ipPos<0 || ipPos>=GetLength()) {
			return CFSBaseString();
		}
		if (ipLength<0) {
			ipLength=GetLength()-ipPos;
		}
		else {
			ipLength=FSMIN(GetLength()-ipPos, ipLength);
		}
		CFSBaseString szResult;
		szResult._GetBuffer(ipLength+1, 0);
		memcpy(szResult.m_pszStr, m_pszStr+ipPos, ipLength*sizeof(CHARTYPE));
		szResult._ReleaseBuffer(ipLength);
		return szResult;
	}

/**
* Extracts rightmost ipLength characters from string.
* @param[in] ipLength Number of characters to extract.
* If ipLength is larger that length of the string, whole string is returned.
* @return Extracted substring.
* @sa Left, Mid
*/
	CFSBaseString Right(INTPTR ipLength) const
	{
		ASSERT(ipLength>=0);
		if (ipLength<=0) {
			return CFSBaseString();
		}
		if (ipLength>=GetLength()) {
			return *this;
		}
		CFSBaseString szResult;
		szResult._GetBuffer(ipLength+1, 0);
		memcpy(szResult.m_pszStr, m_pszStr+GetLength()-ipLength, ipLength*sizeof(CHARTYPE));
		szResult._ReleaseBuffer(ipLength);
		return szResult;
	}

/**
* Extracts substring from the beginning of class until the character that is not included in pszStr.
* @param[in] pszStr A set of accepted characters.
* @return Extracted string.
*/
	CFSBaseString SpanIncluding(const CHARTYPE *pszStr) const
	{ 
		CFSBaseString szResult;
		if (!pszStr) {
			return szResult;
		}
		for (CHARTYPE *pChar=m_pszStr; pChar[0]; pChar++){
			if (FSStrChr(pszStr, pChar[0])) {
				szResult+=pChar[0];
			}
			else {
				break;
			}
		}
		return szResult;
	}

/**
* Extracts substring from the beginning of class until the character that is included in pszStr.
* @param[in] pszStr A set of rejected characters.
* @return Extracted string.
*/
	CFSBaseString SpanExcluding(const CHARTYPE *pszStr) const
	{
		if (!pszStr) {
			return *this;
		}
		CFSBaseString szResult;
		for (CHARTYPE *pChar=m_pszStr; pChar[0]; pChar++){
			if (FSStrChr(pszStr, pChar[0])) {
				break;
			}
			else {
				szResult+=pChar[0];
			}
		}
		return szResult;
	}

/**
* Checks whether string starts with pszStr.
* It is logically equal to Str.Left(FSStrLen(pszStr))==pszStr, but much faster.
* @param[in] pszStr Sting to check.
* @retval true String starts with pszStr.
* @retval false Otherwise.
* @sa ContainsAt, EndsWith
*/
	bool StartsWith(const CHARTYPE *pszStr) const
	{
		const CHARTYPE *pszMyStr=m_pszStr;
		if (!pszStr) {
			return true;
		}
		while (*pszStr){
			if (*pszMyStr++ != *pszStr++) {
				return false;
			}
		}
		return true;
	}

/**
* Checks whether substring starting at specified index is equal to pszStr.
* It is logically equal to Str.Mid(ipIndex, FSStrLen(pszStr))==pszStr, but much faster.
* @param[in] ipIndex Position where substring starts.
* @param[in] pszStr Sting to compare.
* @retval true String contains pszStr at ipIndex.
* @retval false Otherwise.
* @sa ContainsAt, EndsWith
*/
	bool ContainsAt(INTPTR ipIndex, const CHARTYPE *pszStr) const
	{
		ASSERT(ipIndex>=0);
		if (ipIndex<0 || ipIndex>GetLength()) {
			return false;
		}
		const CHARTYPE *pszMyStr=m_pszStr+ipIndex;
		if (!pszStr) {
			return true;
		}
		while (*pszStr){
			if (*pszMyStr++ != *pszStr++) {
				return false;
			}
		}
		return true;
	}

/**
* Checks whether string ends with pszStr.
* It is logically equal to Str.Right(FSStrLen(pszStr))==pszStr, but much faster.
* @param[in] pszStr Sting to check.
* @retval true String ends with pszStr.
* @retval false Otherwise.
* @sa StartsWith, ContainsAt
*/
	bool EndsWith(const CHARTYPE *pszStr) const
	{
		INTPTR ipMyLength=GetLength();
		pszStr=FSSafeStr(pszStr);
		INTPTR ipLength=FSStrLen(pszStr);
		if (ipLength>ipMyLength) {
			return false;
		}
		return (memcmp(m_pszStr+ipMyLength-ipLength, pszStr, ipLength*sizeof(CHARTYPE))==0);
	}

/**
* Searches for first matching substring in the string.
* @param[in] pszStr Substring to search for.
* @param[in] ipStartPos Start the search from specific position.
* @return Index of first character in string that matches pszStr.
* @retval -1 Not found.
*/
	INTPTR Find(const CHARTYPE *pszStr, INTPTR ipStartPos=0) const
	{
		ASSERT(ipStartPos>=0);
		if (ipStartPos<0 || ipStartPos>=GetLength()) {
			return -1;
		}
		const CHARTYPE *pCh=FSStrStr(m_pszStr+ipStartPos, FSSafeStr(pszStr));
		return (pCh ? pCh-m_pszStr : -1);
	}

/**
* Searches for first matching characters in the string.
* @param[in] cChar Character to search for.
* @param[in] ipStartPos Start the search from specific position.
* @return Index of first found matching character.
* @retval -1 Not found.
*/
	INTPTR Find(CHARTYPE cChar, INTPTR ipStartPos=0) const
	{
		ASSERT(ipStartPos>=0);
		if (ipStartPos<0 || ipStartPos>=GetLength()) {
			return -1;
		}
		const CHARTYPE *pCh=FSStrChr(m_pszStr+ipStartPos, cChar);
		return (pCh ? pCh-m_pszStr : -1);
	}

/**
* Searches for last matching substring in the string.
* @param[in] pszStr Substring to search for.
* @return Index of first character in string that matches pszStr.
* @retval -1 Not found.
*/
	INTPTR ReverseFind(const CHARTYPE *pszStr) const
	{
		const CHARTYPE *pCh=FSStrRStr(m_pszStr, FSSafeStr(pszStr));
		return (pCh ? pCh-m_pszStr : -1);
	}

/**
* Searches for last matching characters in the string.
* @param[in] cChar Character to search for.
* @return Index of found matching character.
* @retval -1 Not found.
*/
	INTPTR ReverseFind(CHARTYPE cChar) const
	{
		const CHARTYPE *pCh=FSStrRChr(m_pszStr, cChar);
		return (pCh ? pCh-m_pszStr : -1);
	}

/**
* Searches for first matching characters defined in pszStr.
* @param[in] pszStr A set of characters to search for.
* @return Index of first found matching character.
* @retval -1 Not found.
*/
	INTPTR FindOneOf(const CHARTYPE *pszStr) const
	{
		const CHARTYPE *pCh=FSStrSet(m_pszStr, FSSafeStr(pszStr));
		return (pCh ? pCh-m_pszStr : -1);
	}

/**
* Replaces substrings with new ones.
* @param[in] pszOld Substring to search for.
* @param[in] pszNew String to replace with.
* @param[in] iMode Search-replace mode (eReplaceMode).\n
* REPLACE_1 Only one replacement is done.\n
* REPLACE_ALL Replaces all substrings with new one.
* For example "aaaa".Replace("aa", "a", REPLACE_ALL) = "aa"\n
* REPLACE_CONT repeatedly executes function until there are no changes.
* For example "aaaab".Replace("aab", "b", REPLACE_CONT) = "b"\n
* REPLACE_ALL|REPLACE_CONT executes REPLACE_ALL in inner loop and REPLACE_CONT in outer loop.
* @return Count of replacements made.
*/
	INTPTR Replace(const CHARTYPE *pszOld, const CHARTYPE *pszNew, int iMode)
	{
		pszOld=FSSafeStr(pszOld);
		pszNew=FSSafeStr(pszNew);
		if (IsOverlapped(pszOld) || IsOverlapped(pszNew)) {
			return Replace(CFSBaseString(pszOld), CFSBaseString(pszNew), iMode);
		}
		INTPTR ipCount=0;

		if (iMode & REPLACE_CONT){
			INTPTR ipSubCount;
			do{
				ipSubCount=Replace(pszOld, pszNew, iMode & ~REPLACE_CONT);
				ipCount+=ipSubCount;
			}while (ipSubCount);
			return ipCount;
		}


		INTPTR ipOldLength=FSStrLen(pszOld);

		if (iMode & REPLACE_ALL) {
			INTPTR ipStart=0;
			CFSBaseString szResult;
			for (;;) {
				INTPTR ipPos=Find(pszOld, ipStart);
				if (ipPos>=0) {
					szResult+=Mid(ipStart, ipPos-ipStart);
					szResult+=pszNew;
					ipStart=ipPos+ipOldLength;
					ipCount++;
				}
				else{
					*this=szResult+Mid(ipStart);
					break;
				}
			}
		}
		else{
			INTPTR ipPos=Find(pszOld);
			if (ipPos>=0) {
				*this=Left(ipPos)+pszNew+Mid(ipPos+ipOldLength);
				ipCount=1;
			}
		}
		return ipCount;
	}

/**
* Makes string lower case.
* @sa ToLower, MakeUpper, ToUpper
*/
	void MakeLower()
	{
		if (IsEmpty()) {
			return;
		}
		_GetBuffer(GetLength()+1, 1);
		for (CHARTYPE *pCh=m_pszStr; pCh[0]; pCh++) {
			pCh[0]=STRFUNCTIONS::ToLower(pCh[0]);
		}
		// _ReleaseBuffer() unnecessary
	}

/**
* @return Lower case version of the string.
* @sa MakeLower, ToUpper, MakeUpper
*/
	CFSBaseString ToLower() const
	{
		CFSBaseString szResult;
		if (!IsEmpty()) {
			INTPTR ipLength=GetLength();
			szResult._GetBuffer(ipLength+1, 0);
			for (INTPTR ip=0; ip<ipLength; ip++) {
				szResult.m_pszStr[ip]=STRFUNCTIONS::ToLower(m_pszStr[ip]);
			}
			szResult._ReleaseBuffer(ipLength);
		}
		return szResult;
	}

/**
* Makes string upper case.
* @sa ToUpper, MakeLower, ToLower
*/
	void MakeUpper()
	{
		if (IsEmpty()) {
			return;
		}
		_GetBuffer(GetLength()+1, 1);
		for (CHARTYPE *pCh=m_pszStr; pCh[0]; pCh++) {
			pCh[0]=STRFUNCTIONS::ToUpper(pCh[0]);
		}
		// _ReleaseBuffer() unnecessary
	}

/**
* @return Upper case version of the string.
* @sa MakeUpper, ToLower, MakeLower
*/
	CFSBaseString ToUpper() const
	{
		CFSBaseString szResult;
		if (!IsEmpty()) {
			INTPTR ipLength=GetLength();
			szResult._GetBuffer(ipLength+1, 0);
			for (INTPTR ip=0; ip<ipLength; ip++) {
				szResult.m_pszStr[ip]=STRFUNCTIONS::ToUpper(m_pszStr[ip]);
			}
			szResult._ReleaseBuffer(ipLength);
		}
		return szResult;
	}

/**
* Reverses string.
* For example, "abc".MakeReverse()="cba"
*/
	void MakeReverse()
	{
		if (IsEmpty()) {
			return;
		}
		INTPTR ipMyLength=GetLength();
		if (GetData()->IsLocked()) {
			for (INTPTR ip=0; ip<(ipMyLength>>1); ip++){
				CHARTYPE cTemp=m_pszStr[ip];
				m_pszStr[ip]=m_pszStr[ipMyLength-ip-1];
				m_pszStr[ipMyLength-ip-1]=cTemp;
			}
		}
		else{
			CHARTYPE *pszStr=Alloc(ipMyLength+1);
			for (INTPTR ip=0; ip<ipMyLength; ip++){
				pszStr[ip]=m_pszStr[ipMyLength-ip-1];
			}
			Release();
			m_pszStr=pszStr;
			_ReleaseBuffer(ipMyLength);
		}
	}

/**
* Removes all existence of specific character from string.
* @param[in] cChar Character to remove.\n
* For exacmple, "abcba".Remove('b')="aca"
*/
	INTPTR Remove(CHARTYPE cChar)
	{
		if (IsEmpty()) {
			return 0;
		}
		INTPTR ipLength=GetLength();
		_GetBuffer(ipLength+1, 1);
		INTPTR ipDest=0;
		for (INTPTR ipSrc=0; ipSrc<ipLength; ipSrc++) {
			if (m_pszStr[ipSrc]==cChar) {
				continue;
			}
			if (ipSrc!=ipDest) {
				m_pszStr[ipDest]=m_pszStr[ipSrc];
			}
			ipDest++;
		}
		_ReleaseBuffer(ipDest);
		return ipLength-ipDest;
	}

/*
* Inserts substring into string.
* @param[in] ipStartPos Index to insert to.
* @pszStr[in] pszStr String to be inserted.\n
* For example, "abc".Insert(1, "XY")="aXYbc"
*/
	void Insert(INTPTR ipStartPos, const CHARTYPE *pszStr)
	{
		ASSERT(ipStartPos>=0 && ipStartPos<=GetLength());
		pszStr=FSSafeStr(pszStr);
		INTPTR ipLength=FSStrLen(pszStr);
		if (!ipLength) {
			return;
		}
		INTPTR ipMyLength=GetLength();
		if (ipStartPos<0 || ipStartPos>ipMyLength) {
			return;
		}
		if (GetData()->IsLocked()) { 
			if (IsOverlapped(pszStr)) {
				Insert(ipStartPos, CFSBaseString(pszStr));
				return;
			}
			_GetBuffer(ipMyLength+ipLength+1, 1);
			memmove(m_pszStr+ipStartPos+ipLength, m_pszStr+ipStartPos, (ipMyLength-ipStartPos)*sizeof(CHARTYPE));
			memcpy(m_pszStr+ipStartPos, pszStr, ipLength*sizeof(CHARTYPE));
		}
		else{
			CHARTYPE *pszStrNew=Alloc(ipMyLength+ipLength+1);
			memcpy(pszStrNew, m_pszStr, ipStartPos*sizeof(CHARTYPE));
			memcpy(pszStrNew+ipStartPos, pszStr, ipLength*sizeof(CHARTYPE));
			memcpy(pszStrNew+ipStartPos+ipLength, m_pszStr+ipStartPos, (ipMyLength-ipStartPos)*sizeof(CHARTYPE));
			Release();
			m_pszStr=pszStrNew;
		}
		_ReleaseBuffer(ipMyLength+ipLength);
	}

/**
* Deletes substring from string.
* @param[in] ipStartPos Index to start deletion from.
* @param[in] ipLength Length of the string to be deleted.
*/
	void Delete(INTPTR ipStartPos, INTPTR ipLength=1)
	{
		ASSERT(ipStartPos>=0);
		ASSERT(ipLength>=0);
		INTPTR ipOldLength=GetLength();
		if (ipStartPos<0 || ipStartPos>=ipOldLength) {
			return;
		}
		ipLength=FSMIN(ipLength, ipOldLength-ipStartPos);
		if (!ipLength) {
			return;
		}
		_GetBuffer(ipOldLength+1, 1);
		memmove(m_pszStr+ipStartPos, m_pszStr+ipStartPos+ipLength, (ipOldLength-ipLength-ipStartPos)*sizeof(CHARTYPE));
		_ReleaseBuffer(ipOldLength-ipLength);
	}

/**
* Truncate string so it will be ipPos characters long.
* @param[in] ipPos Length of the string to truncate to.
*/
	void Truncate(INTPTR ipPos)
	{
		SetAt(ipPos, 0);
	}

/**
* Removes control characters and whitespaces from the beginning of the string.
* @return Number of characters removed.
* @sa TrimRight, Trim
*/
	INTPTR TrimLeft()
	{
		INTPTR ipPos=0;
		for (; m_pszStr[ipPos]; ipPos++){
			if (!FSIsSpace(m_pszStr[ipPos])) {
				break;
			}
		}
		if (ipPos) {
			*this=Mid(ipPos);
		}
		return ipPos;
	}

/**
* Removes custom characters from the beginning of the string.
* @param[in] pszStr Set of characters to remove.
* @return Number of characters removed.
*/
	INTPTR TrimLeft(const CHARTYPE *pszStr)
	{
		pszStr=FSSafeStr(pszStr);
		INTPTR ipPos=0;
		for (; m_pszStr[ipPos]; ipPos++){
			if (!FSStrChr(pszStr, m_pszStr[ipPos])) {
				break;
			}
		}
		if (ipPos) {
			*this=Mid(ipPos);
		}
		return ipPos;
	}

/**
* Removes control characters and whitespaces from the end of the string.
* @return Number of characters removed.
* @sa TrimLeft, Trim
*/
	INTPTR TrimRight()
	{
		INTPTR ipPos=GetLength();
		for (; ipPos>0; ipPos--){
			if (!FSIsSpace(m_pszStr[ipPos-1])) {
				break;
			}
		}
		INTPTR ipRes=GetLength()-ipPos;
		if (ipRes) {
			Truncate(ipPos);
		}
		return ipRes;
	}

/**
* Removes custom characters from the end of the string.
* @param[in] pszStr Set of characters to remove.
* @return Number of characters removed.
*/
	INTPTR TrimRight(const CHARTYPE *pszStr)
	{
		pszStr=FSSafeStr(pszStr);
		INTPTR ipPos=GetLength();
		for (; ipPos>0; ipPos--){
			if (!FSStrChr(pszStr, m_pszStr[ipPos-1])) {
				break;
			}
		}
		INTPTR ipRes=GetLength()-ipPos;
		if (ipRes) {
			Truncate(ipPos);
		}
		return ipRes;
	}

/**
* Removes control characters and whitespaces from the both sides of the string.
* @return Number of characters removed from the beginning.
* @sa TrimLeft, TrimRight
*/
	INTPTR Trim() 
	{
		TrimRight();
		return TrimLeft();
	}

/**
* Removes control characters and whitespaces from the both sides of the string.
* @param[in] pszStr Set of characters to remove.
* @return Number of characters removed from the beginning.
* @sa TrimLeft, TrimRight
*/
	INTPTR Trim(const CHARTYPE *pszStr) 
	{
		TrimRight(pszStr);
		return TrimLeft(pszStr);
	}

/**
* Casts string into 0-terminated C-string.
* @return Pointer to 0-terminated string.
*/
	operator const CHARTYPE* () const 
	{
		return m_pszStr;
	}

/**
* Provides access to string buffer. String buffer will be locked and not shared to another strings.
* Caller must make sure, that the buffer contains correct 0-terminated string if any string functions are called.
* ReleaseBuffer should be called to set string back to its normal state.
* @param[in] ipSize Minimum size of buffer needed.
* @return Pointer to 0-terminated string buffer.
* @sa ReleaseBuffer
*/
	CHARTYPE *GetBuffer(INTPTR ipSize)
	{
		_GetBuffer(ipSize, 1);
		if (m_pszStr!=GetNullString()){
			GetData()->m_iRefCount--; // Lock buffer, no interlock necessary
		}
		return m_pszStr;
	}

/**
* Releases string buffer previously got from GetBuffer().
* @param[in] ipSize Length of the modified string. If ipSize is -1, string length is automatically calculated.
*/
	void ReleaseBuffer(INTPTR ipSize=-1)
	{
		ASSERT(ipSize>=-1);
		if (m_pszStr!=GetNullString()){
			ASSERT(GetData()->IsLocked());
			GetData()->m_iRefCount++; // Unlock buffer
		}
		if (ipSize<0) {
			ipSize=FSStrLen(m_pszStr);
		}
		_ReleaseBuffer(ipSize);
	}

/**
* Returns specified character in string.
* @param[in] Pos Index of the character requested. Valid range: 0<=Pos<=GetLength().
* @return Character in the position.
* Character at position GetLength() is always 0, characters at other positions are never 0.
* @sa GetAt
*/
	template <class INDEX> CHARTYPE operator[](INDEX Pos) const
	{
		return GetAt(Pos);
	}

/**
* Returns reference to specified character in string.\n
* On read access: Character at position GetLength() is always 0, characters at other positions are never 0.\n
* On write access: If 0-character is written somewhere in the string, string is automatically shortened in length.
* If non-0 character is written to the last position, string length will be automatically increased by 1.
* @param[in] Pos Index of the character requested. Valid range: 0<=Pos<=GetLength().
* @return Reference to character in the position.
* CFSBaseStringChar is a technical trick to differ read-write operations.
* Its usage is still classic, like String[2]='a' or char c=String[2].\n
* @sa GetAt, SetAt
*/
	template <class INDEX> CFSBaseStringChar operator[](INDEX Pos)
	{
		return CFSBaseStringChar(this, Pos);
	}

/**
* Returns specified character in string.
* @param[in] ipPos Index of the character requested. Valid range: 0<=Pos<=GetLength().
* @return Character in the position.
* Character at position GetLength() is always 0, characters at other positions are never 0.
* @sa operator[]
*/
	CHARTYPE GetAt(INTPTR ipPos) const
	{
		ASSERT(ipPos>=0 && ipPos<=GetLength());
		return m_pszStr[ipPos];
	}

/**
* Sets a value of a character in a string.
* If 0-character is written somewhere in the string, string is automatically shortened in length.
* If non-0 character is written to the last position, string length will be automatically increased by 1.
* @param[in] ipPos An Index of character which value will be set. Valid range: 0<=Pos<=GetLength().
* @param[in] cChar Value to set character to.
* @sa operator[]
*/
	void SetAt(INTPTR ipPos, CHARTYPE cChar)
	{
		ASSERT(ipPos>=0 && ipPos<=GetLength());
		if (cChar){
			if (ipPos<GetLength()){
				_GetBuffer(GetLength()+1, 1);
				m_pszStr[ipPos]=cChar;
				// _ReleaseBuffer(); unnecessary
			}
			else{
				INTPTR ipOldLength=GetLength();
				_GetBuffer(ipOldLength+2, 1);
				m_pszStr[ipOldLength]=cChar;
				_ReleaseBuffer(ipOldLength+1);
			}
		}
		else{
			_GetBuffer(ipPos+1, 1);
			_ReleaseBuffer(ipPos);
		}
	}

/**
* Compares two strings.
* @param[in] pszStr String to compare to.
* @retval 0 Strings are identical.
* @retval <0 this is smaller than pszStr.
* @retval >0 this is larger than pszStr.
* @sa CompareNoCase
*/
	int Compare(const CHARTYPE *pszStr) const
	{
		return FSStrCmp(m_pszStr, FSSafeStr(pszStr));
	}

/**
* Compares two strings in case-insenstive mode.
* @param[in] pszStr String to compare to.
* @retval 0 Strings are identical.
* @retval <0 this is smaller than pszStr.
* @retval >0 this is larger than pszStr.
* @sa g_lFSCodePage, Compare
*/
	int CompareNoCase(const CHARTYPE *pszStr) const
	{
		pszStr=FSSafeStr(pszStr);
		for (INTPTR ip=0; ; ip++){
			CHARTYPE ch1=STRFUNCTIONS::ToLower(m_pszStr[ip]);
			CHARTYPE ch2=STRFUNCTIONS::ToLower(pszStr[ip]);
			if (ch1<ch2) {
				return -1;
			}
			if (ch1>ch2) {
				return 1;
			}
			if (!ch1) {
				return 0;
			}
		}	
	}

/**
* Formats string in printf-style.
* @param[in] pszFormat A printf-style format string.\n
* %%[flag][width][.prec][size]format\n
*
* flag:\n
* \arg - - left align.
* \arg + - always displays sign of signed integer. Applies to [d]\n
* \arg ' ' - display ' ' or '-' as a sign of signed integer. Applies to [d]\n
* \arg # - adds C-style format specifier for integers: 0 for oct, 0x/0X  for hex. Applies to [uoxX].\n
*
* width:\n
* \arg number - minimum width of the result, fill with blanks, if neccessary.\n
* \arg 0number - minimum width of the result, fill numbers with '0', if neccessary.\n
*
* prec:\n
* \arg number - number of significant digits/characters.\n
* For [s] no more characters than prec, id displayed.
* For [diuoxXp] number is zero-expanded to prec characters.
* For [eEf] prec means number of digits after comma.
*
* size:\n
* \arg l - argument size is long. Applies to [duoxXeEf].\n
* \arg z - argument size is intptr. Applies to [duoxX].\n
*
* format:\n
* \arg %% - %%\n
* \arg c - character - h\n
* \arg s - string - hello\n
* \arg d - int - -1235\n
* \arg i - int - same as d
* \arg u - uint - 32748\n
* \arg o - uintoct - 53454\n
* \arg x - uinthex - abad\n
* \arg X - uinthex - ABAD\n
* \arg p - pointer - 78ABCD56\n
* \arg e - double - 1.234e-006 (warning: uses sprintf!)\n
* \arg E - double - 1.234E-006 (warning: uses sprintf!)\n
* \arg f - double - 12.567 (warning: uses sprintf!)\n
*
* @sa FormatV
*/
	void Format(const CHARTYPE *pszFormat, ...)
	{
		va_list Args;
		va_start(Args, pszFormat);
		FormatV(pszFormat, Args);
		va_end(Args);
	}

/**
* Formats string in vprintf-style.
* @param[in] pszFormat A printf-style format string.
* @param[in] Args Argument list.
* @sa Format
*/
	void FormatV(const CHARTYPE *pszFormat, va_list Args)
	{
		if (IsOverlapped(pszFormat)){
			FormatV(CFSBaseString(pszFormat), Args);
			return;
		}
		Empty();
		if (!pszFormat) return;

		enum { __TEXT, __FLAG, __WIDTH, __PREC, __SIZE, __FORMAT, __DONE };
		int iMode=__TEXT;

		char cFlag=0;
		int iWidth=0;
		char cFill=0;
		int iPrec=0;
		char cSize=0;
		char cFormat=0;
		bool bLeftAlign=false;
		for (INTPTR iPos=0; pszFormat[iPos]; iPos++){
			char Ch=((pszFormat[iPos]&0x7f) == pszFormat[iPos] ? (char)pszFormat[iPos] : 0);
			switch (iMode){
				case __TEXT:
					if (Ch=='%'){
						cFlag=cSize=cFormat=0; cFill=' ';
						iWidth=0; iPrec=-1;
						bLeftAlign=false;
						iMode=__FLAG;
					}
					else {
						(*this)+=pszFormat[iPos];
					}
				break;
				case __FLAG:
					if (Ch=='-') {
						bLeftAlign=true;
					}
					else if (strchr("+ #", Ch)!=0) {
						cFlag=Ch;
					}
					else { 
						iPos--;
						iMode=__WIDTH;
					}
				break;
				case __WIDTH:
					if (Ch=='0' && iWidth==0) {
						cFill='0';
					}
					if (strchr("0123456789", Ch)!=0) {
						iWidth=iWidth*10+(Ch-'0');
					}
					else {
						iMode=__PREC;
						iPos--;
					}
				break;
				case __PREC:
					if (Ch=='.') {
						iPrec=0;
					}
					else if (strchr("0123456789", Ch)!=0) {
						iPrec=iPrec*10+(Ch-'0');
					}
					else { 
						iMode=__SIZE;
						iPos--;
					}
				break;
				case __SIZE:
					if (strchr("lz", Ch)!=0) {
						cSize=Ch;
					}
					else {
						iPos--;
					}
					iMode=__FORMAT;
				break;
				case __FORMAT:
					switch (Ch){
						case '%':
							(*this)+='%';
						break;
						case 'c':{
							if (!bLeftAlign) {
								for (INTPTR iFill=1; iFill<iWidth; iFill++) {
									(*this)+=(CHARTYPE)' ';
								}
							}
							(*this)+=(CHARTYPE)va_arg(Args, int);
							if (bLeftAlign) {
								for (INTPTR iFill=1; iFill<iWidth; iFill++) {
									(*this)+=(CHARTYPE)' ';
								}
							}
						}break;
						case 's':{
							CFSBaseString sTemp=va_arg(Args, const CHARTYPE *);
							if (iPrec>=0) {
								sTemp=sTemp.Left(iPrec);
							}
							if (!bLeftAlign) {
								for (INTPTR iFill=sTemp.GetLength(); iFill<iWidth; iFill++) {
									(*this)+=(CHARTYPE)' ';
								}
							}
							(*this)+=sTemp;
							if (bLeftAlign) {
								for (INTPTR iFill=sTemp.GetLength(); iFill<iWidth; iFill++) {
									(*this)+=(CHARTYPE)' ';
								}
							}
						}break;
						case 'd':
						case 'i':
							if (cSize=='l') {
								(*this)+=FormatSInt(va_arg(Args, long), "0123456789", (cFlag=='+' ? "+" : (cFlag==' ' ? " " : "")), iWidth, cFill, bLeftAlign, iPrec);
							}
							else if (cSize=='z') {
								(*this)+=FormatSInt(va_arg(Args, INTPTR), "0123456789", (cFlag=='+' ? "+" : (cFlag==' ' ? " " : "")), iWidth, cFill, bLeftAlign, iPrec);
							}
							else {
								(*this)+=FormatSInt(va_arg(Args, int), "0123456789", (cFlag=='+' ? "+" : (cFlag==' ' ? " " : "")), iWidth, cFill, bLeftAlign, iPrec);
							}
						break;
						case 'u':
							if (cSize=='l') {
								(*this)+=FormatUInt(va_arg(Args, unsigned long), "0123456789", "", iWidth, cFill, bLeftAlign, iPrec);
							}
							else if (cSize=='z') {
								(*this)+=FormatUInt(va_arg(Args, UINTPTR), "0123456789", "", iWidth, cFill, bLeftAlign, iPrec);
							}
							else {
								(*this)+=FormatUInt(va_arg(Args, unsigned int), "0123456789", "", iWidth, cFill, bLeftAlign, iPrec);
							}
						break;
						case 'o':
							if (cSize=='l') {
								(*this)+=FormatUInt(va_arg(Args, unsigned long), "01234567", (cFlag=='#' ? "0" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else if (cSize=='z') {
								(*this)+=FormatUInt(va_arg(Args, UINTPTR), "01234567", (cFlag=='#' ? "0" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else {
								(*this)+=FormatUInt(va_arg(Args, unsigned int), "01234567", (cFlag=='#' ? "0" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
						break;
						case 'x':
							if (cSize=='l') {
								(*this)+=FormatUInt(va_arg(Args, unsigned long), "0123456789abcdef", (cFlag=='#' ? "0x" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else if (cSize=='z') {
								(*this)+=FormatUInt(va_arg(Args, UINTPTR), "0123456789abcdef", (cFlag=='#' ? "0x" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else {
								(*this)+=FormatUInt(va_arg(Args, unsigned int), "0123456789abcdef", (cFlag=='#' ? "0x" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
						break;
						case 'X':
							if (cSize=='l') {
								(*this)+=FormatUInt(va_arg(Args, unsigned long), "0123456789ABCDEF", (cFlag=='#' ? "0X" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else if (cSize=='z') {
								(*this)+=FormatUInt(va_arg(Args, UINTPTR), "0123456789ABCDEF", (cFlag=='#' ? "0X" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
							else {
								(*this)+=FormatUInt(va_arg(Args, unsigned int), "0123456789ABCDEF", (cFlag=='#' ? "0X" : ""), iWidth, cFill, bLeftAlign, iPrec);
							}
						break;
						case 'p':
							if (iPrec==-1) {
								iPrec=(int)(sizeof(UINTPTR)*2);
							}
							(*this)+=FormatUInt(va_arg(Args, UINTPTR), "0123456789ABCDEF",  "", iWidth, cFill, bLeftAlign, iPrec);
						break;
						case 'e':
						case 'E':
						case 'f':
							if (iPrec==-1) {
								iPrec=6;
							}
							if (cSize=='l') {
								(*this)+=FormatDouble((double)va_arg(Args, long double), (cFlag=='+' ? "+" : (cFlag==' ' ? " " : "")), iWidth, cFill, bLeftAlign, iPrec, Ch);
							}
							else {
								(*this)+=FormatDouble(va_arg(Args, double), (cFlag=='+' ? "+" : (cFlag==' ' ? " " : "")), iWidth, cFill, bLeftAlign, iPrec, Ch);
							}
						break;
					}
					iMode=__TEXT;
				break;
			}
		}
	}

	CFSBaseString &operator =(const CFSBaseString &szStr)
	{
		if (szStr.GetData()->IsLocked() || GetData()->IsLocked()) {
			return operator =((const CHARTYPE *)szStr);
		}
		if (szStr.m_pszStr!=m_pszStr){
			Release();
			m_pszStr=szStr.m_pszStr;
			AddRef();
		}
		return *this;
	}

#if defined (__FSCXX0X)
	CFSBaseString &operator =(CFSBaseString &&szStr)
	{
		if (szStr.GetData()->IsLocked() || GetData()->IsLocked()) {
			return operator =((const CHARTYPE *)szStr);
		}
		if (szStr.m_pszStr!=m_pszStr){
			Release();
			m_pszStr=szStr.m_pszStr;
			szStr.m_pszStr=szStr.GetNullString();
		}
		return *this;
	}
#endif

	CFSBaseString &operator =(const CHARTYPE *pszStr)
	{
		if (pszStr && pszStr[0]){
			if (IsOverlapped(pszStr)) {
				return operator=(CFSBaseString(pszStr));
			}
			INTPTR ipLength=FSStrLen(pszStr);
			_GetBuffer(ipLength+1, 0);
			memcpy(m_pszStr, pszStr, ipLength*sizeof(CHARTYPE));
			_ReleaseBuffer(ipLength);
		}
		else {
			Empty();
		}
		return *this;
	}

	CFSBaseString &operator =(CHARTYPE cChar)
	{
		if (cChar){
			_GetBuffer(2, 0);
			m_pszStr[0]=cChar;
			_ReleaseBuffer(1);
		}
		else {
			Empty();
		}
		return *this;
	}

	CFSBaseString &operator +=(const CFSBaseString &szStr)
	{
		if (IsEmpty() && !szStr.IsEmpty()) {
			*this=szStr;
		}
		else {
			Append(szStr, szStr.GetLength());
		}
		return *this;
	}

	CFSBaseString &operator +=(const CHARTYPE *pszStr)
	{
		if (pszStr){
			if (IsOverlapped(pszStr)) {
				return operator+=(CFSBaseString(pszStr));
			}
			Append(pszStr, FSStrLen(pszStr));
		}
		return *this;
	}

	CFSBaseString &operator +=(CHARTYPE cChar)
	{
		if (cChar) {
			Append(&cChar, 1);
		}
		return *this;
	}

	friend CFSBaseString operator +(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		if (szStr2.IsEmpty()) {
			return szStr1;
		}
		if (szStr1.IsEmpty()) {
			return szStr2;
		}
		CFSBaseString szResult;
		Concatenate(szResult, szStr1, szStr1.GetLength(), szStr2, szStr2.GetLength());
		return szResult;
	}
	friend CFSBaseString operator +(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		pszStr2=FSSafeStr(pszStr2);
		INTPTR ipLength2=FSStrLen(pszStr2);
		if (!ipLength2) {
			return szStr1;
		}
		CFSBaseString szResult;
		Concatenate(szResult, szStr1, szStr1.GetLength(), pszStr2, ipLength2);
		return szResult;
	}
	friend CFSBaseString operator +(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		pszStr1=FSSafeStr(pszStr1);
		INTPTR ipLength1=FSStrLen(pszStr1);
		if (!ipLength1) {
			return szStr2;
		}
		CFSBaseString szResult;
		Concatenate(szResult, pszStr1, ipLength1, szStr2, szStr2.GetLength());
		return szResult;
	}
	friend CFSBaseString operator +(const CFSBaseString &szStr, CHARTYPE cChar)
	{
		if (!cChar) {
			return szStr;
		}
		CFSBaseString szResult;
		Concatenate(szResult, szStr, szStr.GetLength(), &cChar, 1);
		return szResult;
	}
	friend CFSBaseString operator +(CHARTYPE cChar, const CFSBaseString &szStr)
	{
		if (!cChar) {
			return szStr;
		}
		CFSBaseString szResult;
		Concatenate(szResult, &cChar, 1, szStr, szStr.GetLength());
		return szResult;
	}

	friend bool operator ==(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{ 
		return szStr1.Compare(szStr2)==0;
	}
	friend bool operator ==(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)==0;
	}
	friend bool operator ==(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)==0;
	}
	friend bool operator !=(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		return szStr1.Compare(szStr2)!=0;
	}
	friend bool operator !=(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)!=0;
	}
	friend bool operator !=(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)!=0;
	}
	friend bool operator <(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		return szStr1.Compare(szStr2)<0;
	}
	friend bool operator <(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)<0;
	}
	friend bool operator <(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)>0;
	}
	friend bool operator <=(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		return szStr1.Compare(szStr2)<=0;
	}
	friend bool operator <=(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)<=0;
	}
	friend bool operator <=(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)>=0;
	}
	friend bool operator >(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		return szStr1.Compare(szStr2)>0;
	}
	friend bool operator >(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)>0;
	}
	friend bool operator >(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)<0;
	}
	friend bool operator >=(const CFSBaseString &szStr1, const CFSBaseString &szStr2)
	{
		return szStr1.Compare(szStr2)>=0;
	}
	friend bool operator >=(const CFSBaseString &szStr1, const CHARTYPE *pszStr2)
	{
		return szStr1.Compare(pszStr2)>=0;
	}
	friend bool operator >=(const CHARTYPE *pszStr1, const CFSBaseString &szStr2)
	{
		return szStr2.Compare(pszStr1)<=0;
	}

/**
* Replace mode constants.
*/
	enum eReplaceMode { REPLACE_1=0, REPLACE_ALL=1, REPLACE_CONT=2 };

protected:
//	int Printf(CHARTYPE *pszBuf, const CHARTYPE *pszFormat, ...) const;
	CFSBaseString FromAscii7(const char *pszStr)
	{
		CFSBaseString szStr;
		if (!pszStr) {
			return szStr;
		}
		for (; pszStr[0]; pszStr++) {
			szStr+=pszStr[0];
		}
		return szStr;
	}

	CFSBaseString FormatIntAlign(CFSBaseString szStr, const char *pszPrefix, INTPTR ipMinLength, char cFill, bool bLeftAlign, INTPTR iPrec)
	{
		while (szStr.GetLength()<iPrec) {
			szStr=(CHARTYPE)'0'+szStr;
		}
		if (bLeftAlign){
			szStr=FromAscii7(pszPrefix)+szStr;
			while (szStr.GetLength()<ipMinLength) {
				szStr+=' ';
			}
		}
		else{
			if (cFill!=' ' && iPrec==-1){
				ipMinLength-=FSStrLen(pszPrefix);
				while (szStr.GetLength()<ipMinLength) {
					szStr=(CHARTYPE)cFill+szStr;
				}
				szStr=FromAscii7(pszPrefix)+szStr;
			}
			else{
				szStr=FromAscii7(pszPrefix)+szStr;
				while (szStr.GetLength()<ipMinLength) {
					szStr=(CHARTYPE)' '+szStr;
				}
			}
		}
		return szStr;
	}

	template<class TYPE>
	CFSBaseString FormatUInt(TYPE iInt, const char *pszChars, const char *pszPrefix, INTPTR ipMinLength, char cFill, bool bLeftAlign, INTPTR iPrec)
	{
		CFSBaseString szStr;
		INTPTR ipBase=FSStrLen(pszChars);
		if (iInt==0) {
			szStr='0';
		}
		else while (iInt){
			TYPE iMod=(TYPE)(iInt%ipBase);
			szStr=(CHARTYPE)pszChars[iMod]+szStr;
			iInt=(TYPE)(iInt/ipBase);
		}
		return FormatIntAlign(szStr, pszPrefix, ipMinLength, cFill, bLeftAlign, iPrec);
	}

	template<class TYPE>
	CFSBaseString FormatSInt(TYPE iInt, const char *pszChars, const char *pszPrefix, INTPTR ipMinLength, char cFill, bool bLeftAlign, INTPTR iPrec)
	{
		if (iInt>=0) {
			return FormatUInt(iInt, pszChars, pszPrefix, ipMinLength, cFill, bLeftAlign, iPrec);
		}
		INTPTR ipBase=FSStrLen(pszChars);
		CFSBaseString szStr;
		while (iInt){
			TYPE iMod=(TYPE)(iInt%ipBase);
			szStr=(CHARTYPE)pszChars[-iMod]+szStr;
			iInt=(TYPE)(iInt/ipBase);
		}
		return FormatIntAlign(szStr, "-", ipMinLength, cFill, bLeftAlign, iPrec);
	}

	CFSBaseString FormatDouble(double dDouble, const char *pszPrefix, int iMinLength, char cFill, bool bLeftAlign, int iPrecision, char cMain)
	{
		char szFill[2]={ (cFill==' ' ? '\0' : cFill), 0 };
		char szBuf1[128], szBuf2[1024];
#if defined (WIN32)
		_snprintf_s(szBuf1, 128, 127, "%%%s%s%s%d.%d%c", (bLeftAlign ? "-" : ""), pszPrefix, szFill, iMinLength, iPrecision, cMain); szBuf1[127]=0;
		_snprintf_s(szBuf2, 1024, 1023, szBuf1, dDouble); szBuf2[1023]=0;
#else
		snprintf(szBuf1, 127, "%%%s%s%s%d.%d%c", (bLeftAlign ? "-" : ""), pszPrefix, szFill, iMinLength, iPrecision, cMain);  szBuf1[127]=0;
		snprintf(szBuf2, 1023, szBuf1, dDouble); szBuf2[1023]=0;
#endif		
		return FromAscii7(szBuf2);
	}

	bool IsOverlapped(const CHARTYPE *pszStr) const
	{
		INTPTR ipOffset=pszStr-m_pszStr;
		return (ipOffset>=0 && ipOffset<GetData()->m_ipBufSize);
	}

	void Append(const CHARTYPE *pszStr, INTPTR ipLength)
	{
		if (ipLength>0){
			INTPTR ipMyLength=GetLength();
			_GetBuffer(ipMyLength+ipLength+1, 1);
			memcpy(m_pszStr+ipMyLength, pszStr, ipLength*sizeof(CHARTYPE));
			_ReleaseBuffer(ipMyLength+ipLength);
		}
	}

	static void Concatenate(CFSBaseString &szResult, const CHARTYPE *pszStr1, INTPTR ipLength1, const CHARTYPE *pszStr2, INTPTR ipLength2)
	{
		if (ipLength1+ipLength2>0){
			szResult._GetBuffer(ipLength1+ipLength2+1, 0);
			memcpy(szResult.m_pszStr, pszStr1, ipLength1*sizeof(CHARTYPE));
			memcpy(szResult.m_pszStr+ipLength1, pszStr2, ipLength2*sizeof(CHARTYPE));
			szResult._ReleaseBuffer(ipLength1+ipLength2);
		}
	}

	void _GetBuffer(INTPTR ipSize, bool bPreserve)
	{
		if (GetData()->IsShared() || ipSize>GetData()->m_ipBufSize){
			ASSERT(GetData()->m_iRefCount>=1); // Not locked
			if (ipSize<=0){
				Release();
				m_pszStr=GetNullString();
			}
			else{
				CHARTYPE *pszStr=Alloc(ipSize);
				INTPTR ipCount=FSMIN(ipSize-1, GetLength());
				if (bPreserve) {
					memcpy(pszStr, m_pszStr, ipCount*sizeof(CHARTYPE));
				}
				Release();
				m_pszStr=pszStr;
				if (bPreserve){
					GetData()->m_ipLength=ipCount;
					m_pszStr[ipCount]=0;
				}
			}
		}
	}

	void _ReleaseBuffer(INTPTR ipLength)
	{
		ASSERT(ipLength>=0);
		ASSERT(ipLength<GetData()->m_ipBufSize);
		if (m_pszStr==GetNullString()) {
			return;
		}
		ASSERT(GetData()->m_iRefCount<=1);
		if (ipLength<=0) {
			Empty();
		}
		else{
			GetData()->m_ipLength=ipLength;
			m_pszStr[ipLength]=0;
			ASSERT(GetLength()==FSStrLen(m_pszStr));
		}
	}

	CHARTYPE *Alloc(INTPTR ipSize)
	{
		ASSERT(ipSize>0);
		CHARTYPE *pszBuf=(CHARTYPE *)FSStringAlloc(ipSize, sizeof(CHARTYPE));
		pszBuf[0]=0;
		return pszBuf;
	}

	void Free(CHARTYPE *pszStr)
	{
		FSStringFree(pszStr, sizeof(CHARTYPE));
	}

	void AddRef()
	{
		if (m_pszStr!=GetNullString()){
			ASSERT(GetData()->m_iRefCount>=1);
			FSAtomicInc(&GetData()->m_iRefCount);
		}
	}

	void Release()
	{
		if (m_pszStr!=GetNullString()){
			if (FSAtomicDec(&GetData()->m_iRefCount)<=0) {
				Free(m_pszStr);
			}
		}
	}

	const CFSStringData *GetData() const
	{
		return ((CFSStringData *)m_pszStr)-1;
	}
	CFSStringData *GetData()
	{
		return ((CFSStringData *)m_pszStr)-1;
	}
	CHARTYPE *GetNullString() const
	{
		struct DataPlusNull{
			CFSStringData m_Data;
			CHARTYPE ch;
		};
		static const DataPlusNull NullStr={{1, 0, 2}, 0};
		return (CHARTYPE *)(((CFSStringData *)&NullStr)+1);
	}

	CHARTYPE *m_pszStr;
};

typedef CFSBaseString<char, CFSStrFunctions<char> > CFSAString;
typedef CFSBaseString<WCHAR, CFSStrFunctions<WCHAR> > CFSWString;

#if defined (UNICODE)
	#define CFSString CFSWString
	#define CFSStringArray CFSWStringArray
#else
	#define CFSString CFSAString
	#define CFSStringArray CFSAStringArray
#endif

#endif // _FSSTRING_H_ 
