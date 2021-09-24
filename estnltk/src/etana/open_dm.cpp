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
/*
* teeb k6ik ettevalmistused use_d() kasutamiseks
*/

#include <string.h>
#include <stdlib.h>

#include "cxxbs3.h"

void DCTRD::NulliViidad(void)
    {
    groups=NULL;
    gr=NULL;
    fgr=NULL;
    sufix=NULL;
    prfix=NULL;
    ps.kTabel=NULL;
    ps.v6tmed=NULL;
    tmpCharPtr=NULL;
    }

void DCTRD::VabastaViidad(void)
    {
//    int i;

    if(groups) free(groups);    //readgrs()
    if(gr) free(gr);            //readgrs()
    if(fgr) free(fgr);          //readfgrs()
    if(sufix) free(sufix);      //readsuf()
    if(prfix) free(prfix);      //readprf()
    if(ps.kTabel) free(ps.kTabel);  //cXXread()
    if(ps.v6tmed) free(ps.v6tmed);  //cXXread()
    //if(tmpCharPtr) free(tmpCharPtr);
    NulliViidad();
    }

void DCTRD::Open(
    const CFSFileName *pSon)
	{ 
	open_d1(pSon);
	open_d2();
	if (TyvedSisse( this ) == false) // pl�morfism, tegelikult &cFILEINFO
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if (sonaliik.Start( this ) == false) // pl�morfism, tegelikult &cFILEINFO
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if (CacheOpen(
            file_info.buf_size, // k�shis t�kkide suurus
            -1                  // t�kkide arv k�shis
            ) != ALL_RIGHT)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	}

