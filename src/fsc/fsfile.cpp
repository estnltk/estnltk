#include "stdfsc.h"
#include "fstype.h"

#include "fsfile.h"
#include "fssmartptr.h"
#include "fsstring2.h"

CFSString FSFileNametoString(const CFSFileName &FileName)
{
	return FileName;
}

#if defined (WIN32)
HINSTANCE g_hFSInst=0;
#endif
CFSFileName FSGetModulePath()
{
	CFSString szPath;
#if defined (WINRT)
	auto aFolder=Windows::ApplicationModel::Package::Current->InstalledLocation;
	szPath=aFolder->Path->Data();
	if (!szPath.IsEmpty() && !szPath.EndsWith(L"\\")) {
		szPath+=L"\\";
	}
	return szPath;
#elif defined (WIN32)
	GetModuleFileName(g_hFSInst, szPath.GetBuffer(_MAX_PATH+1), _MAX_PATH+1);
	szPath.ReleaseBuffer();
	INTPTR ipPos=szPath.ReverseFind(FSTSTR('\\'));
	if (ipPos!=-1) {
		szPath.Truncate(ipPos+1);
	}
	return szPath;
#elif defined (UNIX)
	return "";
#elif defined (MAC)
	ProcessSerialNumber thePSN;
	if (GetCurrentProcess(&thePSN)!=noErr) {
		return szPath;
	}
	FSRef Ref;
	if (GetProcessBundleLocation(&thePSN, &Ref)!=noErr) {
		return szPath;
	}
	FSRefMakePath(&Ref, (UInt8 *)szPath.GetBuffer(512), 512);
	szPath.ReleaseBuffer();
	INTPTR ipPos=szPath.ReverseFind(FSTSTR('/'));
	if (ipPos!=-1) {
		szPath.Truncate(ipPos+1);
	}
	return szPath;
#endif
}

CFSFileName FSGetTempPath()
{
#if defined (WINRT)
	auto aFolder=Windows::Storage::ApplicationData::Current->TemporaryFolder;
	CFSWString szPath=aFolder->Path->Data();
	if (!szPath.IsEmpty() && !szPath.EndsWith(L"\\")) {
		szPath+=L"\\";
	}
	return szPath;
#elif defined (WIN32)
	CFSString szPath;
	GetTempPath(_MAX_PATH+1, szPath.GetBuffer(_MAX_PATH+1));
	szPath.ReleaseBuffer();
	return szPath;
#elif defined (UNIX)
	return "/tmp/";
#elif defined (MAC)
	CFSString szPath;
	FSRef Ref;
	if (FSFindFolder(kOnSystemDisk, kTemporaryFolderType, true, &Ref)!=noErr) {
		return szPath;
	}
	FSRefMakePath(&Ref, (UInt8 *)szPath.GetBuffer(512), 512);
	szPath.ReleaseBuffer();
	if (!szPath.IsEmpty()) {
		szPath+='/';
	}
	return szPath;
#endif
}

//////////////////////////////////////////////////////////////////////
// Base File
//////////////////////////////////////////////////////////////////////

void CFSStream::ReadByte(BYTE *pByte)
{
	ReadBuf(pByte, 1);
}

void CFSStream::WriteByte(BYTE Byte)
{
	WriteBuf(&Byte, 1);
}

void CFSStream::ReadBool(bool *pBool)
{
	BYTE Byte;
	ReadByte(&Byte);
	*pBool=(Byte!=0);
}

void CFSStream::WriteBool(bool Bool)
{
	WriteByte(Bool ? 1 : 0);
}

void CFSStream::ReadChar(char *pChar)
{
	ReadByte((BYTE *)pChar);
}

void CFSStream::ReadChar(WCHAR *pChar)
{
	LCHAR lChar;
	ReadUInt(&lChar);
	if (lChar>=0x110000) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	if (!FSAssign(*pChar, lChar)) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
}

void CFSStream::WriteChar(char Char)
{
	WriteByte(Char);
}

