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
// 2000.07.14 TV 

#include <string.h>
#include <stdlib.h>
#include "cxxbs3.h"

void DCTRD::readeel(void)
	{
    if(taandliik.Start(this, file_info.taandsl, 
            file_info.tyvelp-file_info.taandsl, TAANDL_MAX_PIK+1)==false)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	// tyvelopud 

    if(tyvelp.Start(this, file_info.tyvelp, 
            file_info.sonaliik - file_info.tyvelp,TYVELP_MAX_PIK+1)==false)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	}
