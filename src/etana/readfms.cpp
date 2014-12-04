
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

void DCTRD::readfms(void)
	{
	unsigned size;
    FSxCHAR *formings;
	// vormide tabel

	size = (unsigned)(file_info.fgr - file_info.forms); // vormide mass. pikkus
    formings = (FSxCHAR *) malloc(sizeof(char) * size); // see malloc on OK
	if(formings==NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if(c_read(file_info.forms, formings, size) == false)
        {
        free(formings);
        formings=NULL;
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
    assert( (size%sizeof(FSxCHAR)) == 0 );
    // pistame need loendiklassi sisse
    vormideLoend.Start(FSxvrdle, size, formings);
	}