void CFSStream::WriteChar(WCHAR Char)
{
	LCHAR lChar=Char;
	if (lChar>=0x110000) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	WriteUInt(lChar);
}

void CFSStream::ReadString(CFSAString *pszStr)
{
	INTPTR ipSize;
	ReadUInt((UINTPTR *)&ipSize);
	if (ipSize<0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	else if (ipSize==0) {
		pszStr->Empty();
	}
	else {
		ReadBuf(pszStr->GetBuffer(ipSize+1), ipSize);
		pszStr->ReleaseBuffer(ipSize);
	}
}

void CFSStream::ReadString(CFSWString *pszStr)
{
	CFSAString szAStr;
	ReadString(&szAStr);
	bool bError=false;
	*pszStr=FSStrAtoW(szAStr, FSCP_UTF8, &bError);
	if (bError) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
}

void CFSStream::WriteString(const CFSAString &szStr)
{
	WriteUInt((UINTPTR)szStr.GetLength());
	WriteBuf((const char *)szStr, szStr.GetLength());
}

void CFSStream::WriteString(const CFSWString &szStr)
{
	bool bError=false;
	CFSAString szAString=FSStrWtoA(szStr, FSCP_UTF8, &bError);
	if (bError) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	WriteString(szAString);
}

bool CFSStream::ReadTextChar(char *pChar)
{
	return (ReadBuf(pChar, 1, false)==1);
}

bool CFSStream::ReadTextChar(wchar_t *pChar)
{
	BYTE Buf[2];
	if (ReadBuf(Buf, 2, false)!=2) {
		return false;
	}
	*pChar=((UINT16)Buf[1])<<8 | Buf[0];
	return true;
}

bool CFSStream::ReadTextLine(CFSWString *pszStr)
{
	bool bResult=__ReadTextLine(pszStr, 2);
	if (FSStrCombineW2(*pszStr)!=0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	return bResult;
}

bool CFSStream::ReadTextUntil(CFSWString *pszStr, const CFSWString &szSymbols)
{
	bool bResult=__ReadTextUntil(pszStr, szSymbols);
	if (FSStrCombineW2(*pszStr)!=0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	return bResult;
}

void CFSStream::WriteText(const CFSAString &szStr)
{
	WriteBuf(szStr, szStr.GetLength());
}

void CFSStream::WriteText(const CFSWString &szStr)
{
	for (INTPTR ip=0; szStr[ip]; ip++){
		if ((LCHAR)szStr[ip]>=0x10000){
#if defined FSUTF16
			throw CFSFileException(CFSFileException::INVALIDDATA);
#endif
			WCHAR Char1, Char2;
			if (FSLtoW2(szStr[ip], &Char1, &Char2)!=0) {
				throw CFSFileException(CFSFileException::INVALIDDATA);
			}
			WriteUInt((UINT16)Char1, 2);
			WriteUInt((UINT16)Char1, 2);
		}
		else {
			WriteUInt((UINT16)szStr[ip], 2);
		}
	}
}

void CFSStream::Printf(const char *pszFormat, ...)
{
	va_list args;
	va_start(args, pszFormat);
	CFSAString szString;
	szString.FormatV(pszFormat, args);
	va_end(args);
	WriteText(szString);
}

void CFSStream::Printf(const WCHAR *pszFormat, ...)
{
	va_list args;
	va_start(args, pszFormat);
	CFSWString szString;
	szString.FormatV(pszFormat, args);
	va_end(args);
	WriteText(szString);
}

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CFSFile::CFSFile()
{
	m_pFile=0;
	m_bClose=true;
#if defined (MAC)
	m_Creator=m_Type=0;
#endif
}

CFSFile::CFSFile(const CFSFileName &FileName, const CFSString &szMode)
{
	m_pFile=0;
	m_bClose=true;
#if defined (MAC)
	m_Creator=m_Type=0;
#endif
	Open(FileName, szMode);
}

CFSFile::CFSFile(FILE *pFile, bool bCloseLater)
{
	m_pFile=0;
	m_bClose=true;
#if defined (MAC)
	m_Creator=m_Type=0;
#endif
	Attach(pFile, bCloseLater);
}

CFSFile::~CFSFile()
{
	IGNORE_FSEXCEPTION( Close(); )
}

void CFSFile::Open(const CFSFileName &FileName, const CFSString &szMode)
{
	IGNORE_FSEXCEPTION( Close(); )
	m_pFile=0;
	m_bClose=true;
#if defined (_DEBUG)
	if (szMode.Find('b')==-1) {
		TRACE(FSTSTR("WARNING: File will be opened in text mode\n"));
	}
#endif
#if defined (MAC)
	m_pFile=fopen(FileName, szMode);
	OSErr Err=noErr;
	if (m_pFile && szMode.FindOneOf("wa")>=0 && (m_Creator!=0 || m_Type!=0)) {
		FSRef Ref;
		Err=FSPathMakeRef((const UInt8 *)(const char *)FileName, &Ref, 0);
		FSCatalogInfo Info;
		FileInfo *pFileInfo=(FileInfo *)&Info.finderInfo;
		if (Err==noErr) {
			Err=FSGetCatalogInfo(&Ref, kFSCatInfoFinderInfo, &Info, NULL, NULL, NULL);
		}
		if (Err==noErr) {
			if (m_Creator!=0) pFileInfo->fileCreator=m_Creator;
			if (m_Type!=0) pFileInfo->fileType=m_Type;
			Err=FSSetCatalogInfo(&Ref, kFSCatInfoFinderInfo, &Info);
		}
	}
	if (Err!=noErr && m_pFile) {
		fclose(m_pFile);
		m_pFile=0;
	}
#elif defined (WIN32CE) || defined(UNIX)
	if (FileName.IsEmpty()) {
		throw CFSFileException(CFSFileException::OPEN);
	}
	#if defined (UNICODE)
	m_pFile=_wfopen(FileName, szMode);
	#else // !UNICODE
	m_pFile=fopen(FileName, szMode);
	#endif // UNICODE
#elif defined (WIN32)
	if (FileName.IsEmpty() || FileName.GetLength()>MAX_PATH-1) {
		throw CFSFileException(CFSFileException::OPEN);
	}
	int iShareFlag=_SH_DENYWR;
	if (szMode.FindOneOf(FSTSTR("aw+"))>=0) {
		iShareFlag=_SH_DENYRW;
	}
	#if defined (UNICODE)
	m_pFile=_wfsopen(FileName, szMode, iShareFlag);
	#else // !UNICODE
	m_pFile=_fsopen(FileName, szMode, iShareFlag);
	#endif // UNICODE
#endif
	if (!m_pFile) {
		throw CFSFileException(CFSFileException::OPEN);
	}
}

void CFSFile::Close()
{
	if (m_pFile){
		if (m_bClose) {
			if (fclose(m_pFile)!=0) {
				throw CFSFileException(CFSFileException::CLOSE);
			}
		}
		m_pFile=0;
	}
	m_bClose=true;
}

void CFSFile::Attach(FILE *pFile, bool bCloseLater)
{
	IGNORE_FSEXCEPTION( Close(); )
	m_pFile=pFile;
	m_bClose=bCloseLater;
}

FILE *CFSFile::Detach()
{
	FILE *pFile=m_pFile;
	m_pFile=0;
	m_bClose=true;
	return pFile;
}

INTPTR CFSFile::ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipRes=(INTPTR)fread(pBuf, 1, ipBytes, m_pFile);
	if (bExceptionOnError && ipRes!=ipBytes) {
		throw CFSFileException(CFSFileException::READ);
	}
	return ipRes;
}

INTPTR CFSFile::WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipRes=(INTPTR)fwrite(pBuf, 1, ipBytes, m_pFile);
	if (bExceptionOnError && ipRes!=ipBytes) {
		throw CFSFileException(CFSFileException::WRITE);
	}
	return ipRes;
}

void CFSFile::Seek(INT64 lPos, int lType)
{
	int iRes=-1;
#if defined (WIN32) && !defined (WIN32CE)
	iRes=_fseeki64(m_pFile, lPos, lType);
#else
	long lPos0;
	if (FSAssign(lPos0, lPos)) {
		iRes=fseek(m_pFile, lPos0, lType);
	}
#endif
	if (iRes!=0) {
		throw CFSFileException(CFSFileException::SEEK);
	}
}

INT64 CFSFile::Tell() const
{
#if defined (WIN32) && !defined (WIN32CE)
	return _ftelli64(m_pFile);
#else
	return ftell(m_pFile);
#endif
}

//////////////////////////////////////////////////////////////////////

CFSMemFile::CFSMemFile()
{
	m_ipCursor=0;
}

CFSMemFile::~CFSMemFile()
{
}

INTPTR CFSMemFile::ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipAvailable=m_Data.GetSize()-m_ipCursor;
	INTPTR ipCount=FSMIN(ipAvailable, ipBytes);
	memcpy(pBuf, (char *)m_Data.GetData()+m_ipCursor, ipCount);
	m_ipCursor+=ipCount;
	if (bExceptionOnError && ipCount!=ipBytes) {
		throw CFSFileException(CFSFileException::READ);
	}
	return ipCount;
}

