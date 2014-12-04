#if !defined _FSSTREAM_H_
#define _FSSTREAM_H_

#include "fsexception.h"
#include "fsstring.h"

/**
* Default text-mode line breaks for different platforms.
*/
#if defined (WIN32)
#define FSLBA "\r\n"
#define FSLBW FSWSTR("\r\n")
#elif defined (UNIX)
#define FSLBA "\n"
#define FSLBW FSWSTR("\n")
#elif defined (MAC)
#define FSLBA "\r"
#define FSLBW FSWSTR("\r")
#endif

/**
* High level functionality for smart file.
* File stores data in internal format.
* Any data written with WriteSomeFunc must be read with corresponding ReadSomeFunc function.
* All low level writing goes through pure virtual functions, that must be overridden to get working class.
* @sa CFSFile, CFSMemFile
*/
class CFSStream
{
public:
	CFSStream() {}
	virtual ~CFSStream() {}

/**
* Reads one byte from file.\n
* Throws exception on error.
* @param[out] pByte Pointer to a variable, that receives data.
*/
	void ReadByte(BYTE *pByte);

/**
* Writes one byte to file.\n
* Throws exception on error.
* @param[in] Byte Value to store.
*/
	void WriteByte(BYTE Byte);

/**
* Reads character from file.\n
* Throws exception on error.
* @param[out] pChar Pointer to a variable, that receives data.
*/
	void ReadChar(char *pChar);

/**
* Reads wide character from file.\n
* Throws exception on error.
* @param[out] pChar Pointer to a variable, that receives data.
*/
	void ReadChar(WCHAR *pChar);

/**
* Writes character to file.\n
* Throws exception on error.
* @param[in] Char data to store.
*/
	void WriteChar(char Char);

/**
* Writes wide character to file.\n
* Throws exception on error.
* @param[in] Char data to store. Valid range of the WCHAR is 0..0x10ffff for 4byte WCHARs and 0..0xffff for 2byte WCHARs.
*/
	void WriteChar(WCHAR Char);

/**
* Reads boolean from file.\n
* Throws exception on error.
* @param[out] pBool Pointer to a variable, that receives data.
*/
	void ReadBool(bool *pBool);

/**
* Writes boolean to file.\n
* Throws exception on error.
* @param[in] Bool Value to store.
*/
	void WriteBool(bool Bool);

// To make it compilable with VC6/eVC4, templates below must be implemented in-place.
/**
* Reads packed signed integer from file.\n
* Throws exception on error.
* @param[out] pNumber Pointer to a variable, that receives data.
*/
	template <class TYPE> void ReadSInt(TYPE *pNumber)
	{
		STATIC_ASSERT(0>(TYPE)-1);
		const long lMaxBits=sizeof(TYPE)*8-1;
		BYTE Byte;
		ReadByte(&Byte);
		bool bNegative=((Byte&0x40)==0x40);
		*pNumber=Byte&0x3f;
		for (long l=6; Byte&0x80; l+=7){
			ReadByte(&Byte);
			if (l+7>lMaxBits){
				BYTE Byte2=Byte&0x7f;
				long lBits=0;
				for (; Byte2; Byte2>>=1) {
					lBits++;
				}
				if (l+lBits>lMaxBits) {
					throw CFSFileException(CFSFileException::INVALIDDATA);
				}
			}
			(*pNumber)|=((TYPE)(Byte&0x7f))<<l;
		}
		if (bNegative) {
			*pNumber=~*pNumber;
		}
	}

/**
* Reads packed unsigned integer from file.\n
* Throws exception on error.
* @param[out] pNumber Pointer to a variable, that receives data.
*/
	template <class TYPE> void ReadUInt(TYPE *pNumber)
	{
		STATIC_ASSERT(0<(TYPE)-1);
		const long lMaxBits=sizeof(TYPE)*8;
		BYTE Byte;
		*pNumber=0;
		for (long l=0; ; l+=7){
			ReadByte(&Byte);
			if (l+7>lMaxBits){
				BYTE Byte2=Byte&0x7f;
				long lBits=0;
				for (; Byte2; Byte2>>=1) {
					lBits++;
				}
				if (l+lBits>lMaxBits) {
					throw CFSFileException(CFSFileException::INVALIDDATA);
				}
			}
			(*pNumber)|=((TYPE)(Byte&0x7f))<<l;
			if ((Byte&0x80)==0) {
				break;
			}
		}
	}

/**
* Reads unpacked signed integer from file. Data in file must be in LittleEndian-format.\n
* Throws exception on error.
* @param[out] pNumber Pointer to a variable, that receives data.
* @param[in] iBytes Size of the number block in file in bytes. Never not use sizeof() here, use integer constants instead!
*/
	template <class TYPE> void ReadSInt(TYPE *pNumber, int iBytes)
	{
		STATIC_ASSERT(0>(TYPE)-1);
		*pNumber=0;
		BYTE Byte=0;
		int i;
		if ((int)sizeof(*pNumber)<=iBytes){
			for (i=0; i<(int)sizeof(*pNumber); i++){
				ReadByte(&Byte);
				*pNumber|=((TYPE)(Byte))<<(i*8);
			}
			bool bNegative=*pNumber<0;
			for (i=sizeof(*pNumber); i<iBytes; i++){
				ReadByte(&Byte);
				if (Byte!=(bNegative ? 0xff : 0)) {
					throw CFSFileException(CFSFileException::INVALIDDATA);
				}
			}
		}
		else{
			for (i=0; i<iBytes; i++){
				ReadByte(&Byte);
				*pNumber|=((TYPE)(Byte))<<(i*8);
			}
			bool bNegative=((Byte&0x80)==0x80);
			for (i=iBytes; i<(int)sizeof(*pNumber); i++){
				*pNumber|=((TYPE)(bNegative ? 0xff : 0))<<(i*8);
			}
		}
	}

/**
* Reads unpacked unsigned integer from file. Data in file must be in LittleEndian-format.\n
* Throws exception on error.
* @param[out] pNumber Pointer to a variable, that receives data.
* @param[in] iBytes Size of the number block in file in bytes. Never not use sizeof() here, use integer constants instead!
*/
	template <class TYPE> void ReadUInt(TYPE *pNumber, int iBytes)
	{
		STATIC_ASSERT(0<(TYPE)-1);
		*pNumber=0;
		BYTE Byte;
		for (int i=0; i<iBytes; i++){
			ReadByte(&Byte);
			if (i>=(int)sizeof(TYPE)){
				if (Byte) {
					throw CFSFileException(CFSFileException::INVALIDDATA);
				}
			}
			else {
				(*pNumber)|=((TYPE)(Byte))<<(i*8);
			}
		}
	}

/**
* Reads packed floating point from file.\n
* Throws exception on error.
* @param[out] pNumber Pointer to a variable, that receives data.
*/
	template<class TYPE> void ReadFloat(TYPE *pNumber)
	{
		*pNumber=(TYPE)0.0;
		BYTE byBuf;
		ReadByte(&byBuf);

		bool bSign=((byBuf&1)==1);
		byBuf>>=1;
		int iBit=1;
		for (int iPos=0; ; iPos--) {
			if (byBuf&1) {
				*pNumber+=ldexp((TYPE)0.5, iPos);
			}
			byBuf>>=1;
			iBit++;

			if (iBit==7) {
				if (byBuf&1) {
					ReadByte(&byBuf);
					iBit=0;
				}
				else {
					break;
				}
			}
		}
		
		int iExp;
		ReadSInt(&iExp);
		*pNumber=ldexp(*pNumber, iExp);

		if (bSign) {
			*pNumber=-*pNumber;
		}
	}

/**
* Writes packed signed integer to file.\n
* Throws exception on error.
* @param[in] Number Value to store.
*/
	template <class TYPE> void WriteSInt(TYPE Number)
	{
		STATIC_ASSERT(0>(TYPE)-1);
		bool bNegative=(Number<0);
		if (bNegative) {
			Number=~Number;
		}
		BYTE Byte=(BYTE)(Number&0x3f);
		Number>>=6;
		if (bNegative) {
			Byte|=0x40;
		}
		if (Number) {
			Byte|=0x80;
		}
		WriteByte(Byte);
		while (Number){
			Byte=(BYTE)(Number&0x7f);
			Number>>=7;
			if (Number) {
				Byte|=0x80;
			}
			WriteByte(Byte);
		}
	}

/**
* Writes packed unsigned integer to file.\n
* Throws exception on error.
* @param[in] Number Value to store.
*/
	template <class TYPE> void WriteUInt(TYPE Number)
	{
		STATIC_ASSERT(0<(TYPE)-1);
		do{
			BYTE Byte=(BYTE)(Number&0x7f);
			Number>>=7;
			if (Number) {
				Byte|=0x80;
			}
			WriteByte(Byte);
		}while (Number);
	}

/**
* Writes unpacked signed integer to file.\n
* Throws exception on error.
* @param[in] Number Value to store.
* @param[in] iBytes Size of the number block in file in bytes. Never not use sizeof() here, use integer constants instead!
*/
	template <class TYPE> void WriteSInt(TYPE Number, int iBytes)
	{
		STATIC_ASSERT(0>(TYPE)-1);
		bool bNegative=(Number<0);
		if (bNegative) {
			Number=~Number;
		}
		for (int i=0; i<iBytes; i++){
			WriteByte(bNegative ? ~(BYTE)Number : (BYTE)Number);
			Number>>=8;
		}
		if (Number) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
	}

/**
* Writes unpacked unsigned integer to file.\n
* Throws exception on error.
* @param[in] Number Value to store.
* @param[in] iBytes Size of the number block in file in bytes. Never not use sizeof() here, use integer constants instead!
*/
	template <class TYPE> void WriteUInt(TYPE Number, int iBytes)
	{
		STATIC_ASSERT(0<(TYPE)-1);
		for (int i=0; i<iBytes; i++){
			WriteByte((BYTE)Number);
			Number>>=8;
		}
		if (Number) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
	}

/**
* Writes packed floating point to file.\n
* Throws exception on error.
* @param[in] Number Value to store.
*/
	template<class TYPE> void WriteFloat(TYPE Number)
	{
		BYTE byBuf=(Number<0 ? 1 : 0);
		int iBit=1;
		Number=fabs(Number);

		int iExp;
		Number=frexp(Number, &iExp);

		while (Number!=0) {
			if (iBit>=7) {
				WriteByte(byBuf|0x80);
				byBuf=0; iBit=0;
			}
			byBuf|=1<<iBit;
			iBit++;

			int iExpSkip;
			Number=frexp(Number-(TYPE)0.5, &iExpSkip);
			for (; iExpSkip<-1; iExpSkip++) {
				if (iBit>=7) {
					WriteByte(byBuf|0x80);
					byBuf=0; iBit=0;
				}
				iBit++;
			}
		}
		WriteByte(byBuf);
		WriteSInt(iExp);
	}

/**
* Reads string from file.\n
* Throws exception on error.
* @param[out] pszStr Pointer to a variable, that receives data.
*/
	void ReadString(CFSAString *pszStr);

/**
* Reads wide string from file.\n
* Throws exception on error.
* @param[out] pszStr Pointer to a variable, that receives data.
*/
	void ReadString(CFSWString *pszStr);

/**
* Writes string to file.\n
* Throws exception on error.
* @param[in] szStr Value to store.
*/
	void WriteString(const CFSAString &szStr);

/**
* Writes wide string to file.\n
* Throws exception on error.
* @param[in] szStr Value to store.
*/
	void WriteString(const CFSWString &szStr);

/**
* Reads one text character from stream\n
* Does NOT throw exception in case of EOF.\n
* Unicode version reads Little endian UTF16 character.
* @param[out] pChar Pointer to a character that receives data.
* @retval true - no error.
*/
	bool ReadTextChar(char *pChar);
	bool ReadTextChar(wchar_t *pChar);

/**
* Reads textual line from file.\n
* Does NOT throw exception in case of EOF.\n
* @param[out] pszStr Pointer to a variable that receives data.
* @retval true - no error.
*/
	bool ReadTextLine(CFSAString *pszStr) {
		return __ReadTextLine(pszStr, 1);
	}
	bool ReadTextLine(CFSWString *pszStr);

/**
* Reads text from stream until one of predefined symbols is found.\n
* Does NOT throw exception in case of EOF.\n
* @param[out] pszStr Pointer to a variable that receives data.
* @param[in] szSymbols defines symbols that stop reading.
* @retval true - no error.
*/
	bool ReadTextUntil(CFSAString *pszStr, const CFSAString &szSymbols) {
		return __ReadTextUntil(pszStr, szSymbols);
	}
	bool ReadTextUntil(CFSWString *pszStr, const CFSWString &szSymbols);

/**
* Writes textual string to file.\n
* Throws exception on error.
* @param[in] szStr Value to store.
*/
	void WriteText(const CFSAString &szStr);

/**
* Writes textual wide string to file, LittleEndian UTF16 characters are used.\n
* Throws exception on error.
* @param[in] szStr Value to store.
*/
	void WriteText(const CFSWString &szStr);

/**
* Writes textual string to file.\n
* Throws exception on error.
* @param[in] pszFormat Format string, like fprintf.
*/
	void Printf(const char *pszFormat, ...);

/**
* Writes textual wide string to file.\n
* Throws exception on error.
* @param[in] pszFormat Format string, like fwprintf.
*/
	void Printf(const WCHAR *pszFormat, ...);

/**
* Streaming functions
*/
	CFSStream &operator<<(char Var) { WriteByte(Var); return *this; }
	CFSStream &operator<<(signed char Var) { WriteByte(Var); return *this; }
	CFSStream &operator<<(unsigned char Var) { WriteByte(Var); return *this; }

