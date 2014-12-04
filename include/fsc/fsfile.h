#if !defined _FSFILE_H_
#define _FSFILE_H_

#include "fsstream.h"
#include "fsdata.h"
#include "fslist.h"

/**
* Class, that uniquely identifies the file.
* CFSFileName is equal to CFSString.
*/
typedef CFSString CFSFileName;

#if defined (WIN32)
/**
* Global handle to the module instance, that is used as helper for different functions.
* Variable is typically initialized in WinMain or DllMain.\n
* Platform Win
*/
extern HINSTANCE g_hFSInst;
#endif
/**
* Returns directory of the module. For Win32 DLLs, requires initialization of g_hFSInst, otherwize retruns path of the process.\n
* Mac SHLBs always return a path of process.\n
* Platform Win, Mac
* @return Directory, where module is located.
* @sa g_hFSInst
*/
CFSFileName FSGetModulePath();
/**
* Returns directory that can be used to store temporary files.
* @return Directory name for temp files.
*/
CFSFileName FSGetTempPath();

/**
* Converts file identifier to readable format. On Win and Unix, FileName already is in readable format,
* on Mac the readable form is calculated.
* @param[in] FileName File identifier.
* @return Readable form of the file name.
*/
CFSString FSFileNametoString(const CFSFileName &FileName);

/**
* CFSStream implementation for disk files.
*/
class CFSFile : public CFSStream
{
public:
	DECLARE_FSNOCOPY(CFSFile);

	CFSFile();
/**
* Initializes class and opens the file. See Open for parameters and error handling.
* @sa Open
*/
	CFSFile(const CFSFileName &FileName, const CFSString &szMode);

/**
* Initializes attaches it to the file handle. See Attach for parameters.
* @sa Attach
*/
	CFSFile(FILE *pFile, bool bCloseLater);

/**
* If file is open, file is automatically closed. All errors are ignored.
*/
	virtual ~CFSFile();

/**
* Opens the file.
* If another file is already open, it will be closed and close errors are ignored.\n
* Throws CFSFileException on error.
* @param[in] FileName File identifier.
* @param[in] szMode fopen-style character set of open mode flags.
*/
	void Open(const CFSFileName &FileName, const CFSString &szMode);

/**
* Closes the file if opened.\n
* Throws CFSFileException on error.
*/
	void Close();

/**
* Attaches to existing file.
* If another file is already open, it will be closed and close errors are ignored.
* @param[in] pFile pointer to existing FILE structure.
* @param[in] bCloseLater if true, file will be closed automatically by destructor or by Close() call.
*/
	void Attach(FILE *pFile, bool bCloseLater);

/**
* Detaches object from file.
* Object will be reset.
* @return Pointer to FILE that was used so far.
*/
	FILE *Detach();

#if defined (MAC)
/**
* Configures file to use Creator and Type arguments of the file on file creation. Must be set before call to Open function.
* @param[in] Creator ID of the creator.
* @param[in] Type ID of the file.
*/
	void UseCreatorType(OSType Creator, OSType Type)
	{
		m_Creator=Creator; m_Type=Type;
	}
#endif

	INTPTR ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);
	INTPTR WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);

	void Seek(INT64 lPos, int iType=SEEK_SET);
	INT64 Tell() const;
	bool IsEOF() const 
	{
		return feof(m_pFile)!=0;
	}

/**
* Provides raw access to file.
* @return Pointer to FILE to be used with f-functions, like fread/fwrite/etc.
*/
	operator FILE* ()
	{
		return m_pFile;
	}
protected:
	FILE *m_pFile;
	bool m_bClose;
#if defined (MAC)
	OSType m_Creator, m_Type;
#endif
};

/**
* Virtual file, that writes and reads data from RAM. Always open in read-write mode.
*/
class CFSMemFile : public CFSStream
{
public:
	CFSMemFile();
	virtual ~CFSMemFile();