INTPTR CFSMemFile::WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	FSUNUSED(bExceptionOnError);
	if (m_ipCursor+ipBytes>m_Data.GetSize()) {
		m_Data.SetSize(m_ipCursor+ipBytes);
	}
	memcpy((char *)m_Data.GetData()+m_ipCursor, pBuf, ipBytes);
	m_ipCursor+=ipBytes;
	return ipBytes;
}

void CFSMemFile::Seek(INT64 lPos, int lType)
{
	switch (lType){
		case SEEK_SET:
		break;
		case SEEK_CUR:
			lPos+=m_ipCursor;
		break;
		case SEEK_END:
			lPos+=m_Data.GetSize();
		break;
		default:
			ASSERT(false);
		break;
	}
	if (lPos<0 || lPos>m_Data.GetSize()) {
		throw CFSFileException(CFSFileException::SEEK);
	}
	m_ipCursor=(INTPTR)lPos;
}

//////////////////////////////////////////////////////////////////////

CFSCryptedFile::CFSCryptedFile(const CFSAString &szCrypt)
{
	m_pFile=0;
	m_szCrypt=szCrypt;
}

INTPTR CFSCryptedFile::ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipRes;
	INT64 iFilePos=Tell();
	if (ipBytes<=32) {
		BYTE Buf2[32];
		ipRes=m_pFile->ReadBuf(Buf2, ipBytes, bExceptionOnError);
		Codec((BYTE *)pBuf, Buf2, ipRes, iFilePos);
	}
	else{
		CFSSmartPtr<BYTE> pBuf2=new BYTE[ipBytes];
		ipRes=m_pFile->ReadBuf(pBuf2, ipBytes, bExceptionOnError);
		Codec((BYTE *)pBuf, pBuf2, ipRes, iFilePos);
	}
	return ipRes;
}

