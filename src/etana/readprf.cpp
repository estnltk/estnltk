
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

void DCTRD::readprf(void)
	{
	unsigned size;
    int i;
    KETTA_PREFINFO* ketta_prfix;	     /* suf. seot. info kettal*/
    FSxCHAR* prffixes;

	/* prefiksite massiiv */

	size = (unsigned)(file_info.prfix - file_info.pref); // pref mass. pikkus
    prffixes = (FSxCHAR *) malloc(sizeof(char) * size);  // see malloc on ok
	if (prffixes==NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.pref, prffixes, size) == false)
        {
        free(prffixes);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    assert((size%dctsizeofFSxCHAR)==0);
    prefiksiteLoend.Start(FSxvrdle, size, prffixes); // prefiksiteLoend'i asi on free(prffixes)

	// pref seot. info

	size = (unsigned)(file_info.taandsl - file_info.prfix);     // pref. infot sisald. mass. pikkus
    if (sizeof(KETTA_PREFINFO) * prefiksiteLoend.len != size)   // ei saa olla
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_MINGIJAMA,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    ketta_prfix = (KETTA_PREFINFO*)malloc(sizeof(KETTA_PREFINFO)*prefiksiteLoend.len); // see malloc on OK
	if (ketta_prfix==NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
	if(c_read(file_info.prfix, ketta_prfix, size) == false)
        {
        free(ketta_prfix);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    prfix = (PREFINFO *) malloc(sizeof(PREFINFO) * prefiksiteLoend.len); // see malloc on ok
	if (prfix == NULL)
        {
        free(ketta_prfix);
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 521 $"));
        }
    for (i=0; i < prefiksiteLoend.len; i++) /* kopeeri prefiksiga seotud info paremale kujule*/
        {
        prfix[i].sl = ketta_prfix[i].sl;
        prfix[i].piiriKr6nksud = (ketta_prfix[i].piiriKr6nksud0 & 0xFF) | ((ketta_prfix[i].piiriKr6nksud1 & 0xFF)<<8);
        prfix[i].lisaKr6nksud = (ketta_prfix[i].lisaKr6nksud0 & 0xFF) | ((ketta_prfix[i].lisaKr6nksud1 & 0xFF)<<8);
        }
    free(ketta_prfix);
	}
