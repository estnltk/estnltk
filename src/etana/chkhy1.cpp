
/*
* kontrollib, kas S6na on suurt�hega algav ja '-' sisaldav;
* n�iteks:
*
* Dudajevi-meelne
*
*/
#include "mrf-mrf.h"

int MORF0::chkhy1(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    int i;
    int res;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    int k;
    FSXSTRING algus;
    FSXSTRING kriips;
    FSXSTRING lopp;

    k = S6na->Find((FSxCHAR)'-');
    if (k == -1)
        k = S6na->Find((FSxCHAR)'/');
    if (k == -1)
	    return ALL_RIGHT;    // ei sisalda '-' ega '/'
    if (!TaheHulgad::OnSuur(S6na, 0))
	    return ALL_RIGHT;
    algus = (const FSxCHAR *)(S6na->Left(k));
    kriips = (const FSxCHAR *)(S6na->Mid(k, 1));
    lopp = (const FSxCHAR *)(S6na->Mid(k+1));
    if (lopp.GetLength() == 0)
        return ALL_RIGHT;
    if ( kriips == FSxSTR("-") )
	    {
	    /* algul vt, kas on Ida-, L��ne- vms + geo-nimi */
	    i = ( (dctLoend[7])[(FSxCHAR *)(const FSxCHAR *)algus] );   /* kontr. algust loendist */
	    if ( i != -1 )   /* oli loendis */
	        {
	        /* kontr, kas s�na on geograafiline nimi + lp */

            res = kchk1(&ctoo_variandid.ptr, &lopp, lopp.GetLength(), &csobivad_variandid.ptr, NULL,0);
	        if (res > ALL_RIGHT)
		        {
		        return res; /* viga! */
		        }
            if (csobivad_variandid.ptr)
		        {
                variandid_tulemuseks(tulemus, LIIK_PARISNIMI, &csobivad_variandid.ptr);
//                tulem_struktuuri( tulemus, "H", lopp+1 ); /* luban ainult geo-nimesid */
                if ( tulemus->on_tulem() ) /* oligi mingi geo-nimi */
                    {
                    algus += kriips;
                    tulemus->LisaTyvedeleEtte( (const FSxCHAR *)algus );
                    }
		        }
	        }
	    }
    //ahelad_vabaks(&sobivad_variandid);    // destruktoris
    //ahelad_vabaks(&too_variandid);        // destruktoris
    return ALL_RIGHT;
    }