INTPTR CFSCryptedFile::WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	if (ipBytes<=32) {
		BYTE Buf2[32];
		Codec(Buf2, (const BYTE *)pBuf, ipBytes, Tell());
		return m_pFile->WriteBuf(Buf2, ipBytes, bExceptionOnError);
	}
	else{
		CFSSmartPtr<BYTE> pBuf2=new BYTE[ipBytes];
		Codec(pBuf2, (const BYTE *)pBuf, ipBytes, Tell());
		return m_pFile->WriteBuf(pBuf2, ipBytes, bExceptionOnError);
	}
}

void CFSCryptedFile::Codec(BYTE *pDest, const BYTE *pSrc, INTPTR ipSize, INT64 iFilePos)
{
	INTPTR ipCursor=(INTPTR)(iFilePos%m_szCrypt.GetLength());
	while (ipSize>0){
		pDest[0]=pSrc[0]^m_szCrypt[ipCursor];
		ipCursor=(ipCursor+1)%m_szCrypt.GetLength();
		pDest++; pSrc++; ipSize--;
	}
}

//////////////////////////////////////////////////////////////////////

static BYTE g_HuffmannBitFilter[]={0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff};

class CFSHuffmanFile::CBuildNode {
public:
	CBuildNode() { m_pParent=0; m_Byte=0; m_ipCount=0; }
	CBuildNode(BYTE Byte, INTPTR ipCount) { m_pParent=0; m_Byte=Byte; m_ipCount=ipCount; }

