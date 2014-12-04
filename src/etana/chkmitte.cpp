
/*
* kontrollib, kas S6na on 'mittes�na' nt - & ;
*/

#include "mrf-mrf.h"
#include "mittesona.h"

int MORF0::chkmitte(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    //FSxCHAR *vn;
    FSXSTRING punkt(FSxSTR("."));

    if (S6naPikkus == 1)
	    {
        //vn = erimark.otsi_sonaliik((const FSxCHAR *)(*S6na));
		if (*S6na==FSxSTR("&"))
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR("0"), FSxSTR(""), FSxSTR("J"), FSxSTR("")); 
		else if (*S6na==FSxSTR("-"))
            tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR(""), FSxSTR(""), FSxSTR("Z"), FSxSTR("")); 
        //if (vn != NULL)
            //tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR(""), FSxSTR(""), vn, FSxSTR("")); 

        }
/*   if ( *S6na == '.' )     // kontr, kas on punktide joru
	    {
	    k = strtok( S6na, "." );
	    if ( !k )  // polegi muud kui punktid
            sl[0] = 'Z';
	    }
    if (sl[0])
*/
    else if (TaheHulgad::PoleMuudKui(S6na, &punkt))
        {
        tulemus->Add((const FSxCHAR *)(*S6na), FSxSTR(""), FSxSTR(""), FSxSTR("Z"), FSxSTR("")); 
        }
    return ALL_RIGHT;
    }
