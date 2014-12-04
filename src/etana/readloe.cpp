
#if defined(WIN32)
    #include <malloc.h>
    #include <io.h>
#endif
#if defined(UNIX)
    #include <unistd.h>
#endif
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

#include "cxxbs3.h"
#include "sonatk.h"

void DCTRD::readloe(int i)
	{
    unsigned size;
    FSxCHAR* tmpPtr;

	size = (unsigned)(file_info.loend[i+1] - file_info.loend[i]);  //loendi mass. pikkus
	if (size == 0L) // loendit polegi 
		{
		return;
		}
    tmpPtr=(FSxCHAR *)(malloc(size)); // see malloc on OK
    if(tmpPtr==NULL) // reserveerime loendile m�lu
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.loend[i], tmpPtr, size) == false) // t�mbame loendi sisse
        {
        free(tmpPtr);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    // dctLoend[i] asi on free(tmpPtr)
    dctLoend[i].Start(FSxvrdle, size, tmpPtr);
	}

HJK_LOEND::HJK_LOEND(void)
    {
    xstrArr=NULL;
    }

void HJK_LOEND::Start(
    const CMPFUNBS  _cmpbs_,    // v�rdleb(v�ti,  kirje)
    const int _len_,            // _ptr_==NULL: _xstrArr_ pikkus; _ptr_!=NULL: _ptr_massiivi pikkus BAITIDES
    FSxCHAR *_xstrArr_,
    FSxCHAR **_ptr_)            // massiivi viit
    {
    int len;
    assert(xstrArr==NULL);
    if(_ptr_==NULL)
        {
        int i, pos, strCnt;
        const unsigned char *tmp2=(unsigned char *)_xstrArr_;
        assert( (_len_%dctsizeofFSxCHAR) == 0 );
        len = _len_ / dctsizeofFSxCHAR;
        // _ptr_ massiivi pikkus ja sisu tuleb v�lja arvutada
        if((xstrArr=(FSxCHAR *)malloc(len*sizeof(FSxCHAR)))==NULL) // see malloc on ok
            {
            free(_xstrArr_); // seda pole enam vaja, tuleb vabastada
            throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
            }
        //xstrArr=tmp4;
        // teisendame baidij�rje&pikkuse
        for(pos=i=0; i < len; pos+=2,i++)
            {
            xstrArr[i]=(FSxCHAR)((tmp2[pos]|((tmp2[pos+1])<<8))&0xFFFF);
            }
        free(_xstrArr_); // seda pole enam vaja, tuleb vabastada
        // arvutame v�lja stringide arvu
	    for (pos=strCnt=0; pos < len; strCnt++) 
		    {
		    pos += FSxSTRLEN( xstrArr + pos )+1;
		    assert( pos <= len );
		    }
        // reserveerime l�puviitade massiivi
        if((_ptr_=(FSxCHAR **)malloc(sizeof(FSxCHAR *)*strCnt))==NULL) // see malloc on ok
            {
            free(xstrArr);
            xstrArr=NULL;
            throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
		    }
        // kirjutame l�puviitade massiivi viidad sisse
	    for (pos=strCnt=0; pos < len; strCnt++)
		    {
            _ptr_[strCnt] = xstrArr + pos;
		    pos += FSxSTRLEN( xstrArr + pos )+1;
		    assert( pos <= _len_ );
		    }
        LOEND<FSxCHAR *,FSxCHAR *>::Start(_ptr_, strCnt, NULL, _cmpbs_, false);
        }
    else
        {
        // pistame need loendiklassi sisse
        assert( (_len_%sizeof(FSxCHAR)) == 0 );
        len = _len_ / sizeof(FSxCHAR);
        LOEND<FSxCHAR*,FSxCHAR*>::Start(_ptr_, _len_, NULL, _cmpbs_, false);
        }
    }
        
 HJK_LOEND::~HJK_LOEND(void)
    {
    if(xstrArr)
        free(xstrArr);
     }