	CBuildNode *m_pParent;
	BYTE m_Byte;
	INTPTR m_ipCount;
};


CFSHuffmanFile::CFSHuffmanFile()
{
	m_pFile=0;
	memset(&m_BitLengths, 0, sizeof(m_BitLengths));
	memset(&m_Encoder, 0, sizeof(m_Encoder));
	memset(&m_Decoder, 0, sizeof(m_Decoder));
	m_byDecoderBitLength=0;
	InitCache();
}

CFSHuffmanFile::CBuildNode *CFSHuffmanFile::GetBuildNode(CFSObjArray<CFSHuffmanFile::CBuildNode> &Leaves, INTPTR &ipLeafCursor, CFSObjArray<CFSHuffmanFile::CBuildNode> &Nodes, INTPTR &ipNodeCursor) const
{
	if (ipLeafCursor>=Leaves.GetSize()) {
		return Nodes[ipNodeCursor++];
	}
	if (ipNodeCursor>=Nodes.GetSize()) {
		return Leaves[ipLeafCursor++];
	}
	if (Leaves[ipLeafCursor]->m_ipCount<=Nodes[ipNodeCursor]->m_ipCount) {
		return Leaves[ipLeafCursor++];
	}
	return Nodes[ipNodeCursor++];
}

void CFSHuffmanFile::BuildCodecData(const void *pData, INTPTR ipLength)
{
	BuildBitLengths(pData, ipLength);
	BuildMaps();
}

void CFSHuffmanFile::LoadCodecData()
{
	for (INTPTR ip=0; ip<256; ip++){
		m_pFile->ReadByte(&m_BitLengths[ip]);
	}
	BuildMaps();
}

void CFSHuffmanFile::SaveCodecData() const
{
	for (INTPTR ip=0; ip<256; ip++){
		m_pFile->WriteByte(m_BitLengths[ip]);
	}
}

void CFSHuffmanFile::BuildBitLengths(const void *pData, INTPTR ipLength)
{
	memset(&m_BitLengths, 0, sizeof(m_BitLengths));
	INTPTR ip;

	// Count appearances
	INTPTR Count[256];
	memset(&Count, 0, sizeof(Count));
	for (ip=0; ip<ipLength; ip++) {
		Count[((BYTE *)pData)[ip]]++;
	}

	// Build ordered leaves list
	CFSObjArray<CBuildNode> Leaves;
	for (ip=0; ip<256; ip++) {
		if (Count[ip]) {
			if (Leaves.GetSize()==0 || Count[ip]>=Leaves[Leaves.GetSize()-1]->m_ipCount){
				Leaves.AddItem(new CBuildNode((BYTE)ip, Count[ip]));
			}
			else{
				for (INTPTR ip2=0; ip2<Leaves.GetSize(); ip2++){
					if (Count[ip]<Leaves[ip2]->m_ipCount) {
						Leaves.InsertItem(ip2, new CBuildNode((BYTE)ip, Count[ip]));
						break;
					}
				}
			}
		}
	}

	if (Leaves.GetSize()==0) {
		return;
	}
	if (Leaves.GetSize()==1) {
		m_BitLengths[Leaves[0]->m_Byte]=1;
		return;
	}

	// Optimize tree
	CFSObjArray<CBuildNode> Nodes;
	INTPTR ipLeafCursor=0, ipNodeCursor=0;
	for (ip=0; ip<Leaves.GetSize()-1; ip++){
		CBuildNode *pNode1=GetBuildNode(Leaves, ipLeafCursor, Nodes, ipNodeCursor);
		CBuildNode *pNode2=GetBuildNode(Leaves, ipLeafCursor, Nodes, ipNodeCursor);
		CBuildNode *pNode=new CBuildNode(0, pNode1->m_ipCount+pNode2->m_ipCount);
		pNode1->m_pParent=pNode2->m_pParent=pNode;
		Nodes.AddItem(pNode);
	}

	// Count lengths
	for (ip=0; ip<Leaves.GetSize(); ip++){
		for (CBuildNode *pNode=Leaves[ip]; pNode->m_pParent!=0; pNode=pNode->m_pParent) {
			m_BitLengths[Leaves[ip]->m_Byte]++;
		}
	}
}

