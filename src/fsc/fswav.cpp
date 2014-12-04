#include "stdfsc.h"
#include "fstype.h"

#include "fswav.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CFSWav::CFSWav()
{
	memset(&m_WaveFormat, 0, sizeof(m_WaveFormat));
}

CFSWav::~CFSWav()
{
}

void CFSWav::Cleanup(){
	memset(&m_WaveFormat, 0, sizeof(m_WaveFormat));
	m_Data.Cleanup();
}

CFSStream &operator<<(CFSStream &Stream, const CFSWav &Wav)
{
	if (!Wav.m_WaveFormat.wBitsPerSample) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}

	// Header
	Stream.WriteBuf("RIFF", 4);
	Stream.WriteUInt((UINTPTR)((Wav.m_Data.GetSize()+4+4) + (16+4+4) + 4), 4);
	Stream.WriteBuf("WAVE", 4);

	// Format
	Stream.WriteBuf("fmt ", 4);
	Stream.WriteUInt((ULONG)16, 4);
	Stream.WriteUInt(Wav.m_WaveFormat.wFormatTag, 2);
	Stream.WriteUInt(Wav.m_WaveFormat.nChannels, 2);
	Stream.WriteUInt(Wav.m_WaveFormat.nSamplesPerSec, 4);
	Stream.WriteUInt(Wav.m_WaveFormat.nAvgBytesPerSec, 4);
	Stream.WriteUInt(Wav.m_WaveFormat.nBlockAlign, 2);
	Stream.WriteUInt(Wav.m_WaveFormat.wBitsPerSample, 2);

	// Data
	Stream.WriteBuf("data", 4);
	Stream.WriteUInt((UINTPTR)Wav.m_Data.GetSize(), 4);
	Stream.WriteBuf(Wav.m_Data.GetData(), Wav.m_Data.GetSize());

	return Stream;
}

CFSStream &operator>>(CFSStream &Stream, CFSWav &Wav)
{
	Wav.Cleanup();

	UINT32 lFileSize;
	UINT32 lChunkSize;
	BYTE Buf4[4];
	// Header
	Stream.ReadBuf(Buf4, 4);
	if (memcmp(Buf4, "RIFF", 4)) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	Stream.ReadUInt(&lFileSize, 4);
	Stream.ReadBuf(Buf4, 4);
	if (memcmp(Buf4, "WAVE", 4)) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}

	// Format
	Stream.ReadBuf(Buf4, 4);
	if (memcmp(Buf4, "fmt ", 4)) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	Stream.ReadUInt(&lChunkSize, 4);
	if (lChunkSize!=16) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	Stream.ReadUInt(&Wav.m_WaveFormat.wFormatTag, 2);
	Stream.ReadUInt(&Wav.m_WaveFormat.nChannels, 2);
	Stream.ReadUInt(&Wav.m_WaveFormat.nSamplesPerSec, 4);
	Stream.ReadUInt(&Wav.m_WaveFormat.nAvgBytesPerSec, 4);
	Stream.ReadUInt(&Wav.m_WaveFormat.nBlockAlign, 2);
	Stream.ReadUInt(&Wav.m_WaveFormat.wBitsPerSample, 2);

	// Data
	Stream.ReadBuf(Buf4, 4);
	if (memcmp(Buf4, "data", 4)) {
		throw CFSFileException(CFSFileException::INVALIDDATA);
	}
	Stream.ReadUInt(&lChunkSize, 4);

	Wav.m_Data.SetSize(lChunkSize);
	Stream.ReadBuf(Wav.m_Data.GetData(), Wav.m_Data.GetSize());

	return Stream;
}
