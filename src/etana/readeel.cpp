
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
