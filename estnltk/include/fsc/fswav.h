/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
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
