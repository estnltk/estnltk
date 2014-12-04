
#include <fcntl.h>
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


#include "cxxbs3.h"

void DCTRD::readends(void)
	{
	unsigned size;
    FSxCHAR *endings;

	// l�ppude tabel

	size = (unsigned)(file_info.groups - file_info.ends);  // l�ppude mass. pikkuse
    endings = (FSxCHAR *) malloc(sizeof(char) * size); // see malloc on OK
	if (endings==NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.ends, endings, size) == false) // ok, sealt ei tule throw()-d
        {
        free(endings);
        endings=NULL;
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    // pistame need loendiklassi sisse
    l6ppudeLoend.Start(FSxvrdle, size, endings);
	}

