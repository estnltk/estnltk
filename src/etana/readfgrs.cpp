
#if defined(WIN32)
    #include <malloc.h>
    #include <io.h>
#endif
#if defined(UNIX)
    #include <unistd.h>
#endif
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>

#include "cxxbs3.h"

void DCTRD::readfgrs(void)
	{
	//int  res;
	unsigned size;

	/* l�pugruppide vormijadad */

	size = (unsigned)(file_info.suf - file_info.fgr); /* l�pugruppide vormijadade mass. pikkus */
	homo_form = size/gr_size;
    fgr = (char *)malloc(sizeof(char) * size); // see malloc on ok
	if (fgr==NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if(c_read(file_info.fgr, fgr, size) == false)
        {
        free(fgr);
        fgr=NULL;
        throw(VEAD(ERR_MORFI_PS6N,ERR_MINGIJAMA,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	}
