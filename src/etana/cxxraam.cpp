
#include <stdlib.h>
#include <stdio.h>

#include "cxxbs3.h"
//#include "lib_chrconv/tv_db.h"

bool cTYVEDETABEL::TyvedSisse(
    cFILEINFO *cFileInfo)
	{
	int i;
    const FILE_INFO *file_info=&(cFileInfo->file_info);
	const unsigned char* tmp2;
    //
    // kahendtabel
    //
	ps.ktSuurus = (int)(file_info->sa_offset - file_info->bt_offset); // kahendtabeli pikkus baitides kettal
    
    assert( (ps.ktSuurus % 3)==0 );
    
    if((tmp1=(unsigned char *)malloc(ps.ktSuurus))==NULL) // see malloc() on ok
        return false;
	if(cFileInfo->c_read(file_info->bt_offset, tmp1, ps.ktSuurus) == false)
		{
        free(tmp1); tmp1=NULL;
		return false;
		}
    ps.ktSuurus /= 3; // elementide arv 2ndtabelis
    ps.kTabel = ((TABLE *)malloc(ps.ktSuurus*(sizeof(TABLE)))); // see malloc on ok
    if(ps.kTabel==NULL)
		{
        free(tmp1); tmp1=NULL;
		return false;
		}
    tmp2=tmp1;

    for(i=0; i < ps.ktSuurus; i++)
        {
        STRSOUP::ReadUnsignedFromString<UB1,int>(tmp2,&(ps.kTabel[i].len));
        assert( ps.kTabel[i].len <= 0xFF );
        tmp2++;
        STRSOUP::ReadUnsignedFromString<UB2,int>(tmp2, &(ps.kTabel[i].s_nihe)); 
        assert( ps.kTabel[i].s_nihe <= 0xFFFF );
        tmp2 += 2;
        }
    assert( tmp1+(ps.ktSuurus*3) == tmp2 );
    free(tmp1); tmp1=NULL;
    //
	// tyved
    //
	//ps.vbSuurus = (unsigned)(file_info->tyveL6ppudeAlgus - file_info->sa_offset)/
    //                                                             dctsizeofFSxCHAR;
    //assert( (ps.vbSuurus % 2)==0 );
	ps.vbSuurus = (unsigned)(file_info->tyveL6ppudeAlgus - file_info->sa_offset);
    assert( (ps.vbSuurus % dctsizeofFSxCHAR)==0 );
    ps.vbSuurus /= dctsizeofFSxCHAR;

//printf("%s:%d -- vbSuurus=%5d\n", __FILE__,__LINE__,ps.vbSuurus);
    ps.v6tmed = ((FSxCHAR *)malloc(ps.vbSuurus*sizeof(FSxCHAR))); // see malloc on ok
    if(ps.v6tmed==NULL)
		{
		return false;
		}
	if(cFileInfo->dctFile.Seek(file_info->sa_offset)==false)// lugemisj�rg paika
        {
		return false;
		}
    for(unsigned ui=0; ui < ps.vbSuurus; ui++)
        {
        if(cFileInfo->dctFile.ReadChar(ps.v6tmed+ui)==false)
            return false;
        assert( ps.v6tmed[ui] <= 0xFFFF );
        }
	if(cFileInfo->dctFile.Seek(0L)==false)// lugemisj@rg faili algusesse
        {
		return false;
		}
#if defined DB_2TABEL
	{
	int k;
	for(k=0; k < 20; k++)
		dbPrint(S6naAlgus((&ps), k), ps.kTabel[k].len);
	}
#endif
	return true;
	}



