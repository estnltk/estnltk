
#include "f-info.h"

void cFILEINFO::ReadFileInfo(const CFSFileName *pDctName)
    {
	int i;
    if(ReadMeta(pDctName)==false)
        {
        throw(VEAD(ERR_MORFI_PS6N, ERR_OPN, __FILE__, __LINE__, "$Revision: 521 $"));
        }
    if(Seek2(XFI_SPL)==false)
        {
        throw(VEAD(ERR_MORFI_PS6N, ERR_RD, __FILE__, __LINE__, "$Revision: 521 $"));
        }
    if(
       dctFile.ReadUnsigned<UB4,long>( &(file_info.bt_offset))==false
       || dctFile.ReadUnsigned<UB4,long>( &(file_info.sa_offset))==false
       || dctFile.ReadUnsigned<UB4,long>( &(file_info.tyveL6ppudeAlgus))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.piiriKr6nksud))==false

       || dctFile.ReadUnsigned<UB4,int>( &(file_info.VersionMS))==false 
	   || dctFile.ReadUnsigned<UB4,int>( &(file_info.VersionLS))==false
	   || dctFile.ReadUnsigned<UB2,int>( &(file_info.buf_size ))==false

	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.tyveKr6nksud))==false

       || dctFile.ReadUnsigned<UB4,long>( &(file_info.ends     ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.groups   ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.gr       ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.forms    ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.fgr      ))==false

       || dctFile.ReadUnsigned<UB4,long>( &(file_info.suf      ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.sufix    ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.vaba1    ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.vaba2    ))==false

       || dctFile.ReadUnsigned<UB4,long>( &(file_info.pref     ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.prfix    ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.taandsl  ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.tyvelp   ))==false
	   || dctFile.ReadUnsigned<UB4,long>( &(file_info.sonaliik ))==false )
	       {
           throw(VEAD(ERR_MORFI_PS6N, ERR_RD, __FILE__, __LINE__, "$Revision: 521 $"));
	       }
	for(i=0; i < LOENDEID; i++) 
		{
		if(dctFile.ReadUnsigned<UB4,long>( &(file_info.loend[i]) )==false)
            {
            throw(VEAD(ERR_MORFI_PS6N, ERR_RD, __FILE__, __LINE__, "$Revision: 521 $"));
            }
		}
    assert( ClassInvariant() );
	}

bool cFILEINFO::c_read( // ==0:ok; ==-1:jama
	const long offset,
	void *pBuffer,
	const int len)
	{
    if(dctFile.Seek(offset)==false)
        return false;
    if(dctFile.ReadBuffer(pBuffer,len)==false)
        return false;
	return true;
	}
