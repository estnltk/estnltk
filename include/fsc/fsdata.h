#if !defined _FSDATA_H_
#define _FSDATA_H_

#include "fsstream.h"

/**
* Class to store and manipulate any binary data block.
*/
class CFSData  
{
public:
	CFSData();
	CFSData(const CFSData &Data);
#if defined (__FSCXX0X)
	CFSData(CFSData &&Data);
#endif
	virtual ~CFSData();

	CFSData &operator =(const CFSData &Data);
#if defined (__FSCXX0X)
	CFSData &operator =(CFSData &&Data);
#endif
	CFSData &operator +=(const CFSData &Data) { 
		Append(Data);
		return *this;
	}

/**
* Provides access to raw data.
* @return Pointer to raw data.
*/
	const void *GetData() const { 
		return m_pData; 
	}
	void *GetData() { 
		return m_pData; 
	}

/**
* Returns size of the data in bytes.
* @return Size of the data.
*/
	INTPTR GetSize() const { 
		return m_ipSize; 
	}

	void Reserve(INTPTR ipSize);

/**
* Resizes the data buffer.
* @param[in] ipSize New size of the buffer.
*/
	void SetSize(INTPTR ipSize, bool bReserveMore=true);

/**
* Compacts data and releases all unused resources.
*/
	void FreeExtra();

/**
* Releases all data and reinitializes class.
*/
	void Cleanup();

/**
* Appends data to the buffer.
* @param[in] pData Data to be appended.
* @param[in] ipSize Data size in bytes.
*/
	void Append(const void *pData, INTPTR ipSize);
/**
* Appends data to the buffer.
* @param[in] Data Data to be appended.
*/
	void Append(const CFSData &Data) { 
		Append(Data.GetData(), Data.GetSize()); 
	}

	friend CFSStream &operator<<(CFSStream &Stream, const CFSData &Data);
	friend CFSStream &operator>>(CFSStream &Stream, CFSData &Data);

protected:
	void *m_pData;
	INTPTR m_ipSize;
	INTPTR m_ipBufferSize;
};

#endif // _FSDATA_H_