BYTE CFSHuffmanFile::GetBits(BYTE byCount, BYTE &byBits, BYTE &byLength) const
{
	ASSERT(byCount<=byLength && byCount<=8);
	BYTE byRet;
	if (byLength>=8+byCount) byRet=0;
	else byRet=((UINT16)byBits)>>(byLength-byCount);
	byLength-=byCount;
	if (byLength<8) byBits&=g_HuffmannBitFilter[byLength];
	return byRet;
}

void CFSHuffmanFile::BuildMaps()
{
	INTPTR ip;

	BYTE byMaxBitLength=0;
	m_byDecoderBitLength=255;
	memset(&m_Encoder, 0, sizeof(m_Encoder));
	memset(&m_Decoder, 0, sizeof(m_Decoder));

	for (ip=0; ip<256; ip++){
		if (m_BitLengths[ip]>0 && m_BitLengths[ip]<m_byDecoderBitLength) {
			m_byDecoderBitLength=m_BitLengths[ip];
		}
		if (m_BitLengths[ip]>byMaxBitLength) {
			byMaxBitLength=m_BitLengths[ip];
		}
	}
	if (m_byDecoderBitLength>byMaxBitLength){
		m_byDecoderBitLength=byMaxBitLength;
	}
	ASSERT(m_byDecoderBitLength<=8);
	if (m_byDecoderBitLength==0) return;

	UINT16 uiCursor=1<<m_byDecoderBitLength;
	BYTE byBits=0;
	for (BYTE byLength=byMaxBitLength; byLength>=m_byDecoderBitLength; byLength--) {
		for (ip=0; ip<256; ip++) {
			if (m_BitLengths[ip]==byLength) {
				m_Encoder[ip]=byBits;

				BYTE byBits2=byBits;
				BYTE byLength2=byLength;
				UINT16 uiPos=GetBits(m_byDecoderBitLength, byBits2, byLength2);
				while (byLength2){
					ASSERT(m_Decoder[uiPos].m_byByte==0);
					BYTE byTemp=GetBits(1, byBits2, byLength2);
					if (m_Decoder[uiPos].m_uiChild[byTemp]==0){
						m_Decoder[uiPos].m_uiChild[byTemp]=uiCursor++;
					}
					uiPos=m_Decoder[uiPos].m_uiChild[byTemp];
				}
				m_Decoder[uiPos].m_byByte=(BYTE)ip;
				byBits++;
			}
		}
		byBits>>=1;
	}
}

void CFSHuffmanFile::InitCache()
{
	m_byCache=0;
	m_byCacheLevel=0;
}

void CFSHuffmanFile::CheckAndWrite()
{
	if (m_byCacheLevel==8){
		m_pFile->WriteByte(m_byCache);
		InitCache();
	}
}
void CFSHuffmanFile::Flush()
{
	if (m_byCacheLevel) {
		m_byCache<<=(8-m_byCacheLevel);
		m_byCacheLevel=8;
		CheckAndWrite();
	}
}

