/*
* kontrollib, kas viimane sonaosa pa'rast '-' on OK sona;
* n�iteks:
*
* bla-bla-jutt
*
*/
#include "post-fsc.h"
#include "mrf-mrf.h"

int MORF0::arvahy1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    int  tmp;
    int res;
    int i, i1, i2;
    FSXSTRING S6na3;
    FSXSTRING ette, vn, sl;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    
    S6na3 = *S6na;
    i1 = S6na3.ReverseFind(FSxSTR("-"));     // kriipsu eelne jupp ei loe
    i2 = S6na3.ReverseFind(FSxSTR("/"));
    i = i1 > i2 ? i1 : i2;
    if (i == -1 || i == S6naPikkus-1)  // kriipsu pole v�i on ta s�na l�pus
	    return ALL_RIGHT;
    ette = S6na3.Left(i+1);
    S6na3 = S6na3.Mid(i+1);
    if (i == i1)  // viimane oli -
        { // kas on nt. i-le, cd-sid vms
        vn = nLopud.otsi_lyh_vorm((const FSxCHAR *)S6na3);    
        if ( vn != NULL) // ongi mingi l�pp 
	        {
            vn += FSxSTR(", ");
            if (S6na3 == FSxSTR("d"))
                vn += FSxSTR("sg p, ");

            FSXSTRING e1;
            e1 = ette.Left(ette.GetLength()-1);

            if (sobiks_lyhendiks(&e1))
                sl = FSxSTR("Y");
            else
                sl = LIIK_YLDNIMI;
            tulemus->Add((const FSxCHAR *)e1, 
                    (const FSxCHAR *)S6na3, FSxSTR(""), (const FSxCHAR *)sl, (const FSxCHAR *)vn); 
		    return ALL_RIGHT;
            }
        }
    if (TaheHulgad::PoleMuudKui(&S6na3, &(TaheHulgad::number)))
        tulemus->Add((const FSxCHAR *)S6na3, FSxSTR("0"), FSxSTR(""), FSxSTR("N"), FSxSTR("?, "));
    else
        {
        res = kchk1(&ctoo_variandid.ptr, &S6na3, S6na3.GetLength(), &csobivad_variandid.ptr, NULL,0); // ty+lp
        if (res > ALL_RIGHT)
	        return res; // viga! 
        if (csobivad_variandid.ptr)
            {
            variandid_tulemuseks(tulemus, MITTE_VERB, &csobivad_variandid.ptr);
            }
        ahelad_vabaks(&ctoo_variandid.ptr);
        ahelad_vabaks(&csobivad_variandid.ptr);
        }
    if (!tulemus->on_tulem())
        {
        FSXSTRING S6na1;

        S6na1 = S6na3;
        S6na1.MakeLower();
        if (TaheHulgad::SuurAlgustaht(&S6na3))
            res = chkwrd(tulemus, &S6na1, S6na1.GetLength(), 100, &tmp, LIIK_KAANDSONA); // ainult ka'a'ndsonad
        else
		    res = chkwrd(tulemus, &S6na1, S6na1.GetLength(), 100, &tmp, LIIK_KAAND1);
        if (res > ALL_RIGHT)
	        return res; // viga! 
        }
    if (!tulemus->on_tulem())
        {
        if(Barvaww(tulemus, &S6na3, S6na3.GetLength(), LIIK_KAANDSONA)==false)
	        return CRASH; // viga! 
        }
    if (!tulemus->on_tulem())
        {
        res = arvalyh2(tulemus, &S6na3);
        if (res > ALL_RIGHT)
	        return res; // viga! 
        }
    if (!tulemus->on_tulem())
 		return ALL_RIGHT;
    i1 = S6na->FindOneOf(TaheHulgad::suurtht);
    if (TaheHulgad::SuurAlgustaht(&S6na3))   // viimane s�na on suure algust�hega
        tulemus->TulemidNimeks(LIIK_KAANDSONA);
    tulemus->LisaTyvedeleEtte( (const FSxCHAR *)ette );

    return ALL_RIGHT;
    }
