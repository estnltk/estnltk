
// HJK 14.08.95
// TV  25.08.95 - printf'id v�ljat6stetud
//     19.02.02 - klass �mberm�tsitud

#if defined(WIN32)
    #include <malloc.h>
    #include <io.h>
#endif
#if defined(UNIX)
    #include <unistd.h>
#endif
#include <stdlib.h>
#include <fcntl.h>

#include "cxxbs3.h"
#include "sonatk.h"

void DCTRD::open_d2(void)
	{
	register int i;

	readeel();

	readends();    // teeb loppude mass.
	readgrs();     // teeb lgr mass. 
	readfms();     // teeb vormide mass. 
	readfgrs();    // teeb lgr mass. 
	readsuf();     // teeb suf mass. 
	readprf();     // teeb pref mass. 
    // teeb loend[i] mass.
	for (i=0; i < LOENDEID-1; i++) // tegelik loendite arv <= LOENDEID-1
	    {
	    readloe(i);
	    }
	sg_g = vormnr(FSxSTR("sg g"));
	sg_n = vormnr(FSxSTR("sg n"));
	sg_p = vormnr(FSxSTR("sg p"));
	adt  = vormnr(FSxSTR("adt"));
	pl_n = vormnr(FSxSTR("pl n"));
	pl_g = vormnr(FSxSTR("pl g"));
	pl_p = vormnr(FSxSTR("pl p"));
	da   = vormnr(FSxSTR("da"));
	ma   = vormnr(FSxSTR("ma"));
    suva_vrm = SUVA_VRM;
	if(sg_g == -1||sg_n == -1 ||ma == -1) // valikuline test
        {
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
		}
    lopp_a = lpnr(FSxSTR("a"));
    lopp_d = lpnr(FSxSTR("d"));
    lopp_da = lpnr(FSxSTR("da"));
    lopp_dama = lpnr(FSxSTR("dama"));
    lopp_dav = lpnr(FSxSTR("dav"));
    lopp_des = lpnr(FSxSTR("des"));
    lopp_dud = lpnr(FSxSTR("dud"));
    lopp_es = lpnr(FSxSTR("es"));
    lopp_ma = lpnr(FSxSTR("ma"));
    lopp_mata = lpnr(FSxSTR("mata"));
    lopp_nud = lpnr(FSxSTR("nud"));
    lopp_t = lpnr(FSxSTR("t"));
    lopp_ta = lpnr(FSxSTR("ta"));
    lopp_tama = lpnr(FSxSTR("tama"));
    lopp_tav = lpnr(FSxSTR("tav"));
    lopp_te = lpnr(FSxSTR("te"));
    lopp_tes = lpnr(FSxSTR("tes"));
    lopp_tud = lpnr(FSxSTR("tud"));
    lopp_v = lpnr(FSxSTR("v"));
    lopp_0 = null_lopp;
    suva_lp = SUVA_LP;
	if((signed char)lopp_d == (signed char)-1 || 
	   (signed char)lopp_ma == (signed char)-1)   // valikuline test
		{
        throw(VEAD(ERR_MORFI_PS6N,ERR_ROTTEN,__FILE__,__LINE__, "$Revision: 521 $"));
		}
	}