void CFSHuffmanFile::WriteZeroBits(BYTE byCount)
{
	BYTE byFillByte=FSMIN((BYTE)(8-m_byCacheLevel), byCount);
	m_byCache<<=byFillByte;
	m_byCacheLevel+=byFillByte;
	CheckAndWrite();
	byCount-=byFillByte;
	while (byCount>=8){
		m_pFile->WriteByte(0);
		byCount-=8;
	}
	m_byCacheLevel+=byCount;
}

void CFSHuffmanFile::WriteBits(BYTE byBits, BYTE byCount)
{
	if (m_byCacheLevel+byCount<=8){
		m_byCache<<=byCount;
		m_byCache|=byBits;
		m_byCacheLevel+=byCount;
		CheckAndWrite();
	}
	else{
		BYTE byLeftOver=byCount-(8-m_byCacheLevel);
		m_byCache<<=(8-m_byCacheLevel);
		m_byCache|=byBits>>byLeftOver;
		m_byCacheLevel=8;
		CheckAndWrite();
		m_byCache=byBits&g_HuffmannBitFilter[byLeftOver];
		m_byCacheLevel=byLeftOver;
	}
}

INTPTR CFSHuffmanFile::WriteBuf(const void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipRes=0;
	const BYTE *pbBuf=(const BYTE *)pBuf;
	while (ipRes<ipBytes) {
		if (m_BitLengths[*pbBuf]==0) {
			throw CFSFileException(CFSFileException::INVALIDDATA);
		}
		if (m_BitLengths[*pbBuf]>8) {
			WriteZeroBits(m_BitLengths[*pbBuf]-8);
		}
		if (bExceptionOnError) {
			WriteBits(m_Encoder[*pbBuf], FSMIN(m_BitLengths[*pbBuf], (BYTE)8));
		}
		else {
			try {
				WriteBits(m_Encoder[*pbBuf], FSMIN(m_BitLengths[*pbBuf], (BYTE)8));
			} catch (...) {
				break;
			}
		}
		pbBuf++; ipRes++;
	}
	return ipRes;
}

BYTE CFSHuffmanFile::ReadBits(BYTE byCount)
{
	if (m_byCacheLevel==0){
		m_pFile->ReadByte(&m_byCache);
		m_byCacheLevel=8;
	}
	if (byCount<=m_byCacheLevel) {
		BYTE byRes=m_byCache>>(m_byCacheLevel-byCount);
		m_byCacheLevel-=byCount;
		m_byCache&=g_HuffmannBitFilter[m_byCacheLevel];
		return byRes;
	}
	else{
		BYTE byLeftOver=byCount-m_byCacheLevel;
		BYTE byRes=m_byCache<<byLeftOver;
		m_pFile->ReadByte(&m_byCache);
		byRes|=m_byCache>>(8-byLeftOver);
		m_byCacheLevel=8-byLeftOver;
		m_byCache&=g_HuffmannBitFilter[m_byCacheLevel];
		return byRes;
	}
}
INTPTR CFSHuffmanFile::ReadBuf(void *pBuf, INTPTR ipBytes, bool bExceptionOnError)
{
	INTPTR ipRes=0;
	if (m_byDecoderBitLength==0) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	try {
		BYTE *pbBuf=(BYTE *)pBuf;
		while (ipRes<ipBytes) {
			UINT16 uiPos=ReadBits(m_byDecoderBitLength);
			while (m_Decoder[uiPos].m_uiChild[0]) {
				uiPos=m_Decoder[uiPos].m_uiChild[ReadBits(1)];
			}
			pbBuf[ipRes++]=m_Decoder[uiPos].m_byByte;
		}
	} catch (...) {
		if (bExceptionOnError) throw;
	}
	return ipRes;
}

//////////////////////////////////////////////////////////////////////

