
/*  NB! seda faili kasutab ka "init3.exe"!!!
* 2-otsimised op-ma'lus
*/

#include <string.h>
#include <stdlib.h>

#include "cxxbs3.h"

/*
 * bsearch()-i vrdlusfunkts.;
 * key ja *elem on viidad v6tmele ja elem-le, mida TEGELIKULT v6rreldakse
 */
    int vrdle(const void *key, const void *elem)
        {
        return( strcmp((const char*)key, *(const char **)elem ) );
        }
    //* bsearch()-i v�rdlusfunkts.;
    int vordle(const void *key, const void *elem)
        {
        return( strcmp( (const char *)key, (const char *)elem ) );
        }

//    }
extern "C" // m�ned v�rdlusfunktsioonid
    {
    // ==0: kui v�ti == kirje v�ti
    //
    int FSxvrdle(const void *ee1, const void *ee2 )// vajalik 2ndotsimiseks
        {
        const FSxCHAR *e1=(const FSxCHAR *)ee1; 
        const FSxCHAR **e2=(const FSxCHAR **)ee2;
        return FSStrCmpW0( e1, *e2);
        }
    }

/*
* l�ppude, prefiksite ja sufiksite jrk. nr-te m��ramiste jaoks
*/
/** leiab lopu jrk nr loppude tabelis endings[];
* kasutades viitade massiivi ends[]
*/
char DCTRD::lpnr( const FSxCHAR *lp ) const
    {
    return l6ppudeLoend[(FSxCHAR *)lp]; // (FSxCHAR *)(const FSxCHAR *)
    }

/** leiab vormi jrk nr vormide tabelis formings[];
* kasutades viitade massiivi forms[]
*/
int DCTRD::vormnr( const FSxCHAR *lp ) const
    {
    return vormideLoend[(FSxCHAR *)lp]; // (FSxCHAR *)(const FSxCHAR *)
    }


/** leiab sufiksi jrk nr sufiksite tabelis suffixes[];
* kasutades viitade massiivi sufs[]
*/
int DCTRD::suffnr( const FSxCHAR *suf ) const 
    {
    return sufiksiteLoend[(FSxCHAR *)suf]; // (FSxCHAR *)(const FSxCHAR *)
    }

/** leiab prefiksi jrk nr prefiksite tabelis preffixes[];
* kasutades viitade massiivi prefs[]
*/
int DCTRD::preffnr( const FSxCHAR *pref ) const
    {
    return prefiksiteLoend[(FSxCHAR *)pref]; // (FSxCHAR *)(const FSxCHAR *)
    }

