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

void DCTRD::readgrs(void)
	{
	//register int   res;
	unsigned size;

	// l�pugrupid

	size = (unsigned)(file_info.gr - file_info.groups);  // l�pugruppide mass. pikkus
    groups = (GRUPP *) malloc(sizeof(char) * size); // see malloc on OK
	if (groups == NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.groups, groups, size) == false)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }

	// l�pugruppide l�pujadad
	gr_size = (unsigned)(file_info.forms - file_info.gr); // l�pugruppide l�pujadade mass. pikkus
    gr = (char *) malloc(sizeof(char) * gr_size); // see malloc on OK
	if (gr == NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.gr, gr, gr_size) == false)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_MINGIJAMA,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	}