	CFSStream &operator<<(short Var) { WriteSInt(Var); return *this; }
	CFSStream &operator<<(int Var) { WriteSInt(Var); return *this; }
	CFSStream &operator<<(long Var) { WriteSInt(Var); return *this; }
	CFSStream &operator<<(long long Var) { WriteSInt(Var); return *this; }

	CFSStream &operator<<(unsigned short Var) { WriteUInt(Var); return *this; }
	CFSStream &operator<<(unsigned int Var) { WriteUInt(Var); return *this; }
	CFSStream &operator<<(unsigned long Var) { WriteUInt(Var); return *this; }
	CFSStream &operator<<(unsigned long long Var) { WriteUInt(Var); return *this; }

	CFSStream &operator<<(float Var) { WriteFloat(Var); return *this; }
	CFSStream &operator<<(double Var) { WriteFloat(Var); return *this; }
	CFSStream &operator<<(long double Var) { WriteFloat(Var); return *this; }

	CFSStream &operator<<(const CFSAString &Var) { WriteString(Var); return *this; }
	CFSStream &operator<<(const CFSWString &Var) { WriteString(Var); return *this; }

	CFSStream &operator>>(char &Var) { ReadByte((BYTE *)&Var); return *this; }
	CFSStream &operator>>(short &Var) { ReadSInt(&Var); return *this; }
	CFSStream &operator>>(int &Var) { ReadSInt(&Var); return *this; }
	CFSStream &operator>>(long &Var) { ReadSInt(&Var); return *this; }
	CFSStream &operator>>(long long &Var) { ReadSInt(&Var); return *this; }

