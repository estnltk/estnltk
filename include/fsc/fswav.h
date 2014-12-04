#if !defined _FSWAV_H_
#define _FSWAV_H_

#include "fsstream.h"
#include "fsdata.h"

#if defined (UNIX) || defined (MAC) || defined (WINRT) // WAVEFORMATEX is defined for WIN32

typedef struct tWAVEFORMATEX
{
	UINT16	wFormatTag;
	UINT16	nChannels;
	UINT32	nSamplesPerSec;
	UINT32	nAvgBytesPerSec;
	UINT16	nBlockAlign;
	UINT16	wBitsPerSample;
	UINT16	cbSize;
} WAVEFORMATEX;

#endif

/**
* Simple suport for uncompressed audio data.
*/
class CFSWav
{
public:
	CFSWav();
	virtual ~CFSWav();

/**
* Frees memory and reinitializes class.
*/
	void Cleanup();

/**
* Provides raw access to sound data.
* @return Raw data
*/
	CFSData &Data() {
		return m_Data;
	}

/**
* Gets wav information.
* @return Wave format information.
*/
	const WAVEFORMATEX &GetWaveFormat() const {
		return m_WaveFormat;
	}

/**
* Sets wav information.
* @param[in] WaveFormat Wave format to use.
*/
	void SetWaveFormat(const WAVEFORMATEX &WaveFormat) {
		m_WaveFormat=WaveFormat;
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSWav &Wav);
	friend CFSStream &operator>>(CFSStream &Stream, CFSWav &Wav);

protected:
	WAVEFORMATEX m_WaveFormat;
	CFSData m_Data;
};

#endif // _FSWAV_H_
