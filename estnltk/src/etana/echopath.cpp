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
// 2003.01.03 stringiklassile �mbertehtud

#include <stdlib.h> //sealt windoosas v�lismuutujad environ ja wenviron
//#if defined(__GNUC__)
//    #include <unistd.h> //sealt linuxis v�lismuutuja environ
//#endif
#include "post-fsc.h"

bool Which(			// ==false:polnud; ==true:leidsin,vt muutujat pathName
    CFSString *dctPathStr,	// leitud pathname 
    const CFSString *path,  // sellest proovime katalooge
    const CFSString *file)  // seda otsime
    {
    assert(dctPathStr != NULL);
    assert(path != NULL);
    assert(file != NULL);
    CFSFileName cfsFileName;

	CFSString tmpStr;
    CFSString tmpPath;
    int left,right;

    #if defined(WIN32)					// Vindoosas
        const FSTCHAR *eraldajaPath = FSTSTR(";");
        const FSTCHAR *eraldajaDir  = FSTSTR("\\");
    #else                               // UNIXis 
        const FSTCHAR *eraldajaPath = FSTSTR(":");
        const FSTCHAR *eraldajaDir  = FSTSTR("/");
    #endif

	if(file->Find(eraldajaDir)>=0) // oligi juba pathname
		{
        CPFSFile accessTst; // destruktor sulgeb ise faili
        cfsFileName=(const FSTCHAR *)(*file);
        if(accessTst.Open(cfsFileName, FSTSTR("rb"))==true)
            {
            (*dctPathStr)=(const FSTCHAR *)(*file);
		    return true; 
            }
        return false;
		}
#if defined(SELLEST_LOOBUTUD_080711)
#if defined(WIN32) // otsime proge kataloogist ka
#if defined(UNICODE)
	tmpStr = (const FSTCHAR *) _wpgmptr;
#else
	tmpStr = (const FSTCHAR *) _pgmptr;
#endif
    int lastSlash;
    if((lastSlash=(int)tmpStr.ReverseFind(eraldajaDir[0]))<0)
	    tmpStr = FSTSTR("");
    else
	    tmpStr = tmpStr.Left(lastSlash+1);
    tmpStr += (*file);
    CPFSFile accessTst; // destruktor sulgeb ise faili
    cfsFileName= (const FSTCHAR *)tmpStr;
    if(accessTst.Open(cfsFileName, FSTSTR("rb"))==true)
        {
        (*dctPathStr)=tmpStr;
	    return true; 
        }
#endif
#endif
    tmpPath  = (*path);
    tmpPath += eraldajaPath;
    for(left=0;(right=(int)tmpPath.Find(eraldajaPath[0], left)) >= 0; left=right+1)
        {
        if(left < right)
            {
            tmpStr=tmpPath.Mid(left, right-left);
            tmpStr += eraldajaDir;
            tmpStr += (*file);
            CPFSFile accessTst; // destruktor sulgeb ise faili
            cfsFileName= (const FSTCHAR *)tmpStr;
            if(accessTst.Open(cfsFileName, FSTSTR("rb"))==true)
                {
                (*dctPathStr)=tmpStr;
	            return true; 
                }
            }
        }
    return false;
    }

