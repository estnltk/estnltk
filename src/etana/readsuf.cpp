

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
//#include <sonatk.h>

void DCTRD::readsuf(void)
	{
    int i, j;
	unsigned size;
    KETTA_SUFINFO* ketta_sufix;	     //* suf. seot. info kettal
    FSxCHAR* suffixes;

	//* sufiksite massiiv 

	size = (unsigned)(file_info.sufix - file_info.suf);  //suf mass. pikkus
    suffixes = (FSxCHAR *) malloc(sizeof(char) * size);  // see malloc on OK
	if (suffixes == NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if(c_read(file_info.suf, suffixes, size) == false)
        {
        free(suffixes);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
    // pistame need loendiklassi sisse. sufiksiteLoend'i asi on free(suffixes)
    sufiksiteLoend.Start(FSxvrdle, size, suffixes);

    // suf seot. info 
	size = (unsigned)(file_info.pref - file_info.sufix);  // suf. infot sisald. mass. pikkus 
    if (sizeof(KETTA_SUFINFO) * sufiksiteLoend.len != size) // ei saa olla 
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_MINGIJAMA,__FILE__,__LINE__, "$Revision: 521 $"));
        }
    ketta_sufix=(KETTA_SUFINFO*)malloc(sizeof(KETTA_SUFINFO)*sufiksiteLoend.len); // see malloc on ok
	if (ketta_sufix == NULL)
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_NOMEM,__FILE__,__LINE__, "$Revision: 521 $"));
        }
	if(c_read(file_info.sufix, ketta_sufix, size) == false)
        {
        free(ketta_sufix);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
    sufix = (SUFINFO *) malloc(sizeof(SUFINFO) * sufiksiteLoend.len); // see malloc on ok
	if (sufix == NULL)
        {
        free(ketta_sufix);
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
        }
    for (i=0; i < sufiksiteLoend.len; i++) //* kopeeri sufiksiga seotud info paremale kujule
        {
        sufix[i].taandlp = ketta_sufix[i].taandlp;
        sufix[i].tsl = ketta_sufix[i].tsl;
        sufix[i].tylp = ketta_sufix[i].tylp;
        sufix[i].mitutht = ketta_sufix[i].mitutht;
        //assert( ketta_sufix[i].ssl1==0 ); // JAMA-JAMA
        if(ketta_sufix[i].ssl1!=0)
            {
            free(ketta_sufix);
            free(sufix);
            sufix=NULL;
            throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
            }
        sufix[i].ssl = (ketta_sufix[i].ssl0 & 0xFF) | ((ketta_sufix[i].ssl1 & 0xFF)<<8);
        for (j=0; j < SUF_LGCNT; j++)
            char2sufinfo(&(ketta_sufix[i].suftyinf[j]), &(sufix[i].suftyinf[j]));
        }
    free(ketta_sufix);
	}

//* 
//* sufinfo char-kujult TYVE_INF kujule 
//*
void DCTRD::char2sufinfo(SUF_TYVE_INF *ch, TYVE_INF *ti)
    {
    ti->piiriKr6nksud = (ch->piiriKr6nksud0 & 0xFF) | ((ch->piiriKr6nksud1 & 0xFF)<<8);
    ti->lisaKr6nksud = (ch->lisaKr6nksud0 & 0xFF) | ((ch->lisaKr6nksud1 & 0xFF)<<8);
    ti->idx.tab_idx = (ch->tab_idx0 & 0xFF) | ((ch->tab_idx1 & 0xFF)<<8);
    ti->idx.blk_idx=ch->blk_idx;
    }