	CFSStream &operator>>(unsigned char &Var) { ReadByte(&Var); return *this; }
	CFSStream &operator>>(unsigned short &Var) { ReadUInt(&Var); return *this; }
	CFSStream &operator>>(unsigned int &Var) { ReadUInt(&Var); return *this; }
	CFSStream &operator>>(unsigned long &Var) { ReadUInt(&Var); return *this; }
	CFSStream &operator>>(unsigned long long &Var) { ReadUInt(&Var); return *this; }

	CFSStream &operator>>(float &Var) { ReadFloat(&Var); return *this; }
	CFSStream &operator>>(double &Var) { ReadFloat(&Var); return *this; }
	CFSStream &operator>>(long double &Var) { ReadFloat(&Var); return *this; }

	CFSStream &operator>>(CFSAString &Var) { ReadString(&Var); return *this; }
	CFSStream &operator>>(CFSWString &Var) { ReadString(&Var); return *this; }

/**
* Reads binary data from file.\n
* Throws exception on error.
* @param[out] pBuf Pointer to a variable, that receives data.
* @param[in] ipBytes Number of bytes to read
* @param[in] bExceptionOnError If set, failure to read all the data results exception.
*/
	virtual INTPTR ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true) = 0;

/**
* Writes binary data to file.\n
* Throws exception on error.
* @param[in] pBuf Pointer to a buffer that contains data.
* @param[in] ipBytes Size of the data pointed by pBuf.
* @param[in] bExceptionOnError If set, failure to write all the data results exception.
*/
	virtual INTPTR WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true) = 0;