	INTPTR ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);
	INTPTR WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);

	void Seek(INT64 lPos, int iType=SEEK_SET);
	INT64 Tell() const
	{
		return m_ipCursor;
	}
	bool IsEOF() const
	{
		return m_ipCursor>=m_Data.GetSize();
	}

/**
* Provides raw access to memory file data.
* @return Reference to the data.
*/
	const CFSData &GetData() const
	{
		return m_Data;
	}
protected:
	CFSData m_Data;
	INTPTR m_ipCursor;
};

///////////////////////////////////////////////////////////
// File Filters

/**
* XOR filter.
* Automatically scrambles saved and unscrambles read data by XORing it with given key.
*/
class CFSCryptedFile : public CFSStream 
{
public:
	CFSCryptedFile(const CFSAString &szCrypt);

/**
* Assigns a file which will be used for real I/O.
* @param[in] pFile File to use.
*/
	void SetDelegate(CFSStream *pFile) { m_pFile=pFile; }

	INTPTR ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);
	INTPTR WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);

	void Seek(INT64 lPos, int iType=SEEK_SET) { return m_pFile->Seek(lPos, iType); }
	INT64 Tell() const { return m_pFile->Tell(); }
	bool IsEOF() const { return m_pFile->IsEOF(); }

protected:
	void Codec(BYTE *pDest, const BYTE *pSrc, INTPTR ipSize, INT64 iFilePos);

	CFSStream *m_pFile;
	CFSAString m_szCrypt;
};

/**
* Huffman filter.
* Automatically compresses saved data using Huffman algorithm and decodes it on read.
* Allows only stream mode -- cursor position is undefined.
*/
class CFSHuffmanFile : public CFSStream
{
public:
	CFSHuffmanFile();

/**
* Assigns a file which will be used for real I/O.
* @param[in] pFile File to use.
*/
	void SetDelegate(CFSStream *pFile) { m_pFile=pFile; }

/**
* Builds Huffman tree from the statistical data.
* @param[in] pData Data calculate the tree from.
* @param[in] ipLength Length of data.
*/
	void BuildCodecData(const void *pData, INTPTR ipLength);

/**
* Reads Huffman tree from the delegated file.
*/
	void LoadCodecData();

/**
* Writes Huffman tree to the delegated file.
*/
	void SaveCodecData() const;

/**
* Resets byte cache used by the class. Contents of the cache will be destroyed.
*/
	void InitCache();

/**
* If there is some data in the byte cache, it will be filled with zero bits and written to output stream.\n
* Always use Flush in the end of the file or when you to start next write from clean byte.
*/
	void Flush();

	INTPTR ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);
	INTPTR WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError=true);

	void Seek(INT64 lPos, int iType=SEEK_SET) { FSUNUSED(lPos); FSUNUSED(iType); ASSERT(false); }
	INT64 Tell() const { ASSERT(false); return 0; }
	bool IsEOF() const { ASSERT(false); return false; }

protected:
	class CBuildNode;
	CBuildNode *GetBuildNode(CFSObjArray<CBuildNode> &Leaves, INTPTR &ipLeafCursor, CFSObjArray<CBuildNode> &Nodes, INTPTR &ipNodeCursor) const;
	void BuildBitLengths(const void *pData, INTPTR ipLength);
	BYTE GetBits(BYTE byCount, BYTE &byBits, BYTE &byLength) const;
	void BuildMaps();

	BYTE ReadBits(BYTE byCount);

	void CheckAndWrite();
	void WriteBits(BYTE byBits, BYTE byCount);
	void WriteZeroBits(BYTE byCount);

	CFSStream *m_pFile;
	BYTE m_byCache;
	BYTE m_byCacheLevel;

	BYTE m_BitLengths[256];
	BYTE m_Encoder[256];
	struct CDecoderNode {
		UINT16 m_uiChild[2];
		BYTE m_byByte;
	} m_Decoder[511];
	BYTE m_byDecoderBitLength;
};

#endif // _FSFILE_H_