/**
* Moves file cursor to new place.\n
* Throws exception on error.
* @param[in] lPos Requested position of the cursor.
* @param[in] iType How cursor should be moved. Possible values SEEK_SET, SEEK_END, SEEK_CUR, see fseek for details.
*/
	virtual void Seek(INT64 lPos, int iType=SEEK_SET) = 0;

/**
* Returns cursor position in the file.
* @return File cursor position.
* @retval -1 Error occurred.
*/
	virtual INT64 Tell() const = 0;

/**
* Checks whether end of file is reached.
* @retval true EOF reached.
* @retval false EOF not reached.
*/
	virtual bool IsEOF() const = 0;

protected:
	template<class CHARTYPE> bool __ReadTextLine(CFSBaseString<CHARTYPE, CFSStrFunctions<CHARTYPE> > *pszStr, INTPTR ipSizeInStream) {
		pszStr->Empty();
		bool bNewLine=false;
		CHARTYPE ch;
		for (;;) {
			if (!ReadTextChar(&ch)) {
				break;
			}
			if (!ch) {
				throw CFSFileException(CFSFileException::INVALIDDATA);
			}
			if (bNewLine && ch!='\n') {
				Seek(-ipSizeInStream, SEEK_CUR);
				break;
			}
			(*pszStr)+=ch;
			if (ch=='\r') {
				bNewLine=true;
			}
			else if (ch=='\n') {
				break;
			}
		}
		return !pszStr->IsEmpty();
	}

	template<class CHARTYPE> bool __ReadTextUntil(CFSBaseString<CHARTYPE, CFSStrFunctions<CHARTYPE> > *pszStr, const CFSBaseString<CHARTYPE, CFSStrFunctions<CHARTYPE> > &szSymbols)
	{
		pszStr->Empty();
		char ch;
		for (;;) {
			if (!ReadTextChar(&ch)) {
				return !pszStr->IsEmpty();
			}
			if (!ch) {
				throw CFSFileException(CFSFileException::INVALIDDATA);
			}
			(*pszStr)+=ch;
			if (szSymbols.Find(ch)!=-1) {
				return true;
			}
		}
	}

};

#endif // _FSSTREAM_H_
